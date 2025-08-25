# Monitoring Flow

Monitoring Flow를 이용하여 로드밸런서, API 서버, Hadoop 클러스터 등을 모니터링하는 실습입니다.

## 1. 사용자 리소스 정보 조회
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `api-server-1`, `api-server-2` 의 private IP 클립보드 등에 복사 붙여넣기
3. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
4. `api-lb`의 Public IP 클립보드 등에 복사 붙여넣기
5. 카카오 클라우드 콘솔 > Analytics > Hadoop Eco
6. `hadoop-eco` 클릭
7. 클러스터 정보 클릭
8. `클러스터 ID` 클립보드 등에 복사 붙여넣기

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
   - Key: `HADOOP_NODE_LIST`
   - Type: `JSON List`
   - Value: `[]`
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

19. 좌측 상단 API 블럭에 다음 스텝 추가 클릭
20. 유형 선택 클릭
21. Set Variables 클릭

   - 스텝
      - 스텝 이름: `HADOOP_LIST_CHECK`
   - Parameters
      - Variable: `HADOOP_NODE_LIST`
      - Step: `HADOOP_CHECK` > `response` > `body`
      - Key: `content`
         - 저장 클릭

22. 테스트 진행 후 성공 확인
23. 저장 버튼 클릭
