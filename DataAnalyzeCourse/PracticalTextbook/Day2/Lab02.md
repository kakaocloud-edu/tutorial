# Kafka Connect를 활용한 CDC 데이터 파이프라인 구축

MySQL Connector VM 생성을 통해 MySQL 데이터의 CDC(Change Data Capture) 변경 사항을 Kafka로 실시간 전송하고, S3 Sink Connector를 이용하여 Kafka 데이터를 Object Storage에 자동 적재하는 데이터 파이프라인 구축하는 실습을 진행합니다.

---
## 1. MySQL Connector VM 생성
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `mysql-source-connector`
        - 개수: `1`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.xlarge`
    - 볼륨: `10GB`
    - 키 페어: `keypair`
    - 네트워크
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
        - 유형: `새 인터페이스`
        - IP 할당 방식: `자동`
        - 보안 그룹: `con-sg`
    - 고급 설정
        - 사용자 스크립트: `mysql_source_connector_init.sh`의 쌍따옴표("") 사이에 자신의 리소스 값 입력
            - **Note**: 스크립트에 대한 자세한 내용은 아래 파일들 참고
                - [mysql_source_connector_init.sh](https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/kafka/mysql_source_connector_init.sh)
        #### **lab2-1-2**
        ```bash
        #!/bin/bash
        
        echo "kakaocloud: 1. 환경 변수 설정 시작"
        
        cat <<'EOF' > /tmp/env_vars.sh
        export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
        export MYSQL_DB_HOSTNAME="{MySQL 엔드포인트}"
        export LOGFILE="/home/ubuntu/setup.log"
        export MYSQL_DB_PORT="3306"
        export MYSQL_DB_USER="admin"
        export MYSQL_DB_PASSWORD="admin1234"
        export MYSQL_SERVER_ID="184054"
        export MYSQL_SERVER_NAME="mysql-server"
        EOF
        
        source /tmp/env_vars.sh
        
        if ! grep -q "source /tmp/env_vars.sh" /home/ubuntu/.bashrc; then
            echo "" >> /home/ubuntu/.bashrc
            echo "# Load custom environment variables" >> /home/ubuntu/.bashrc
            echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc
        fi
        
        chown ubuntu:ubuntu /tmp/env_vars.sh
        
        echo "kakaocloud: 2. 스크립트 다운로드 사이트 유효성 검사 시작"
        SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/kafka/mysql_source_connector.sh"
        CONNECTOR_SCRIPT="/home/ubuntu/mysql_source_connector.sh"
        
        curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
        wget -q "$SCRIPT_URL" -O "$CONNECTOR_SCRIPT"
        
        chown ubuntu:ubuntu "$CONNECTOR_SCRIPT"
        chmod +x "$CONNECTOR_SCRIPT"
        sudo -E "$CONNECTOR_SCRIPT"
        ```
        
    - 생성 버튼 클릭
3. `mysql_source_connector` 상태 Active 확인 후 Public IP 연결
    - 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭
4. `mysql_source_connector` 인스턴스 SSH 접속
    - `mysql_source_connector` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력
    
    #### **lab2-1-4-1**

    ```bash
    cd {keypair.pem 다운로드 위치}
    ```

    #### **lab2-1-4-3**
    - **Note**: {mysql_source_connector의 public ip주소} 부분을 복사한 각 IP 주소로 교체
   
    ```bash
    ssh -i keypair.pem ubuntu@{mysql_source_connector의 public ip주소}
    ```

    #### **lab2-1-4-4**
    ```bash
    yes
    ```
    
6. mysql_source_connector 스크립트 적용 확인
    - **Note**: 스크립트 적용에 약 7분 소요
      
    #### **lab2-1-5**
    - **Note**: 터미널 창이 작으면 로그가 안보일 수 있으니 터미널 창 크기 조절
    ```bash
    watch -c "awk '/kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}' < /var/log/cloud-init-output.log"
    ```
    
    - 모든 스크립트 완료 시 아래 출력됨
    ```
    kakaocloud: 1. 환경 변수 설정 시작
    kakaocloud: 2. 스크립트 다운로드 사이트 유효성 검사 시작
    kakaocloud: 2. 필수 환경 변수 검증 시작
    kakaocloud: 3. 시스템 업데이트 및 필수 패키지 설치 시작
    kakaocloud: 4. Kafka 설치 시작
    kakaocloud: 5. Java 환경 변수 등록 시작
    kakaocloud: 6. Debezium MySQL Connector 플러그인 다운로드 및 설치 시작
    kakaocloud: 7. Kafka Connect 분산 모드 설정 (worker.properties) 시작
    kakaocloud: 8. Kafka Connect 시스템 서비스 등록 및 시작
    kakaocloud: 9. Debezium Connector 구성 파일 생성 시작
    kakaocloud: Setup 완료
    ```
    
7. REST API를 통해 커넥터 생성
   
    #### **lab2-1-6**
    ```bash
    curl -s -X POST -H "Content-Type: application/json" \
      --data @/home/ubuntu/kafka/config/connectors/mysql-connector.json \
      http://localhost:8084/connectors \
    | jq .
    ```
    
8. mysql-connector의 상태 확인

    #### **lab2-1-7**
    ```bash
    curl -X GET http://localhost:8084/connectors/mysql-cdc-shopdb/status | jq .
    ```
    
   ![image](https://github.com/user-attachments/assets/3a2ee9a1-5c6f-48b8-8db7-bf623c64eb95)

9. Kafka에 생성된 토픽 목록 조회
    #### **lab2-1-8**
    
    ```bash
    /home/ubuntu/kafka/bin/kafka-topics.sh \
      --bootstrap-server "$KAFKA_BOOTSTRAP_SERVER" \
      --list \
    | grep '^mysql-server'
    ```
    
    ![image](https://github.com/user-attachments/assets/faedd699-2cd2-4ebf-9137-b438404cfb15)

## 2. S3 Sink Connector VM에서 Connector 추가
1. `s3-sink-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    ### **lab2-2-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    ### **lab2-2-2**
    
    ```bash
    ssh -i keypair.pem ubuntu@{s3-sink-connector public ip주소}
    ```
    

