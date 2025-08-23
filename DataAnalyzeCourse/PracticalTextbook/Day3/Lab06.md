# Monitoring Flow

Monitoring Flow를 이용하여 로드밸런서, API 서버, Hadoop 클러스터 등을 모니터링하는 실습입니다.

## 1. 사용자 리소스 정보 조회
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `api-server-1`의 private IP 클립보드 등에 복사 붙여넣기
3. `api-server-2`의 private IP 클립보드 등에 복사 붙여넣기
4. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
5. `api-lb`의 Public IP 클립보드 등에 복사 붙여넣기
6. 카카오 클라우드 콘솔 > Analytics > Hadoop Eco
7. `hadoop-eco` 클릭
8. 클러스터 정보 클릭
9. `클러스터 ID` 클립보드 등에 복사 붙여넣기

## 2. 퍼블릭 가용성 모니터링
1. 카카오 클라우드 콘솔 > Management > Mornitoring Flow
2. 좌측 시나리오 탭 클릭
3. 시나리오 생성 버튼 클릭

   - 시나리오 이름: `lab1`
   - 플로우 커넥션(선택): `카카오클라우드 VPC를 활용 선택 안 함`
   - 스케줄:
      - `분 단위`
      - 실행 분: `1`

4. 생성 버튼 클릭
5. 생성된 `lab1` 시나리오 클릭
6. 시나리오 스텝 추가 버튼 클릭
7. 우측 상단의 `Default Variable 관리` 클릭

   - Key: `LB_IP`
   - Type: `String`
   - Value: `{Load Balancer의 public IP}`
      - 저장 버튼 클릭

8. 닫기 버튼 클릭
9. 새 스탭 설정의 유형 선택 클릭
10. API 클릭

   - 스텝
      - 스텝 이름: `LB_CHECK`
   - 요청
      - Expected Code: `200`
      - Method: `GET`
      - URL: `http://${LB_IP}`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers: `빈 칸`
      - Body: `빈 칸`

11. 테스트 진행 후 성공 확인
12. 저장 버튼 클릭
13. 실행 결과 탭 클릭 후 결과 확인


## 3. 내부 자원 헬스체크
1. 좌측 플로우 커넥션 탭 클릭
2. 플로우 커넥션 생성 버튼 클릭

   - 플로우 커넥션 이름: `flowconnection`
   - VPC: `kc-vpc`
   - 서브넷: `main`, `public`

3. 생성 버튼 클릭
4. 좌측 시나리오 탭 클릭
5. 시나리오 생성 버튼 클릭

   - 시나리오 이름: `lab2`
   - 플로우 커넥션(선택): `카카오클라우드 VPC를 활용 선택`
      - `flowconnection`
   - 연결 서브넷: `main`, `public`
   - 스케줄:
      - `분 단위`
      - 실행 분: `1`

6. 생성 버튼 클릭
7. 생성된 `lab2` 시나리오 클릭
8. 시나리오 스텝 추가 버튼 클릭
9. 우측 상단의 `Default Variable 관리` 클릭

   - Key: `API_IP`
   - Type: `String`
   - Value: `{api-server-1의 private IP}`
      - 저장 버튼 클릭
   - Key: `HADOOP_ID`
   - Type: `String`
   - Value: `{hadoop-eco kluster ID}`
      - 저장 버튼 클릭

10. 닫기 버튼 클릭
11. 새 스탭 설정의 유형 선택 클릭
12. API 클릭

   - 스텝
      - 스텝 이름: `API_CHECK`
   - 요청
      - Expected Code: `200`
      - Method: `GET`
      - URL: `http://${API_IP}`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers: `빈 칸`
      - Body: `빈 칸`

13. 좌측 상단 API 블럭에 다음 스텝 추가 클릭
14. 유형 선택 클릭
15. SLEEP 클릭

   - 스텝
      - 스텝 이름: `SLEEP`
      - 상태: `0`분 `10`초

16. 좌측 상단 SLEEP 블럭에 다음 스텝 추가 클릭
17. 유형 선택 클릭
18. API 클릭

   - 스텝
      - 스텝 이름: `HADOOP_CHECK`
   - 요청
      - Expected Code: `200`
      - Method: `GET`
      - URL: `https://hadoop-eco.kr-central-2.kakaocloud.com/v2/hadoop-eco/clusters/${HADOOP_ID}/vms`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers:
         - Key: `content-type`
         - Value: `application/json`
            - 저장 클릭
         - Key: `credential-id`
         - Value: `{IAM 액세스 키 ID}`
            - 저장 클릭
         - Key: `credential-secret`
         - Value: `{IAM 보안 액세스 키}`
            - 저장 클릭
      - Body: `빈 칸`

