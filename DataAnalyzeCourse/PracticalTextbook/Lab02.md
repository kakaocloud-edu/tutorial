# Kafka 기반 데이터 스트리밍 및 Object Storage 연동

Kafka로 메시지를 송수신하고, Nginx 로그를 실시간으로 수집·처리하는 과정을 다룹니다. 또한, Kafka Connect와 S3 Sink Connector를 이용해 수집된 데이터를 Object Storage에 저장하는 방법을 실습합니다.

---

## 1. Kafka 기본 환경 설정
- **Note**: `trarffic-generator-1, 2`에서 설치 진행
- **Note**: 설치 중간에 보라색 화면이 뜨면 'Enter`로 진행

1. Java 설치
    
    #### lab2-1-1-1
    
    ```bash
    cd
    ```
    
    #### lab2-1-1-2
    
    ```bash
    sudo apt update
    sudo apt install -y openjdk-21-jdk
    java -version
    ```
    
3. Kafka 바이너리 다운로드 및 설치
    - /opt 디렉터리로 이동 후 압축 풀어서 kafka 폴더 구성
    
        #### lab2-1-2
        
        ```bash
        cd /opt && sudo wget -qO- https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz | sudo tar -xz && sudo mv kafka_2.13-3.7.1 kafka
        ```
        - **Note**: 정지한 상태로 보일 수 있으나 명령어 실행 중이므로 약 10분정도 대기 필요
    
4. ~/.bashrc에 환경 변수 및 부트스트랩 서버 주소를 설정하여 Kafka 실행에 필요한 경로와 정보 등록
    
    #### lab2-1-3-1
   - **Note**: `{Kafka 부트스트랩 서버}`: `kafka` 클러스터의 부트스트랩 서버 입력
    
    ```bash
    cat << 'EOF' >> ~/.bashrc
    export KAFKA_HOME=/opt/kafka
    export PATH=$PATH:$KAFKA_HOME/bin
    export KAFKA_BOOTSTRAP_SERVERS="{Kafka 부트스트랩 서버}"
    EOF
    ```
    

   #### lab2-1-3-2
    
    ```bash
    source ~/.bashrc
    ```
    
6. kafka-python 라이브러리 설치
    
    #### lab2-1-4
    
    ```bash
    sudo apt update
    sudo pip3 install kafka-python
    ```
    
