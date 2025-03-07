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
   - **Note**: 핑크색 화면이 뜨면 'Enter' 입력 후 설치 재개
    
    ```bash
    sudo apt update
    sudo apt install -y openjdk-21-jdk
    java -version
    ```
    
3. Kafka 바이너리 다운로드 및 설치
    - /opt 디렉터리로 이동 후 압축 풀어서 kafka 폴더 구성
    
    #### lab2-1-2
   - **Note**: 정지한 상태로 보일 수 있으나 명령어 실행 중이므로 약 5분정도 대기 필요
    ```bash
    cd /opt && sudo wget -qO- https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz | sudo tar -xz && sudo mv kafka_2.13-3.7.1 kafka
    ```

    
5. ~/.bashrc에 환경 변수 및 부트스트랩 서버 주소를 설정하여 Kafka 실행에 필요한 경로와 정보 등록
    
    #### lab2-1-3-1
   - **Note**: `{Kafka 부트스트랩 서버}`: `kafka` 클러스터의 부트스트랩 서버 입력
   - **Note**: `{Kafka 부트스트랩 서버}` 개인 환경에 맞게 수정 필수
    
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
    ```
    ```bash
    sudo pip3 install kafka-python
    ```
    
7. Kafka 클러스터와 통신 확인
    
    #### lab2-1-5
    - **Note**: `traffic-generator-1, 2`에서 진행
    - **Note**: 콤마(,) 기준으로 앞뒤의 kafka 클러스터의 부트스트랩 서버 주소 하나씩 입력
    - **Note**: 포트 번호 입력 시 콜론(:) 대신 공백(space) 넣은 후 진행
    
    ```bash
    nc -zv {Kafka 클러스터의 부트스트랩 서버}
    ```
    - 예시
      ```
      nc -zv 10.0.0.27 9092
      ```
   - 아래와 같은 정상적인 화면 확인 후 진행
   - ![image](https://github.com/user-attachments/assets/e769ee52-5a32-49f6-8124-f20c9ed60227)
   - **Note**: 실패 시 네트워크 및 보안 그룹 설정 확인
    

# 2. Kafka 메시지 송수신 확인

## 2-1. 콘솔 스크립트로 메시지 송수신(earlist 옵션)

1. `traffic-generator-1`에서 `/opt/kafka` 디렉터리로 이동
    
    #### lab2-2-1-1
        
    ```bash
    cd /opt/kafka
    ```
    
2. 새 토픽(`consol-topic`) 생성
    
    #### lab2-2-1-2
        
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic consol-topic --partitions 2 --replication-factor 2
    ```

    - **Note**: `kafka-topics.sh`란?
        - Kafka 클러스터에서 토픽을 생성, 삭제, 조회 등 토픽 관련 작업을 수행하기 위한 도구
        ```
        #!/bin/bash

        # Apache Software Foundation (ASF) 라이선스 관련 정보를 설명하는 주석입니다.
        # Licensed to the Apache Software Foundation (ASF) under one or more
        # contributor license agreements.  See the NOTICE file distributed with
        # this work for additional information regarding copyright ownership.
        # The ASF licenses this file to You under the Apache License, Version 2.0
        # (the "License"); you may not use this file except in compliance with
        # the License.  You may obtain a copy of the License at
        #
        #    http://www.apache.org/licenses/LICENSE-2.0
        #
        # Unless required by applicable law or agreed to in writing, software
        # distributed under the License is distributed on an "AS IS" BASIS,
        # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        # See the License for the specific language governing permissions and
        # limitations under the License.

        # 아래는 실행 부분으로 현재 스크립트와 같은 디렉터리에 있는 kafka-run-class.sh 스크립트를 호출합니다.
        # 실행 시 전달된 모든 인자("$@")를 그대로 넘겨주며, 자바 클래스 org.apache.kafka.tools.TopicCommand를 실행합니다.
        exec $(dirname $0)/kafka-run-class.sh org.apache.kafka.tools.TopicCommand "$@"
        ```
    