19. 테스트 진행 후 성공 확인
20. 저장 버튼 클릭
21. 실행 결과 탭 클릭 후 결과 확인


## 4. 쇼핑몰 API 서버 다수 Endpoint 시나리오 체크
1. 좌측 시나리오 탭 클릭
2. 시나리오 생성 버튼 클릭

   - 시나리오 이름: `lab3`
   - 플로우 커넥션(선택): `카카오클라우드 VPC를 활용 선택`
      - `flowconnection`
   - 연결 서브넷: `main`, `public`
   - 스케줄:
      - `분 단위`
      - 실행 분: `1`

3. 생성 버튼 클릭
4. 생성된 `lab3` 시나리오 클릭
5. 시나리오 스텝 추가 버튼 클릭
6. 우측 상단의 `Default Variable 관리` 클릭

   - Key: `LB_IP`
   - Type: `String`
   - Value: `{Load Balancer의 public IP}`
      - 저장 버튼 클릭

   - Key: `CATEGORY_NAME`
   - Type: `String`
   - Value: `Electronics`
      - 저장 버튼 클릭

   - Key: `USER_ID`
   - Type: `String`
   - Value: `u1`
      - 저장 버튼 클릭

7. 닫기 버튼 클릭
8. 새 스탭 설정의 유형 선택 클릭
9. API 클릭

   - 스텝
      - 스텝 이름: `CATEGORY`
   - 요청
      - Expected Code: `200`
      - Method: `GET`
      - URL: `http://${LB_IP}/categories`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers:
         - Key: `Accept`
         - Value: `application/json`
            - 저장 클릭
      - Body: `빈 칸`

10. 좌측 상단 API 블럭에 다음 스텝 추가 클릭
11. 유형 선택 클릭
12. API 클릭

   - 스텝
      - 스텝 이름: `PRODUCT`
   - 요청
      - Expected Code: `200`
      - Method: `GET`
      - URL: `http://${LB_IP}/category?name=${CATEGORY_NAME}`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers:
         - Key: `Accept`
         - Value: `application/json`
            - 저장 클릭
      - Body: `빈 칸`

13. 좌측 상단 API 블럭에 다음 스텝 추가 클릭
14. 유형 선택 클릭
15. API 클릭

   - 스텝
      - 스텝 이름: `LOGIN`
   - 요청
      - Expected Code: `200`
      - Method: `POST`
      - URL: `http://${LB_IP}/login`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers:
         - Key: `Content-Type`
         - Value: `application/x-www-form-urlencoded`
            - 저장 클릭
      - Body: `user_id=${USER_ID}`

16. 테스트 진행 후 성공 확인
17. 저장 버튼 클릭
18. 실행 결과 탭 클릭 후 결과 확인


## 5. 멀티 타깃 모니터링
1. 좌측 시나리오 탭 클릭
2. 시나리오 생성 버튼 클릭

   - 시나리오 이름: `lab4`
   - 플로우 커넥션(선택): `카카오클라우드 VPC를 활용 선택`
      - `flowconnection`
   - 연결 서브넷: `main`, `public`
   - 스케줄:
      - `분 단위`
      - 실행 분: `1`

3. 생성 버튼 클릭
4. 생성된 `lab4` 시나리오 클릭
5. 시나리오 스텝 추가 버튼 클릭
6. 우측 상단의 `Default Variable 관리` 클릭

   - Key: `END_POINTS`
   - Type: `JSON List`
   - Value: `["{api-server-1의 private IP}","{api-server-2의 private IP}"]`
      - 저장 버튼 클릭

   - Key: `TARGET_IP`
   - Type: `String`
   - Value: `""`
      - 저장 버튼 클릭

7. 닫기 버튼 클릭
8. 새 스탭 설정의 유형 선택 클릭
9. FOR 클릭

   - 스텝
      - 스텝 이름: `API_SERVERS_CHECK`
   - 상태
      - Type: `foreach`
      - Base Variable: `END_POINTS`
   - Markers
      - Marker Variable: `TARGET_IP`
      - Marker Value: `${marker}`
         - 저장 클릭

