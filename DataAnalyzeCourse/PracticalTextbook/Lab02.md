# Kafka 기반 데이터 스트리밍 및 Object Storage 연동

Kafka로 메시지를 송수신하고, Nginx 로그를 실시간으로 수집·처리하는 과정을 다룹니다. 또한, Kafka Connect와 S3 Sink Connector를 이용해 수집된 데이터를 Object Storage에 저장하는 방법을 실습합니다.

---

## 1. Kafka Cluster 생성

1. 카카오 클라우드 콘솔 > Analytics > Advanced Managed Kafka > 클러스터
2. 클러스터 생성 버튼 클릭
    - 기본 설정
        - 클러스터 이름: `kafka`
        - Kafka 버전: `3.7.1`
        - 포트: `9092`
    - 인스턴스 유형: `r2a.2xlarge`
    - 네트워크 설정
        - VPC: `kc-vpc`
        - Subnet: `kr-central-2-a의 Public 서브넷`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭
            - 보안 그룹 이름: `kafka-clu-sg`
            - 보안 그룹 설명: `없음`
            - **Note**: `인바운드`, `아웃바운드` 생성 시 `+`버튼을 눌러 생성
            - 인바운드 규칙
                - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`
            - 아웃바운드 규칙
                - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
            - `생성` 버튼 클릭
    - 브로커 구성 설정
        - 지정된 가용 영역 수: `1`
        - 브로커 수: `2`
        - 볼륨 유형/크기: `SSD`/`50`
        - 최대 IOPS: `3000`
    - 생성 버튼 클릭

3. 위에서 생성한 `kafka` 클러스터 클릭
    ![1](https://github.com/user-attachments/assets/e8cbc795-c3e4-429a-b957-119910f9492e)
4. 우측 상단의 `부트스트랩 서버` 복사 후 클립보드 등에 붙여넣기
    ![2](https://github.com/user-attachments/assets/fcdfb4ad-6206-42df-9319-70459e1f59c4)

## 2. Kafka 실습을 위한 API Server 환경 설정 

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
2. `api-server-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭

    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab2-2-2-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab2-2-2-2**
    
    ```bash
    chmod 400 keypair.pem
    
    ```
    
    #### **lab2-2-2-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{api-server-1의 public ip 주소}
    
    ```
    
    - **Note**: {api-server-1의 public ip 주소} 부분을 복사한 각 IP 주소로 교체
    
    #### **lab2-2-2-4**
    
    ```bash
    yes
    
    ```
    

3. API Server VM의 `temp-kafka-bootstrap-server` 값을 실제 생성된 Kafka 클러스터 부트스트랩 서버 값으로 수정

    #### lab2-2-3
    
    ```bash
    sudo sed -i 's/temp-kafka-bootstrap-server/{실제 Kafka 클러스터 부트스트랩 서버값}/g' /home/ubuntu/.bashrc /etc/default/logstash
    ```
    - {실제 Kafka 클러스터 부트스트랩 서버값}을 개인 환경에 맞게 수정 필요

4. /etc/default/logstash의 `ENABLE_KAFKA_OUTPUT`을 수정하여 Kafka Output을 활성화

    #### lab2-2-4
    
    ```bash
    sudo sed -i 's/^ENABLE_KAFKA_OUTPUT="false"/ENABLE_KAFKA_OUTPUT="true"/' /etc/default/logstash
    ```

5. `api-server-1`에서 Logstash 설정 파일을 수정하여 Kafka로 송신하도록 설정

    #### lab2-2-5
   
    ```
    sudo sed -i 's/logs-to-pubsub.conf/logs-to-kafka.conf/g' /etc/logstash/logstash.yml
    ```

6. Logstash 재시작 및 상태 확인
    
    #### lab2-2-6-1
    
    ```bash
    sudo systemctl daemon-reload
    ```

    #### lab2-2-6-2
    
    ```bash
    sudo systemctl restart logstash
    ```

7. Logstash 가 `Active:active (running)` 상태인 것을 확인
    #### lab2-2-6-3

    ```bash
    sudo systemctl status logstash
    ```

    - `ctrl` + `c`로 종료

    ![image](https://github.com/user-attachments/assets/98ac20eb-1018-48f3-824d-ca5ad848f243)


## 3. Kafka 실습을 위한 Traffic Generator 환경 설정

1. `traffic-generator-1, 2`에서 Kafka 부트스트랩 서버 주소를 환경 변수로 설정
    
    #### lab2-3-1
   - **Note**: `{Kafka 부트스트랩 서버}`: `kafka` 클러스터의 부트스트랩 서버 입력
    
    ```bash
    echo 'export KAFKA_BOOTSTRAP_SERVERS="{Kafka 부트스트랩 서버}"' >> ~/.bashrc \
    && source ~/.bashrc
    ```
    
2. `traffic-generator-1, 2`에서 Kafka 클러스터와 통신 확인
    
    #### lab2-3-2
    - **Note**: 콤마(,) 기준으로 앞뒤의 kafka 클러스터의 부트스트랩 서버 주소 하나씩 입력
    - **Note**: 포트 번호 입력 시 콜론(:) 대신 공백(space) 넣은 후 진행
    
    ```bash
    nc -zv {Kafka 클러스터의 부트스트랩 서버}
    ```
    ![image](https://github.com/user-attachments/assets/e769ee52-5a32-49f6-8124-f20c9ed60227)
    


## 4. 콘솔 스크립트를 통한 Kafka 메시지 송수신 확인(수정중)

1. `traffic-generator-1`에서 kafka 작업을 위한 디렉터리인 `/opt/kafka`로 이동
    
    #### lab2-4-1
        
    ```bash
    cd /opt/kafka
    ```
    
2. `traffic-generator-1`에서 kafka-console을 이용하여 메세지를 받을 `consol-topic` 생성
    
    #### lab2-4-2
        
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic consol-topic --partitions 2 --replication-factor 2
    ```
    
    - 사진 예정(사진 넣은 후 삭제)

