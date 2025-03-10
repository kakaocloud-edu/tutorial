# Pub/Sub 기반 실시간 메시징 및 로그 적재

Pub/Sub을 활용한 메시지 송수신, REST API 및 Go SDK를 통한 메시지 처리, Object Storage로의 NGINX 로그 적재를 다루는 실습입니다. 이를 통해 실시간 데이터 스트리밍과 로그 수집 및 저장 자동화 과정을 학습합니다.

---
## 1. 콘솔을 통한 토픽, 서브스크립션 생성

1. 카카오 클라우드 콘솔 > Analytics > Pub/Sub > 토픽
2. 토픽 서비스 시작하기
- topic-subscription 사진 넣을 예정


3. `test-topic` 토픽 생성
    - 토픽 생성 버튼 클릭
        - 이름: `test-topic`
        - 기본 서브스크립션: `생성 안함`
        - 토픽 메세지 보존 기간: `0일 0시 10분`
        - 설명: `없음`
    - 생성 버튼 클릭
4. `test-topic` 토픽 생성 확인 (확인 부분 사진 넣을 예정)
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
7. `test-pull-sub` 서브스크립션 생성 확인(확인 부분 사진 넣을 예정)

8. `test-topic`의 Push 서브스크립션 생성
    - 서브스크립션 생성 버튼 클릭
        - 기본 설정
            - 이름: `test-push-sub`
            - 토픽 선택: `test-topic`
        - 유형: `Push`
            - 엔드포인트
              - 프로토콜: `http://`
              - 엔드 포인트 URL: `{ALB Public IP}/push-subscription`
        - 서브스크립션 메시지 보존 기간: `0일 0시 10분`
        - 응답 대기 시간: `20초`
        - 재처리 횟수: `횟수 지정`, `3번`
    - 생성 버튼 클릭
9. `test-push-sub` 생성 확인(확인 부분 사진 넣을 예정)

---

## 2. REST API를 통한 토픽, 서브스크립션 생성

1. `traffic-generator-1` 터미널 창에서 `Pub/Sub`실습을 위한 디렉토리로 이동하기 위해 아래 명령어 실행
    
    #### **lab1-2-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub/
    ```
    
2. NGINX 로그 적재용 토픽 생성을 위해 아래 명령어 실행
    
    #### **lab1-2-2**
    
    ```bash
    python3 create_topic.py
    ```
    
3. 카카오 클라우드 콘솔 > Analytics > Pub/Sub > 토픽
4. `log-topic` 토픽 생성 확인(확인 부분 사진 넣을 예정)

5. Object Storage에 NGINX 로그를 적재하는 서브스크립션 생성을 위해 아래 명령어 실행
    
    #### **lab1-2-5**
    
    ```bash
    python3 create_subscription.py
    ```
    
6. 서브스크립션 탭 클릭 후 `log-obj-sub` 서브스크립션 생성 확인(확인 부분 사진 넣을 예정)

---

## 3. Pub/Sub 디렉토리에 권한 부여

1. `traffic-generator-1, 2`에서 `pubsub` 디렉토리로 이동하기 위한 아래 명령어 실행
    - **Note**: `traffic-generator-1`은 이미 `pubsub` 디렉토리로 이동되어져 있음

    #### **lab1-3-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub/
    ```

2. `traffic-generator-1, 2`에서 `pubsub` 디렉토리에 권한 부여
    - **Note**: 모든 사용자에게 읽기/실행 권한, 소유자 및 그룹에게 쓰기 권한(775)을 부여

    #### **lab1-3-2**
    
    ```bash
    sudo chown ubuntu:ubuntu /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub
    ```
    ```bash
    sudo chmod 775 /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub
    ```
---

## 4. REST API를 활용한 메시지 송수신

1. `traffic-generator-1` 터미널 창에서 `test-topic`으로 메세지 전송하기 위한 아래 명령어 실행
    - 메시지 전송 스크립트 실행 후 메시지를 입력하고, `Enter` 후 `Ctrl+D` 키로 전송 완료

    #### **lab1-4-1-1**
    
    ```bash
    python3 pub_sub_publisher.py
    ```
        
    #### **lab1-4-1-2**
    - **Note**: 아래 값은 하나의 예시, 다른 값을 입력해도 무관
        
    ```bash
    Publish a message to the test-topic in Pub/Sub using the REST API
    ```

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)
    
2. `traffic-generator-2` 터미널 창에서 `test-topic`의 메세지를 `test-pull-sub` 서브스크립션을 통해 수신하기 위한 아래 명령어 실행
    - 메시지 수신 스크립트 실행하여 `traffic-generator-2` 터미널에서 메시지가 정상적으로 수신되는지 확인 후, `Ctrl` + `C` 키로 종료
    #### **lab1-4-2**
        
    ```bash
    python3 pub_sub_subscriber.py
    ```

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)

