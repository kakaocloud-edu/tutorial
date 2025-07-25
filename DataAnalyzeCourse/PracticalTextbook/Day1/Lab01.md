# 사전 환경 구성
사전 환경 구성에 대한 실습입니다.

- Day1 구성 아키텍처
<img width="787" height="444" alt="day1 아키텍쳐" src="https://github.com/user-attachments/assets/fb466a13-e83e-4e2b-b96f-ab7cd4101142" />

## 1. VPC 생성
1. 카카오 클라우드 콘솔 > Beyond Networking Service > VPC
2. VPC 생성 버튼 클릭  
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
3. 생성 버튼 클릭  
4. VPC 생성 확인

## 2. Object Storage 생성
- **Note**: Object Storage 버킷 구조  
   ![image](https://github.com/user-attachments/assets/905e9b40-63a9-496a-8dee-af5858e91f40)

1. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage 
2. 버킷 생성 버튼 클릭  
3. Pub/Sub과 연동할 NGINX 로그 수집용 버킷 생성
   - 이름: `pubsub-log-bucket`
   - 암호화: `미사용`  
   - 생성 버튼 클릭  
4. `pubsub-log-bucket` 버킷 생성 확인
5. 좌측 일반 버킷 탭 클릭 후 버킷 생성 버튼 클릭  
6. Data Catalog의 데이터 저장용 버킷 생성
   - 이름: `data-catalog-bucket`  
   - 암호화: `미사용`  
   - 생성 버튼 클릭  
7. `data-catalog-bucket` 버킷 생성 확인

## 3. MySQL 인스턴스 그룹 생성 (7분)

1. 카카오 클라우드 콘솔 > Data Store > MySQL
2. 인스턴스 그룹 생성 버튼 클릭
    - 기본 설정
        - 이름: `database`
        - 설명: `빈 칸`
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
        - 다중 AZ 옵션: `미사용`
        - VPC: `kc-vpc`
        - Subnet: `kr-central-2-a의 Private 서브넷`
        - 보안 그룹
            - `보안 그룹 생성` 버튼 클릭
            - 보안 그룹 이름: `mysql-sg`
                - 인바운드 규칙
                    - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `3306`, 설명(선택): `mysql`
                - 아웃바운드 규칙
                    - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
                    - `생성` 버튼 클릭
    - 자동 백업 옵션: `미사용`
    - 테이블 대소문자 구분: `사용`
    - 만들기 버튼 클릭
3. MySQL 생성 확인

## 4. 자격 증명 생성
1. 우측 상단 계정 프로필 > 자격 증명
2. 비밀번호 재확인 > 비밀번호 입력 > 비밀번호 확인
3. `IAM 액세스 키 생성` 클릭  
   - `IAM 액세스 키` 생성 정보  
     - 프로젝트: `사용자가 위치한 프로젝트 지정`  
     - IAM 액세스 키 이름: `iam-acc-key`  
     - IAM 액세스 키 설명(선택): `빈 칸`  
     - 만료일: `무제한`  
   - 생성 버튼 클릭  
   - `IAM 액세스 키 ID` 복사 후 클립보드 등에 붙여넣기  
   - `보안 엑세스 키` 복사 후 클립보드 등에 붙여넣기  
     - **Note**: 사용자 액세스 키 만들기 팝업창을 닫은 이후 사용자 액세스 보안 키 정보 다시 조회 불가  
   - 확인 버튼 클릭

## 5. 로드 밸런서 생성 (18분)
1. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
2. 로드 밸런서 생성 버튼 클릭  
   - 유형 선택: `Application Load Balancer`  
   - 기본 정보  
     - 로드 밸런서 이름: `api-lb`  
     - 로드 밸런서 설명: `빈 칸`  
   - 네트워크  
     - VPC: `kc-vpc`  
     - 서브넷: `kr-central-2-a의 Public 서브넷`  
   - 리스너  
     - 프로토콜: `HTTP`, 포트: `80`  
   - 생성 버튼 클릭  
3. 로드 밸런서 프로비저닝 상태: `Active`, 운영 상태: `Online` 확인  
4. 로드 밸런서 Public IP 연결
   - 로드밸런서 우측의 `⋮` 클릭
   - Public IP 연결 클릭  
   - `새로운 퍼블릭 IP를 생성하고 자동으로 할당` 선택
   - 적용 버튼 클릭
5. `Public IP` 할당된 것을 확인하고 클립보드 등에 복사 붙여넣기  
6. 로드 밸런서 액세스 로그 설정
   - 로드밸런서 우측의 `⋮` 클릭
   - `액세스 로그 설정` 클릭
      - 액세스 로그: `사용`  
      - 선택할 버킷: `data-catalog-bucket`  
      - 선택할 액세스 키 ID: 위에서 생성한 `액세스 키 ID` 입력  
      - 입력할 보안 액세스 키: 위에서 생성한 `보안 엑세스 키` 입력  
   - 적용 클릭

## 6. Kafka Cluster 생성 (3분)

1. 카카오 클라우드 콘솔 > Analytics > Advanced Managed Kafka
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
            - 보안 그룹 설명: `빈 칸`
            - **Note**: `인바운드`, `아웃바운드` 생성 시 `+`버튼을 눌러 생성
            - 인바운드 규칙
                - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`, 설명(선택): `kafka`
            - 아웃바운드 규칙
                - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
            - `생성` 버튼 클릭
    - 브로커 구성 설정
        - 지정된 가용 영역 수: `1`
        - 브로커 수: `2`
        - 볼륨 유형/크기: `SSD`/`50`
        - 최대 IOPS: `3000`
    - 생성 버튼 클릭

3. `kafka` Kafka Cluster 생성 확인
    ![image](https://github.com/user-attachments/assets/cca5102a-b111-4a78-90ee-d1d1886f37f9)

4. 생성한 `kafka` 클러스터 클릭
    ![Image](https://github.com/user-attachments/assets/614eb148-ce90-40a0-bcd5-1b9881f825b5)

5. `부트스트랩 서버` 복사 후 클립보드 등에 붙여넣기
    ![Image](https://github.com/user-attachments/assets/32e09004-a8c2-4b3f-8f36-9e7df3b6d34a)


## 7. 사용자 리소스 정보 조회
1. 카카오 클라우드 콘솔 > Data Store > MySQL
2. `database` Instance Group 클릭
3. 우측 상단의 `엔드포인트` 복사 및 클립보드 등에 붙여넣기 후 좌측 상단 카카오 클라우드 로고 클릭

   ![스크린샷](https://github.com/user-attachments/assets/c5e2e829-02f1-41dc-9932-e14efddfca1c)  
5. 상단 중앙 `프로젝트 ID` 복사 및 클립보드 등에 붙여넣기

   ![프로젝트 ID](https://github.com/user-attachments/assets/8c20f705-2aa1-41fe-872d-5eca55a79150)  
7. 우측 상단 계정 프로필 > 계정 정보
8. 비밀번호 재확인 > 비밀번호 입력 > 비밀번호 확인
9. 우측 상단 `사용자 UUID`, 우측 하단 `조직 ID` 복사 후 클립보드 등에 붙여넣기
   - **Note**: pub/sub 토큰 생성 API 호출 시 `조직 id`와 `프로젝트 id`를 경로 변수로 사용
   - {endpoint-url}/v1/domains/`{조직 id}`/projects/`{프로젝트 id}`/topics/{topic-name}
   - `사용자 UUID` 는 이후 s3 sink connector 생성 시 필요

   <img width="1501" height="526" alt="계정 정보 모자이크" src="https://github.com/user-attachments/assets/3a8ef09e-185f-48a5-bdfe-a0069f48b2b6" />

## 8. Data Stream VM 생성

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `data-stream-vm`
        - 개수: `1`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.xlarge`
    - 볼륨: `10GB`
    - 키 페어: `키 페어 생성` 클릭
      - **Note**: 다운로드 된 private key(e.g. keypair.pem)의 경로 기억하기
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
            - `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름:  `data-st-sg`
                    - 인바운드 규칙
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`, 설명(선택): `ssh`
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `3306`, 설명(선택): `mysql`
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`, 설명(선택): `kafka`
                        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `8081`, 설명(선택): `schema registry`
                    - 아웃바운드 규칙
                        - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
                    - `생성` 버튼 클릭
    - 고급 설정
        - 사용자 스크립트: `data_stream_vm.init.sh`의 쌍따옴표("") 사이에 자신의 리소스 값 입력
            - **Note**: 스크립트에 대한 자세한 내용은 아래 파일들 참고
                - [data_stream_vm.init.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/data_stream_vm/data_stream_vm.init)
        
        ### **lab1-8-2**
        
        ```bash
      #!/bin/bash
      # data_stream_vm_init.sh
      echo "kakaocloud: 1. 환경 변수 설정 시작"
      
      cat <<'EOF' > /tmp/env_vars.sh
      export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
      export MYSQL_DB_HOSTNAME="{MySQL 엔드포인트}"
      export LOGFILE="/home/ubuntu/setup.log"
      export MYSQL_DB_PORT="3306"
      export MYSQL_DB_USER="admin"
      export MYSQL_DB_PASSWORD="admin1234"
      export MYSQL_SERVER_ID="184054"
      export MYSQL_SERVER_NAME="mysql-server"
      EOF
      
      source /tmp/env_vars.sh
      
      if ! grep -q "source /tmp/env_vars.sh" /home/ubuntu/.bashrc; then
          echo "" >> /home/ubuntu/.bashrc
          echo "# Load custom environment variables" >> /home/ubuntu/.bashrc
          echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc
      fi
      
      chown ubuntu:ubuntu /tmp/env_vars.sh
      
      echo "kakaocloud: 2. 통합 설정 스크립트 다운로드"
      SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab01/data_stream_vm/mysql_source_connector.sh"
      CONNECTOR_SCRIPT="/home/ubuntu/mysql_source_connector.sh"
      
      curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
      wget -q "$SCRIPT_URL" -O "$CONNECTOR_SCRIPT"
      
      chown ubuntu:ubuntu "$CONNECTOR_SCRIPT"
      chmod +x "$CONNECTOR_SCRIPT"
      sudo -E "$CONNECTOR_SCRIPT"
      
      SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab01/data_stream_vm/schema_registry_setup.sh"
      SCHEMA_REGISTRY_SCRIPT="/home/ubuntu/schema_registry_setup.sh"
      
      curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Schema Registry script download site is not valid"; exit 1; }
      wget -q "$SCRIPT_URL" -O "$SCHEMA_REGISTRY_SCRIPT"
      
      chown ubuntu:ubuntu "$SCHEMA_REGISTRY_SCRIPT"
      chmod +x "$SCHEMA_REGISTRY_SCRIPT"
      sudo -E "$SCHEMA_REGISTRY_SCRIPT"
        ```
        
    - 생성 버튼 클릭
3. `data-stream-vm` 상태 Active 확인 후 Public IP 연결
    - 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭
4. `data-stream-vm` 인스턴스 SSH 접속
    - `data-stream-vm` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력
    
    ### **lab1-8-4-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    
    ```
    
    ### **lab1-8-4-2**
    
    - **Note**: {data-stream-vm의 public ip주소} 부분을 복사한 각 IP 주소로 교체
    
    ```bash
    ssh -i keypair.pem ubuntu@{data-stream-vm의 public ip주소}
    
    ```
    
    ### **lab1-8-4-3**
    
    ```bash
    yes
    
    ```
    
5. data-stream-vm 스크립트 적용 확인
    - **Note**: 스크립트 적용에 약 7분 소요
    
    ### **lab1-8-5**
    
    - **Note**: 터미널 창이 작으면 로그가 안보일 수 있으니 터미널 창 크기 조절
    
    ```bash
   watch -c "awk '/kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}' < /var/log/cloud-init-output.log"

    ```
    
    - 모든 스크립트 완료 시 아래 출력됨
    
    ```
   kakaocloud: 1. 환경 변수 설정 시작
   kakaocloud: 2. 통합 설정 스크립트 다운로드
   kakaocloud: 3. 필수 환경 변수 검증 시작
   kakaocloud: 4. 시스템 업데이트 및 필수 패키지 설치 시작
   kakaocloud: 5. Kafka 설치 시작
   kakaocloud: 6. Java 환경 변수 등록 시작
   kakaocloud: 7. Debezium MySQL Connector 플러그인 다운로드 및 설치 시작
   kakaocloud: 8. Kafka Connect 분산 모드 설정 (worker.properties) 시작
   kakaocloud: 9. Kafka Connect 시스템 서비스 등록 및 시작
   kakaocloud: 10. Debezium Connector 구성 파일 생성 시작
   kakaocloud: 11. apt 업데이트 및 Java 설치
   kakaocloud: 12. Confluent 패키지 다운로드 및 설치
   kakaocloud: 13. 환경변수 설정
   kakaocloud: 14. Schema Registry 설정
   kakaocloud: 15. systemd 유닛 파일 생성 및 Schema Registry 서비스 등록
   kakaocloud: 16. Schema Registry 서비스 시작
   kakaocloud: 17. Schema Registry 연결 테스트
   kakaocloud: 18. Schema Registry 연결 성공 (시도: 1)
   kakaocloud: Setup 완료
    ```

## 9. Traffic Generator VM 생성 (7분)
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. 인스턴스 생성 버튼 클릭  
   - 기본 정보  
     - 이름: `trarffic-generator`  
     - 개수: `2`  
   - 이미지: `Ubuntu 22.04`  
   - 인스턴스유형: `m2a.xlarge`  
   - 볼륨: `30GB`
   - 키 페어: `keypair`   
   - 네트워크  
      - VPC: `kc-vpc`  
      - 서브넷: `kr-central-2-a의 Public 서브넷`  
      - 유형: `새 인터페이스`  
      - IP 할당 방식: `자동`  
      - 보안 그룹  
         - `보안 그룹 생성` 버튼 클릭  
         - 보안 그룹 이름: `tg-sg`  
           - 인바운드 규칙  
             - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`, 설명(선택): `ssh`  
             - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`, 설명(선택): `kafka`  
           - 아웃바운드 규칙  
             - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`  
   - 고급 설정  
     - 사용자 스크립트: [`tg_vm_init.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/tg_vm_init.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력  
       - **Note**: 스크립트에 대한 자세한 내용은 아래 파일들 참고
         - [tg_full_setup.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/tg_full_setup.sh)  
         - [config.yml](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/config.yml)  
         - [config.py](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/config.py)
      - #### **lab1-9-2**
      ```bash
      #!/bin/bash
      # tg_vm_init.sh
      set -e  # 오류 발생 시 스크립트 종료
      
      echo "kakaocloud: 1.환경 변수 설정 시작"
      # 환경 변수 정의
      command=$(cat <<EOF
      # 프로젝트 및 인증 정보
      export DOMAIN_ID="{조직 ID}"
      export PROJECT_ID="{프로젝트 ID}"
      export CREDENTIAL_ID="{액세스 키 ID}"
      export CREDENTIAL_SECRET="{보안 액세스 키}"
      
      # 생성한 리소스의 값
      export API_BASE_URL="{ALB의 Public IP}"
      export KAFKA_BOOTSTRAP_SERVERS="{Kafka 부트스트랩 서버}"
      export TOPIC_NAME="test-topic"
      export SUB_NAME="test-pull-sub"
      
      # 생성할 Pub/Sub 리소스 정보
      export TOPIC_NAME_MK="log-topic"
      export OBJECT_STORAGE_SUBSCRIPTION_NAME="log-obj-sub"
      export OBJECT_STORAGE_BUCKET="pubsub-log-bucket"
      export PUBSUB_ENDPOINT="https://pub-sub.kr-central-2.kakaocloud.com"
      
      # Kafka 실행에 필요한 경로 및 정보
      export KAFKA_HOME=/opt/kafka
      export PATH=$PATH:$KAFKA_HOME/bin
      EOF
      )
      
      # 환경 변수 적용
      eval "$command"
      echo "$command" >> /home/ubuntu/.bashrc
      
      echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
      curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/tg_full_setup.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
      
      wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/tg_full_setup.sh
      chmod +x tg_full_setup.sh
      sudo -E ./tg_full_setup.sh
      ```
     - CPU 멀티스레딩: `활성화`  
   - 생성 버튼 클릭  
3. `traffic-generator-1`, `traffic-generator-2` 상태 Actice 확인 후 Public IP 연결
   - 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭  
   - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`  
   - 확인 버튼 클릭  
4. `traffic-generator-1`, `traffic-generator-2` 인스턴스 SSH 접속
   - `traffic-generator-1`, `traffic-generator-2` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭  
   - SSH 접속 명령어 복사  
   - 터미널 열기  
   - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력  
    #### **lab1-9-4-1**
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    - 리눅스의 경우 아래와 같이 키페어 권한 조정  
    #### **lab1-9-4-2**
    ```bash
    chmod 400 keypair.pem
    ```
    #### **lab1-9-4-3**
    ```bash
    ssh -i keypair.pem ubuntu@{traffic-generator-1, 2의 public ip주소}
    ```
    - **Note**: {traffic-generator-1, 2의 public ip주소} 부분을 복사한 각 IP 주소로 교체  
    #### **lab1-9-4-4**
    ```bash
    yes
    ```
5. Traffic Generator 스크립트 적용 확인  
   - **Note**: 스크립트 적용에 약 7분 소요  
    #### **lab1-9-5**
    - **Note**: 터미널 창이 작으면 로그가 안보일 수 있으니 터미널 창 크기 조절  
    ```bash
    watch -c "awk '/kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}' < /var/log/cloud-init-output.log"
    ```
    - 모든 스크립트 완료 시 아래 출력됨:
    ```
    kakaocloud: 1.환경 변수 설정 시작
    kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작
    kakaocloud: 3. 필수 환경변수 검증 시작
    kakaocloud: 4. Git 클론 시작
    kakaocloud: 5. config.yml 파일 생성 시작
    kakaocloud: 6. Go SDK 설치 및 설정 시작
    kakaocloud: 7. Pub/Sub SDK 다운로드 및 설치 시작
    kakaocloud: 8. Pub/Sub SDK 의존성 추가 및 로컬 경로 교체 시작
    kakaocloud: 9. go mod tidy 실행 시작
    kakaocloud: 10. Python3 및 pip 설치 시작
    kakaocloud: 11. Python dependencies (requests, pyyaml) 설치 시작
    kakaocloud: 12. OpenJDK 21 설치 시작
    kakaocloud: 13. Apache Kafka 설치 시작
    kakaocloud: 14. kafka-python 라이브러리 설치 시작
    kakaocloud: Setup 완료
    ```


## 10. API Server VM 생성 (3분)
1. 인스턴스 생성 버튼 클릭  
   - 기본 정보  
     - 이름: `api-server`  
     - 개수: `2`  
   - 이미지: `Ubuntu 22.04`  
   - 인스턴스유형: `m2a.large`  
   - 볼륨: `10GB`  
   - 키 페어: 위에서 생성한 `keypair` 선택  
   - 네트워크  
     - VPC: `kc-vpc`  
     - 서브넷: `kr-central-2-a의 Public 서브넷`  
     - 유형: `새 인터페이스`  
     - IP 할당 방식: `자동`  
     - 보안 그룹  
       - `보안 그룹 생성` 버튼 클릭  
         - 보안 그룹 이름: `api-sg`  
           - 인바운드 규칙  
             - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`, 설명(선택): `ssh`  
             - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `80`, 설명(선택): `http`  
             - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `3306`, 설명(선택): `mysql`
             - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `9092`, 설명(선택): `kafka`
             - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `8081`, 설명(선택): `schema registry`
           - 아웃바운드 규칙  
             - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`  
           - `생성` 버튼 클릭  
   - 고급 설정  
     - **Note**: 메모장에 아래 링크의 코드를 복사 붙여넣기 하여 사용  
     - **Note**: 중괄호({})는 제거하고 쌍 따옴표는 유지  
     - 사용자 스크립트: [`api_vm_init`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/api_vm_init.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력  
       - **Note**: 스크립트에 대한 자세한 내용은 아래 파일들 참고
         - [api_env_setup.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/api_env_setup.sh)  
         - [api_full_setup.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/api_full_setup.sh)  
         - [setup_db.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/setup_db.sh)  
         - [filebeat.yml](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/filebeat.yml)  
         - [logs-to-pubsub.conf](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/logs-to-pubsub.conf)  
         - [logs-to-kafka.conf](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/api_server/logs-to-kafka.conf)
      #### **lab1-10-2**
      ```bash
      #!/bin/bash
      # api_vm_init.sh
      # 프로젝트 및 인증 정보
      export DOMAIN_ID="{조직 ID}"
      export PROJECT_ID="{프로젝트 ID}"
      export CREDENTIAL_ID="{액세스 키 ID}"
      export CREDENTIAL_SECRET="{보안 액세스 키}"
      
      # 데이터베이스 설정
      export MYSQL_HOST="{MySQL 엔드포인트}"
      
      # 스키마 레지스트리 설정
      export SCHEMA_REGISTRY_URL="{data-stream-vm의 Public IP}"
      
      # Pub/Sub 및 Kafka 설정
      export LOGSTASH_KAFKA_ENDPOINT="{Kafka 부트스트랩 서버}"
      export PUBSUB_TOPIC_NAME="log-topic"
      export KAFKA_TOPIC_NAME="nginx-topic"
      
      # 로그 및 환경 설정
      export LOGSTASH_ENV_FILE="/etc/default/logstash"
      export ENV_SETUP_SCRIPT_URL="https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/api_server/api_env_setup.sh"
      
      echo "kakaocloud: 1. api server VM 환경 설정용 api_env_setup.sh 다운로드"
      curl --output /dev/null --silent --head --fail "$ENV_SETUP_SCRIPT_URL" || {
        echo "kakaocloud: api_env_setup.sh 다운로드 링크가 유효하지 않습니다."
        exit 1
      }
      
      wget -O api_env_setup.sh "$ENV_SETUP_SCRIPT_URL"
      
      echo "kakaocloud: 2. api_env_setup.sh 실행"
      chmod +x api_env_setup.sh
      sudo -E ./api_env_setup.sh
      ```
     - CPU 멀티스레딩: `활성화`  
2. `api-server-1`, `api-server-2` 상태 Actice 확인 후 Public IP 연결
   - 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭  
   - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`  
   - 확인 버튼 클릭  
3. `api-server-1`, `api-server-2` 인스턴스 SSH 접속
   - `api-server-1`, `api-server-2` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭  
   - SSH 접속 명령어 복사  
   - 터미널 열기  
   - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력  
    #### **lab1-10-3-1**
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    - 리눅스의 경우 아래와 같이 키페어 권한 조정  
    #### **lab1-10-3-2**
    ```bash
    chmod 400 keypair.pem
    ```
    #### **lab1-10-3-3**
    ```bash
    ssh -i keypair.pem ubuntu@{api-server-1의 public ip 주소}
    ```
    - **Note**: {api-server-1의 public ip 주소} 부분을 복사한 각 IP 주소로 교체  
    #### **lab1-10-3-4**
    ```bash
    yes
    ```
    - **Note**: 윈도우에서 ssh 접근이 안될 경우, cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 실행  
    #### **lab1-10-3-5**
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```
4. API Server 스크립트 적용 확인  
    #### **lab1-10-4-1**
    - **Note**: 터미널 창이 작으면 로그가 안보일 수 있으니 터미널 창 크기 조절  
    ```bash
    watch -c "awk '/kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}' < /var/log/cloud-init-output.log"
    ```
    - 모든 스크립트 완료 시 아래 출력됨:
    ```
    kakaocloud: 1. api server VM 환경 설정용 api_env_setup.sh 다운로드
    kakaocloud: 2. api_env_setup.sh 실행
    kakaocloud: 3. 환경 변수를 ~/.bashrc에 추가
    kakaocloud: 4. filebeat, logstash 다운로드
    kakaocloud: 5. filebeat, logstash 환경 변수 설정
    kakaocloud: 6. flask_app.service 환경 변수 설정
    kakaocloud: 7. 스크립트 및 실습 진행에 필요한 파일 다운로드
    kakaocloud: 8. API 서버·파이프라인 가동용 api_full_setup.sh 실행 시작
    kakaocloud: 9. Avro 플러그인 설치용 api_arvo_setup.sh 실행 시작
    kakaocloud: 10. systemd 유닛 파일 생성 및 Schema Registry 서비스 등록 시작
    kakaocloud: 11. logstash.yml 구성 시작
    kakaocloud: 12. filebeat, logstash 재시작
    kakaocloud: Setup 완료
    ```

5. `api-server-1`에서 `setup_db.sh` 실행

   #### **lab1-10-5-1**

   ```bash
   sudo chmod +x /home/ubuntu/setup_db.sh
   ```

   #### **lab1-10-5-2**

   ```bash
   sudo -E /home/ubuntu/setup_db.sh
   ```

   <img width="1219" height="189" alt="setupdb 결과" src="https://github.com/user-attachments/assets/3ee69e38-5dd3-4066-9cc3-863768e93022" />
   
## 11. 로드 밸런서 대상 그룹 생성 (15분)
1. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
2. 대상 그룹 탭 클릭 후 대상 그룹 생성 버튼 클릭 
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
   - 네트워크
     - 연결 대상: `api-server-1`, `api-server-2` 선택
     - 포트: `80`
   - 대상 추가 버튼 클릭  
   - 다음 버튼 클릭  
   - 생성 버튼 클릭  
3. 대상 그룹 프로비저닝 상태: Active, 운영 상태: Online 확인
