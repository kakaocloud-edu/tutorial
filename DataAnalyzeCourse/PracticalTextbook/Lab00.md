
# 사전 환경 구성

사전 환경 구성에 대한 실습입니다.

# 1. VPC 생성

1. 카카오 클라우드 콘솔 > Beyond Networking Service > VPC > VPC

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

# 2. Object Storage 생성 (1분)

1. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
2. 버킷 생성 버튼 클릭

3. Nginx Log 수집용 버킷 (Pub/Sub 연동)
    - 이름: `pubsub-nginx-log`
    - 암호화: `미사용`
    - 생성 버튼 클릭
    - **Note**: 왼쪽의 일반 버킷 눌러 Object Storage 메인 화면으로 이동

4. Data Catalog의 데이터 저장용 버킷
    - 이름: `data-catalog`
    - 암호화: `미사용`
    - 생성 버튼 클릭
5. Object Storage 버킷 생성 확인
    - **Note**: 왼쪽의 일반 버킷 눌러 Object Storage 메인 화면으로 이동

- **Note**: 최종 data-catalog 버킷의 구조
    - **Note**: 최종 data-catalog 버킷의 구조



    ![111](https://github.com/user-attachments/assets/4b8aeac5-1d74-4240-a3c9-fdca4029c2ce)



# 3. MySQL 생성 (7분)

1. 카카오 클라우드 콘솔 >  Data Store > MySQL > Instance Group
2. 인스턴스 그룹 만들기 버튼 클릭
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
        - VPC: `kc-vpc`
        - Subnet: `kr-central-2-a의 Private 서브넷`
    - 자동 백업 옵션: `미사용`
3. 만들기 버튼 클릭

# 4. 자격 증명 생성 (3분)

1. 우측 상단 계정 프로필 > 자격 증명 > 비밀번호 확인
2. `IAM 액세스 키 생성` 클릭
    - `IAM 액세스 키` 생성 정보
        - 프로젝트: `사용자가 위치한 프로젝트 지정`
        - IAM 액세스 키 이름 : `user-acc-key`
        - IAM 액세스 키 설명(선택) : `빈 칸`
        - 만료일 : `무제한`
    - 생성 버튼 클릭
    - 사용자 `IAM 액세스 키 ID` 복사 후 클립보드 등에 붙여넣기
    - 사용자 `보안 엑세스 키` 복사 후 클립보드 등에 붙여넣기
        - **Note**: 사용자 액세스 키 만들기 팝업창을 닫은 이후 사용자 액세스 보안 키 정보 다시 조회 불가
    - 확인 버튼 클릭

3. 우측 상단 계정 프로필 > 자격 증명 > 비밀번호 확인
4. `S3 액세스 키` 탭 클릭
5. `S3 액세스 키 생성` 버튼 클릭
    - S3 액세스 키 생성 정보
        - 프로젝트: `사용자가 위치한 프로젝트`
        - S3 액세스 키 이름: `s3-acc-key`
        - S3 액세스 키 설명 (선택): `빈 칸`
    - 생성 버튼 클릭
    - S3 인증 정보 항목의 사용자 `인증 키` 복사 후 클립보드 등에 붙여넣기
    - S3 인증 정보 항목의 사용자 `보안 엑세스 키` 복사 후 클립보드 등에 붙여넣기
        - **Note**: S3 액세스 키 정보 팝업창을 닫은 이후 S3 인증 정보 다시 조회 불가
    - 확인 버튼 클릭
    
# 5. 로드 밸런서(ALB) 생성 (18분)

1. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing > 로드 밸런서
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
    - 생성 버튼 클릭
3. 로드 밸런서 프로비저닝 상태: Active, 운영 상태: Online 확인
4. 로드밸런서 우측의 `...`클릭 후 `Public IP 연결`
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당` 선택
5. `Public IP` 할당된 것을 확인하고 클립보드 등에 복사 붙여넣기
6. `액세스 로그 설정` 클릭
    - 액세스 로그: `사용`
    - 선택할 버킷: `data-catalog`
    - 선택할 액세스 키 ID: 위에서 생성한 `액세스 키 ID` 입력
    - 입력할 보안 액세스 키: 위에서 생성한 `보안 엑세스 키` 입력
    - 적용 클릭


# 6. 환경 변수 설정 (3분)
1. MySQL
    - 카카오 클라우드 콘솔 > Data Store > MySQL > Instance Group
    - 생성된 `database` 클릭
    - 우측 상단의 `엔드포인트` 복사 후 클립보드 등에 붙여넣기
      <img width="1317" alt="스크린샷 2025-03-06 오후 4 37 37" src="https://github.com/user-attachments/assets/c5e2e829-02f1-41dc-9932-e14efddfca1c" />


2. Kafka Cluster
    - 카카오 클라우드 콘솔 > Analytics > Advanced Managed Kafka > 클러스터
    - 생성된 `kafka` 클릭
    - 우측 상단의 `부트스트랩 서버` 복사 후 클립보드 등에 붙여넣기
      <img width="1323" alt="스크린샷 2025-03-06 오후 4 39 29" src="https://github.com/user-attachments/assets/1fc0623e-2deb-4dfa-98d7-fd60a37ea1d6" />


3. IAM
    - 카카오 클라우드 콘솔 > Management > IAM > 프로젝트
    - 좌측의 `자신이 속한 프로젝트` 클릭
    - `조직 ID` , '프로젝트 ID' 복사 후 클립보드 등에 붙여넣기
    ![그림1](https://github.com/user-attachments/assets/22192309-344b-4233-becc-5b801e5e0dad)


# 7. API Server VM 생성 (미완)

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `api-server`
        - 개수: `2`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.large`
    - 볼륨: `10GB`
    - 키 페어: `키 페어 생성` 클릭
        - 생성 방법: `신규 키 페어 생성하기`
        - 이름: `keypair`
        - 유형 설정: `SSH`
        - 생성 버튼 클릭
        - **Note**: 다운로드 된 private key(e.g. keypair.pem)의 경로 기억하기
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
        - **Note**: 메모장에 아래 링크의 코드를 복사 붙여넣기 하여 사용
        - **Note**: 중괄호({})는 제거하고 쌍 따옴표는 유지
        - 사용자 스크립트: [`api_vm_init`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/api_server/as_vm_init.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
        ```
        #!/bin/bash
        export DOMAIN_ID="{조직 ID}"
        export PROJECT_ID="{프로젝트 ID}"
        export CREDENTIAL_ID="{액세스 키 ID}"
        export CREDENTIAL_SECRET="{보안 액세스 키}"
        export MYSQL_HOST="{MySQL 엔드포인트}"
        export LOGSTASH_KAFKA_ENDPOINT="{임시 Kafka 클러스터 부트스트랩 서버}"
        
        export PUBSUB_TOPIC_NAME="test-topic"
        export KAFKA_TOPIC_NAME="nginx-topic"
        export LOGSTASH_ENV_FILE="/etc/default/logstash"
        export ENV_SETUP_SCRIPT_URL="https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/as_env_setup.sh"
        
        echo "kakaocloud: 1. as_env_setup.sh 스크립트를 다운로드합니다."
        
        curl --output /dev/null --silent --head --fail "$ENV_SETUP_SCRIPT_URL" || {
          echo "kakaocloud: as_env_setup.sh 다운로드 링크가 유효하지 않습니다."
          exit 1
        }
        
        wget -O as_env_setup.sh "$ENV_SETUP_SCRIPT_URL"
        chmod +x as_env_setup.sh
        
        echo "kakaocloud: 2. as_env_setup.sh 실행을 시작합니다."
        sudo -E ./as_env_setup.sh
        
        echo "kakaocloud: 모든 작업 완료"
        ```
        - CPU 멀티스레딩: `활성화`
    - 생성 버튼 클릭

6. `api-server-1` 상태 Actice 확인 후 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭

4. `api-server-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab0-7-4-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab0-7-4-2**
    
    ```bash
    chmod 400 keypair.pem
    
    ```
    
    #### **lab0-7-4-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{api-server-1의 public ip 주소}
    
    ```
    
    - **Note**: {api-server-1의 public ip 주소} 부분을 복사한 각 IP 주소로 교체하세요.
    
    #### **lab0-7-4-4**
    
    ```bash
    yes
    
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
    
    #### **lab0-7-4-5**
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```

5. API Server VM 스크립트 적용 확인

    #### **lab0-7-5**
    
    ```bash
    watch cat /home/ubuntu/as_script.log
    ```


# 8. Traffic Generator VM 생성 (7분)

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭
    - 기본 정보
        - 이름: `trarffic-generator`
        - 개수: `2`
    - 이미지: `Ubuntu 22.04`
    - 인스턴스유형: `m2a.xlarge`
    - 볼륨: `30GB`
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
        - 사용자 스크립트: [`tg_vm_init.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/traffic_generator/tg_vm_init.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
      ```
        #!/bin/bash
        # tg_vm_init.sh        
        set -e  # 오류 발생 시 스크립트 종료
        
        echo "kakaocloud: 1.환경 변수 설정 시작"
        # 환경 변수 정의
        command=$(cat <<EOF
        export DOMAIN_ID="{조직 ID}"
        export PROJECT_ID="{프로젝트 ID}"
        export CREDENTIAL_ID="{액세스 키 ID}"
        export CREDENTIAL_SECRET="{보안 액세스 키}"
        export API_BASE_URL="{ALB의 Public IP}"
        export TOPIC_NAME="test-topic"
        export SUB_NAME="test-pull-sub"
        export TOPIC_NAME_MK="log-topic"
        export OBJECT_STORAGE_SUBSCRIPTION_NAME="log-obj-sub"
        export OBJECT_STORAGE_BUCKET="pubsub-nginx-log"
        export PUBSUB_ENDPOINT="https://pub-sub.kr-central-2.kakaocloud.com"
        EOF
        )
        
        # 환경 변수 적용
        eval "$command"
        echo "$command" >> /home/ubuntu/.bashrc
        
        echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
        curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/traffic_generator/tg_full_setup.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
        
        wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab00/traffic_generator/tg_full_setup.sh
        chmod +x tg_full_setup.sh
        sudo -E ./tg_full_setup.sh
      ```
        - CPU 멀티스레딩: `활성화`
    - 생성 버튼 클릭
3. `traffic-generator-1`, `traffic-generator-2` 상태 Actice 확인 후 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭
4. `traffic-generator-1`, `traffic-generator-2` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - **Note**: 터미널 창 2개를 사용합니다.
    - **Note**: `traffic-generator-1, 2`가 구분되도록 cli창을 위치시키기
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab0-8-4-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab0-8-4-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab0-8-4-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{traffic-generator-1, 2의 public ip주소}
    ```
    
    - **Note**: {traffic-generator-1, 2의 public ip주소} 부분을 복사한 각 IP 주소로 교체하세요.
    
    #### **lab0-8-4-4**
    
    ```bash
    yes
    ```

    
5. trarffic-generator 스크립트 적용 확인
    
    #### **lab0-8-5**
    
    ```bash
    watch -c 'awk "/kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}" < /var/log/cloud-init-output.log'
    ```
   

# 9. Kafka Connector VM 생성 (5분)

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 인스턴스
2. 인스턴스 생성 버튼 클릭
    - Kafka Connector VM 생성 정보
        - 기본 정보
            - 이름: `kafka-connector`
            - 개수: `1`
        - 이미지: `Ubuntu 22.04`
        - 인스턴스유형: `m2a.xlarge`
        - 볼륨: `10`
        - 키 페어: 위에서 생성한 `keypair`
        - 네트워크
            - VPC: `kc-vpc`
            - 서브넷: `kr-central-2-a의 Public 서브넷`
            - 유형: `새 인터페이스`
            - IP 할당 방식: `자동`
            - 보안 그룹
                - **Note**: 기존에 Traffic Generator VM에서 사용한 보안그룹 사용
                - 보안 그룹 이름: `tg-sg` 선택
                    - 인바운드 규칙
                        - 프로토콜: TCP, 출발지: 0.0.0.0/0, 포트 번호: `22`
                        - 프로토콜: TCP, 출발지: 0.0.0.0/0, 포트 번호: `9092`
                    - 아웃바운드 규칙
                        - 프로토콜: ALL, 출발지: 0.0.0.0/0, 포트 번호: `ALL`
    
        - 고급 설정
            - 아래 스크립트 입력
            - **Note**: 메모장에 아래 링크의 코드를 복사 붙여넣기 하여 사용
            - **Note**: 중괄호({})는 제거하고 쌍 따옴표는 유지
            - 사용자 스크립트: [`kafka_vm_init.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_vm_init.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
              ```
              #!/bin/bash
                
              ################################################################################
              # 0. 초기 설정
              ################################################################################
              
              echo "kakaocloud: 1.환경 변수 설정 시작"
              # 환경 변수 정의
              command=$(cat <<EOF
              # Kafka용 설정 변수
              KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
              BUCKET_NAME="data-catalog"
                
              # Kakao i Cloud S3 Credentials 및 Kafka 관련 변수 설정
              AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
              AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
              AWS_DEFAULT_REGION_VALUE="kr-central-2"
              AWS_DEFAULT_OUTPUT_VALUE="json"
              
              
              LOGFILE="/home/ubuntu/setup.log"
              EOF
              )
              
              # 환경 변수 적용
              eval "$command"
              echo "$command" >> /home/ubuntu/.bashrc
              
              
              echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
              curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_full_setup.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
              
              wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_vm_init
              chmod +x kafka_vm_init
              sudo -E ./kafka_vm_init
              ```
            
            - CPU 멀티스레딩: `활성화`
        
    - 생성 버튼 클릭
3. `kafka-connector` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
4. 확인 버튼 클릭
5. `kafka-connector` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    #### **lab0-9-5-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab0-9-5-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab0-9-5-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{kafka-connector의 public ip주소}
    ```
    
    - {kafka-connector의 public ip주소}: 복사한 각 IP 주소 입력
    
    #### **lab0-9-5-4**
    
    ```bash
    yes
    ```

6. 스크립트 적용 확인
    - **Note**: 스크립트 적용에 10~15분 소요

    #### **lab0-9-6**
   
    ```
    watch -c 'awk "/^kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}" < /var/log/cloud-init-output.log'
    ```

## 10. 로드 밸런서 대상 그룹 생성 (15분)

1. 카카오 클라우드 콘솔 >Beyond Networking Service > Load Balancing > 대상 그룹
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
    - 생성 버튼 클릭
3. 대상 그룹 프로비저닝 상태: Active, 운영 상태: Online 확인
