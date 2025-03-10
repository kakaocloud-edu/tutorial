
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

# 4. 자격 증명 생성

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


# 6. 환경 변수 설정
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


3. 조직 ID(Domain ID)
    - 카카오 클라우드 콘솔 > Management > IAM > 프로젝트
    - 좌측의 `조직 관리` 클릭
    - `조직 ID` 복사 후 클립보드 등에 붙여넣기


4. 카카오 클라우드 콘솔 상단 중앙의 `프로젝트 ID` 복사 후 메모장에 붙여넣기
    - **Note**: `kakaocloud` 로고를 클릭하여 콘솔 메인화면으로 이동

# 7. API Server VM 생성

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
        - 사용자 스크립트: [`api_dev.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/ApiServer/api_dev.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
        - **Note**: 중괄호({})안에 괄호(())로 쌓여진 값은 지정된 값이므로 그 값을 변경없이 그대로 사용
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


# 8. Traffic Generator VM 생성 (5분)

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
        - 사용자 스크립트: [`setup_initial.sh`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/TrafficGenerator/setup_initial.sh)의 쌍따옴표(“”) 사이에 자신의 리소스 값 입력
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
   

# 9. Kafka Connector VM 생성

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
            - `{S3 액세스 키}`, `{S3 보안 액세스 키}`, `{Kafka 부트스트랩 서버}`, `{Kafka와 연동된 버킷 이름(data-catalog)}`를 개인 환경에 맞게 수정
                #### **lab0-9-2**
                
                ```
                #!/bin/bash
                
                ################################################################################
                # 0. 초기 설정
                ################################################################################
                
                # 원하는 Kakao i Cloud S3 Credentials
                AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
                AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
                AWS_DEFAULT_REGION_VALUE="kr-central-2"
                AWS_DEFAULT_OUTPUT_VALUE="json"
                
                # Kafka용 설정 변수
                KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
                BUCKET_NAME="{Kafka와 연동된 버킷 이름(data-catalog)}"
                
                LOGFILE="/home/ubuntu/setup.log"
                exec &> >(tee -a "$LOGFILE")  # 모든 echo 출력도 setup.log에 기록
                
                log() {
                  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
                }
                
                log "Start setup script"
                
                ################################################################################
                # 1. apt 업데이트 & 필수 패키지 설치
                ################################################################################
                log "Step 1: apt 패키지 목록 업데이트 시작"
                sudo apt-get update -y
                log "Step 1: apt 패키지 목록 업데이트 완료"
                
                log "Step 2: 필요한 패키지 설치 시작"
                sudo apt-get install -y python3 python3-pip openjdk-21-jdk unzip jq aria2 curl
                log "Step 2: 필요한 패키지 설치 완료"
                
                ################################################################################
                # 2. Kafka 다운로드 & 설치
                ################################################################################
                log "Step 3: Kafka 다운로드 및 설치 시작"
                
                aria2c -x 16 -s 16 -d /home/ubuntu -o kafka_2.13-3.7.1.tgz "https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz"
                tar -xzf /home/ubuntu/kafka_2.13-3.7.1.tgz -C /home/ubuntu
                rm /home/ubuntu/kafka_2.13-3.7.1.tgz
                mv /home/ubuntu/kafka_2.13-3.7.1 /home/ubuntu/kafka
                
                log "Step 3: Kafka 다운로드 및 설치 완료"
                
                ################################################################################
                # 3. Confluent Hub Client 설치
                ################################################################################
                log "Step 4: Confluent Hub Client 설치 시작"
                
                sudo mkdir -p /confluent-hub/plugins
                CONFLUENT_HUB_DIR="/confluent-hub"
                CONFLUENT_HUB_URL="http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz"
                CONFLUENT_HUB_FILE="confluent-hub-client-latest.tar.gz"
                
                sudo mkdir -p "$CONFLUENT_HUB_DIR"
                cd "$CONFLUENT_HUB_DIR"
                aria2c -x 16 -s 16 -o "$CONFLUENT_HUB_FILE" "$CONFLUENT_HUB_URL"
                sudo tar -zxf "$CONFLUENT_HUB_FILE"
                sudo chown -R ubuntu:ubuntu /confluent-hub
                
                log "Step 4: Confluent Hub Client 설치 완료"
                
                ################################################################################
                # 4. .bashrc 에 S3 Credentials + Confluent + Java 경로 설정
                ################################################################################
                log "Step 5: .bashrc에 환경 변수 등록"
                
                # 4-1) 기존 라인 제거 (중복 방지)
                sed -i '/S3_ACCESS_KEY=/d' /home/ubuntu/.bashrc
                sed -i '/S3_SECRET_ACCESS_KEY=/d' /home/ubuntu/.bashrc
                sed -i '/AWS_DEFAULT_REGION=/d' /home/ubuntu/.bashrc
                sed -i '/AWS_DEFAULT_OUTPUT=/d' /home/ubuntu/.bashrc
                sed -i '/CONFLUENT_HOME=/d' /home/ubuntu/.bashrc
                sed -i '/JAVA_HOME=/d' /home/ubuntu/.bashrc
                
                # 4-2) 실제 값 치환해서 추가
                cat <<EOF >> /home/ubuntu/.bashrc
                
                # Kakao i Cloud S3 Credentials
                export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID_VALUE"
                export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY_VALUE"
                export AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION_VALUE"
                export AWS_DEFAULT_OUTPUT="$AWS_DEFAULT_OUTPUT_VALUE"
                
                # Confluent 설정
                export CONFLUENT_HOME="/confluent-hub"
                export PATH="\$PATH:\$CONFLUENT_HOME/bin"
                
                # Java 설정
                export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
                export PATH="\$JAVA_HOME/bin:\$PATH"
                EOF
                
                log "Step 5: .bashrc 환경 변수 등록 완료"
                
                ################################################################################
                # 5. .bashrc 적용 → confluent-hub / AWS CLI 에서 쓸 수 있도록
                ################################################################################
                # 주의: cloud-init 등 비인터랙티브 실행 시 .bashrc가 자동 적용되지 않을 수 있으므로, 직접 source.
                source /home/ubuntu/.bashrc
                
                ################################################################################
                # 6. S3 Sink Connector 설치 (confluent-hub)
                ################################################################################
                log "Step 6: S3 Sink Connector 설치 시작"
                
                # (1) connect-standalone.properties 권한 변경
                sudo chown ubuntu:ubuntu /home/ubuntu/kafka/config/connect-standalone.properties 2>/dev/null
                
                # (2) S3 Sink Connector 설치
                /confluent-hub/bin/confluent-hub install confluentinc/kafka-connect-s3:latest \
                  --component-dir /confluent-hub/plugins \
                  --worker-configs /home/ubuntu/kafka/config/connect-standalone.properties \
                  --no-prompt
                
                log "Step 6: S3 Sink Connector 설치 완료"
                
                ################################################################################
                # 7. AWS CLI 설치
                ################################################################################
                log "Step 7: AWS CLI 설치 시작"
                
                cd /home/ubuntu
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.22.0.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install
                rm -rf aws awscliv2.zip
                
                AWS_VERSION=$(aws --version 2>&1 || true)
                log "AWS CLI 버전: $AWS_VERSION"
                log "Step 7: AWS CLI 설치 완료"
                
                ################################################################################
                # 8. AWS CLI configure 설정 (파일)
                ################################################################################
                log "Step 8: AWS CLI configure 파일에 자동 세팅"
                sudo -u ubuntu -i aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID_VALUE"
                sudo -u ubuntu -i aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY_VALUE"
                sudo -u ubuntu -i aws configure set default.region "$AWS_DEFAULT_REGION_VALUE"
                sudo -u ubuntu -i aws configure set default.output "$AWS_DEFAULT_OUTPUT_VALUE"
                
                AWS_VERSION=$(aws --version 2>&1)
                log "Step 8: AWS CLI configure 설정 완료"
                source /home/ubuntu/.bashrc
                
                ################################################################################
                # 9. Kafka 설정 폴더 생성 및 권한 부여
                ################################################################################
                log "Step 9: Kafka 설정 폴더 생성 및 권한 부여"
                
                sudo mkdir -p /opt/kafka/config
                sudo chown -R ubuntu:ubuntu /opt/kafka
                
                ################################################################################
                # 10. 커스텀 파티셔너, 파일네임 플러그인을 다운로드
                ################################################################################
                log "Step 10: 커스텀 파티셔너, 파일네임 플러그인 다운로드"
                
                sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-partitioner-1.0-SNAPSHOT.jar \
                  "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/KafkaConnector/custom-partitioner-1.0-SNAPSHOT.jar" && \
                sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-filename-1.0-SNAPSHOT.jar \
                  "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/KafkaConnector/custom-filename-1.0-SNAPSHOT.jar"
                
                ################################################################################
                # 11. s3-sink-connector.properties 생성
                ################################################################################
                log "Step 11: /opt/kafka/config/s3-sink-connector.properties 파일 생성"
                
                cat <<EOF > /opt/kafka/config/s3-sink-connector.properties
                # 커넥터 이름
                name=s3-sink-connector
                
                # S3 Sink Connector 클래스
                connector.class=io.confluent.connect.s3.S3SinkConnector
                tasks.max=1
                
                # 연결할 토픽
                topics=nginx-topic
                
                # Object Storage/S3 관련 설정
                s3.region=kr-central-2
                s3.bucket.name=${BUCKET_NAME}
                s3.part.size=5242880
                
                aws.access.key.id=${AWS_ACCESS_KEY_ID_VALUE}
                aws.secret.access.key=${AWS_SECRET_ACCESS_KEY_VALUE}
                store.url=https://objectstorage.kr-central-2.kakaocloud.com
                
                # Key/Value Converter 설정
                key.converter=org.apache.kafka.connect.json.JsonConverter
                value.converter=org.apache.kafka.connect.json.JsonConverter
                key.converter.schemas.enable=false
                value.converter.schemas.enable=false
                
                # 스토리지 및 포맷 설정
                storage.class=io.confluent.connect.s3.storage.S3Storage
                format.class=io.confluent.connect.s3.format.json.JsonFormat
                
                # flush.size: 지정한 메시지 수만큼 누적 시 S3에 업로드
                flush.size=1
                
                # 커스텀 파티셔너 클래스 지정
                partitioner.class=com.mycompany.connect.FlexibleTimeBasedPartitioner
                
                # 커스텀 파일네임 클래스 지정
                format.class=com.mycompany.connect.CustomJsonFormat
                
                # 최상위 디렉터리명 변경
                topics.dir=kafka-nginx-log
                
                # 토픽 디렉터리를 기본 토픽 이름 대신 다른 이름으로 대체
                custom.topic.dir=nginx-topic
                
                # 파티션 디렉터리를 커스텀 접두어 생성
                custom.partition.prefix=partition_
                
                # Time-based 파티셔너 필수 설정
                partition.duration.ms=3600000
                path.format='year_'yyyy/'month_'MM/'day_'dd/'hour_'HH
                locale=en-US
                timezone=Asia/Seoul
                timestamp.extractor=Wallclock
                
                # 예약어 치환 규칙
                custom.replacements==:_
                EOF
                
                ################################################################################
                # 12. worker.properties 생성
                ################################################################################
                log "Step 12: /opt/kafka/config/worker.properties 생성"
                
                cat <<EOF > /opt/kafka/config/worker.properties
                # 워커 기본 설정
                bootstrap.servers=${KAFKA_BOOTSTRAP_SERVER}
                key.converter=org.apache.kafka.connect.json.JsonConverter
                value.converter=org.apache.kafka.connect.json.JsonConverter
                key.converter.schemas.enable=false
                value.converter.schemas.enable=false
                
                # Offset 저장 관련 설정 (standalone 모드 필수)
                offset.storage.file.filename=/tmp/connect.offsets
                offset.flush.interval.ms=10000
                
                # 플러그인 경로 (S3 Sink Connector가 설치된 경로)
                plugin.path=/confluent-hub/plugins
                
                # REST 인터페이스 리스너 (커넥터 상태 확인용)
                listeners=http://0.0.0.0:8083
                EOF
                
                ################################################################################
                # 13. kafka-connect systemd 서비스 등록
                ################################################################################
                log "Step 13: kafka-connect systemd 서비스 등록"
                
                cat <<EOF | sudo tee /etc/systemd/system/kafka-connect.service
                [Unit]
                Description=Kafka Connect Standalone Service
                After=network.target
                
                [Service]
                User=ubuntu
                ExecStart=/home/ubuntu/kafka/bin/connect-standalone.sh \
                  /opt/kafka/config/worker.properties \
                  /opt/kafka/config/s3-sink-connector.properties
                Restart=on-failure
                RestartSec=5
                
                [Install]
                WantedBy=multi-user.target
                EOF
                
                log "Step 13: systemd 등록 완료 (kafka-connect.service)"
                
                ################################################################################
                # 완료
                ################################################################################
                log "Setup 완료"
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
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
    
    #### **lab0-9-5-5**
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```

6. 스크립트 적용 확인
    - **Note**: 스크립트 적용에 10~15분 소요

    #### **lab0-9-6**
   
    ```
    cat /home/ubuntu/setup.log
    ```

## 10. 로드 밸런서 대상 그룹 생성

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
