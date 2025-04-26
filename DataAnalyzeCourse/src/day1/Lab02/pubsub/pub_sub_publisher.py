#!/usr/bin/env python3
"""
pub_sub_send.py
- CLI(터미널)에서 사용자가 원하는 문자열을 입력받아,
- Base64 인코딩 후 Kakao Cloud Pub/Sub에 전송

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

# 절대경로 지정
sys.path.append(config_path)

import config

def main():
    # Pub/Sub URL 및 헤더 설정
    pubsub_url = (
        f"{config.PUBSUB_ENDPOINT}/v1/domains/{config.DOMAIN_ID}/"
        f"projects/{config.PROJECT_ID}/topics/{config.TOPIC_NAME}/publish"
    )
    headers = {
        "Credential-ID": config.CREDENTIAL_ID,
        "Credential-Secret": config.CREDENTIAL_SECRET,
        "Content-Type": "application/json"
    }
    
    print("메시지를 입력하세요. (종료하려면 'exit'을 입력하거나 Ctrl+C를 누르세요)")
    
    while True:
        try:
            user_input = input("메시지 전송: ")
        except KeyboardInterrupt:
            print("\nCtrl+C 입력 감지. 프로그램을 종료합니다.")
            break
        
        if user_input.strip().lower() == "exit":
            print("종료 명령어 입력. 프로그램을 종료합니다.")
            break
        
        if not user_input.strip():
            print("빈 메시지는 전송되지 않습니다.")
            continue
        
        # Base64 인코딩 후 메시지 객체 생성
        encoded_data = base64.b64encode(user_input.encode('utf-8')).decode('utf-8')
        message_obj = {
            "data": encoded_data,
            "attributes": {
                "source": "cli_input",
                "line_length": str(len(user_input.strip()))
            }
        }
        body = {"messages": [message_obj]}
        
        try:
            response = requests.post(pubsub_url, headers=headers, json=body, timeout=10)
            if response.status_code in [200, 201]:
                print("메시지가 전송되었습니다.")
            else:
                print(f"메시지 전송 실패: {response.status_code} - {response.text}")
        except Exception as e:
            print("메시지 전송 중 예외 발생:", e)

if __name__ == "__main__":
    main()
