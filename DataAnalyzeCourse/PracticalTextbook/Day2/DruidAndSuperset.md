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

