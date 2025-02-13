# 사전 환경 구성

사전 환경 구성에 대한 실습입니다.


## 1. VPC 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > VPC 접속
2. VPC 만들기 버튼 클릭
    - VPC 정보
        - VPC 이름: `kc-vpc`
        - VPC IP CIDR 블록: `10.0.0.0/16`
    - Availability Zone
        - 가용 영역 개수: `1`
        - 첫 번째 AZ: `kr-central-2-a`
    - 서브넷 설정
        - 가용 영역당 퍼블릭 서브넷 개수: `1`
        - 가용 영역당 프라이빗 서브넷 개수: `1`
        - 퍼블릭 서브넷 IPv4 CIDR 블록: `10.0.0.0/20`
        - 프라이빗 서브넷 IPv4 CIDR 블록: `10.0.16.0/20`
3. 만들기 버튼 클릭
4. VPC 생성 확인


## 2. 로드 밸런서(ALB) 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Load Balancing > 로드 밸런서
2. 로드 밸런서 생성 버튼 클릭

    - 유형 선택: `Application Load Balancer`
    - 기본 정보
        - 로드 밸런서 이름: `api-lb`
        - 로드 밸런서 설명: `없음`
    - 네트워크
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
    - 리스너
        - 프로토콜: `HTTP`, 포트: `80`
3. 생성 버튼 클릭
4. 로드 밸런서 프로비저닝 상태: Active, 운영 상태: Online 확인 후 `Public IP 연결`


## 3. MySQL 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > MySQL > Instance Group
2. 인스턴스 그룹 만들기 버튼 클릭

    - 기본 설정
        - 이름: `database`
        - 설명: `없음`
    - 인스턴스 가용성: `단일`
    - MySQL 설정
        - 엔진 버전: `MySQL 8.0.34`
        - Primary 포트: `3306`
        - MySQL 사용자 이름: `admin`
        - MySQL 비밀번호: `admin1234`
    - 파라미터 그룹: `default-mysql-8-0-34`
    - 인스턴스 유형: `m2a.large`
    - 기본 스토리지
        - 유형/크기: `SSD`/`100GB`
        - 최대 IOPS: `3000`
    - 로그 스토리지
        - 유형/크기: `SSD`/`100GB`
        - 최대 IOPS: `3000`
    - 네트워크 설정
        - VPC: `kc-vpc`
        - Subnet: `kr-central-2-a의 Private 서브넷`
    - 자동 백업 옵션: `미사용`
3. 만들기 버튼 클릭
4. MySQL 인스턴스 생성 확인


## 4. Object Storage 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage
2. 버킷 생성 버튼 클릭

    - LB Accesslog용 버킷
        - 이름: `lb-accesslog`
        - 암호화: `미사용`
    - Nginx 로그 수집용 버킷 (`Pub/Sub` 연동)
        - 이름: `pubsub-nginx-log`
        - 암호화: `미사용`
    - Nginx 로그 수집용 버킷 (`kafka` 연동)
        - 이름: `kafka-nginx-log`
        - 암호화: `미사용`
    - Data Query의 쿼리 결과 저장용 버킷
        - 이름: `data-query-result`
        - 암호화: `미사용`
    - Spark, Hive 처리 결과에 대한 저장용 버킷
        - 이름: `hive-result`
        - 암호화: `미사용`
3. 생성 버튼 클릭
4. Object Storage 버킷 생성 확인


## 5. Pub/Sub 토픽/서브스크립션 생성

### 1. test-topic 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Pub/Sub > 토픽
2. 토픽 생성 버튼 클릭
   
    - 이름: `test-topic`
    - 기본 서브스크립션: `생성 안함`
    - 토픽 메세지 보존 기간: `0일 0시 10분`
    - 설명: `없음`
3. 생성 버튼 클릭
4. topic 생성 확인

### 2. test-topic의 pull-subscription 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Pub/Sub > 서브스크립션
2. 서브스크립션 생성 버튼 클릭
   
    - 기본 설정
        - 이름: `test-top-pull`
        - 토픽 선택: `test-topic`
    - 유형: `Pull`
    - 서브스크립션 메시지 보존 기간: `1일`
    - 응답 대기 시간: `20초`
    - 재처리 횟수: `횟수 지정`, `3번`
3. 생성 버튼 클릭
4. subscription 생성 확인

