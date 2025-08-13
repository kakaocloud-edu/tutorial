#!/usr/bin/env python3
"""
config.py

- config.yml 파일을 로드하여 설정을 관리합니다.
"""
_BOOST_APPLIED = False

import os
import yaml

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
# 상위 상태 전이 표
#################################
STATE_TRANSITIONS = {
    "Anon_NotRegistered": {
        "Anon_NotRegistered": 0.3,
        "Anon_Registered": 0.5,
        "Unregistered": 0.0,
        "Done": 0.2
    },
    "Anon_Registered": {
        "Anon_Registered": 0.3,
        "Logged_In": 0.5,
        "Unregistered": 0.1,
        "Done": 0.1
    },
    "Logged_In": {
        "Logged_In": 0.7,
        "Logged_Out": 0.1,
        "Unregistered": 0.1,
        "Done": 0.1
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
# 로그인 하위머신 전이 표
#################################
LOGGED_SUB_TRANSITIONS = {
    # 진입점
    "Login_Sub_Initial": {
        "Login_Sub_Main": 0.95,
        "Login_Sub_Error": 0.05
    },
    
    # 메인 페이지
    "Login_Sub_Main": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_Products": 0.2,
        "Login_Sub_ViewProduct": 0.2,
        "Login_Sub_Search": 0.2,
        "Login_Sub_Categories": 0.1,
        "Login_Sub_CheckoutHistory": 0.1,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 상품 목록
    "Login_Sub_Products": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_Products": 0.1,
        "Login_Sub_ViewProduct": 0.4,
        "Login_Sub_Categories": 0.1,
        "Login_Sub_Search": 0.2,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 상품 상세
    "Login_Sub_ViewProduct": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_ViewProduct": 0.1,
        "Login_Sub_Products": 0.1,
        "Login_Sub_Search": 0.1,
        "Login_Sub_Categories": 0.1,
        "Login_Sub_ViewCart": 0.1,
        "Login_Sub_CartAdd": 0.2,
        "Login_Sub_Checkout": 0.1,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 검색
    "Login_Sub_Search": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_Products": 0.2, 
        "Login_Sub_Categories": 0.2, 
        "Login_Sub_ViewProduct": 0.4,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 카테고리 목록
    "Login_Sub_Categories": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_CategoryList": 0.5,
        "Login_Sub_Search": 0.3,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 특정 카테고리 상품 목록
    "Login_Sub_CategoryList": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_Categories": 0.3,
        "Login_Sub_ViewProduct": 0.5,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 장바구니 보기
    "Login_Sub_ViewCart": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_CartRemove": 0.3,
        "Login_Sub_Checkout": 0.5,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 결제 이력 보기
    "Login_Sub_CheckoutHistory": {
        "Login_Sub_Main": 0.55,
        "Login_Sub_ViewCart": 0.2,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.2
    },
    
    # 장바구니에 상품 추가
    "Login_Sub_CartAdd": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_ViewCart": 0.4,
        "Login_Sub_Checkout": 0.4,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 장바구니 상품 제거
    "Login_Sub_CartRemove": {
        "Login_Sub_Main": 0.25,
        "Login_Sub_ViewCart": 0.5,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.2
    },
    
    # 결제
    "Login_Sub_Checkout": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_CheckoutHistory": 0.4,
        "Login_Sub_ViewCart": 0.1,
        "Login_Sub_AddReview": 0.3,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.1
    },
    
    # 리뷰 작성
    "Login_Sub_AddReview": {
        "Login_Sub_Main": 0.05,
        "Login_Sub_AddReview": 0.2,
        "Login_Sub_ViewCart": 0.1,
        "Login_Sub_CheckoutHistory": 0.3,
        "Login_Sub_Error": 0.05,
        "Login_Sub_Done": 0.3
    },
    
    # 에러
    "Login_Sub_Error": {
        "Login_Sub_Done": 1.0
    },
    
    # 종료
    "Login_Sub_Done": {}
}

def _renormalize(d: dict) -> dict:
    s = sum(d.values())
    if s <= 0:
        # 모두 0이면 균등 분배
        n = len(d)
        return {k: (1.0 / n) for k in d} if n else d
    return {k: v / s for k, v in d.items()}

def boost_checkout_and_review(
    transitions: dict,
    checkout_mul: float = 1.2,
    review_mul: float = 1.5
):
    for state, nxt in transitions.items():
        if not isinstance(nxt, dict):
            continue
        # 값 곱하기
        for k in list(nxt.keys()):
            if k == "Login_Sub_Checkout":
                nxt[k] = float(nxt[k]) * checkout_mul
            elif k == "Login_Sub_AddReview":
                nxt[k] = float(nxt[k]) * review_mul
        # 상태별 정규화
        transitions[state] = _renormalize(nxt)

# 적용
if not _BOOST_APPLIED:
    boost = config.get('boost', {})
    checkout_mul = float(boost.get('checkout_mul', 1.2))
    review_mul   = float(boost.get('review_mul', 1.5))
    boost_checkout_and_review(LOGGED_SUB_TRANSITIONS, checkout_mul=checkout_mul, review_mul=review_mul)
    _BOOST_APPLIED = True

#################################
# 카테고리 선호도
#################################
CATEGORY_PREFERENCE = {
    "F": {
        "young": ["Fashion", "Books"],
        "middle": ["Fashion", "Home", "Books"],
        "old": ["Home", "Books"]
    },
    "M": {
        "young": ["Electronics", "Gaming"],
        "middle": ["Electronics", "Home", "Gaming"],
        "old": ["Books"]
    }
}

#################################
# 검색어 목록
#################################
SEARCH_KEYWORDS = [
    "Bluetooth", "Laptop", "Fashion", "Camera", "Book", "Home",
    "Coffee", "Mouse", "Sneakers", "Bag", "Sunglasses", "Mug",
    "cofee", "blu tooth", "iphon", "labtop", "rayban"
]

PATTERN_BIAS = config.get('pattern_bias', {})
BIAS_THRESHOLDS = config.get('bias_thresholds', {})
SUB_BIAS       = config.get('sub_bias', {})

CATEGORY_PICK_W_PREF = 4.5
CATEGORY_PICK_EPS = 0.1
CATEGORY_PICK_W_OTHER = 1.0

ANON_W_PREF = 3.0        # 익명 단계에서 선호 카테고리 가중치
ANON_W_OTHER = 1.0       # 비선호 가중치
ANON_EPS = 0.15          # ε-탐색(무작위 섞기)

# 선택: 카테고리별 검색 키워드 풀 (없으면 상품명에서 자동 추출)
CATEGORY_KEYWORDS = {
    "Electronics": ["mouse", "earbuds", "speaker", "tablet", "laptop", "phone"],
    "Fashion": ["sneakers", "dress", "bag"],
    "Home": ["mug", "fryer", "coffee"],
    "Gaming": ["keyboard", "console", "headset"],
    "Books": ["book", "novel"]
}
