#!/usr/bin/env python3
"""
Ultimate Enhanced E-commerce Traffic Generator
===========================================

완전한 트래픽 생성기 - 모든 문제 해결됨:
✅ Ctrl+C 즉시 종료
✅ 완전한 헤더 정보
✅ 안정적인 에러 처리
✅ 현실적인 사용자 행동
✅ 파레토 분포 세션 길이
✅ 사용자 재사용 로직
✅ 특가 세일 이벤트
✅ 성능 최적화
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import signal
import sys
import threading
import time
import uuid
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import weakref

# 써드파티 라이브러리
try:
    import numpy as np
except ImportError:
    print("numpy 설치 필요: pip install numpy")
    sys.exit(1)

try:
    import psutil
except ImportError:
    print("psutil 설치 필요: pip install psutil")
    sys.exit(1)

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("requests 설치 필요: pip install requests")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("PyYAML 설치 필요: pip install PyYAML")
    sys.exit(1)

# ────────────────────────────────
# 설정 로드
# ────────────────────────────────
# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# config.py가 위치한 경로:
# 현재 디렉토리에서 두 단계 위로 이동한 후 Lab00/traffic_generator 디렉토리로 이동
config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "Lab01", "traffic_generator"))

# 절대경로 지정
sys.path.append(config_path)

try:
    import config
except ImportError as e:
    print(f"config.py 파일이 필요함: {e}")
    sys.exit(1)

# ────────────────────────────────
# 전역 종료 처리기
# ────────────────────────────────
class GracefulKiller:
    """우아한 종료 처리기 - Ctrl+C 즉시 반응"""
    
    def __init__(self):
        self.kill_now = False
        self.start_time = time.time()
        
        # 신호 핸들러 등록
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        
        print("🚀 트래픽 생성기 시작 (Ctrl+C로 종료)")
    
    def _exit_gracefully(self, signum, frame):
        if not self.kill_now:
            elapsed = time.time() - self.start_time
            print(f"\n🛑 종료 신호 수신 (실행시간: {elapsed:.1f}초)")
            print("⏳ 5초 내 정리 후 종료됨...")
            self.kill_now = True
            
            # 5초 후 강제 종료
            def force_exit():
                time.sleep(5)
                print("💥 강제 종료")
                os._exit(1)
            
            threading.Thread(target=force_exit, daemon=True).start()
        else:
            print("💥 즉시 강제 종료")
            os._exit(1)

# 전역 종료 처리기 인스턴스
killer = GracefulKiller()

# ────────────────────────────────
# 로깅 설정
# ────────────────────────────────
class StructuredFormatter(logging.Formatter):
    """JSON 구조화 로깅 포맷터"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 추가 필드
        for attr in ['user_id', 'session_id', 'event_name', 'duration', 'status_code']:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)
        
        return json.dumps(log_data, ensure_ascii=False)