3. `traffic-generator-1`에서 `consol-topic` 토픽으로 메세지를 전송하기 위한 producer 스크립트 실행
    
    #### lab2-4-3
        
    ```bash
    bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
    ```

4. 송신할 메세지를 하나씩 입력 후 `Enter` 입력

    #### lab2-4-4-1

    ```
    test1
    ```
    
    #### lab2-4-4-2

    ```
    test2
    ```
    
    #### lab2-4-4-3

    ```
    test3
    ```
    - 송신되는 시간 5초 대기 후 `ctrl` + `c`로 종료

5. `traffic-generator-2`에서 kafka 작업을 위한 디렉터리인 `/opt/kafka`로 이동
    
    #### lab2-4-5
        
    ```bash
    cd /opt/kafka
    ```
    
6. `traffic-generator-2`에서 `consumer-group-earliest` 그룹으로 `consol-topic` 토픽의 메시지를 수신하기 위해 consumer 스크립트에 `earlist` 옵션을 추가하여 실행
    - `traffic-generator-1`에서 입력했던 메세지 수신 확인
    
    #### lab2-4-6
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest \
    --consumer-property auto.offset.reset=earliest
    ```

    - `ctrl` + `c`로 종료

   - 사진 예정(사진 넣은 후 삭제)

7. `traffic-generator-2`에서 `consumer-group-earliest-notcommit` 그룹으로 `consol-topic` 토픽의 메시지를 수신하기 위해 consumer 스크립트에 `earlist` 옵션과 `not commit` 옵션을 추가하여 실행
    - `traffic-generator-1`에서 입력했던 메세지 수신 확인

    #### lab2-4-7
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest-notcommit \
    --consumer-property auto.offset.reset=earliest \
    --consumer-property enable.auto.commit=false
    ```

    - `ctrl` + `c`로 종료

   - 사진 예정(사진 넣은 후 삭제)

