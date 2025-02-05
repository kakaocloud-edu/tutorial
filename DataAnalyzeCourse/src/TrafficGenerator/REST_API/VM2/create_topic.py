#!/usr/bin/env python3
"""
CreateTopic.py

- Kakao Cloud Pub/Sub에 새 토픽을 생성하는 스크립트
- 모든 설정을 config.py에서 가져오며, 사용자 입력 없이 바로 생성
"""

import requests
import json
import sys
import os

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))
# 상위 디렉토리 경로 가져오기 (REST API 루트)
parent_dir = os.path.dirname(current_dir)
# 상위 디렉토리를 Python 경로에 추가하여 config.py를 임포트 가능하게 함
sys.path.append(parent_dir)

import config

def create_topic():
    """
    Kakao Pub/Sub에 새 토픽을 생성하고, 응답 JSON을 반환합니다.
    """
    # 토픽 생성 URL 설정
    url = (
        f"{config.PUBSUB_ENDPOINT}/v1/domains/{config.DOMAIN_ID}/"
        f"projects/{config.PROJECT_ID}/topics/{config.TOPIC_NAME_MK}"
    )

    # 요청 바디
    body = {
        "topic": {
            "description": config.TOPIC_DESCRIPTION,
            "messageRetentionDuration": config.TOPIC_RETENTION_DURATION
        }
    }

    # 요청 헤더
    headers = {
        "Credential-ID": config.CREDENTIAL_ID,
        "Credential-Secret": config.CREDENTIAL_SECRET,
        "Content-Type": "application/json"
    }

    # PUT 요청
    resp = requests.put(url, headers=headers, json=body, timeout=10)

    # 결과 처리
    if not (200 <= resp.status_code < 300):
        raise RuntimeError(
            f"[ERROR] 토픽 생성 실패 (status={resp.status_code}). 응답 바디: {resp.text}"
        )

    return resp.json()

def main():
    print("=== Kakao Cloud Pub/Sub: 토픽 자동 생성 ===")
    print(f"토픽 이름: {config.TOPIC_NAME_MK}")  # 수정된 부분
    try:
        result = create_topic()
        print("[INFO] 토픽 생성 성공!")
        print("응답 데이터:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except RuntimeError as e:
        if "duplicate topic" in str(e):
            print("[WARNING] 이미 존재하는 토픽입니다.")
        else:
            print("[ERROR] 토픽 생성 중 오류:", e)

if __name__ == "__main__":
    main()
