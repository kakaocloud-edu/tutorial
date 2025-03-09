#!/usr/bin/env python3
"""
pub_sub_send.py

- CLI(터미널)에서 사용자가 원하는 문자열을 입력받아,
- Base64 인코딩 후 Kakao Cloud Pub/Sub에 전송

Usage:
  python3 pub_sub_send.py
  (프로그램 실행 후 원하는 값을 입력, Ctrl+D 또는 빈 줄 입력 혹은 "quit"을 입력 시 종료)
"""

import os
import sys
import base64
import json
import requests

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# config.py가 위치한 경로:
# 현재 디렉토리에서 두 단계 위로 이동한 후 Lab00/traffic_generator 디렉토리로 이동
config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "Lab00", "traffic_generator"))

#절대경로 지정
sys.path.append(config_path)

import config

def main():
    print("아래에 전송하고 싶은 문자열을 입력하세요: ")

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

    response = requests.post(pubsub_url, headers=headers, json=body, timeout=10)

    # 응답 상태에 따른 메시지 출력
    if response.status_code in [200, 201]:
        print("메세지가 전송되었습니다.")
    else:
        print(f"메세지 전송 실패: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
