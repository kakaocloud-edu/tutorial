
# Pub/Sub 가이드

이 가이드는 Pub/Sub 기능을 활용한 메시지 송수신, 트래픽 로그 생성하고 NGINX 로그를 Object Storage에 적재하는 실습입니다.
---

## 1. Topic 및 Subscription 생성

1. Traffic-Generator-VM2에서 실행하여 VM2로 디렉토리 이동
   #### **lab1-2-1**
   ```bash
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
   ```

2. Traffic-Generator-VM2에서 토픽 생성
   #### **lab1-2-2**
       - nginx 로그 적재용 토픽 생성
   ```bash
   python3 create_topic.py
   ```
    - 카카오클라우드 콘솔 > Analytics > Pub/Sub > 토픽 메뉴 클릭
    - `log-topic` 토픽 생성 확인
      
3. Traffic-Generator-VM2에서 서브스크립션 생성
   #### **lab1-2-3**
       - object storage로 쌓는 서브스크립션 생성
   ```bash
   python3 create_subscription.py
   ```
    - 카카오클라우드 콘솔 > Analytics > Pub/Sub > 서브스크립션 메뉴 클릭
    - `objectstoragesubscription` 서브스크립션 생성 확인
  

## 2. Python을 활용한 Pub/Sub 실습

1. Traffic-Generator-VM1에서 실행하여 VM1로 디렉토리 이동
   #### **lab1-3-1**
   ```bash
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
   ```

2. Traffic-Generator-VM1에서 pub/sub으로 메세지 전송
   #### **lab1-3-2**
   ```bash
   python3 pub_sub_send.py
   ```
    - Traffic-Generator-VM1 터미널 창에 전송하고 싶은 메세지 입력 후 키보드의 `Enter`, `Ctrl+D` 키를 눌러 메세지 송신

3. Traffic-Generator-VM2에서 pub/sub의 pull-subscription으로 수신
    #### **lab1-3-3**
    ```bash
    python3 restapi_pull_sub.py
    ```
    - Traffic-Generator-VM2 터미널에서 Traffic-Generator-VM1에서 입력한 메세지 수신 확인


A. 웹 API로 메시지 확인

1. 웹 브라우저에서 아래 URL에 접속합니다.
    ```
    http://{alb public ip 주소}/push-messages
    ```
    - 여러 번 새로고침하여 메시지 적재 여부를 확인합니다.
        - Note: 메세지 받은 부분이 안뜰시 전송시간이 걸리므로 잠시 기다렸다가 다시 확인
    - 종료: `Ctrl + C`
        - Note: Traceback 메시지가 뜨는 것은 정상
    

## 3. Go SDK 메세지 송수신 테스트
1. Traffic-Generator-VM1에서 pub/sub으로 메세지 전송
    #### **lab1-4-1-1**
       - Go SDK 디렉토리로 이동
    ```bash
    cd /home/ubuntu/gosdk/cmd
    ```

    #### **lab1-4-1-2**
    - publisher 실행 파일 생성
    ```bash
    go build -o publisher config.go publisher.go
    ```
    #### **lab1-4-1-3**
       - publisher 실행 파일 실행
    ```bash
    ./publisher
    ```

 4. Traffic-Generator-VM2에서 pub/sub의 pull-subscription으로 수신
    #### **lab1-4-2-1**
    - Go SDK 디렉토리로 이동
    ```bash
    cd /home/ubuntu/gosdk/cmd
    ```
    #### **lab1-4-2-2**
    - subscriber 실행 파일 생성
    ```bash
    go build -o subscriber config.go subscriber.go
    ```
    #### **lab1-4-2-3**
    - subscriber 실행 파일 실행
    ```bash
    ./subscriber
    ```
    
    - 확인: VM1에서 입력한 메시지가 VM2에서 정상적으로 수신되는지 확인합니다.


## 4. NGINX 로그를 Object Storage에 적재

1. Traffic-Generator-VM1에서 트래픽 로그 생성
    #### **lab1-5-1**
    ```bash
    python3 traffic_generator.py
    ```
    
2. 실행 완료 후, 생성된 로그 확인(Traffic-Generator-VM1)
    #### **lab1-5-2**
   - cat 명령어로 로그 파일 내용 출력
    ```bash
    cat traffic_generator.log
    ```

1. API Public ip를 이용하여 접속 후 로그 생성
   - web에 이 주소로 접속하여 웹페이지 내용 클릭하여 로그 생성
   ```bash
   http://{alb public ip}
   ```
   

## 5. Pub/Sub용 Object Storage 콘솔 확인
    
1. NGINX 로그가 Object Storage에 정상적으로 쌓이는지 Pub/Sub용 Object Storage 콘솔을 통해 확인
2. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Storage Service > Object Storage

---
