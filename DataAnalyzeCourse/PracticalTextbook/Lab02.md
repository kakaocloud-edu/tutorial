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


## 2. Kafka 기본 환경 설정
- **Note**: `trarffic-generator-1, 2`에서 설치 진행
- **Note**: 설치 중간에 보라색 화면이 뜨면 'Enter`로 진행

1. Java 설치
    
    #### lab2-6-1-1
    
    ```bash
    cd
    ```
    
    #### lab2-6-1-2
   - **Note**: 핑크색 화면이 뜨면 'Enter' 입력 후 설치 재개
    
    ```bash
    sudo apt update
    sudo apt install -y openjdk-21-jdk
    java -version
    ```
    
2. Kafka 바이너리 다운로드 및 설치
    - /opt 디렉터리로 이동 후 압축 풀어서 kafka 폴더 구성
    
    #### lab2-6-2
   - **Note**: 정지한 상태로 보일 수 있으나 명령어 실행 중이므로 약 5분정도 대기 필요
    ```bash
    cd /opt && sudo wget -qO- https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz | sudo tar -xz && sudo mv kafka_2.13-3.7.1 kafka
    ```

    
5. ~/.bashrc에 환경 변수 및 부트스트랩 서버 주소를 설정하여 Kafka 실행에 필요한 경로와 정보 등록
    
    #### lab2-6-3-1
   - **Note**: `{Kafka 부트스트랩 서버}`: `kafka` 클러스터의 부트스트랩 서버 입력
   - **Note**: `{Kafka 부트스트랩 서버}` 개인 환경에 맞게 수정 필수
    
    ```bash
    cat << 'EOF' >> ~/.bashrc
    export KAFKA_HOME=/opt/kafka
    export PATH=$PATH:$KAFKA_HOME/bin
    export KAFKA_BOOTSTRAP_SERVERS="{Kafka 부트스트랩 서버}"
    EOF
    ```
    

   #### lab2-6-3-2
    
    ```bash
    source ~/.bashrc
    ```
    
6. kafka-python 라이브러리 설치
    
    #### lab2-2-4
    
    ```bash
    sudo apt update
    ```
    ```bash
    sudo pip3 install kafka-python
    ```
    
7. Kafka 클러스터와 통신 확인
    
    #### lab2-2-5
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
    

# 3. Kafka 메시지 송수신 확인

## 3-1. 콘솔 스크립트로 메시지 송수신(earlist 옵션)

1. `traffic-generator-1`에서 `/opt/kafka` 디렉터리로 이동
    
    #### lab2-6-1-1
        
    ```bash
    cd /opt/kafka
    ```
    
