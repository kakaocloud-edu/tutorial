#!/usr/bin/env python3
"""
config.py

- config.yml 파일을 로드하여 설정을 관리합니다.
"""

import os
import yaml
import random
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Dict, Any
import threading
import uuid

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))
# 상위 디렉토리 경로 가져오기 (REST API의 상위 디렉토리는 TrafficGenerator)
parent_dir = os.path.dirname(current_dir)
# config.yml 파일의 전체 경로 설정
config_path = os.path.join(current_dir, "config.yml")

# config.yml 파일 열기
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Pub/Sub 설정
PUBSUB_ENDPOINT = config['pubsub']['endpoint']
DOMAIN_ID = config['pubsub']['domain_id']
PROJECT_ID = config['pubsub']['project_id']
TOPIC_NAME = config['pubsub']['topic_name']
TOPIC_NAME_MK = config['pubsub']['topic_name_mk']
TOPIC_DESCRIPTION = config['pubsub']['topic_description']
TOPIC_RETENTION_DURATION = config['pubsub']['topic_retention_duration']
SUB_NAME = config['pubsub']['sub_name']
CREDENTIAL_ID = config['pubsub']['credential_id']
CREDENTIAL_SECRET = config['pubsub']['credential_secret']

# Object Storage 서브스크립션 설정
OBJECT_STORAGE_SUBSCRIPTION_NAME_MK = config['object_storage_subscription']['name']
OBJECT_STORAGE_BUCKET = config['object_storage_subscription']['bucket']
EXPORT_INTERVAL_MIN = config['object_storage_subscription']['export_interval_min']
FILE_PREFIX = config['object_storage_subscription']['file_prefix']
FILE_SUFFIX = config['object_storage_subscription']['file_suffix']
CHANNEL_COUNT = config['object_storage_subscription']['channel_count']
MAX_CHANNEL_COUNT = config['object_storage_subscription']['max_channel_count']
IS_EXPORT_ENABLED = config['object_storage_subscription']['is_export_enabled']

# 로그 설정
LOG_FILENAME = config['logging']['filename']
LOG_LEVEL = config['logging']['level']

# 스레드 및 사용자 설정
NUM_USERS = config['threads']['num_users']
MAX_THREADS = config['threads']['max_threads']
ACTIONS_PER_USER = config['threads']['actions_per_user']

# API 서버 정보
API_BASE_URL = config['api']['base_url']
API_URL_WITH_HTTP = f"http://{API_BASE_URL}/"
API_ENDPOINTS = {k.upper(): v for k, v in config['api']['endpoints'].items()}

# 요청 간 대기 시간 범위 (초)
TIME_SLEEP_RANGE = (config['api']['time_sleep_range']['min'], config['api']['time_sleep_range']['max'])

# 나이 구간 임계값
AGE_THRESHOLD_YOUNG = config['age_threshold']['young']
AGE_THRESHOLD_MIDDLE = config['age_threshold']['middle']

#################################
# 추가 설정 - 현실적 트래픽 제너레이터용 (수정됨)
#################################

# 사용자 참여도 레벨 설정 (수정됨 - 구매 확률 대폭 증가)
USER_ENGAGEMENT_LEVELS = {
    'low': {
        'probability': 0.15,        # 0.25 → 0.15 (비율 감소)
        'actions_range': (3, 8),
        'sleep_multiplier': (1.5, 2.5),
        'conversion_rate': 0.25,    # 0.02 → 0.25 (12.5배 증가)
        'dwell_time_multiplier': 1.5
    },
    'medium': {
        'probability': 0.35,        # 0.55 → 0.35 (비율 감소)
        'actions_range': (8, 15),
        'sleep_multiplier': (0.8, 1.2),
        'conversion_rate': 0.45,    # 0.08 → 0.45 (5.6배 증가)
        'dwell_time_multiplier': 1.0
    },
    'high': {
        'probability': 0.50,        # 0.20 → 0.50 (2.5배 증가)
        'actions_range': (15, 30),
        'sleep_multiplier': (0.3, 0.8),
        'conversion_rate': 0.75,    # 0.15 → 0.75 (5배 증가)
        'dwell_time_multiplier': 0.7
    }
}

