#!/usr/bin/env python3
"""
traffic_generator.py (Advanced & API-Compatible)
--------------------------------------------------
현실적인 E-commerce 트래픽 시뮬레이터.
- Flask API 서버 구조 완벽 대응 및 오류 수정
- 사용자 재사용 및 파레토 분포 기반 행동 모델링
- 실시간 연동 트래픽 볼륨 조절
- 특가 세일(Flash Sale) 시뮬레이션
- 컨텍스트(행동 이력) 기반 체류 시간 및 다음 행동 결정
"""
from __future__ import annotations
import argparse
import logging
import os
import random
import sys
import threading
import time
import uuid
from datetime import datetime, time as dt_time, timedelta
from typing import Any, Dict, List, Optional
import requests
import json

# ────────────────────────────────
# 경로 & 설정 로드
# ────────────────────────────────
try:
    from config import config
except ImportError:
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.abspath(os.path.join(CUR_DIR, "..", "..", "Lab01", "traffic_generator"))
    sys.path.append(CONFIG_PATH)
    from config import config

# ────────────────────────────────
# 로깅 설정
# ────────────────────────────────
logging.basicConfig(
    filename=config.logging.get('filename', 'traffic_generator.log'),
    level=config.logging.get('level', 'INFO').upper(),
    format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
)
logging.info(f"Traffic Generator Bootstrapped. API_BASE_URL={config.api.base_url}")

# ────────────────────────────────
# 전역 상태 및 관리자
# ────────────────────────────────
products_cache: list[dict] = []
categories_cache: list[str] = []
global_user_manager: Optional[UserManager] = None
global_sale_manager: Optional[SaleManager] = None

# ────────────────────────────────
# 유틸리티 함수
# ────────────────────────────────
def get_age_segment(age: int) -> str:
    """나이를 기반으로 연령대를 반환합니다."""
    if age < config.age_threshold.young:
        return "young"
    elif age < config.age_threshold.middle:
        return "middle"
    else:
        return "old"

# ────────────────────────────────
# 핵심 관리자 클래스
# ────────────────────────────────
class UserManager:
    """사용자 풀 관리, 신규/기존 사용자 분배, 파레토 분포 기반 세션 길이 결정"""
    def __init__(self):
        self.user_pool = [f"user_{uuid.uuid4().hex[:8]}" for _ in range(config.user_pool.size)]
        self.lock = threading.Lock()
        logging.info(f"UserManager initialized with pool size {config.user_pool.size}")

    def get_user(self) -> tuple[str, bool]:
        with self.lock:
            if random.random() < config.user_pool.reuse_rate and self.user_pool:
                return random.choice(self.user_pool), False  # 기존 유저
            
            new_user_id = f"user_{uuid.uuid4().hex[:8]}"
            if len(self.user_pool) < config.user_pool.size:
                self.user_pool.append(new_user_id)
            return new_user_id, True # 신규 유저

    def get_actions_for_user(self) -> int:
        """파레토 분포에 따라 사용자의 세션 당 액션 수를 결정"""
        actions = int(random.paretovariate(config.pareto.alpha)) + config.pareto.min_actions
        return min(actions, config.pareto.max_actions)

class SaleManager:
    """특가 세일 상태를 관리"""
    def __init__(self):
        self.is_active = False
        self.purchases_made = 0
        self.lock = threading.Lock()
        self.sale_config = config.special_sale
        try:
            self.start_time = dt_time.fromisoformat(self.sale_config.start_time)
            logging.info(f"SaleManager initialized for product {self.sale_config.product_id} at {self.sale_config.start_time}")
        except (ValueError, TypeError):
            logging.error("Invalid start_time format in config.yml. Disabling special_sale.")
            self.sale_config.enabled = False

    def check_and_update_status(self):
        if not hasattr(self, 'start_time') or not self.sale_config.enabled: return
            
        now_dt = datetime.now()
        start_dt = datetime.combine(now_dt.date(), self.start_time)
        end_dt = start_dt + timedelta(minutes=self.sale_config.duration_minutes)
        currently_active = start_dt <= now_dt < end_dt

        if currently_active and not self.is_active:
            self.is_active = True
            self.purchases_made = 0
            logging.warning(f"FLASH SALE STARTED for product {self.sale_config.product_id}!")
        elif not currently_active and self.is_active:
            self.is_active = False
            logging.warning("FLASH SALE ENDED.")

    def attempt_purchase(self) -> bool:
        if not self.is_active: return False
        with self.lock:
            if self.purchases_made < self.sale_config.max_purchases:
                self.purchases_made += 1
                logging.info(f"Successful flash sale! ({self.purchases_made}/{self.sale_config.max_purchases})")
                return True
            logging.warning("Flash sale stock depleted!")
            return False

