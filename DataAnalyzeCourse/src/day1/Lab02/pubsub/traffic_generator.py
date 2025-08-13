import os
import sys
import requests
import threading
import time
import random
import uuid
import logging
import argparse
from collections import defaultdict

# 현재 스크립트의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# config.py 경로: ../.. / Lab01 / traffic_generator
config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "Lab01", "traffic_generator"))
sys.path.append(config_path)

# config 불러오기
import config

#################################
# 전역 상품/카테고리 캐시
#################################
products_cache = []
categories_cache = []

#################################
# 로깅 설정
#################################
logging.basicConfig(
    filename=config.LOG_FILENAME,
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 로깅으로 config 값 확인
logging.info(f"Config loaded: LOG_FILENAME={config.LOG_FILENAME}, LOG_LEVEL={config.LOG_LEVEL}")
logging.info(f"API_URL_WITH_HTTP: {config.API_URL_WITH_HTTP}")
logging.info(f"Number of Users: {config.NUM_USERS}")

# Argument parsing for mode
def parse_args():
    parser = argparse.ArgumentParser(description="Traffic generator: once vs continuous")
    parser.add_argument('--mode', choices=['once','continuous'], default='once',
                        help='한번 실행(once) vs 지속 실행(continuous)')
    return parser.parse_args()

#################################
# 나이 구간 판단 함수
#################################
def get_age_segment(age: int) -> str:
    if age < config.AGE_THRESHOLD_YOUNG:
        return "young"
    elif age < config.AGE_THRESHOLD_MIDDLE:
        return "middle"
    else:
        return "old"
    
    # ✅ 카테고리 → 상품ID 인덱스
category_to_pids = defaultdict(list)

def build_category_index():
    """products_cache를 기반으로 카테고리→상품ID 인덱스 재생성"""
    category_to_pids.clear()
    for p in products_cache:
        cat = str(p.get("category", "")).strip()
        pid = str(p.get("id", "")).strip()
        if cat and pid:
            category_to_pids[cat].append(pid)

def random_pid_in_category(cat: str) -> str:
    """해당 카테고리에서 랜덤 상품ID 하나 선택 (없으면 폴백)"""
    ids = category_to_pids.get(cat, [])
    if ids:
        return random.choice(ids)
    # 폴백: 전체 products_cache에서 랜덤
    if products_cache:
        return str(random.choice(products_cache).get("id", "")).strip()
    return ""

#################################
# 상품/카테고리 데이터 가져오기
#################################
def fetch_products(api_base_url: str):
    global products_cache
    headers = {"Accept": "application/json"}
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                products_cache = data
            elif isinstance(data, dict):
                products_cache = data.get("products", [])
            else:
                products_cache = []
            logging.info(f"Fetched {len(products_cache)} products.")

            # ✅ 여기서 인덱스 재빌드 (핵심 한 줄)
            build_category_index()
            logging.info(f"Built category index for {len(category_to_pids)} categories.")

        else:
            logging.error(f"Failed to fetch products: {resp.status_code}, content={resp.text}")
            # 실패 시 인덱스를 건드리지 않음 (이전 인덱스 유지)
    except Exception as e:
        logging.error(f"Exception while fetching products: {e}")

def fetch_categories(api_base_url: str):
    global categories_cache
    headers = {"Accept": "application/json"}
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CATEGORIES"]
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                categories_cache = data
            elif isinstance(data, dict):
                categories_cache = data.get("categories", [])
            else:
                categories_cache = []
            logging.info(f"Fetched {len(categories_cache)} categories.")
        else:
            logging.error(f"Failed to fetch categories: {resp.status_code}, content={resp.text}")
    except Exception as e:
        logging.error(f"Exception while fetching categories: {e}")

#################################
# products_cache 기반 ID 선택 유틸
#################################
def _cached_product_ids() -> list:
    return [str(p.get("id")) for p in products_cache if p.get("id") not in (None, "")]

def random_product_id() -> str:
    """products_cache에서 무작위 상품 ID 선택. 비어있으면 101~124로 폴백."""
    ids = _cached_product_ids()
    if ids:
        return random.choice(ids)
    return str(random.randint(101, 124))

#################################
# Referer 헤더 포함용 유틸
#################################
def make_headers(session: requests.Session, extra: dict = None) -> dict:
    headers = {"Accept": "application/json"}
    if getattr(session, "prev_url", None):
        headers["Referer"] = session.prev_url
    if extra:
        headers.update(extra)
    return headers

#################################
# 확률 전이 공통 함수
#################################
def pick_next_state(prob_dict: dict) -> str:
    states = list(prob_dict.keys())
    probs = list(prob_dict.values())
    return random.choices(states, weights=probs, k=1)[0]

#################################
# 선호 카테고리 상품 선택 (가중치 기반)
#################################
def pick_preferred_product_id(gender: str, age_segment: str) -> str:
    if not products_cache:
        return random_product_id()

    W_PREF = getattr(config, "CATEGORY_PICK_W_PREF", 3.0)
    W_OTHER = getattr(config, "CATEGORY_PICK_W_OTHER", 1.0)
    EPS = getattr(config, "CATEGORY_PICK_EPS", 0.10)

    preferred = config.CATEGORY_PREFERENCE.get(gender, {}).get(age_segment, [])

    # ε-탐색: 일부는 완전 랜덤
    if random.random() < EPS:
        chosen = random.choice(products_cache)
        return str(chosen.get("id", "101"))

    weights = []
    for p in products_cache:
        cat = p.get("category", "")
        base = W_PREF if cat in preferred else W_OTHER
        # 가격 페널티(살짝)
        try:
            price = float(p.get("price", 0))
        except Exception:
            price = 0.0
        price_factor = 1.2 - min(max(price / 700.0, 0.0), 0.5)  # 0.7~1.2
        weights.append(base * price_factor)

    chosen = random.choices(products_cache, weights=weights, k=1)[0]
    return str(chosen.get("id", "101"))

def pick_preferred_category(gender: str, age_segment: str) -> str:
    preferred = getattr(config, "CATEGORY_PREFERENCE", {}).get(gender, {}).get(age_segment, [])
    pool = categories_cache[:] if categories_cache else []
    if not pool:
        return ""  # 안전 폴백

    # ε-탐색
    eps = getattr(config, "ANON_EPS", 0.15)
    if random.random() < eps:
        return random.choice(당구)

    w_pref = float(getattr(config, "ANON_W_PREF", 3.0))
    w_other = float(getattr(config, "ANON_W_OTHER", 1.0))
    weights = [(w_pref if c in preferred else w_other) for c in pool]
    return random.choices(pool, weights=weights, k=1)[0]

def pick_keyword_for_category(cat: str) -> str:
    # 1) 설정에 있으면 그걸 사용
    ck = getattr(config, "CATEGORY_KEYWORDS", {})
    pool = ck.get(cat, [])

    # 2) 없으면 해당 카테고리 상품명에서 어휘 추출(아주 단순)
    if not pool:
        names = [str(p.get("name","")) for p in products_cache if str(p.get("category","")) == cat]
        tokens = []
        for nm in names:
            tokens += [t.lower() for t in nm.split() if len(t) >= 3]
        tokens = list({t for t in tokens})[:20]  # 상위 20개만
        pool = tokens

    # 3) 그래도 없으면 공용 키워드 사용
    if not pool:
        pool = getattr(config, "SEARCH_KEYWORDS", []) or ["sale","new"]

    return random.choice(당구)


#################################
# ID로부터 카테고리 조회
#################################
def get_category_for_product(pid: str) -> str:
    for p in products_cache:
        if str(p.get("id")) == str(pid):
            return p.get("category", "")
    return ""

#################################
# 실제 회원가입/로그인/로그아웃/탈퇴 시도
#################################
def try_register(session: requests.Session, user_id: str, gender: str, age_segment: str) -> bool:
    headers = {"Accept": "application/json"}
    payload = {
        "user_id": user_id,
        "name": f"TestUser_{user_id}",
        "email": f"{user_id}@example.com",
        "gender": gender,
        "age": str(random.randint(18, 70))
    }
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ADD_USER"]
        r = session.post(url, data=payload, headers=headers)
        logging.info(f"[{user_id}] POST /add_user => {r.status_code}")
        return (r.status_code == 201)
    except Exception as e:
        logging.error(f"[{user_id}] register exception: {e}")
        return False

def try_login(session: requests.Session, user_id: str) -> bool:
    headers = {"Accept": "application/json"}
    payload = {"user_id": user_id}
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["LOGIN"]
        r = session.post(url, data=payload, headers=headers)
        logging.info(f"[{user_id}] POST /login => {r.status_code}")
        if 200 <= r.status_code < 300:
            # 전역헤더는 건드리지 않고, 각 요청마다 X-User-Id 부여(Referer 유지 포함)
            return True
    except Exception as e:
        logging.error(f"[{user_id}] login exception: {e}")
        return False

def try_logout(session: requests.Session, user_id: str) -> bool:
    # 전역 헤더에 남은 Referer만 살리고 X-User-Id는 보내지 않음
    headers = {"Accept": "application/json"}
    if getattr(session, "prev_url", None):
        headers["Referer"] = session.prev_url

    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["LOGOUT"]
        r = session.post(url, headers=headers)
        ok = (200 <= r.status_code < 300)
        logging.info(f"[{user_id}] POST /logout => {r.status_code}")

        if ok:
            # 방어적으로 세션 쿠키/헤더 정리
            session.headers.pop("X-User-Id", None)
            session.cookies.clear()
            session.prev_url = url
        return ok
    except Exception as e:
        logging.error(f"[{user_id}] logout exception: {e}")
        return False

def try_delete_user(session: requests.Session, user_id: str) -> bool:
    headers = {"Accept": "application/json"}
    payload = {"user_id": user_id}
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["DELETE_USER"]
        r = session.post(url, data=payload, headers=headers)
        logging.info(f"[{user_id}] POST /delete_user => {r.status_code}")
        return (200 <= r.status_code < 300)
    except Exception as e:
        logging.error(f"[{user_id}] delete_user exception: {e}")
        return False

#################################
# Bias/컨텍스트 유틸
#################################
def _normalize_probs(d: dict) -> dict:
    s = sum(d.values())
    if s <= 0:
        n = len(d)
        if n == 0:
            return d
        return {k: 1.0/n for k in d}
    return {k: v / s for k, v in d.items()}

def _session_duration(ctx: dict) -> float:
    return time.time() - ctx.get("session_start_ts", time.time())

def _apply_bias_from_config(state: str, probs: dict, ctx: dict) -> dict:
    if state != "Logged_In":
        return probs
    out = probs.copy()
    pattern_bias = getattr(config, "PATTERN_BIAS", {})
    thr = getattr(config, "BIAS_THRESHOLDS", {})

    mode = "with_goal" if ctx.get("has_cart_or_checkout") else "no_goal"
    for k, mul in pattern_bias.get('logged_in', {}).get(mode, {}).items():
        if k in out:
            out[k] *= float(mul)

    cart_cnt = ctx.get("cart_item_count", 0)
    page_depth = ctx.get("page_depth", 0)
    duration = _session_duration(ctx)
    idle = ctx.get("last_action_elapsed", 0.0)

    if cart_cnt >= thr.get("cart_has_items_min", 1):
        if "Logged_Out" in out:
            out["Logged_Out"] *= 1.3
    else:
        if "Done" in out:
            out["Done"] *= 1.2

    if (page_depth >= thr.get("deep_page_min", 6)) or (duration >= thr.get("long_session_sec", 60)):
        if "Logged_Out" in out:
            out["Logged_Out"] *= 1.15

    if idle >= thr.get("idle_slow_sec", 5):
        if "Done" in out:
            out["Done"] *= 1.1

    return _normalize_probs(out)

def _apply_sub_bias_from_config(sub_group: str, sub_state: str, probs: dict, ctx: dict) -> dict:
    sb = getattr(config, "SUB_BIAS", {}).get(sub_group, {})
    rules = sb.get(sub_state, {})
    if not rules:
        return _normalize_probs(probs)
    out = probs.copy()
    if "if_cart_item_count_lt" in rules and ctx.get("cart_item_count", 0) < rules["if_cart_item_count_lt"]:
        for k, mul in rules.get("multiply", {}).items():
            if k in out:
                out[k] *= float(mul)
    if "if_cart_item_count_gte" in rules and ctx.get("cart_item_count", 0) >= rules["if_cart_item_count_gte"]:
        for k, mul in rules.get("multiply", {}).items():
            if k in out:
                out[k] *= float(mul)
    if "if_idle_slow_sec_gte" in rules and ctx.get("last_action_elapsed", 0.0) >= rules["if_idle_slow_sec_gte"]:
        for k, mul in rules.get("multiply", {}).items():
            if k in out:
                out[k] *= float(mul)
    if "if_search_count_gte" in rules and ctx.get("search_count", 0) >= rules["if_search_count_gte"]:
        for k, mul in rules.get("multiply", {}).items():
            if k in out:
                out[k] *= float(mul)
    if "if_page_depth_gte" in rules and ctx.get("page_depth", 0) >= rules["if_page_depth_gte"]:
        for k, mul in rules.get("multiply", {}).items():
            if k in out:
                out[k] *= float(mul)
    return _normalize_probs(out)

def _tick_ctx_after_action(ctx: dict):
    now = time.time()
    ctx["last_action_elapsed"] = now - ctx.get("last_ts", now)
    ctx["last_ts"] = now
    ctx["page_depth"] = ctx.get("page_depth", 0) + 1

#################################
# 비로그인 하위 FSM
#################################
def do_anon_sub_fsm(session: requests.Session, user_unique_id: str, gender: str, age_segment: str, ctx: dict):
    sub_state = "Anon_Sub_Initial"
    while sub_state != "Anon_Sub_Done":
        logging.info(f"[{user_unique_id}] Anon Sub-FSM state = {sub_state}")
        perform_anon_sub_action(session, user_unique_id, sub_state, gender, age_segment, ctx)

        if sub_state not in config.ANON_SUB_TRANSITIONS:
            logging.warning(f"[{user_unique_id}] {sub_state} not in ANON_SUB_TRANSITIONS => break")
            break

        transitions = config.ANON_SUB_TRANSITIONS[sub_state]
        if not transitions:
            logging.warning(f"[{user_unique_id}] No next transitions => break")
            break

        biased_sub = _apply_sub_bias_from_config("anon", sub_state, dict(transitions), ctx)
        next_sub = pick_next_state(biased_sub)
        logging.info(f"[{user_unique_id}] (AnonSub) {sub_state} -> {next_sub}")
        sub_state = next_sub

        time.sleep(random.uniform(*config.TIME_SLEEP_RANGE))

def perform_anon_sub_action(session: requests.Session, user_unique_id: str, sub_state: str, gender: str, age_segment: str, ctx: dict):
    headers = make_headers(session)

    if sub_state == "Anon_Sub_Main":
        try:
            url = config.API_URL_WITH_HTTP
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET / => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Anon_Sub_Main error: {e}")

    elif sub_state == "Anon_Sub_Products":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
            resp = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /products => {resp.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Anon_Sub_Products error: {e}")

    elif sub_state == "Anon_Sub_ViewProduct":
        # ✅ 선호 카테고리 내 상품 상세 조회
        cat = pick_preferred_category(gender, age_segment)
        pid = random_pid_in_category(cat) if cat else random_product_id()
        url = f"{config.API_URL_WITH_HTTP}{config.API_ENDPOINTS['PRODUCT_DETAIL']}?id={pid}"
        try:
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /product?id={pid} [cat={cat}] => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] view product error: {err}")

    elif sub_state == "Anon_Sub_Categories":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CATEGORIES"]
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /categories => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] categories error: {err}")

    elif sub_state == "Anon_Sub_CategoryList":
        # ✅ 선호 카테고리 위주로 리스트 조회
        chosen_cat = pick_preferred_category(gender, age_segment)
        if not chosen_cat and categories_cache:
            chosen_cat = random.choice(categories_cache)
        if chosen_cat:
            cat_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['CATEGORY']}?name={chosen_cat}"
            try:
                r = session.get(cat_url, headers=headers)
                session.prev_url = cat_url
                logging.info(f"[{user_unique_id}] GET /category?name={chosen_cat} => {r.status_code}")
            except Exception as err:
                logging.error(f"[{user_unique_id}] category list error: {err}")

    elif sub_state == "Anon_Sub_Search":
        # ✅ 해당 카테고리의 상품을 '검색'하는 히스토리 생성
        cat = pick_preferred_category(gender, age_segment)
        q = pick_keyword_for_category(cat) if cat else random.choice(getattr(config, "SEARCH_KEYWORDS", ["sale"]))
        search_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['SEARCH']}?query={q}"
        try:
            r = session.get(search_url, headers=headers)
            session.prev_url = search_url
            logging.info(f"[{user_unique_id}] GET /search?query={q} [cat={cat}] => {r.status_code}")
            if 200 <= r.status_code < 300:
                ctx["search_count"] = ctx.get("search_count", 0) + 1
        except Exception as err:
            logging.error(f"[{user_unique_id}] search error: {err}")

    elif sub_state == "Anon_Sub_Error":
        try:
            err_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ERROR_PAGE"]
            r = session.get(err_url, headers=headers)
            session.prev_url = err_url
            logging.info(f"[{user_unique_id}] GET /error => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] error page fail: {err}")

    # 사용자 행동 사이의 대기 및 컨텍스트 tick
    time.sleep(random.uniform(0.5, 1.0))
    if sub_state != "Anon_Sub_Initial":
        _tick_ctx_after_action(ctx)

