### **Kafka 기반 데이터 스트리밍 및 Object Storage 연동**

Kafka를 활용하여 메시지를 송수신하고, Nginx 로그를 실시간으로 수집 및 처리하는 과정을 다룹니다. 또한, Kafka Connect와 S3 Sink Connector를 활용하여 수집된 데이터를 Object Storage에 저장하는 방법을 실습합니다.

---

        

1. **홈 디렉토리로 이동**
    ```bash
    cd
    ```

### **각 VM에 Kafka 클라이언트(바이너리) 설치**

1. **Java 설치**
    
    ```bash
    sudo apt update
    sudo apt install -y openjdk-21-jdk
    java -version
    ```
    
2. **Kafka 바이너리 다운로드 및 설치**
    
    ```bash
    cd /opt
    sudo wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
    sudo tar -xzf kafka_2.13-3.7.1.tgz
    sudo mv kafka_2.13-3.7.1 kafka
    sudo rm kafka_2.13-3.7.1.tgz
    ```
    
3. **환경 변수 설정**
    
    ```bash
    echo 'export KAFKA_HOME=/opt/kafka' >> ~/.bashrc
    echo 'export PATH=$PATH:$KAFKA_HOME/bin' >> ~/.bashrc
    echo export KAFKA_BOOTSTRAP_SERVERS="{카프카 부트스트랩 서버}" >> ~/.bashrc
    source ~/.bashrc
    ```
    

### **1.4 Python 환경 준비**

1. **Python, Kafka-Python 설치**
    
    ```bash
    sudo apt update
    sudo apt install -y python3 python3-pip
    python3 --version
    pip3 --version
    sudo pip3 install kafka-python
    ```
    

    

### **1.5 Kafka 클러스터와 통신 확인**

1. **네트워크 통신 가능 여부 체크(각 클러스터의 부트스트랩 서버)**
    
    ```bash
    nc -zv {각 클러스터의 부트스트랩 서버}
    nc -zv {각 클러스터의 부트스트랩 서버}
    ```

    ```
    예시
    nc -zv 0.0.0.0 9092
    nc -zv 0.0.0.0 9092
    ```
    
    - 실패 시 네트워크 및 보안 그룹 설정을 확인합니다.
---

# 콘솔 스크립트(바이너리)로 메시지 프로듀싱/컨슈밍 실습
카프카 디렉토리로 이동 (TG1, 2)
```
cd kafka
```

토픽 생성 (TG1)
```
bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --create --topic consol-topic --partitions 2 --replication-factor 2
```

프로듀서 실행(TG1)
```
bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
```

컨슈머 실행(TG2)

earliest 설정
```
bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic --group consumer-group-earliest --from-beginning
```

latest 설정
```
bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic --group consumer-group-latest
```

# python 코드로 메시지 프로듀싱/컨슈밍 실습
python 토픽 생성(TG1)
```
bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --create --topic python-topic --partitions 2 --replication-factor 2
```

producer.py실행(TG1)
```
sudo wget -O producer.py "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/Kafka_Connect_VM/producer.py"
sudo chmod +x producer.py
sudo -E ./producer.py
```

consumer.py실행(TG2)
```
sudo wget -O consumer.py "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/Kafka_Connect_VM/consumer.py"
sudo chmod +x consumer.py
sudo -E ./consumer.py
```

---
# nginx 로그 → kafka로 프로듀싱 실습 (logstash 활용)
콘솔 스크립트(바이너리)로 새로운 토픽 생성(TG1)
```
bin/kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --create --topic nginx-topic --partitions 2 --replication-factor 2
```

api서버에서 logstash 설정(API VM1, 2)
```
cd /etc/logstash/
sudo vi logstash.yml
```

보이는 파일
```
path.data: /var/lib/logstash
path.logs: /var/log/logstash
path.config: /etc/logstash/conf.d/logs-to-pubsub.conf
```

path.config 수정 필요 logs-to-pubsub.conf -> logs-to-kafka.conf
```bash
i 클릭 후 방향키로 이동하여logs-to-pubsub.conf로 이동
logs-to-pubsub.conf에서 pubsub 삭제 후 kafka 입력
esc 클릭 후 :wq 입력
```


Logstash 재실행 및 상태 확인 (API VM1, 2)
```
sudo systemctl restart logstash
sudo systemctl status logstash
```

TG에서 데이터 받기 (TG1)
```
bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --topic nginx-topic --from-beginning
```


데이터가 쌓이고 있는지 체크(시간 좀 걸림)

---
# kafka → kafka connector → object storage 실습

## kafka connector 역할을 할 새로운 VM 카카오클라우드 콘솔에서 생성

Kafka Connector VM 생성
이름: `kafka-connector`

이미지: `Ubuntu 22.04`

인스턴스유형: `m2a.xlarge`

볼륨: `30GB`

