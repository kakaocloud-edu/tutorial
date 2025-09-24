# 사전 환경 구성
사전 환경 구성에 대한 실습입니다.

## 1. Hadoop Eco 클러스터 생성
1. 카카오 클라우드 콘솔 > Analytics > Hadoop Eco
2. 클러스터 생성 버튼 클릭
    - 클러스터 이름: `hadoop-eco`
    - 클러스터 구성
        - 클러스터 가용성: `클러스터 고가용성 (HA) 선택 안 함`
        - 클러스터 버전: `Hadoop Eco 2.2.0 (Ubuntu 22.04)`
        - 클러스터 번들: `커스텀 번들`
            - `Druid 25.0.0`
            - `Spark 3.5.2`
            - `Tez 0.10.2`
            - `Hive 3.1.3`
            - `Hue 4.11.0`
            - `Superset 2.1.1`
    - 관리자 설정
        - 관리자 아이디: `admin`
        - 관리자 비밀번호: `Admin1234!`
        - 관리자 비밀번호 확인: `Admin1234!`
    - VPC 설정
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
    - 다음 버튼 클릭
    - 마스터 노드 설정
        - 마스터 노드 인스턴스 개수: `1`
        - 마스터 노드 인스턴스 유형: `m2a.xlarge`
        - 디스크 볼륨 크기: `50GB`
    - 워커 노드 설정
        - 워커 노드 인스턴스 개수: `2`
        - 워커 노드 인스턴스 유형: `m2a.4xlarge`
        - 디스크 볼륨 크기: `100GB`
    - 키 페어: lab00에서 생성한 `keypair`
    - 사용자 스크립트 (선택): [스크립트 사이트](http://210.109.54.80/) 에서 다운로드 후 업로드
        - Hadoop Configuration 생성 탭 클릭
        - 리소스 값 입력 후 사용자 스크립트 다운로드 클릭
        - 스크립트 업로드 클릭 후 다운로드 된 스크립트 선택
    - 다음 버튼 클릭
    - 모니터링 에이전트 설치: `설치 안 함`
    - 외부 저장소 연동
        - Hive 메타 저장소: `Data Catalog 연동`
            - 카탈로그 이름: `data_catalog`
        - Superset 캐시 저장소: `연동하지 않음`
    - HDFS 설정
        - HDFS 블록 크기: `128MB`
        - HDFS 복제 개수: `2`
    - 클러스터 구성 설정 (선택): [스크립트 사이트](http://210.109.54.80/) 를 활용하여 사용자 스크립트 생성 가능
        - 자신의 환경 변수에 맞게 수정 후 삽입
        - **클러스터 구성 설정 파일**
            
            ```sql
            {
                "configurations":
                [
                    {
                        "classification": "core-site",
                        "properties":
                        {
                            "fs.swifta.service.kic.credential.id": "credential_id",
                            "fs.swifta.service.kic.credential.secret": "credential_secret",
                            "fs.s3a.access.key": "access_key",
                            "fs.s3a.secret.key": "secret_key",
                            "fs.s3a.buckets.create.region": "kr-central-2",
                            "fs.s3a.endpoint.region": "kr-central-2",
                            "fs.s3a.endpoint": "objectstorage.kr-central-2.kakaocloud.com",
                            "s3service.s3-endpoint": "objectstorage.kr-central-2.kakaocloud.com"
                        }
                    }
                ]
            }
            ```
            
    - 로그 저장 설정: `미사용`
    - Kerberos 설치: `설치 안 함`
    - Ranger 설치:`설치 안 함`
    - 생성 버튼 클릭
3. hadoop-eco 클러스터 `Running` 상태 확인
4. hadoop-eco 클러스터 클릭 후 보안 그룹 클릭
5. 인바운드 규칙 관리 클릭
6. 아래 인바운드 규칙 추가
    
    
    | **프로토콜** | **출발지** | **포트 번호** | **정책 설명** |
    | --- | --- | --- | --- |
    | TCP | 0.0.0.0/0 | 3008 | Druid |
    | TCP | 0.0.0.0/0 | 4000 | Superset |
    | TCP | 0.0.0.0/0 | 9092 | Kafka |
    | TCP | 0.0.0.0/0 | 8081 | Schema Registry |
    | TCP | 0.0.0.0/0 | 8888 | Hue |
    | TCP | 0.0.0.0/0 | 22 | SSH |