2. Kafka Connect 서비스 설정

    ### **lab2-2-3**
    ```bash
    sudo systemctl daemon-reload
    ```

    ### **lab2-2-3**
    ```bash
    sudo systemctl enable kafka-connect-mysql-s3-sink.service 
    ```

    ### **lab2-2-3**
    ```bash
    sudo systemctl start kafka-connect-mysql-s3-sink.service
    ```
    
3. 서비스가 정상적으로 active (Running) 상태인지 확인

    ### **lab2-2-3**
    ```bash
    sudo systemctl status kafka-connect-mysql-s3-sink.service
    ```
    ![image](https://github.com/user-attachments/assets/bc305e4a-b407-418e-8689-65cd17dd1e49)

    
4. kafka-s3-sink Connector 생성
    - **Note**: kafka-connect.service 실행 후 5초 정도 대기 후 진행
    
    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      --data @/home/ubuntu/kafka/config/connectors/mysql-s3-sink-connector.json \
      http://localhost:8084/connectors
    ```
    
5. 커넥터 상태 확인
    
    ```bash
    curl -X GET http://localhost:8084/connectors/mysql-s3-sink-connector/status | jq .
    ```
    ![image](https://github.com/user-attachments/assets/e8b3b0f1-ac8e-4d8f-8c13-6612147399fe)


6. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
7. `data-catalog-bucket` 클릭
8. MySQL 데이터 적재 확인
    - **Note**: `data-catalog-bucket/raw_cdc_events/mysql-server.shopdb.users/partition=0/`디렉터리로 이동
      ![MySQL 데이터](https://github.com/user-attachments/assets/7b4f8255-a3e7-48a1-a56e-4eb626f4cbec)