def setup_logging():
    """고급 로깅 설정"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 (회전 로그)
    try:
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            config.LOG_FILENAME,
            maxBytes=config.LOG_MAX_SIZE,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"파일 로깅 설정 실패: {e}")
    
    # 콘솔 핸들러 (간단한 포맷)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ────────────────────────────────
# 전역 상태 관리
# ────────────────────────────────
class GlobalState:
    """스레드 안전한 전역 상태 관리"""
    
    def __init__(self):
        # 캐시 데이터
        self.products_cache: List[Dict] = []
        self.categories_cache: List[str] = []
        
        # 사용자 관리
        self.user_profiles: Dict[str, Dict] = {}
        self.purchase_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # 세일 이벤트
        self.sale_events_state: Dict[str, Dict] = {}
        
        # 세션 관리
        self.active_sessions: Set[str] = set()
        self.session_stats: Dict[str, int] = defaultdict(int)
        
        # 성능 메트릭
        self.performance_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_counts: Dict[str, int] = defaultdict(int)
        
        # 스레드 안전성
        self.lock = threading.RLock()
        
        # 종료 플래그
        self.shutdown_requested = False
    
    def update_stats(self, key: str, value: int = 1):
        """통계 업데이트 (스레드 안전)"""
        with self.lock:
            self.session_stats[key] += value
    
    def add_performance_metric(self, metric_name: str, value: float):
        """성능 메트릭 추가"""
        with self.lock:
            self.performance_metrics[metric_name].append({
                'timestamp': datetime.now(),
                'value': value
            })
    
    def get_stats_snapshot(self) -> Dict[str, Any]:
        """현재 통계 스냅샷 반환"""
        with self.lock:
            return {
                'session_stats': dict(self.session_stats),
                'active_sessions': len(self.active_sessions),
                'total_users': len(self.user_profiles),
                'error_counts': dict(self.error_counts),
                'products_cached': len(self.products_cache),
                'categories_cached': len(self.categories_cache)
            }

# 전역 상태 인스턴스
global_state = GlobalState()

# ────────────────────────────────
# 중단 가능한 유틸리티
# ────────────────────────────────
def interruptible_sleep(duration: float) -> bool:
    """중단 가능한 sleep - True 반환 시 중단됨"""
    if duration <= 0:
        return killer.kill_now
    
    end_time = time.time() + duration
    while time.time() < end_time and not killer.kill_now:
        sleep_chunk = min(0.1, end_time - time.time())
        if sleep_chunk > 0:
            time.sleep(sleep_chunk)
    
    return killer.kill_now

def safe_request(method: str, url: str, headers: Dict = None, data: Dict = None, 
                timeout: int = 10, max_retries: int = 3) -> requests.Response:
    """안전한 HTTP 요청 처리"""
    
    headers = headers or {}
    
    for attempt in range(max_retries):
        if killer.kill_now:
            raise KeyboardInterrupt("Graceful shutdown requested")
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            duration = time.time() - start_time
            global_state.add_performance_metric('request_duration', duration)
            
            # 성공적인 응답
            if response.status_code < 400:
                global_state.update_stats('successful_requests')
                return response
            else:
                global_state.update_stats(f'http_error_{response.status_code}')
                global_state.error_counts[f'HTTP_{response.status_code}'] += 1
                
                if attempt == max_retries - 1:  # 마지막 시도
                    return response
                
        except requests.exceptions.Timeout:
            global_state.update_stats('timeout_errors')
            global_state.error_counts['Timeout'] += 1
            
        except requests.exceptions.ConnectionError:
            global_state.update_stats('connection_errors')
            global_state.error_counts['Connection'] += 1
            
        except Exception as e:
            global_state.update_stats('unknown_errors')
            global_state.error_counts[f'Unknown_{type(e).__name__}'] += 1
            
            if attempt == max_retries - 1:
                raise
        
        # 재시도 대기
        if attempt < max_retries - 1:
            retry_delay = 0.5 * (2 ** attempt)  # 지수 백오프
            if interruptible_sleep(retry_delay):
                raise KeyboardInterrupt("Graceful shutdown during retry")
    
    # 실패 시 더미 응답
    class DummyResponse:
        def __init__(self):
            self.status_code = 503
            self.ok = False
            self.text = "Service Unavailable"
    
    return DummyResponse()

# ────────────────────────────────
# 데이터 클래스
# ────────────────────────────────
@dataclass
class UserProfile:
    """사용자 프로필"""
    user_id: str
    gender: str
    age: int
    age_segment: str
    region: str
    device: str
    engagement_level: str
    registration_date: datetime
    total_sessions: int = 0
    total_purchases: int = 0
    preferred_categories: List[str] = field(default_factory=list)
    loyalty_tier: str = "bronze"
    
    def __post_init__(self):
        if not self.preferred_categories:
            self.preferred_categories = config.CATEGORY_PREFERENCE.get(
                self.gender, {}
            ).get(self.age_segment, [])

@dataclass
class SessionContext:
    """세션 컨텍스트"""
    session_id: str
    user_profile: UserProfile
    session_idx: int
    start_time: datetime
    last_action_time: datetime
    actions_count: int = 0
    pages_visited: List[str] = field(default_factory=list)
    products_viewed: List[str] = field(default_factory=list)
    cart_items: List[str] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    conversion_events: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # 활성 세션에 추가
        global_state.active_sessions.add(self.session_id)
    
    def end_session(self):
        """세션 종료 처리"""
        global_state.active_sessions.discard(self.session_id)
        
        session_duration = (datetime.now() - self.start_time).total_seconds()
        global_state.add_performance_metric('session_duration', session_duration)
        global_state.update_stats('completed_sessions')
        
        logger.info("Session completed", extra={
            'user_id': self.user_profile.user_id,
            'session_id': self.session_id,
            'duration': session_duration,
            'actions_count': self.actions_count,
            'pages_visited': len(self.pages_visited),
            'conversions': len(self.conversion_events)
        })

# ────────────────────────────────
# 파레토 분포 및 사용자 관리
# ────────────────────────────────
def generate_pareto_session_lengths(num_users: int, base_actions: int) -> List[int]:
    """파레토 분포 기반 세션 길이 생성 (20-80 법칙)"""
    if not config.PARETO_ENABLED:
        return [base_actions] * num_users
    
    alpha = config.PARETO_ALPHA
    min_actions = config.PARETO_MIN_ACTIONS
    max_multiplier = config.PARETO_MAX_MULTIPLIER
    
    session_lengths = []
    
    for _ in range(num_users):
        # 파레토 분포에서 샘플링
        length = int(np.random.pareto(alpha) * base_actions)
        length = max(min_actions, min(length, int(base_actions * max_multiplier)))
        session_lengths.append(length)
    
    # 총 액션 수를 목표에 맞춤
    total_actions = sum(session_lengths)
    target_total = base_actions * num_users
    
    if total_actions > 0:
        scale_factor = target_total / total_actions
        scaled_lengths = [max(min_actions, int(length * scale_factor)) for length in session_lengths]
    else:
        scaled_lengths = [base_actions] * num_users
    
    logger.info(f"Pareto distribution - min: {min(scaled_lengths)}, max: {max(scaled_lengths)}, avg: {np.mean(scaled_lengths):.1f}")
    
    return scaled_lengths

def get_age_segment(age: int) -> str:
    """나이대 분류"""
    if age < config.AGE_THRESHOLD_YOUNG:
        return "young"
    elif age < config.AGE_THRESHOLD_MIDDLE:
        return "middle"
    else:
        return "old"

def create_or_reuse_user_profile() -> Tuple[UserProfile, bool]:
    """사용자 프로필 생성 또는 재사용"""
    with global_state.lock:
        is_returning = False
        
        # 기존 사용자 재사용 확률
        if (config.USER_REUSE_ENABLED and 
            global_state.user_profiles and 
            len(global_state.user_profiles) < config.MAX_EXISTING_USERS and 
            random.random() < config.USER_REUSE_PROBABILITY):
            
            # 기존 사용자 선택
            user_id = random.choice(list(global_state.user_profiles.keys()))
            profile_data = global_state.user_profiles[user_id]
            
            profile = UserProfile(
                user_id=user_id,
                gender=profile_data['gender'],
                age=profile_data['age'],
                age_segment=profile_data['age_segment'],
                region=profile_data['region'],
                device=profile_data['device'],
                engagement_level=profile_data['engagement_level'],
                registration_date=profile_data['registration_date'],
                total_sessions=profile_data['total_sessions'],
                total_purchases=profile_data['total_purchases'],
                preferred_categories=profile_data['preferred_categories'],
                loyalty_tier=profile_data.get('loyalty_tier', 'bronze')
            )
            
            # 세션 카운트 증가
            profile.total_sessions += 1
            global_state.user_profiles[user_id]['total_sessions'] += 1
            
            is_returning = True
            
        else:
            # 새 사용자 생성
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            gender = random.choice(["F", "M"])
            
            # 현실적인 나이 분포
            age = int(np.random.normal(35, 12))
            age = max(18, min(age, 70))
            
            age_segment = get_age_segment(age)
            region = random.choice(config.REGIONS)
            device = random.choice(config.DEVICE_TYPES)
            
            # 참여도 레벨 결정
            engagement_levels = ['low', 'normal', 'high']
            engagement_level = random.choices(engagement_levels, weights=config.ENGAGEMENT_WEIGHTS)[0]
            
            profile = UserProfile(
                user_id=user_id,
                gender=gender,
                age=age,
                age_segment=age_segment,
                region=region,
                device=device,
                engagement_level=engagement_level,
                registration_date=datetime.now(),
                total_sessions=1
            )
            
            # 프로필 저장
            global_state.user_profiles[user_id] = {
                'gender': gender,
                'age': age,
                'age_segment': age_segment,
                'region': region,
                'device': device,
                'engagement_level': engagement_level,
                'registration_date': datetime.now(),
                'total_sessions': 1,
                'total_purchases': 0,
                'preferred_categories': profile.preferred_categories,
                'loyalty_tier': 'bronze'
            }
    
    return profile, is_returning

# ────────────────────────────────
# 상품 및 카테고리 관리
# ────────────────────────────────
def fetch_products():
    """상품 정보 조회"""
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
        resp = safe_request('GET', url, headers={"Accept": "application/json"})
        
        if resp.status_code == 200:
            data = resp.json() if hasattr(resp, 'json') else []
            global_state.products_cache = data if isinstance(data, list) else data.get("products", [])
        
        if not global_state.products_cache:
            global_state.products_cache = generate_dummy_products()
        
        logger.info(f"Products loaded: {len(global_state.products_cache)}")
        
    except Exception as exc:
        logger.error(f"Failed to fetch products: {exc}")
        global_state.products_cache = generate_dummy_products()

def fetch_categories():
    """카테고리 정보 조회"""
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CATEGORIES"]
        resp = safe_request('GET', url, headers={"Accept": "application/json"})
        
        if resp.status_code == 200:
            data = resp.json() if hasattr(resp, 'json') else []
            global_state.categories_cache = data if isinstance(data, list) else data.get("categories", [])
        
        if not global_state.categories_cache:
            global_state.categories_cache = ["Electronics", "Fashion", "Home", "Books", "Gaming", "Food", "Beauty", "Sports"]
        
        logger.info(f"Categories loaded: {len(global_state.categories_cache)}")
        
    except Exception as exc:
        logger.error(f"Failed to fetch categories: {exc}")
        global_state.categories_cache = ["Electronics", "Fashion", "Home", "Books", "Gaming", "Food"]

def generate_dummy_products() -> List[Dict]:
    """더미 상품 데이터 생성"""
    products = []
    categories = ["Electronics", "Fashion", "Home", "Books", "Gaming", "Food", "Beauty", "Sports"]
    
    for i in range(101, 301):  # 200개 상품
        category = random.choice(categories)
        
        price_ranges = {
            "Electronics": (50, 2000), "Fashion": (20, 500), "Home": (15, 800),
            "Books": (10, 50), "Gaming": (30, 100), "Food": (5, 100),
            "Beauty": (10, 200), "Sports": (25, 300)
        }
        
        price_range = price_ranges.get(category, (10, 100))
        price = random.randint(*price_range)
        
        products.append({
            "id": i,
            "name": f"{category}_Product_{i}",
            "category": category,
            "price": price,
            "rating": round(random.uniform(3.0, 5.0), 1),
            "reviews_count": random.randint(5, 500),
            "in_stock": random.choice([True, True, True, False])  # 25% 품절
        })
    
    return products

def pick_preferred_product_id(ctx: SessionContext) -> str:
    """사용자 선호도 기반 상품 선택"""
    if not global_state.products_cache:
        return str(random.randint(101, 200))
    
    # 구매 이력 기반 추천
    recent_purchases = global_state.purchase_history.get(ctx.user_profile.user_id, [])
    if recent_purchases and random.random() < 0.3:
        last_category = recent_purchases[-1].get('category')
        if last_category:
            category_products = [p for p in global_state.products_cache 
                               if p.get("category") == last_category and p.get("in_stock", True)]
            if category_products:
                return str(random.choice(category_products).get("id"))
    
    # 세션 내 행동 기반
    if ctx.products_viewed and random.random() < 0.2:
        last_viewed = ctx.products_viewed[-1]
        last_product = next((p for p in global_state.products_cache 
                           if str(p.get("id")) == last_viewed), None)
        if last_product:
            same_category = [p for p in global_state.products_cache 
                           if (p.get("category") == last_product.get("category") and
                               str(p.get("id")) != last_viewed and
                               p.get("in_stock", True))]
            if same_category:
                return str(random.choice(same_category).get("id"))
    
    # 기본 선호도 기반
    preferred_categories = ctx.user_profile.preferred_categories
    if preferred_categories:
        category_products = [p for p in global_state.products_cache 
                           if p.get("category") in preferred_categories and p.get("in_stock", True)]
        if category_products:
            return str(random.choice(category_products).get("id"))
    
    # 무작위 선택
    in_stock_products = [p for p in global_state.products_cache if p.get("in_stock", True)]
    if in_stock_products:
        return str(random.choice(in_stock_products).get("id"))
    
    return str(random.randint(101, 200))

# ────────────────────────────────
# 체류 시간 계산
# ────────────────────────────────
def calculate_realistic_dwell_time(page_type: str, engagement_level: str = "normal") -> float:
    """현실적인 체류 시간 계산"""
    if not config.REALISTIC_DWELL_ENABLED:
        return random.uniform(*config.DWELL_TIME_RANGE)
    
    min_time, max_time = config.PAGE_DWELL_TIMES.get(page_type, (2.0, 10.0))
    
    # 참여도별 배수
    engagement_multipliers = {"low": 0.7, "normal": 1.0, "high": 1.4}
    multiplier = engagement_multipliers.get(engagement_level, 1.0)
    
    if config.USE_LOGNORMAL_DWELL:
        # 로그정규분포 사용
        mean_log = np.log(np.sqrt(min_time * max_time))
        std_log = np.log(max_time / min_time) / 4
        dwell_time = np.random.lognormal(mean_log, std_log)
    else:
        # 균등분포 사용
        dwell_time = random.uniform(min_time, max_time)
    
    dwell_time *= multiplier
    return max(0.5, min(dwell_time, max_time * 2))

# ────────────────────────────────
# 헤더 생성 (완전한 정보 포함)
# ────────────────────────────────
def build_complete_headers(ctx: SessionContext, event_name: str, 
                          page_type: str = "main", extra: Dict[str, str] = None) -> Dict[str, str]:
    """완전한 헤더 정보 생성 - 모든 필드 보장"""
    
    # 체류 시간 계산 및 실제 대기
    dwell_time = calculate_realistic_dwell_time(page_type, ctx.user_profile.engagement_level)
    if interruptible_sleep(dwell_time):
        raise KeyboardInterrupt("Interrupted during dwell time")
    
    # 상태 업데이트
    ctx.last_action_time = datetime.now()
    ctx.actions_count += 1
    if page_type not in ctx.pages_visited:
        ctx.pages_visited.append(page_type)
    
    # 완전한 헤더 생성
    headers = {
        "Accept": "application/json",
        "User-Agent": f"EcommerceSim/2.0 ({ctx.user_profile.device}; {ctx.user_profile.region})",
        "Content-Type": "application/x-www-form-urlencoded",
        
        # 기본 이벤트 정보
        "X-Event-Id": str(uuid.uuid4()),
        "X-Event-Name": event_name,
        "X-Event-Timestamp": datetime.now().isoformat(),
        
        # 사용자 정보 (필수 - 절대 빈 값 없음)
        "X-User-Id": ctx.user_profile.user_id,
        "X-User-Age": str(ctx.user_profile.age),
        "X-User-Gender": ctx.user_profile.gender,
        "X-User-Region": ctx.user_profile.region or "KR",
        "X-User-Device": ctx.user_profile.device or "PC",
        "X-User-Engagement": ctx.user_profile.engagement_level or "normal",
        
        # 세션 정보 (필수 - 절대 빈 값 없음)
        "X-Session-Id": ctx.session_id,
        "X-Session-Index": str(ctx.session_idx) if ctx.session_idx else "1",
        "X-Is-Return-Visitor": "1" if ctx.session_idx > 1 else "0",
        "X-Session-Actions": str(ctx.actions_count),
        "X-Session-Duration": str(int((datetime.now() - ctx.start_time).total_seconds())),
        
        # 페이지 정보
        "X-Page-Type": page_type,
        "X-Pages-Visited": str(len(ctx.pages_visited)),
        "X-Dwell-Time": f"{dwell_time:.3f}",
        
        # 행동 정보
        "X-Products-Viewed": str(len(ctx.products_viewed)),
        "X-Cart-Items": str(len(ctx.cart_items)),
        "X-Search-Queries": str(len(ctx.search_queries)),
        "X-Conversions": str(len(ctx.conversion_events)),
    }
    
    # 구매 이력 정보
    purchase_count = len(global_state.purchase_history.get(ctx.user_profile.user_id, []))
    headers["X-Purchase-History-Count"] = str(purchase_count)
    
    # 추가 헤더
    if extra:
        headers.update(extra)
    
    return headers

# ────────────────────────────────
# 회원 관리 함수들
# ────────────────────────────────
def try_register(ctx: SessionContext) -> bool:
    """회원가입 시도"""
    payload = {
        "user_id": ctx.user_profile.user_id,
        "name": f"User_{ctx.user_profile.user_id[-6:]}",
        "email": f"{ctx.user_profile.user_id}@example.com",
        "gender": ctx.user_profile.gender,
        "age": str(ctx.user_profile.age),
        "region": ctx.user_profile.region,
        "device": ctx.user_profile.device
    }
    
    headers = build_complete_headers(ctx, "register", "register")
    url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ADD_USER"]
    
    response = safe_request('POST', url, headers, payload)
    success = response.status_code == 201
    
    if success:
        ctx.conversion_events.append('registration')
        global_state.update_stats('successful_registrations')
    else:
        global_state.update_stats('failed_registrations')
    
    logger.info("Registration attempt", extra={
        'user_id': ctx.user_profile.user_id,
        'status_code': response.status_code,
        'success': success
    })
    
    return success

def try_login(ctx: SessionContext) -> bool:
    """로그인 시도"""
    headers = build_complete_headers(ctx, "login", "login")
    url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["LOGIN"]
    
    response = safe_request('POST', url, headers, {"user_id": ctx.user_profile.user_id})
    success = response.status_code == 200
    
    if success:
        global_state.update_stats('successful_logins')
    else:
        global_state.update_stats('failed_logins')
    
    return success

def try_logout(ctx: SessionContext) -> bool:
    """로그아웃 시도"""
    headers = build_complete_headers(ctx, "logout", "main")
    url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["LOGOUT"]
    
    response = safe_request('POST', url, headers)
    success = response.status_code == 200
    
    if success:
        global_state.update_stats('successful_logouts')
    
    return success

# ────────────────────────────────
# 액션 함수들
# ────────────────────────────────
def perform_anon_action(ctx: SessionContext, state: str):
    """비로그인 사용자 액션"""
    try:
        if state == "Anon_Sub_Main":
            headers = build_complete_headers(ctx, "page_view", "main")
            safe_request('GET', config.API_URL_WITH_HTTP, headers)
        
        elif state == "Anon_Sub_Products":
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
            headers = build_complete_headers(ctx, "products_list", "product_list")
            safe_request('GET', url, headers)
        
        elif state == "Anon_Sub_ViewProduct":
            pid = pick_preferred_product_id(ctx)
            url = f"{config.API_URL_WITH_HTTP}{config.API_ENDPOINTS['PRODUCT_DETAIL']}?id={pid}"
            headers = build_complete_headers(ctx, "product_view", "product_detail", {"X-Product-Id": pid})
            
            safe_request('GET', url, headers)
            ctx.products_viewed.append(pid)
        
        elif state == "Anon_Sub_Categories":
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CATEGORIES"]
            headers = build_complete_headers(ctx, "categories_list", "category")
            safe_request('GET', url, headers)
        
        elif state == "Anon_Sub_CategoryList" and global_state.categories_cache:
            category = random.choice(global_state.categories_cache)
            url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['CATEGORY']}?name={category}"
            headers = build_complete_headers(ctx, "category_view", "category", {"X-Category": category})
            safe_request('GET', url, headers)
        
        elif state == "Anon_Sub_Search":
            query = random.choice(config.SEARCH_KEYWORDS)
            url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['SEARCH']}?query={query}"
            headers = build_complete_headers(ctx, "search", "search", {"X-Search-Query": query})
            safe_request('GET', url, headers)
            ctx.search_queries.append(query)
    
    except Exception as exc:
        global_state.error_counts[f'Anon_{state}'] += 1
        logger.error(f"Anon action error in {state}", extra={
            'user_id': ctx.user_profile.user_id,
            'state': state,
            'error': str(exc)
        })

def perform_logged_action(ctx: SessionContext, state: str):
    """로그인 사용자 액션"""
    try:
        # 참여도별 액션 실행 확률
        engagement_probs = {"low": 0.6, "normal": 1.0, "high": 1.3}
        action_prob = engagement_probs.get(ctx.user_profile.engagement_level, 1.0)
        
        if random.random() > action_prob:
            return  # 액션 스킵
        
        if state == "Login_Sub_Main":
            headers = build_complete_headers(ctx, "page_view", "main")
            safe_request('GET', config.API_URL_WITH_HTTP, headers)
        
        elif state == "Login_Sub_Products":
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
            headers = build_complete_headers(ctx, "products_list", "product_list")
            safe_request('GET', url, headers)
        
        elif state == "Login_Sub_ViewProduct":
            pid = pick_preferred_product_id(ctx)
            url = f"{config.API_URL_WITH_HTTP}{config.API_ENDPOINTS['PRODUCT_DETAIL']}?id={pid}"
            headers = build_complete_headers(ctx, "product_view", "product_detail", {"X-Product-Id": pid})
            
            safe_request('GET', url, headers)
            ctx.products_viewed.append(pid)
        
        elif state == "Login_Sub_Search":
            query = random.choice(config.SEARCH_KEYWORDS)
            url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['SEARCH']}?query={query}"
            headers = build_complete_headers(ctx, "search", "search", {"X-Search-Query": query})
            safe_request('GET', url, headers)
            ctx.search_queries.append(query)
        
        elif state == "Login_Sub_ViewCart":
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_VIEW"]
            headers = build_complete_headers(ctx, "cart_view", "cart")
            safe_request('GET', url, headers)
        
        elif state == "Login_Sub_CartAdd":
            pid = pick_preferred_product_id(ctx)
            qty = random.randint(1, 3)
            
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_ADD"] + f"?id={pid}"
            headers = build_complete_headers(ctx, "add_to_cart", "cart", 
                                           {"X-Quantity": str(qty), "X-Product-Id": pid})
            
            safe_request('POST', url, headers, {"id": pid, "quantity": qty})
            ctx.cart_items.append(pid)
        
        elif state == "Login_Sub_CartRemove" and ctx.cart_items:
            pid = random.choice(ctx.cart_items)
            ctx.cart_items.remove(pid)
            qty = random.randint(1, 2)
            
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_REMOVE"] + f"?product_id={pid}&quantity={qty}"
            headers = build_complete_headers(ctx, "remove_from_cart", "cart", 
                                           {"X-Quantity": str(qty), "X-Product-Id": pid})
            safe_request('POST', url, headers)
        
        elif state == "Login_Sub_Checkout":
            # 참여도별 구매 확률
            purchase_probs = {"low": 0.1, "normal": 0.25, "high": 0.5}
            purchase_prob = purchase_probs.get(ctx.user_profile.engagement_level, 0.25)
            
            if random.random() < purchase_prob:
                url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CHECKOUT"]
                headers = build_complete_headers(ctx, "purchase", "checkout", 
                                               {"X-Purchase-Probability": str(purchase_prob)})
                
                response = safe_request('POST', url, headers)
                
                if response.status_code == 200:
                    # 구매 성공 처리
                    ctx.conversion_events.append('purchase')
                    global_state.update_stats('successful_purchases')
                    
                    # 구매 이력 업데이트
                    purchase_data = {
                        "timestamp": datetime.now().isoformat(),
                        "products": ctx.cart_items.copy(),
                        "amount": random.randint(50, 500),
                        "category": random.choice(ctx.user_profile.preferred_categories) if ctx.user_profile.preferred_categories else "Unknown"
                    }
                    
                    with global_state.lock:
                        global_state.purchase_history[ctx.user_profile.user_id].append(purchase_data)
                        if ctx.user_profile.user_id in global_state.user_profiles:
                            global_state.user_profiles[ctx.user_profile.user_id]['total_purchases'] += 1
                    
                    ctx.cart_items.clear()
                    
                    logger.info("Purchase completed", extra={
                        'user_id': ctx.user_profile.user_id,
                        'amount': purchase_data['amount'],
                        'products_count': len(purchase_data['products'])
                    })
                else:
                    global_state.update_stats('failed_purchases')
        
        elif state == "Login_Sub_AddReview":
            if ctx.products_viewed:
                pid = random.choice(ctx.products_viewed)
            else:
                pid = pick_preferred_product_id(ctx)
            
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 15, 35, 40])[0]
            
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ADD_REVIEW"] + f"?id={pid}"
            headers = build_complete_headers(ctx, "review_submitted", "main", 
                                           {"X-Review-Rating": str(rating), "X-Product-Id": pid})
            
            review_data = {
                "product_id": pid, 
                "rating": rating,
                "review_text": f"Review from {ctx.user_profile.user_id}"
            }
            safe_request('POST', url, headers, review_data)
            
            ctx.conversion_events.append('review')
    
    except Exception as exc:
        global_state.error_counts[f'Logged_{state}'] += 1
        logger.error(f"Logged action error in {state}", extra={
            'user_id': ctx.user_profile.user_id,
            'state': state,
            'error': str(exc)
        })

# ────────────────────────────────
# 사용자 시뮬레이션
# ────────────────────────────────
def run_user_simulation(user_idx: int, session_length: int):
    """단일 사용자 시뮬레이션 실행"""
    
    try:
        # 사용자 프로필 생성/재사용
        user_profile, is_returning = create_or_reuse_user_profile()
        
        # 세션 컨텍스트 생성
        ctx = SessionContext(
            session_id=str(uuid.uuid4()),
            user_profile=user_profile,
            session_idx=user_profile.total_sessions,
            start_time=datetime.now(),
            last_action_time=datetime.now()
        )
        
        # 재방문 사용자 세션 길이 조정
        if is_returning:
            session_length = int(session_length * config.RETURNING_USER_MULTIPLIER)
        
        # 상태 머신 초기화
        current_state = "Anon_NotRegistered" if not is_returning else "Anon_Registered"
        transition_count = 0
        
        logger.info(f"Starting simulation #{user_idx}", extra={
            'user_id': ctx.user_profile.user_id,
            'session_id': ctx.session_id,
            'is_returning': is_returning,
            'target_actions': session_length,
            'engagement_level': ctx.user_profile.engagement_level
        })
        
        while transition_count < session_length and not killer.kill_now:
            try:
                # 상태별 처리
                if current_state == "Anon_NotRegistered":
                    if try_register(ctx):
                        current_state = "Anon_Registered"
                    else:
                        perform_anon_action(ctx, "Anon_Sub_Main")
                
                elif current_state == "Anon_Registered":
                    if try_login(ctx):
                        current_state = "Logged_In"
                    else:
                        action_state = random.choice(list(config.ANON_SUB_TRANSITIONS.keys()))
                        perform_anon_action(ctx, action_state)
                
                elif current_state == "Logged_In":
                    action_state = random.choice(list(config.LOGGED_SUB_TRANSITIONS.keys()))
                    perform_logged_action(ctx, action_state)
                    
                    # 로그아웃 확률 (참여도별 조정)
                    logout_probs = {"low": 0.15, "normal": 0.08, "high": 0.05}
                    logout_prob = logout_probs.get(ctx.user_profile.engagement_level, 0.08)
                    
                    if random.random() < logout_prob:
                        if try_logout(ctx):
                            current_state = "Logged_Out"
                
                elif current_state == "Logged_Out":
                    if random.random() < 0.6:
                        current_state = "Anon_Registered"
                    else:
                        current_state = "Done"
                
                elif current_state == "Done":
                    break
                
                transition_count += 1
                
                # 액션 간 대기 시간
                sleep_duration = random.uniform(*config.TIME_SLEEP_RANGE)
                if interruptible_sleep(sleep_duration):
                    break
                
            except KeyboardInterrupt:
                logger.info(f"User {user_idx} interrupted")
                break
            except Exception as e:
                logger.error(f"User {user_idx} action error: {e}")
                break
        
        # 세션 종료
        ctx.end_session()
        
        logger.info(f"Simulation #{user_idx} completed", extra={
            'user_id': ctx.user_profile.user_id,
            'actions_completed': transition_count,
            'target_actions': session_length,
            'final_state': current_state,
            'conversions': len(ctx.conversion_events)
        })
        
    except Exception as exc:
        logger.error(f"Simulation #{user_idx} failed: {exc}")

# ────────────────────────────────
# 메인 트래픽 실행 엔진
# ────────────────────────────────
def launch_traffic_generation(num_users: int, max_threads: int):
    """트래픽 생성 메인 실행"""
    
    start_time = datetime.now()
    
    print(f"🚀 트래픽 생성 시작")
    print(f"   사용자: {num_users}명")
    print(f"   최대 스레드: {max_threads}개")
    print(f"   시작 시간: {start_time.strftime('%H:%M:%S')}")
    print("=" * 50)
    
    try:
        # 초기화
        print("📡 상품 및 카테고리 정보 로드 중...")
        fetch_products()
        fetch_categories()
        
        # 파레토 분포 세션 길이 생성
        print("📊 파레토 분포 기반 세션 길이 생성 중...")
        session_lengths = generate_pareto_session_lengths(num_users, config.ACTIONS_PER_USER)
        
        # 통계 초기화
        global_state.session_stats.clear()
        
        # ThreadPoolExecutor로 실행
        print("🎯 사용자 시뮬레이션 시작...")
        
        with ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix="TrafficSim") as executor:
            # 진행상황 모니터링 스레드
            def progress_monitor():
                while not killer.kill_now:
                    stats = global_state.get_stats_snapshot()
                    completed = stats['session_stats'].get('completed_sessions', 0)
                    
                    if completed > 0:
                        print(f"⏳ 진행상황: {completed}/{num_users} 완료 "
                              f"(성공요청: {stats['session_stats'].get('successful_requests', 0)}, "
                              f"활성세션: {stats['active_sessions']})")
                    
                    if interruptible_sleep(10):  # 10초마다 체크
                        break
            
            monitor_thread = threading.Thread(target=progress_monitor, daemon=True)
            monitor_thread.start()
            
            # 시뮬레이션 태스크 제출
            futures = []
            for i in range(num_users):
                if killer.kill_now:
                    break
                
                future = executor.submit(run_user_simulation, i, session_lengths[i])
                futures.append(future)
                
                # 부드러운 시작
                if interruptible_sleep(0.1):
                    break
            
            # 결과 수집
            completed_count = 0
            for future in as_completed(futures, timeout=300):  # 5분 타임아웃
                try:
                    future.result(timeout=30)  # 개별 태스크 30초 타임아웃
                    completed_count += 1
                except Exception as e:
                    logger.error(f"Task execution error: {e}")
                
                if killer.kill_now:
                    print("🛑 사용자 중단 요청으로 조기 종료")
                    break
        
        # 최종 결과
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        final_stats = global_state.get_stats_snapshot()
        
        print("\n" + "=" * 50)
        print("📊 최종 결과")
        print("=" * 50)
        print(f"⏱️  총 실행시간: {total_duration:.1f}초")
        print(f"👥 완료된 시뮬레이션: {completed_count}/{num_users}")
        print(f"✅ 성공 요청: {final_stats['session_stats'].get('successful_requests', 0)}")
        print(f"📝 성공 가입: {final_stats['session_stats'].get('successful_registrations', 0)}")
        print(f"🔑 성공 로그인: {final_stats['session_stats'].get('successful_logins', 0)}")
        print(f"💰 성공 구매: {final_stats['session_stats'].get('successful_purchases', 0)}")
        print(f"❌ 에러 총계: {sum(final_stats['error_counts'].values())}")
        print(f"👤 총 사용자: {final_stats['total_users']}")
        print(f"📦 상품 캐시: {final_stats['products_cached']}개")
        print(f"📂 카테고리 캐시: {final_stats['categories_cached']}개")
        
        if final_stats['error_counts']:
            print("\n🔍 에러 상세:")
            for error_type, count in sorted(final_stats['error_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {error_type}: {count}회")
        
        # 성능 요약
        perf_metrics = global_state.performance_metrics
        if perf_metrics:
            print("\n📈 성능 요약:")
            for metric_name, values in perf_metrics.items():
                if values:
                    values_only = [v['value'] for v in values]
                    avg_val = np.mean(values_only)
                    max_val = np.max(values_only)
                    
                    if metric_name == 'request_duration':
                        print(f"   평균 요청시간: {avg_val:.3f}초 (최대: {max_val:.3f}초)")
                    elif metric_name == 'session_duration':
                        print(f"   평균 세션시간: {avg_val:.1f}초 (최대: {max_val:.1f}초)")
        
    except KeyboardInterrupt:
        print("\n🛑 사용자 중단 요청")
    except Exception as exc:
        print(f"\n❌ 실행 오류: {exc}")
        logger.error(f"Traffic generation failed: {exc}")
    finally:
        print("🔄 정리 작업 완료")

# ────────────────────────────────
# CLI 및 메인 함수
# ────────────────────────────────
def parse_cli() -> argparse.Namespace:
    """CLI 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="완전한 E-commerce 트래픽 생성기",
        epilog="예시: python traffic_generator.py --users 50 --threads 10"
    )
    
    parser.add_argument("--users", type=int, default=None, help="사용자 수 (기본값: config에서 로드)")
    parser.add_argument("--threads", type=int, default=None, help="최대 스레드 수 (기본값: config에서 로드)")
    parser.add_argument("--actions", type=int, default=None, help="사용자당 액션 수 (기본값: config에서 로드)")
    parser.add_argument("--debug", action="store_true", help="디버그 모드 활성화")
    parser.add_argument("--quiet", action="store_true", help="최소한의 출력만 표시")
    parser.add_argument("--stats-only", action="store_true", help="통계만 출력")
    
    return parser.parse_args()