# 시간대별 트래픽 가중치
HOURLY_TRAFFIC_WEIGHTS = {
    0: 0.2, 1: 0.15, 2: 0.1, 3: 0.1, 4: 0.15, 5: 0.2,
    6: 0.6, 7: 0.8, 8: 1.0, 9: 1.2, 10: 1.1, 11: 1.3,
    12: 1.8, 13: 1.6, 14: 1.0, 15: 1.1, 16: 1.2, 17: 1.5,
    18: 1.7, 19: 1.8, 20: 2.0, 21: 1.9, 22: 1.5, 23: 0.8
}

# 요일별 트래픽 가중치
WEEKDAY_TRAFFIC_WEIGHTS = {
    0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.1, 5: 1.3, 6: 1.2
}

# 특가 세일 이벤트 설정
FLASH_SALE_EVENTS = {
    'morning_flash': {
        'time_range': (9, 11),
        'probability': 0.15,
        'traffic_boost': 2.5,
        'conversion_boost': 1.8,
        'name': '모닝 플래시 세일'
    },
    'lunch_special': {
        'time_range': (12, 14),
        'probability': 0.20,
        'traffic_boost': 2.0,
        'conversion_boost': 1.5,
        'name': '런치 타임 특가'
    },
    'weekend_mega': {
        'days': [5, 6],
        'time_range': (14, 18),
        'probability': 0.30,
        'traffic_boost': 3.0,
        'conversion_boost': 2.2,
        'name': '주말 메가 세일'
    },
    'evening_rush': {
        'time_range': (19, 21),
        'probability': 0.25,
        'traffic_boost': 2.2,
        'conversion_boost': 1.6,
        'name': '저녁 러시 세일'
    }
}

# 로그정규분포 체류시간 파라미터
DWELL_TIME_PARAMS = {
    'page_view': (0.8, 3.0),
    'product_view': (0.6, 15.0),
    'product_list_view': (0.7, 8.0),
    'search': (0.9, 5.0),
    'cart_view': (0.5, 10.0),
    'checkout': (0.4, 25.0),
    'add_to_cart': (0.6, 6.0),
    'review_submitted': (0.3, 18.0),
    'login': (0.7, 8.0),
    'register': (0.4, 20.0)
}

# 에러율 설정 (수정됨 - 에러율 대폭 감소)
BASE_ERROR_RATES = {
    'server_error': 0.005,      # 0.02 → 0.005 (1/4로 감소)
    'network_timeout': 0.002,   # 0.01 → 0.002 (1/5로 감소)
    'payment_failure': 0.01     # 0.05 → 0.01 (1/5로 감소)
}

# 엔드포인트별 에러 패턴 (수정됨 - 전체적으로 감소)
ENDPOINT_ERROR_RATES = {
    'checkout': {
        'payment_failure': 0.02,    # 0.05 → 0.02
        'server_error': 0.01,       # 0.03 → 0.01
        'network_timeout': 0.005    # 0.02 → 0.005
    },
    'cart': {
        'server_error': 0.005,      # 0.02 → 0.005
        'network_timeout': 0.002    # 0.01 → 0.002
    },
    'search': {
        'server_error': 0.003,      # 0.015 → 0.003
        'network_timeout': 0.002    # 0.008 → 0.002
    },
    'products': {
        'server_error': 0.002,      # 0.01 → 0.002
        'network_timeout': 0.001    # 0.005 → 0.001
    },
    'login': {
        'server_error': 0.005,      # 0.02 → 0.005
        'network_timeout': 0.003    # 0.015 → 0.003
    }
}

# 피크 시간대 설정
PEAK_HOUR_ERROR_MULTIPLIER = 1.2  # 1.5 → 1.2 (에러 증가율 감소)
PEAK_HOURS = [(12, 14), (20, 22)]