#################################
# 로그인 하위 FSM
#################################
def do_logged_sub_fsm(session: requests.Session,
                      user_unique_id: str,
                      gender,
                      age_segment: str,
                      ctx: dict):
    sub_state = "Login_Sub_Initial"
    while sub_state != "Login_Sub_Done":
        logging.info(f"[{user_unique_id}] Logged Sub-FSM state = {sub_state}")
        perform_logged_sub_action(session, user_unique_id, sub_state, gender, age_segment, ctx)

        if sub_state not in config.LOGGED_SUB_TRANSITIONS:
            logging.warning(f"[{user_unique_id}] {sub_state} not in LOGGED_SUB_TRANSITIONS => break")
            break

        transitions = config.LOGGED_SUB_TRANSITIONS[sub_state]
        if not transitions:
            logging.warning(f"[{user_unique_id}] No next transitions => break")
            break

        # 컨텍스트 기반 바이어스
        biased_sub = _apply_sub_bias_from_config("logged_in", sub_state, dict(transitions), ctx)
        next_sub = pick_next_state(biased_sub)
        logging.info(f"[{user_unique_id}] (LoggedSub) {sub_state} -> {next_sub}")
        sub_state = next_sub

        time.sleep(random.uniform(*config.TIME_SLEEP_RANGE))