10. 좌측 상단 FOR 블럭에 하위 스텝 추가 클릭
11. 유형 선택 클릭
12. API 클릭

   - 스텝
      - 스텝 이름: `API_SERVER1`
   - 요청
      - Expected Code: `200`
      - Method: `GET`
      - URL: `http://${TARGET_IP}`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers: `빈 칸`
      - Body: `빈 칸`

13. 좌측 상단 FOR 블럭에 하위 스텝 추가 클릭
14. 유형 선택 클릭
15. API 클릭

   - 스텝
      - 스텝 이름: `API_SERVER2`
   - 요청
      - Expected Code: `200`
      - Method: `GET`
      - URL: `http://${TARGET_IP}`
      - Timeout: `3000`
      - Parameters: `빈 칸`
      - Headers: `빈 칸`
      - Body: `빈 칸`

16. 테스트 진행 후 성공 확인
17. 저장 버튼 클릭
18. 실행 결과 탭 클릭 후 결과 확인


## 6. Monitering Flow & Alert Center 장애 탐지 (8분)

1. 우측 상단 프로필 이미지 클릭 > 계정 정보
2. 계정 정보 내 이메일 주소 입력
    - **note :** 이메일 인증 필요
3. 카카오 클라우드 콘솔 > Management > Alert Center
4. 좌측 수신 채널 클릭
5. 수신 채널 생성 버튼 클릭
    - 수신 채널 이름 : `mf-email`
    - 메인 채널 유형 : `기본 채널` > `이메일` 선택
    - 수신자 유형
        - `사용자`
        - `{본인의 이메일}` 선택
    - 대체 채널: `미사용` 선택
    - 수신 채널 사용 여부 : `사용` 선택
    - 생성 버튼 클릭
6. 좌측 알림 정책 클릭
7. 알림 정책 생성 클릭
    - 1단계: 알림 조건 설정
        - 조건 유형 : `메트릭`
        - 서비스 : `Monitoring Flow`
        - 조건 설정
            - 메트릭 항목 : `Scenario Fail Count`
            - 리소스: `시나리오`, `lab2`
        - 임계치 : `1` , `count`, `이상`
        - 지속시간 : `1분`
        - 심각도 : `경고`
        - `다음` 버튼 클릭
    - 2단계: 수신 채널 설정
        - 채널 유형 : `이메일`
        - 수신 채널 : `mf-email`
        - `다음` 버튼 클릭
    - 3단계: 기본 정보 설정
        - 알림 정책 이름 : `mf-alert`
        - 알림 정책 설명 (선택) : `빈 칸`
        - 사용 여부 : `기본 체크 상태`
        - `다음` 버튼 클릭
    - 4단계: 검토
        - `설정 정보 확인`
        - `생성` 버튼 클릭
8. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
9. `api-server-1` 인스턴스 SSH 접속
    - `api-server-1` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력
      
       **lab6-5-9-1**
       ```
       cd {keypair.pem 다운로드 위치}
       ```
        
   - 리눅스의 경우 아래와 같이 키페어 권한 조정
        
     **lab6-5-9-2**
        
     ```
     chmod 400 keypair.pem
     ```
        
     **lab6-5-9-3**
        
     ```
     ssh -i keypair.pem ubuntu@{api-server-1의 public ip 주소}
     ```
     - **Note**: {api-server-1의 public ip 주소} 부분을 복사한 각 IP 주소로 교체
   
11. 장애를 발생시키기 위해 http 80 포트를 90초 동안 차단하는 명령어 실행
    
    ```
    sudo nohup bash -c '
      iptables -I INPUT -p tcp --dport 80  -j REJECT
      sleep 90
      iptables -D INPUT -p tcp --dport 80  -j REJECT
    ' >/tmp/http_drop.log 2>&1 &
    ```
    
12. 카카오 클라우드 콘솔 > Management > Monitoring Flow
13. `lab2` 시나리오 클릭
    - 실행 결과 탭 클릭
    - 1분 뒤 새로고침하여 상태가 `Failed` 인 행 확인
    - 다시 1분 뒤 새로고침하여 상태가 `Succeed`로 재전이 되었음을 확인
14. Alert Center 수신 채널에 등록한 이메일로 접속하여 Alert 메일 확인
