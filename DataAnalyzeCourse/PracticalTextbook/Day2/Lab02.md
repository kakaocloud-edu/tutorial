# Kafka Connect로 CDC 데이터 파이프라인 구축

Data Stream VM을 통해 MySQL 데이터의 CDC(Change Data Capture) 변경 사항을 Kafka로 실시간 전송하고, S3 Sink Connector를 이용하여 Kafka 데이터를 Object Storage에 적재하는 데이터 파이프라인을 구축하는 실습을 진행합니다.
<img width="3164" height="1165" alt="커넥터_아키텍처" src="https://github.com/user-attachments/assets/26d294d3-45b6-4e4f-8cb3-37e675a7304c" />

---
## 1. Data Stream VM에 커넥터 추가
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `data-stream-vm` 인스턴스 SSH 접속
    - `data-stream-vm` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력
    
    #### **lab2-1-2-1**

    ```bash
    cd {keypair.pem 다운로드 위치}
    ```

    #### **lab2-1-2-2**
    - **Note**: {data-stream-vm의 public ip주소} 부분을 복사한 각 IP 주소로 교체
   
    ```bash
    ssh -i keypair.pem ubuntu@{data-stream-vm의 public ip주소}
    ```

    #### **lab2-1-2-3**
   
    ```bash
    yes
    ```
    
3. REST API를 통해 mysql-connector 생성
   
    #### **lab2-1-3**
   
    ```bash
    curl -s -X POST -H "Content-Type: application/json" \
      --data @/home/ubuntu/kafka/config/connectors/mysql-connector.json \
      http://localhost:8084/connectors \
    | jq .
    ```
    
4. mysql-connector의 RUNNING 상태 확인

    #### **lab2-1-4**
   
    ```bash
    curl -X GET http://localhost:8084/connectors/mysql-cdc-shopdb/status | jq .
    ```
    
   ![image](https://github.com/user-attachments/assets/3a2ee9a1-5c6f-48b8-8db7-bf623c64eb95)

5. Kafka에 생성된 토픽 목록 조회

    #### **lab2-1-5**
    
    ```bash
    /home/ubuntu/kafka/bin/kafka-topics.sh \
      --bootstrap-server "$KAFKA_BOOTSTRAP_SERVER" \
      --list \
    | grep ^mysql-server
    ```
    
    ![image](https://github.com/user-attachments/assets/faedd699-2cd2-4ebf-9137-b438404cfb15)

## 2. S3 Sink Connector VM에 커넥터 추가
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `s3-sink-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab2-2-2-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    #### **lab2-2-2-2**
    
    ```bash
    ssh -i keypair.pem ubuntu@{s3-sink-connector public ip주소}
    ```
    

3. Kafka Connect 서비스 설정

    #### **lab2-2-3-1**
   
    ```bash
    sudo systemctl daemon-reload
    ```

    #### **lab2-2-3-2**
   
    ```bash
    sudo systemctl enable kafka-connect-mysql-s3-sink.service 
    ```

    #### **lab2-2-3-3**
   
    ```bash
    sudo systemctl start kafka-connect-mysql-s3-sink.service
    ```
    
4. 서비스가 정상적으로 active (Running) 상태인지 확인

    #### **lab2-2-4**
   
    ```bash
    sudo systemctl status kafka-connect-mysql-s3-sink.service
    ```
    ![image](https://github.com/user-attachments/assets/bc305e4a-b407-418e-8689-65cd17dd1e49)


5. `data-catalog-bucket`에 nginx 로그를 쌓기 위해 필요한 쓰기 권한을 부여하는 명령어 실행(개선중)

    #### **lab2-2-5** 
    
    ```bash
    aws s3api put-bucket-acl \
      --bucket data-catalog-bucket \
      --grant-full-control "id=${USER_UUID}" \
      --endpoint-url https://objectstorage.kr-central-2.kakaocloud.com
    ```


6. mysql-s3-sink-connector 생성
    
    - **Note**: kafka-connect.service 실행 후 5초 정도 대기 후 진행
    #### **lab2-2-6** 
    
    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      --data @/home/ubuntu/kafka/config/connectors/mysql-s3-sink-connector.json \
      http://localhost:8084/connectors \
    | jq .
    ```
    
7. mysql-s3-sink-connector의 RUNNING 상태 확인

    #### **lab2-2-7** 

    ```bash
    curl -X GET http://localhost:8084/connectors/mysql-s3-sink-connector/status | jq .
    ```
    ![image](https://github.com/user-attachments/assets/e8b3b0f1-ac8e-4d8f-8c13-6612147399fe)


8. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
9. `data-catalog-bucket` 클릭
10. MySQL 데이터 적재 확인
    - **Note**: `data-catalog-bucket/raw_cdc_events/mysql-server.shopdb.users/partition=0/`디렉터리로 이동
      ![MySQL 데이터](https://github.com/user-attachments/assets/7b4f8255-a3e7-48a1-a56e-4eb626f4cbec)



