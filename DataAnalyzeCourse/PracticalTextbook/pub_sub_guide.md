
# Pub/Sub 가이드

이 가이드는 Pub/Sub 기능을 활용한 메시지 송수신, 트래픽 로그 생성, REST API 실습, Go SDK 실습, 그리고 NGINX 로그를 Object Storage에 적재하는 전체 과정을 설명합니다.


## 1. 기본 환경 설정
1. Traffic Generator VM 1,2 접속
    - Traffic Generator VM 1, 2에 public IP를 통해 연결
    - 각 VM에 SSH로 접속
   #### **lab2-1-1**
   ```bash
   ssh -i {keypair}.pem ubuntu@{vm public ip}
   ```
      
2. 디렉토리 이동
    - Traffic-Generator-VM1에서 실행하여 VM1로 디렉토리 이동
   #### **lab2-1-2**
   ```bash
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
   ```
        
    - Traffic-Generator-VM2에서 실행하여 VM2로 디렉토리 이동
   #### **lab2-1-3**
   ```bash
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
   ```

3. 디렉토리 내부 파일 생성 여부 확인
   #### **lab2-1-4**
   ```bash
   ls -l
   ```

---
- **파일 생성이 안 되었을 시 아래 명령어 실행**
  - **Traffic-Generator-VM1,2 모두 실행**
  ```bash
  wget -nc -P /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API \
    https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/config.py
  ```

  - **Traffic-Generator-VM1에서 실행**
  ```bash
  wget -nc -P /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1 \
    https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM1/pub_sub_send.py \
    https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM1/traffic_generator.py
  ```

  - **Traffic-Generator-VM2에서 실행**
  ```bash
  wget -nc -P /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2 \
    https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/create_subscription.py \
    https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/create_topic.py \
    https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/restapi_pull_sub.py
  ```
---


## 2. Topic 및 Subscription 생성

1. Traffic-Generator-VM2에서 토픽 생성
   #### **lab2-2-1**
   ```bash
   python3 create_topic.py
   ```

    - 카카오클라우드 콘솔 > Analytics > Pub/Sub > 토픽 메뉴 클릭
    - `log-topic` 토픽 생성 확인
      
2. Traffic-Generator-VM2에서 Subscription 생성
   #### **lab2-2-2**
   ```bash
   python3 create_subscription.py
   ```
    - 카카오클라우드 콘솔 > Analytics > Pub/Sub > 서브스크립션 메뉴 클릭
    - `objectstoragesubscription` 서브스크립션 생성 확인
  

## 3. 콘솔 메시지 송수신 테스트

1. Traffic-Generator-VM1에서 pub/sub으로 메세지 전송
    #### **lab2-3-1**
    ```bash
    python3 pub_sub_send.py
    ```
    - Traffic-Generator-VM1 터미널 창에 전송하고 싶은 메세지 입력 후 키보드의 `Enter`, `Ctrl+D` 키를 눌러 메세지 송신

2. Traffic-Generator-VM2에서 pub/sub의 pull-subscription으로 수신
    #### **lab2-3-2**
    ```bash
    python3 restapi_pull_sub.py
    ```
    - Traffic-Generator-VM2 터미널에서 Traffic-Generator-VM1에서 입력한 메세지 수신 확인


## 4. 웹 API로 메시지 확인

1. 웹 브라우저에서 아래 URL에 접속합니다.
    ```
    http://{alb public ip 주소}/push-messages
    ```
    - 여러 번 새로고침하여 메시지 적재 여부를 확인합니다.
    - note (메세지 받은 부분이 안뜰시 전송시간이 걸리므로 잠시 기다렸다가 다시 확인)
    - 종료: `Ctrl + C`
    - (Traceback 메시지가 뜨는 것은 정상입니다.)


## 5. Traffic Generator 실행
1. Traffic-Generator-VM1에서 트래픽 로그 생성
    #### **lab2-4-1**
    ```bash
    python3 traffic_generator.py
    ```
    
2. 실행 완료 후, 생성된 로그 확인
    #### **lab2-4-2**
    ```bash
    cat traffic_generator.log
    ```
    

## 6. Go SDK 메세지 송수신 테스트
1. Go SDK 디렉토리로 이동(Traffic-Generator-VM1, 2)
    #### **lab2-5-1**
    ```bash
    cd /home/ubuntu/gosdk/cmd
    ```

2. Traffic-Generator-VM1에서 pub/sub으로 메세지 전송
    #### **lab2-5-2-1**
    ```bash
    go build -o publisher config.go publisher.go
    ```
    #### **lab2-5-2-2**
    ```bash
    ./publisher
    ```

 3. Traffic-Generator-VM2에서 pub/sub의 pull-subscription으로 수신
    #### **lab2-5-3-1**
    ```bash
    go build -o subscriber config.go subscriber.go
    ```
    #### **lab2-5-3-2**
    ```bash
    ./subscriber
    ```
    
    > 확인: VM1에서 입력한 메시지가 VM2에서 정상적으로 수신되는지 확인합니다.


## 7. NGINX 로그를 Object Storage에 적재

1. API Public ip를 이용하여 접속 후 로그 생성
   ```bash
   http://{alb public ip}
   ```
   - web에 위 주소로 접속하여 웹페이지 내용 클릭하여 로그 생성

## 8. Pub/Sub용 Object Storage 콘솔 확인
    
1. NGINX 로그가 Object Storage에 정상적으로 쌓이는지 Pub/Sub용 Object Storage 콘솔을 통해 확인
2. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Storage Service > Object Storage


---

### API Server 접속 및 설정 파일 확인(Object Storage에 적재 안될 시 확인)

1. API Server 1, 2에 SSH 접속 후 디렉토리 이동
    
    ```bash
    cd /etc/logstash/conf.d
    ```
    
2. 설정 파일 확인
    
    ```bash
    cat logs-to-pubsub.conf
    ```
    
3. 설정 파일 편집(필요시)
    
    ```bash
    vi logs-to-pubsub.conf
    ```
    
4. 편집 후 저장 및 나가기(필요시)

    ```bash
    Esc -> :wq
    ```

### 서비스 상태 확인

1. 각 서비스를 아래 명령어로 확인합니다.

    ```bash
    sudo systemctl status filebeat
    sudo systemctl status logstash
    sudo systemctl status nginx
    ```

---
