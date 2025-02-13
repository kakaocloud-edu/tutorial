# Kafka 기반 데이터 스트리밍 및 Object Storage 연동

Kafka를 활용하여 메시지를 송수신하고, Nginx 로그를 실시간으로 수집 및 처리하는 과정을 다룹니다. 또한, Kafka Connect와 S3 Sink Connector를 활용하여 수집된 데이터를 Object Storage에 저장하는 방법을 실습합니다.

---

## 1. 각 VM에 Kafka 클라이언트 설치
1. Java 설치(Traffic-Generator-VM1, 2)
   #### **lab2-1-1**
      - 홈 디렉토리로 이동
   ```bash
   cd
   ```
   #### **lab2-1-2**
      - Java 설치
   ```bash
   sudo apt update
   sudo apt install -y openjdk-21-jdk
   java -version
   ```
    
2. Kafka 바이너리 다운로드 및 설치
   #### **lab2-1-3**
   ```bash
   cd /opt
   sudo wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
   sudo tar -xzf kafka_2.13-3.7.1.tgz
   sudo mv kafka_2.13-3.7.1 kafka
   sudo rm kafka_2.13-3.7.1.tgz
   ```

3. 환경 변수 설정
   #### **lab2-1-4**
      - 카프카 부트스트랩 서버 환경에 맞게 입력
   ```bash
   echo 'export KAFKA_HOME=/opt/kafka' >> ~/.bashrc
   echo 'export PATH=$PATH:$KAFKA_HOME/bin' >> ~/.bashrc
   echo export KAFKA_BOOTSTRAP_SERVERS="{카프카 부트스트랩 서버}" >> ~/.bashrc
   source ~/.bashrc
   ```

4. Python 환경 준비
   #### **lab2-1-5**
      - Python, Kafka-Python 설치
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip
   python3 --version
   pip3 --version
   sudo pip3 install kafka-python
   ```

5. Kafka 클러스터와 통신 확인
   #### **lab2-1-6**
      - 네트워크 통신 가능 여부 체크(각 클러스터의 부트스트랩 서버)
   ```bash
   nc -zv {각 클러스터의 부트스트랩 서버}
   nc -zv {각 클러스터의 부트스트랩 서버}
   ```
      - 예시
   ```bash    
   nc -zv 0.0.0.0 9092
   nc -zv 0.0.0.0 9092
   ```
    
      - 실패 시 네트워크 및 보안 그룹 설정을 확인합니다.


## 2. 콘솔 스크립트로 메시지 프로듀싱/컨슈밍 실습
1. 카프카 디렉토리로 이동 (TG1, 2)
   #### **lab2-2-1**
   ```
   cd kafka
   ```

2. 토픽 생성 (TG1)
   #### **lab2-2-2**
   ```
   bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --create --topic consol-topic --partitions 2 --replication-factor 2
   ```

3. 프로듀서 실행(TG1)
   #### **lab2-2-3**
   ```
   bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
   ```

4. 컨슈머 실행(TG2)
   #### **lab2-2-4-1**
      a. earliest 설정
   ```
   bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic --group consumer-group-earliest --from-beginning
   ```
   #### **lab2-2-4-2**
      b. latest 설정
   ```
   bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic --group consumer-group-latest
   ```

## 3. python 코드로 메시지 프로듀싱/컨슈밍 실습
1. python 토픽 생성(TG1)
   #### **lab2-3-1**
   ```
   bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --create --topic python-topic --partitions 2 --replication-factor 2
   ```

2. producer.py실행(TG1)
   #### **lab2-3-2**
   ```
   sudo wget -O producer.py "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/Kafka_Connect_VM/producer.py"
   sudo chmod +x producer.py
   sudo -E ./producer.py
   ```

3. consumer.py실행(TG2)
   #### **lab2-3-3**
   ```
   sudo wget -O consumer.py "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/Kafka_Connect_VM/consumer.py"
   sudo chmod +x consumer.py
   sudo -E ./consumer.py
   ```


## 4. nginx 로그 → kafka로 프로듀싱 실습 (logstash 활용)
1. 콘솔 스크립트(바이너리)로 새로운 토픽 생성(TG1)
   #### **lab2-4-1**
   ```
   bin/kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --create --topic nginx-topic --partitions 2 --replication-factor 2
   ```

2. api서버에서 logstash 설정(API VM1, 2)
   #### **lab2-4-2**
   ```
   cd /etc/logstash/
   sudo vi logstash.yml
   ```

      - 보이는 파일
   ```
   path.data: /var/lib/logstash
   path.logs: /var/log/logstash
   path.config: /etc/logstash/conf.d/logs-to-pubsub.conf
   ```

3. path.config 수정 필요 logs-to-pubsub.conf -> logs-to-kafka.conf
      - path.config 수정
   ```bash
   i 클릭 후 방향키로 이동하여logs-to-pubsub.conf로 이동
   logs-to-pubsub.conf에서 pubsub 삭제 후 kafka 입력
   esc 클릭 후 :wq 입력
   ```

4. Logstash 재실행 및 상태 확인 (API VM1, 2)
   #### **lab2-4-3**
   ```
   sudo systemctl restart logstash
   sudo systemctl status logstash
   ```

5. TG에서 데이터 받기 (TG1)
   #### **lab2-4-4**
   ```
   bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --topic nginx-topic --from-beginning
   ```
      - Note: 데이터가 쌓이고 있는지 체크(시간 좀 걸림)


---


# kafka → kafka connector → object storage 실습

      - kafka connector역할을 할 VM 생성
   
1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭

    - 기본 정보
        - 이름: `kafka-connector`
        - 개수: `1`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.xlarge`
    - 볼륨: `30`
    - 키 페어: 위에서 생성한 `keypair`
    - 네트워크
        - VPC: `kc-vpc`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름: `tg-sg`
                  - 인바운드
                  
                      | 프로토콜 | 출발지 | 포트 번호 |
                      | --- | --- | --- |
                      | TCP | 0.0.0.0/0 | 22 |
                      | TCP | 0.0.0.0/0 | 80 |
                      | TCP | 0.0.0.0/0 | 9092 |
              
                  - 아웃바운드
                  
                      | 프로토콜 | 목적지 | 포트 번호 |
                      | --- | --- | --- |
                      | ALL | 0.0.0.0/0 | ALL |
    
            - 네트워크 인터페이스: `새 인터페이스`
            - 서브넷: `kr-central-2-a의 Public 서브넷`
            - IP 할당 방식: `자동`
    - 고급 설정
        - 아래 코드 입력