7. Kafka 클러스터와 통신 확인
    
    #### lab2-1-5
    - **Note**: 콤마(,) 기준으로 kafka 클러스터의 부트스트랩 서버 주소 하나씩 입력
    - **Note**: 실패 시 네트워크 및 보안 그룹 설정 확인
    
    ```bash
    nc -zv {Kafka 클러스터의 부트스트랩 서버}
    ```
    - 예시
      ```
      nc -zv 10.0.0.27 9092
      ```
   - 아래와 같은 정상적인 화면 확인 후 진행
   - ![image](https://github.com/user-attachments/assets/e769ee52-5a32-49f6-8124-f20c9ed60227)

    

# 2. Kafka 메시지 송수신 확인 (지만 - 수정 예정)

1. 콘솔 스크립트로 메시지 송수신
    1) `traffic-generator-1`에서 `/opt/kafka` 디렉터리로 이동
    
        #### lab2-2-1-1
        
        ```bash
        cd /opt/kafka
        ```
    
    2) 새 토픽(`consol-topic`) 생성
    
        #### lab2-2-1-2
        
        ```bash
        bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
        --create --topic consol-topic --partitions 2 --replication-factor 2
        ```
    
    3) 콘솔 프로듀서 실행(1) 후 송신할 메세지 입력 후 `Enter` 키 입력
    
        #### lab2-2-1-3

        - **Note**: 메세지가 입력될 때 마다 offset에 쌓임
        - **Note**: `offset 0` 부터 시작
        
        ```bash
        bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
        ```

        - 메시지 입력
          ```
          test1
          test2
          test3
          ```
    - `traffic-generator-1`에서 `Ctrl` + `c` 키로 종료
    
    4) `traffic-generator-2`에서 Kafka 디렉터리로 이동
    
        #### lab2-2-1-4
        
        ```bash
        cd /opt/kafka
        ```
    
    5) Kafka 콘솔 컨슈머를 실행해 consumer-group-earliest 그룹으로 `consol-topic` 토픽의 메시지를 수신
    
        #### lab2-2-1-5
        
        ```bash
        bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
            --topic consol-topic --group consumer-group-earliest \
            --consumer-property auto.offset.reset=earliest \
            --property print.offset=true
        ```

    - `traffic-generator-2` 터미널 창에서 `traffic-generator-1`에서 입력했던 메세지와 offset 수신 확인
    - `traffic-generator-2`에서 `Ctrl` + `c` 키로 종료


    6) 콘솔 프로듀서 실행(2) 후 송신할 메세지 입력 후 `Enter` 키 입력
    
        #### lab2-2-1-6
        
        ```bash
        bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
        ```

        - 메시지 입력
          ```
          test4
          test5
          test6
          ```
    - `traffic-generator-1`에서 `Ctrl` + `c` 키로 종료

    7) Kafka 콘솔 컨슈머를 실행해 consumer-group-latest 그룹으로 `consol-topic` 토픽의 메시지를 수신
   
        #### lab2-2-1-7
        
        ```bash
        bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
            --topic consol-topic --group consumer-group-latest \
            --consumer-property auto.offset.reset=latest
            --property print.offset=true
        ```
    - **Note**: 이후 실행할 producer 메세지 받아야하므로 종료하면 안됨
    - auto.offset.reset의 latest 옵션은 consumer 실행 이후 producer로 들어오는 offset부터 읽기 때문에 이전에 실행된 producer의 메세지 'test1~6'은 출력 X

    8) 콘솔 프로듀서 실행(3) 후 송신할 메세지 입력 후 `Enter` 키 입력
    
        #### lab2-2-1-8
        
        ```bash
        bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
        ```

        - 메시지 입력
          ```
          test7
          test8
          test9
          ```
    - **Note**: test를 입력할 때마다 consumer latest에서 출력되는 것 확인
    - `traffic-generator-1`에서 `Ctrl` + `c` 키로 종료
 

    9) `traffic-generator-2`에서 컨슈머 그룹 목록 확인
    
        #### lab2-2-1-7
        
        ```bash
        bin/kafka-consumer-groups.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --list
        ```
    - `consumer-group-latest`, `consumer-group-earliest` 두 값이 뜨는거 확인


    

1. Python 코드로 메시지 송수신
    - `traffic-generator-1`에서 새 토픽(`python-topic`) 생성
    
        #### lab2-2-2-1
        
        ```bash
        bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
        --create --topic python-topic --partitions 2 --replication-factor 2
        ```
    
    - `traffic-generator-1`에서 Python 프로듀서 코드 실행
    
        #### lab2-2-2-2
        
        ```bash
        sudo wget -O producer.py \
        "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/producer.py"
        sudo chmod +x producer.py
        sudo -E ./producer.py
        ```

    - `python-topic`으로 메세지 전송 확인
    - `traffic-generator-2`에서 Python 컨슈머 코드 실행
    
        #### lab2-2-2-3
        
        ```bash
        sudo wget -O consumer.py \
        "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/consumer.py"
        sudo chmod +x consumer.py
        sudo -E ./consumer.py
        ```
        
    - `python-topic`으로 메세지 수신 확인 후 `Ctrl`+`c` 키를 입력하여 종료
    

# 3. Nginx 로그 수집 및 Kafka 전송

1. Nginx 로그 토픽 생성
    - `trarffic-generator-1`에서 nginx-topic 생성
    
        #### lab2-3-1
        
        ```bash
        bin/kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
        --create --topic nginx-topic --partitions 2 --replication-factor 2
        ```
    
2. Logstash 설정 파일 수정
    - `api-server-1, 2`에서 `/etc/logstash/logstash.yml` 열기
    - `path.config` 항목을 `logs-to-kafka.conf`로 변경 후 저장
    
        #### lab2-3-2
        
        ```bash
        sudo vi /etc/logstash/logstash.yml
        ```
    - **Note**: `i`(입력 모드) 누른 후 화면 하단에`--INSERT-- 확인` 후 수정
    - **Note**: `esc`(명령 모드) 누른 후 `:wq`로 저장

3. Logstash 재실행 및 상태 확인
    
    #### lab2-3-3
    
    ```bash
    sudo systemctl restart logstash
    sudo systemctl status logstash
    ```

    - `Active:active (running)` 확인
    
