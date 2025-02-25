# Pub/Sub 기반 실시간 메시징 및 로그 적재

Pub/Sub을 활용한 메시지 송수신, REST API 및 Go SDK를 통한 메시지 처리, Object Storage로의 NGINX 로그 적재를 다루는 실습입니다. 이를 통해 실시간 데이터 스트리밍과 로그 수집 및 저장 자동화 과정을 학습합니다.

---
## 1. 콘솔을 통한 토픽, 서브스크립션 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Pub/Sub > 토픽
2. 토픽 서비스 시작하기
3. `test-topic` 토픽 생성
    - 토픽 생성 버튼 클릭
        - 이름: `test-topic`
        - 기본 서브스크립션: `생성 안함`
        - 토픽 메세지 보존 기간: `0일 0시 10분`
        - 설명: `없음`
    - 생성 버튼 클릭
4. `test-topic` 토픽 생성 확인 후 클릭
5. 서브스크립션 탭 클릭
6. `test-topic`의 Pull 서브스크립션 생성
    - 서브스크립션 생성 버튼 클릭
        - 기본 설정
            - 이름: `test-pull-sub`
            - 토픽 선택: `test-topic`
        - 유형: `Pull`
        - 서브스크립션 메시지 보존 기간: `0일 0시 10분`
        - 응답 대기 시간: `20초`
        - 재처리 횟수: `횟수 지정`, `3번`
    - 생성 버튼 클릭
7. `test-pull-sub` 서브스크립션 생성 확인
8. `test-topic`의 Push 서브스크립션 생성
    - 서브스크립션 생성 버튼 클릭
        - 기본 설정
            - 이름: `test-push-sub`
            - 토픽 선택: `test-topic`
        - 유형: `Push`
            - 엔드포인트: `http://`, `{ALB Public IP}/push-subscription`
        - 서브스크립션 메시지 보존 기간: `0일 0시 10분`
        - 응답 대기 시간: `20초`
        - 재처리 횟수: `횟수 지정`, `3번`
    - 생성 버튼 클릭
9. `test-push-sub` 생성 확인
10. `data-catalog-topic` 토픽 생성
    - 좌측 토픽 탭 클릭
    - 토픽 생성 버튼 클릭
        - 이름: `data-catalog-topic`
        - 기본 서브스크립션: `생성 안함`
        - 토픽 메세지 보존 기간: `0일 0시 10분`
        - 설명: `없음`
    - 생성 버튼 클릭
11. `data-catalog-topic` 생성 확인 후 클릭
12. 서브스크립션 탭 클릭
13. `data-catalog-topic`의 Pull 서브스크립션 생성
    - 서브스크립션 생성 버튼 클릭
        - 기본 설정
            - 이름: `data-catalog-pull-sub`
            - 토픽 선택: `data-catalog-topic`
        - 유형: `Pull`
        - 서브스크립션 메시지 보존 기간: `0일 0시 10분`
        - 응답 대기 시간: `20초`
        - 재처리 횟수: `횟수 지정`, `3번`
    - 생성 버튼 클릭
14. `data-catalog-pull-sub` 생성 확인


## 2. CLI를 통한 토픽, 서브스크립션 생성

1. `traffic-generator-2` 터미널 창에서 아래 명령어 실행
    
    #### **lab1-2-1**
    
    ```bash
    cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
    ```
    
2. NGINX 로그 적재용 토픽 생성
    
    #### **lab1-2-2**
    
    ```bash
    python3 create_topic.py
    ```
    
3. 카카오 클라우드 콘솔 > Analytics > Pub/Sub > 토픽 메뉴로 이동 후 `log-topic` 토픽 생성 확인
4. Object Storage용 서브스크립션 생성
    
    #### **lab1-2-4**
    
    ```bash
    python3 create_subscription.py
    ```
    
5. 서브스크립션 탭 클릭 후 `obj-subscription` 서브스크립션 생성 확인

---

## 3. REST API를 활용한 메시지 송수신

1. `traffic-generator-1` 터미널 창에서 아래 명령어 실행
    
    #### **lab1-3-1**
    
    ```bash
    cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
    ```
    