# 사용자 재사용 확률
USER_RETURN_PROBABILITY = 0.35
MAX_RECENT_USERS = 1000
RECENT_USERS_TRIM_SIZE = 500

# DB 기반 상품 정보
PRODUCT_CATEGORIES = ['Electronics', 'Fashion', 'Home', 'Gaming', 'Books']
PRODUCT_ID_RANGES = {
    'Electronics': ['101', '102', '106', '108', '118', '119'],
    'Fashion': ['103', '104', '107', '113', '117', '120', '124'],
    'Home': ['105', '114', '115', '116'],
    'Gaming': ['109', '110', '121'],
    'Books': ['111', '112', '122', '123']
}

# 기존 사용자 ID 목록
EXISTING_USER_IDS = ['u1', 'u2', 'u3', 'u4']

# 인구통계 분포
DEMOGRAPHIC_DISTRIBUTION = {
    'age_segments': {
        '18-25': 0.25,
        '26-35': 0.30,
        '36-45': 0.25,
        '46-55': 0.15,
        '56+': 0.05
    },
    'genders': {
        'M': 0.48,
        'F': 0.50,
    },
    'regions': {
        'Seoul': 0.20,
        'Busan': 0.08,
        'Incheon': 0.06,
        'Daegu': 0.05,
        'Daejeon': 0.03,
        'Gwangju': 0.03,
        'Other': 0.55
    },
    'devices': {
        'mobile': 0.65,
        'desktop': 0.30,
        'tablet': 0.05
    }
}

# User-Agent 목록
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

# 검색 키워드 풀 (카테고리별)
SEARCH_KEYWORDS_BY_CATEGORY = {
    'Electronics': ['earbuds', 'speaker', 'mouse', 'laptop', 'smartphone', 'tablet'],
    'Fashion': ['sneakers', 'backpack', 'sunglasses', 'hat', 'jeans', 'dress', 'shirt'],
    'Home': ['mug', 'fryer', 'vacuum', 'coffee', 'cleaner'],
    'Gaming': ['keyboard', 'console', 'headset', 'gaming'],
    'Books': ['programming', 'novel', 'cookbook', 'thriller', 'python', 'book']
}

#################################
# 사용자 프로필 클래스
#################################
@dataclass
class UserProfile:
    """사용자 프로필 클래스"""
    user_id: str
    session_count: int = 1
    total_purchases: int = 0
    favorite_categories: List[str] = field(default_factory=list)
    purchase_history: List[str] = field(default_factory=list)
    avg_session_duration: float = 0.0
    engagement_level: str = ""
    age_segment: str = ""
    gender: str = ""
    region: str = ""
    device: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_existing_user: bool = False
    
    def __post_init__(self):
        if not self.engagement_level:
            engagement_choice = random.choices(
                ['low', 'medium', 'high'],
                weights=[0.15, 0.35, 0.50]  # 수정됨 - high 참여도 비율 대폭 증가
            )[0]
            self.engagement_level = engagement_choice
        
        if not self.age_segment:
            self.age_segment = random.choices(
                list(DEMOGRAPHIC_DISTRIBUTION['age_segments'].keys()),
                weights=list(DEMOGRAPHIC_DISTRIBUTION['age_segments'].values())
            )[0]
        
        if not self.gender:
            self.gender = random.choices(
                list(DEMOGRAPHIC_DISTRIBUTION['genders'].keys()),
                weights=list(DEMOGRAPHIC_DISTRIBUTION['genders'].values())
            )[0]
        
        if not self.region:
            self.region = random.choices(
                list(DEMOGRAPHIC_DISTRIBUTION['regions'].keys()),
                weights=list(DEMOGRAPHIC_DISTRIBUTION['regions'].values())
            )[0]
        
        if not self.device:
            self.device = random.choices(
                list(DEMOGRAPHIC_DISTRIBUTION['devices'].keys()),
                weights=list(DEMOGRAPHIC_DISTRIBUTION['devices'].values())
            )[0]

