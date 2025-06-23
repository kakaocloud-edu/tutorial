#!/bin/bash

#------------------------------------------
# 설정 변수
#------------------------------------------
KAFKA_VERSION="3.7.1"
KAFKA_SCALA_VERSION="2.13"
KAFKA_TGZ="kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz"
KAFKA_DOWNLOAD_URL="https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${KAFKA_TGZ}"
KAFKA_INSTALL_DIR="/home/ubuntu/kafka"

CONFLUENT_HUB_DIR="/confluent-hub"
CONFLUENT_HUB_URL="http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz"
CONFLUENT_HUB_FILE="confluent-hub-client-latest.tar.gz"

AWS_CLI_VERSION="2.22.0"
AWS_CLI_ZIP="awscliv2.zip"
AWS_CLI_DOWNLOAD_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip"

required_variables=(
  KAFKA_BOOTSTRAP_SERVER BUCKET_NAME
  AWS_ACCESS_KEY_ID_VALUE AWS_SECRET_ACCESS_KEY_VALUE
  AWS_DEFAULT_REGION_VALUE AWS_DEFAULT_OUTPUT_VALUE
)

echo "kakaocloud: 필수 환경변수 검증"
for var in "${required_variables[@]}"; do
  if [ -z "${!var}" ]; then
    echo "  → $var 이(가) 설정되지 않았습니다. 종료."
    exit 1
  fi
done

################################################################################
# 1. 시스템 패키지 설치
################################################################################
echo "kakaocloud: 시스템 업데이트 및 패키지 설치"
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip openjdk-21-jdk unzip jq aria2 curl

################################################################################
# 2. Kafka 설치
################################################################################
echo "kakaocloud: Kafka 다운로드 및 설치"
aria2c -x16 -s16 -d /home/ubuntu -o "${KAFKA_TGZ}" "${KAFKA_DOWNLOAD_URL}"
tar -xzf "/home/ubuntu/${KAFKA_TGZ}" -C /home/ubuntu
rm "/home/ubuntu/${KAFKA_TGZ}"
mv "/home/ubuntu/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}" "${KAFKA_INSTALL_DIR}"
chown -R ubuntu:ubuntu "${KAFKA_INSTALL_DIR}"

################################################################################
# 3. Confluent Hub Client 설치
################################################################################
echo "kakaocloud: Confluent Hub Client 설치"
sudo mkdir -p "${CONFLUENT_HUB_DIR}"
cd "${CONFLUENT_HUB_DIR}"
aria2c -x16 -s16 -o "${CONFLUENT_HUB_FILE}" "${CONFLUENT_HUB_URL}"
sudo tar -zxf "${CONFLUENT_HUB_FILE}"
sudo chown -R ubuntu:ubuntu "${CONFLUENT_HUB_DIR}"

################################################################################
# 4. .bashrc 환경변수 등록
################################################################################
echo "kakaocloud: .bashrc 환경변수 추가"# 기존 관련 라인 제거
sed -i '/S3_ACCESS_KEY=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/S3_SECRET_ACCESS_KEY=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/AWS_DEFAULT_REGION=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/AWS_DEFAULT_OUTPUT=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/CONFLUENT_HOME=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/JAVA_HOME=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }

sed -i '/# Kakao i Cloud S3 Credentials/Q' /home/ubuntu/.bashrc
cat <<EOF >> /home/ubuntu/.bashrc

# Kakao i Cloud S3 Credentials
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID_VALUE}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY_VALUE}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION_VALUE}"
export AWS_DEFAULT_OUTPUT="${AWS_DEFAULT_OUTPUT_VALUE}"

# Confluent Hub
export CONFLUENT_HOME="${CONFLUENT_HUB_DIR}"
export PATH="\$PATH:\$CONFLUENT_HOME/bin"

# Java
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
export PATH="\$JAVA_HOME/bin:\$PATH"
EOF

################################################################################
# 5. S3 Connector 플러그인 설치
################################################################################
echo "kakaocloud: S3 Sink Connector 플러그인 설치"
${CONFLUENT_HUB_DIR}/bin/confluent-hub install \
  confluentinc/kafka-connect-s3:latest \
  --component-dir "${CONFLUENT_HUB_DIR}/plugins" \
  --no-prompt

################################################################################
# 6. AWS CLI 설치
################################################################################
echo "kakaocloud: AWS CLI 설치"
cd /home/ubuntu
curl "${AWS_CLI_DOWNLOAD_URL}" -o "${AWS_CLI_ZIP}"
unzip "${AWS_CLI_ZIP}"
sudo ./aws/install
rm -rf aws "${AWS_CLI_ZIP}"