2. `traffic-generator-1`에서 `test-topic`으로 메시지 전송
    - 메시지 전송 스크립트 실행 후 메시지를 입력하고, `Enter` 후 `Ctrl+D` 키로 전송 완료
    
        #### **lab1-3-2-1**
        
        ```bash
        python3 pub_sub_send.py
        ```
        
        #### **lab1-3-2-2**
        
        ```bash
        Publish a message to the test-topic in Pub/Sub using the REST API
        ```
    
3. `test-topic`의 메시지를 `test-pull-sub`서브스크립션을 통해 `traffic-generator-2`에서 수신
    - 메시지 수신 스크립트 실행하여 `traffic-generator-2` 터미널에서 메시지가 정상적으로 수신되는지 확인 후 `Ctrl` + `C` 키로 종료
    
        #### **lab1-3-3**
        
        ```bash
        python3 restapi_pull_sub.py
        ```

4. 웹 브라우저 주소창에 아래 URL 입력

    #### **lab1-3-5**
    ```
    http://{복사해둔 ALB Public IP 주소}/push-messages
    ```
        
5. `test-push-sub`서브스크립션에서 송신한 메시지 확인
    - **Note**: 메시지가 보이지 않을 경우 전송에 시간이 걸릴 수 있으므로 잠시 대기 후 다시 시도
      

---

## 4. Go SDK를 활용한 메시지 송수신

1. `traffic-generator-1` 터미널 창에서 아래 명령어를 실행하여 Go SDK 실습용 디렉터리로 이동
    
    #### **lab1-4-1**
    
    ```bash
    cd /home/ubuntu/gosdk/cmd
    ```
        
2. Publisher 실행 파일 생성
        
    #### **lab1-4-2**
    
    ```bash
    go build -o publisher config.go publisher.go
    ```
        
3. Publisher 실행 파일을 이용해 `traffic-generator-1`에서 `test-topic`으로 메시지 송신
    - 아래 명령어를 이용하여 Publisher 실행 파일 실행 후 송신할 메세지를 입력하고, `Enter`로 송신 및 `Ctrl` + `c`로 종료
    
        #### **lab1-4-1-3-1**
        
        ```bash
        ./publisher
        ```

        #### **lab1-4-1-3-2**
        
        ```bash
        Publish a message to the test-topic in Pub/Sub using the Go SDK
        ```
        
        
4. `traffic-generator-2` 터미널 창에서 아래 명령어를 실행하여 Go SDK 실습용 디렉터리로 이동
        
    #### **lab1-4-2-4**
    
    ```bash
    cd /home/ubuntu/gosdk/cmd
    ```
        
5. Subscriber 실행 파일 생성
        
    #### **lab1-4-2-5**
    
    ```bash
    go build -o subscriber config.go subscriber.go
    ```
        
6. Subscriber 실행 파일을 이용하여 `test-topic`의 메시지를 `test-pull-sub`서브스크립션을 통해 `traffic-generator-2`에서 수신
    - `traffic-generator-2` 터미널에서 메시지가 정상적으로 수신되는지 확인 후 `Ctrl` + `C` 키로 종료
        
        #### **lab1-4-2-6**
        
        ```bash
        ./subscriber
        ```
            

---

## 5. Object Storage에 NGINX 로그 적재
1. `traffic-generator-1` 터미널 창에서 아래 명령을 실행하여 VM1 디렉터리로 이동
    
    #### **lab1-5-1**
    
    ```bash
    cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM1
    
    ```
2. `traffic-generator-1`에서 트래픽 로그 생성
    - 트래픽 로그가 자동으로 생성되어 NGINX 로그에 반영됨
    
    #### **lab1-5-2**
    
    ```bash
    python3 traffic_generator.py
    ```
    
3. 실행 완료 후, 생성된 로그 확인
    
    #### **lab1-5-3**
    
    ```bash
    cat traffic_generator.log
    ```
    
4. 웹 브라우저 주소창에 아래 URL 입력

    #### **lab1-5-4**
    
    ```
    http://{복사해둔 ALB Public IP 주소}
    ```

5. 사용자 등록, 상품 목록 확인 등을 수행하여 로그 생성
4. 카카오 클라우드 콘솔에서 `pubsub-nginx-log` 버킷에 쌓인 NGINX 로그 확인
    - **카카오 클라우드 콘솔 > 전체 서비스 > Beyond Storage Service > Object Storage**
    - `pubsub-nginx-log` 버킷 클릭
    - 해당 날짜(년/월/일) 디렉터리로 이동하여 생성된 log 파일 확인
