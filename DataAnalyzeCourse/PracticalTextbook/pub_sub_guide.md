# 1. 사전 준비
- 콘솔로 자원 미리 구축
  - Pub/Sub topic
  - MySQL
  - Object Storage
  - API Server VM 2개
  - ALB
  - Pub/Sub pull,push subscription
  - Traffice generator VM 2개

---

# Pub/Sub 가이드

이 가이드는 Pub/Sub 기능을 활용한 메시지 송수신, 트래픽 로그 생성, REST API 실습, Go SDK 실습, 그리고 NGINX 로그를 Object Storage에 적재하는 전체 과정을 설명합니다.

---

## 1. 기본 환경 설정

1. **VM 접속**
    - Traffic Generator VM 1, 2에 public IP를 통해 연결합니다.
    - 각 VM에 SSH로 접속합니다.
      ```bash
      ssh -i {keypair}.pem ubuntu@{vm public ip}
      ```
      
2. **디렉토리 이동**
    - **Traffic-Generator-VM1**
        
        ```bash
        cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
        ```
        
    - **Traffic-Generator-VM2**
        
        ```bash
        cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
        ```

    - **디렉토리 내부 파일 생성 여부 확인**

        ```bash
        ls -l
        ```
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

**Traffic-Generator-VM2에서 실행**

1. **토픽 생성**
    
    ```bash
    python3 create_topic.py
    ```

2. **카카오클라우드 콘솔 > Analytics > Pub/Sub > 토픽 메뉴 클릭**
3. **`log-topic` 토픽 생성 확인**
4. **Subscription 생성**
    
    ```bash
    python3 create_subscription.py
    ```
5. **카카오클라우드 콘솔 > Analytics > Pub/Sub > 서브스크립션 메뉴 클릭**
6. **`obj-subscription` 서브스크립션 생성 확인**
    

---

## 3. 메시지 송수신 테스트

1. **Traffic-Generator-VM1 (Publisher)에서 아래 명령어를 입력하여 Pub/Sub send 스크립트 실행**
    
    ```bash
    python3 pub_sub_send.py
    ```
2. **Traffic-Generator-VM1 터미널 창에 전송하고 싶은 메세지 입력 후 키보드의 `Enter`, `Ctrl+D` 키를 눌러 메세지 송신**
3. **Traffic-Generator-VM2 (Subscriber)에서 아래 명령어를 입력하여 Pub/Sub receive 스크립트 실행**
    
    ```bash
    python3 restapi_pull_sub.py
    ```
4. **Traffic-Generator-VM2 터미널에서 Traffic-Generator-VM1에서 입력한 메세지 수신 확인**


---

## 4. 웹 API로 메시지 확인

1. 웹 브라우저에서 아래 URL에 접속합니다.
    
    ```
    http://{alb public ip 주소}/push-messages
    ```
    
2. 여러 번 새로고침하여 메시지 적재 여부를 확인합니다.

  - note (메세지 받은 부분이 안뜰시 전송 중이라 그런거므로 잠시 기다렸다가 확인)

3. **종료:** `Ctrl + C`
    - (Traceback 메시지가 뜨는 것은 정상입니다.)

---

## 5. Traffic Generator 실행

**Traffic-Generator-VM1에서 아래 명령어 실행**

1. 트래픽 생성 스크립트 실행
    
    ```bash
    python3 traffic_generator.py
    ```
    
2. 실행 완료 후, 생성된 로그 확인
    
    ```bash
    cat traffic_generator.log
    ```
    

---

## 6. Go SDK 실습

### A. 작업 디렉토리 이동(VM1, 2)
```bash
cd /home/ubuntu/gosdk/cmd
```
    

### B. Publisher 및 Subscriber 실행

- **Traffic-Generator-VM1 (Publisher)**
    
    ```bash
    go build -o publisher config.go publisher.go
    ```
    ```bash
    ./publisher
    ```
    
- **Traffic-Generator-VM2 (Subscriber)**
    
    ```bash
    go build -o subscriber config.go subscriber.go
    ```
    ```bash
    ./subscriber
    ```
    

> 확인: VM1에서 입력한 메시지가 VM2에서 정상적으로 수신되는지 확인합니다.
> 

---

## 7. NGINX 로그를 Object Storage에 적재

### API Public ip를 이용하여 접속 후 로그 생성

- web에 http://api server public ip로 접속하여 웹페이지 내용 클릭하여 로그 생성


### Pub/Sub용 Object Storage 콘솔 확인

- NGINX 로그가 Object Storage에 정상적으로 쌓이는지 Pub/Sub용 Object Storage 콘솔을 통해 확인합니다.




### API Server 접속 및 설정 파일 확인(Object Storage에 적재 안될 시 확인)

1. **API Server 1, 2에 SSH 접속**
    
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

```jsx
Esc -> :wq
```

### 서비스 상태 확인

각 서비스를 아래 명령어로 확인합니다.

```bash
sudo systemctl status filebeat
sudo systemctl status logstash
sudo systemctl status nginx
```