3. 웹 브라우저 주소창에서 `test-topic`의 메세지를 `test-push-sub` 서브스크립션을 통해 `api-server-vm`으로 송신된 메세지를 확인하기 위한 아래 URL 입력
    #### **lab1-4-3**

    ```
    http://{ALB Public IP 주소}/push-messages
    ```
        
4. `test-push-sub` 서브스크립션에서 `api-server-vm`으로 송신한 메시지 확인
    - **Note**: 메시지가 보이지 않을 경우 전송에 시간이 걸릴 수 있으므로 잠시 대기 후 다시 시도
    - **Note**: 새로고침(F5)을 여러 번 진행하여 메세지가 적재된 부분 확인

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)

---

## 5. Go SDK를 활용한 메시지 송수신

1. `traffic-generator-1` 터미널 창에서  Go SDK 실습용 디렉터리로 이동하기 위한 아래 명령어를 실행
    
    #### **lab1-5-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/go/
    ```
        
2. 메세지를 발행하는 Publisher 실행 파일 생성
        
    #### **lab1-5-2**
    
    ```bash
    go build -o publisher config.go go_publisher.go
    ```
        
3. Publisher 실행 파일을 이용해 `traffic-generator-1`에서 `test-topic`으로 메시지 송신
    - 아래 명령어를 이용하여 Publisher 실행 파일 실행 후 송신할 메세지를 입력하고, `Enter`로 송신 및 `Ctrl` + `c`로 종료
    
    #### **lab1-5-3-1**
        
    ```bash
    ./publisher
    ```

    #### **lab1-5-3-2**
    - **Note**: 아래 값은 하나의 예시, 다른 값을 입력해도 무관
        
    ```bash
    Publish a message to the test-topic in Pub/Sub using the Go SDK
    ```

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)
        
4. `traffic-generator-2` 터미널 창에서  Go SDK 실습용 디렉터리로 이동하기 위한 아래 명령어를 실행
        
    #### **lab1-5-4**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/go/
    ```
        
5. 메세지를 수신하는 Subscriber 실행 파일 생성
        
    #### **lab1-5-5**
    
    ```bash
    go build -o subscriber config.go go_subscriber.go
    ```
        
6. Subscriber 실행 파일을 이용하여 `test-topic`의 메시지를 `test-pull-sub`서브스크립션을 통해 `traffic-generator-2`에서 수신
    - 아래 명령어를 이용하여 Publisher 실행 파일 실행 후 메시지가 정상적으로 수신되는지 확인하고, `Ctrl` + `C` 키로 종료
        
    #### **lab1-5-6**
        
    ```bash
    ./subscriber
    ```

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)

---

## 6. Object Storage에 NGINX 로그 적재
1. `traffic-generator-1`에서 `pubsub` 디렉토리로 이동하기 위한 아래 명령어 실행
    
    #### **lab1-6-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub/
    
    ```

    - 로그 생성 전 디렉터리 구조 확인
    #### **lab1-6-1-2**
    ```
    ls
    ```

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)

2. `traffic-generator-1`에서 트래픽 로그를 생성하는 `traffic_generator.py` 실행
    - **Note**: 트래픽 로그가 자동으로 생성되어 NGINX 로그에 반영됨
    
    #### **lab1-6-2**
    
    ```bash
    python3 traffic_generator.py
    ```
    
3. 실행 완료 후 생성된 로그 확인

    #### **lab1-6-3-1**
    
    ```bash
    ls
    ```
    - 로그 생성 후 디렉터리 구조에 `traffic_generator.log` 파일 생성 확인

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)
    
    #### **lab1-6-3-2**
    
    ```bash
    cat traffic_generator.log
    ```
    - 로그 생성 후 `traffic_generator.log` 파일 내부 확인

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)    

4. 웹 브라우저 주소창에서 직접 로그를 발생시키기 위해 아래 URL 입력

    #### **lab1-6-4**
    
    ```
    http://{ALB Public IP 주소}
    ```

    - (실제 실습 부분 사진 넣을 예정)

5. 사용자 등록, 상품 목록 확인 등을 수행하여 로그 생성
6. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
    - 쌓인 로그를 확인하기 위한 `pubsub-nginx-log` 버킷 클릭
        - 현재 연도/월/일/시 디렉터리로 이동하여 생성된 NGINX 로그 확인

    - 아래와 같은 결과 확인(확인 부분 사진 넣을 예정)


---

