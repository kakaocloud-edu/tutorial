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
            - **Note**: `VPC의 보안 그룹`으로 이동 됐을 시 `보안 그룹 생성` 후 기존에 쓰던 `클러스터 창`으로 이동
    - 브로커 구성 설정
        - 지정된 가용 영역 수: `1`
        - 브로커 수: `2`
        - 볼륨 유형/크기: `SSD`/`50`
        - 최대 IOPS: `3000`
    - 생성 버튼 클릭
    - 아래 결과 확인
![1](https://github.com/user-attachments/assets/e8cbc795-c3e4-429a-b957-119910f9492e)

3. 위에서 생성한 `kafka` 클러스터 클릭
    - 우측 상단의 `부트스트랩 서버` 복사 후 클립보드 등에 붙여넣기
    - 아래 결과 확인
![2](https://github.com/user-attachments/assets/fcdfb4ad-6206-42df-9319-70459e1f59c4)

## 2. Kafka 실습을 위한 API SERVER VM 설정 

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
    
    - **Note**: {api-server-1의 public ip 주소} 부분을 복사한 각 IP 주소로 교체하세요.
    
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

4. /etc/default/logstash의 ENABLE_KAFKA_OUTPUT을 수정하여 Kafka Output을 활성화

    #### lab2-2-4
    
    ```bash
    sudo sed -i 's/^ENABLE_KAFKA_OUTPUT="false"/ENABLE_KAFKA_OUTPUT="true"/' /etc/default/logstash
    ```

5. `api-server-1`에서 Logstash 설정 파일을 수정하여 Kafka로 송신하도록 설정

    #### lab2-2-5-1
   
    ```
    sudo sed -i 's/logs-to-pubsub.conf/logs-to-kafka.conf/g' /etc/logstash/logstash.yml
    ```

    - Logstash 재시작 및 상태 확인
    
    #### lab2-2-5-2
    
    ```bash
    sudo systemctl daemon-reload
    ```

    #### lab2-2-5-3
    
    ```bash
    sudo systemctl restart logstash
    ```

    #### lab2-2-5-4

    ```bash
    sudo systemctl status logstash
    ```

    - `Active:active (running)` 확인
    - 아래 결과 확인
    ![3](https://github.com/user-attachments/assets/791245d1-7f81-4e4a-be7e-a9192645e7ad)


## 3. Kafka 기본 환경 설정

1. `traffic-generator-1, 2`에서 ~/.bashrc에 환경 변수 및 부트스트랩 서버 주소를 설정하여 Kafka 실행에 필요한 경로와 정보 등록
    
    #### lab2-3-1-1
   - **Note**: `{Kafka 부트스트랩 서버}`: `kafka` 클러스터의 부트스트랩 서버 입력
   - **Note**: `{Kafka 부트스트랩 서버}` 개인 환경에 맞게 수정 필수
    
    ```bash
    cat << 'EOF' >> ~/.bashrc
    export KAFKA_HOME=/opt/kafka
    export PATH=$PATH:$KAFKA_HOME/bin
    export KAFKA_BOOTSTRAP_SERVERS="{Kafka 부트스트랩 서버}"
    EOF
    ```
    
   #### lab2-3-1-2
    - 수정한 환경 변수 값 적용
    
    ```bash
    source ~/.bashrc
    ```
    
2. Kafka 클러스터와 통신 확인
    
    #### lab2-3-2
    - **Note**: `traffic-generator-1, 2`에서 진행
    - **Note**: 콤마(,) 기준으로 앞뒤의 kafka 클러스터의 부트스트랩 서버 주소 하나씩 입력
    - **Note**: 포트 번호 입력 시 콜론(:) 대신 공백(space) 넣은 후 진행
    
    ```bash
    nc -zv {Kafka 클러스터의 부트스트랩 서버}
    ```
    - 예시
      ```
      nc -zv 10.0.0.199 9092
      ```
   - 아래 결과 확인
       - **Note**: 실패 시 네트워크 및 보안 그룹 설정 확인

   - ![image](https://github.com/user-attachments/assets/e769ee52-5a32-49f6-8124-f20c9ed60227)
    

# 4. Kafka 메시지 송수신 확인

## 4-1. earlist 옵션의 카프카 콘솔 스크립트로 메시지 송수신

1. `traffic-generator-1`에서 kafka 작업을 위한 디렉터리인 `/opt/kafka`로 이동
    
    #### lab2-4-1-1
        
    ```bash
    cd /opt/kafka
    ```
    
2. `traffic-generator-1`에서 kafka-console을 이용하여 메세지를 받을 `consol-topic` 생성
    
    #### lab2-4-1-2
        
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic consol-topic --partitions 2 --replication-factor 2
    ```
    
    - 아래 결과 확인
![4](https://github.com/user-attachments/assets/c24f87ea-9ebc-4355-b4f7-a9661f052281)

3. `traffic-generator-1`에서 `kafka-console-producer.sh` 실행 후 송신할 메세지 입력 후 `Enter` 키 입력
    
    #### lab2-4-1-3

    - **Note**: 메세지가 입력될 때 마다 `offset`에 쌓임
    - **Note**: `offset 0` 부터 시작
    - `kafka-console-producer.sh` 실행
        
    ```bash
    bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
    ```

4. 메시지 입력
    ```
    test1
    test2
    test3
    ```
    - 메시지 입력 후 'Enter' 입력
    
5. `traffic-generator-2`에서 kafka 작업을 위한 디렉터리인 `/opt/kafka`로 이동
    
    #### lab2-4-1-5
        
    ```bash
    cd /opt/kafka
    ```
    
6. `traffic-generator-2`에서 Kafka 콘솔 컨슈머를 실행해 consumer-group-earliest 그룹으로 `consol-topic` 토픽의 메시지 수신
    
    #### lab2-4-1-6
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest \
    --consumer-property auto.offset.reset=earliest \
    --property print.offset=true
    ```

    - `traffic-generator-2` 터미널 창에서 `traffic-generator-1`에서 입력했던 메세지와 offset 수신 확인
    - 아래 결과 확인
![5](https://github.com/user-attachments/assets/cde48506-40d2-4550-a9f0-426da39e2438)

7. `traffic-generator-2`에서 `Ctrl` + `c` 키로 Kafka 콘솔 컨슈머 종료



## 4-2. latest 옵션의 카프카 콘솔 스크립트로 메시지 송수신
1. `traffic-generator-1`에서 실행 중인 콘솔 프로듀서에 송신할 메세지 입력 후 `Enter` 키 입력
    - **Note**: 전송되는 시간이 필요하므로 전송 후 5초 정도 대기
        ```
        test4
        test5
        test6
        ```
        - 메시지 입력 후 `Enter` 입력

2. `traffic-generator-2`에서 Kafka 콘솔 컨슈머를 실행해 consumer-group-latest 그룹으로 `consol-topic` 토픽의 메시지를 수신
    - **Note**: 이후 실행할 `producer` 메세지 받아야하므로 종료하면 안됨
    - **Note**: `consumer-group-latest`라는 새로운 그룹이므로 `offset 0`부터 쌓임
   
    #### lab2-4-2-2

    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-latest \
    --consumer-property auto.offset.reset=latest \
    --property print.offset=true
    ```
    - `auto.offset.reset`의 `latest` 옵션은 `consumer` 실행 이후 `producer`로 들어오는 `offset`부터 읽기 때문에 이전에 실행된 `producer`의 메세지 'test4~6'은 출력이 안되는 것 확인

3. `traffic-generator-1`에서 콘솔 프로듀서 실행 후 송신할 메세지 입력 후 `Enter` 키 입력
    - **Note**: 전송되는 시간이 필요하므로 전송 후 5초 정도 대기
    ```
    test7
    test8
    test9
    ```
    - **Note**: test를 입력할 때마다 latest 옵션의 `kafka-console-consumer`에서 출력되는 것 확인
    - `traffic-generator-1`에서 `Ctrl` + `c` 키로 종료
    - `traffic-generator-2`에서 `Ctrl` + `c` 키로 종료
    - 아래 결과 확인
 ![6](https://github.com/user-attachments/assets/37c653bf-85f0-46f8-a8ae-22d5011a4341)


4. `traffic-generator-2`에서 컨슈머 그룹 목록 확인
    
    #### lab2-4-2-4
        
    ```bash
    bin/kafka-consumer-groups.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --list
    ```
    - `consumer-group-latest`, `consumer-group-earliest` 두 값이 뜨는거 확인
    - 아래 결과 확인
![7](https://github.com/user-attachments/assets/be8f5dbd-25ab-4892-9f32-ef683406fb3e)


## 4-3. Python SDK로 메시지 송수신

1. `traffic-generator-1`에서 Python-SDK를 이용하여 메세지를 받을 `python-topic` 생성
    #### lab2-4-3-1
    
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic python-topic --partitions 2 --replication-factor 2
    ```

    - 아래 결과 확인
![8](https://github.com/user-attachments/assets/733df113-1628-43b7-a5c9-bb07b691b3ee)

2. `traffic-generator-1`에서 메세지를 전송할 Python 프로듀서 코드 실행
    #### lab2-4-3-2

    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/kafka
    ```
    ```bash
    python3 kafka_publisher.py
    ```

    - `python-topic`으로 메세지 전송 확인
    - 아래 결과 확인
![9](https://github.com/user-attachments/assets/5ec13a06-782d-4ae0-b1e3-a03b64c8f367)

3. `traffic-generator-2`에서 메세지를 수신할 Python 컨슈머 코드 실행

    #### lab2-4-3-3-1
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/kafka
    ```

    #### lab2-4-3-3-2

    ```bash
    python3 kafka_subscriber.py
    ```
        
    - `python-topic`으로 메세지 수신 확인 후 `Ctrl`+`c` 키를 입력하여 종료
    - 아래 결과 확인
![10](https://github.com/user-attachments/assets/cf9099b2-8960-4d04-a21a-71cbf0b30cd2)

  
4. `traffic-generator-2`에서 Python 컨슈머 코드의 옵션을 START_OFFSET = 3, commit_threshold = 4로 수정하여 다시 실행

    #### lab2-4-3-4

    ```bash
    sudo -E ./kafka_subscriber.py --start-offset 3 --commit-threshold 4
    ```

    - `python-topic`으로 메세지 수신 확인 후 `Ctrl`+`c` 키를 입력하여 종료
    - 아래 결과 확인
![11](https://github.com/user-attachments/assets/a6b1924c-83b1-43c1-a819-b80e701c4ccb)


# 5. Nginx 로그 수집 및 Kafka 전송

1. Nginx 로그 토픽 생성
    - `trarffic-generator-1`에서 nginx을 이용하여 메세지를 받을 `nginx-topic` 생성
    
    #### lab2-5-1
        
    ```bash
    bin/kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --create --topic nginx-topic --partitions 2 --replication-factor 2
    ```

    - 아래 결과 확인
![12](https://github.com/user-attachments/assets/8dad4862-9206-41f0-b892-ece7d2d04dbd)

2. `trarffic-generator-2`에서 `nginx-topic`의 메세지를 수신할 콘솔 컨슈머 실행
    
    #### lab2-5-2
    
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --topic nginx-topic --from-beginning
    ```
    
3. 웹 브라우저 주소창에 `http://{ALB의 Public IP}`를 입력하여 접속 후 링크 클릭 등을 통해 임의로 트래픽 생성
4. `trarffic-generator-2`의 터미널에서 NGINX 로그 확인

    - `Ctrl`+`c` 키를 입력하여 종료
    - 아래 결과 확인(사진 넣을 예정)
   
    
# 6. S3 Sink Connector 생성

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
2. `kafka-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab2-6-2-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab2-6-2-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab2-6-2-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{kafka-connector의 public ip주소}
    ```
    
    - {kafka-connector의 public ip주소}: 복사한 각 IP 주소 입력
    
    #### **lab2-6-2-4**
    
    ```bash
    yes
    ```

3. `data-catalog` 버킷에 nginx 로그를 쌓기 위한 쓰기 권한 부여

    #### lab2-6-3
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket data-catalog \
      --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```
    
4. S3 Sink Connector([`s3-sink-connector.properties`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/s3-sink-connector.properties)), Standalone Worker([`worker.properties`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/worker.properties)) 설정 파일 확인

    #### lab2-6-4
    
    ```
    ls /opt/kafka/config
    ```
    - 아래 결과 확인
    ![image](https://github.com/user-attachments/assets/2bdefc88-31aa-4d5e-8498-0a7ff3619da6)
    

5. kafka-connect 시스템 서비스 파일([`kafka-connect.service`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/kafka-connect.service)) 확인
    
    #### lab2-6-5
    
    ```bash
    ls /etc/systemd/system | grep kafka-connect.service
    ```

    
6. 데몬 리로드 및 서비스 시작
    
    #### lab2-6-6-1
    
    ```bash
    sudo systemctl daemon-reload
    ```

    #### lab2-6-6-2
    
    ```bash
    sudo systemctl enable kafka-connect
    ```
    
    #### lab2-6-6-3
    
    ```bash
    sudo systemctl start kafka-connect
    ```

    - 아래 결과 확인
![13](https://github.com/user-attachments/assets/b34813be-72bb-4842-9a3d-e03bbb0b30a5)

7. s3-sink-connector 상태 정보 조회
   - **Note**: `connector`, `tasks` 항목의 `state` 값이 `RUNNING`인 것을 확인
   
    #### lab2-5-7
    
    ```bash
    watch -n 1 "curl -s http://localhost:8083/connectors/s3-sink-connector/status | jq"
    ```

    - 아래 결과 확인
![14](https://github.com/user-attachments/assets/f18745bc-b791-47ea-b339-e46df150f376)

8. Object Storage 버킷 내 NGINX 로그 적재 확인
    - 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
    - `data-catalog` 버킷 클릭

    - `/topics/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}/day_{현재 일}/hour_{현재 시}` 디렉터리로 이동

    - 버킷 내 적재된 NGINX 로그 적재 확인

    - 아래 결과 확인(사진 넣을 예정)



