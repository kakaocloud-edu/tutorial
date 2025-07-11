import os
import sys
import requests
import threading
import time
import random
import uuid
import logging
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# config.py가 위치한 경로:
# 현재 디렉토리에서 두 단계 위로 이동한 후 Lab00/traffic_generator 디렉토리로 이동
config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "Lab01", "traffic_generator"))

# 절대경로 지정
sys.path.append(config_path)

# config.py 불러오기
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
# 페이지 체류 시간 범위 (초)
#################################
TIME_SEGMENTS   = config.TIME_SEGMENTS
SEGMENT_FACTORS = config.SEGMENT_FACTORS
DWELL_TIME_RANGE = config.DWELL_TIME_RANGE

#################################
# 지역별 시간존
#################################

REGION_TIMEZONES = {
    'KR': 'Asia/Seoul',
    'US': 'America/New_York',
    'AU': 'Australia/Sydney',
    'UK': 'Europe/London',
}

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

#################################
# 시간대 판단 함수 및 부하 계수
#################################
def get_time_segment(hour: int) -> str:
    """
    config.TIME_SEGMENTS 에 정의된 구간 중
    hour 가 속한 segment(name)를 리턴
    """
    for segment, (start, end) in TIME_SEGMENTS.items():
        # 일반적인 구간 (start < end)
        if start < end and start <= hour < end:
            return segment
        # 자정을 넘기는 구간 (start > end)
        if start > end and (hour >= start or hour < end):
            return segment
    return "night"

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
        else:
            logging.error(f"Failed to fetch products: {resp.status_code}, content={resp.text}")
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
# 확률 전이 공통 함수
#################################
def pick_next_state(prob_dict: dict) -> str:
    states = list(prob_dict.keys())
    probs = list(prob_dict.values())
    return random.choices(states, weights=probs, k=1)[0]

#################################
# 선호 카테고리 상품 선택
#################################
def pick_preferred_product_id(gender: str, age_segment: str) -> str:
    if not products_cache:
        return str(random.randint(101, 124))
    cat_list = config.CATEGORY_PREFERENCE.get(gender, {}).get(age_segment, [])
    filtered = [p for p in products_cache if p.get("category", "") in cat_list]
    if filtered:
        chosen = random.choice(filtered)
        return chosen.get("id", "101")
    else:
        chosen = random.choice(products_cache)
        return chosen.get("id", "101")

#################################
# ID로부터 카테고리 조회 유틸
#################################
def get_category_for_product(pid: str) -> str:
    """
    products_cache 에서 id==pid 인 상품을 찾아
    'category' 값을 반환합니다.
    못 찾으면 빈 문자열 반환.
    """
    for p in products_cache:
        # p['id'] 가 int 혹은 str 일 수 있으니 str 비교
        if str(p.get("id")) == str(pid):
            return p.get("category", "")
    return ""