2. 새 토픽(`consol-topic`) 생성
    
    #### lab2-6-1-2
        
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

        # 현재 스크립트와 같은 디렉터리에 있는 kafka-run-class.sh 스크립트를 호출합니다.
        # 실행 시 전달된 모든 인자("$@")를 그대로 넘겨주며, 자바 클래스 org.apache.kafka.tools.TopicCommand를 실행합니다.
        exec $(dirname $0)/kafka-run-class.sh org.apache.kafka.tools.TopicCommand "$@"
        ```
    
3. 콘솔 프로듀서 실행 후 송신할 메세지 입력 후 `Enter` 키 입력
    
    #### lab2-6-1-3

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
    
    #### lab2-6-1-5
        
    ```bash
    cd /opt/kafka
    ```
    
6. `traffic-generator-2`에서 Kafka 콘솔 컨슈머를 실행해 consumer-group-earliest 그룹으로 `consol-topic` 토픽의 메시지 수신
    
    #### lab2-6-1-6
        
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
        

## 3-2. 콘솔 스크립트로 메시지 송수신(latest 옵션)
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
   
        #### lab2-6-2-2
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
    
    #### lab2-6-2-4
        
    ```bash
    bin/kafka-consumer-groups.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} --list
    ```
    - `consumer-group-latest`, `consumer-group-earliest` 두 값이 뜨는거 확인


## 3-3. Python SDK로 메시지 송수신

1. `traffic-generator-1`에서 새 토픽(`python-topic`) 생성
    #### lab2-6-3-1
    
    ```bash
    bin/kafka-topics.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS} \
    --create --topic python-topic --partitions 2 --replication-factor 2
    ```
    
2. `traffic-generator-1`에서 Python 프로듀서 코드 실행
    #### lab2-6-3-2
    
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

    #### lab2-6-3-2
    
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
    

# 5. Nginx 로그 수집 및 Kafka 전송

1. Nginx 로그 토픽 생성
    - `trarffic-generator-1`에서 nginx-topic 생성
    
        #### lab2-6-1
        
        ```bash
        bin/kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
        --create --topic nginx-topic --partitions 2 --replication-factor 2
        ```


3. `api-server-1`에서 Logstash 설정 파일을 수정하여 Kafka로 송신하도록 설정

    #### lab2-6-3
   
    ```
    sudo sed -i 's/logs-to-pubsub.conf/logs-to-kafka.conf/g' /etc/logstash/logstash.yml
    ```

4. Logstash 재실행 및 상태 확인
    
    #### lab2-6-4
    
    ```bash
    sudo systemctl restart logstash
    ```
    ```bash
    sudo systemctl status logstash
    ```

    - `Active:active (running)` 확인
    
5. `trarffic-generator-2`에서 콘솔 컨슈머 실행
    
    #### lab2-6-5
    
    ```bash
    bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS \
    --topic nginx-topic --from-beginning
    ```
    
6. 웹 브라우저 주소창에 `http://{ALB의 Public IP}`를 입력하여 접속 후 링크 클릭 등을 통해 임의로 트래픽 생성
7. `trarffic-generator-2`의 터미널에서 NGINX 로그 확인
8. `Ctrl`+`c` 키를 입력하여 종료
   
    
# 5. S3 Sink Connector 생성

1. 버킷에 쓰기 권한 부여

    #### lab2-5-1
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket data-catalog \
      --grant-write 'uri="http://acs.amazonaws.com/groups/global/AllUsers"' \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```
    
2. S3 Sink Connector([`s3-sink-connector.properties`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/s3-sink-connector.properties)), Standalone Worker([`worker.properties`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/worker.properties)) 설정 파일 확인

    #### lab2-5-2
    
    ```
    ls /opt/kafka/config
    ```
    ![image](https://github.com/user-attachments/assets/2bdefc88-31aa-4d5e-8498-0a7ff3619da6)
    

3. kafka-connect 시스템 서비스 파일([`kafka-connect.service`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/KafkaConnector/kafka-connect.service)) 확인
    
    #### lab2-5-3
    
    ```bash
    ls /etc/systemd/system | grep kafka-connect.service
    ```

    
4. 데몬 리로드 및 서비스 시작
    
    #### lab2-5-4-1
    
    ```bash
    sudo systemctl daemon-reload
    ```

    #### lab2-5-4-2
    
    ```bash
    sudo systemctl enable kafka-connect
    ```
    
    #### lab2-5-4-3
    
    ```bash
    sudo systemctl start kafka-connect
    ```

5. s3-sink-connector 상태 정보 조회
   - **Note**: `connector`, `tasks` 항목의 `state` 값이 `RUNNING`인 것을 확인
   
    #### lab2-5-5
    
    ```bash
    watch -n 1 "curl -s http://localhost:8083/connectors/s3-sink-connector/status | jq"
    ```



6. Object Storage 버킷 내 NGINX 로그 적재 확인
    - 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
    - `data-catalog` 버킷 클릭
    - `/topics/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}/day_{현재 일}/hour_{현재 시}` 디렉터리로 이동
    - 버킷 내 적재된 NGINX 로그 적재 확인
