import os
import sys
import requests
import threading
import time
import random
import uuid
import logging

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# REST API 디렉토리의 절대 경로 가져오기 (상위 디렉토리)
rest_api_dir = os.path.abspath(os.path.join(current_dir, '..'))

# REST API 디렉토리를 Python 경로에 추가하여 config.py와 traffic_config.py를 임포트 가능하게 함
sys.path.append(rest_api_dir)

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
        return "101"  # fallback
    cat_list = config.CATEGORY_PREFERENCE.get(gender, {}).get(age_segment, [])
    filtered = [p for p in products_cache if p.get("category", "") in cat_list]
    if filtered:
        chosen = random.choice(filtered)
        return chosen.get("id", "101")
    else:
        chosen = random.choice(products_cache)
        return chosen.get("id", "101")

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
        return (200 <= r.status_code < 300) # 로그인 성공 시 200~299라 가정
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
        if products_cache:
            prod = random.choice(products_cache)
            pid = prod.get("id", "101")
            url = f"http://{config.API_BASE_URL}/{config.API_ENDPOINTS['PRODUCT_DETAIL']}?id={pid}"
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

    # Anon_Sub_Initial, Anon_Sub_Done => no specific action

#################################
# 로그인 하위 FSM
#################################
def do_logged_sub_fsm(session: requests.Session,
                      user_unique_id: str,
                      gender: str,
                      age_segment: str):
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
                              age_segment: str):
    headers = {"Accept": "application/json"}

    if sub_state == "Login_Sub_ViewCart":
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_VIEW"]
        try:
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /cart/view => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] view cart error: {e}")

    elif sub_state == "Login_Sub_CheckoutHistory":
        url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CHECKOUT_HISTORY"]
        try:
            r = session.get(url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /checkout_history => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] checkout_history error: {e}")

    elif sub_state == "Login_Sub_CartAdd":
        pid = pick_preferred_product_id(gender, age_segment)
        qty = random.randint(1,3)
        payload = {"id": pid, "quantity": str(qty)}
        try:
            add_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_ADD"]
            r = session.post(add_url, data=payload, headers=headers)
            logging.info(f"[{user_unique_id}] POST /cart/add (pid={pid}, qty={qty}) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] cart add error: {e}")

    elif sub_state == "Login_Sub_CartRemove":
        # 우선 장바구니 조회
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
                    remove_payload = {"product_id": rid, "quantity": rqty}

                    # 기존 장바구니 수량을 고려하여 삭제
                    remove_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CART_REMOVE"]
                    rr = session.post(remove_url, data=remove_payload, headers=headers)
                    logging.info(f"[{user_unique_id}] POST /cart/remove (pid={rid}, qty={rqty}) => {rr.status_code}")
                else:
                    logging.info(f"[{user_unique_id}] Cart empty => skip remove")
            else:
                logging.error(f"[{user_unique_id}] GET /cart/view fail => {vr.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] remove cart error: {e}")

    elif sub_state == "Login_Sub_Checkout":
        check_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["CHECKOUT"]
        try:
            r = session.post(check_url, headers=headers)
            logging.info(f"[{user_unique_id}] POST /checkout => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] checkout error: {e}")

    elif sub_state == "Login_Sub_AddReview":
        pid = pick_preferred_product_id(gender, age_segment)
        rating = random.randint(1,5)
        payload = {"product_id": pid, "rating": str(rating)}
        try:
            rev_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ADD_REVIEW"]
            r = session.post(rev_url, data=payload, headers=headers)
            logging.info(f"[{user_unique_id}] POST /add_review (pid={pid},rating={rating}) => {r.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] add review error: {e}")

    elif sub_state == "Login_Sub_Error":
        err_url = config.API_URL_WITH_HTTP + config.API_ENDPOINTS["ERROR_PAGE"]
        try:
            rr = session.get(err_url, headers=headers)
            logging.info(f"[{user_unique_id}] GET /error => {rr.status_code}")
        except Exception as e:
            logging.error(f"[{user_unique_id}] error page => {e}")

#################################
# do_top_level_action_and_confirm
# (상위 상태 전이 시 실제 API 호출로 성공/실패 반영)
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
    성공 => proposed_next 반환
    실패 => current_state로 롤백
    """
    # Anon_NotRegistered -> Anon_Registered => 회원가입
    if current_state == "Anon_NotRegistered" and proposed_next == "Anon_Registered":
        ok = try_register(session, user_id, gender, age_segment)
        return "Anon_Registered" if ok else "Anon_NotRegistered"

    # Anon_Registered -> Logged_In => 로그인
    if current_state == "Anon_Registered" and proposed_next == "Logged_In":
        ok = try_login(session, user_id)
        return "Logged_In" if ok else "Anon_Registered"

    # Logged_In -> Logged_Out => 로그아웃
    if current_state == "Logged_In" and proposed_next == "Logged_Out":
        ok = try_logout(session, user_id)
        return "Logged_Out" if ok else "Logged_In"

    # Logged_In -> Unregistered => 탈퇴
    if current_state == "Logged_In" and proposed_next == "Unregistered":
        ok = try_delete_user(session, user_id)
        return "Unregistered" if ok else "Logged_In"

    # Logged_Out -> Anon_Registered => 그냥 상태 전이(실제 API 없음)
    if current_state == "Logged_Out" and proposed_next == "Anon_Registered":
        return "Anon_Registered"

    # Logged_Out -> Unregistered => 탈퇴
    if current_state == "Logged_Out" and proposed_next == "Unregistered":
        ok = try_delete_user(session, user_id)
        return "Unregistered" if ok else "Logged_Out"

    # 그 외에는 그냥 전이
    return proposed_next


#################################
# 사용자 전체 로직
#################################
def run_user_simulation(user_idx: int):
    session = requests.Session()

    gender = random.choice(["F", "M"])
    age = random.randint(18,70)
    age_segment = get_age_segment(age)

    user_unique_id = f"user_{uuid.uuid4().hex[:6]}"
    logging.info(f"[{user_unique_id}] Start simulation. gender={gender}, age={age}")

    current_state = "Anon_NotRegistered"
    transition_count = 0

    while True:
        if transition_count >= config.ACTIONS_PER_USER:
            logging.info(f"[{user_unique_id}] Reached max transitions => end.")
            break

        if current_state == "Done":
            logging.info(f"[{user_unique_id}] state=Done => end.")
            break

        # 상위 전이 후보
        if current_state not in config.STATE_TRANSITIONS:
            logging.error(f"[{user_unique_id}] no transitions from {current_state} => end.")
            break

        possible_next = config.STATE_TRANSITIONS[current_state]
        if not possible_next:
            logging.warning(f"[{user_unique_id}] next_candidates empty => end.")
            break

        proposed_next = pick_next_state(possible_next)
        logging.info(f"[{user_unique_id}] (Top) {current_state} -> proposed={proposed_next}")

        # 실제 API 호출로 성공/실패 반영
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
            current_state = actual_next

        # 하위 FSM
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

def main():
    # 초기 데이터
    fetch_products(config.API_URL_WITH_HTTP)
    fetch_categories(config.API_URL_WITH_HTTP)

    threads = []
    for i in range(config.NUM_USERS):
        t = threading.Thread(target=user_thread, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(0.05)

    for t in threads:
        t.join()

    logging.info("All user threads finished.")

if __name__ == "__main__":
    main()
    print("Traffic generation completed. Check the log file for details.")
