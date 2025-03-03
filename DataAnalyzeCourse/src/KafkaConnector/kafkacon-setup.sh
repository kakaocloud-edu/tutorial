#!/bin/bash

################################################################################
# 0. 초기 설정
################################################################################

# 원하는 Kakao i Cloud S3 Credentials
AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
AWS_DEFAULT_REGION_VALUE="kr-central-2"
AWS_DEFAULT_OUTPUT_VALUE="json"

LOGFILE="/home/ubuntu/setup.log"
exec &> >(tee -a "$LOGFILE")  # 모든 echo 출력도 setup.log에 기록(원한다면)

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
# log "Step 6: 소스 적용 (source /home/ubuntu/.bashrc)"
# 주의: 이 `source` 명령은 현재 root 쉘에서 /home/ubuntu/.bashrc를 읽게 합니다.
# 실제 ubuntu 계정의 로그인 쉘과 완전히 동일하게 동작하는 것은 아니지만,
# PATH나 export 변수 정도는 반영됩니다.
source /home/ubuntu/.bashrc

################################################################################
# 6. S3 Sink Connector 설치 (confluent-hub)
################################################################################
log "Step 6: S3 Sink Connector 설치 시작"

# (1) connect-standalone.properties 권한 변경
sudo chown ubuntu:ubuntu /home/ubuntu/kafka/config/connect-standalone.properties

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
# 완료
################################################################################
log "Setup 완료"