4. `trarffic-generator-2`에서 콘솔 컨슈머 실행
    
    #### lab2-3-4
    
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --topic nginx-topic --from-beginning
    ```
    
5. 웹 브라우저 주소창에 `http://{ALB의 Public IP}`를 입력하여 접속 후 링크 클릭 등을 통해 임의로 트래픽 생성
6. `trarffic-generator-2`의 터미널에서 NGINX 로그 확인
7. `Ctrl`+`c` 키를 입력하여 종료
    

# 4. Kafka Connector VM 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `kafka-connector`
        - 개수: `1`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.large`
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
                    - 프로토콜: TCP, 출발지: 0.0.0.0/0, 포트 번호: 22
                    - 프로토콜: TCP, 출발지: 0.0.0.0/0, 포트 번호: 9092
                - 아웃바운드 규칙
                    - 프로토콜: ALL, 출발지: 0.0.0.0/0, 포트 번호: ALL

    - 고급 설정
        - 아래 스크립트 입력
            
            #### **lab2-4-2**
            
            ```
            #!/bin/bash
            
            # apt 패키지 목록 업데이트
            sudo apt update
            
            # 필요한 패키지 설치
            sudo apt install -y python3 python3-pip openjdk-21-jdk unzip jq
            ```
        
        - CPU 멀티스레딩: `활성화`
        
3. 생성 버튼 클릭
4. `kafka-connector` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
5. 확인 버튼 클릭
6. `kafka-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab2-4-6-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab2-4-6-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab2-4-6-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{kafka-connector의 public ip주소}
    ```
    
    - {kafka-connector의 public ip주소}: 복사한 각 IP 주소 입력
    
    #### **lab2-4-6-4**
    
    ```bash
    yes
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
    
    #### **lab2-4-6-5**
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```
    

# 5. S3 Sink Connector 설치 및 연동

1. Kafka 다운로드 및 /home/ubuntu/kafka 경로에 배치
    
    #### lab2-5-1
    
    ```bash
    curl -o /home/ubuntu/kafka_2.13-3.7.1.tgz \
    https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz && \
    tar -xzf /home/ubuntu/kafka_2.13-3.7.1.tgz -C /home/ubuntu && \
    rm /home/ubuntu/kafka_2.13-3.7.1.tgz && \
    mv /home/ubuntu/kafka_2.13-3.7.1 /home/ubuntu/kafka
    ```
    
2. Confluent Hub Client 설치
    
    #### lab2-5-2
    
    ```bash
    cd /
    sudo mkdir -p /confluent-hub/plugins && \
    cd /confluent-hub && \
    sudo curl -LO http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz && \
    sudo tar -zxvf confluent-hub-client-latest.tar.gz
    ```
    
3. .bashrc에 Confluent, Java Home 등 환경 변수 등록
    
    #### lab2-5-3-1
   
    ```bash
    cat <<'EOF' >> /home/ubuntu/.bashrc
    # Confluent 설정
    export CONFLUENT_HOME='/confluent-hub'
    export PATH="$PATH:$CONFLUENT_HOME/bin"
    
    # Java 설정
    export JAVA_HOME='/usr/lib/jvm/java-21-openjdk-amd64'
    export PATH="$JAVA_HOME/bin:$PATH"
    EOF
    ```
    
    #### lab2-5-3-3
    
    ```bash
    source ~/.bashrc
    ```
    
5. API 인증 토큰 발급
    - **Note**: {액세스 키 ID}: 현재 프로젝트의 액세스 키 ID
    - **Note**: {보안 액세스 키}: 현재 프로젝트의 보안 액세스 키
    #### lab2-5-4
    
    ```bash
    export API_TOKEN=$(curl -s -X POST -i https://iam.kakaocloud.com/identity/v3/auth/tokens \
    -H "Content-Type: application/json" -d \
    '{
        "auth": {
            "identity": {
                "methods": [
                    "application_credential"
                ],
                "application_credential": {
                    "id": "{액세스 키 ID}",
                    "secret": "{보안 액세스 키}"
                }
            }
        }
    }' | grep x-subject-token | awk -v RS='\r\n' '{print $2}')
    ```

6. 발급받은 인증 토큰 환경 변수 등록
    
    #### lab2-5-5
    
    ```bash
    echo "export API_TOKEN=${API_TOKEN}" >> ~/.bashrc
    ```
    
7. 발급된 토큰 확인
    
    #### lab2-5-6
    
    ```bash
    echo $API_TOKEN
    ```
    
8. 임시 자격 증명 발급
    - **Note**: 사용자 고유 ID, 프로젝트 ID 확인 후 아래 명령어 실행
    - **Note**: 사용자 UUID는 콘솔 -> 우측 상단 프로필 -> 계정 정보 통해서 확인


    #### lab2-5-7
    
    ```bash
    echo $(curl -s -X POST -i https://iam.kakaocloud.com/identity/v3/users/{사용자 UUID}/credentials/OS-EC2 \
    -H "Content-Type: application/json" \
    -H "X-Auth-Token: ${API_TOKEN}" -d \
    '{
        "tenant_id": "{프로젝트 ID}"
    }')
    ```
    
9. 임시 자격 증명의 S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY 등록
    
    #### lab2-5-8-1   
    - **Note**: {S3_ACCESS_KEY}: lab2-5-7의 응답에서 확인한 `access` 값
    - **Note**: {S3_SECRET_ACCESS_KEY}: lab2-5-7의 응답에서 확인한 `secret` 값
    
    ```bash
    cat <<'EOF' >> ~/.bashrc
    export AWS_ACCESS_KEY_ID="{S3_ACCESS_KEY}"
    export AWS_SECRET_ACCESS_KEY="{S3_SECRET_ACCESS_KEY}"
    EOF
    ```
    
    #### lab2-5-8-3
    
    ```bash
    source ~/.bashrc
    ```
    
11. Confluent Hub Plugins 폴더 권한 변경
    
    #### lab2-5-9
    
    ```bash
    sudo chown ubuntu:ubuntu /confluent-hub/plugins
    ```
    
12. S3 Sink Connector 설치    
    #### lab2-5-10
    
    ```bash
    confluent-hub install confluentinc/kafka-connect-s3:latest \
    --component-dir /confluent-hub/plugins \
    --worker-configs /home/ubuntu/kafka/config/connect-standalone.properties \
    --no-prompt
    ```
    
13. AWS CLI 설치
    - Object Storage S3 API 연동 위해 AWS CLI 2.22.0 다운로드 및 설치
    
    #### lab2-5-11-1
    
    ```bash
    cd /home/ubuntu && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.22.0.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    sudo ./aws/install
    ```
    
    - AWS CLI 버전 확인
    
    #### lab2-5-11-2
    
    ```bash
    aws --version
    ```
    
14. AWS CLI 환경 설정
    
    #### lab2-5-12
    
    ```bash
    aws configure
    ```
    
    - AWS Access Key ID: lab2-5-7의 응답에서 확인한 `access` 값
    - AWS Secret Access Key: lab2-5-7의 응답에서 확인한 `secret` 값
    - Default region name: `kr-central-2`
    - Default output format: (생략)
15. 버킷에 쓰기 권한 부여
    - **Note**: `{버킷 이름}`: 실제 생성한 버킷 이름(`data-catalog`)으로 변경

    #### lab2-5-13
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket {버킷 이름(data-catalog)} \
      --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```
    