class UserContext:
    """개별 사용자의 상태 및 행동 이력(컨텍스트) 관리"""
    def __init__(self, user_id: str, is_new: bool, region: str, device: str):
        self.user_id, self.is_new, self.region, self.device = user_id, is_new, region, device
        self.session_idx = 0
        self.viewed_categories: List[str] = []
        self.new_session()

    def new_session(self):
        self.session_idx += 1
        self.session_id = str(uuid.uuid4())
        self.is_return = "0" if self.session_idx == 1 else "1"
        self.viewed_categories = []

    def add_viewed_category(self, category: str):
        if category and category not in self.viewed_categories:
            self.viewed_categories.append(category)
        if len(self.viewed_categories) > 3: self.viewed_categories.pop(0)

def build_headers(ctx: UserContext, event_name: str, **kwargs: Any) -> dict:
    headers = {"Accept": "application/json", "X-Event-Id": str(uuid.uuid4()), "X-Event-Name": event_name, "X-User-Id": ctx.user_id, "X-Region": ctx.region, "X-Device": ctx.device}
    if 'dwell' in kwargs: headers['X-Dwell-Time'] = f"{kwargs['dwell']:.2f}"
    if 'quantity' in kwargs: headers['X-Quantity'] = str(kwargs['quantity'])
    if 'rating' in kwargs: headers['X-Review-Rating'] = str(kwargs['rating'])
    if 'context' in kwargs: headers['X-Event-Context'] = json.dumps(kwargs['context'])
    return headers

# ────────────────────────────────
# API 호출 및 액션 함수
# ────────────────────────────────
def safe_request(session: requests.Session, method: str, url: str, **kwargs: Any) -> Optional[requests.Response]:
    """타임아웃 및 예외 처리를 포함한 안전한 요청 래퍼"""
    try:
        response = session.request(method, url, timeout=5, **kwargs)
        if not response.ok:
            logging.warning(f"Request to {url} returned status {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {method} {url}: {e}")
        return None

def fetch_products():
    """서버에서 상품 목록을 가져와 전역 캐시를 채웁니다."""
    global products_cache
    try:
        url = f"http://{config.api.base_url}/{config.api.endpoints.products}"
        # BUG-FIX: 서버가 JSON을 반환하도록 Accept 헤더 추가
        headers = {"Accept": "application/json"}
        resp = safe_request(requests, 'GET', url, headers=headers)
        if resp and resp.ok:
            products_cache = resp.json()
            logging.info(f"Products fetched: {len(products_cache)}")
        else:
            logging.error(f"Failed to fetch products. Response was not OK or not valid JSON.")
            products_cache = []
    except Exception as exc:
        logging.error(f"fetch_products critical error: {exc}")
        products_cache = []

def fetch_categories():
    """서버에서 카테고리 목록을 가져와 전역 캐시를 채웁니다."""
    global categories_cache
    try:
        url = f"http://{config.api.base_url}/{config.api.endpoints.categories}"
        # BUG-FIX: 서버가 JSON을 반환하도록 Accept 헤더 추가
        headers = {"Accept": "application/json"}
        resp = safe_request(requests, 'GET', url, headers=headers)
        if resp and resp.ok:
            data = resp.json()
            # 서버 응답 형식에 맞춰 수정
            categories_cache = data.get("categories", []) if isinstance(data, dict) else data
            logging.info(f"Categories fetched: {len(categories_cache)}")
        else:
            logging.error(f"Failed to fetch categories. Response was not OK or not valid JSON.")
            categories_cache = []
    except Exception as exc:
        logging.error(f"fetch_categories critical error: {exc}")
        categories_cache = []

