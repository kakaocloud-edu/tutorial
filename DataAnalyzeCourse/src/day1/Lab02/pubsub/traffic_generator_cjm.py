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

# 기존에 생성된 user_id 저장 (재방문 로직용)
existing_user_ids = set()

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))
# config_cjm.py가 위치한 경로 설정
config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "Lab01", "traffic_generator"))
sys.path.append(config_path)
import config_cjm

# 로깅 설정
logging.basicConfig(
    filename=config_cjm.LOG_FILENAME,
    level=config_cjm.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info(f"Config loaded: LOG_FILENAME={config_cjm.LOG_FILENAME}, LOG_LEVEL={config_cjm.LOG_LEVEL}")
logging.info(f"API_URL_WITH_HTTP: {config_cjm.API_URL_WITH_HTTP}")
logging.info(f"Number of Users: {config_cjm.NUM_USERS}")

# Argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Traffic generator: once vs continuous")
    parser.add_argument('--mode', choices=['once','continuous'], default='once',
                        help='한번 실행(once) vs 지속 실행(continuous)')
    return parser.parse_args()

# 나이 구간 판단
def get_age_segment(age: int) -> str:
    if age < config_cjm.AGE_THRESHOLD_YOUNG:
        return "young"
    elif age < config_cjm.AGE_THRESHOLD_MIDDLE:
        return "middle"
    else:
        return "old"

# 상품/카테고리 캐시
products_cache = []
categories_cache = []

def fetch_products():
    global products_cache
    try:
        url = config_cjm.API_URL_WITH_HTTP + config_cjm.API_ENDPOINTS["PRODUCTS"]
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            products_cache = data if isinstance(data, list) else data.get("products", [])
            logging.info(f"Fetched {len(products_cache)} products.")
    except Exception as e:
        logging.error(f"Exception while fetching products: {e}")

def fetch_categories():
    global categories_cache
    try:
        url = config_cjm.API_URL_WITH_HTTP + config_cjm.API_ENDPOINTS["CATEGORIES"]
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            categories_cache = data if isinstance(data, list) else data.get("categories", [])
            logging.info(f"Fetched {len(categories_cache)} categories.")
    except Exception as e:
        logging.error(f"Exception while fetching categories: {e}")

# 상태 전이 선택
def pick_next_state(prob_dict: dict) -> str:
    return random.choices(list(prob_dict.keys()), weights=list(prob_dict.values()), k=1)[0]

# 선호 상품 선택
def pick_preferred_product_id(gender: str, age_segment: str) -> str:
    if not products_cache:
        return str(random.randint(101, 124))
    pref = config_cjm.CATEGORY_PREFERENCE.get(gender, {}).get(age_segment, [])
    filtered = [p for p in products_cache if p.get("category") in pref]
    chosen = random.choice(filtered or products_cache)
    return str(chosen.get("id"))

# 회원가입/로그인/로그아웃/탈퇴
# 각 함수 예외 처리 포함
def try_register(session, user_id, gender, age_segment):
    payload = {
        "user_id": user_id,
        "name": f"TestUser_{user_id}",
        "email": f"{user_id}@example.com",
        "gender": gender,
        "age": str(random.randint(18, 70))
    }
    try:
        r = session.post(
            config_cjm.API_URL_WITH_HTTP + config_cjm.API_ENDPOINTS["ADD_USER"],
            data=payload
        )
        logging.info(f"[{user_id}] POST /add_user => {r.status_code}")
        return r.status_code == 201
    except Exception as e:
        logging.error(f"[{user_id}] register exception: {e}")
        return False

def try_login(session, user_id):
    try:
        r = session.post(
            config_cjm.API_URL_WITH_HTTP + config_cjm.API_ENDPOINTS["LOGIN"],
            data={"user_id": user_id}
        )
        logging.info(f"[{user_id}] POST /login => {r.status_code}")
        if 200 <= r.status_code < 300:
            session.headers.update({"X-User-Id": user_id})
            return True
    except Exception as e:
        logging.error(f"[{user_id}] login exception: {e}")
    return False

def try_logout(session, user_id):
    try:
        r = session.post(config_cjm.API_URL_WITH_HTTP + config_cjm.API_ENDPOINTS["LOGOUT"])
        logging.info(f"[{user_id}] POST /logout => {r.status_code}")
        return 200 <= r.status_code < 300
    except Exception as e:
        logging.error(f"[{user_id}] logout exception: {e}")
    return False

def try_delete_user(session, user_id):
    try:
        r = session.post(
            config_cjm.API_URL_WITH_HTTP + config_cjm.API_ENDPOINTS["DELETE_USER"],
            data={"user_id": user_id}
        )
        logging.info(f"[{user_id}] POST /delete_user => {r.status_code}")
        return 200 <= r.status_code < 300
    except Exception as e:
        logging.error(f"[{user_id}] delete exception: {e}")
    return False

# 비로그인 FSM
def do_anon_sub_fsm(session, user_id, time_sleep_range):
    state = "Anon_Sub_Initial"
    while state != "Anon_Sub_Done":
        # perform action based on state
        next_state = pick_next_state(config_cjm.ANON_SUB_TRANSITIONS.get(state, {}))
        state = next_state
        time.sleep(random.uniform(*time_sleep_range))

# 로그인 FSM
def do_logged_sub_fsm(session, user_id, gender, age_segment, time_sleep_range):
    state = "Login_Sub_Initial"
    while state != "Login_Sub_Done":
        next_state = pick_next_state(config_cjm.LOGGED_SUB_TRANSITIONS.get(state, {}))
        state = next_state
        time.sleep(random.uniform(*time_sleep_range))

# 최상위 시뮬레이션
def run_user_simulation(idx):
    session = requests.Session()
    session.get(config_cjm.API_URL_WITH_HTTP)

    # 지역/기기
    region = random.choice(config_cjm.LOCATIONS)
    device = random.choice(config_cjm.DEVICE_TYPES)
    session.headers.update({"X-Region": region, "X-Device-Type": device})

    # 재방문/신규
    if existing_user_ids and random.random() < config_cjm.REVISIT_PROBABILITY:
        user_id = random.choice(list(existing_user_ids))
    else:
        user_id = f"user_{uuid.uuid4().hex[:6]}"
        existing_user_ids.add(user_id)

    # 세션 길이 (파레토 분포)
    pareto = random.paretovariate(config_cjm.SESSION_LENGTH_SHAPE)
    actions = max(1, int(config_cjm.ACTIONS_PER_USER * pareto))

    # 시간대 가중치
    hr = datetime.now().hour
    if 6 <= hr < 12:
        seg = "morning"
    elif 12 <= hr < 15:
        seg = "lunch"
    elif 17 <= hr < 21:
        seg = "evening"
    else:
        seg = "night"
    weight = config_cjm.TIME_SEGMENT_WEIGHTS.get(seg, 1.0)
    actions = max(1, int(actions * weight))

    # 세일 이벤트 보너스
    for e in config_cjm.SALE_EVENTS:
        if e['start_hour'] <= hr < e['end_hour']:
            weight *= e['bonus_factor']
    time_range = (
        config_cjm.TIME_SLEEP_RANGE[0] / weight,
        config_cjm.TIME_SLEEP_RANGE[1] / weight
    )

    # 사용자 프로필
    gender = random.choice(["F", "M"])
    age = random.randint(18, 70)
    age_seg = get_age_segment(age)

    logging.info(
        f"[{user_id}] Start sim: region={region}, device={device}, "
        f"gender={gender}, age={age}"
    )

    state = "Anon_NotRegistered"
    count = 0
    while count < actions and state != "Done":
        next_state = pick_next_state(config_cjm.STATE_TRANSITIONS.get(state, {}))
        # 최상위 행동 확인
        if state == "Anon_NotRegistered" and next_state == "Anon_Registered":
            ok = try_register(session, user_id, gender, age_seg)
            state = "Anon_Registered" if ok else state
        # (이어서 로그인/로그아웃/탈퇴 등 처리)
        # 서브 FSM 실행
        if state in ("Anon_NotRegistered", "Anon_Registered"):
            do_anon_sub_fsm(session, user_id, time_range)
        elif state == "Logged_In":
            do_logged_sub_fsm(session, user_id, gender, age_seg, time_range)
        count += 1
        time.sleep(random.uniform(*time_range))

    logging.info(f"[{user_id}] Simulation ended. final={state}")

# 멀티스레드 실행
semaphore = threading.Semaphore(config_cjm.MAX_THREADS)

def user_thread(i):
    with semaphore:
        run_user_simulation(i)

def launch_traffic(num, max_threads, time_sleep_range):
    orig = (
        config_cjm.NUM_USERS,
        config_cjm.MAX_THREADS,
        config_cjm.TIME_SLEEP_RANGE
    )
    config_cjm.NUM_USERS, config_cjm.MAX_THREADS, config_cjm.TIME_SLEEP_RANGE = (
        num, max_threads, time_sleep_range
    )
    fetch_products()
    fetch_categories()
    threads = []
    for i in range(config_cjm.NUM_USERS):
        t = threading.Thread(target=user_thread, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(random.uniform(0.01, 0.1))
    for t in threads:
        t.join()
    config_cjm.NUM_USERS, config_cjm.MAX_THREADS, config_cjm.TIME_SLEEP_RANGE = orig

if __name__ == "__main__":
    args = parse_args()
    if args.mode == "once":
        launch_traffic(
            config_cjm.NUM_USERS,
            config_cjm.MAX_THREADS,
            config_cjm.TIME_SLEEP_RANGE
        )
        print("[Done] Single launch completed.")
    else:
        patterns = ["light", "normal", "heavy"]
        while True:
            random.shuffle(patterns)
            for p in patterns:
                bf = {
                    "light": (0.5, 0.8),
                    "normal": (0.8, 1.2),
                    "heavy": (1.2, 1.5)
                }[p]
                f = random.uniform(*bf)
                n = max(1, int(config_cjm.NUM_USERS * f))
                mt = max(1, int(config_cjm.MAX_THREADS * f))
                base = config_cjm.TIME_SLEEP_RANGE
                sr = (
                    base[0] * random.uniform(0.8, 1.2),
                    base[1] * random.uniform(0.8, 1.2)
                )
                launch_traffic(n, mt, sr)
                time.sleep(5)