```
#!/bin/bash

# apt 패키지 목록 업데이트
sudo apt update

# 필요한 패키지 설치
sudo apt install -y python3 python3-pip openjdk-21-jdk unzip jq
```
3. 생성 버튼 클릭
4. `kafka-connector` 상태 Actice 확인 후 `Public IP 연결`


## 1. 새로운 Kafka Connector VM에서 사전 준비
1. Kafka Connector VM에 SSH 연결
   #### **lab2-5-1**
   ```bash
   ssh -i {keypair}.pem ubuntu@{vm public ip}
   ```

2. Kafka 다운로드 및 압축 해제
   #### **lab2-5-2**
   ```bash
   cd /home/ubuntu
   curl https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz -o kafka_2.13-3.7.1.tgz
   tar -xzf /home/ubuntu/kafka_2.13-3.7.1.tgz
   rm /home/ubuntu/kafka_2.13-3.7.1.tgz
   mv /home/ubuntu/kafka_2.13-3.7.1 /home/ubuntu/kafka
   ```

3. Confluent Hub Client 설치
   #### **lab2-5-3**
   ```bash
   cd /
   sudo mkdir -p /confluent-hub/plugins && \
   cd /confluent-hub && \
   sudo curl -LO http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz && \
   sudo tar -zxvf confluent-hub-client-latest.tar.gz
   ```

4. 환경 변수 설정
   #### **lab2-5-4**
      - 환경 변수 폴더 열기
   ```bash
   vi /home/ubuntu/.bashrc
   ```
      - 아래 내용을 `.bashrc` 맨 아래에 추가
   #### **lab2-5-5**
   ```bash
   # Confluent 설정
   export CONFLUENT_HOME='/confluent-hub'
   export PATH="$PATH:$CONFLUENT_HOME/bin"
   
   # Java 설정
   export JAVA_HOME='/usr/lib/jvm/java-21-openjdk-amd64'
   export PATH="$JAVA_HOME/bin:$PATH"
   ```

   #### **lab2-5-6**
      - 변경 사항 적용
   ```bash
   source /home/ubuntu/.bashrc
   ```
   