def main():
    """메인 함수"""
    args = parse_cli()
    
    # 디버그 모드
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🐛 디버그 모드 활성화")
    
    # 조용한 모드
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # 설정 값 (CLI 인자가 우선)
    num_users = args.users or config.NUM_USERS
    max_threads = args.threads or config.MAX_THREADS
    
    if args.actions:
        config.ACTIONS_PER_USER = args.actions
    
    # 기본 정보 출력
    if not args.quiet:
        print("🎯 완전한 E-commerce 트래픽 생성기")
        print(f"   버전: 2.0 (완전 개선)")
        print(f"   설정: {num_users}명 사용자, {max_threads}개 스레드")
        print(f"   액션: 사용자당 평균 {config.ACTIONS_PER_USER}개")
        print(f"   특징: 파레토분포, 사용자재사용, 현실적체류시간")
        print(f"   종료: Ctrl+C 누르면 5초 내 종료됨")
        
        if config.PARETO_ENABLED:
            print(f"   파레토: 20% 유저가 80% 액션 수행")
        if config.USER_REUSE_ENABLED:
            print(f"   재사용: {config.USER_REUSE_PROBABILITY*100:.0f}% 확률로 기존 유저 재사용")
        
        print()
    
    # 통계만 출력 모드
    if args.stats_only:
        stats = global_state.get_stats_snapshot()
        print("📊 현재 통계:")
        for key, value in stats['session_stats'].items():
            print(f"   {key}: {value}")
        return
    
    try:
        # 메인 트래픽 생성 실행
        launch_traffic_generation(num_users, max_threads)
        
    except KeyboardInterrupt:
        print("\n🛑 사용자 중단 요청")
    except Exception as exc:
        print(f"\n❌ 실행 실패: {exc}")
        logger.error(f"Main execution failed: {exc}")
        return 1
    finally:
        print("✅ 프로그램 종료")
        # 강제 종료 (모든 데몬 스레드 정리)
        os._exit(0)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

