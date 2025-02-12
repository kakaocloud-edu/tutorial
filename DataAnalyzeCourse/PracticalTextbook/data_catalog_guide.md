# 콘솔에서 리소스 생성 및 연동

## 1. 카탈로그 생성
- 이름:`data_catalog`
- vpc: `실습 환경`
- 서브넷: `실습 환경`
</br>

## 2. 데이터베이스 생성
- **Note**: 버킷의 권한 - 접근 - 퍼블릭 액세스 허용 해줘야함
1. 콘솔에서 생성한 카탈로그 클릭
2. `데이터 베이스 생성` 클릭
3. 생성 정보
   - 카탈로그: `data_catalog`
   - 이름: `database`
   - 경로
     - S3 연결 : `체크`
     - 버킷 이름: `{카프카와 연동된 버킷}`
     - 디렉터리:`{topics/nginx-topic/partition_0}` // 현재 임의 설정 (경로에`=` 못 넣음, partition을 경로에서 빼면 오류) 
</br>

## 3. 테이블 생성
1. 콘솔에서 생성한 데이터베이스 클릭
2. `테이블 생성` 클릭
3. 생성 정보
   - 테이블 이름: `data_table`
   - 데이터 저장경로
     - 버킷 이름: {카프카와 연동된 버킷}
     - 디렉터리: {topics/nginx-topic} // 임의 테스트
   - 데이터 유형: `JSON` // 테스트
   - Pub/Sub 연동: `사용` // 테스트
     - 토픽 선택: {data-catalog-topic}
     - `저장` 클릭
   - 스키마(추후 시나리오에 맞게 수정해야함)
     - `필드추가` 클릭
     - 필드 정보
        - `파티션 키`: 사용
        - 필드 이름: `partition`
        - 데이터 유형: `string`
        - ---
    
        - `파티션 키`: 미사용
        - 필드 이름: `status`
        - 데이터 유형: `string`
        - ---
        - `파티션 키`: 미사용
        - 필드 이름: `endpoint`
        - 데이터 유형: `string`
        - ---
        - `파티션 키`: 미사용
        - 필드 이름: `request`
        - 데이터 유형: `string`
        - ---
        - `파티션 키`: 미사용
        - 필드 이름: `query_params`
        - 데이터 유형: `string`

    
   - 모든 필드 선택 후 `생성` 클릭
  
# 메시지 확인 실습
## 1. pub/sub 연동을 통한 메시지 확인
   ### 서브스크립션 생성
   - 기본설정
      - 이름: pull-subscription-cjm //임의 값
      - 토픽: data-catalog-topic //임의 값
      - 유형: Pull

   ### TG에서 메시지 확인 코드 실행
   - 기존에 쓰던 메시지 확인 코드에서 subscription 이름만 변경하는 방향이 나을것 같다는 생각
   ```
   import requests
   import base64
   import json
   import logging
   import time
   import sys
   import os
   
   # 현재 스크립트의 디렉토리 경로 가져오기
   current_dir = os.path.dirname(os.path.abspath(__file__))
   
   # 상위 디렉토리 경로 가져오기 (REST API의 상위 디렉토리는 TrafficGenerator)
   parent_dir = os.path.dirname(current_dir)
   
   # TrafficGenerator 디렉토리를 Python 경로에 추가하여 config.py를 임포트 가능하게 함
   sys.path.append(parent_dir)
   
   from config import *
   
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
   def pull_messages(subscription_name, max_messages=10, wait_time="3s"):
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
   def receive_and_ack_messages(subscription_name, max_messages=10, wait_time="3s"):
       """
       메시지를 Pull하고, 콘솔에 출력한 후 Ack 처리하는 함수
       :param subscription_name: Pull Subscription 이름
       :param max_messages: 한 번에 Pull할 메시지 수
       :param wait_time: 메시지 fetch 대기 시간
       """
       received_messages = pull_messages(subscription_name, max_messages, wait_time)
   
       if not received_messages:
           print("No messages received.")
           return
   
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
       # Pull Subscription 이름 설정
       subscription_name = "pull-subscription"  # 실제 Subscription
   
       print(f"현재 사용하는 Topic: {TOPIC_NAME}")
       print(f"현재 사용하는 Subscription: {subscription_name}")
   
       while True:
           # 메시지 수신 및 Ack 처리
           receive_and_ack_messages(subscription_name, max_messages=10, wait_time="3s")
   
           # 일정 시간 대기 후 다시 Pull (예: 5초)
           time.sleep(5)
   
   if __name__ == "__main__":
       main()

   ```

   ### 콘솔에서 이벤트 발생
   - 데이터 속성 추가
   - 스키마 필드 추가
   - 스키마 필드 삭제
   - 터미널 창에서 실시간 메시지 수신 확인
   
