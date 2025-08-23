# Monitoring Flow

Monitoring Flow를 이용하여 로드밸런서, API 서버, Hadoop 클러스터 등을 모니터링하는 실습입니다.

## 1. 퍼블릭 가용성 모니터링 (without Flow Connection)
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


## 2. 내부 자원 헬스체크 (Flow Connection 사용)
1. 좌츨 플로우 커넥션 탭 클릭
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


## 3. 쇼핑몰 API 서버 다수 Endpoint 시나리오 체크
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


## 4. 멀티 타깃 모니터링 (For + JSON List)

**목표**: 여러 API 서버를 하나의 시나리오에서 반복 점검.

### Default Variable
```yaml
END_POINTS = ["{api-server-1의 private IP}", "{api-server-2의 private IP}"]   # JSON List
TARGET_IP  = ""   # String
```

### 스텝
1. **FOR Loop**
   - foreach: `END_POINTS`
   - marker → `TARGET_IP`
2. **하위 API 호출**
   - GET `http://${TARGET_IP}` (Expected Code: 200)

**성공 기준**
- 모든 엔드포인트 정상 응답 시 `Succeeded`
