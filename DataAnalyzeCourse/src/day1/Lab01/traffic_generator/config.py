#!/usr/bin/env python3
"""
config.py (Enhanced Version)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
개선된 YAML 설정을 읽어 전역 상수로 노출
- 시계열 트래픽 설정
- 파레토 분포 설정  
- 특가 세일 이벤트 설정
- 사용자 재사용 설정
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# ────────────────────────────────
# YAML 로드
# ────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
CFG_FILE = BASE_DIR / "config.yml"

with CFG_FILE.open("r", encoding="utf-8") as fp:
    _cfg = yaml.safe_load(fp)

# ────────────────────────────────
# Pub/Sub (실습용)
# ────────────────────────────────
PUBSUB_ENDPOINT: str = _cfg["pubsub"]["endpoint"]
DOMAIN_ID: str = _cfg["pubsub"]["domain_id"]
PROJECT_ID: str = _cfg["pubsub"]["project_id"]
TOPIC_NAME: str = _cfg["pubsub"]["topic_name"]
TOPIC_NAME_MK: str = _cfg["pubsub"]["topic_name_mk"]
TOPIC_DESCRIPTION: str = _cfg["pubsub"]["topic_description"]
TOPIC_RETENTION_DURATION: str = _cfg["pubsub"]["topic_retention_duration"]
SUB_NAME: str = _cfg["pubsub"]["sub_name"]
CREDENTIAL_ID: str = _cfg["pubsub"]["credential_id"]
CREDENTIAL_SECRET: str = _cfg["pubsub"]["credential_secret"]

# ────────────────────────────────
# Object Storage 서브스크립션
# ────────────────────────────────
OSS = _cfg["object_storage_subscription"]
OBJECT_STORAGE_SUBSCRIPTION_NAME_MK: str = OSS["name"]
OBJECT_STORAGE_BUCKET: str = OSS["bucket"]
EXPORT_INTERVAL_MIN: int = OSS["export_interval_min"]
FILE_PREFIX: str = OSS["file_prefix"]
FILE_SUFFIX: str = OSS["file_suffix"]
CHANNEL_COUNT: int = OSS["channel_count"]
MAX_CHANNEL_COUNT: int = OSS["max_channel_count"]
IS_EXPORT_ENABLED: bool = OSS["is_export_enabled"]

# ────────────────────────────────
# 로깅
# ────────────────────────────────
LOG_FILENAME: str = _cfg["logging"]["filename"]
LOG_LEVEL: str = _cfg["logging"]["level"].upper()

# ────────────────────────────────
# 스레드 / 사용자 설정
# ────────────────────────────────
NUM_USERS: int = _cfg["threads"]["num_users"]
MAX_THREADS: int = _cfg["threads"]["max_threads"]
ACTIONS_PER_USER: int = _cfg["threads"]["actions_per_user"]

# ────────────────────────────────
# API
# ────────────────────────────────
API_BASE_URL: str = _cfg["api"]["base_url"].rstrip("/")
API_URL_WITH_HTTP: str = f"http://{API_BASE_URL}/"
API_ENDPOINTS = {k.upper(): v for k, v in _cfg["api"]["endpoints"].items()}
TIME_SLEEP_RANGE: tuple[float, float] = (
    _cfg["api"]["time_sleep_range"]["min"],
    _cfg["api"]["time_sleep_range"]["max"],
)

# ────────────────────────────────
# 기본 파라미터
# ────────────────────────────────
AGE_THRESHOLD_YOUNG: int = _cfg["age_threshold"]["young"]
AGE_THRESHOLD_MIDDLE: int = _cfg["age_threshold"]["middle"]

REGIONS: list[str] = _cfg.get("regions", ["KR"])
DEVICE_TYPES: list[str] = _cfg.get("device_types", ["Mobile", "PC"])

DWELL_TIME_RANGE: tuple[float, float] = (
    _cfg["dwell_time_range"]["min"],
    _cfg["dwell_time_range"]["max"],
)

# ────────────────────────────────
# 시간대 & 부하 계수 (개선됨)
# ────────────────────────────────
TIME_SEGMENTS = {}
SEGMENT_FACTORS = {}

if "time_segments" in _cfg:
    for name, seg in _cfg["time_segments"].items():
        TIME_SEGMENTS[name] = (seg["start"], seg["end"])
        SEGMENT_FACTORS[name] = tuple(seg["factor_range"])

# ────────────────────────────────
# 개선된 기능 설정
# ────────────────────────────────
ENHANCED_FEATURES = _cfg.get("enhanced_features", {})

# 파레토 분포 설정
PARETO_ENABLED: bool = ENHANCED_FEATURES.get("pareto_distribution", {}).get("enabled", True)
PARETO_ALPHA: float = ENHANCED_FEATURES.get("pareto_distribution", {}).get("alpha", 1.16)

# 사용자 재사용 설정
USER_REUSE_ENABLED: bool = ENHANCED_FEATURES.get("user_reuse", {}).get("enabled", True)
USER_REUSE_PROBABILITY: float = ENHANCED_FEATURES.get("user_reuse", {}).get("probability", 0.3)

# 특가 세일 설정
SALE_EVENTS_ENABLED: bool = ENHANCED_FEATURES.get("sale_events", {}).get("enabled", True)
SALE_EVENTS_CONFIG = ENHANCED_FEATURES.get("sale_events", {})

# 참여도 레벨 가중치
ENGAGEMENT_WEIGHTS: list[float] = ENHANCED_FEATURES.get("engagement_levels", {}).get("weights", [0.2, 0.6, 0.2])

# 현실적 체류 시간 설정
REALISTIC_DWELL_ENABLED: bool = ENHANCED_FEATURES.get("realistic_dwell_times", {}).get("enabled", True)
USE_LOGNORMAL_DWELL: bool = ENHANCED_FEATURES.get("realistic_dwell_times", {}).get("use_lognormal", True)

# ────────────────────────────────
# 상태전이 및 FSM 설정
# ────────────────────────────────
STATE_TRANSITIONS: Dict[str, Dict[str, float]] = {
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
    "Done": {},
}

ANON_SUB_TRANSITIONS: Dict[str, Dict[str, float]] = {
    "Anon_Sub_Main": {
        "Anon_Sub_Main": 0.2,
        "Anon_Sub_Products": 0.3,
        "Anon_Sub_Categories": 0.2,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Error": 0.1,
    },
    "Anon_Sub_Products": {
        "Anon_Sub_ViewProduct": 0.4,
        "Anon_Sub_Categories": 0.2,
        "Anon_Sub_Search": 0.2,
        "Anon_Sub_Main": 0.2,
    },
    "Anon_Sub_ViewProduct": {
        "Anon_Sub_ViewProduct": 0.3,
        "Anon_Sub_Products": 0.3,
        "Anon_Sub_Main": 0.2,
        "Anon_Sub_Search": 0.2,
    },
    "Anon_Sub_Categories": {
        "Anon_Sub_CategoryList": 0.5,
        "Anon_Sub_Products": 0.3,
        "Anon_Sub_Main": 0.2,
    },
    "Anon_Sub_CategoryList": {
        "Anon_Sub_ViewProduct": 0.4,
        "Anon_Sub_Categories": 0.3,
        "Anon_Sub_Main": 0.3,
    },
    "Anon_Sub_Search": {
        "Anon_Sub_ViewProduct": 0.4,
        "Anon_Sub_Products": 0.3,
        "Anon_Sub_Main": 0.3,
    },
    "Anon_Sub_Error": {
        "Anon_Sub_Main": 0.8,
        "Done": 0.2,
    },
}

LOGGED_SUB_TRANSITIONS: Dict[str, Dict[str, float]] = {
    "Login_Sub_Main": {
        "Login_Sub_Products": 0.3,
        "Login_Sub_Categories": 0.2,
        "Login_Sub_Search": 0.2,
        "Login_Sub_ViewCart": 0.15,
        "Login_Sub_Main": 0.15,
    },
    "Login_Sub_Products": {
        "Login_Sub_ViewProduct": 0.4,
        "Login_Sub_Categories": 0.2,
        "Login_Sub_Search": 0.2,
        "Login_Sub_Main": 0.2,
    },
    "Login_Sub_ViewProduct": {
        "Login_Sub_CartAdd": 0.3,
        "Login_Sub_ViewProduct": 0.25,
        "Login_Sub_AddReview": 0.15,
        "Login_Sub_Products": 0.15,
        "Login_Sub_Main": 0.15,
    },
    "Login_Sub_Categories": {
        "Login_Sub_CategoryList": 0.5,
        "Login_Sub_Products": 0.3,
        "Login_Sub_Main": 0.2,
    },
    "Login_Sub_CategoryList": {
        "Login_Sub_ViewProduct": 0.4,
        "Login_Sub_Categories": 0.3,
        "Login_Sub_Main": 0.3,
    },
    "Login_Sub_Search": {
        "Login_Sub_ViewProduct": 0.4,
        "Login_Sub_Products": 0.3,
        "Login_Sub_Main": 0.3,
    },
    "Login_Sub_ViewCart": {
        "Login_Sub_Checkout": 0.4,
        "Login_Sub_CartRemove": 0.2,
        "Login_Sub_Products": 0.2,
        "Login_Sub_Main": 0.2,
    },
    "Login_Sub_CartAdd": {
        "Login_Sub_ViewCart": 0.4,
        "Login_Sub_Checkout": 0.3,
        "Login_Sub_Products": 0.15,
        "Login_Sub_Main": 0.15,
    },
    "Login_Sub_CartRemove": {
        "Login_Sub_ViewCart": 0.5,
        "Login_Sub_Products": 0.3,
        "Login_Sub_Main": 0.2,
    },
    "Login_Sub_Checkout": {
        "Login_Sub_AddReview": 0.3,
        "Login_Sub_Main": 0.4,
        "Login_Sub_Products": 0.3,
    },
    "Login_Sub_AddReview": {
        "Login_Sub_Products": 0.4,
        "Login_Sub_Main": 0.6,
    },
    "Login_Sub_Error": {
        "Login_Sub_Main": 0.8,
        "Done": 0.2,
    },
}

# ────────────────────────────────
# 카테고리 선호도 및 검색 키워드
# ────────────────────────────────
CATEGORY_PREFERENCE: Dict[str, Dict[str, List[str]]] = {
    "F": {
        "young": ["Fashion", "Electronics", "Books"],
        "middle": ["Fashion", "Home", "Books", "Electronics"],
        "old": ["Home", "Books", "Fashion"],
    },
    "M": {
        "young": ["Electronics", "Gaming", "Fashion", "Books"],
        "middle": ["Electronics", "Home", "Gaming", "Books"],
        "old": ["Home", "Books", "Electronics"],
    },
}

SEARCH_KEYWORDS: List[str] = [
    "Bluetooth", "Laptop", "Fashion", "Camera", "Book", "Home", "Coffee", 
    "Mouse", "Sneakers", "Bag", "Sunglasses", "Mug", "iPhone", "Gaming",
    "Headphone", "Watch", "Keyboard", "Monitor", "Speaker", "Tablet",
    "Dress", "Shirt", "Jeans", "Shoes", "Jacket", "Hat", "Perfume",
]

# ────────────────────────────────
# 페이지별 기본 체류시간 설정 (초)
# ────────────────────────────────
PAGE_DWELL_TIMES: Dict[str, Tuple[float, float]] = {
    "main": (2.0, 8.0),
    "product_list": (3.0, 15.0),
    "product_detail": (5.0, 30.0),
    "cart": (2.0, 10.0),
    "checkout": (10.0, 60.0),
    "search": (2.0, 12.0),
    "category": (3.0, 18.0),
    "login": (3.0, 10.0),
    "register": (5.0, 20.0),
}

# ────────────────────────────────
# 특가 세일 기본 상품 ID 범위
# ────────────────────────────────
PRODUCT_ID_RANGE: Tuple[int, int] = (101, 124)
SALE_PRODUCT_IDS: List[int] = list(range(105, 115))  # 세일 대상 상품들