# 6. Worker 구성 및 Object Storage 테스트

1. Kafka 설정 폴더 생성 및 권한 부여
    
    #### lab2-6-1
    
    ```bash
    sudo mkdir -p /opt/kafka/config && sudo chown -R ubuntu:ubuntu /opt/kafka
    ```

2. 커스텀 파티셔너, 파일네임 플러그인을 Kafka Connect가 사용하는 플러그인 디렉터리 /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib 에 다운로드

    #### lab2-6-2
    
    ```bash
    wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-partitioner-1.0-SNAPSHOT.jar "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/KafkaConnector/custom-partitioner-1.0-SNAPSHOT.jar" && \
    wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-filename-1.0-SNAPSHOT.jar "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/KafkaConnector/custom-filename-1.0-SNAPSHOT.jar"
    ```
    
3. S3 Sink Connector 설정 파일 생성
    - `/opt/kafka/config/s3-sink-connector.properties` 파일 생성
    
    #### lab2-6-3-1
    
    ```bash
    vi /opt/kafka/config/s3-sink-connector.properties
    ```
    - **Note**: `i`(입력 모드) 누른 후 화면 하단에`--INSERT-- 확인` 후 수정
    - **Note**: `esc`(명령 모드) 누른 후 `:wq`로 저장
    
    - 아래 내용 추가
      - **Note**: `{버킷 이름}`, `{S3_ACCESS_KEY}`, `{S3_SECRET_ACCESS_KEY}` 수정 후 붙여넣기
    #### lab2-6-3-2
    
    ```
    # 커넥터 이름
    name=s3-sink-connector
    
    # S3 Sink Connector 클래스
    connector.class=io.confluent.connect.s3.S3SinkConnector
    
    # 태스크 수
    tasks.max=1
    
    # 연결할 토픽
    topics=nginx-topic
    
    # Object Storage/S3 관련 설정
    s3.region=kr-central-2
    s3.bucket.name={버킷 이름(data-catalog)}
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
    
    # 커스텀 파티셔너 클래스 지정
    partitioner.class=com.mycompany.connect.FlexibleTimeBasedPartitioner
    
    # 커스텀 파일네임 클래스 지정
    format.class=com.mycompany.connect.CustomJsonFormat
    
    # 최상위 디렉터리명 변경
    topics.dir=kafka-nginx-log
    
    # 토픽 디렉터리를 기본 토픽 이름 대신 다른 이름으로 대체
    custom.topic.dir=nginx-topic
    
    # 파티션 디렉터리를 커스텀 접두어 생성
    custom.partition.prefix=partition_
    
    # Time-based 필수 설정
    # partition.duration.ms: 파티션 구간(밀리초). 예: 1시간 = 3600000ms
    partition.duration.ms=3600000
    # path.format: year=YYYY/month=MM/day=dd/hour=HH 등 원하는 년/월/일/시 형식
    path.format='year_'yyyy/'month_'MM/'day_'dd/'hour_'HH
    # locale, timezone, timestamp.extractor: TimeBasedPartitioner에서 요구하는 설정
    locale=en-US
    timezone=Asia/Seoul
    timestamp.extractor=Wallclock
    
    # 5) 예약어 치환 규칙 (예: "A:B,C:D" → 경로 문자열 내 "A"를 "B"로, "C"를 "D"로 치환)
    custom.replacements==:_
    ```
    
