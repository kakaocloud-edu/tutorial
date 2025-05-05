# Hadoop Eco의 Dataflow, Druid, Superset을 통한 실시간  데이터 시각화

Hadoop Eco의 Dataflow 유형을 통해 Druid, Superset을 이용하여 실시간 데이터를 그래프 등으로 시각화하는 실습입니다.

---
## 1. Hadoop Eco의 Dataflow 유형 마스터, 워커 노드 생성

1. 카카오 클라우드 콘솔 > Analytics > Hadoop Eco
2. 클러스터 생성 클릭
   - 클러스터 이름: `hadoop-dataflow`
   - 클러스터 구성
      - 클러스터 버전: `Hadoop Eco 2.1.0 (Ubuntu 22.04, Core Hadoop, HBase, Trino, Dataflow)`
      - 클러스터 유형:  `Dataflow`
      - 클러스터 가용성:
         - 클러스터 고가용성 (HA) 선택: `안 함`
   - 관리자 설정
      - 관리자 아이디: `admin`
      - 관리자 비밀번호: `Admin1234!`
      - 관리자 비밀번호 확인: `Admin1234!`
   - VPC 설정
      - VPC: `kc-vpc`
      - 서브넷: `kr-central-2-a의 Public 서브넷`
   - 보안 그룹 설정: `새 보안 그룹 생성`
   - 다음 버튼 클릭
   - 마스터 노드 설정
      - 마스터 노드 인스턴스 개수: `1`
      - 마스터 노드 인스턴스 유형: `m2a.xlarge`
      - 디스크 볼륨 크기: `50GB`
   - 워커 노드 설정
      - 워커 노드 인스턴스 개수: `2`
      - 워커 노드 인스턴스 유형: `m2a.xlarge`
      - 디스크 볼륨 크기: `100GB`
   - 총 YARN 사용량: `6`
   - 키 페어: lab01에서 생성한 `keypair`
   - 사용자 스크립트 (선택): `빈 칸`
   - 다음 버튼 클릭
   - 모니터링 에이전트 설치: `설치 안 함`
   - 서비스 연동: `연동하지 않음`
   - HDFS 설정
      - HDFS 블록 크기: `128MB`
      - HDFS 복제 개수: `2`
   - 클러스터 구성 설정 (선택): `빈 칸`
   - 로그 저장 설정: `미사용`
   - Kerberos 설치: `설치 안 함`
   - Ranger 설치:`설치 안 함`
   - 생성 버튼 클릭
3. hadoop-dataflow `Running` 상태 확인
4. hadoop-dataflow 클릭 후 보안 그룹 클릭
5. 인바운드 규칙 관리 클릭
   - 아래 인바운드 규칙 추가

   | 프로토콜 | 패킷 출발지   | 포트 번호 | 정책 설명  |
   | -------- | ------------- | --------- | ---------- |
   | TCP      | 0.0.0.0/0     | 3008      | Druid      |
   | TCP      | 0.0.0.0/0     | 4000      | Superset   |
   | TCP      | 0.0.0.0/0     | 9092      | Kafka      |


## 2. Druid 접속 후 Kafka와 연결하여 데이터 연동

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. HadoopMST-hadoop-dataflow-1, HadoopWRK-hadoop-dataflow-1, HadoopWRK-hadoop-dataflow-2 상태 Active 확인
3. HadoopMST-hadoop-dataflow-1에 Public IP 연결
   - 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
   - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
   - 확인 버튼 클릭
4. Druid에 접속
   - HadoopMST-hadoop-dataflow-1의 Public IP 복사
   - 웹페이지에 `http://{MASTER_NODE_PUBLIC_IP}:3008` 입력 후 이동
5. Druid에 Apache Kafka 연동
   - Druid 화면의 상단의 Load Data 탭 클릭 후 Streaming 탭 클릭
   - `Start a new streaming spec` 클릭 후 `Apache Kafka` 선택, `Connect data` 버튼 클릭
   - Kafka 연결 단계에서 연결할 Kafka 클러스터 및 토픽 정보 설정
      - Bootstrap servers: `Day1 lab03에서 생성한 부트스트랩 서버 입력`
      - Topic: `nginx-topic`
      - Apply 버튼 클릭
   - Next: Parse data 버튼 클릭
   - Next: Parse time 버튼 클릭
   - Next: Transfrom 버튼 클릭
   - Next: Filter 버튼 클릭
   - Next: Configure schema 버튼 클릭
   - Next: Partition 버튼 클릭
   - Segment granularity: `all` 선택 후 Next: Tune 버튼 클릭
   - Use earliest offset: `True` 선택 후 Next: Publish 버튼 클릭
   - Next: Edit spec 버튼 클릭
   - Submit 버튼 클릭