## 2. Object Storage 버킷의 CORS 정책으로 쓰기 접근 권한 허용
1. API 인증 토큰 발급
    - 사용자 로컬 머신의 터미널에 접속합니다. 아래 명령에서 `ACCESS_KEY`와 `ACCESS_SECRET_KEY`를 각각 '액세스 키'와 '보안 액세스 키' 값으로 수정합니다.
    - 그 다음 아래 API 인증 토큰을 발급받는 명령을 실행합니다.
   #### **lab2-6-1**
        ```bash
        export API_TOKEN=$(curl -s -X POST -i https://iam.kakaocloud.com/identity/v3/auth/tokens -H "Content-Type: application/json" -d \
        '{
            "auth": {
                "identity": {
                    "methods": [
                        "application_credential"
                    ],
                    "application_credential": {
                        "id": "{엑세스 키 ID}",
                        "secret": "{보안 엑세스 키}"
                    }
                }
            }
        }' | grep x-subject-token | awk -v RS='\r\n' '{print $2}')
        ```
        
2. API 인증 토큰을 환경변수로 등록합니다.
   #### **lab2-6-2**
   ```bash
   echo "export API_TOKEN=${API_TOKEN}" >> ~/.bashrc
   ```
   
   #### **lab2-6-3**
   
      - 발급받은 API 인증 토큰을 확인합니다.
   
   ```bash
   echo $API_TOKEN
   ```
        
4. 임시 자격 증명 발급 (STS AssumeRoleWithWebIdentity)
    - 발급받은 API 토큰을 사용하여 임시 자격 증명을 요청합니다
    - S3 API 사용을 위한 크리덴셜 발급을 위해서는 `사용자 고유 ID`, `프로젝트 ID`가 필요합니다.
        - [콘솔] > [계정 정보]에서 `사용자 고유 ID`를 확인합니다.
        - **카카오클라우드 콘솔 메인 화면** 상단의 **작업 중인 프로젝트**에서 `프로젝트 ID`를 확인합니다.
        #### **lab2-6-4**
        ```bash
        echo $(curl -s -X POST -i https://iam.kakaocloud.com/identity/v3/users/{사용자 고유 ID}/credentials/OS-EC2 \
         -H "Content-Type: application/json" \
         -H "X-Auth-Token: ${API_TOKEN}" -d \
         '{
             "tenant_id": "{프로젝트 ID}"
         }')
        ```
        
        - 입력 예시
            
            ```bash
            echo $(curl -s -X POST -i https://iam.kakaocloud.com/identity/v3/users/0c097b8ae8e74de2a49c3b5f33fdb9cf/credentials/OS-EC2 \
             -H "Content-Type: application/json" \
             -H "X-Auth-Token: ${API_TOKEN}" -d \
             '{
                 "tenant_id": "0aa67b93c3ec48e587a51c9f842ca407"
             }')
            ```
            
        - 출력 예시
            
            ```bash
            ubuntu@host-172-16-2-233:/confluent-hub$ echo $(curl -s -X POST -i https://iam.kakaocloud.com/identity/v3/users/0c097b8ae8e74de2a49c3b5f33fdb9cf/credentials/OS-EC2 \
             -H "Content-Type: application/json" \
             -H "X-Auth-Token: ${API_TOKEN}" -d \
             '{
                 "tenant_id": "0aa67b93c3ec48e587a51c9f842ca407"
             }')
             {"credential": {"user_id": "0c097b8ae8e74de2a49c3b5f33fdb9cf", "tenant_id": "0aa67b93c3ec48e587a51c9f842ca407", "access": "2fc5f24fd45c4e5c905fb7d0bdac61ee", "secret": "f9cf53fa34a144268b803eaad9fdf502", "trust_id": null, "links": {"self": "http://iam.kakaocloud.com/v3/users/0c097b8ae8e74de2a49c3b5f33fdb9cf/credentials/OS-EC2/2fc5f24fd45c4e5c905fb7d0bdac61ee"}}}
            ```
            
    - **Response Elements**
        
        
        | 결과 키 | 환경 변수 |
        | --- | --- |
        | “access” | S3_ACCESS_KEY |
        | “secret” | S3_SECRET_ACCESS_KEY |
    
    ### (https://docs.kakaocloud.com/service/bss/object-storage/api/bss-api-os-s3#response-elements)
    