def perform_logged_sub_action(session: requests.Session,
                              user_unique_id: str,
                              sub_state: str,
                              gender: str,
                              age_segment: str,
                              ctx: dict):
    headers = make_headers(session, {"X-User-Id": user_unique_id})

    if sub_state == "Login_Sub_Initial":
        logging.info(f"[{user_unique_id}] Login Sub-FSM initialized")

    elif sub_state == "Login_Sub_Main":
        try:
            url = config.API_URL_WITH_HTTP
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET / (logged) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_Main error: {e}")

    elif sub_state == "Login_Sub_Products":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /products (logged) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_Products error: {e}")

    elif sub_state == "Login_Sub_ViewProduct":
        pid = pick_preferred_product_id(gender, age_segment)
        url = f"{config.API_URL_WITH_HTTP}{config.API_ENDPOINTS['PRODUCT_DETAIL']}?id={pid}"
        try:
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /product?id={pid} (logged) => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] Login_Sub_ViewProduct error: {err}")

    elif sub_state == "Login_Sub_Search":
        q = random.choice(config.SEARCH_KEYWORDS)
        search_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['SEARCH']}?query={q}"
        try:
            r = session.get(search_url, headers=headers)
            session.prev_url = search_url
            logging.info(f"[{user_unique_id}] GET /search?query={q} (logged) => {r.status_code}")
            if 200 <= r.status_code < 300:
                ctx["search_count"] = ctx.get("search_count", 0) + 1
        except Exception as err:
            logging.error(f"[{user_unique_id}] Login_Sub_Search error: {err}")

    elif sub_state == "Login_Sub_Categories":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CATEGORIES"]
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /categories (logged) => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] Login_Sub_Categories error: {err}")

    elif sub_state == "Login_Sub_CategoryList":
        if categories_cache:
            preferred_cats = config.CATEGORY_PREFERENCE.get(gender, {}).get(age_segment, [])
            available_cats = [cat for cat in categories_cache if cat in preferred_cats]
            chosen_cat = random.choice(available_cats) if available_cats else random.choice(categories_cache)

            cat_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['CATEGORY']}?name={chosen_cat}"
            try:
                r = session.get(cat_url, headers=headers)
                session.prev_url = cat_url
                logging.info(f"[{user_unique_id}] GET /category?name={chosen_cat} (logged) => {r.status_code}")
            except Exception as err:
                logging.error(f"[{user_unique_id}] Login_Sub_CategoryList error: {err}")

    elif sub_state == "Login_Sub_ViewCart":
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_VIEW"]
        try:
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /cart/view => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] view cart error: {e}")

    elif sub_state == "Login_Sub_CheckoutHistory":
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CHECKOUT_HISTORY"]
        try:
            r = session.get(url, headers=headers)
            session.prev_url = url
            logging.info(f"[{user_unique_id}] GET /checkout_history => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] checkout_history error: {e}")

    elif sub_state == "Login_Sub_CartAdd":
        pid = pick_preferred_product_id(gender, age_segment)
        qty = random.randint(1,5)
        payload = {"id": pid, "quantity": str(qty)}
        try:
            add_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_ADD"]
            r = session.post(add_url, data=payload, headers=headers)
            session.prev_url = add_url
            logging.info(f"[{user_unique_id}] POST /cart/add (pid={pid}, qty={qty}) => {r.status_code}")
            if 200 <= r.status_code < 300:
                ctx["has_cart_or_checkout"] = True
                ctx["cart_item_count"] = ctx.get("cart_item_count", 0) + qty
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_CartAdd error: {e}")

    elif sub_state == "Login_Sub_CartRemove":
        view_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_VIEW"]
        try:
            vr = session.get(view_url, headers=headers)
            session.prev_url = view_url
            if vr.status_code == 200:
                cart_data = vr.json()
                items = cart_data.get("cart_items", [])
                if items:
                    chosen_item = random.choice(items)
                    rid = chosen_item["product_id"]
                    rqty = random.randint(1, chosen_item["quantity"])
                    remove_payload = {"product_id": rid, "quantity": rqty}
                    remove_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_REMOVE"]
                    rr = session.post(remove_url, data=remove_payload, headers=headers)
                    session.prev_url = remove_url
                    logging.info(f"[{user_unique_id}] POST /cart/remove (pid={rid}, qty={rqty}) => {rr.status_code}")
                    if 200 <= rr.status_code < 300:
                        ctx["cart_item_count"] = max(0, ctx.get("cart_item_count", 0) - rqty)
                else:
                    logging.info(f"[{user_unique_id}] Cart empty => skip remove")
            else:
                logging.error(f"[{user_unique_id}] GET /cart/view fail => {vr.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_CartRemove error: {e}")

    elif sub_state == "Login_Sub_Checkout":
        check_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CHECKOUT"]
        try:
            r = session.post(check_url, headers=headers)
            session.prev_url = check_url
            logging.info(f"[{user_unique_id}] POST /checkout => {r.status_code}")
            if 200 <= r.status_code < 300:
                ctx["has_cart_or_checkout"] = True
        except Exception as e:
            logging.error(f"[{user_unique_id}] checkout error: {e}")

    elif sub_state == "Login_Sub_AddReview":
        pid = pick_preferred_product_id(gender, age_segment)
        rating = random.randint(1,5)
        payload = {"product_id": pid, "rating": str(rating)}
        try:
            rev_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ADD_REVIEW"]
            r = session.post(rev_url, data=payload, headers=headers)
            session.prev_url = rev_url
            logging.info(f"[{user_unique_id}] POST /add_review (pid={pid},rating={rating}) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] add review error: {e}")

    elif sub_state == "Login_Sub_Error":
        err_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ERROR_PAGE"]
        try:
            rr = session.get(err_url, headers=headers)
            session.prev_url = err_url
            logging.info(f"[{user_unique_id}] GET /error => {rr.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_Error => {e}")

    # 사용자 행동 사이의 대기 및 컨텍스트 tick
    time.sleep(random.uniform(0.5, 1.0))
    if sub_state != "Login_Sub_Initial":
        _tick_ctx_after_action(ctx)