6. Druid 화면의 상단의 Ingestion 탭 클릭 후 nginx-topic `RUNNING` 상태 확인
7. Druid 화면의 상단의 Datasources 탭 클릭 후 nginx-topic의 Availability가 `Fully available` 상태 확인


## 3. Superset 접속 후 DATASET과 DASHBOARD 설정

1. Superset에 접속
   - HadoopMST-hadoop-dataflow-1의 Public IP 복사
   - 웹페이지에 `http://{MASTER_NODE_PUBLIC_IP}:4000` 입력 후 이동
2. Hadoop Eco 생성 시 입력했던 ID와 비밀번호로 로그인
   - ID: `admin`
   - PW: `Admin1234!`
3. 상단 메뉴의 Datasets 버튼 클릭
4. `+ DATASET` 버튼 클릭
5. DATASET 설정
   - DATABASE: `druid`
   - SCHEMA: `druid`
   - Select database table: `nginx-topic`
   - `CREATE DATASET AND CREATE CHART` 클릭
6. 상단 메뉴의 Datasets 버튼 클릭 후 생성된 `nginx-topic` 확인
7. 상단 메뉴의 Dashboards 버튼 클릭
8. `+ DASHBOARD` 버튼 클릭
9. DASHBOARD 설정
   - 좌측 상단의 [untitled dashboard] 삭제 후 `실시간 시각화` 입력
   - 우측 상단의 `SAVE` 버튼 클릭


## 4. Superset에서 실시간 데이터 시각화 생성

1. 상단 메뉴의 Datasets 버튼 클릭
2. `nginx-topic` Dataset의 Actions 항목 중 Edit 아이콘 클릭
3. METRICS 탭 클릭 후 추가
   - `+ ADD ITEM` 버튼 클릭
   - Metric 추가

| Metric                   | SQL expression                                                                                                                                                                                                                                                                                                                   | 설명                                                 |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Avg Response Time (ms)   | `AVG((CAST(request_time AS DOUBLE) + CAST(upstream_response_time AS DOUBLE)) * 1000)`                                                                                                                                                                                                                                            | 평균 총 응답 시간                                         |
| Error Rate %             | `SUM(CASE WHEN CAST(status AS INT) BETWEEN 400 AND 599 THEN 1 ELSE 0 END) / COUNT(*) * 100`                                                                                                                                                                                                                                      | 오류 비율(%)                                           |
| Cart Add Rate            | `CASE WHEN SUM(CASE WHEN endpoint = '/product' THEN 1 ELSE 0 END) = 0 THEN 0 ELSE SUM(CASE WHEN endpoint = '/cart/add' THEN 1 ELSE 0 END) * 1.0 / SUM(CASE WHEN endpoint = '/product' THEN 1 ELSE 0 END) END`                                                                                                                    | 전체 조회 대비 장바구니에 담긴 비율                               |
| View Count               | `SUM(CASE WHEN endpoint = '/product' THEN 1 ELSE 0 END)`                                                                                                                                                                                                                                                                         | 상품 페이지(/product)가 조회된 총 횟수                         |
| Order Count              | `SUM(CASE WHEN endpoint = '/checkout' THEN 1 ELSE 0 END)`                                                                                                                                                                                                                                                                        | 체크아웃(/checkout)이 완료된 총 횟수                          |
| Popularity Score         | `SUM(CASE WHEN endpoint = '/product' THEN 1 ELSE 0 END) + SUM(CASE WHEN endpoint = '/checkout' THEN 1 ELSE 0 END)`                                                                                                                                                                                                               | 조회 횟수와 주문 횟수를 합산한 값                                |
| Purchase Conversion Rate | `CASE WHEN SUM(CASE WHEN endpoint = '/product' THEN 1 ELSE 0 END) = 0 THEN 0 ELSE SUM(CASE WHEN endpoint = '/checkout' THEN 1 ELSE 0 END) * 1.0 / SUM(CASE WHEN endpoint = '/product' THEN 1 ELSE 0 END) END`                                                                                                                    | /product 엔드포인트 수 대비 /checkout 전환율                  |
| Signup Rate              | `CASE WHEN COUNT(DISTINCT CASE WHEN user_id IS NULL OR TRIM(user_id) = '' THEN session_id END) = 0 THEN 0 ELSE COUNT(DISTINCT CASE WHEN endpoint = '/add_user' AND (user_id IS NULL OR TRIM(user_id) = '') THEN session_id END) * 1.0 / COUNT(DISTINCT CASE WHEN user_id IS NULL OR TRIM(user_id) = '' THEN session_id END) END` | 익명 세션 대비 회원가입 전환율                                  |
| Login Conversion Rate    | `CASE WHEN COUNT(DISTINCT CASE WHEN user_id IS NULL OR TRIM(user_id) = '' THEN session_id END) = 0 THEN 0 ELSE COUNT(DISTINCT CASE WHEN endpoint = '/login' AND (user_id IS NULL OR TRIM(user_id) = '') THEN session_id END) * 1.0 / COUNT(DISTINCT CASE WHEN user_id IS NULL OR TRIM(user_id) = '' THEN session_id END) END`    | 익명 세션 대비 로그인 전환율                                   |
| Delayed Request Ratio    | `CASE WHEN COUNT(*) = 0 THEN 0 ELSE SUM(CASE WHEN upstream_response_time > request_time THEN 1 ELSE 0 END) * 1.0 / COUNT(*) END`                                                                                                                                                                                                 | request\_time 대비 upstream\_response\_time이 큰 요청 비율 |