8. `traffic-generator-2`에서 `consumer-group-latest` 그룹으로 `consol-topic` 토픽의 메시지를 수신하기 위해 consumer 스크립트에 `latest` 옵션을 추가하여 실행
    - `traffic-generator-1`에서 입력했던 메세지 수신 확인

    #### lab2-4-8

    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-latest \
    --consumer-property auto.offset.reset=latest
    ```

    - `ctrl` + `c`로 종료

   - 사진 예정(사진 넣은 후 삭제)

9. `traffic-generator-1`에서 `consol-topic` 토픽으로 메세지를 전송하기 위한 producer 스크립트 실행
    
    #### lab2-4-9
        
    ```bash
    bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
    ```

10. 송신할 메세지를 하나씩 입력 후 `Enter` 입력

    #### lab2-4-10-1

    ```
    test4
    ```
    
    #### lab2-4-10-2

    ```
    test5
    ```
    
    #### lab2-4-10-3

    ```
    test6
    ```
     - 송신되는 시간 5초 대기 후 `ctrl` + `c`로 종료

11. `traffic-generator-2`에서 `consumer-group-earliest` 그룹으로 `consol-topic` 토픽의 메시지 수신하기 위해 consumer 스크립트에 `earlist` 옵션을 추가하여 실행
    - `traffic-generator-1`에서 입력했던 메세지 수신 확인
    
    #### lab2-4-11
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest \
    --consumer-property auto.offset.reset=earliest
    ```

    - `ctrl` + `c`로 종료

    - 사진 예정(사진 넣은 후 삭제)

12. `traffic-generator-2`에서 `consumer-group-earliest-notcommit` 그룹으로 `consol-topic` 토픽의 메시지를 수신하기 위해 consumer 스크립트에 `earlist` 옵션과 `not commit` 옵션을 추가하여 실행
    - `traffic-generator-1`에서 입력했던 메세지 수신 확인

    #### lab2-4-12
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest-notcommit \
    --consumer-property auto.offset.reset=earliest \
    --consumer-property enable.auto.commit=false
    ```

    - `ctrl` + `c`로 종료

    - 사진 예정(사진 넣은 후 삭제)

13. `traffic-generator-2`에서 `consumer-group-latest` 그룹으로 `consol-topic` 토픽의 메시지를 수신하기 위해 consumer 스크립트에 `latest` 옵션을 추가하여 실행
    - `traffic-generator-1`에서 입력했던 메세지 수신 확인

    #### lab2-4-13

    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-latest \
    --consumer-property auto.offset.reset=latest
    ```

    - `ctrl` + `c`로 종료

    - 사진 예정(사진 넣은 후 삭제)

14. `traffic-generator-2`에서 생성된 consumer 그룹 목록 확인

    #### lab2-4-14

    ```bash
    bin/kafka-consumer-groups.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --list
    ```

    - 사진 예정(사진 넣은 후 삭제)

## 6. Python SDK를 활용한 Kafka 메시지 송수신 확인

1. `traffic-generator-1`에서 Python-SDK를 이용하여 메세지를 받을 `python-topic` 생성
    #### lab2-6-1
    
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic python-topic --partitions 2 --replication-factor 2
    ```

    - 사진 예정(사진 넣은 후 삭제)

2. `traffic-generator-1`에서 Kafka 실습용 디렉터리로 이동
    #### lab2-6-2

    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/kafka
    ```

3. `traffic-generator-1`에서 `python-topic` 토픽으로 메세지를 전송하기 위한 `kafka_publisher` 파일 실행
    #### lab2-6-3
    
    ```bash
    python3 kafka_publisher.py
    ```
    - 사진 예정(사진 넣은 후 삭제)

