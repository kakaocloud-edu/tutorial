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


## 3. Superset 접속 후 실시간 데이터 시각화 생성

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
10. 