3. 콘솔 프로듀서 실행 후 송신할 메세지 입력 후 `Enter` 키 입력
    
    #### lab2-2-1-3

    - **Note**: 메세지가 입력될 때 마다 `offset`에 쌓임
    - **Note**: `offset 0` 부터 시작
        
    ```bash
    bin/kafka-console-producer.sh --broker-list ${KAFKA_BOOTSTRAP_SERVERS} --topic consol-topic
    ```

4. 메시지 입력
    - **Note**: 전송되는 시간이 필요하므로 전송 후 5초 정도 대기
    ```
    test1
    test2
    test3
    ```
    - 메시지 입력 후 'Enter' 입력
    
5. `traffic-generator-2`에서 Kafka 디렉터리로 이동
    
    #### lab2-2-1-5
        
    ```bash
    cd /opt/kafka
    ```
    
6. `traffic-generator-2`에서 Kafka 콘솔 컨슈머를 실행해 consumer-group-earliest 그룹으로 `consol-topic` 토픽의 메시지 수신
    
    #### lab2-2-1-6
        
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --topic consol-topic --group consumer-group-earliest \
    --consumer-property auto.offset.reset=earliest \
    --property print.offset=true
    ```

    - `traffic-generator-2` 터미널 창에서 `traffic-generator-1`에서 입력했던 메세지와 offset 수신 확인
    - `traffic-generator-2`에서 `Ctrl` + `c` 키로 종료
    
    - **Note**: `kafka-console-producer.sh`, `kafka-console-consumer.sh`란?
        - `kafka-console-producer.sh`: 콘솔을 통해 Kafka 토픽으로 메시지를 전송하는 역할 수행
            ```
            #!/bin/bash
    
            # Apache Software Foundation (ASF) 라이선스 관련 정보를 설명하는 주석입니다.
            # Licensed to the Apache Software Foundation (ASF) under one or more
            # contributor license agreements.  See the NOTICE file distributed with
            # this work for additional information regarding copyright ownership.
            # The ASF licenses this file to You under the Apache License, Version 2.0
            # (the "License"); you may not use this file except in compliance with
            # the License.  You may obtain a copy of the License at
            #
            #    http://www.apache.org/licenses/LICENSE-2.0
            #
            # Unless required by applicable law or agreed to in writing, software
            # distributed under the License is distributed on an "AS IS" BASIS,
            # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
            # See the License for the specific language governing permissions and
            # limitations under the License.
    
            # KAFKA_HEAP_OPTS 환경 변수가 아직 설정되지 않았다면,
            # JVM의 최대 힙 메모리를 512MB(-Xmx512M)로 지정합니다.
            if [ "x$KAFKA_HEAP_OPTS" = "x" ]; then
                export KAFKA_HEAP_OPTS="-Xmx512M"
            fi
    
            # kafka-run-class.sh를 호출해 kafka.tools.ConsoleProducer 클래스를 실행하며, 입력받은 인자들을 전달합니다.
            exec $(dirname $0)/kafka-run-class.sh kafka.tools.ConsoleProducer "$@"
            ```

        - `kafka-console-consumer.sh`: 콘솔에서 Kafka 토픽의 메시지를 실시간으로 수신하는 역할을 수행
            ```
            #!/bin/bash

            # Apache Software Foundation (ASF) 라이선스 관련 정보를 설명하는 주석입니다.
            # Licensed to the Apache Software Foundation (ASF) under one or more
            # contributor license agreements.  See the NOTICE file distributed with
            # this work for additional information regarding copyright ownership.
            # The ASF licenses this file to You under the Apache License, Version 2.0
            # (the "License"); you may not use this file except in compliance with
            # the License.  You may obtain a copy of the License at
            #
            #    http://www.apache.org/licenses/LICENSE-2.0
            #
            # Unless required by applicable law or agreed to in writing, software
            # distributed under the License is distributed on an "AS IS" BASIS,
            # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
            # See the License for the specific language governing permissions and
            # limitations under the License.

            # KAFKA_HEAP_OPTS 환경 변수가 설정되어 있지 않은 경우,
            # JVM의 최대 힙 메모리를 512MB(-Xmx512M)로 설정합니다.
            if [ "x$KAFKA_HEAP_OPTS" = "x" ]; then
                export KAFKA_HEAP_OPTS="-Xmx512M"
            fi

            # kafka-run-class.sh 스크립트를 호출해 kafka.tools.ConsoleConsumer 클래스를 실행하고, 전달된 인자를 넘깁니다.
            exec $(dirname $0)/kafka-run-class.sh kafka.tools.ConsoleConsumer "$@"
            ```
        

## 2-2. 콘솔 스크립트로 메시지 송수신(latest 옵션)
1. `traffic-generator-1`에서 콘솔 프로듀서 실행 후 송신할 메세지 입력 후 `Enter` 키 입력
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
   
        #### lab2-2-2-2
        ```bash
        bin/kafka-console-consumer.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
        --topic consol-topic --group consumer-group-latest \
        --consumer-property auto.offset.reset=latest \
        --property print.offset=true
        ```
    - `auto.offset.reset`의 `latest` 옵션은 `consumer` 실행 이후 `producer`로 들어오는 `offset`부터 읽기 때문에 이전에 실행된 `producer`의 메세지     'test4~6'은 출력이 안되는 것 확인

3. `traffic-generator-1`에서 콘솔 프로듀서 실행 후 송신할 메세지 입력 후 `Enter` 키 입력
    - **Note**: 전송되는 시간이 필요하므로 전송 후 5초 정도 대기
    ```
    test7
    test8
    test9
    ```
    - **Note**: test를 입력할 때마다 `consumer latest`에서 출력되는 것 확인
    - `traffic-generator-1`에서 `Ctrl` + `c` 키로 종료
    - `traffic-generator-2`에서 `Ctrl` + `c` 키로 종료
 

4. `traffic-generator-2`에서 컨슈머 그룹 목록 확인
    
    #### lab2-2-2-4
        
    ```bash
    bin/kafka-consumer-groups.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --list
    ```
    - `consumer-group-latest`, `consumer-group-earliest` 두 값이 뜨는거 확인


## 2-3. Python SDK로 메시지 송수신

1. `traffic-generator-1`에서 새 토픽(`python-topic`) 생성
    #### lab2-2-3-1
    
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic python-topic --partitions 2 --replication-factor 2
    ```
    