#################################
# do_top_level_action_and_confirm
#################################
def do_top_level_action_and_confirm(
    session: requests.Session,
    current_state: str,
    proposed_next: str,
    user_id: str,
    gender: str,
    age_segment: str
) -> str:
    """
    실제 API 호출로 회원가입/로그인/로그아웃/탈퇴 시도.
    성공 => proposed_next 반환, 실패 시 현재 상태 유지.
    """
    if current_state == "Anon_NotRegistered" and proposed_next == "Anon_Registered":
        ok = try_register(session, user_id, gender, age_segment)
        return "Anon_Registered" if ok else "Anon_NotRegistered"

    if current_state == "Anon_Registered" and proposed_next == "Logged_In":
        ok = try_login(session, user_id)
        return "Logged_In" if ok else "Anon_Registered"

    if current_state == "Logged_In" and proposed_next == "Logged_Out":
        ok = try_logout(session, user_id)
        return "Logged_Out" if ok else "Logged_In"

    if current_state == "Logged_In" and proposed_next == "Unregistered":
        ok = try_delete_user(session, user_id)
        return "Unregistered" if ok else "Logged_In"

    if current_state == "Logged_Out" and proposed_next == "Anon_Registered":
        return "Anon_Registered"

    if current_state == "Logged_Out" and proposed_next == "Unregistered":
        ok = try_delete_user(session, user_id)
        return "Unregistered" if ok else "Logged_Out"

    return proposed_next