def get_product_category(pid: str) -> str:
    return next((p.get("category", "") for p in products_cache if str(p.get("id")) == str(pid)), "")

def pick_contextual_product_id(ctx: UserContext, gender: str, age_segment: str) -> str:
    """사용자 컨텍스트(최근 본 카테고리)를 고려하여 상품 선택"""
    if not products_cache: return ""
    if ctx.viewed_categories and random.random() < 0.6:
        cat_to_view = random.choice(ctx.viewed_categories)
        subset = [p for p in products_cache if p.get("category") == cat_to_view]
        if subset: return str(random.choice(subset).get("id"))
    
    prefs = getattr(getattr(config.category_preference, gender), age_segment)
    subset = [p for p in products_cache if p.get("category") in prefs] or products_cache
    return str(random.choice(subset).get("id")) if subset else ""

# ────────────────────────────────
# 시뮬레이션 메인 로직
# ────────────────────────────────
class UserSimulator:
    def __init__(self, user_manager: UserManager, sale_manager: SaleManager):
        self.user_manager, self.sale_manager, self.session = user_manager, sale_manager, requests.Session()
        user_id, is_new = self.user_manager.get_user()
        self.ctx = UserContext(user_id=user_id, is_new=is_new, region=random.choice(config.regions), device=random.choice(config.device_types))
        self.gender, self.age = random.choice(["F", "M"]), random.randint(18, 70)
        self.age_segment = get_age_segment(self.age)
        self.actions_to_perform = self.user_manager.get_actions_for_user()

    def run(self):
        logging.info(f"Starting simulation for user {self.ctx.user_id} (new: {self.ctx.is_new}) with {self.actions_to_perform} actions.")
        self.session.cookies.set("session_id", self.ctx.session_id)
        self.session.cookies.set("session_idx", str(self.ctx.session_idx))
        self.session.cookies.set("is_return", self.ctx.is_return)

        state = "Anon" if self.ctx.is_new else ("Logged_Out" if random.random() < 0.7 else "Anon") # 기존 유저는 70% 확률로 로그아웃 상태에서 시작
        
        for _ in range(self.actions_to_perform):
            if state == "Anon" and self.try_register(): state = "Logged_In"
            elif state == "Logged_Out":
                self.ctx.new_session()
                self.session.cookies.set("session_id", self.ctx.session_id); self.session.cookies.set("session_idx", str(self.ctx.session_idx))
                if self.try_login(): state = "Logged_In"
            elif state == "Logged_In" and random.random() < 0.05: # 5% 확률로 로그아웃
                if self.try_logout(): state = "Logged_Out"
            
            self.perform_state_action(state)
        logging.info(f"Finished simulation for user {self.ctx.user_id}.")

    def perform_state_action(self, state: str):
        event = "add_to_cart_sale" if state == "Logged_In" and self.sale_manager.is_active and random.random() < self.sale_manager.sale_config.interest_boost else \
                random.choice(["page_view", "product_view", "products_list", "search", "add_to_cart", "purchase"]) if state == "Logged_In" else \
                random.choice(["page_view", "product_view", "products_list", "search"])
        
        start_time = time.time()
        self.execute_event(event)
        
        base_sleep = random.uniform(config.api.time_sleep_range.min, config.api.time_sleep_range.max)
        dwell_factor = config.dwell_factors.get(event, 1.0)
        processing_time = time.time() - start_time
        sleep_duration = (base_sleep * dwell_factor) - processing_time
        
        if sleep_duration > 0: time.sleep(sleep_duration)

    def execute_event(self, event_name:str):
        api_url, endpoints = f"http://{config.api.base_url}", config.api.endpoints
        method, url_path, extra_headers, data = 'GET', None, {}, None

        if event_name == "page_view": url_path = "/"
        elif event_name == "products_list": url_path = f"/{endpoints.products}"
        elif event_name == "product_view":
            pid = pick_contextual_product_id(self.ctx, self.gender, self.age_segment)
            if pid:
                self.ctx.add_viewed_category(get_product_category(pid))
                url_path, extra_headers['context'] = f"/{endpoints.product_detail}?id={pid}", {'product_id': pid}
        elif event_name in ["add_to_cart", "add_to_cart_sale"]:
            is_sale = event_name == "add_to_cart_sale"
            pid = self.sale_manager.sale_config.product_id if is_sale else pick_contextual_product_id(self.ctx, self.gender, self.age_segment)
            if pid and (not is_sale or self.sale_manager.attempt_purchase()):
                qty = 1 if is_sale else random.randint(1, 3)
                method, url_path = 'POST', f"/{endpoints.cart_add}"
                data, extra_headers = {'id': pid, 'quantity': qty}, {'quantity': qty, 'context': {'product_id': pid}}
        
        if url_path:
            final_headers = build_headers(self.ctx, event_name, **extra_headers)
            safe_request(self.session, method, api_url + url_path, headers=final_headers, data=data)

    def try_register(self) -> bool:
        url = f"http://{config.api.base_url}/{config.api.endpoints.add_user}"
        payload = {"user_id": self.ctx.user_id, "name": f"Test_{self.ctx.user_id}", "email": f"{self.ctx.user_id}@example.com", "gender": self.gender, "age": str(self.age)}
        headers = build_headers(self.ctx, 'register')
        resp = safe_request(self.session, 'POST', url, headers=headers, data=payload)
        return resp is not None and resp.status_code == 201

    def try_login(self) -> bool:
        url = f"http://{config.api.base_url}/{config.api.endpoints.login}"
        payload = {"user_id": self.ctx.user_id}
        headers = build_headers(self.ctx, 'login')
        resp = safe_request(self.session, 'POST', url, headers=headers, data=payload)
        # BUG-FIX: .ok는 2xx, 3xx를 True로 간주. 명시적으로 2xx만 성공으로 처리.
        return resp is not None and 200 <= resp.status_code < 300

    def try_logout(self) -> bool:
        url = f"http://{config.api.base_url}/{config.api.endpoints.logout}"
        headers = build_headers(self.ctx, 'logout')
        resp = safe_request(self.session, 'POST', url, headers=headers)
        return resp is not None and 200 <= resp.status_code < 300