2. `traffic-generator-1`에서 Python 프로듀서 코드 실행
    #### lab2-2-3-2
    
    ```bash
    sudo wget -O producer.py \
    "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/producer.py"
    ```
    ```bash
    sudo chmod +x producer.py
    ```
    ```bash
    sudo -E ./producer.py
    ```

    - `python-topic`으로 메세지 전송 확인
3. `traffic-generator-2`에서 Python 컨슈머 코드 실행

    #### lab2-2-3-2
    
    ```bash
    sudo wget -O consumer.py \
    "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/consumer.py"
    ```
    ```bash
    sudo chmod +x consumer.py
    ```
    ```bash
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
    
2. `api-server-1` ssh연결
    - 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
    - `api-server-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    ### **lab2-3-2-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    ### **lab2-3-2-2**
    
    ```bash
    chmod 400 keypair.pem
    
    ```
    
    ### **lab2-3-2-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{api-server-1, 2의 public ip주소}
    
    ```
    
    - **Note**: {api-server-1, 2의 public ip 주소} 부분을 복사한 각 IP 주소로 교체하세요.
    
    ### **lab2-3-2-4**
    
    ```bash
    yes
    
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
    
    ### **lab2-3-2-5**
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    
    ```


3. `api-server-1`에서 Logstash 설정 파일을 수정하여 Kafka로 송신하도록 설정

    #### lab2-3-3
   
    ```
    sudo sed -i 's/logs-to-pubsub.conf/logs-to-kafka.conf/g' /etc/logstash/logstash.yml
    ```

4. Logstash 재실행 및 상태 확인
    
    #### lab2-3-4
    
    ```bash
    sudo systemctl restart logstash
    ```
    ```bash
    sudo systemctl status logstash
    ```

    - `Active:active (running)` 확인
    
5. `trarffic-generator-2`에서 콘솔 컨슈머 실행
    
    #### lab2-3-5
    
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --topic nginx-topic --from-beginning
    ```
    
6. 웹 브라우저 주소창에 `http://{ALB의 Public IP}`를 입력하여 접속 후 링크 클릭 등을 통해 임의로 트래픽 생성
7. `trarffic-generator-2`의 터미널에서 NGINX 로그 확인
8. `Ctrl`+`c` 키를 입력하여 종료
    