#################################
# 사용자 전체 로직
#################################
def run_user_simulation(user_idx: int):
    session = requests.Session()
    session.prev_url = None
    session.get(config.API_URL_WITH_HTTP)

    gender = "F" if (user_idx % 2 == 0) else "M"  # 클래스 균형
    age = random.randint(18,70)
    age_segment = get_age_segment(age)

    user_unique_id = f"user_{uuid.uuid4().hex[:6]}"
    logging.info(f"[{user_unique_id}] Start simulation. gender={gender}, age={age}")

    current_state = "Anon_NotRegistered"
    transition_count = 0

    # 컨텍스트 플래그
    ctx = {
        "has_cart_or_checkout": False,
        "search_count": 0,
        "cart_item_count": 0,
        "page_depth": 0,
        "session_start_ts": time.time(),
        "last_ts": time.time(),
        "last_action_elapsed": 0.0,
    }

    while True:
        if transition_count >= config.ACTIONS_PER_USER:
            logging.info(f"[{user_unique_id}] Reached max transitions => end.")
            break

        if current_state == "Done":
            logging.info(f"[{user_unique_id}] state=Done => end.")
            break

        if current_state not in config.STATE_TRANSITIONS:
            logging.error(f"[{user_unique_id}] no transitions from {current_state} => end.")
            break

        # 1) 현재 state에 맞는 sub-FSM 먼저 실행 → ctx 갱신
        if current_state in ("Anon_NotRegistered", "Anon_Registered"):
            do_anon_sub_fsm(session, user_unique_id, gender, age_segment, ctx)
        elif current_state == "Logged_In":
            do_logged_sub_fsm(session, user_unique_id, gender, age_segment, ctx)
        # Logged_Out/Unregistered/Done 은 sub-FSM 없음

        # 2) 상위 전이 확률 계산/보정
        possible_next = dict(config.STATE_TRANSITIONS[current_state])
        if not possible_next:
            logging.warning(f"[{user_unique_id}] next_candidates empty => end.")
            break

        if current_state == "Logged_In":
            possible_next = _apply_bias_from_config(
                state=current_state,
                probs=possible_next,
                ctx=ctx
            )

        proposed_next = pick_next_state(possible_next)
        logging.info(f"[{user_unique_id}] (Top) {current_state} -> proposed={proposed_next}")

        # 3) 상위 전이 확정(실제 API 호출 포함)
        actual_next = do_top_level_action_and_confirm(
            session=session,
            current_state=current_state,
            proposed_next=proposed_next,
            user_id=user_unique_id,
            gender=gender,
            age_segment=age_segment
        )

        if actual_next != current_state:
            logging.info(f"[{user_unique_id}] => confirmed next: {actual_next}")
            if actual_next in ("Logged_Out", "Anon_NotRegistered"):
                ctx.update({
                    "has_cart_or_checkout": False,
                    "cart_item_count": 0,
                    "search_count": 0,
                    "page_depth": 0,
                    "session_start_ts": time.time(),
                    "last_ts": time.time(),
                    "last_action_elapsed": 0.0,
                })
            current_state = actual_next
            if current_state == "Unregistered":
                ctx.update({
                    "has_cart_or_checkout": False,
                    "cart_item_count": 0,
                    "search_count": 0,
                    "page_depth": 0,
                    "session_start_ts": time.time(),
                    "last_ts": time.time(),
                    "last_action_elapsed": 0.0,
                })
                logging.info(f"[{user_unique_id}] user unregistered => next=Done")
                current_state = "Done"

        transition_count += 1
        time.sleep(random.uniform(*config.TIME_SLEEP_RANGE))

    logging.info(f"[{user_unique_id}] Simulation ended. final={current_state}")