### 3. test-topic의 push-subscription
1. 카카오 클라우드 콘솔 > 전체 서비스 > Pub/Sub > 서브스크립션
2. 서브스크립션 생성 버튼 클릭
   
    - 기본 설정
        - 이름: `test-top-push-sub`
        - 토픽 선택: `test-topic`
    - 유형: `Push`
        - 엔드포인트: `http://`, `{ALB Public IP}`, `push-subscription`
    - 서브스크립션 메시지 보존 기간: `1일`
    - 응답 대기 시간: `20초`
    - 재처리 횟수: `횟수 지정`, `3번`
3. 생성 버튼 클릭
4. subscription 생성 확인


## 6. Kafka Cluster 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Advanced Managed Kafka
2. 클러스터 생성 버튼 클릭
   
    - 기본 설정
        - 클러스터 이름: `kafka`
        - Kafka 버전: `3.7.1`
        - 포트: `9092`
    - 인스턴스 유형: `r2a.2xlarge`
    - 네트워크 설정
        - VPC: `kc-vpc`
        - Subnet: `kr-central-2-a의 Public 서브넷`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭
            - 보안 그룹 이름: `kafka-clu-sg`
            - 보안 그룹 설명: `없음`
            - 인바운드 규칙
                - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`
            - 아웃바운드 규칙
                - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
            - `생성` 버튼 클릭
    - 브로커 구성 설정
        - 지정된 가용 영역 수: `0`
        - 브로커 수: `2`
        - 볼륨 유형/크기: `SSD`/`50`
        - 최대 IOPS: `3000`
3. 생성 버튼 클릭
4. kafka 생성 확인
   

## 7. API Server VM 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭

    - 기본 정보
        - 이름: `api-server`
        - 개수: `2`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.xlarge`
    - 볼륨: `30GB`
    - 키 페어: 위에서 생성한 `keypair`
    - 네트워크
        - VPC: `kc-vpc`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름: `api-sg`
                  - 인바운드
                    
                      | 프로토콜 | 출발지 | 포트 번호 |
                      | --- | --- | --- |
                      | TCP | 0.0.0.0/0 | 22 |
                      | TCP | 0.0.0.0/0 | 80 |
                      | TCP | 0.0.0.0/0 | 3306 |
                  
                  - 아웃바운드
                  
                      | 프로토콜 | 목적지 | 포트 번호 |
                      | --- | --- | --- |
                      | ALL | 0.0.0.0/0 | ALL |
                  - `생성` 버튼 클릭
            - 네트워크 인터페이스: `새 인터페이스`
            - 서브넷: `kr-central-2-a의 Public 서브넷`
            - IP 할당 방식: `자동`
    - 고급 설정
        - 사용자 스크립트: [`api_dev.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/ApiServer/api_dev.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
    - `생성` 버튼 클릭
    - `api-server-1`, `api-server-2` 상태 Actice 확인 후 `Public IP 연결`



## 대상 그룹 생성

- **로드 밸런서**
    - **가용 영역**
    - **로드 밸런서**: `kc-alb`
    - **리스너**: `HTTP:80`
- **기본 정보**
    - **대상 그룹 이름**: `api-srv`
    - **프로토콜**: `HTTP`
    - **알고리즘**: `라운드 로빈`
    - **고정 세션**: `미사용`
- **상태 확인**: `미사용`
- **대상 유형**: `인스턴스`
- **네트워크**: `api-srv-1`, `api-srv-2`





## Traffic Generator VM 생성

- **기본 정보**
    - **이름**: `trf-gen`
    - **개수**: `2`
- **이미지**: `Ubuntu 22.04`
- **인스턴스유형**: `t1i.xlarge`
- **볼륨**: `30`
- **키 페어**
    - `키 페어 생성` 버튼 클릭
        - **생성 방법**: `신규 키 페어 생성하기`
        - **이름**: `keypair`
- **네트워크**
    - **VPC**: `kc-vpc`
    - **보안 그룹**
        - `보안 그룹 생성` 버튼 클릭
            - **보안 그룹 이름**: `tgen-sg`
              - **인바운드**
              
                  | 프로토콜 | 출발지 | 포트 번호 |
                  | --- | --- | --- |
                  | TCP | 0.0.0.0/0 | 22 |
              
              - **아웃바운드**
              
                  | 프로토콜 | 목적지 | 포트 번호 |
                  | --- | --- | --- |
                  | ALL | 0.0.0.0/0 | ALL |

        - **네트워크 인터페이스**: `새 인터페이스`
        - **서브넷**: `kr-central-2-a의 Public 서브넷`
        - **IP 할당 방식**: `자동`
- **고급 설정**
    - **사용자 스크립트**: [`setup_initial.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/TrafficGenerator/setup_initial.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
- `생성` 버튼 클릭
- `trf-gen-1`, `trf-gen-2` 상태 Actice 확인 후 `Public IP 연결`




