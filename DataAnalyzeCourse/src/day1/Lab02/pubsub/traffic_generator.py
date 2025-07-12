#!/usr/bin/env python3
"""
traffic_generator.py

백엔드 오류 무시 - product_id 누락 문제 해결된 트래픽 생성기
"""

import os
import sys
import time
import json
import random
import threading
import requests
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import logging
from urllib.parse import urljoin
from scipy.stats import lognorm
import numpy as np
from collections import deque

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))
# config.py가 위치한 경로
config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "Lab01", "traffic_generator"))
# 절대경로 지정
sys.path.append(config_path)

# config.py에서 모든 설정 import
from config import *

@dataclass
class UserSession:
    """사용자 세션 클래스"""
    user_id: str
    session_id: str
    user_profile: UserProfile
    session_start_time: float = field(default_factory=time.time)
    session_index: int = 0
    current_state: str = "home"
    current_sub_state: str = ""
    visited_pages: List[str] = field(default_factory=list)
    visited_products: List[str] = field(default_factory=list)
    cart_items: List[Dict] = field(default_factory=list)
    search_terms: List[str] = field(default_factory=list)
    page_views: int = 0
    cart_adds: int = 0
    searches: int = 0
    purchases: int = 0
    total_spent: float = 0.0
    action_count: int = 0
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"session_{uuid.uuid4().hex[:12]}"

class DynamicUserPool:
    """동적 사용자 풀 관리 클래스"""
    
    def __init__(self, max_pool_size=1000, max_recent_size=200):
        self.users = {}
        self.recent_users = deque(maxlen=max_recent_size)
        self.active_users = set()
        self.user_weights = {}
        self.max_pool_size = max_pool_size
        self.lock = threading.RLock()
        self.stats = {
            'total_created': 0,
            'total_reused': 0,
            'pool_size': 0,
            'active_sessions': 0
        }
        
        # 기존 DB 사용자 초기화
        self._initialize_existing_users()
    
    def _initialize_existing_users(self):
        """기존 DB 사용자 풀에 미리 로드"""
        with self.lock:
            for user_id in EXISTING_USER_IDS:
                profile = UserProfile(user_id, is_existing_user=True)
                self.users[user_id] = profile
                self.user_weights[user_id] = 2.0
                self.recent_users.append(user_id)
                self.stats['total_created'] += 1
    
    def get_pool_stats(self):
        """풀 통계 반환"""
        with self.lock:
            self.stats['pool_size'] = len(self.users)
            self.stats['active_sessions'] = len(self.active_users)
            return self.stats.copy()
    
    def mark_user_active(self, user_id):
        """사용자를 활성 상태로 마킹"""
        with self.lock:
            self.active_users.add(user_id)
    
    def mark_user_inactive(self, user_id):
        """사용자를 비활성 상태로 마킹"""
        with self.lock:
            self.active_users.discard(user_id)
    
    def _update_user_weight(self, user_id):
        """사용자 가중치 업데이트"""
        if user_id in self.user_weights:
            self.user_weights[user_id] = min(5.0, self.user_weights[user_id] + 0.1)
        else:
            self.user_weights[user_id] = 1.0
    
    def _select_weighted_user(self):
        """가중치 기반 사용자 선택"""
        if not self.recent_users:
            return None
        
        # 현재 활성 세션이 아닌 사용자만 선택
        available_users = [uid for uid in self.recent_users if uid not in self.active_users]
        if not available_users:
            return random.choice(list(self.recent_users))
        
        # 가중치 기반 선택
        weights = [self.user_weights.get(uid, 1.0) for uid in available_users]
        return random.choices(available_users, weights=weights)[0]
    
    def _create_new_user(self):
        """새 사용자 생성"""
        if random.random() < 0.7:
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            profile = UserProfile(user_id, is_existing_user=False)
        else:
            base_user = random.choice(EXISTING_USER_IDS)
            user_id = f"{base_user}_clone_{uuid.uuid4().hex[:4]}"
            profile = UserProfile(user_id, is_existing_user=True)
        
        return user_id, profile
    
    def _cleanup_old_users(self):
        """오래된 사용자 정리"""
        if len(self.users) <= self.max_pool_size:
            return
        
        recent_set = set(self.recent_users)
        old_users = [uid for uid in self.users.keys() if uid not in recent_set and uid not in self.active_users]
        
        remove_count = len(self.users) - self.max_pool_size
        for user_id in old_users[:remove_count]:
            del self.users[user_id]
            self.user_weights.pop(user_id, None)
    
    def decide_user_for_simulation(self, return_probability=0.35) -> Tuple[str, UserProfile]:
        """사용자 결정 로직"""
        with self.lock:
            # 기존 사용자 재사용
            if self.recent_users and random.random() < return_probability:
                user_id = self._select_weighted_user()
                if user_id and user_id in self.users:
                    profile = self.users[user_id]
                    profile.session_count += 1
                    self._update_user_weight(user_id)
                    
                    if user_id in self.recent_users:
                        temp_recent = list(self.recent_users)
                        temp_recent.remove(user_id)
                        temp_recent.append(user_id)
                        self.recent_users.clear()
                        self.recent_users.extend(temp_recent)
                    
                    self.stats['total_reused'] += 1
                    return user_id, profile
            
            # 신규 사용자 생성
            user_id, profile = self._create_new_user()
            
            self.users[user_id] = profile
            self.recent_users.append(user_id)
            self.user_weights[user_id] = 1.0
            
            self._cleanup_old_users()
            
            self.stats['total_created'] += 1
            return user_id, profile