#################################
# 멀티 스레드 실행
#################################
def user_thread(idx: int, sem: threading.Semaphore):
    with sem:
        run_user_simulation(idx)

def launch_traffic(num_users, max_threads, time_sleep_range):
    # Override config values for this run
    orig_num_users        = config.NUM_USERS
    orig_max_threads      = config.MAX_THREADS
    orig_time_sleep_range = config.TIME_SLEEP_RANGE
    config.NUM_USERS      = num_users
    config.MAX_THREADS    = max_threads
    config.TIME_SLEEP_RANGE = time_sleep_range

    # 미리 캐시 갱신
    fetch_products(config.API_URL_WITH_HTTP)
    fetch_categories(config.API_URL_WITH_HTTP)
    build_category_index()

    # 스레드 스폰
    spawn_min, spawn_max = 0.01, 0.1
    sem = threading.Semaphore(max_threads)
    threads = []
    for i in range(config.NUM_USERS):
        t = threading.Thread(target=user_thread, args=(i, sem))
        threads.append(t)
        t.start()

        delay = random.uniform(spawn_min, spawn_max)
        logging.info(f"[Launch] spawned user #{i}, next in {delay:.3f}s")
        time.sleep(delay)

    for t in threads:
        t.join()

    logging.info("All user threads finished.")

    # 원래 config 값 복원
    config.NUM_USERS        = orig_num_users
    config.MAX_THREADS      = orig_max_threads
    config.TIME_SLEEP_RANGE = orig_time_sleep_range

