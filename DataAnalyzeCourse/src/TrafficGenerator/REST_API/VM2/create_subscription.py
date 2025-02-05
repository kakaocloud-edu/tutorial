#!/usr/bin/env python3
"""
CreateSubscription.py

- Kakao Cloud Pub/Sub에 서브스크립션(Subscription)을 생성하는 스크립트
- objectStorageConfig를 config.py에서 읽어와 설정
"""

import requests
import json
import sys
import os

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 경로 가져오기 (REST API의 상위 디렉토리는 TrafficGenerator)
parent_dir = os.path.dirname(current_dir)

# 상위 디렉토리를 Python 경로에 추가하여 config.py를 임포트 가능하게 함
sys.path.append(parent_dir)

import config

def create_subscription():
    """
    Kakao Pub/Sub에서 서브스크립션을 생성하고, 응답 JSON을 반환합니다.
    """
    # (1) 요청 URL
    url = (
        f"{config.PUBSUB_ENDPOINT}/v1/domains/{config.DOMAIN_ID}/"
        f"projects/{config.PROJECT_ID}/subscriptions/{config.OBJECT_STORAGE_SUBSCRIPTION_NAME_MK}"
    )

    # (2) subscription 요청 바디
    body = {
        "subscription": {
            "topic": config.TOPIC_NAME_MK,
            "ackDeadlineSeconds": 30,
            "messageRetentionDuration": "600s",  # 10분 예시 (7일은 "604800s")
            "maxDeliveryAttempt": 1
        }
    }

    # (3) objectStorageConfig 설정
    object_storage_config = {
        "bucket": config.OBJECT_STORAGE_BUCKET,
        "exportIntervalMinutes": config.EXPORT_INTERVAL_MIN,
        "filePrefix": config.FILE_PREFIX,
        "fileSuffix": config.FILE_SUFFIX,
        "channelCount": config.CHANNEL_COUNT,
        "maxChannelCount": config.MAX_CHANNEL_COUNT,
        "isExportEnabled": config.IS_EXPORT_ENABLED
    }
    body["subscription"]["objectStorageConfig"] = object_storage_config

    # (4) 요청 헤더
    headers = {
        "Credential-ID": config.CREDENTIAL_ID,
        "Credential-Secret": config.CREDENTIAL_SECRET,
        "Content-Type": "application/json"
    }

    # (5) PUT 요청 (문서에 맞춰 수정)
    resp = requests.put(url, headers=headers, json=body, timeout=10)

    # (6) 응답 검사
    if not (200 <= resp.status_code < 300):
        raise RuntimeError(
            f"[ERROR] 서브스크립션 생성 실패 (status={resp.status_code}). 응답 바디: {resp.text}"
        )

    return resp.json()

def main():
    print(f"=== Kakao Cloud Pub/Sub: '{config.TOPIC_NAME_MK}' 서브스크립션 '{config.OBJECT_STORAGE_SUBSCRIPTION_NAME_MK}' 생성 요청 ===")
    try:
        result = create_subscription()
        print("[INFO] 서브스크립션 생성 성공!")
        print("응답 데이터:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print("[ERROR] 서브스크립션 생성 중 오류 발생:", e)

if __name__ == "__main__":
    main()
