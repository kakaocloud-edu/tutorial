# Pub/Sub 기반 실시간 메시징 및 로그 적재

Pub/Sub을 활용한 메시지 송수신, REST API 및 Go SDK를 활용하여 메시지 처리, Object Storage로의 NGINX 로그 적재를 다루는 실습입니다. 이를 통해 실시간 데이터 스트리밍과 로그 수집 및 저장 자동화 과정을 학습합니다.

---
## 1. 콘솔을 통한 메시징 리소스 생성

1. 카카오 클라우드 콘솔 > Analytics > Pub/Sub
2. 토픽 서비스 시작하기
   - 시작하기 버튼 클릭
   - **Note**: Lab02 실습 환경 구조
    ![image](https://github.com/user-attachments/assets/c0c3ba47-c82c-4552-88b5-f9e282913c04)

4. `test-topic` 토픽 생성
    - 토픽 생성 버튼 클릭
        - 이름: `test-topic`
        - 기본 서브스크립션: `생성 안함`
        - 토픽 메시지 보존 기간: `0일 0시 10분`
        - 설명: `빈 칸`
    - 생성 버튼 클릭
5. `test-topic` 토픽 생성 확인
<img width="3195" height="475" alt="image" src="https://github.com/user-attachments/assets/672b699d-92c5-4209-af35-48d3b80a14bd" />



6. 서브스크립션 탭 클릭 후 `test-topic`의 Pull 서브스크립션 생성
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
        - 메시지 전송 방식 : `기본 전송 방식`
        - 서브스크립션 메시지 보존 기간: `0일 0시 10분`
        - 응답 대기 시간: `20초`
        - 재처리 횟수: `횟수 지정`, `3번`
    - 생성 버튼 클릭
9. `test-push-sub` 생성 확인
![3](https://github.com/user-attachments/assets/1efd6aa5-0d21-4cbe-9a59-854ee06b91ba)



## 2. REST API를 통한 메시징 리소스 생성

1. `traffic-generator-1` 터미널에서 Pub/Sub 실습 디렉토리로 이동
    
    #### **lab2-2-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/pubsub/
    ```
    
2. NGINX 로그 적재용 토픽 생성
   - **Note**: [`create_topic.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/pubsub/create_topic.py)
    
    #### **lab2-2-2**
    
    ```bash
    python3 create_topic.py
    ```
    
3. 카카오 클라우드 콘솔 > Analytics > Pub/Sub
4. `log-topic` 토픽 생성 확인
![4](https://github.com/user-attachments/assets/1bd82237-d002-4e7f-a232-df79266970d2)

5. `traffic-generator-1` 터미널에서 서브스크립션 생성
    
    #### **lab2-2-5**
   - **Note**: [`create_subscription.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/pubsub/create_subscription.py)
    ```bash
    python3 create_subscription.py
    ```
    
6. 서브스크립션 탭 클릭 후 `log-obj-sub` 서브스크립션 생성 확인
![5](https://github.com/user-attachments/assets/03b45751-81c2-492c-ab98-7aad6dde8b97)

## 3. REST API를 통한 메시지 송수신

1. `traffic-generator-1` 터미널에서 `test-topic`으로 메시지를 전송하는 스크립트 실행
   - **Note**: [`pub_sub_publisher.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/pubsub/pub_sub_publisher.py)
    #### **lab2-3-1**
    
    ```bash
    python3 pub_sub_publisher.py
    ```

2. 송신할 메시지 입력
        
    #### **lab2-3-2**
    - **Note**: 아래 값은 하나의 예시이며 다른 값도 입력 가능합니다.
        
    ```bash
    Publish a message to the test-topic in Pub/Sub using the REST API
    ```
      ![스크린샷 2025-03-15 141538](https://github.com/user-attachments/assets/b7686dc7-9af1-468c-9e1b-4d4df792b53e)

3. `Enter`를 눌러 송신 완료

- `Ctrl` + `c`로 메세지 수신 스크립트 실행 종료
    
4. `traffic-generator-2` 터미널에서 Pub/Sub 실습 디렉토리로 이동
    
    #### **lab2-3-4**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/pubsub/
    ```

5. `traffic-generator-2` 터미널에서 `test-topic`의 메시지를 `test-pull-sub` 서브스크립션을 통해 메시지 수신
   - **Note**: [`pub_sub_subscriber.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/pubsub/pub_sub_subscriber.py)
    #### **lab2-3-5**
        
    ```bash
    python3 pub_sub_subscriber.py
    ```
      ![image](https://github.com/user-attachments/assets/de6e6265-0d32-495b-8074-82635dd4f94f)


6. `Ctrl` + `c`로 메시지 수신 스크립트 실행 종료


7. LoadBalancer의 Public IP가 포함된 URL로  웹브라우저에 접속
    #### **lab2-3-7**

    ```
    http://{ALB Public IP 주소}/push-messages
    ```
        
8. `test-topic`에 게시된 메시지를 `test-push-sub` 서브스크립션을 통해 `api-server-vm`으로 송신된 메시지 확인
   
    ![image](https://github.com/user-attachments/assets/8dd35cf9-7eee-4b41-8e50-6f79c6ac2635)



## 4. Go SDK를 통한 메시지 송수신

1. `traffic-generator-1` 터미널에서 GO 실습 디렉토리로 이동
    
    #### **lab2-4-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/go/
    ```
        
2. 메시지를 발행하는 publisher 파일 생성
   - **Note**: [`go_publisher.go`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/go/go_publisher.go)
    #### **lab2-4-2**
    
    ```bash
    go build -o publisher config.go go_publisher.go
    ```
        
3. `test-topic`으로 메시지 송신하는 publisher 파일 실행
    
    #### **lab2-4-3**
        
    ```bash
    ./publisher
    ```

4. 송신할 메시지를 입력 후 `Enter`

    #### **lab2-4-4**
    - **Note**: 아래 값은 하나의 예시이며 다른 값도 입력 가능합니다.
        
    ```bash
    Publish a message to the test-topic in Pub/Sub using the Go SDK
    ```
      ![스크린샷 2025-03-15 141538](https://github.com/user-attachments/assets/55fdb394-75e1-4c1e-b3b1-154ef794c0a9)

5. `Ctrl` + `c`로 publisher 파일 종료

6. `traffic-generator-2` 터미널에서 GO 실습 디렉토리로 이동
        
    #### **lab2-4-6**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/go/
    ```
        
7. 메시지를 수신하는 subscriber 파일 생성
   - **Note**: [`go_subscriber.go`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/go/go_subscriber.go)

    #### **lab2-4-7**
    
    ```bash
    go build -o subscriber config.go go_subscriber.go
    ```
        
8. subscriber 실행 파일을 실행하여 `test-topic`의 메시지를 `test-pull-sub`서브스크립션을 통해 `traffic-generator-2`에서 수신
        
    #### **lab2-4-8**
        
    ```bash
    ./subscriber
    ```
   ![11](https://github.com/user-attachments/assets/7051f257-485b-49a7-bd24-301824d72542)

9. `Ctrl` + `c`로 subscriber 파일 종료


## 5. Object Storage에 NGINX 로그 적재
> 아래와 같은 과정으로 nginx 로그가 Object Storage에 적재가 됩니다.
> 이 파이프라인은 Nginx 서버에서 발생한 접근 로그와 에러 로그를
> Filebeat를 통해 Logstash로 전달하고,  
> Logstash가 로그를 가공(Base64 인코딩)하여 KakaoCloud Pub/Sub 토픽으로 전송하는 구조입니다.
> 
> - **[Filebeat 설정 파일](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/filebeat.yml)**: `/var/log/nginx/*.log` 파일을 실시간 수집  
> - **[Logstash 설정 파일](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/logs-to-pubsub.conf)**: Filebeat로부터 받은 로그를 Pub/Sub HTTP API로 게시  
> - **Pub/Sub**: 수신된 로그 메시지를 Topic 단위로 저장 및 전달

1. `traffic-generator-1` 터미널에서 Pub/Sub 실습 디렉토리로 이동
    
    #### **lab2-5-1**
    
    ```bash
    cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/pubsub/
    ```

2. `traffic-generator-1`에서 트래픽 로그를 생성
   - **Note**: [`traffic_generator.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab02/pubsub/traffic_generator.py)

    #### **lab2-5-2**
    
    ```bash
    nohup python3 /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/pubsub/traffic_generator.py --mode continuous > /dev/null 2>&1 &
    ```
    
3. 실행 후 새로 생성된 `traffic_generator.log` 로그 파일 확인

    #### **lab2-5-3**
    
    ```bash
    cat /home/ubuntu/DataAnalyzeCourse/src/day1/Lab02/pubsub/traffic_generator.log
    ```
    ![그림1](https://github.com/user-attachments/assets/18a43d5b-61c5-4812-b2eb-3788357c2890)

4. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
5. `pubsub-log-bucket` 버킷 클릭
6. 현재 연도/월/일/시 디렉터리로 이동하여 생성된 NGINX 로그 확인
   ![16](https://github.com/user-attachments/assets/50308a92-97e5-4325-b620-5ceb457ddd37)