- SAVE 버튼 클릭

4. CALCULATED COLUMNS 탭 클릭 후 추가
   - `+ ADD ITEM` 버튼 클릭
   - Column 추가

| Column        | SQL expression                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Data Type |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| user_type     | <code>CASE<br>WHEN user_id IS NULL OR TRIM(user_id) = '' THEN 'Anonymous'<br>ELSE 'Logged In'<br>END</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | STRING    |
| search_term   | <code>REGEXP_EXTRACT(query_params, 'query=([^&]+)', 1)</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | STRING    |
| all_statuses  | <code>CONCAT('All','')</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | STRING    |
| product_name  | <code>CASE<br>WHEN product_id = '101' THEN 'Wireless Earbuds'<br>WHEN product_id = '102' THEN 'Bluetooth Speaker'<br>WHEN product_id = '103' THEN 'Sneakers'<br>WHEN product_id = '104' THEN 'Backpack'<br>WHEN product_id = '105' THEN 'Coffee Mug'<br>WHEN product_id = '106' THEN 'Gaming Mouse'<br>WHEN product_id = '107' THEN 'Sunglasses'<br>WHEN product_id = '108' THEN 'Laptop Stand'<br>WHEN product_id = '109' THEN 'Gaming Keyboard'<br>WHEN product_id = '110' THEN 'Game Console'<br>WHEN product_id = '111' THEN 'Python Programming Book'<br>WHEN product_id = '112' THEN 'Science Fiction Novel'<br>WHEN product_id = '113' THEN 'Fashionable Hat'<br>WHEN product_id = '114' THEN 'Air Fryer'<br>WHEN product_id = '115' THEN 'Vacuum Cleaner'<br>WHEN product_id = '116' THEN 'Coffee Machine'<br>WHEN product_id = '117' THEN 'Jeans'<br>WHEN product_id = '118' THEN 'Smartphone'<br>WHEN product_id = '119' THEN 'Tablet'<br>WHEN product_id = '120' THEN 'Dress'<br>WHEN product_id = '121' THEN 'Gaming Headset'<br>WHEN product_id = '122' THEN 'Cookbook'<br>WHEN product_id = '123' THEN 'Thriller Novel'<br>WHEN product_id = '124' THEN 'T-Shirt'<br>END</code> | STRING    |
| login_status  | <code>CASE<br>WHEN endpoint = '/login' AND (user_id IS NULL OR TRIM(user_id) = '') THEN 'Logged In'<br>WHEN (user_id IS NULL OR TRIM(user_id) = '') THEN 'Not Logged In'<br>END</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | STRING    |


