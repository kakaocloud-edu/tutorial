# Pub/Sub 가이드

Pub/Sub을 활용하여 메시지를 송수신하고, REST API 및 Go SDK를 사용해 메시지를 처리하며, NGINX 로그를 Object Storage에 적재하는 과정을 다룹니다. 이를 통해 실시간 데이터 스트리밍과 로그 수집 및 저장을 자동화하는 방법을 실습합니다.
---

## 1. Topic 및 Subscription 생성

1. traffic-generator-2에서 VM2로 디렉터리 이동
    
    ### **lab1-2-1**
    
    ```bash
    cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
    ```
    
- 이후 단계를 진행하기 위해 작업 디렉터리를 변경
1. NGINX 로그 적재용 토픽 생성
    
    ### **lab1-2-2**
    
    ```bash
    python3 create_topic.py
    ```
    
2. 카카오 클라우드 콘솔 > **Analytics > Pub/Sub** > **토픽** 메뉴로 이동
3. `log-topic` 토픽 생성 확인
4. Object Storage용 서브스크립션 생성
    
    ### **lab1-2-3**
    
    ```bash
    python3 create_subscription.py
    ```
    
5. 카카오 클라우드 콘솔 > **Analytics > Pub/Sub** > **서브스크립션** 메뉴로 이동
6. `obj-subscription` 서브스크립션 생성 확인

---

## 2. REST API를 활용한 메시지 송수신

1. traffic-generator-1에서 아래 명령을 실행하여 VM1 디렉터리로 이동
    
    ### **lab1-3-1**
    
    ```bash
    cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
    
    ```
    
2. traffic-generator-1에서 `test-topic`으로 메시지 전송
    - 터미널 CLI를 통한 메시지 전송 스크립트 실행
    
    ### **lab1-3-2**
    
    ```bash
    python3 pub_sub_send.py
    ```
    
    - 실행 후 원하는 메시지를 입력하고, `Enter` 및 `Ctrl+D` 키로 전송 완료
3. test-topic의 `pull-subscription` 메시지를 traffic-generator-2에서 수신
    - 터미널 CLI를 통한 메시지 수신 스크립트 실행
    
    ### **lab1-3-3**
    
    ```bash
    python3 restapi_pull_sub.py
    ```
    
    - traffic-generator-2 터미널에서 방금 전송한 메시지가 정상적으로 수신되는지 확인
4. 웹 API로 메시지 확인
    - 웹 브라우저 주소창에 아래 URL 입력
        
        ```
        http://{ALB public ip 주소}/push-messages
        ```
        
    - 새로고침을 여러 번 시도하여 메시지 수신 내용을 확인
        - 메시지가 안 보일 경우 전송에 시간이 걸릴 수 있으므로 잠시 대기 후 다시 시도
    - 프로그램 종료: `Ctrl + C`
        - **Note**: Traceback 메시지가 뜨는 것은 정상

---

## 3. Go SDK를 활용한 메시지 송수신

1. traffic-generator-1에서 Pub/Sub으로 메시지 전송
    - Go SDK 실습용 디렉터리로 이동
        
        ### **lab1-4-1-1**
        
        ```bash
        cd /home/ubuntu/gosdk/cmd
        ```
        
    - Publisher 실행 파일 생성
        
        ### **lab1-4-1-2**
        
        ```bash
        go build -o publisher config.go publisher.go
        ```
        
    - Publisher 실행 파일을 이용해 `test-topic`으로 메시지 송신
        
        ### **lab1-4-1-3**
        
        ```bash
        ./publisher
        ```
        
2. test-topic의 `pull-subscription` 메시지를 traffic-generator-2에서 수신
    - Go SDK 실습용 디렉터리로 이동
        
        ### **lab1-4-2-1**
        
        ```bash
        cd /home/ubuntu/gosdk/cmd
        ```
        
    - Subscriber 실행 파일 생성
        
        ### **lab1-4-2-2**
        
        ```bash
        go build -o subscriber config.go subscriber.go
        
        ```
        
    - Subscriber 실행 파일을 이용해 `pull-subscription` 메시지 수신
        
        ### **lab1-4-2-3**
        
        ```bash
        ./subscriber
        ```
        

---

## 4. Object Storage에 NGINX 로그 적재

1. traffic-generator-1에서 트래픽 로그 생성
    
    ### **lab1-5-1**
    
    ```bash
    python3 /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1/traffic_generator.py
    ```
    
    - 트래픽 로그가 자동으로 생성되어 NGINX 로그에 반영됨
2. 실행 완료 후, 생성된 로그 확인
    
    ### **lab1-5-2**
    
    ```bash
    cat /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1/traffic_generator.log
    ```
    
3. ALB Public IP로 접속하여 로그 생성
    - 웹 브라우저 주소창에 아래 URL 입력
        
        ```
        http://{ALB의 Public IP}
        ```
        
4. 카카오 클라우드 콘솔에서 `pubsub-nginx-log` 버킷에 쌓인 NGINX 로그 확인
    - **카카오 클라우드 콘솔 > 전체 서비스 > Beyond Storage Service > Object Storage**
    - `pubsub-nginx-log` 버킷 클릭
    - 해당 날짜(년/월/일) 디렉터리로 이동하여 생성된 log 파일 확인