#################################
# 상위 상태 전이 표 (수정됨 - 로그인 확률 증가)
#################################
STATE_TRANSITIONS = {
    "Anon_NotRegistered": {
        "Anon_NotRegistered": 0.2,  # 0.3 → 0.2 (감소)
        "Anon_Registered": 0.7,     # 0.5 → 0.7 (회원가입 확률 증가)
        "Unregistered": 0.0,
        "Done": 0.1                 # 0.2 → 0.1 (감소)
    },
    "Anon_Registered": {
        "Anon_Registered": 0.1,     # 0.3 → 0.1 (감소)
        "Logged_In": 0.8,           # 0.5 → 0.8 (로그인 확률 대폭 증가)
        "Unregistered": 0.05,       # 0.1 → 0.05 (감소)
        "Done": 0.05                # 0.1 → 0.05 (감소)
    },
    "Logged_In": {
        "Logged_In": 0.85,          # 0.7 → 0.85 (로그인 유지 확률 증가)
        "Logged_Out": 0.05,         # 0.1 → 0.05 (감소)
        "Unregistered": 0.05,       # 0.1 → 0.05 (감소)
        "Done": 0.05                # 0.1 → 0.05 (감소)
    },
    "Logged_Out": {
        "Unregistered": 0.1,
        "Anon_Registered": 0.1,
        "Done": 0.8
    },
    "Unregistered": {
        "Done": 1.0
    },
    "Done": {}
}

#################################
# 개선된 FSM 상태 전이 표 (ML 친화적)
#################################
FSM_TRANSITIONS = {
    'home': {
        'product_list': 0.4,
        'search': 0.3,
        'login': 0.15,
        'cart': 0.1,
        'exit': 0.05
    },
    'product_list': {
        'product_detail': 0.6,
        'search': 0.2,
        'cart': 0.1,
        'home': 0.05,
        'exit': 0.05
    },
    'product_detail': {
        'add_to_cart': 0.3,
        'product_list': 0.25,
        'related_products': 0.2,
        'reviews': 0.15,
        'exit': 0.1
    },
    'search': {
        'product_list': 0.5,
        'product_detail': 0.3,
        'refine_search': 0.15,
        'exit': 0.05
    },
    'cart': {
        'checkout': 0.4,
        'continue_shopping': 0.35,
        'remove_item': 0.15,
        'exit': 0.1
    },
    'checkout': {
        'payment': 0.7,
        'cart': 0.2,
        'exit': 0.1
    },
    'payment': {
        'success': 0.85,
        'failure': 0.15
    }
}

#################################
# 비로그인 하위머신 전이 표
#################################
ANON_SUB_TRANSITIONS = {
    "Anon_Sub_Initial": {
        "Anon_Sub_Main": 1.0,
        "Anon_Sub_Products": 0.2,
        "Anon_Sub_Categories": 0.2,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Done": 0.2
    },
    "Anon_Sub_Main": {
        "Anon_Sub_Main": 0.1,
        "Anon_Sub_Products": 0.2,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Categories": 0.2,
        "Anon_Sub_Error": 0.1,
        "Anon_Sub_Done": 0.2
    },
    "Anon_Sub_Products": {
        "Anon_Sub_ViewProduct": 0.2,
        "Anon_Sub_Products": 0.2,
        "Anon_Sub_Categories": 0.1,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Error": 0.1,
        "Anon_Sub_Done": 0.2
    },
    "Anon_Sub_ViewProduct": {
        "Anon_Sub_Products": 0.2,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Categories": 0.1,
        "Anon_Sub_Error": 0.1,
        "Anon_Sub_Done": 0.4
    },
    "Anon_Sub_Categories": {
        "Anon_Sub_CategoryList": 0.4,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Error": 0.1,
        "Anon_Sub_Done": 0.3
    },
    "Anon_Sub_CategoryList": {
        "Anon_Sub_Categories": 0.2,
        "Anon_Sub_ViewProduct": 0.3,
        "Anon_Sub_Error": 0.1,
        "Anon_Sub_Done": 0.4
    },
    "Anon_Sub_Search": {
        "Anon_Sub_ViewProduct": 0.3,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Error": 0.1,
        "Anon_Sub_Done": 0.4
    },
    "Anon_Sub_Error": {
        "Anon_Sub_Main": 0.3,
        "Anon_Sub_Products": 0.2,
        "Anon_Sub_Done": 0.5
    },
    "Anon_Sub_Done": {}
}