4. `traffic-generator-1`에서 Kafka 실습용 디렉터리로 이동

    #### lab2-6-4
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/kafka
    ```

5. Python Consumer 파일을 실행아여 `python-topic` 토픽으로부터 메세지 수신

    #### lab2-6-3-2

    ```bash
    python3 kafka_subscriber.py
    ```
    - 사진 예정(사진 넣은 후 삭제)

6. `Ctrl`+`c` 키를 입력하여 종료

7. `traffic-generator-2`에서 옵션을 오프셋 3부터 메시지 소비를 시작하고 4개 메시지마다 커밋하도록 옵션을 수정하여 다시 실행하여 `python-topic`으로부터 메세지 수신 확인

    #### lab2-6-4

    ```bash
    python3 kafka_subscriber.py --start-offset 3 --commit-threshold 4
    ```
    - 사진 예정(사진 넣은 후 삭제)


## 7. Nginx 로그 수집 및 Kafka 전송

1. `traffic-generator-1`에서 kafka 작업을 위한 디렉터리인 `/opt/kafka`로 이동
    #### lab2-5-1-1
        
    ```bash
    cd /opt/kafka
    ```
    
2. `trarffic-generator-1`에서 nginx을 이용하여 메세지를 받을 `nginx-topic` 생성

    #### lab2-5-2-2
        
    ```bash
    bin/kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --create --topic nginx-topic --partitions 2 --replication-factor 2
    ```

    - 사진 예정(사진 넣은 후 삭제)

3. `traffic-generator-2`에서 kafka 작업을 위한 디렉터리인 `/opt/kafka`로 이동

   #### lab2-5-2-1
        
    ```bash
    cd /opt/kafka
    ```

3. `trarffic-generator-2`에서 `nginx-topic`의 메세지를 수신할 콘솔 Consumer 실행

    #### lab2-5-2-2
    
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --topic nginx-topic --from-beginning
    ```

3. Logstash 재시작 및 상태 확인
    
    #### lab2-7-3-1
    
    ```bash
    sudo systemctl daemon-reload
    ```

    #### lab2-7-3-2
    
    ```bash
    sudo systemctl restart logstash
    ```

4. 웹 브라우저 주소창에 `http://{ALB의 Public IP}`를 입력하여 접속 후 링크 클릭 등을 통해 임의로 트래픽 생성
    #### lab2-5-4
    
    ```bash
    http://{ALB의 Public IP}
    ```

5. `trarffic-generator-2`의 터미널에서 NGINX 로그 확인

    - `Ctrl`+`c` 키를 입력하여 종료

    - 사진 예정(사진 넣은 후 삭제)
    
6. `traffic-generator-1`에서 트래픽 생성을 위해 디렉터리 이동
    
    #### **lab2-7-6**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub/
    ```

7. `traffic-generator-1`에서 트래픽 로그를 생성하는 `traffic_generator.py` 실행
    - **Note**: 트래픽 로그가 자동으로 생성되어 NGINX 로그에 반영됨
    
    #### **lab2-7-7**
    
    ```bash
    python3 traffic_generator.py
    ```
   
    
## 6. S3 액세스 키 발급

1. 카카오 클라우드 콘솔에서 우측 상단 계정 프로필 > 자격 증명 > 비밀번호 확인
2. `S3 액세스 키` 탭 클릭
3. `S3 액세스 키 생성` 버튼 클릭

    - S3 액세스 키 생성 정보
        - 프로젝트: `사용자가 위치한 프로젝트`
        - S3 액세스 키 이름: `s3-acc-key`
        - S3 액세스 키 설명 (선택): `빈 칸`
    - 생성 버튼 클릭
    - S3 인증 정보 항목의 사용자 `인증 키` 복사 후 클립보드 등에 붙여넣기
    - S3 인증 정보 항목의 사용자 `보안 엑세스 키` 복사 후 클립보드 등에 붙여넣기
        - **Note**: S3 액세스 키 정보 팝업창을 닫은 이후 S3 인증 정보 다시 조회 불가
    - 확인 버튼 클릭

## 7. Kafka Connector VM 생성 (2분)
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭
    - Kafka Connector VM 생성 정보
        - 기본 정보
            - 이름: `kafka-connector`
            - 개수: `1`
            - 이미지: `Ubuntu 22.04`
            - 인스턴스유형: `m2a.xlarge`
            - 볼륨: `10`
            - 키 페어: 위에서 생성한 `keypair`
            - 네트워크
                - VPC: `kc-vpc`
                - 서브넷: `kr-central-2-a의 Public 서브넷`
            - 유형: `새 인터페이스`
            - IP 할당 방식: `자동`
            - 보안 그룹
            - **Note**: 기존에 Traffic Generator VM에서 사용한 보안그룹 사용
                - 보안 그룹 이름: `tg-sg` 선택
                    - 인바운드 규칙
                        - 프로토콜: TCP, 출발지: 0.0.0.0/0, 포트 번호: `22`
                        - 프로토콜: TCP, 출발지: 0.0.0.0/0, 포트 번호: `9092`
                    - 아웃바운드 규칙
                        - 프로토콜: ALL, 출발지: 0.0.0.0/0, 포트 번호: `ALL`
        
            - 고급 설정
                - 아래 스크립트 입력
                - **Note**: 메모장에 아래 링크의 코드를 복사 붙여넣기 하여 사용
                - **Note**: 중괄호({})는 제거하고 쌍 따옴표는 유지
                - 사용자 스크립트: [`kafka_vm_init.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_vm_init.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
                ```
                #!/bin/bash
                
                echo "kakaocloud: 1.환경 변수 설정 시작"
                
                cat <<'EOF' > /tmp/env_vars.sh
                # Kafka 설정
                export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
                
                # S3 인증 정보
                export AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
                export AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
                
                # AWS 환경 변수 설정
                export BUCKET_NAME="data-catalog"
                export AWS_DEFAULT_REGION_VALUE="kr-central-2"
                export AWS_DEFAULT_OUTPUT_VALUE="json"
                
                # 로그 파일 경로
                export LOGFILE="/home/ubuntu/setup.log"
                EOF
                
                # 환경 변수 적용 
                source /tmp/env_vars.sh
                echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc
                
                echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
                SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_full_setup.sh"
                
                curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
                wget -q "$SCRIPT_URL"
                chmod +x kafka_full_setup.sh
                sudo -E ./kafka_full_setup.sh
                ```
                
                - CPU 멀티스레딩: `활성화`
        
    - 생성 버튼 클릭
