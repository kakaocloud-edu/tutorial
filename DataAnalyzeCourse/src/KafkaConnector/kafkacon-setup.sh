#!/bin/bash

set -euo pipefail

# 원하는 kakaocloud S3 Credentials
AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
AWS_DEFAULT_REGION_VALUE="kr-central-2"
AWS_DEFAULT_OUTPUT_VALUE="json"

# Kafka용 설정 변수
KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버 값}"
BUCKET_NAME="{Kafka와 연동된 버킷 이름(data-catalog)}"

################################################################################
# 0. 초기 설정
################################################################################

# 로그 파일 경로 설정
LOGFILE="/home/ubuntu/setup.log"

# 로그 기록 함수
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGFILE"
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
