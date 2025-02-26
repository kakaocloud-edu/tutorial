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

## 2. Object Storage 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage
2. 버킷 생성 버튼 클릭
    - ALB Access Log 수집용 버킷
        - 이름: `alb-log`
        - 암호화: `미사용`
    - Nginx Log 수집용 버킷 (`Pub/Sub` 연동)
        - 이름: `pubsub-nginx-log`
        - 암호화: `미사용`
    - Nginx Log 수집용 버킷 (`kafka` 연동)
        - 이름: `kafka-nginx-log`
        - 암호화: `미사용`
    - Data Query의 쿼리 결과 저장용 버킷
        - 이름: `data-query-result`
        - 암호화: `미사용`
    - Data Catalog의 데이터 저장용 버킷
        - 이름: `data-catalog`
        - 암호화: `미사용`

3. 생성 버튼 클릭
4. Object Storage 버킷 생성 확인

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
4. 생성된 `database` 클릭
5. `엔드포인트` 복사 후 클립보드 등에 붙여넣기

## 4. 로드 밸런서(ALB) 생성

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
5. 연결된 `Public IP` 복사 후 클립보드 등에 붙여넣기
6. `액세스 로그 설정` 클릭
    - 액세스 로그: `사용`
    - 선택할 버킷: `alb-log`
    - 선택할 액세스 키 ID: `액세스 키 생성` 클릭
        1. 우측 상단 계정 프로필 > 사용자 액세스 키 > 비밀번호 확인
        2. 사용자 액세스 키를 생성해 주세요 클릭
            - 사용자 액세스 키 이름 : `keypair`
            - 프로젝트 지정 : `(사용자가 위치한 프로젝트 지정)`
            - 사용자 액세스 키 정보 : `(사용자 선택 입력)`
            - 만료 기한 : `(지정하지 않음)`
        3. 만들기 버튼 클릭
        4. 사용자 `액세스 키 ID` 복사 후 클립보드 등에 붙여넣기
        5. 사용자 `보안 엑세스 키` 복사 후 클립보드 등에 붙여넣기
            - **Note**: 사용자 액세스 키 만들기 팝업창을 닫은 이후 사용자 액세스 보안 키 정보 다시 조회 불가
    - 입력할 보안 액세스 키: 위에서 생성한 `보안 엑세스 키` 입력



## 5. Kafka Cluster 생성

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
        - 지정된 가용 영역 수: `1`
        - 브로커 수: `2`
        - 볼륨 유형/크기: `SSD`/`50`
        - 최대 IOPS: `3000`
3. 생성 버튼 클릭
4. `kafka` 생성 확인 후 클릭
5. `부트스트랩 서버` 복사 후 클립보드 등에 붙여넣기

## 6. API Server VM 생성

1. 카카오 클라우드 콘솔 상단 중앙의 `프로젝트 ID` 복사 후 메모장에 붙여넣기
2. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > 인스턴스
3. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `api-server`
        - 개수: `2`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.xlarge`
    - 볼륨: `30GB`
    - 키 페어: `키 페어 생성` 클릭
        - 생성 방법: `신규 키 페어 생성하기`
        - 이름: `keypair`
        - 유형 설정: `SSH`
        - 생성 버튼 클릭
    - 네트워크
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
        - 유형: `새 인터페이스`
        - IP 할당 방식: `자동`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름: `api-sg`
                    - 인바운드 규칙
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `80`
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `3306`
                    - 아웃바운드 규칙
                        - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
                    - `생성` 버튼 클릭
    - 고급 설정
        - 사용자 스크립트: [`api_dev.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/ApiServer/api_dev.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
        - CPU 멀티스레딩: `활성화`
4. 생성 버튼 클릭
5. `api-server-1`, `api-server-2` 상태 Actice 확인 후 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
6. 확인 버튼 클릭
7. `api-server-1`, `api-server-2` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    ### **lab0-7-7-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    ### **lab0-7-7-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    ### **lab0-7-7-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{api-server-1, 2의 public ip주소}
    ```
    
    - **Note**: {api-server-1, 2의 public ip 주소} 부분을 복사한 각 IP 주소로 교체하세요.
    
    ### **lab0-7-7-4**
    
    ```bash
    yes
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
    
    ### **lab0-7-7-5**
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```
    

## 7. Traffic Generator VM 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `trarffic-generator`
        - 개수: `2`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.xlarge`
    - 볼륨: `30`
    - 키 페어: 위에서 생성한 `keypair` 선택
    - 네트워크
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
        - 유형: `새 인터페이스`
        - IP 할당 방식: `자동`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름: `tg-sg`
                    - 인바운드 규칙
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`
                    - 아웃바운드 규칙
                        - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
    - 고급 설정
        - 사용자 스크립트: [`setup_initial.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/TrafficGenerator/setup_initial.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
        - CPU 멀티스레딩: `활성화`
3. 생성 버튼 클릭
4. `traffic-generator-1`, `traffic-generator-2` 상태 Actice 확인 후 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
5. 확인 버튼 클릭
6. `traffic-generator-1`, `traffic-generator-2` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    ### **lab0-8-6-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    ### **lab0-8-6-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    ### **lab0-8-6-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{traffic-generator-1, 2의 public ip주소}
    ```
    
    - **Note**: {traffic-generator-1, 2의 public ip주소} 부분을 복사한 각 IP 주소로 교체하세요.
    
    ### **lab0-8-6-4**
    
    ```bash
    yes
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
    
    ### **lab0-8-6-5**
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```
    
7. 디렉토리 내부 파일 생성 여부 확인
    
    ### **lab1-1-2**
    
    ```bash
    ls -l
    ```
    

## 8. 로드 밸런서 대상 그룹 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Load Balancing > 대상 그룹
2. 대상 그룹 생성 버튼 클릭
    - 로드 밸런서
        - 가용 영역: `kr-central-2-a`
        - 로드 밸런서: `api-lb`
        - 리스너: `HTTP:80`
    - 기본 정보
        - 대상 그룹 이름: `api-server-group`
        - 프로토콜: `HTTP`
        - 알고리즘: `라운드 로빈`
        - 고정 세션: `미사용`
    - 상태 확인: `미사용`
    - 다음 클릭
    - 대상 유형: `인스턴스`
    - 네트워크:
        - `api-server-1`, `api-server-2` 선택
        - 포트: `80`
        - 대상 추가 버튼 클릭
    - 다음 버튼 클릭
3. 생성 버튼 클릭
4. 대상 그룹 프로비저닝 상태: Active, 운영 상태: Online 확인

---