3. `kafka-connector` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭
4. `kafka-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab2-7-5-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab2-7-5-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab2-7-5-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{kafka-connector의 public ip주소}
    ```
    
    - {kafka-connector의 public ip주소}: 복사한 각 IP 주소 입력
    
    #### **lab2-7-5-4**
    
    ```bash
    yes
    ```

5. 스크립트 적용 확인
    #### **lab2-7-6**
   
    ```
    watch -c 'awk "/^kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}" < /var/log/cloud-init-output.log'
    ```

6. `data-catalog` 버킷에 nginx 로그를 쌓기 위한 쓰기 권한 부여

    #### lab2-7-3
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket data-catalog \
      --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```
    
7. S3 Sink Connector([`s3-sink-connector.properties`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/s3-sink-connector.properties)), Standalone Worker([`worker.properties`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/worker.properties)) 설정 파일 확인

    #### lab2-7-4
    
    ```
    ls /opt/kafka/config
    ```
    ![image](https://github.com/user-attachments/assets/2bdefc88-31aa-4d5e-8498-0a7ff3619da6)
    

8. kafka-connect 시스템 서비스 파일([`kafka-connect.service`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/kafka-connect.service)) 확인
    
    #### lab2-7-5
    
    ```bash
    ls /etc/systemd/system | grep kafka-connect.service
    ```

    
9. 데몬 리로드 및 서비스 시작
    
    #### lab2-7-6-1
    
    ```bash
    sudo systemctl daemon-reload
    ```

    #### lab2-7-6-2
   
    ```bash
    sudo systemctl enable kafka-connect
    ```
    
    #### lab2-7-6-3
    
    ```bash
    sudo systemctl start kafka-connect
    ```

     ![13](https://github.com/user-attachments/assets/b34813be-72bb-4842-9a3d-e03bbb0b30a5)

10. s3-sink-connector 상태 정보 조회
    - **Note**: `connector`, `tasks` 항목의 `state` 값이 `RUNNING`인 것을 확인
   
     #### lab2-7-7
    
     ```bash
     watch -n 1 "curl -s http://localhost:8083/connectors/s3-sink-connector/status | jq"
     ```

    ![14](https://github.com/user-attachments/assets/f18745bc-b791-47ea-b339-e46df150f376)

11. Object Storage 버킷 내 NGINX 로그 적재 확인
12. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
13. `data-catalog` 버킷 클릭

14. `/topics/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}/day_{현재 일}/hour_{현재 시}` 디렉터리로 이동

15. 버킷 내 추가로 적재된 NGINX 로그 적재 확인

     - 아래 결과 확인(사진 넣을 예정)