# 4. Kafka Connector VM 생성
- **Note**: `trarffic-generator-2`를 제외한 기존에 사용하던 터미널 창 모두 종료

1. 우측 상단 계정 프로필 > 자격 증명 > 비밀번호 확인
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
4. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
5. 인스턴스 생성 버튼 클릭
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
            - `{S3 액세스 키}`, `{S3 보안 액세스 키}`, `{Kafka 부트스트랩 서버}`, `{Kafka와 연동된 버킷 이름(data-catalog)}`를 개인 환경에 맞게 수정
                #### **lab2-4-5**
                
                ```
                #!/bin/bash
                
                ################################################################################
                # 0. 초기 설정
                ################################################################################
                
                # 원하는 Kakao i Cloud S3 Credentials
                AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
                AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
                AWS_DEFAULT_REGION_VALUE="kr-central-2"
                AWS_DEFAULT_OUTPUT_VALUE="json"
                
                # Kafka용 설정 변수
                KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
                BUCKET_NAME="{Kafka와 연동된 버킷 이름(data-catalog)}"
                
                LOGFILE="/home/ubuntu/setup.log"
                exec &> >(tee -a "$LOGFILE")  # 모든 echo 출력도 setup.log에 기록
                
                log() {
                  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
                }
                
                log "Start setup script"
                
                ################################################################################
                # 1. apt 업데이트 & 필수 패키지 설치
                ################################################################################
                log "Step 1: apt 패키지 목록 업데이트 시작"
                sudo apt-get update -y
                log "Step 1: apt 패키지 목록 업데이트 완료"
                
                log "Step 2: 필요한 패키지 설치 시작"
                sudo apt-get install -y python3 python3-pip openjdk-21-jdk unzip jq aria2 curl
                log "Step 2: 필요한 패키지 설치 완료"
                
                ################################################################################
                # 2. Kafka 다운로드 & 설치
                ################################################################################
                log "Step 3: Kafka 다운로드 및 설치 시작"
                
                aria2c -x 16 -s 16 -d /home/ubuntu -o kafka_2.13-3.7.1.tgz "https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz"
                tar -xzf /home/ubuntu/kafka_2.13-3.7.1.tgz -C /home/ubuntu
                rm /home/ubuntu/kafka_2.13-3.7.1.tgz
                mv /home/ubuntu/kafka_2.13-3.7.1 /home/ubuntu/kafka
                
                log "Step 3: Kafka 다운로드 및 설치 완료"
                
                ################################################################################
                # 3. Confluent Hub Client 설치
                ################################################################################
                log "Step 4: Confluent Hub Client 설치 시작"
                
                sudo mkdir -p /confluent-hub/plugins
                CONFLUENT_HUB_DIR="/confluent-hub"
                CONFLUENT_HUB_URL="http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz"
                CONFLUENT_HUB_FILE="confluent-hub-client-latest.tar.gz"
                
                sudo mkdir -p "$CONFLUENT_HUB_DIR"
                cd "$CONFLUENT_HUB_DIR"
                aria2c -x 16 -s 16 -o "$CONFLUENT_HUB_FILE" "$CONFLUENT_HUB_URL"
                sudo tar -zxf "$CONFLUENT_HUB_FILE"
                sudo chown -R ubuntu:ubuntu /confluent-hub
                
                log "Step 4: Confluent Hub Client 설치 완료"
                
                ################################################################################
                # 4. .bashrc 에 S3 Credentials + Confluent + Java 경로 설정
                ################################################################################
                log "Step 5: .bashrc에 환경 변수 등록"
                
                # 4-1) 기존 라인 제거 (중복 방지)
                sed -i '/S3_ACCESS_KEY=/d' /home/ubuntu/.bashrc
                sed -i '/S3_SECRET_ACCESS_KEY=/d' /home/ubuntu/.bashrc
                sed -i '/AWS_DEFAULT_REGION=/d' /home/ubuntu/.bashrc
                sed -i '/AWS_DEFAULT_OUTPUT=/d' /home/ubuntu/.bashrc
                sed -i '/CONFLUENT_HOME=/d' /home/ubuntu/.bashrc
                sed -i '/JAVA_HOME=/d' /home/ubuntu/.bashrc
                
                # 4-2) 실제 값 치환해서 추가
                cat <<EOF >> /home/ubuntu/.bashrc
                
                # Kakao i Cloud S3 Credentials
                export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID_VALUE"
                export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY_VALUE"
                export AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION_VALUE"
                export AWS_DEFAULT_OUTPUT="$AWS_DEFAULT_OUTPUT_VALUE"
                
                # Confluent 설정
                export CONFLUENT_HOME="/confluent-hub"
                export PATH="\$PATH:\$CONFLUENT_HOME/bin"
                
                # Java 설정
                export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
                export PATH="\$JAVA_HOME/bin:\$PATH"
                EOF
                
                log "Step 5: .bashrc 환경 변수 등록 완료"
                
                ################################################################################
                # 5. .bashrc 적용 → confluent-hub / AWS CLI 에서 쓸 수 있도록
                ################################################################################
                # 주의: cloud-init 등 비인터랙티브 실행 시 .bashrc가 자동 적용되지 않을 수 있으므로, 직접 source.
                source /home/ubuntu/.bashrc
                
                ################################################################################
                # 6. S3 Sink Connector 설치 (confluent-hub)
                ################################################################################
                log "Step 6: S3 Sink Connector 설치 시작"
                
                # (1) connect-standalone.properties 권한 변경
                sudo chown ubuntu:ubuntu /home/ubuntu/kafka/config/connect-standalone.properties 2>/dev/null
                
                # (2) S3 Sink Connector 설치
                /confluent-hub/bin/confluent-hub install confluentinc/kafka-connect-s3:latest \
                  --component-dir /confluent-hub/plugins \
                  --worker-configs /home/ubuntu/kafka/config/connect-standalone.properties \
                  --no-prompt
                
                log "Step 6: S3 Sink Connector 설치 완료"
                
                ################################################################################
                # 7. AWS CLI 설치
                ################################################################################
                log "Step 7: AWS CLI 설치 시작"
                
                cd /home/ubuntu
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.22.0.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install
                rm -rf aws awscliv2.zip
                
                AWS_VERSION=$(aws --version 2>&1 || true)
                log "AWS CLI 버전: $AWS_VERSION"
                log "Step 7: AWS CLI 설치 완료"
                
                ################################################################################
                # 8. AWS CLI configure 설정 (파일)
                ################################################################################
                log "Step 8: AWS CLI configure 파일에 자동 세팅"
                sudo -u ubuntu -i aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID_VALUE"
                sudo -u ubuntu -i aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY_VALUE"
                sudo -u ubuntu -i aws configure set default.region "$AWS_DEFAULT_REGION_VALUE"
                sudo -u ubuntu -i aws configure set default.output "$AWS_DEFAULT_OUTPUT_VALUE"
                
                AWS_VERSION=$(aws --version 2>&1)
                log "Step 8: AWS CLI configure 설정 완료"
                source /home/ubuntu/.bashrc
                
                ################################################################################
                # 9. Kafka 설정 폴더 생성 및 권한 부여
                ################################################################################
                log "Step 9: Kafka 설정 폴더 생성 및 권한 부여"
                
                sudo mkdir -p /opt/kafka/config
                sudo chown -R ubuntu:ubuntu /opt/kafka
                
                ################################################################################
                # 10. 커스텀 파티셔너, 파일네임 플러그인을 다운로드
                ################################################################################
                log "Step 10: 커스텀 파티셔너, 파일네임 플러그인 다운로드"
                
                sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-partitioner-1.0-SNAPSHOT.jar \
                  "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/KafkaConnector/custom-partitioner-1.0-SNAPSHOT.jar" && \
                sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-filename-1.0-SNAPSHOT.jar \
                  "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/KafkaConnector/custom-filename-1.0-SNAPSHOT.jar"
                
                ################################################################################
                # 11. s3-sink-connector.properties 생성
                ################################################################################
                log "Step 11: /opt/kafka/config/s3-sink-connector.properties 파일 생성"
                
                cat <<EOF > /opt/kafka/config/s3-sink-connector.properties
                # 커넥터 이름
                name=s3-sink-connector
                
                # S3 Sink Connector 클래스
                connector.class=io.confluent.connect.s3.S3SinkConnector
                tasks.max=1
                
                # 연결할 토픽
                topics=nginx-topic
                
                # Object Storage/S3 관련 설정
                s3.region=kr-central-2
                s3.bucket.name=${BUCKET_NAME}
                s3.part.size=5242880
                
                aws.access.key.id=${AWS_ACCESS_KEY_ID_VALUE}
                aws.secret.access.key=${AWS_SECRET_ACCESS_KEY_VALUE}
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
                
                # Time-based 파티셔너 필수 설정
                partition.duration.ms=3600000
                path.format='year_'yyyy/'month_'MM/'day_'dd/'hour_'HH
                locale=en-US
                timezone=Asia/Seoul
                timestamp.extractor=Wallclock
                
                # 예약어 치환 규칙
                custom.replacements==:_
                EOF
                
                ################################################################################
                # 12. worker.properties 생성
                ################################################################################
                log "Step 12: /opt/kafka/config/worker.properties 생성"
                
                cat <<EOF > /opt/kafka/config/worker.properties
                # 워커 기본 설정
                bootstrap.servers=${KAFKA_BOOTSTRAP_SERVER}
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
                EOF
                
                ################################################################################
                # 13. kafka-connect systemd 서비스 등록
                ################################################################################
                log "Step 13: kafka-connect systemd 서비스 등록"
                
                cat <<EOF | sudo tee /etc/systemd/system/kafka-connect.service
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
                EOF
                
                log "Step 13: systemd 등록 완료 (kafka-connect.service)"
                
                ################################################################################
                # 완료
                ################################################################################
                log "Setup 완료"
                ```
            
            - CPU 멀티스레딩: `활성화`
        
    - 생성 버튼 클릭
