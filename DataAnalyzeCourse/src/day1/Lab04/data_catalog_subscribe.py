#!/usr/bin/env python3
"""
restapi_pull_sub.py

- Pub/Sub Subscription에서 메시지를 Pull하고 처리하는 스크립트
- 설정을 config.py에서 읽어옴
"""

import requests
import base64
import json
import logging
import time
import sys
import os

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# config.py가 있는 Lab00/traffic_generator 경로를 sys.path에 추가
config_path = os.path.abspath(os.path.join(current_dir, "..", "Lab01", "traffic_generator"))
sys.path.append(config_path)

#절대경로 지정
sys.path.append(config_path)

# config.py 가져오기
from config import *

#################################
# 사용자 수정 가능한 설정 변수
#################################
SUBSCRIPTION_NAME = "data-catalog-pull-sub"      # Pull Subscription 이름 
PULL_MAX_MESSAGES = 10            # 한 번에 Pull할 메시지 수 (최대 100)
PULL_WAIT_TIME = "1s"             # 메시지 fetch 대기 시간 (최대 "30s")
PULL_INTERVAL_SECONDS = 0         # Pull 간의 대기 시간 (초)

#################################
# 로깅 설정
#################################
logging.basicConfig(
    filename=LOG_FILENAME,
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#################################
# 메시지 Pull 함수
#################################
def pull_messages(subscription_name, max_messages=PULL_MAX_MESSAGES, wait_time=PULL_WAIT_TIME):
    """
    Pub/Sub Subscription에서 메시지를 Pull하는 함수
    :param subscription_name: Pull Subscription 이름
    :param max_messages: 한 번에 Pull할 메시지 수 (최대 100)
    :param wait_time: 메시지 fetch 대기 시간 (기본: "3s", 최대: "30s")
    :return: 수신된 메시지 리스트
    """
    url = f"{PUBSUB_ENDPOINT}/v1/domains/{DOMAIN_ID}/projects/{PROJECT_ID}/subscriptions/{subscription_name}/pull"

    headers = {
        "Credential-ID": CREDENTIAL_ID,
        "Credential-Secret": CREDENTIAL_SECRET,
        "Content-Type": "application/json"
    }

    payload = {
        "maxMessages": max_messages,
        "waitTime": wait_time
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            response_json = response.json()
            received_messages = response_json.get('receivedMessages', [])
            logging.info(f"Pulled {len(received_messages)} message(s) from subscription '{subscription_name}'.")
            return received_messages
        else:
            logging.error(f"Failed to pull messages. Status Code: {response.status_code}, Response: {response.text}")
            return []
    except Exception as e:
        logging.error(f"Exception while pulling messages: {e}")
        return []

#################################
# 메시지 Ack 함수
#################################
def ack_messages(subscription_name, ack_ids, retries=3):
    """
    Pull한 메시지를 Ack 처리하는 함수 (재시도 기능 포함)
    :param subscription_name: Subscription 이름
    :param ack_ids: Ack 처리할 메시지의 ackId 리스트
    :param retries: 재시도 횟수
    """
    if not ack_ids:
        return

    url = f"{PUBSUB_ENDPOINT}/v1/domains/{DOMAIN_ID}/projects/{PROJECT_ID}/subscriptions/{subscription_name}/acknowledge"

    headers = {
        "Credential-ID": CREDENTIAL_ID,
        "Credential-Secret": CREDENTIAL_SECRET,
        "Content-Type": "application/json"
    }

    payload = {
        "ackIds": ack_ids
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code in [200, 201]:
                response_json = response.json()
                failures = response_json.get('failure', [])
                if not failures:
                    logging.info(f"Acknowledged {len(ack_ids)} message(s) successfully.")
                    print(f"Acknowledged {len(ack_ids)} message(s) successfully.")
                    return
                else:
                    for failure in failures:
                        ack_id = failure.get('ackID')
                        error = failure.get('error', {})
                        logging.error(f"Failed to ack message with ackID: {ack_id}, Error: {error}")
                        print(f"Failed to ack message with ackID: {ack_id}, Error: {error}")
            else:
                logging.error(f"Failed to acknowledge messages. Status Code: {response.status_code}, Response: {response.text}")
                print(f"Failed to acknowledge messages. Status Code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            logging.error(f"Exception while acknowledging messages (Attempt {attempt}): {e}")
            print(f"Exception occurred while acknowledging messages (Attempt {attempt}): {e}")

        # 재시도 간 대기 시간 (Exponential Backoff)
        time.sleep(2 ** attempt)

    logging.error(f"All {retries} attempts to acknowledge messages failed.")
    print(f"All {retries} attempts to acknowledge messages failed.")

#################################
# 메시지 디코딩 함수
#################################
def decode_message(message):
    """
    Pub/Sub 메시지 데이터를 디코딩하는 함수
    :param message: PubsubMessage 객체
    :return: 디코딩된 메시지 데이터와 속성
    """
    try:
        data = base64.b64decode(message.get('data', '')).decode('utf-8')
    except Exception as e:
        data = f"Failed to decode data: {e}"

    attributes = message.get('attributes', {})
    message_id = message.get('messageId', 'N/A')
    publish_time = message.get('publishTime', 'N/A')

    return {
        "data": data,
        "attributes": attributes,
        "message_id": message_id,
        "publish_time": publish_time
    }

#################################
# 메시지 Pull 및 Ack 처리 함수
#################################
def receive_and_ack_messages(subscription_name, max_messages=PULL_MAX_MESSAGES, wait_time=PULL_WAIT_TIME):
    """
    메시지를 Pull하고, 콘솔에 출력한 후 Ack 처리하는 함수
    :param subscription_name: Pull Subscription 이름
    :param max_messages: 한 번에 Pull할 메시지 수
    :param wait_time: 메시지 fetch 대기 시간
    """
    received_messages = pull_messages(subscription_name, max_messages, wait_time)

    ack_ids = []
    for idx, received_msg in enumerate(received_messages, start=1):
        ack_id = received_msg.get('ackId')
        message = received_msg.get('message', {})
        decoded = decode_message(message)

        # 메시지 내용을 콘솔에 출력
        print(f"Message {idx}:")
        print(f"  Data: {decoded['data']}")
        print(f"  Attributes: {decoded['attributes']}")
        print(f"  Message ID: {decoded['message_id']}")
        print(f"  Publish Time: {decoded['publish_time']}")
        print("-" * 40)

        ack_ids.append(ack_id)

    # Ack 처리
    ack_messages(subscription_name, ack_ids)

#################################
# 메인 함수
#################################
def main():
    while True:
        # 메시지 수신 및 Ack 처리
        receive_and_ack_messages(SUBSCRIPTION_NAME, max_messages=PULL_MAX_MESSAGES, wait_time=PULL_WAIT_TIME)

        # 설정한 간격만큼 대기 후 다시 Pull
        time.sleep(PULL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