# ────────────────────────────────
# 스레드 실행 및 메인 함수
# ────────────────────────────────
def launch_traffic(num_users: int, max_threads: int):
    semaphore, threads = threading.Semaphore(max_threads), []
    def _thread_wrapper():
        with semaphore:
            if global_user_manager and global_sale_manager:
                UserSimulator(global_user_manager, global_sale_manager).run()

    for i in range(num_users):
        t = threading.Thread(target=_thread_wrapper, daemon=True, name=f"UserSim-{i+1}")
        threads.append(t); t.start()
        time.sleep(random.uniform(0.01, 0.1))
    for t in threads: t.join()

def main():
    global global_user_manager, global_sale_manager
    fetch_products(); fetch_categories()
    
    global_user_manager, global_sale_manager = UserManager(), SaleManager()
    
    if config.special_sale.get('enabled', False):
        def sale_checker():
            while True:
                global_sale_manager.check_and_update_status()
                time.sleep(1)
        threading.Thread(target=sale_checker, daemon=True, name="SaleManagerThread").start()
    
    parser = argparse.ArgumentParser(); parser.add_argument("--mode", choices=["once", "continuous"], default="continuous")
    args = parser.parse_args()
    
    if args.mode == 'once':
         launch_traffic(config.threads.num_users, config.threads.max_threads)
         logging.warning("Finished 'once' mode execution.")
    else:
        while True:
            current_hour = datetime.now().hour
            segment_config = config.time_segments
            current_segment_name = next((name for name, segment in segment_config.__dict__.items() if segment.start <= current_hour < segment.end), "night")
            
            segment_factors_config = getattr(config.time_segments, current_segment_name)
            factors = segment_factors_config.factor_range
            factor = random.uniform(factors[0], factors[1])
            
            n_users = max(1, int(config.threads.num_users * factor))
            n_threads = max(1, int(config.threads.max_threads * factor))

            logging.warning(f"[{current_segment_name.upper()}] Starting new wave. Users: {n_users}, Threads: {n_threads}")
            launch_traffic(n_users, n_threads)
            logging.info("Wave finished. Waiting for 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()
