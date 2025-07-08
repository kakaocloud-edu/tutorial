# Kafka 기반 데이터 스트리밍 및 Object Storage 연동

Kafka로 메시지를 송수신하고, Nginx 로그를 실시간으로 수집·처리하는 과정을 다룹니다. 또한, Kafka Connect와 S3 Sink Connector를 이용해 수집된 데이터를 Object Storage에 저장하는 방법을 실습합니다.

---

## 1. Kafka 실습을 위한 API Server 환경 설정

![최최종 그림 lab02](https://github.com/user-attachments/assets/e2042303-f606-49e9-8a60-df66872581bf)

1. `api-server-1`에서 Kafka Output 활성화 및 Pub/Sub 송신 설정 제거

    #### **lab3-1-1-1**
    
    ```bash
    sudo sed -i 's/^ENABLE_KAFKA_OUTPUT="false"/ENABLE_KAFKA_OUTPUT="true"/' /etc/default/logstash
    ```
    ```bash
    sudo sed -i 's/\["127.0.0.1:5044","127.0.0.1:5045"\]/["127.0.0.1:5045"]/g' /etc/filebeat/filebeat.yml
    ```
    

2. `api-server-1`서 Logstash 설정 파일을 수정하여 Kafka로 송신하도록 설정

    #### **lab3-1-2**
   
    ```
    sudo sed -i 's/logs-to-pubsub.conf/logs-to-kafka.conf/g' /etc/logstash/logstash.yml
    ```
    
3. `api-server-1`에서 Logstash, Filebeat 재시작 및 상태 확인
    
    #### **lab3-1-3-1**
    
    ```bash
    sudo systemctl daemon-reload
    ```

    #### **lab3-1-3-2**
   
    ```bash
    sudo systemctl restart filebeat
    ```

    #### **lab3-1-3-3**
    ```bash
    sudo systemctl restart logstash
    ```

4. `api-server-1`에서 Logstash 가 `Active:active (running)` 상태인 것을 확인

    #### **lab3-1-4**

    ```bash
    sudo systemctl status logstash
    ```

5. `ctrl` + `c`로 종료

    ![Image](https://github.com/user-attachments/assets/d6b11193-66a6-4bf3-a86f-7cd3a7169b51)


## 2. Kafka 실습을 위한 Traffic Generator 환경 설정

    
1. `traffic-generator-1`, `traffic-generator-2`에서 Kafka 클러스터와 통신 확인

    #### **lab3-2-1**
   
    ```bash
    for s in $(echo $KAFKA_BOOTSTRAP_SERVERS | tr ',' ' '); do nc -zv ${s%:*} ${s##*:} 2>&1 | grep "succeeded"; done
    ```

    <img width="702" alt="image" src="https://github.com/user-attachments/assets/6d00a842-60dd-4998-ae90-f3f90c8b10f8" />



## 3. 콘솔을 활용한 Kafka 메시지 송수신 확인

1. `traffic-generator-1`에서 Kafka 실습용 디렉터리로 이동
    
    #### **lab3-3-1**
        
    ```bash
    cd /opt/kafka
    ```
    
2. `traffic-generator-1`에서 스크립트를 이용하여 메세지를 받을 `consol-topic` 생성
    
    #### **lab3-3-2**
        
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic consol-topic --partitions 2 --replication-factor 2
    ```
    
    ![Image](https://github.com/user-attachments/assets/9321a32b-fde4-486b-8398-da235d7d1de0)

3. `traffic-generator-1`에서 `consol-topic`으로 메세지 전송 스크립트 실행
    
    #### **lab3-3-3**
        
    ```bash
    bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
    ```

4. 송신할 메세지를 하나씩 입력 후 `Enter` 입력

    #### **lab3-3-4**

    ```
    test1
    ```
    ```
    test2
    ```
    ```
    test3
    ```
    ![Image](https://github.com/user-attachments/assets/800bd1cb-72a6-4cff-afd0-70fa42cbe79d)


5. 송신되는 시간 5초 대기 후 `ctrl` + `c`로 종료

6. `traffic-generator-2`에서 Kafka 실습용 디렉터리로 이동
    
    #### **lab3-3-6**
        
    ```bash
    cd /opt/kafka
    ```
    
7. `traffic-generator-2`에서 `consumer-group-earliest` 그룹으로 `consol-topic`의 메시지를 `earlist` 옵션으로 메시지 수신
    
    #### **lab3-3-7**
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest \
    --consumer-property auto.offset.reset=earliest
    ```
    ![earliest 1](https://github.com/user-attachments/assets/bb5b7e75-d8b1-4c32-8344-7b6a2e752d7a)


8. `ctrl` + `c`로 종료


9. `traffic-generator-2`에서 `consumer-group-earliest-notcommit` 그룹으로 `consol-topic`의 메시지를 `earlist` 옵션과 `not commit` 옵션으로 메세지 수신

    #### **lab3-3-9**
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest-notcommit \
    --consumer-property auto.offset.reset=earliest \
    --consumer-property enable.auto.commit=false
    ```
    ![earliest notcommit 1](https://github.com/user-attachments/assets/b1723fab-3552-4ce6-864f-83d9f1eecb4f)

10. `ctrl` + `c`로 종료

11. `traffic-generator-2`에서 `consumer-group-latest` 그룹으로 `consol-topic`의 메시지를 `latest` 옵션으로 메세지 수신

    #### **lab3-3-11**

    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-latest \
    --consumer-property auto.offset.reset=latest
    ```
    ![latest 1](https://github.com/user-attachments/assets/775440c5-5cfa-49be-afbe-d125ee29d2c0)

12. `ctrl` + `c`로 종료

13. traffic-generator-1에서 consol-topic으로 메세지 전송 스크립트 실행

    #### **lab3-3-13**
        
    ```bash
    bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
    ```

14. 송신할 메세지를 하나씩 입력 후 `Enter` 입력

    #### **lab3-3-14**

    ```
    test4
    ```
    ```
    test5
    ```
    ```
    test6
    ```
    ![Image](https://github.com/user-attachments/assets/27cf5a74-f03f-4874-92a8-96c97e30b0d0)

15. 송신되는 시간 5초 대기 후 `ctrl` + `c`로 종료


16. `traffic-generator-2`에서 `consumer-group-earliest` 그룹으로 `consol-topic`의 메시지를 `earlist` 옵션으로 메시지 수신
    
    #### **lab3-3-16**
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest \
    --consumer-property auto.offset.reset=earliest
    ```
    ![earliest 2](https://github.com/user-attachments/assets/eb96892e-b67c-482c-9cce-eda5b78d7ce7)


17. `ctrl` + `c`로 종료

18. `traffic-generator-2`에서 `consumer-group-earliest-notcommit` 그룹으로 `consol-topic`의 메시지를 `earlist` 옵션과 `not commit` 옵션으로 메세지 수신

    #### **lab3-3-18**
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest-notcommit \
    --consumer-property auto.offset.reset=earliest \
    --consumer-property enable.auto.commit=false
    ```
    ![earliest notcommit 2](https://github.com/user-attachments/assets/58d6bbbb-a91f-4398-830a-9c5bf5cfd29a)


19. `ctrl` + `c`로 종료


20. `traffic-generator-2`에서 `consumer-group-latest` 그룹으로 `consol-topic`의 메시지를 `latest` 옵션으로 메세지 수신

    #### **lab3-3-20**

    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-latest \
    --consumer-property auto.offset.reset=latest
    ```
    ![latest 2](https://github.com/user-attachments/assets/9aabbab4-0434-466f-a4dc-203e66d2bfa2)


21. `ctrl` + `c`로 종료


22. `traffic-generator-2`에서 생성된 consumer 그룹 목록 확인

    #### **lab3-3-22**

    ```bash
    bin/kafka-consumer-groups.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --list
    ```
    ![컨슈머 그룹 최종](https://github.com/user-attachments/assets/332734ef-912d-43cd-8286-4da3dbf69b38)

## 4. Python SDK를 활용한 Kafka 메시지 송수신 확인

1. `traffic-generator-1`에서 Python-SDK를 이용하여 메세지를 받을 `python-topic` 생성
    #### **lab3-4-1**
    
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic python-topic --partitions 2 --replication-factor 2
    ```

    ![Image](https://github.com/user-attachments/assets/f9cf89d8-fd0b-46ac-8043-914a22228f8d)

2. `traffic-generator-1`에서 Kafka 실습용 디렉터리로 이동
    #### **lab3-4-2**

    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab03/kafka
    ```

3. `traffic-generator-1`에서 `python-topic`으로 메세지를 전송
    - **Note**: [`kafka_publisher.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/kafka/kafka_publisher.py) 
    #### **lab3-4-3**
    
    ```bash
    python3 kafka_publisher.py
    ```

    ![Image](https://github.com/user-attachments/assets/64712617-66df-4dd2-849a-8f2d1ee28006)

4. `traffic-generator-2`에서 Kafka 실습용 디렉터리로 이동

    #### **lab3-4-4**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab03/kafka
    ```

5. `traffic-generator-2`에서 `python-topic`으로부터 메세지를 수신
    - **Note**: [`kafka_subscriber.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/kafka/kafka_subscriber.py)

    #### **lab3-4-5**

    ```bash
    python3 kafka_subscriber.py
    ```
    ![Image](https://github.com/user-attachments/assets/50dba0ea-868e-4730-b0ec-15aab3578609)

6. `traffic-generator-2`에서 오프셋 3부터 메시지 소비 시작 및 오프셋 4에서 커밋 옵션을 추가하여 메세지 수신

    #### **lab3-4-6**

    ```bash
    python3 kafka_subscriber.py --start-offset 3 --commit-threshold 4
    ```
    ![Image](https://github.com/user-attachments/assets/7ffe09d3-efc2-4f01-9827-3d760f8fb452)

## 5. Logstash와 콘솔을 활용한 Nginx 로그 수신 확인

1. `traffic-generator-1`에서 Kafka 실습용 디렉터리로 이동
    #### **lab3-5-1**
        
    ```bash
    cd /opt/kafka
    ```
    
2. `traffic-generator-1`에서 nginx을 이용하여 메세지를 받을 `nginx-topic` 생성
    #### **lab3-5-2**
        
    ```bash
    bin/kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --create --topic nginx-topic --partitions 2 --replication-factor 2
    ```

    ![Image](https://github.com/user-attachments/assets/1574a7c0-9dfa-4945-8b5a-8ce0824b381e)

3. `traffic-generator-2`에서 Kafka 실습용 디렉터리로 이동
   #### **lab3-5-3**
        
    ```bash
    cd /opt/kafka
    ```

4. `traffic-generator-2`에서 `nginx-topic`의 메세지를 수신하기 위해 consumer 스크립트 실행

    #### **lab3-5-4**
    
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --topic nginx-topic --from-beginning
    ```

5. 웹 브라우저 주소창에서 아래 URL 입력


    #### **lab3-5-5**
    
    ```bash
    http://{ALB의 Public IP}
    ```
    ![웹브라우저에서 URL 입력](https://github.com/user-attachments/assets/03d041ce-013b-465d-b829-202022aabe79)

6. 웹 브라우저에서 로그를 생성하기 위해 Products 검색 등 실행
    ![웹브라우저 URL 접속 후 로그 생성](https://github.com/user-attachments/assets/e7472aba-e8be-433b-8d3d-478fb574c4f7)


7. `trarffic-generator-2`의 터미널에서 NGINX 로그 확인
    ![nginx로그 consume](https://github.com/user-attachments/assets/c2dc790e-d249-41bb-965a-de8a0fc48038)

8. `ctrl`+`c` 키를 입력하여 종료


## 6. S3 액세스 키 발급

1. 카카오 클라우드 콘솔에서 우측 상단 계정 프로필 > 자격 증명
2. 비밀번호 재확인 > 비밀번호 입력 > 비밀번호 확인
3. `S3 액세스 키` 탭 클릭
4. `S3 액세스 키 생성` 버튼 클릭

    - S3 액세스 키 생성 정보
        - 프로젝트: `사용자가 위치한 프로젝트`
        - S3 액세스 키 이름: `s3-acc-key`
        - S3 액세스 키 설명 (선택): `빈 칸`
    - 생성 버튼 클릭

    ![Image](https://github.com/user-attachments/assets/e5f89822-cb4f-4922-bf9c-f142e341e888)

5. `S3 액세스 키 정보`의 `인증 키`와 `보안 엑세스 키` 복사 후 클립보드 등에 붙여넣기
    - **Note**: S3 액세스 키 정보 팝업창을 닫은 이후 S3 인증 정보 다시 조회 불가
    - 확인 버튼 클릭

    ![Image](https://github.com/user-attachments/assets/9e2bf8ff-5869-40e5-b151-1360cbb6ea59)

## 7. s3 sink connector VM 생성 (2분)

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `s3-sink-connector`
        - 개수: `1`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.2xlarge`
    - 볼륨: `10`
    - 키 페어: 위에서 생성한 `keypair`
    - 네트워크
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
        - 유형: `새 인터페이스`
        - IP 할당 방식: `자동`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭  
            - 보안 그룹 이름: `s3-con-sg`
                - 인바운드 규칙
                    - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`, 설명(선택): `ssh`
                    - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`, 설명(선택): `kafka`
                - 아웃바운드 규칙
                    - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
        
    - 고급 설정
        - 사용자 스크립트: [`s3_sink_connector_init.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/kafka/s3_sink_connector_init.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
            - **Note**: 스크립트에 대한 자세한 내용은 아래 파일들 참고
                - [s3_sink_connector.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/kafka/s3_sink_connector.sh)
                  
        #### **lab3-7-2**
        ```
        #!/bin/bash
        # s3_sink_connector_init.sh
        echo "kakaocloud: 1. 환경 변수 설정 시작"
        
        cat <<'EOF' > /tmp/env_vars.sh
        # 기존 리소스 정보
        export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
        export API_SRV_IP="{API Server의 Public IP}"
        
        # S3 인증 정보
        export AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
        export AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
        
        # AWS 환경 변수 설정
        export BUCKET_NAME="data-catalog-bucket"
        export AWS_DEFAULT_REGION_VALUE="kr-central-2"
        export AWS_DEFAULT_OUTPUT_VALUE="json"
        
        # 로그 파일 경로
        export LOGFILE="/home/ubuntu/setup.log"
        EOF
        
        # 환경 변수 적용 
        source /tmp/env_vars.sh
        echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc
        
        echo "kakaocloud: 2. 스크립트 다운로드 사이트 유효성 검사 시작"
        SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/kafka/s3_sink_connector.sh"
        
        curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
        wget -q "$SCRIPT_URL"
        chmod +x s3_sink_connector.sh
        sudo -E ./s3_sink_connector.sh
        ```
                
    - CPU 멀티스레딩: `활성화`
        
    - 생성 버튼 클릭

3. `s3-sink-connector` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭

    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭

4. `s3-sink-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭

    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab3-7-4-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab3-7-4-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab3-7-4-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{s3-sink-connector public ip주소}
    ```
    
    
    
    #### **lab3-7-4-4**
    
    ```bash
    yes
    ```

5. Kafka Connector 스크립트 적용 확인
    #### **lab3-7-5**
    - **Note**: 터미널 창이 작으면 로그가 안보일 수도 있으니, 터미널 창의 크기를 늘려주세요.
   
    ```
    watch -c 'awk "/^kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}" < /var/log/cloud-init-output.log'
    ```
    - 모든 스크립트가 완료되면 아래와 같음
    ```
    kakaocloud: 1. 환경 변수 설정 시작
    kakaocloud: 2. 스크립트 다운로드 사이트 유효성 검사 시작
    kakaocloud: 3. 필수 환경 변수 검증 시작
    kakaocloud: 4. 시스템 업데이트 및 필수 패키지 설치 시작
    kakaocloud: 5. Kafka 설치 시작
    kakaocloud: 6. Confluent Hub Client 설치 시작
    kakaocloud: 7. Java 환경 변수 등록 시작
    kakaocloud: 8. S3 Sink Connector 설치 시작
    kakaocloud: 9. AWS CLI 설치 시작
    kakaocloud: 10. AWS CLI 설정 시작
    kakaocloud: 11. Kafka Connect 설정 폴더 권한 부여 시작
    kakaocloud: 12. 커스텀 플러그인 다운로드 시작
    kakaocloud: 13. mysql-s3-sink-connector.json 생성 시작 (8084 포트용)
    kakaocloud: 14. connect-distributed-mysql-s3-sink.properties 생성 시작 (8084 포트용)
    kakaocloud: 15. kafka-connect-mysql-s3-sink.service 등록 시작 (8084 포트용)
    kakaocloud: 16. Avro 컨버터 설치 및 설정 시작
    kakaocloud: 17. 순수 KEY=VALUE 파일 생성 시작
    kakaocloud: 18. connect-distributed-nginx-s3-sink.properties 생성 시작 (8083 포트용)
    kakaocloud: 19. kafka-connect-nginx-s3-sink.service 등록 시작 (8083 포트용)
    kakaocloud: 20. nginx-s3-sink-connector.json 생성 시작 (8083 포트용)
    kakaocloud: Setup 완료
    ```
6. `data-catalog-bucket`에 nginx 로그를 쌓기 위해 필요한 쓰기 권한을 부여하는 명령어 실행

    #### **lab3-7-6**
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket data-catalog-bucket \
      --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```

7. nginx-s3-sink-connector 생성
    
    #### lab**3-7-7**
   
    ```bash
    curl -s -X POST \
      -H "Content-Type: application/json" \
      --data @/home/ubuntu/kafka/config/connectors/nginx-s3-sink-connector.json \
      http://localhost:8083/connectors \
    | jq .
    ```

8. `nginx-s3-sink-connector` 커넥터 상태 확인

    #### lab**3-7-8**
    
     ```bash
     curl -s http://localhost:8083/connectors/nginx-s3-sink-connector/status | jq .
     ```
    ![image](https://github.com/user-attachments/assets/012ca5ef-70e6-499e-a8d1-22a4fa83eae0)


9. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
10. `data-catalog-bucket` 클릭
11. NGINX 로그가 쌓인 디렉터리로 이동 후 버킷 내 적재된 NGINX 로그 적재 확인
    - **Note**: `/kafka-nginx-log/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}/day_{현재 일}/hour_{현재 시}`디렉터리로 이동
   ![nginx로그 object storage 적재](https://github.com/user-attachments/assets/f825bf28-1302-4c4c-92e0-7d250cb5d86f)