4. Standalone Worker 설정
    - `/opt/kafka/config/worker.properties` 파일 생성
    
    #### lab2-6-4-1
    
    ```bash
    vi /opt/kafka/config/worker.properties
    ```
    
    #### lab2-6-4-2
    
    ```bash
    # 워커 기본 설정
    bootstrap.servers={Kafka 부트스트랩 서버}
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
    
    - {Kafka 부트스트랩 서버}: Kafka 클러스터의 부트스트랩 서버 값으로 변경
5. kafka-connect 시스템 서비스 등록
    - `/etc/systemd/system/kafka-connect.service` 파일 생성
    
    #### lab2-6-5-1
    
    ```bash
    sudo vi /etc/systemd/system/kafka-connect.service
    ```
    
    - 아래 내용 입력
    
    #### lab2-6-5-2
    
    ```bash
    [Unit]
    Description=Kafka Connect Standalone Service
    After=network.target
    
    [Service]
    User=ubuntu
    ExecStart=/home/ubuntu/kafka/bin/connect-standalone.sh \
    /opt/kafka/config/worker.properties \
    /opt/kafka/config/s3-sink-connector.properties
    Restart=on-failure
    RestartSec=5
    
    [Install]
    WantedBy=multi-user.target
    ```
    
6. 데몬 리로드 및 서비스 시작
    
    #### lab2-6-6
    
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable kafka-connect
    sudo systemctl start kafka-connect
    ```

7. s3-sink-connector 상태 정보 조회
   
    #### lab2-6-6-2
    
    ```bash
    watch -n 1 "curl -s http://localhost:8083/connectors/s3-sink-connector/status | jq"
    ```

8. `connector`, `tasks`의 `state` 값이 `RUNNING`인 것을 확인

9. Object Storage 버킷 내 NGINX 로그 적재 확인
    - 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage
    - `data-catalog` 버킷 클릭
    - `/topics/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}/day_{현재 일}/hour_{현재 시}` 디렉터리로 이동
    - 버킷 내 적재된 NGINX 로그 적재 확인