echo "kakaocloud: AWS CLI 구성"
sudo -u ubuntu mkdir -p /home/ubuntu/.aws
cat <<EOF | sudo -u ubuntu tee /home/ubuntu/.aws/credentials
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID_VALUE}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY_VALUE}
EOF
cat <<EOF | sudo -u ubuntu tee /home/ubuntu/.aws/config
[default]
region = ${AWS_DEFAULT_REGION_VALUE}
output = ${AWS_DEFAULT_OUTPUT_VALUE}
EOF

################################################################################
# 7. Distributed worker 설정 생성
################################################################################
echo "kakaocloud: connect-distributed-8083.properties 생성"
sudo mkdir -p /opt/kafka/config
cat <<EOF > /opt/kafka/config/connect-distributed-8083.properties
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVER}

key.converter=org.apache.kafka.connect.storage.StringConverter
value.converter=io.confluent.connect.avro.AvroConverter
value.converter.schema.registry.url=http://localhost:8081
value.converter.schemas.enable=true

offset.storage.topic=connect-offsets-8083
config.storage.topic=connect-configs-8083
status.storage.topic=connect-statuses-8083
offset.storage.replication.factor=1
config.storage.replication.factor=1
status.storage.replication.factor=1

plugin.path=${CONFLUENT_HUB_DIR}/plugins
listeners=http://0.0.0.0:8083
offset.flush.interval.ms=10000
EOF
chown ubuntu:ubuntu /opt/kafka/config/connect-distributed.properties

################################################################################
# 8. Systemd 유닛 생성 (Distributed)
################################################################################
echo "kakaocloud: kafka-connect-8083.service 등록"
cat <<EOF | sudo tee /etc/systemd/system/kafka-connect-8083.service
[Unit]
Description=Kafka Connect Distributed
After=network.target

[Service]
User=ubuntu
Environment="KAFKA_HEAP_OPTS=-Xms256M -Xmx1G"
ExecStart=${KAFKA_INSTALL_DIR}/bin/connect-distributed.sh /opt/kafka/config/connect-distributed-8083.properties
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable kafka-connect-distributed-8083
sudo systemctl start kafka-connect-distributed-8083

################################################################################
# 9. 커스텀 파티셔너, 파일네임 플러그인 다운로드
################################################################################
echo "kakaocloud: 커스텀 플러그인 다운로드 시작"
sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-partitioner-1.0-SNAPSHOT.jar \
  "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab03/kafka_connector/custom-partitioner-1.0-SNAPSHOT.jar" || { echo "kakaocloud: custom-partitioner 다운로드 실패"; exit 1; }
sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-filename-1.0-SNAPSHOT.jar \
  "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab03/kafka_connector/custom-filename-1.0-SNAPSHOT.jar" || { echo "kakaocloud: custom-filename 다운로드 실패"; exit 1; }

################################################################################
# 10. Connector JSON 생성 및 등록
################################################################################
echo "kakaocloud: s3-sink-avro JSON 생성"
mkdir -p /home/ubuntu/kafka/config/connectors
cat <<EOF > /home/ubuntu/kafka/config/connectors/s3-sink-avro.json
{
  "name": "s3-sink-avro",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "1",
    "topics": "nginx-topic",
    "s3.region": "kr-central-2",
    "s3.bucket.name": "${BUCKET_NAME}",
    "s3.part.size": "5242880",
    "aws.access.key.id": "${AWS_ACCESS_KEY_ID_VALUE}",
    "aws.secret.access.key": "${AWS_SECRET_ACCESS_KEY_VALUE}",
    "store.url": "https://objectstorage.kr-central-2.kakaocloud.com",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "parquet.codec": "snappy",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://localhost:8081",
    "value.converter.schemas.enable": "true",
    "flush.size": "1",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "partition.duration.ms": "3600000",
    "rotate.interval.ms": "60000",
    "path.format": "'year_'yyyy/'month_'MM/'day_'dd/'hour_'HH",
    "timestamp.extractor": "Wallclock",
    "locale": "en-US",
    "timezone": "Asia/Seoul"
  }
}
EOF

echo "kakaocloud: s3-sink-avro 커넥터 등록"
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  --data @/home/ubuntu/kafka/config/connectors/s3-sink-avro.json

echo "kakaocloud: Distributed 모드 설정 완료!"
