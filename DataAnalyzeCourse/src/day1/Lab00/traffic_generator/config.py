#!/usr/bin/env python3
"""
config.py

- config.yml 파일을 로드하여 설정을 관리합니다.
"""

import os
import yaml

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))
# 상위 디렉토리 경로 가져오기 (REST API의 상위 디렉토리는 TrafficGenerator)
parent_dir = os.path.dirname(current_dir)
# config.yml 파일의 전체 경로 설정
config_path = os.path.join(parent_dir, "config.yml")

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
        "Anon_Sub_Main": 0.2,
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
    "Login_Sub_Initial": {
        "Login_Sub_ViewCart": 0.2,
        "Login_Sub_CheckoutHistory": 0.1,
        "Login_Sub_CartAdd": 0.2,
        "Login_Sub_CartRemove": 0.1,
        "Login_Sub_Checkout": 0.1,
        "Login_Sub_AddReview": 0.1,
        "Login_Sub_Error": 0.1,
        "Login_Sub_Done": 0.1
    },
    "Login_Sub_ViewCart": {
        "Login_Sub_ViewCart": 0.1,
        "Login_Sub_CartAdd": 0.2,
        "Login_Sub_CartRemove": 0.2,
        "Login_Sub_Checkout": 0.1,
        "Login_Sub_Error": 0.1,
        "Login_Sub_Done": 0.3
    },
    "Login_Sub_CheckoutHistory": {
        "Login_Sub_CheckoutHistory": 0.1,
        "Login_Sub_ViewCart": 0.2,
        "Login_Sub_CartAdd": 0.1,
        "Login_Sub_Error": 0.1,
        "Login_Sub_Done": 0.5
    },
    "Login_Sub_CartAdd": {
        "Login_Sub_CartAdd": 0.1,
        "Login_Sub_ViewCart": 0.3,
        "Login_Sub_Checkout": 0.1,
        "Login_Sub_Error": 0.1,
        "Login_Sub_Done": 0.4
    },
    "Login_Sub_CartRemove": {
        "Login_Sub_CartRemove": 0.1,
        "Login_Sub_ViewCart": 0.3,
        "Login_Sub_Checkout": 0.1,
        "Login_Sub_Error": 0.1,
        "Login_Sub_Done": 0.4
    },
    "Login_Sub_Checkout": {
        "Login_Sub_Checkout": 0.0,
        "Login_Sub_CheckoutHistory": 0.2,
        "Login_Sub_ViewCart": 0.2,
        "Login_Sub_AddReview": 0.1,
        "Login_Sub_Error": 0.1,
        "Login_Sub_Done": 0.4
    },
    "Login_Sub_AddReview": {
        "Login_Sub_AddReview": 0.1,
        "Login_Sub_ViewCart": 0.2,
        "Login_Sub_CheckoutHistory": 0.1,
        "Login_Sub_Error": 0.1,
        "Login_Sub_Done": 0.5
    },
    "Login_Sub_Error": {
        "Login_Sub_ViewCart": 0.2,
        "Login_Sub_AddReview": 0.1,
        "Login_Sub_Checkout": 0.1,
        "Login_Sub_Done": 0.6
    },
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
    "cofee", "blu tooth", "iphon", "labtop", "rayban"
]