5. ~/.bashrc에 자격 증명 추가
    #### **lab2-6-5**
   
       - `.bashrc` 파일을 열어 AWS 자격 증명을 추가
   
   ```bash
   vi ~/.bashrc
   ```
   
   #### **lab2-6-6**
   
       - S3_ACCESS_KEY 입력
   
   ```bash
   export AWS_ACCESS_KEY_ID="{S3_ACCESS_KEY}"
   export AWS_SECRET_ACCESS_KEY="{S3_SECRET_ACCESS_KEY}"
   ```
   
   - 입력 예시
   
   ```bash
   export AWS_ACCESS_KEY_ID="95c6ad9b8eda493cbf536f203da0893f"
   export AWS_SECRET_ACCESS_KEY="fee9a69d46444b2c925d873358e2e023"
   ```

   #### **lab2-6-7**
   
       - 파일을 저장하고 적용
   
   ```bash
   source ~/.bashrc
   ```


## 3. S3 Sink Connector 설치

1. 권한 변경
   #### **lab2-7-1**
   ```bash
   sudo chown ubuntu:ubuntu /confluent-hub/plugins
   ```

2. Confluent Hub로 S3 Sink Connector 설치
   #### **lab2-7-2**
   ```bash
   confluent-hub install confluentinc/kafka-connect-s3:latest --component-dir /confluent-hub/plugins --worker-configs /home/ubuntu/kafka/config/connect-standalone.properties
   ```

3. AWS CLI 설치 및 설정 (Kakao Cloud Object Storage S3 API 연동용)
   #### **lab2-8-1**
   
      - AWS CLI 2.22.0 다운로드
   
   ```bash
   cd /home/ubuntu
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.22.0.zip" -o "awscliv2.zip"
   ```
   
   #### **lab2-8-2**
   
      - 압축 해제
   
   ```bash
   unzip /home/ubuntu/awscliv2.zip
   ```

   #### **lab2-8-3**
   
      - AWS CLI 설치
   
   ```bash
   sudo /home/ubuntu/aws/install
   ```
   
   #### **lab2-8-4**
   
      - AWS CLI 버전 확인
  
   ```bash
   aws --version
   ```


## 4. AWS CLI 구성
1. `AWS_ACCESS_KEY_ID`와 `AWS_SECRET_ACCESS_KEY`를 `aws configure`에 입력
   #### **lab2-9-1**
   ```bash
   aws configure
   ```

   - AWS Access Key ID: 위에서 추가한 `AWS_ACCESS_KEY_ID`
   - AWS Secret Access Key: 위에서 추가한 `AWS_SECRET_ACCESS_KEY`
   - Default region name: `kr-central-2`
   - Default output format: (생략-입력 없이 Enter)

