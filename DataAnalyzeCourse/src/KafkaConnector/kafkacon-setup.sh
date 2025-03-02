#!/bin/bash

# ------------------------------------------------------------------------------
# 0. 부팅 후 대기 (시스템/네트워크 안정화 대기)
# ------------------------------------------------------------------------------
LOGFILE="/home/ubuntu/setup.log"

# 로그 기록 함수
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGFILE"
}

log "Step 0: 시스템 안정화 대기 후 스크립트 시작"

# ------------------------------------------------------------------------------
# 1. apt 패키지 목록 업데이트 및 업그레이드
# ------------------------------------------------------------------------------
log "Step 1: apt 패키지 목록 업데이트 시작"
sudo apt-get update -y
log "Step 1: apt 패키지 목록 업데이트 완료"

# (선택) 업그레이드 단계: 필요한 경우 아래 주석 해제
# log "Step 1-1: apt 시스템 업그레이드 시작"
# sudo apt-get upgrade -y
# log "Step 1-1: apt 시스템 업그레이드 완료"

# ------------------------------------------------------------------------------
# 2. 필요한 패키지 설치
# ------------------------------------------------------------------------------
log "Step 2: 필요한 패키지 설치 시작"
sudo apt-get install -y python3 python3-pip openjdk-21-jdk unzip jq aria2 curl
log "Step 2: 필요한 패키지 설치 완료"

# ------------------------------------------------------------------------------
# 3. Kafka 다운로드 및 설치 (aria2 이용해 병렬 다운로드)
# ------------------------------------------------------------------------------
log "Step 3: Kafka 다운로드 및 설치 시작"
# Apache 공식 CDN 사용 (dlcdn.apache.org), 필요시 다른 공식 미러 링크로 변경 가능
KAFKA_URL="https://dlcdn.apache.org/kafka/3.7.1/kafka_2.13-3.7.1.tgz"
KAFKA_TGZ="/home/ubuntu/kafka_2.13-3.7.1.tgz"

aria2c -x 16 -s 16 -d /home/ubuntu -o kafka_2.13-3.7.1.tgz "$KAFKA_URL" >> "$LOGFILE" 2>&1

tar -xzf "$KAFKA_TGZ" -C /home/ubuntu >> "$LOGFILE" 2>&1
rm "$KAFKA_TGZ" >> "$LOGFILE" 2>&1
mv /home/ubuntu/kafka_2.13-3.7.1 /home/ubuntu/kafka >> "$LOGFILE" 2>&1
log "Step 3: Kafka 다운로드 및 설치 완료"

# ------------------------------------------------------------------------------
# 4. Confluent Hub Client 설치
# ------------------------------------------------------------------------------
log "Step 4: Confluent Hub Client 설치 시작"
sudo mkdir -p /confluent-hub/plugins

CONFLUENT_HUB_DIR="/confluent-hub"
CONFLUENT_HUB_URL="http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz"
CONFLUENT_HUB_FILE="confluent-hub-client-latest.tar.gz"

cd /
sudo mkdir -p "$CONFLUENT_HUB_DIR"
cd "$CONFLUENT_HUB_DIR"

aria2c -x 16 -s 16 -o "$CONFLUENT_HUB_FILE" "$CONFLUENT_HUB_URL" >> "$LOGFILE" 2>&1
sudo tar -zxf "$CONFLUENT_HUB_FILE" >> "$LOGFILE" 2>&1

log "Step 4: Confluent Hub Client 설치 완료"

# ------------------------------------------------------------------------------
# 4-1. Confluent Hub plugins 폴더 권한 변경
# ------------------------------------------------------------------------------
log "Step 4-1: /confluent-hub/plugins 폴더 권한 변경"
sudo chown ubuntu:ubuntu /confluent-hub/plugins

# ------------------------------------------------------------------------------
# 5. .bashrc에 환경 변수 등록
# ------------------------------------------------------------------------------
log "Step 5: .bashrc에 환경 변수 등록 시작"
cat <<'EOF' >> /home/ubuntu/.bashrc
# Confluent 설정
export CONFLUENT_HOME='/confluent-hub'
export PATH="$PATH:$CONFLUENT_HOME/bin"

# Java 설정
export JAVA_HOME='/usr/lib/jvm/java-21-openjdk-amd64'
export PATH="$JAVA_HOME/bin:$PATH"
EOF
log "Step 5: .bashrc에 환경 변수 등록 완료"

# ------------------------------------------------------------------------------
# 6. .bashrc 적용
# ------------------------------------------------------------------------------
log "Step 6: .bashrc 적용 (source) 시작"
source /home/ubuntu/.bashrc
log "Step 6: .bashrc 적용 완료"

# ------------------------------------------------------------------------------
# 7. S3 Sink Connector 설치
# ------------------------------------------------------------------------------
log "Step 7: S3 Sink Connector 설치 시작"

# 7-1. connect-standalone.properties 권한 변경
log "Step 7-1: /home/ubuntu/kafka/config/connect-standalone.properties 권한 변경"
sudo chown ubuntu:ubuntu /home/ubuntu/kafka/config/connect-standalone.properties

# 7-2. S3 Sink Connector 설치
log "Step 7-2: confluent-hub install confluentinc/kafka-connect-s3:latest"
confluent-hub install confluentinc/kafka-connect-s3:latest \
  --component-dir /confluent-hub/plugins \
  --worker-configs /home/ubuntu/kafka/config/connect-standalone.properties \
  --no-prompt >> "$LOGFILE" 2>&1

log "Step 7: S3 Sink Connector 설치 완료"

# ------------------------------------------------------------------------------
# 8. AWS CLI 설치 (2.22.0)
# ------------------------------------------------------------------------------
log "Step 8: AWS CLI 설치 시작"
cd /home/ubuntu
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.22.0.zip" -o "awscliv2.zip" >> "$LOGFILE" 2>&1
unzip awscliv2.zip >> "$LOGFILE" 2>&1
sudo ./aws/install >> "$LOGFILE" 2>&1
rm -rf aws awscliv2.zip

# 버전 확인 (로그용)
AWS_VERSION=$(aws --version 2>&1)
log "AWS CLI 버전: $AWS_VERSION"
log "Step 8: AWS CLI 설치 완료"

# ------------------------------------------------------------------------------
# 완료
# ------------------------------------------------------------------------------
log "Setup 완료"
