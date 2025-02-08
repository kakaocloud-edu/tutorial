#!/usr/bin/env python3
"""
pub_sub_send.py

- CLI(터미널)에서 사용자가 원하는 문자열을 입력받아,
- Base64 인코딩 후 Kakao Cloud Pub/Sub에 전송

Usage:
  python3 pub_sub_send.py
  (프로그램 실행 후 원하는 값을 입력, Ctrl+D 또는 빈 줄 입력 혹은 "quit"을 입력 시 종료)
"""

import os          # 추가된 부분
import sys         # 추가된 부분
import base64
import json
import requests

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 경로 가져오기 (REST API의 상위 디렉토리는 TrafficGenerator)
parent_dir = os.path.dirname(current_dir)

# 상위 디렉토리를 Python 경로에 추가하여 config.py를 임포트 가능하게 함
sys.path.append(parent_dir)

import config

def main():
    print("CLI 입력 -> Kakao Pub/Sub 전송 프로그램입니다.")
    print("아래에 전송하고 싶은 문자열을 입력하세요.")
    print("(빈 줄, Ctrl+D, 혹은 'quit' 입력 시 전송을 마칩니다.)")

    user_lines = []
    while True:
        try:
            line = input()
        except EOFError:
            # Ctrl+D로 입력이 끝나면 종료
            break

        if not line.strip():
            # 빈 줄이면 종료
            break

        if line.strip().lower() == "quit":
            # 'quit' 입력 시 종료
            break

        user_lines.append(line)

    if not user_lines:
        print("전송할 메시지가 없습니다.")
        return

    # Kakao Cloud Pub/Sub에 메시지를 보내기 위한 URL 구성
    pubsub_url = (
        f"{config.PUBSUB_ENDPOINT}/v1/domains/{config.DOMAIN_ID}/"
        f"projects/{config.PROJECT_ID}/topics/{config.TOPIC_NAME}/publish"
    )

    # 메시지 목록을 Pub/Sub가 요구하는 JSON 구조로 만들기
    messages = []
    for line in user_lines:
        encoded_data = base64.b64encode(line.encode('utf-8')).decode('utf-8')
        message_obj = {
            "data": encoded_data,
            "attributes": {
                "source": "cli_input",
                "line_length": str(len(line.strip()))
            }
        }
        messages.append(message_obj)

    # 최종 Request Body (중요: messages 리스트 자체를 넣어줘야 함)
    body = {"messages": messages}

    # 헤더에 Credential 정보 포함
    headers = {
        "Credential-ID": config.CREDENTIAL_ID,
        "Credential-Secret": config.CREDENTIAL_SECRET,
        "Content-Type": "application/json"
    }

    print(f"총 {len(messages)}개의 메시지를 Pub/Sub로 전송합니다.")
    response = requests.post(pubsub_url, headers=headers, json=body, timeout=10)

    print("Response status:", response.status_code)
    print("Response body:  ", response.text)
    # 필요하면 response.raise_for_status() 사용

if __name__ == "__main__":
    main()