2. Bucket ACL 설정
   #### **lab2-9-2**
   
      - 쓰기 권한 부여
      - 버킷 이름 실제 생성 이름으로 수정

   ```bash
   aws s3api put-bucket-acl \
     --bucket {버킷 이름} \
     --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
     --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
   ```

      - 입력 예시
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket kafka-nginx-log \
      --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```
    

## 5. Standalone 모드와 Systemd를 이용한 커넥터 생성

1. 연결 폴더 생성
   #### **lab2-10-1**
   ```bash
   sudo mkdir -p /opt/kafka/config
   sudo chown ubuntu:ubuntu /opt/kafka
   sudo chown ubuntu:ubuntu /opt/kafka/config
   ```

2. S3 Sink Connector 전용 설정 파일 생성
   #### **lab2-10-2**
   ```bash
   vi /opt/kafka/config/s3-sink-connector.properties
   ```

- `/opt/kafka/config/s3-sink-connector.properties`
    #### **lab2-10-3**
  
        - {버킷 이름}, {S3_ACCESS_KEY}, {S3_SECRET_ACCESS_KEY} 사용자 사용 값으로 수정
  
    ```bash
    # 커넥터 이름
    name=s3-sink-connector
    
    # S3 Sink Connector 클래스
    connector.class=io.confluent.connect.s3.S3SinkConnector
    
    # 태스크 수
    tasks.max=1
    
    # 연결할 토픽 (쉼표로 여러 개 지정 가능)
    topics=nginx-topic
    
    # Object Storage/S3 관련 설정
    s3.region=kr-central-2
    s3.bucket.name={버킷 이름}
    s3.part.size=5242880
    
    aws.access.key.id={S3_ACCESS_KEY}
    aws.secret.access.key={S3_SECRET_ACCESS_KEY}
    store.url=https://objectstorage.kr-central-2.kakaocloud.com
    
    # Key/Value Converter 설정
    key.converter=org.apache.kafka.connect.json.JsonConverter
    value.converter=org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable=false
    value.converter.schemas.enable=false
    
    # 스토리지 및 포맷 설정
    storage.class=io.confluent.connect.s3.storage.S3Storage
    format.class=io.confluent.connect.s3.format.json.JsonFormat
    
    # flush.size: 지정한 메시지 수만큼 누적 시 S3에 업로드
    flush.size=1
    ```
    
      - 입력 예시
    
    ```bash
    # 커넥터 이름
    name=s3-sink-connector
    
    # S3 Sink Connector 클래스
    connector.class=io.confluent.connect.s3.S3SinkConnector
    
    # 태스크 수
    tasks.max=1
    
    # 연결할 토픽 (쉼표로 여러 개 지정 가능)
    topics=nginx-topic
    
    # Object Storage/S3 관련 설정
    s3.region=kr-central-2
    s3.bucket.name=kaf-obj
    s3.part.size=5242880
    
    aws.access.key.id=95c6ad9b8eda493cbf536f203da0893f
    aws.secret.access.key=fee9a69d46444b2c925d873358e2e023
    store.url=https://objectstorage.kr-central-2.kakaocloud.com
    
    # Key/Value Converter 설정
    key.converter=org.apache.kafka.connect.json.JsonConverter
    value.converter=org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable=false
    value.converter.schemas.enable=false
    
    # 스토리지 및 포맷 설정
    storage.class=io.confluent.connect.s3.storage.S3Storage
    format.class=io.confluent.connect.s3.format.json.JsonFormat
    
    # flush.size: 지정한 메시지 수만큼 누적 시 S3에 업로드
    flush.size=1
    ```
    

## 6. Standalone Worker 설정 파일 생성
   #### **lab2-11-1**
   ```bash
   vi /opt/kafka/config/worker.properties
   ```

- `/opt/kafka/config/worker.properties`
    #### **lab2-11-2**
  
        - {카프카 부트스트랩 서버} 사용자 사용 값으로 수정
  
    ```bash
    # 워커 기본 설정
    
    bootstrap.servers={카프카 부트스트랩 서버}
    key.converter=org.apache.kafka.connect.json.JsonConverter
    value.converter=org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable=false
    value.converter.schemas.enable=false
    
    # Offset 저장 관련 설정 (standalone 모드 필수)
    offset.storage.file.filename=/tmp/connect.offsets
    offset.flush.interval.ms=10000
    
    # 플러그인 경로 (S3 Sink Connector가 설치된 경로)
    plugin.path=/confluent-hub/plugins
    
    # REST 인터페이스 리스너 (커넥터 상태 확인용)
    listeners=http://0.0.0.0:8083
    ```
    
      - 입력 예시
    
    ```bash
    # 워커 기본 설정
    
    bootstrap.servers=172.16.0.194:9092,172.16.2.91:9092
    key.converter=org.apache.kafka.connect.json.JsonConverter
    value.converter=org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable=false
    value.converter.schemas.enable=false
    
    # Offset 저장 관련 설정 (standalone 모드 필수)
    offset.storage.file.filename=/tmp/connect.offsets
    offset.flush.interval.ms=10000
    
    # 플러그인 경로 (S3 Sink Connector가 설치된 경로)
    plugin.path=/confluent-hub/plugins
    
    # REST 인터페이스 리스너 (커넥터 상태 확인용)
    listeners=http://0.0.0.0:8083
    ```

    
## 7. Systemd 서비스 파일 생성
1. 시스템 서비스로 등록(상시 유지)
   #### **lab2-12-1**
   
      - 항상 실행되도록 `systemd`에 등록한다.

   ```bash
   sudo vi /etc/systemd/system/kafka-connect.service
   ```

    #### **lab2-12-2**

      - `/etc/systemd/system/kafka-connect.service` 파일 작성
   
    ```bash
    [Unit]
    Description=Kafka Connect Standalone Service
    After=network.target
    
    [Service]
    User=ubuntu
    ExecStart=/home/ubuntu/kafka/bin/connect-standalone.sh /opt/kafka/config/worker.properties /opt/kafka/config/s3-sink-connector.properties
    Restart=on-failure
    RestartSec=5
    
    [Install]
    WantedBy=multi-user.target
    ```

   #### **lab2-12-3**
   
      - kafka-connect 재실행
   
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable kafka-connect
   sudo systemctl start kafka-connect
   sudo systemctl status kafka-connect
   ```
   
      - 상태(Status)가 `active (running)`이면 실행 중


## 8. 데이터가 정상적으로 S3(Kakao Object Storage)에 쌓이는지 확인
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage
2. 카프카 용으로 생성한 `kafka-nginx-log' 클릭
3. 실제 로그가 쌓이는지 확인

---
