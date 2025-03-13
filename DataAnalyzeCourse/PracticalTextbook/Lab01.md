# Pub/Sub 기반 실시간 메시징 및 로그 적재

Pub/Sub을 활용한 메시지 송수신, REST API 및 Go SDK를 통한 메시지 처리, Object Storage로의 NGINX 로그 적재를 다루는 실습입니다. 이를 통해 실시간 데이터 스트리밍과 로그 수집 및 저장 자동화 과정을 학습합니다.

---
## 1. 콘솔을 통한 토픽, 서브스크립션 생성

1. 카카오 클라우드 콘솔 > Analytics > Pub/Sub > 토픽
2. 토픽 서비스 시작하기
![image](https://github.com/user-attachments/assets/c0c3ba47-c82c-4552-88b5-f9e282913c04)



3. `test-topic` 토픽 생성
    - 토픽 생성 버튼 클릭
        - 이름: `test-topic`
        - 기본 서브스크립션: `생성 안함`
        - 토픽 메세지 보존 기간: `0일 0시 10분`
        - 설명: `없음`
    - 생성 버튼 클릭
4. `test-topic` 토픽 생성 확인
![1](https://github.com/user-attachments/assets/4203487a-2ac8-46d2-9903-ab927b6b5809)

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
![2](https://github.com/user-attachments/assets/5c8f80c2-3c2d-4c17-8c95-a8c9b0cdb419)

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
9. `test-push-sub` 생성 확인
![3](https://github.com/user-attachments/assets/1efd6aa5-0d21-4cbe-9a59-854ee06b91ba)

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
4. `log-topic` 토픽 생성 확인
![4](https://github.com/user-attachments/assets/1bd82237-d002-4e7f-a232-df79266970d2)

5. Object Storage에 NGINX 로그를 적재하는 서브스크립션 생성을 위해 아래 명령어 실행
    
    #### **lab1-2-5**
    
    ```bash
    python3 create_subscription.py
    ```
    
6. 서브스크립션 탭 클릭 후 `log-obj-sub` 서브스크립션 생성 확인
![5](https://github.com/user-attachments/assets/03b45751-81c2-492c-ab98-7aad6dde8b97)

---
## 3. REST API를 활용한 메시지 송수신

1. `traffic-generator-1` 터미널 창에서 `test-topic`으로 메세지를 전송하는 스크립트 실행

    #### **lab1-3-1**
    
    ```bash
    python3 pub_sub_publisher.py
    ```

2. 송신할 메세지 입력
        
    #### **lab1-3-2**
    - **Note**: 아래 값은 하나의 예시이며 다른 값도 입력 가능합니다.
        
    ```bash
    Publish a message to the test-topic in Pub/Sub using the REST API
    ```

    - 아래와 같은 결과 확인
    ![image](https://github.com/user-attachments/assets/96ce2786-96f0-4fe2-a4a9-15e3c5eb8a11)

3. `Enter`를 두 번 눌러 송신 완료
    
4. `traffic-generator-2` 터미널 창에서 `Pub/Sub` 실습을 위한 디렉토리로 이동하기 위해 아래 명령어 실행
    
    #### **lab1-3-4**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub/
    ```

5. `traffic-generator-2` 터미널 창에서 `test-topic`의 메세지를 `test-pull-sub` 서브스크립션을 통해 수신하기 위한 아래 명령어 실행
    - 메시지 수신 스크립트 실행하여 `traffic-generator-2` 터미널에서 메시지가 정상적으로 수신되는지 확인
    #### **lab1-3-4**
        
    ```bash
    python3 pub_sub_subscriber.py
    ```
    ![image](https://github.com/user-attachments/assets/d7ffc9fa-12d2-4542-871c-abbb3abe5314)

6. `Ctrl` + `c`로 스크립트 실행 종료


7. 웹 브라우저 주소창에서 `test-topic`의 메세지를 `test-push-sub` 서브스크립션을 통해 `api-server-vm`으로 송신된 메세지를 확인하기 위한 아래 URL 입력
    #### **lab1-3-7**

    ```
    http://{ALB Public IP 주소}/push-messages
    ```
        
8. `test-push-sub` 서브스크립션에서 `api-server-vm`으로 송신한 메시지 확인
    - **Note**: 메시지가 보이지 않을 경우 전송에 시간이 걸릴 수 있으므로 잠시 대기 후 `F5` 키를 눌러 다시 시도
    ![image](https://github.com/user-attachments/assets/8c20c80f-aa9f-44eb-b5e1-1af5b2380556)

---

## 4. Go SDK를 활용한 메시지 송수신

1. `traffic-generator-1` 터미널 창에서  Go SDK 실습용 디렉터리로 이동하기 위한 아래 명령어를 실행
    
    #### **lab1-4-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/go/
    ```
        
2. 메세지를 발행하는 Publisher 실행 파일 생성
        
    #### **lab1-4-2**
    
    ```bash
    go build -o publisher config.go go_publisher.go
    ```
        
3. Publisher 실행 파일을 이용해 `traffic-generator-1`에서 `test-topic`으로 메시지 송신
    - 아래 명령어를 이용하여 Publisher 실행 파일 실행 후 송신할 메세지를 입력하고, `Enter`로 송신
    
    #### **lab1-4-3-1**
        
    ```bash
    ./publisher
    ```

    #### **lab1-4-3-2**
    - **Note**: 아래 값은 하나의 예시이며 다른 값도 입력 가능합니다.
        
    ```bash
    Publish a message to the test-topic in Pub/Sub using the Go SDK
    ```
    ![image](https://github.com/user-attachments/assets/ea2fa21b-810c-44a1-b8ef-e7f3d81876b6)
   
5. `Ctrl` + `c`로 종료

6. `traffic-generator-2` 터미널 창에서  Go SDK 실습용 디렉터리로 이동하기 위한 아래 명령어를 실행
        
    #### **lab1-4-4**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/go/
    ```
        
7. 메세지를 수신하는 Subscriber 실행 파일 생성
        
    #### **lab1-4-5**
    
    ```bash
    go build -o subscriber config.go go_subscriber.go
    ```
        
8. Subscriber 실행 파일을 이용하여 `test-topic`의 메시지를 `test-pull-sub`서브스크립션을 통해 `traffic-generator-2`에서 수신
    - 아래 명령어를 이용하여 Publisher 실행 파일 실행 후 메시지가 정상적으로 수신되는지 확인하고, `Ctrl` + `C` 키로 종료
        
    #### **lab1-4-6**
        
    ```bash
    ./subscriber
    ```

    - 아래와 같은 결과 확인
![10](https://github.com/user-attachments/assets/61df11c3-58a7-435a-aaf2-cefead9d4793)

---

## 5. Object Storage에 NGINX 로그 적재
1. `traffic-generator-1`에서 `pubsub` 디렉토리로 이동하기 위한 아래 명령어 실행
    
    #### **lab1-5-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/pubsub/
    
    ```

    - 로그 생성 전 디렉터리 구조 확인
    #### **lab1-5-1-2**
    ```
    ls
    ```

    - 아래와 같은 결과 확인
![11](https://github.com/user-attachments/assets/4d647d4a-f758-4240-8398-ee81ac008faa)

2. `traffic-generator-1`에서 트래픽 로그를 생성하는 `traffic_generator.py` 실행
    - **Note**: 트래픽 로그가 자동으로 생성되어 NGINX 로그에 반영됨
    
    #### **lab1-5-2**
    
    ```bash
    python3 traffic_generator.py
    ```
    
3. 실행 완료 후 생성된 로그 확인(2분)

    #### **lab1-5-3-1**
    
    ```bash
    ls
    ```
    - 로그 생성 후 디렉터리 구조에 `traffic_generator.log` 파일 생성 확인

    - 아래와 같은 결과 확인
    ![12](https://github.com/user-attachments/assets/ac9f69e5-7b1d-420c-8c1f-3bb00af428ad)

    #### **lab1-5-3-2**
    
    ```bash
    cat traffic_generator.log
    ```
    - 로그 생성 후 `traffic_generator.log` 파일 내부 확인

    - 아래와 같은 결과 확인
![13](https://github.com/user-attachments/assets/be5a3eef-3ed4-4e17-a59d-8000f0f82bcd)

4. 웹 브라우저 주소창에서 직접 로그를 발생시키기 위해 아래 URL 입력

    #### **lab1-5-4**
   
    ```
    http://{ALB Public IP 주소}
    ```

    ![14](https://github.com/user-attachments/assets/a3fff2b9-5d57-4c03-9e0e-805f6c8bd2d9)

5. 사용자 등록, 상품 목록 확인 등을 수행하여 로그 생성
6. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
    - 쌓인 로그를 확인하기 위한 `pubsub-nginx-log` 버킷 클릭
        - 현재 연도/월/일/시 디렉터리로 이동하여 생성된 NGINX 로그 확인

    - 아래와 같은 결과 확인
![15](https://github.com/user-attachments/assets/b8118722-f830-48c1-a0ec-28ea97a4c8b7)
![16](https://github.com/user-attachments/assets/50308a92-97e5-4325-b620-5ceb457ddd37)
