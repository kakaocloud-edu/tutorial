#!/bin/bash
# kafkacon_init.sh
set -euo pipefail

#################################
# Step 0: 초기 설정
#################################
LOGFILE="/home/ubuntu/setup.log"
exec &> >(tee -a "$LOGFILE")

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Start kafkacon init script"

#################################
# Step 1: 환경 변수 입력
#################################
log "Step 1: 환경 변수 입력 및 기본 검사"
# kakaocloud S3 Credentials
export AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
export AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
export AWS_DEFAULT_REGION_VALUE="kr-central-2"
export AWS_DEFAULT_OUTPUT_VALUE="json"

# Kafka용 설정 변수
export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
export BUCKET_NAME="{Kafka와 연동된 버킷 이름(data-catalog)}"

log "환경 변수 입력 완료"

#################################
# Step 2: .bashrc 환경 변수 등록
#################################
log "Step 2: .bashrc 환경 변수 등록"
sed -i '/AWS_ACCESS_KEY_ID=/d' /home/ubuntu/.bashrc
sed -i '/AWS_SECRET_ACCESS_KEY=/d' /home/ubuntu/.bashrc
sed -i '/AWS_DEFAULT_REGION=/d' /home/ubuntu/.bashrc
sed -i '/AWS_DEFAULT_OUTPUT=/d' /home/ubuntu/.bashrc
sed -i '/KAFKA_BOOTSTRAP_SERVER=/d' /home/ubuntu/.bashrc
sed -i '/BUCKET_NAME=/d' /home/ubuntu/.bashrc

cat <<EOF >> /home/ubuntu/.bashrc

# Kakao i Cloud S3 Credentials 및 Kafka 설정
export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID_VALUE"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY_VALUE"
export AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION_VALUE"
export AWS_DEFAULT_OUTPUT="$AWS_DEFAULT_OUTPUT_VALUE"
export KAFKA_BOOTSTRAP_SERVER="$KAFKA_BOOTSTRAP_SERVER"
export BUCKET_NAME="$BUCKET_NAME"

# Confluent 설정
export CONFLUENT_HOME="/confluent-hub"
export PATH="\$PATH:\$CONFLUENT_HOME/bin"

# Java 설정
export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
export PATH="\$JAVA_HOME/bin:\$PATH"

EOF

log ".bashrc 환경 변수 등록 완료"

# 현재 쉘에 적용
source /home/ubuntu/.bashrc

#################################
# Step 3: 메인 스크립트 실행 (필요한 파일 다운로드 및 설치 작업)
#################################
log "Step 3: 메인 스크립트 실행 시작"

wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab02/kafka_connector/kafkacon_setup.sh
chmod +x kafkacon_setup.sh
sudo -E ./kafkacon_setup.sh
