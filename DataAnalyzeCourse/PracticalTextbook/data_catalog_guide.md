# Data Catalog 실습

## 1. 카탈로그 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 카탈로그
2. 카탈로그 생성 클릭

   - 이름
      - 카탈로그 이름: `data_catalog`
   - vpc
      - VPC: `kc-vpc`
   - 서브넷
      - 서브넷: `kr-central-2-a의 Public 서브넷`

3. 생성 클릭

## 2. 데이터베이스 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 데이터베이스
2. 데이터베이스 생성 클릭
   
- **Note**: 연결할 Object Storage 버킷의 권한 - 접근 - 퍼블릭 액세스 허용 필요

   - 카탈로그
      - 카탈로그: `data_catalog`
   - 이름
      - 이름: 'dc_database'
   - 경로
      - S3 연결: `체크`
      - 버킷 이름: `kafka-nginx-log`(카프카와 연동된 버킷)
      - 디렉터리: `topics/nginx-topic/partition_0`// 현재 임의 설정 (경로에`=` 못 넣음, partition을 경로에서 빼면 오류) 
3. 생성 클릭


## 3. 테이블 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 테이블
2. 테이블 생성 클릭

   - 데이터 베이스
      - 데이터 베이스: `dc_database`
   - 테이블 이름
      - 이름: 'data_table'
   - 테이블 저장 경로
      - S3 연결: `미체크`
      - 버킷 이름: `{kafka-nginx-log}`(카프카와 연동된 버킷)
      - 디렉터리: `topics/nginx-topic` // 임의 테스트
   - 데이터 유형
      - 데이터 유형: `JSON`
   - Pub/Sub 연동
      - Pub/Sub 연동: `사용`
      - 토픽 선택: `data-catalog-topic`
   - 설명(선택): `없음`
   - 스키마
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
3. 생성 버튼 클릭


---
## 4. 메시지 확인 실습
1. pub/sub 연동을 통한 메시지 확인

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

---

   
## 5. Hadoop 연동을 통한 메시지 확인
### Hadoop 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Hadoop Eco
2. 클러스터 생성 클릭

   - 클러스터 이름
        - 클러스터 이름: `core-hadoop-cluster`
   - 클러스터 구성
        - 클러스터 버전: `Hadoop Eco 2.1.0`
        - 클러스터 유형: `Core-Hadoop`
        - 클러스터 가용성: `미체크`
   - 관리자 설정
        - 관리자 아이디: `admin`
        - 관리자 비밀번호: `Admin1234!`
        - 관리자 비밀번호 확인: `Admin1234!`
   - VPC 설정
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
   - 보안 그룹 설정
        - 보안 그룹 설정: `새 보안 그룹 생성`
        - 보안 그룹 이름: `HDE-210-hadoop` {기본 입력 정보 사용}
   - `다음` 클릭
   - 마스터 노드 설정
        - 마스터 노드 인스턴스 개수: `1`
        - 마스터 노드 인스턴스 유형: `m2a.xlarge`
        - 디스크 볼륨 유형 / 크기: `50`
   - 워커 노드 설정
        - 워커 노드 인스턴스 개수: `2`
        - 마스터 노드 인스턴스 유형: `m2a.xlarge`
        - 디스크 볼륨 유형 / 크기: `100`
   - 총 YARN 사용량
        - YARN Core: `6개` {입력 필요X}
        - YARN Memory: `20GB` {입력 필요X}
   - 키 페어
        - 키 페어: {기존 생성 키 페어}
   - 사용자 스크립트(선택)
        - 사용자 스크립트: `없음`
   - `다음` 클릭
   - 모니터링 에이전트 설치: `설치 안함`
   - 서비스 연동: `Data Catalog 연동`
        - 카탈로그 이름: `data_catalog`
   - HDFS 설정
        - HDFS 블록 크기: `128`
        - HDFS 복제 개수: `2`
   - 클러스터 구성 설정(선택)
        - 클러스터 구성 설정: {아래 코드 입력}
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
   - Kerberos 설치: `설치 안함`
   - Ranger 설치: `설치 안함`
3. 생성 버튼 클릭
4. Hadoop Eco 클러스터 생성 확인
5. 마스터/워커 노드 VM 생성 확인
      - 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > 인스턴스

      - **Note**: 보안 그룹 22번 포트 열기
   
   5-1. 마스터 노드 VM(HadoopMST) 옆의 ... 클릭 후 보안 그룹 수정 클릭
   5-2. 보안 그룹 선택 클릭
   5-3. `보안 그룹 생성` 버튼 클릭
      - 보안 그룹 이름: `hadoop_mst`
      - 보안 그룹 설명: `없음`
      - 인바운드 규칙
        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`
      - 아웃바운드 규칙
        - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
      - `생성` 버튼 클릭
   5-4. `적용` 버튼 클릭

6. 마스터 노드에 public IP 부여 후 ssh 접속
   #### **lab3-1-1**
   
       - 마스터 노드 VM(HadoopMST)에 SSH로 접속
   
   ```bash
   ssh -i {keypair}.pem ubuntu@{vm public ip}
   ```

7. Hive 실행
   #### **lab3-1-2**
   ```
   hive
   ```
   
8. 사용할 데이터 베이스 선택
   #### **lab3-1-3**
   ```
   use {database 이름};
   ```
   
9. 테이블에 파티션 추가
   #### **lab3-1-4**
   ```
   ALTER TABLE {테이블 이름}
   ADD PARTITION (partition='{특정값(5)')
   LOCATION 's3a://kafka-data/topics/nginx-topic/partition=0';
   ```
   
10. 테이블 파이션 키 삭제
   #### **lab3-1-5**
   ```
   ALTER TABLE part_test_lsh DROP PARTITION (partition_key='{특정값(5)');
   ```
   

## 6. 크롤러 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data catalog > 크롤러
2. 크롤러 생성 버튼 클릭
   
    - 데이터베이스
        - 데이터베이스: `dc_database`
    - 크롤러 이름: `crawler`
    - MySQL 전체 경로
        - 연결할 MySQL: `database`
        - MySQL 데이터베이스 이름: `shopdb`
    - MySQL 계정
        - ID: `admin`
        - PW: `admin1234`
        - 연결 테스트 버튼 클릭(연결 테스트 완료 후에 생성 가능)
    - 설명 (선택): `없음`
    - 테이블 Prefix (선택): `없음`
    - 스케줄: `온디멘드`
3. 생성 버튼 클릭
4. 생성된 크롤러 선택 후 실행
5. 카카오 클라우드 콘솔 > 전체 서비스 > Data catalog > 테이블
      - 생성된 테이블 확인

---
