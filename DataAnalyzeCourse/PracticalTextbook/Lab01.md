# Pub/Sub 가이드

본 가이드는 Kakao Cloud Pub/Sub을 활용하여 메시지를 송수신하고, 트래픽 로그를 생성 및 수집하는 방법을 단계별로 안내합니다. REST API 및 Go SDK 실습을 거쳐, 최종적으로 NGINX 로그를 Object Storage에 적재해보는 과정을 포함합니다.

---

## 1. Topic 및 Subscription 생성

1. traffic-generator-2에서 VM2로 디렉터리 이동
   
   ##### **lab1-2-1**
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
   
   - 이후 단계를 진행하기 위해 작업 디렉터리를 변경

2. NGINX 로그 적재용 토픽 생성
   
   ##### **lab1-2-2**
   python3 create_topic.py
   
   - `log-topic`이라는 이름의 토픽이 생성될 예정

3. 카카오 클라우드 콘솔 > **Analytics > Pub/Sub** > **토픽** 메뉴로 이동  
4. `log-topic` 토픽 생성 확인  
5. Object Storage용 서브스크립션 생성
   
   ##### **lab1-2-3**
   python3 create_subscription.py
   
   - `obj-subscription`이라는 이름의 서브스크립션이 생성될 예정

6. 카카오 클라우드 콘솔 > **Analytics > Pub/Sub** > **서브스크립션** 메뉴로 이동  
7. `obj-subscription` 서브스크립션 생성 확인  

---

## 2. REST API를 활용한 메시지 송수신

1. traffic-generator-1에서 VM1로 디렉터리 이동
   
   ##### **lab1-3-1**
   cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
   
   - 이후 단계를 진행하기 위해 작업 디렉터리를 변경

2. traffic-generator-1에서 `test-topic`으로 메시지 전송
   - 터미널 CLI를 통한 메시지 전송 스크립트 실행
   
   ##### **lab1-3-2**
   python3 pub_sub_send.py
   
   - 실행 후 원하는 메시지를 입력하고, `Enter` 및 `Ctrl+D` 키로 전송 완료

3. test-topic의 `pull-subscription` 메시지를 traffic-generator-2에서 수신
   - 터미널 CLI를 통한 메시지 수신 스크립트 실행
   
   ##### **lab1-3-3**
   python3 restapi_pull_sub.py
   
   - traffic-generator-2 터미널에서 방금 전송한 메시지가 정상적으로 수신되는지 확인

4. 웹 API로 메시지 확인
   - 웹 브라우저에서 아래 URL을 열어 메시지가 제대로 적재됐는지 확인
     http://{ALB public ip 주소}/push-messages
   - 새로고침을 여러 번 시도하여 메시지 수신 내용을 확인
     - 메시지가 안 보일 경우 전송에 시간이 걸릴 수 있으므로 잠시 대기 후 다시 시도
   - 프로그램 종료: `Ctrl + C`
     - Traceback 메시지가 표시되어도 정상 동작

---

## 3. Go SDK를 활용한 메시지 송수신

1. traffic-generator-1에서 Pub/Sub으로 메시지 전송
   - Go SDK 실습용 디렉터리로 이동
   
   #### **lab1-4-1-1**
   cd /home/ubuntu/gosdk/cmd
   
   - Publisher 실행 파일 생성
   
   #### **lab1-4-1-2**
   go build -o publisher config.go publisher.go
   
   - Publisher 실행 파일을 이용해 `test-topic`으로 메시지 송신
   
   #### **lab1-4-1-3**
   ./publisher

2. test-topic의 `pull-subscription` 메시지를 traffic-generator-2에서 수신
   - Go SDK 실습용 디렉터리로 이동
   
   #### **lab1-4-2-1**
   cd /home/ubuntu/gosdk/cmd
   
   - Subscriber 실행 파일 생성
   
   #### **lab1-4-2-2**
   go build -o subscriber config.go subscriber.go
   
   - Subscriber 실행 파일을 이용해 `pull-subscription` 메시지 수신
   
   #### **lab1-4-2-3**
   ./subscriber

---

## 4. Object Storage에 NGINX 로그 적재

1. traffic-generator-1에서 트래픽 로그 생성
   
   ##### **lab1-5-1**
   python3 /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1/traffic_generator.py
   
   - 트래픽 로그가 자동으로 생성되어 NGINX 로그에 반영됨
    
2. 실행 완료 후, 생성된 로그 확인
   
   ##### **lab1-5-2**
   cat /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1/traffic_generator.log
   
   - 로그가 제대로 생성되었는지 터미널에서 확인

3. API Public IP로 접속해 로그 생성
   - 웹 브라우저 주소창에 아래 URL 입력
     http://{ALB의 Public IP}

4. 카카오 클라우드 콘솔에서 `pubsub-nginx-log` 버킷에 쌓인 NGINX 로그 확인
   - **카카오 클라우드 콘솔 > 전체 서비스 > Beyond Storage Service > Object Storage**
   - `pubsub-nginx-log` 버킷 클릭
   - 해당 날짜(년/월/일) 디렉터리로 이동하여 생성된 log 파일 확인