if __name__ == "__main__":
    args = parse_args()
    if args.mode == "once":
        launch_traffic(config.NUM_USERS, config.MAX_THREADS, config.TIME_SLEEP_RANGE)
        print("[Done] Single traffic launch completed.")
    else:
        # continuous 모드: light / normal / heavy 패턴 순환
        patterns = ["light", "normal", "heavy"]
        while True:
            random.shuffle(patterns)
            for pattern in patterns:
                if pattern == "light":
                    base_factor_min, base_factor_max = 0.5, 0.8
                elif pattern == "normal":
                    base_factor_min, base_factor_max = 0.8, 1.2
                else:  # heavy
                    base_factor_min, base_factor_max = 1.2, 1.5

                factor      = random.uniform(base_factor_min, base_factor_max)
                num_users   = max(1, int(config.NUM_USERS   * factor))
                max_threads = max(1, int(config.MAX_THREADS * factor))

                base_min, base_max = config.TIME_SLEEP_RANGE
                sleep_min = base_min * random.uniform(0.8, 1.2)
                sleep_max = base_max * random.uniform(0.8, 1.2)
                time_range = (sleep_min, sleep_max)

                logging.info(
                    f"[Continuous][{pattern}] users={num_users}, "
                    f"threads={max_threads}, sleep_range=({sleep_min:.2f},{sleep_max:.2f})"
                )

                launch_traffic(num_users, max_threads, time_range)

                logging.info(f"[Continuous][{pattern}] done. sleeping 5s before next pattern")
                time.sleep(5)