VPC: `실습 환경`

보안 그룹(SG) 생성

`22`, `80`, `9092`

고급 스크립트 부분에 아래 코드 입력하여 생성

```
#!/bin/bash

# apt 패키지 목록 업데이트
sudo apt update

# 필요한 패키지 설치
sudo apt install -y python3 python3-pip openjdk-21-jdk unzip jq
```

## 1. 새로운 Kafka Connector VM에서 사전 준비

### 1-1. 새로 생성한 Kafka Connector VM에 Public IP 부여 후 SSH 연결
```bash
ssh -i {keypair}.pem ubuntu@{vm public ip}
```

### 1-2. Kafka 다운로드 및 압축 해제

```bash
cd /home/ubuntu
curl https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz -o kafka_2.13-3.7.1.tgz
tar -xzf /home/ubuntu/kafka_2.13-3.7.1.tgz
rm /home/ubuntu/kafka_2.13-3.7.1.tgz
mv /home/ubuntu/kafka_2.13-3.7.1 /home/ubuntu/kafka
```

### 1-3. Confluent Hub Client 설치

```bash
cd /
sudo mkdir -p /confluent-hub/plugins && \
cd /confluent-hub && \
sudo curl -LO http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz && \
sudo tar -zxvf confluent-hub-client-latest.tar.gz
```

### 1-4. 환경 변수 설정

```bash
vi /home/ubuntu/.bashrc
```

아래 내용을 `.bashrc` 맨 아래에 추가

```bash
# Confluent 설정
export CONFLUENT_HOME='/confluent-hub'
export PATH="$PATH:$CONFLUENT_HOME/bin"

# Java 설정
export JAVA_HOME='/usr/lib/jvm/java-21-openjdk-amd64'
export PATH="$JAVA_HOME/bin:$PATH"
```

저장 후,

```bash
source /home/ubuntu/.bashrc
```

---

### **2. Object Storage 버킷의 CORS 정책으로 쓰기 접근 권한 허용**

1. **API 인증 토큰 발급**
    - 사용자 로컬 머신의 터미널에 접속합니다. 아래 명령에서 `ACCESS_KEY`와 `ACCESS_SECRET_KEY`를 각각 '액세스 키'와 '보안 액세스 키' 값으로 수정합니다.
    - 그 다음 아래 API 인증 토큰을 발급받는 명령을 실행합니다.
        
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
        
    - API 인증 토큰을 환경변수로 등록합니다.
        
        ```bash
        echo "export API_TOKEN=${API_TOKEN}" >> ~/.bashrc
        ```
        
    - 발급받은 API 인증 토큰을 확인합니다.
        
        ```bash
        echo $API_TOKEN
        ```
        
2. **임시 자격 증명 발급 (STS AssumeRoleWithWebIdentity)**
    - 발급받은 API 토큰을 사용하여 임시 자격 증명을 요청합니다
    - S3 API 사용을 위한 크리덴셜 발급을 위해서는 `사용자 고유 ID`, `프로젝트 ID`가 필요합니다.
        - [콘솔] > [계정 정보]에서 `사용자 고유 ID`를 확인합니다.
        - **카카오클라우드 콘솔 메인 화면** 상단의 **작업 중인 프로젝트**에서 `프로젝트 ID`를 확인합니다.
        
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
    
    ### [****](https://docs.kakaocloud.com/service/bss/object-storage/api/bss-api-os-s3#response-elements)
    
3. **.bashrc에 자격 증명 추가**
    - `.bashrc` 파일을 열어 AWS 자격 증명을 추가합니다.
        
        ```bash
        vi ~/.bashrc
        ```
        
    - 다음 내용을 추가합니다 .
        
        ```bash
        export AWS_ACCESS_KEY_ID="{S3_ACCESS_KEY}"
        export AWS_SECRET_ACCESS_KEY="{S3_SECRET_ACCESS_KEY}"
        ```
        
        - 입력 예시
            
            ```bash
            export AWS_ACCESS_KEY_ID="95c6ad9b8eda493cbf536f203da0893f"
            export AWS_SECRET_ACCESS_KEY="fee9a69d46444b2c925d873358e2e023"
            ```
            
    - 파일을 저장하고 적용합니다.
        
        ```bash
        source ~/.bashrc
        ```
        

---

## 2. S3 Sink Connector 설치

### 2-1. 권한 변경

```bash
sudo chown ubuntu:ubuntu /confluent-hub/plugins
```

### 2-2. Confluent Hub로 S3 Sink Connector 설치

```bash
confluent-hub install confluentinc/kafka-connect-s3:latest --component-dir /confluent-hub/plugins --worker-configs /home/ubuntu/kafka/config/connect-standalone.properties
```

