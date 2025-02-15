
# Pub/Sub 가이드

Pub/Sub을 활용하여 메시지 송수신, 트래픽 로그 생성, REST API 실습, Go SDK 실습, 그리고 NGINX 로그를 Object Storage에 적재합니다.

---

## 1. Topic 및 Subscription 생성

1. traffic-generator-2에서 아래 명령을 실행하여 VM2로 디렉터리 이동
   #### **lab1-2-1**
   ```bash
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
   ```

2. NGINX 로그 적재용 토픽 생성
   #### **lab1-2-2**
   ```bash
   python3 create_topic.py
   ```
    - 카카오클라우드 콘솔 > Analytics > Pub/Sub > 토픽 메뉴 클릭
    - `log-topic` 토픽 생성 확인
      
3. object storage 유형 서브스크립션 생성
   #### **lab1-2-3**
       - 
   ```bash
   python3 create_subscription.py
   ```
    - 카카오클라우드 콘솔 > Analytics > Pub/Sub > 서브스크립션 메뉴 클릭
    - `obj-subscription` 서브스크립션 생성 확인
  

## 2. REST API를 활용한 메시지 송수신

1. traffic-generator-1에서 아래 명령을 실행하여 VM1로 디렉터리 이동
   #### **lab1-3-1**
   ```bash
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
   ```

2. traffic-generator-1에서 test-topic으로 메세지 전송
   #### **lab1-3-2**
   ```bash
   python3 pub_sub_send.py
   ```
    - traffic-generator-1 터미널 창에 전송하고 싶은 메세지 입력 후 키보드의 `Enter`, `Ctrl+D` 키를 눌러 메세지 송신

3. test-topic의 pull-subscription의 메세지를 traffic-generator-2에서 수신
    #### **lab1-3-3**
    ```bash
    python3 restapi_pull_sub.py
    ```
    - traffic-generator-2 터미널에서 traffic-generator-1에서 입력한 메세지 수신 확인


4. 웹 API로 메시지 확인
   - 웹 브라우저 주소창에 아래 URL 입력
       ```
       http://{ALB public ip 주소}/push-messages
       ```
    - 여러 번 새로고침하여 메시지 적재 여부 확인
        - Note: 메세지 받은 부분이 안뜰시 전송시간이 걸리므로 잠시 기다렸다가 다시 확인
    - 종료: `Ctrl + C`
        - Note: Traceback 메시지가 뜨는 것은 정상
    

## 3. Go SDK를 활용한 메시지 송수신
1. traffic-generator-1에서 pub/sub으로 메세지 전송
   - Go SDK 메세지 송수신 실습용 디렉터리로 이동
    #### **lab1-4-1-1**
    ```bash
    cd /home/ubuntu/gosdk/cmd
    ```

   - publisher 실행 파일 생성
    #### **lab1-4-1-2**
    ```bash
    go build -o publisher config.go publisher.go
    ```

   - publisher 실행 파일을 실행하여 test-topic으로 메세지 송신
    #### **lab1-4-1-3**
    ```bash
    ./publisher
    ```

 2. test-topic의 pull-subscription의 메세지를 traffic-generator-2에서 수신
    #### **lab1-4-2-1**
    - Go SDK 메세지 송수신 실습용 디렉터리로 이동
    ```bash
    cd /home/ubuntu/gosdk/cmd
    ```

   - subscriber 실행 파일 생성
    #### **lab1-4-2-2**
    ```bash
    go build -o subscriber config.go subscriber.go
    ```

   - subscriber 실행 파일을 실행하여 pull-subscription의 메세지 수신
    #### **lab1-4-2-3**
    ```bash
    ./subscriber
    ```
    - **Note**: traffic-generator-1에서 입력한 메시지가 traffic-generator-2에서 정상적으로 수신되는지 확인


## 4. Object Storage에 NGINX 로그 적재

1. traffic-generator-1에서 트래픽 로그 생성
    #### **lab1-5-1**
    ```bash
    python3 /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1/traffic_generator.py
    ```
    
2. 실행 완료 후, 생성된 로그 확인
    #### **lab1-5-2**
    ```bash
    cat /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1/traffic_generator.log
    ```

3. API Public ip를 이용하여 접속 후 로그 생성
   - 웹 브라우저 주소창에 아래 URL 입력
   ```bash
   http://{ALB의 Public IP}
   ```

4. 콘솔에서 `pubsub-nginx-log` 버킷에 쌓인 NGINX 로그 확인
   - 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Storage Service > Object Storage
   - `pubsub-nginx-log` 버킷 클릭
   - 실습 당일 년/월/일 디렉터리로 이동하여 log 파일 생성 확인
---
