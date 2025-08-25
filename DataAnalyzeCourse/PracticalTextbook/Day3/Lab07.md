# Monitoring Flow


## 1. 쇼핑몰 API 서버 다수 Endpoint 시나리오 체크
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


## 2. 멀티 타깃 모니터링
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