- `-component-dir`: 플러그인이 설치될 위치를 지정
- `-worker-configs`: 현재 사용 중인 커넥트 설정 파일 위치를 지정(단, 기본 파일이 없으면 무시될 수도 있음)

설치 후 `/confluent-hub/plugins` 내부에 S3 Sink Connector 관련 폴더가 생성된다.

---

## 3. AWS CLI 설치 및 설정 (Kakao Cloud Object Storage S3 API 연동용)

### 3-1. AWS CLI 2.22.0 다운로드

```bash
cd /home/ubuntu
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.22.0.zip" -o "awscliv2.zip"
```

### 3-2. 압축 해제

```bash
unzip /home/ubuntu/awscliv2.zip
```

### 3-3. AWS CLI 설치

```bash
sudo /home/ubuntu/aws/install
```

### 3-4. AWS CLI 버전 확인

```bash
aws --version
```

### 3-5. AWS CLI 구성

이미 `.bashrc`에 `AWS_ACCESS_KEY_ID`와 `AWS_SECRET_ACCESS_KEY`가 설정되어 있다면, `aws configure` 시 자동으로 입력 가능하다. 아니면 수동 입력 가능

```bash
aws configure
```

- AWS Access Key ID: 위에서 추가한 `AWS_ACCESS_KEY_ID`
- AWS Secret Access Key: 위에서 추가한 `AWS_SECRET_ACCESS_KEY`
- Default region name: `kr-central-2`
- Default output format: (생략)

### 3-6. Bucket ACL(쓰기 권한 부여)

Kakao Cloud Object Storage 특성상 CORS 및 ACL 설정이 필요하다.

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
    

*버킷이름*을 실제 생성한 버킷으로 교체 후 실행

---

## 4. Standalone 모드와 Systemd를 이용한 커넥터 생성

### 4-1. 연결 폴더 생성

```bash
sudo mkdir -p /opt/kafka/config
sudo chown ubuntu:ubuntu /opt/kafka
sudo chown ubuntu:ubuntu /opt/kafka/config
```

### 4-2. S3 Sink Connector 전용 설정 파일 생성

```bash
vi /opt/kafka/config/s3-sink-connector.properties
```

- `/opt/kafka/config/s3-sink-connector.properties`
    
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
    

### 4-3. Standalone Worker 설정 파일 생성

`/opt/kafka/config/worker.properties` 파일은 Kafka Connect 워커의 기본 설정을 포함한다.

```bash
vi /opt/kafka/config/worker.properties
```

- `/opt/kafka/config/worker.properties`
    
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
    

---

## 5. Systemd 서비스 파일 생성

- Kafka Connect를 systemd 서비스로 관리하기 위해 `/etc/systemd/system/kafka-connect.service` 파일을 생성한다

### 5-1. 시스템 서비스로 등록(상시 유지)

항상 실행되도록 `systemd`에 등록한다.

```bash
sudo vi /etc/systemd/system/kafka-connect.service
```

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
    

```bash
sudo systemctl daemon-reload
sudo systemctl enable kafka-connect
sudo systemctl start kafka-connect
sudo systemctl status kafka-connect
```

상태(Status)가 `active (running)`이면 실행 중임을 의미한다.

---

## 6. 데이터가 정상적으로 S3(Kakao Object Storage)에 쌓이는지 확인

1. Kakao Cloud 콘솔에 접속 → Object Storage → 버킷 이름 클릭 → 파일(오브젝트) 생성 여부 확인

<aside>
  
**디렉터리 구조 생성 원리(**topics/nginx-logs/partition=0/**)**

- **topics**: 커넥터는 별도로 저장 경로(prefix)를 지정하지 않으면 기본적으로 “topics” 폴더 아래에 각 토픽 이름을 가진 디렉터리를 생성한다
- **nginx-logs:** 생성한 토픽 이름이 `nginx-logs`이면 버킷 내에 `topics/nginx-logs` 폴더가 만들어진다.
- **partition=0:** 토픽 생성 시 `--partitions 1` 옵션을 사용하면 하나의 파티션이 생성되는데, 이 파티션의 번호는 0이다. 따라서 S3 Sink Connector는 토픽 `nginx-logs`의 유일한 파티션인 0번에 해당하는 데이터를 저장할 때, 디렉터리 이름을 `partition=0`으로 생성하게 된다.

**파일 이름 생성 규칙**

- 생성되는 파일 이름은 기본적으로 `[토픽명]+[파티션번호]+[시작 오프셋].json` 형식이다.
- 예를 들어, `nginx-logs+0+0000000000.json` 파일은 토픽 `nginx-logs`, 파티션 0의 오프셋 0부터 시작된 데이터 파일임을 나타낸다
- 이 규칙은 내부 라이브러리(예, `io.confluent.connect.s3.format.json.JsonFormat`)에서 정의되어 있으며, flush.size 등의 설정 값에 따라 파일이 롤오버된다
</aside>