#################################
# 실제 회원가입/로그인/로그아웃/탈퇴 시도
#################################
def try_register(session: requests.Session, user_id: str, gender: str, age_segment: str, region: str, device: str) -> bool:
    headers = {"Accept": "application/json"}
    payload = {
        "user_id": user_id,
        "name": f"TestUser_{user_id}",
        "email": f"{user_id}@example.com",
        "gender": gender,
        "age": str(random.randint(18, 70)),
        "region": region,
        "device": device
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
            # 헤더에 user_id 추가
            session.headers.update({"X-User-Id": user_id})
            return True
    except Exception as e:
        logging.error(f"[{user_id}] login exception: {e}")
        return False

def try_logout(session: requests.Session, user_id: str) -> bool:
    headers = {"Accept": "application/json"}
    try:
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["LOGOUT"]
        r = session.post(url, headers=headers)
        logging.info(f"[{user_id}] POST /logout => {r.status_code}")
        return (200 <= r.status_code < 300)
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
# 비로그인 하위 FSM
#################################
def do_anon_sub_fsm(session: requests.Session, user_unique_id: str):
    sub_state = "Anon_Sub_Initial"
    while sub_state != "Anon_Sub_Done":
        logging.info(f"[{user_unique_id}] Anon Sub-FSM state = {sub_state}")
        perform_anon_sub_action(session, user_unique_id, sub_state)

        if sub_state not in config.ANON_SUB_TRANSITIONS:
            logging.warning(f"[{user_unique_id}] {sub_state} not in ANON_SUB_TRANSITIONS => break")
            break

        transitions = config.ANON_SUB_TRANSITIONS[sub_state]
        if not transitions:
            logging.warning(f"[{user_unique_id}] No next transitions => break")
            break

        next_sub = pick_next_state(transitions)
        logging.info(f"[{user_unique_id}] (AnonSub) {sub_state} -> {next_sub}")
        sub_state = next_sub

        time.sleep(random.uniform(*config.TIME_SLEEP_RANGE))

def perform_anon_sub_action(session: requests.Session, user_unique_id: str, sub_state: str):
    headers = {"Accept": "application/json"}

    if sub_state == "Anon_Sub_Main":
        try:
            r = session.get(config.API_URL_WITH_HTTP, headers=headers)
            logging.info(f"[{user_unique_id}] GET / => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Anon_Sub_Main error: {e}")

    elif sub_state == "Anon_Sub_Products":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
            resp = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /products => {resp.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Anon_Sub_Products error: {e}")

    elif sub_state == "Anon_Sub_ViewProduct":
        # 101~124 범위의 상품 ID를 랜덤 선택하여 조회
        pid = random.randint(101, 124)
        url = f"{config.API_URL_WITH_HTTP}{config.API_ENDPOINTS['PRODUCT_DETAIL']}?id={pid}"
        
        try:
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /product?id={pid} => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] view product error: {err}")

    elif sub_state == "Anon_Sub_Categories":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CATEGORIES"]
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /categories => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] categories error: {err}")

    elif sub_state == "Anon_Sub_CategoryList":
        if categories_cache:
            chosen_cat = random.choice(categories_cache)
            cat_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['CATEGORY']}?name={chosen_cat}"
            try:
                r = session.get(cat_url, headers=headers)
                logging.info(f"[{user_unique_id}] GET /category?name={chosen_cat} => {r.status_code}")
            except Exception as err:
                logging.error(f"[{user_unique_id}] category list error: {err}")

    elif sub_state == "Anon_Sub_Search":
        q = random.choice(config.SEARCH_KEYWORDS)
        search_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['SEARCH']}?query={q}"
        try:
            r = session.get(search_url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /search?query={q} => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] search error: {err}")

    elif sub_state == "Anon_Sub_Error":
        try:
            err_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ERROR_PAGE"]
            r = session.get(err_url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /error => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] error page fail: {err}")
    
    # 페이지 체류 시간 로직     
    dwell_time = random.uniform(*DWELL_TIME_RANGE)
    session.headers.update({'X-Dwell-Time': f"{dwell_time:.2f}"})
    time.sleep(dwell_time)

#################################
# 로그인 하위 FSM
#################################
def do_logged_sub_fsm(session: requests.Session,
                      user_unique_id: str,
                      gender,
                      age_segment: str
                      ):
    sub_state = "Login_Sub_Initial"
    while sub_state != "Login_Sub_Done":
        logging.info(f"[{user_unique_id}] Logged Sub-FSM state = {sub_state}")
        perform_logged_sub_action(session, user_unique_id, sub_state, gender, age_segment)

        if sub_state not in config.LOGGED_SUB_TRANSITIONS:
            logging.warning(f"[{user_unique_id}] {sub_state} not in LOGGED_SUB_TRANSITIONS => break")
            break

        transitions = config.LOGGED_SUB_TRANSITIONS[sub_state]
        
        if not transitions:
            logging.warning(f"[{user_unique_id}] No next transitions => break")
            break

        next_sub = pick_next_state(transitions)
        logging.info(f"[{user_unique_id}] (LoggedSub) {sub_state} -> {next_sub}")
        sub_state = next_sub

        time.sleep(random.uniform(*config.TIME_SLEEP_RANGE))