## 2. Hadoop 연동을 통한 메시지 확인
### Hadoop 생성
   1. 콘솔에서 Analytics -> Hadoop Eco -> 클러스터 접속
   2. `클러스터 생성` 클릭
   3. 클러스터 정보
      - 클러스터 이름: `core-hadoop-cluster`
      - 클러스터 구성: `Core Hadoop`
      - 관리자 설정
        - 관리자 아이디: admin
        - 관리자 비밀번호: Admin1234!
      - vpc: `실습 환경`
      - 서브넷: `실습 환경`
      - 보안 그룹: `그대로`
      - `다음` 클릭
      - ---
      - 마스터 노드 설정
        - 인스턴스 유형: `m2a.xlarge`
          
      - 워커 노드 설정
        - 인스턴스 개수: 2
        - 인스턴스 유형: `m2a.xlarge`
       
      - `다음` 클릭
      - ---
      - 서비스 연동: `Data Catalog 연동`
        - 카탈로그 이름: `data_catalog` 선택
      - 클러스터 구성 설정:
        ```
         {
         "configurations": [
             {
             "classification": "core-site",
             "properties": {
                 "fs.swifta.service.kic.credential.id": "${ACCESS_KEY}",
                 "fs.swifta.service.kic.credential.secret": "${ACCESS_SECRET_KEY}"
             }
             }
         ]
         }
        ```
   - **NOTE**: 보안 그룹 22번 포트 열어야함
   4. 마스터 노드에 public IP 부여 후 ssh 접속
   5. Hive 실행
      ```
      hive
      ```
   6. 사용할 데이터 베이스 선택
      ```
      use {database 이름};
      ```
   7. 테이블에 파티션 추가
      ```
      ALTER TABLE {테이블 이름}
      ADD PARTITION (partition_key='{특정값(5)')
      LOCATION 's3a://kafka-data/topics/nginx-topic/partition=0';
      ```
   8. 테이블 파이션 키 삭제
      ```
      ALTER TABLE part_test_lsh DROP PARTITION (partition_key='{특정값(5)');
      ```
   

</br>

# 크롤러

## 1. 크롤러 생성

 1.  콘솔에서 Analytics -> Data Catalog -> 크롤러 접속

 2.  `크롤러 생성` 클릭

 3.  생성 정보
      - 데이터베이스: ` 콘솔에서 생성한 데이터베이스 `
      - 크롤러 이름: ` crawler_test `
      - MySQL 전체 경로
         - 연결할 MySQL: ` {사전 생성한 MySQL} `
         - MySQL 데이터베이스 이름: ` shopdb `
      - MySQL 계정
         - MySQL 계정 ID: ` admin `
         - MySQL 계정 PW: ` admin1234 `
         - 연결테스트 진행
      - 설명 (선택):
      - 테이블 Prefix (선택):
      - 스케줄: 온디멘드
   - 생성 클릭


4. 생성된 크롤러 선택 후 실행

5. 테이블 클릭 후 생성된 테이블 확인

---