6. `kafka-connector` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
7. 확인 버튼 클릭
8. `kafka-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab2-4-8-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab2-4-8-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab2-4-8-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{kafka-connector의 public ip주소}
    ```
    
    - {kafka-connector의 public ip주소}: 복사한 각 IP 주소 입력
    
    #### **lab2-4-8-4**
    
    ```bash
    yes
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
    
    #### **lab2-4-8-5**
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```

9. 스크립트 적용 확인
    - **Note**: 스크립트 적용에 10~15분 소요

    #### **lab2-4-9**
   
    ```
    tail -f /home/ubuntu/setup.log
    ```
   
    
# 5. S3 Sink Connector 생성

1. 버킷에 쓰기 권한 부여
    - **Note**: `{버킷 이름}`: 실제 생성한 버킷 이름(`data-catalog`)으로 변경

    #### lab2-5-1
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket {Kafka와 연동된 버킷 이름(data-catalog)} \
      --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```
    
3. S3 Sink Connector(`s3-sink-connector.properties`), Standalone Worker(`worker.properties`) 설정 파일 확인

    #### lab2-5-3
    
    ```
    ls /opt/kafka/config
    ```
    ![image](https://github.com/user-attachments/assets/2bdefc88-31aa-4d5e-8498-0a7ff3619da6)
    

4. kafka-connect 시스템 서비스 파일(`kafka-connect.service`) 확인
    
    #### lab2-5-4
    
    ```bash
    ls /etc/systemd/system | grep kafka-connect.service
    ```

    
5. 데몬 리로드 및 서비스 시작
    
    #### lab2-5-5
    
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable kafka-connect
    sudo systemctl start kafka-connect
    ```

6. s3-sink-connector 상태 정보 조회
   
    #### lab2-5-6
    
    ```bash
    watch -n 1 "curl -s http://localhost:8083/connectors/s3-sink-connector/status | jq"
    ```

7. `connector`, `tasks`의 `state` 값이 `RUNNING`인 것을 확인

8. Object Storage 버킷 내 NGINX 로그 적재 확인
    - 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
    - `data-catalog` 버킷 클릭
    - `/topics/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}/day_{현재 일}/hour_{현재 시}` 디렉터리로 이동
    - 버킷 내 적재된 NGINX 로그 적재 확인