def perform_logged_sub_action(session: requests.Session,
                              user_unique_id: str,
                              sub_state: str,
                              gender: str,
                              age_segment: str
                              ):
    headers = {
        "Accept": "application/json",
        "X-User-Id": user_unique_id,
    }
    
    if sub_state == "Login_Sub_Initial":
        # 진입점: 특별한 액션 없이 상태 확인만
        logging.info(f"[{user_unique_id}] Login Sub-FSM initialized")
    
    elif sub_state == "Login_Sub_Main":
        try:
            r = session.get(config.API_URL_WITH_HTTP, headers=headers)
            logging.info(f"[{user_unique_id}] GET / (logged) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_Main error: {e}")
    
    elif sub_state == "Login_Sub_Products":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["PRODUCTS"]
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /products (logged) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_Products error: {e}")
    
    elif sub_state == "Login_Sub_ViewProduct":
        # 선호 카테고리 기반으로 상품 선택
        pid = pick_preferred_product_id(gender, age_segment)
        url = f"{config.API_URL_WITH_HTTP}{config.API_ENDPOINTS['PRODUCT_DETAIL']}?id={pid}"
        try:
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /product?id={pid} (logged) => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] Login_Sub_ViewProduct error: {err}")

    elif sub_state == "Login_Sub_Search":
        q = random.choice(config.SEARCH_KEYWORDS)
        search_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['SEARCH']}?query={q}"
        try:
            r = session.get(search_url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /search?query={q} (logged) => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] Login_Sub_Search error: {err}")

    elif sub_state == "Login_Sub_Categories":
        try:
            url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CATEGORIES"]
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /categories (logged) => {r.status_code}")
        except Exception as err:
            logging.error(f"[{user_unique_id}] Login_Sub_Categories error: {err}")

    elif sub_state == "Login_Sub_CategoryList":
        if categories_cache:
            # 선호 카테고리 기반으로 선택
            preferred_cats = config.CATEGORY_PREFERENCE.get(gender, {}).get(age_segment, [])
            available_cats = [cat for cat in categories_cache if cat in preferred_cats]
            chosen_cat = random.choice(available_cats) if available_cats else random.choice(categories_cache)
            
            cat_url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['CATEGORY']}?name={chosen_cat}"
            try:
                r = session.get(cat_url, headers=headers)
                logging.info(f"[{user_unique_id}] GET /category?name={chosen_cat} (logged) => {r.status_code}")
            except Exception as err:
                logging.error(f"[{user_unique_id}] Login_Sub_CategoryList error: {err}")

    elif sub_state == "Login_Sub_ViewCart":
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_VIEW"]
        try:
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /cart/view => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_ViewCart error: {e}")

    elif sub_state == "Login_Sub_CheckoutHistory":
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CHECKOUT_HISTORY"]
        try:
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /checkout_history => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_CheckoutHistory error: {e}")

    elif sub_state == "Login_Sub_CartAdd":
        pid = pick_preferred_product_id(gender, age_segment)
        qty = random.randint(1, 5)
        cat = get_category_for_product(pid)

        payload = {"id": pid, "quantity": str(qty)}
        headers.update({
            "X-Product-Id": pid,
            "X-Quantity": str(qty),
            "X-Category": cat,
        })
        try:
            r = session.post(
                config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_ADD"],
                data=payload,
                headers=headers
            )
            logging.info(f"[{user_unique_id}] POST /cart/add id={pid}, qty={qty} => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_CartAdd error: {e}")

    elif sub_state == "Login_Sub_CartRemove":
        view_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_VIEW"]
        try:
            vr = session.get(view_url, headers=headers)
            if vr.status_code == 200:
                cart_data = vr.json()
                items = cart_data.get("cart_items", [])
                if items:
                    chosen_item = random.choice(items)
                    rid = chosen_item["product_id"]
                    rqty = random.randint(1, chosen_item["quantity"])
                    cat = get_category_for_product(rid)

                    payload = {"product_id": rid, "quantity": rqty}
                    headers.update({
                        "X-Product-Id": rid,
                        "X-Quantity": str(rqty),
                        "X-Category": cat,
                    })
                    rr = session.post(
                        config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_REMOVE"],
                        data=payload,
                        headers=headers
                    )
                    logging.info(f"[{user_unique_id}] POST /cart/remove id={rid}, qty={rqty} => {rr.status_code}")
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
            logging.info(f"[{user_unique_id}] POST /checkout => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_Checkout error: {e}")

    elif sub_state == "Login_Sub_AddReview":
        pid = pick_preferred_product_id(gender, age_segment)
        rating = random.randint(1,5)
        
        payload = {"product_id": pid, "rating": str(rating)}
        try:
            rev_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ADD_REVIEW"]
            r = session.post(rev_url, data=payload, headers=headers)
            logging.info(f"[{user_unique_id}] POST /add_review (pid={pid},rating={rating}) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_AddReview error: {e}")

    elif sub_state == "Login_Sub_Error":
        err_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ERROR_PAGE"]
        try:
            rr = session.get(err_url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /error => {rr.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] Login_Sub_Error => {e}")
            
    # 페이지 체류 시간 로직
    dwell_time = random.uniform(*DWELL_TIME_RANGE)
    session.headers.update({'X-Dwell-Time': f"{dwell_time:.2f}"})
    time.sleep(dwell_time)

#################################
# do_top_level_action_and_confirm
#################################
def do_top_level_action_and_confirm(
    session: requests.Session,
    current_state: str,
    proposed_next: str,
    user_id: str,
    gender: str,
    age_segment: str,
    region: str,
    device: str
) -> str:
    """
    실제 API 호출로 회원가입/로그인/로그아웃/탈퇴 시도.
    성공 => proposed_next 반환, 실패 시 현재 상태 유지.
    """
    if current_state == "Anon_NotRegistered" and proposed_next == "Anon_Registered":
        ok = try_register(session, user_id, gender, age_segment, region, device)
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
    
    gender = random.choice(["F", "M"])
    age = random.randint(18,70)
    
    # 지역만 사용하도록 변경: timezone 로직 제거
    region = random.choice(config.REGIONS)
    now = datetime.now()
    hour = now.hour
    
    age_segment = get_age_segment(age)
    
    # 디바이스 선택 로직
    if age_segment == "young":
        device = random.choices(["PC", "Mobile"], weights=[0.2, 0.8], k=1)[0]
    elif age_segment == "middle":
        device = random.choice(["PC", "Mobile"])
    else:
        device = random.choices(["PC", "Mobile"], weights=[0.8, 0.2], k=1)[0]

    segment = get_time_segment(hour)

    session.headers.update({
        "X-Region": region,
        "X-Device": device,
        "X-Time-Segment": segment
    })
    
    session.get(config.API_URL_WITH_HTTP)
    
    user_unique_id = f"user_{uuid.uuid4().hex[:6]}"
    logging.info(f"[{user_unique_id}] Start simulation. gender={gender}, age={age}, region={region}, device={device}")

    current_state = "Anon_NotRegistered"
    transition_count = 0

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

        possible_next = config.STATE_TRANSITIONS[current_state]
        if not possible_next:
            logging.warning(f"[{user_unique_id}] next_candidates empty => end.")
            break

        proposed_next = pick_next_state(possible_next)
        logging.info(f"[{user_unique_id}] (Top) {current_state} -> proposed={proposed_next}")

        actual_next = do_top_level_action_and_confirm(
            session=session,
            current_state=current_state,
            proposed_next=proposed_next,
            user_id=user_unique_id,
            gender=gender,
            age_segment=age_segment,
            region=region,
            device=device
        )
        if actual_next != current_state:
            logging.info(f"[{user_unique_id}] => confirmed next: {actual_next}")
            current_state = actual_next

        if current_state == "Anon_NotRegistered":
            do_anon_sub_fsm(session, user_unique_id)
        elif current_state == "Anon_Registered":
            do_anon_sub_fsm(session, user_unique_id)
        elif current_state == "Logged_In":
            do_logged_sub_fsm(session, user_unique_id, gender, age_segment)
        elif current_state == "Logged_Out":
            logging.info(f"[{user_unique_id}] (Top) state=Logged_Out => no sub-FSM")
        elif current_state == "Unregistered":
            logging.info(f"[{user_unique_id}] user unregistered => next=Done")
            current_state = "Done"

        transition_count += 1
        time.sleep(random.uniform(*config.TIME_SLEEP_RANGE))

    logging.info(f"[{user_unique_id}] Simulation ended. final={current_state}")

#################################
# 멀티 스레드 실행
#################################
semaphore = threading.Semaphore(config.MAX_THREADS)

def user_thread(idx: int):
    with semaphore:
        run_user_simulation(idx)


def launch_traffic(num_users, max_threads, time_sleep_range):
    # Override config values for this run
    orig_num_users       = config.NUM_USERS
    orig_max_threads     = config.MAX_THREADS
    orig_time_sleep_range = config.TIME_SLEEP_RANGE
    config.NUM_USERS     = num_users
    config.MAX_THREADS   = max_threads
    config.TIME_SLEEP_RANGE = time_sleep_range

    # 미리 상품·카테고리 캐시 갱신
    fetch_products(config.API_URL_WITH_HTTP)
    fetch_categories(config.API_URL_WITH_HTTP)

    # 스레드 시작 간격에 약간의 무작위성 부여 (0.01~0.1초)
    spawn_min, spawn_max = 0.01, 0.1

    threads = []
    for i in range(config.NUM_USERS):
        t = threading.Thread(target=user_thread, args=(i,))
        threads.append(t)
        t.start()

        # 자연스러운 사용자 도착 간격
        delay = random.uniform(spawn_min, spawn_max)
        logging.info(f"[Launch] spawned user #{i}, next in {delay:.3f}s")
        time.sleep(delay)

    # 모든 스레드가 작업을 마칠 때까지 대기
    for t in threads:
        t.join()

    logging.info("All user threads finished.")

    # 원래 config 값 복원
    config.NUM_USERS       = orig_num_users
    config.MAX_THREADS     = orig_max_threads
    config.TIME_SLEEP_RANGE = orig_time_sleep_range

# main
if __name__ == "__main__":
    args = parse_args()
    if args.mode == "once":
        launch_traffic(config.NUM_USERS, config.MAX_THREADS, config.TIME_SLEEP_RANGE)
        print("[Done] Single traffic launch completed.")
    else:
        spawn_batch = config.NUM_USERS     # 예: 10명
        interval = 5                       # 사이클 간 5초 대기

        while True:

            logging.info(f"Spawning batch of {spawn_batch} users across random regions")
            # launch_traffic 호출 시 config.REGIONS 건드리지 않음!
            # 내부 run_user_simulation() 에서 각자 random.choice(config.REGIONS) 사용
            launch_traffic(
                num_users=spawn_batch,
                max_threads=config.MAX_THREADS,
                time_sleep_range=config.TIME_SLEEP_RANGE
            )

            logging.info(f"Batch done. Sleeping for {interval}s before next batch")
            time.sleep(interval)