#################################
# 로그인 하위머신 전이 표 (수정됨 - 구매 확률 대폭 증가)
#################################
LOGGED_SUB_TRANSITIONS = {
    # 진입점
    "Login_Sub_Initial": {
        "Login_Sub_Main": 0.9,
        "Login_Sub_Error": 0.1
    },
    
    # 메인 페이지
    "Login_Sub_Main": {
        "Login_Sub_Main": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Products": 0.25,     # 0.2 → 0.25 (증가)
        "Login_Sub_ViewProduct": 0.3,   # 0.2 → 0.3 (증가)
        "Login_Sub_Search": 0.15,       # 0.1 → 0.15 (증가)
        "Login_Sub_Categories": 0.15,   # 0.1 → 0.15 (증가)
        "Login_Sub_CheckoutHistory": 0.05,  # 0.1 → 0.05 (감소)
        "Login_Sub_Error": 0.025,       # 0.1 → 0.025 (감소)
        "Login_Sub_Done": 0.025         # 0.1 → 0.025 (감소)
    },
    
    # 상품 목록
    "Login_Sub_Products": {
        "Login_Sub_Main": 0.05,         # 0.1 → 0.05 (감소)
        "Login_Sub_Products": 0.1,      # 0.2 → 0.1 (감소)
        "Login_Sub_ViewProduct": 0.4,   # 0.2 → 0.4 (2배 증가)
        "Login_Sub_Categories": 0.15,   # 0.1 → 0.15 (증가)
        "Login_Sub_Search": 0.2,        # 유지
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 상품 상세 (핵심 수정 - 구매 플로우 확률 대폭 증가)
    "Login_Sub_ViewProduct": {
        "Login_Sub_Main": 0.05,         # 0.1 → 0.05 (감소)
        "Login_Sub_ViewProduct": 0.05,  # 0.1 → 0.05 (감소)
        "Login_Sub_Products": 0.1,      # 유지
        "Login_Sub_Search": 0.1,        # 유지
        "Login_Sub_Categories": 0.05,   # 0.1 → 0.05 (감소)
        "Login_Sub_ViewCart": 0.15,     # 0.1 → 0.15 (증가)
        "Login_Sub_CartAdd": 0.4,       # 0.1 → 0.4 (4배 증가)
        "Login_Sub_Checkout": 0.15,     # 0.1 → 0.15 (증가)
        "Login_Sub_Error": 0.025,       # 0.1 → 0.025 (감소)
        "Login_Sub_Done": 0.025         # 0.1 → 0.025 (감소)
    },
    
    # 검색
    "Login_Sub_Search": {
        "Login_Sub_Main": 0.1,          # 0.2 → 0.1 (감소)
        "Login_Sub_Products": 0.2,      # 유지
        "Login_Sub_Categories": 0.1,    # 유지
        "Login_Sub_ViewProduct": 0.5,   # 0.3 → 0.5 (증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 카테고리 목록
    "Login_Sub_Categories": {
        "Login_Sub_Main": 0.1,          # 0.2 → 0.1 (감소)
        "Login_Sub_CategoryList": 0.4,  # 0.3 → 0.4 (증가)
        "Login_Sub_Search": 0.4,        # 0.3 → 0.4 (증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 특정 카테고리 상품 목록
    "Login_Sub_CategoryList": {
        "Login_Sub_Main": 0.1,          # 0.2 → 0.1 (감소)
        "Login_Sub_Categories": 0.2,    # 0.3 → 0.2 (감소)
        "Login_Sub_ViewProduct": 0.6,   # 0.3 → 0.6 (2배 증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 장바구니 보기 (핵심 수정 - 결제 확률 대폭 증가)
    "Login_Sub_ViewCart": {
        "Login_Sub_Main": 0.1,          # 0.3 → 0.1 (감소)
        "Login_Sub_CartRemove": 0.1,    # 0.2 → 0.1 (감소)
        "Login_Sub_Checkout": 0.7,      # 0.3 → 0.7 (2.3배 증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 결제 이력 보기
    "Login_Sub_CheckoutHistory": {
        "Login_Sub_Main": 0.3,          # 0.4 → 0.3 (감소)
        "Login_Sub_ViewCart": 0.3,      # 0.2 → 0.3 (증가)
        "Login_Sub_CartAdd": 0.3,       # 0.2 → 0.3 (증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 장바구니에 상품 추가 (핵심 수정 - 즉시 결제 확률 증가)
    "Login_Sub_CartAdd": {
        "Login_Sub_Main": 0.1,          # 0.2 → 0.1 (감소)
        "Login_Sub_ViewCart": 0.25,     # 0.3 → 0.25 (감소)
        "Login_Sub_Checkout": 0.6,      # 0.3 → 0.6 (2배 증가)
        "Login_Sub_Error": 0.025,       # 0.1 → 0.025 (감소)
        "Login_Sub_Done": 0.025         # 0.1 → 0.025 (감소)
    },
    
    # 장바구니 상품 제거
    "Login_Sub_CartRemove": {
        "Login_Sub_Main": 0.2,          # 0.3 → 0.2 (감소)
        "Login_Sub_ViewCart": 0.5,      # 0.4 → 0.5 (증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.25          # 0.2 → 0.25 (증가)
    },
    
    # 결제 (핵심 수정 - 성공적인 구매 완료 흐름)
    "Login_Sub_Checkout": {
        "Login_Sub_Main": 0.1,          # 0.2 → 0.1 (감소)
        "Login_Sub_CheckoutHistory": 0.4,   # 0.3 → 0.4 (증가)
        "Login_Sub_ViewCart": 0.05,     # 0.1 → 0.05 (감소)
        "Login_Sub_AddReview": 0.35,    # 0.2 → 0.35 (증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 리뷰 작성
    "Login_Sub_AddReview": {
        "Login_Sub_Main": 0.3,          # 유지
        "Login_Sub_AddReview": 0.1,     # 0.2 → 0.1 (감소)
        "Login_Sub_ViewCart": 0.2,      # 0.1 → 0.2 (증가)
        "Login_Sub_CheckoutHistory": 0.3,   # 0.2 → 0.3 (증가)
        "Login_Sub_Error": 0.05,        # 0.1 → 0.05 (감소)
        "Login_Sub_Done": 0.05          # 0.1 → 0.05 (감소)
    },
    
    # 에러
    "Login_Sub_Error": {
        "Login_Sub_Done": 1.0
    },
    
    # 종료
    "Login_Sub_Done": {}
}

#################################
# 카테고리 선호도
#################################
CATEGORY_PREFERENCE = {
    "F": {
        "young": ["Fashion", "Electronics", "Books"],
        "middle": ["Fashion", "Home", "Books"],
        "old": ["Home", "Books"]
    },
    "M": {
        "young": ["Electronics", "Gaming", "Fashion"],
        "middle": ["Electronics", "Home", "Gaming"],
        "old": ["Home", "Books"]
    }
}

#################################
# 검색어 목록
#################################
SEARCH_KEYWORDS = [
    "Bluetooth", "Laptop", "Fashion", "Camera", "Book", "Home",
    "Coffee", "Mouse", "Sneakers", "Bag", "Sunglasses", "Mug",
    "iphon", "labtop", "rayban"
]