class TrafficGenerator:
    """메인 트래픽 제너레이터 클래스"""
    
    def __init__(self):
        # config.py에서 설정값 로드
        self.base_url = API_URL_WITH_HTTP
        self.endpoints = API_ENDPOINTS
        self.num_users = NUM_USERS
        self.max_threads = MAX_THREADS
        self.actions_per_user = ACTIONS_PER_USER
        self.time_sleep_range = TIME_SLEEP_RANGE
        
        # 로깅 설정 (파일만)
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILENAME)
            ]
        )
        
        self.session = requests.Session()
        self.session.timeout = 5  # 타임아웃 단축
        self.running = False
        self.threads = []
        self.request_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        
        # 동적 사용자 풀
        self.user_pool = DynamicUserPool(max_pool_size=1500, max_recent_size=300)
        
        # 상품 캐시
        self.products_cache = self._generate_products_cache()
        
        global logger
        logger = logging.getLogger(__name__)
        
    def _generate_products_cache(self):
        """메모리 기반 상품 캐시 생성"""
        products = {}
        for category, product_ids in PRODUCT_ID_RANGES.items():
            for product_id in product_ids:
                products[product_id] = {
                    'id': product_id,
                    'name': f"{category}_{product_id}",
                    'price': random.uniform(10.0, 500.0),
                    'category': category,
                    'rating': round(random.uniform(3.0, 5.0), 1)
                }
        return products
    
    def get_time_based_traffic_multiplier(self):
        """시간대별 트래픽 가중치 계산"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        hourly_weight = HOURLY_TRAFFIC_WEIGHTS.get(hour, 1.0)
        weekday_weight = WEEKDAY_TRAFFIC_WEIGHTS.get(weekday, 1.0)
        
        return hourly_weight * weekday_weight
    
    def check_active_sales(self):
        """현재 시간에 활성화된 세일 이벤트 확인"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        active_sales = []
        for event_name, config in FLASH_SALE_EVENTS.items():
            if 'days' in config:
                if weekday in config['days'] and config['time_range'][0] <= hour <= config['time_range'][1]:
                    if random.random() < config['probability']:
                        active_sales.append((event_name, config))
            else:
                if config['time_range'][0] <= hour <= config['time_range'][1]:
                    if random.random() < config['probability']:
                        active_sales.append((event_name, config))
        
        return active_sales
    
    def calculate_realistic_dwell_time(self, event_type, user_profile):
        """로그정규분포를 사용한 현실적 체류시간 계산"""
        
        sigma, scale = DWELL_TIME_PARAMS.get(event_type, (0.8, 5.0))
        
        try:
            dwell_time = lognorm.rvs(sigma, scale=scale)
        except:
            dwell_time = random.uniform(1.0, 10.0)  # fallback
        
        # 사용자 참여도별 조정
        engagement_config = USER_ENGAGEMENT_LEVELS[user_profile.engagement_level]
        dwell_time *= engagement_config['dwell_time_multiplier']
        
        # 디바이스별 조정
        if user_profile.device == 'mobile':
            dwell_time *= 0.8
        elif user_profile.device == 'tablet':
            dwell_time *= 1.1
        
        return max(0.5, min(dwell_time, 120))
    
    def get_product_for_category(self, category):
        """카테고리별 실제 상품 ID 반환"""
        if category in PRODUCT_ID_RANGES:
            return random.choice(PRODUCT_ID_RANGES[category])
        return random.choice(list(self.products_cache.keys()))
    
    def get_personalized_recommendations(self, user_profile):
        """사용자 프로필 기반 개인화 추천"""
        
        age_num = random.randint(18, 70)
        if age_num <= AGE_THRESHOLD_YOUNG:
            return ['Electronics', 'Gaming', 'Books']
        elif age_num <= AGE_THRESHOLD_MIDDLE:
            return ['Electronics', 'Fashion', 'Books']
        else:
            return ['Home', 'Books', 'Fashion']
    
    def _make_request(self, method, endpoint_key, user_session, **kwargs):
        """HTTP 요청 실행 - 백엔드 오류 무시"""
        
        # API_ENDPOINTS에서 실제 엔드포인트 가져오기
        endpoint = self.endpoints.get(endpoint_key.upper(), endpoint_key)
        url = urljoin(self.base_url, endpoint)
        
        # 기본 헤더 설정
        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = random.choice(USER_AGENTS)
        
        # 이벤트 ID 생성
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        
        # 이벤트명 매핑
        event_name_mapping = {
            'products': 'page_view',
            'product_detail': 'product_view',
            'categories': 'category_browse',
            'category': 'category_view',
            'search': 'search',
            'cart_view': 'cart_view',
            'cart_add': 'add_to_cart',
            'cart_remove': 'remove_from_cart',
            'checkout': 'checkout',
            'checkout_history': 'view_history',
            'add_review': 'add_review',
            'login': 'login',
            'logout': 'logout',
            'add_user': 'register',
            'delete_user': 'unregister',
            'error_page': 'error_page'
        }
        
        event_name = event_name_mapping.get(endpoint_key.lower(), 'unknown')
        
        # 체류시간 계산
        dwell_time = self.calculate_realistic_dwell_time(endpoint_key.lower(), user_session.user_profile)
        
        # Nginx 로그를 위한 헤더 설정
        headers.update({
            'X-Event-Id': event_id,
            'X-Event-Name': event_name,
            'X-User-Id': user_session.user_id,
            'X-Region': user_session.user_profile.region,
            'X-Device': user_session.user_profile.device,
            'X-Dwell-Time': str(round(dwell_time, 2)),
            'X-Event-Context': json.dumps({
                'engagement_level': user_session.user_profile.engagement_level,
                'current_state': user_session.current_state,
                'current_sub_state': user_session.current_sub_state,
                'is_existing_user': user_session.user_profile.is_existing_user,
                'active_sales': [event[0] for event in self.check_active_sales()],
                'traffic_multiplier': self.get_time_based_traffic_multiplier(),
                'session_count': user_session.user_profile.session_count
            })
        })
        
        # 특정 액션별 추가 헤더
        if endpoint_key.lower() == 'cart_add' and kwargs.get('json'):
            headers['X-Quantity'] = str(kwargs['json'].get('quantity', 1))
        
        if endpoint_key.lower() == 'add_review' and kwargs.get('json'):
            headers['X-Review-Rating'] = str(kwargs['json'].get('rating', 5))
        
        # 세션 쿠키 설정
        cookies = kwargs.get('cookies', {})
        cookies.update({
            'session_id': user_session.session_id,
            'session_idx': str(user_session.session_index),
            'is_return': 'true' if user_session.user_profile.session_count > 1 else 'false'
        })
        
        kwargs['headers'] = headers
        kwargs['cookies'] = cookies
        kwargs['timeout'] = 5
        
        start_time = time.time()
        
        try:
            # 백엔드 오류 무시 - 무조건 요청만 보냄
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            with self.lock:
                self.request_count += 1
                # 에러 카운팅도 무시
                
            # 세션 통계 업데이트 (응답 코드 무관)
            self._update_session_stats(user_session, endpoint_key, response)
            
            return response
            
        except requests.RequestException as e:
            response_time = time.time() - start_time
            # 에러 로깅도 최소화
            
            with self.lock:
                self.request_count += 1
            
            # 가짜 성공 응답 반환
            return self._create_success_response()
    
    def _create_success_response(self):
        """가짜 성공 응답 생성"""
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = "OK"
                
        return MockResponse()
    
    def _update_session_stats(self, user_session, endpoint_key, response):
        """세션 통계 업데이트 - 응답 코드 무관"""
        
        # 무조건 성공으로 간주하고 통계 업데이트
        if endpoint_key.lower() in ['products', 'categories', 'category']:
            user_session.page_views += 1
        
        elif endpoint_key.lower() == 'search':
            user_session.searches += 1
        
        elif endpoint_key.lower() == 'product_detail':
            # URL에서 product_id 추출 시도
            try:
                if hasattr(response, 'request') and response.request.url:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(response.request.url)
                    params = urllib.parse.parse_qs(parsed.query)
                    if 'id' in params:
                        product_id = params['id'][0]
                        user_session.visited_products.append(product_id)
            except:
                pass
        
        elif endpoint_key.lower() == 'cart_add':
            user_session.cart_adds += 1
        
        elif endpoint_key.lower() == 'checkout':
            user_session.purchases += 1
        
        user_session.action_count += 1
    
    def _get_next_state(self, current_state, user_session):
        """상위 FSM 상태 전이"""
        transitions = STATE_TRANSITIONS.get(current_state, {})
        
        if not transitions:
            return 'Done'
        
        states = list(transitions.keys())
        weights = list(transitions.values())
        
        return random.choices(states, weights=weights)[0]
    
    def _get_next_sub_state(self, current_sub_state, user_session, sub_transitions):
        """하위 FSM 상태 전이"""
        transitions = sub_transitions.get(current_sub_state, {})
        
        if not transitions:
            return None
        
        # 사용자 참여도에 따른 확률 조정
        engagement_config = USER_ENGAGEMENT_LEVELS[user_session.user_profile.engagement_level]
        
        # 세일 이벤트가 활성화된 경우 구매 확률 증가
        active_sales = self.check_active_sales()
        conversion_boost = 1.0
        if active_sales:
            conversion_boost = max(sale[1]['conversion_boost'] for sale in active_sales)
        
        adjusted_transitions = {}
        for state, prob in transitions.items():
            if 'cart' in state.lower() or 'checkout' in state.lower():
                adjusted_prob = prob * engagement_config['conversion_rate'] * conversion_boost
            else:
                adjusted_prob = prob
            adjusted_transitions[state] = adjusted_prob
        
        # 확률 정규화
        total_prob = sum(adjusted_transitions.values())
        if total_prob > 0:
            normalized_transitions = {k: v/total_prob for k, v in adjusted_transitions.items()}
            
            states = list(normalized_transitions.keys())
            weights = list(normalized_transitions.values())
            
            return random.choices(states, weights=weights)[0]
        
        return None
    
    def _execute_sub_action(self, sub_state, user_session):
        """하위 상태별 액션 실행"""
        
        if not sub_state or 'Done' in sub_state:
            return False
        
        # 비로그인 상태 액션들
        if sub_state == "Anon_Sub_Main":
            self._visit_main_page(user_session)
        elif sub_state == "Anon_Sub_Products":
            self._browse_products(user_session)
        elif sub_state == "Anon_Sub_ViewProduct":
            self._view_product_detail(user_session)
        elif sub_state == "Anon_Sub_Categories":
            self._browse_categories(user_session)
        elif sub_state == "Anon_Sub_CategoryList":
            self._view_category_list(user_session)
        elif sub_state == "Anon_Sub_Search":
            self._perform_search(user_session)
        elif sub_state == "Anon_Sub_Error":
            self._visit_error_page(user_session)
        
        # 로그인 상태 액션들
        elif sub_state == "Login_Sub_Main":
            self._visit_main_page(user_session)
        elif sub_state == "Login_Sub_Products":
            self._browse_products(user_session)
        elif sub_state == "Login_Sub_ViewProduct":
            self._view_product_detail(user_session)
            # 상품 조회 후 즉시 장바구니 추가 시도 (50% 확률)
            if random.random() < 0.5:
                self._add_to_cart(user_session)
        elif sub_state == "Login_Sub_Search":
            self._perform_search(user_session)
        elif sub_state == "Login_Sub_Categories":
            self._browse_categories(user_session)
        elif sub_state == "Login_Sub_CategoryList":
            self._view_category_list(user_session)
        elif sub_state == "Login_Sub_ViewCart":
            self._view_cart(user_session)
        elif sub_state == "Login_Sub_CheckoutHistory":
            self._view_checkout_history(user_session)
        elif sub_state == "Login_Sub_CartAdd":
            self._add_to_cart(user_session)
            # 장바구니 추가 후 즉시 결제 시도 (70% 확률)
            if random.random() < 0.7:
                self._checkout(user_session)
        elif sub_state == "Login_Sub_CartRemove":
            self._remove_from_cart(user_session)
        elif sub_state == "Login_Sub_Checkout":
            self._checkout(user_session)
        elif sub_state == "Login_Sub_AddReview":
            self._add_review(user_session)
        elif sub_state == "Login_Sub_Error":
            self._visit_error_page(user_session)
        
        return True
    
    # 개별 액션 메서드들
    def _visit_main_page(self, user_session):
        """메인 페이지 방문"""
        response = self._make_request('GET', 'products', user_session)
        user_session.page_views += 1
        user_session.visited_pages.append('main')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _browse_products(self, user_session):
        """상품 목록 탐색"""
        response = self._make_request('GET', 'products', user_session)
        user_session.page_views += 1
        user_session.visited_pages.append('products')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _view_product_detail(self, user_session):
        """상품 상세 조회"""
        product_id = random.choice(list(self.products_cache.keys()))
        
        response = self._make_request('GET', 'product_detail', user_session, 
                                    params={'id': product_id})
        
        user_session.page_views += 1
        user_session.visited_products.append(product_id)
        user_session.visited_pages.append(f'product_{product_id}')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _browse_categories(self, user_session):
        """카테고리 탐색"""
        response = self._make_request('GET', 'categories', user_session)
        user_session.page_views += 1
        user_session.visited_pages.append('categories')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _view_category_list(self, user_session):
        """특정 카테고리 상품 목록 조회"""
        category = random.choice(PRODUCT_CATEGORIES)
        
        response = self._make_request('GET', 'category', user_session, 
                                    params={'category': category})
        
        user_session.page_views += 1
        user_session.visited_pages.append(f'category_{category}')
        
        # 선호 카테고리에 추가
        if category not in user_session.user_profile.favorite_categories:
            user_session.user_profile.favorite_categories.append(category)
            if len(user_session.user_profile.favorite_categories) > 3:
                user_session.user_profile.favorite_categories.pop(0)
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _perform_search(self, user_session):
        """검색 수행"""
        search_term = random.choice(SEARCH_KEYWORDS)
        
        response = self._make_request('GET', 'search', user_session, 
                                    params={'query': search_term})
        
        user_session.searches += 1
        user_session.search_terms.append(search_term)
        user_session.visited_pages.append(f'search_{search_term}')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _view_cart(self, user_session):
        """장바구니 조회"""
        response = self._make_request('GET', 'cart_view', user_session)
        user_session.page_views += 1
        user_session.visited_pages.append('cart')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _view_checkout_history(self, user_session):
        """결제 이력 조회"""
        response = self._make_request('GET', 'checkout_history', user_session)
        user_session.page_views += 1
        user_session.visited_pages.append('checkout_history')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _add_to_cart(self, user_session):
        """장바구니에 상품 추가 - product_id URL 파라미터 추가"""
        if user_session.visited_products:
            product_id = random.choice(user_session.visited_products)
        else:
            product_id = random.choice(list(self.products_cache.keys()))
        
        product_info = self.products_cache.get(product_id, {})
        quantity = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        
        cart_data = {
            'product_id': product_id,
            'quantity': quantity,
            'price': product_info.get('price', 50.0)
        }
        
        # URL 파라미터로 product_id 전달 (Nginx $arg_id로 캡처)
        response = self._make_request('POST', 'cart_add', user_session, 
                                    json=cart_data,
                                    params={'id': product_id})
        
        # 백엔드 오류 무시하고 무조건 성공으로 간주
        user_session.cart_items.append(cart_data)
        user_session.cart_adds += 1
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _remove_from_cart(self, user_session):
        """장바구니에서 상품 제거 - product_id URL 파라미터 추가"""
        if user_session.cart_items:
            item_to_remove = random.choice(user_session.cart_items)
            product_id = item_to_remove['product_id']
            
            # URL 파라미터로 product_id 전달
            response = self._make_request('POST', 'cart_remove', user_session, 
                                        json={'product_id': product_id},
                                        params={'id': product_id})
            
            # 백엔드 오류 무시하고 무조건 제거
            user_session.cart_items.remove(item_to_remove)
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _checkout(self, user_session):
        """결제 진행"""
        if user_session.cart_items:
            total_amount = sum(item['price'] * item['quantity'] for item in user_session.cart_items)
            
            checkout_data = {
                'items': user_session.cart_items,
                'total_amount': total_amount
            }
            
            response = self._make_request('POST', 'checkout', user_session, json=checkout_data)
            
            # 백엔드 오류 무시하고 무조건 성공으로 간주
            user_session.purchases += 1
            user_session.total_spent += total_amount
            user_session.user_profile.total_purchases += 1
            
            # 구매한 상품을 구매 이력에 추가
            for item in user_session.cart_items:
                user_session.user_profile.purchase_history.append(item['product_id'])
            
            user_session.cart_items.clear()
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _add_review(self, user_session):
        """리뷰 작성 - product_id URL 파라미터 추가"""
        if user_session.user_profile.purchase_history:
            product_id = random.choice(user_session.user_profile.purchase_history)
        else:
            product_id = random.choice(list(self.products_cache.keys()))
        
        review_data = {
            'product_id': product_id,
            'rating': random.randint(3, 5),
            'comment': f"Review for product {product_id}"
        }
        
        # URL 파라미터로 product_id 전달 (Nginx $arg_id로 캡처)
        response = self._make_request('POST', 'add_review', user_session, 
                                    json=review_data,
                                    params={'id': product_id})
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _visit_error_page(self, user_session):
        """에러 페이지 방문"""
        response = self._make_request('GET', 'error_page', user_session)
        user_session.page_views += 1
        user_session.visited_pages.append('error')
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _perform_login(self, user_session):
        """로그인 수행"""
        login_data = {
            'user_id': user_session.user_id,
            'device': user_session.user_profile.device
        }
        
        response = self._make_request('POST', 'login', user_session, json=login_data)
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _perform_logout(self, user_session):
        """로그아웃 수행"""
        response = self._make_request('POST', 'logout', user_session)
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _perform_registration(self, user_session):
        """회원가입 수행"""
        register_data = {
            'user_id': user_session.user_id,
            'name': f"User_{user_session.user_id[-4:]}",
            'email': f"{user_session.user_id}@example.com",
            'age': random.randint(18, 70),
            'gender': user_session.user_profile.gender
        }
        
        response = self._make_request('POST', 'add_user', user_session, json=register_data)
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _perform_unregistration(self, user_session):
        """회원탈퇴 수행"""
        response = self._make_request('POST', 'delete_user', user_session, 
                                    json={'user_id': user_session.user_id})
        
        dwell_time = random.uniform(*self.time_sleep_range)
        time.sleep(dwell_time)
    
    def _execute_guaranteed_purchase_flow(self, user_session):
        """보장된 구매 플로우 - 무조건 구매까지 진행"""
        logger.info(f"Guaranteed purchase flow for {user_session.user_id}")
        
        # 1. 로그인
        self._perform_login(user_session)
        
        # 2. 상품 조회
        self._view_product_detail(user_session)
        
        # 3. 장바구니 추가
        self._add_to_cart(user_session)
        
        # 4. 즉시 결제
        self._checkout(user_session)
        
        logger.info(f"Guaranteed purchase completed: {user_session.purchases} purchases")
    
    def _simulate_user_session(self):
        """사용자 세션 시뮬레이션"""
        
        user_id, user_profile = self.user_pool.decide_user_for_simulation()
        user_session = UserSession(user_id, "", user_profile)
        
        self.user_pool.mark_user_active(user_id)
        
        try:
            # 30% 확률로 보장된 구매 플로우 실행
            if random.random() < 0.3:
                self._execute_guaranteed_purchase_flow(user_session)
                return
            
            logger.info(f"Starting session for user {user_id} (engagement: {user_profile.engagement_level})")
            
            # 상위 상태 머신 시작
            current_state = "Anon_NotRegistered"
            max_actions = self.actions_per_user
            
            while current_state != "Done" and user_session.action_count < max_actions and self.running:
                try:
                    # 상위 상태별 처리
                    if current_state == "Anon_NotRegistered":
                        current_sub_state = "Anon_Sub_Initial"
                        sub_transitions = ANON_SUB_TRANSITIONS
                        
                        sub_action_count = 0
                        while current_sub_state and "Done" not in current_sub_state and user_session.action_count < max_actions and sub_action_count < 5:
                            self._execute_sub_action(current_sub_state, user_session)
                            user_session.current_sub_state = current_sub_state
                            user_session.action_count += 1
                            sub_action_count += 1
                            
                            current_sub_state = self._get_next_sub_state(current_sub_state, user_session, sub_transitions)
                            
                            engagement_config = USER_ENGAGEMENT_LEVELS[user_profile.engagement_level]
                            sleep_time = random.uniform(*self.time_sleep_range) * random.uniform(*engagement_config['sleep_multiplier'])
                            time.sleep(min(sleep_time, 2.0))  # 최대 2초로 제한
                    
                    elif current_state == "Anon_Registered":
                        self._perform_registration(user_session)
                        user_session.action_count += 1
                    
                    elif current_state == "Logged_In":
                        self._perform_login(user_session)
                        user_session.action_count += 1
                        
                        current_sub_state = "Login_Sub_Initial"
                        sub_transitions = LOGGED_SUB_TRANSITIONS
                        
                        sub_action_count = 0
                        while current_sub_state and "Done" not in current_sub_state and user_session.action_count < max_actions and sub_action_count < 10:
                            self._execute_sub_action(current_sub_state, user_session)
                            user_session.current_sub_state = current_sub_state
                            user_session.action_count += 1
                            sub_action_count += 1
                            
                            current_sub_state = self._get_next_sub_state(current_sub_state, user_session, sub_transitions)
                            
                            engagement_config = USER_ENGAGEMENT_LEVELS[user_profile.engagement_level]
                            sleep_time = random.uniform(*self.time_sleep_range) * random.uniform(*engagement_config['sleep_multiplier'])
                            time.sleep(min(sleep_time, 2.0))  # 최대 2초로 제한
                    
                    elif current_state == "Logged_Out":
                        self._perform_logout(user_session)
                        user_session.action_count += 1
                    
                    elif current_state == "Unregistered":
                        self._perform_unregistration(user_session)
                        user_session.action_count += 1
                    
                    # 다음 상위 상태로 전이
                    user_session.current_state = current_state
                    current_state = self._get_next_state(current_state, user_session)
                    
                except Exception as e:
                    logger.error(f"Error in user session {user_id}: {e}")
                    break
            
            session_duration = time.time() - user_session.session_start_time
            logger.info(f"Session ended for user {user_id}: {user_session.action_count} actions, {session_duration:.1f}s, purchases: {user_session.purchases}, cart_adds: {user_session.cart_adds}")
            
        finally:
            self.user_pool.mark_user_inactive(user_id)
    
    def _worker_thread(self):
        """워커 스레드 함수"""
        
        while self.running:
            try:
                # 시간대별 트래픽 조정
                traffic_multiplier = self.get_time_based_traffic_multiplier()
                
                # 세일 이벤트 트래픽 부스트
                active_sales = self.check_active_sales()
                if active_sales:
                    sale_boost = max(sale[1]['traffic_boost'] for sale in active_sales)
                    traffic_multiplier *= sale_boost
                
                # 요청 간격 조정
                base_interval = 60.0 / self.num_users
                adjusted_interval = base_interval / traffic_multiplier
                
                # 사용자 세션 시뮬레이션
                self._simulate_user_session()
                
                # 대기
                time.sleep(max(0.1, adjusted_interval))
                
            except Exception as e:
                logger.error(f"Worker thread error: {e}")
                time.sleep(1.0)
    
    def start(self):
        """트래픽 제너레이터 시작"""
        
        if self.running:
            logger.warning("Traffic generator is already running")
            return
        
        self.running = True
        logger.info(f"Starting traffic generator with {self.max_threads} threads")
        logger.info(f"User pool initialized with {len(self.user_pool.users)} users")
        
        # 워커 스레드 생성 및 시작
        for i in range(self.max_threads):
            thread = threading.Thread(target=self._worker_thread, name=f"Worker-{i}")
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
        logger.info("Traffic generator started successfully")
    
    def stop(self):
        """트래픽 제너레이터 중지"""
        
        if not self.running:
            logger.warning("Traffic generator is not running")
            return
        
        logger.info("Stopping traffic generator...")
        self.running = False
        
        # 모든 스레드 종료 대기
        for thread in self.threads:
            thread.join(timeout=5.0)
        
        self.threads.clear()
        logger.info("Traffic generator stopped")
    
    def get_stats(self):
        """통계 정보 반환"""
        
        with self.lock:
            pool_stats = self.user_pool.get_pool_stats()
            return {
                'total_requests': self.request_count,
                'total_errors': self.error_count,
                'error_rate': self.error_count / max(1, self.request_count),
                'running': self.running,
                'user_pool': pool_stats
            }

def main():
    """메인 함수"""
    
    generator = TrafficGenerator()
    
    try:
        generator.start()
        
        # 통계 출력
        while True:
            time.sleep(30)
            stats = generator.get_stats()
            logger.info(f"Stats: Requests={stats['total_requests']}, "
                       f"Pool={stats['user_pool']['pool_size']}, Active={stats['user_pool']['active_sessions']}, "
                       f"Created={stats['user_pool']['total_created']}, Reused={stats['user_pool']['total_reused']}")
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        generator.stop()

if __name__ == "__main__":
    main()
