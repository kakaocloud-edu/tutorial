#!/bin/bash

#------------------------------------------
# 0. 초기 환경 설정 및 로그 리디렉션
#------------------------------------------
if [ -f "/tmp/env_vars.sh" ]; then
    source /tmp/env_vars.sh
    if [ -z "$LOGFILE" ]; then
        LOGFILE="/home/ubuntu/setup_s3_sink_connector.log"
    fi
else
    LOGFILE="/home/ubuntu/setup_s3_sink_connector.log"
    echo "kakaocloud: 경고: /tmp/env_vars.sh 파일을 찾을 수 없습니다. 환경 변수가 외부에서 설정되어야 합니다."
fi

exec > >(tee -a "$LOGFILE") 2>&1

#------------------------------------------
# 1. 메인 스크립트 내부 설정 변수
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
AWS_CLI_DOWNLOAD_URL="https://awscli.amazonaws.com/awscliv2-exe-linux-x86_64-${AWS_CLI_VERSION}.zip"

CONNECT_REST_PORT="8084"
DEBEZIUM_SOURCE_SERVER_NAME="mysql-server"

DEBEZIUM_TOPICS="mysql-server.shopdb.cart,mysql-server.shopdb.cart_logs,mysql-server.shopdb.orders,mysql-server.shopdb.products,mysql-server.shopdb.reviews,mysql-server.shopdb.search_logs,mysql-server.shopdb.sessions,mysql-server.shopdb.users,mysql-server.shopdb.users_logs"


#------------------------------------------
# 2. 필수 환경변수 검증
#------------------------------------------
required_env_vars=(
  KAFKA_BOOTSTRAP_SERVER BUCKET_NAME
  AWS_ACCESS_KEY_ID_VALUE AWS_SECRET_ACCESS_KEY_VALUE
  AWS_DEFAULT_REGION_VALUE AWS_DEFAULT_OUTPUT_VALUE
)

echo "kakaocloud: 2. 필수 환경 변수 검증 시작"
for var in "${required_env_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "kakaocloud: 오류: 필수 환경 변수 $var 가 설정되지 않았습니다. 스크립트를 종료합니다."
        exit 1
    fi
done

KAFKA_BOOTSTRAP_SERVERS="$KAFKA_BOOTSTRAP_SERVER"


################################################################################
# 3. 시스템 업데이트 및 필수 패키지 설치
################################################################################
echo "kakaocloud: 3. 시스템 업데이트 및 필수 패키지 설치 시작"
sudo apt-get update -y || { echo "kakaocloud: apt-get update 실패"; exit 1; }
sudo apt-get install -y python3 python3-pip openjdk-21-jdk unzip jq aria2 curl || { echo "kakaocloud: 필수 패키지 설치 실패"; exit 1; }

################################################################################
# 4. Kafka 다운로드 및 설치
################################################################################
echo "kakaocloud: 4. Kafka 설치 시작"
aria2c -x 16 -s 16 -d /home/ubuntu -o "${KAFKA_TGZ}" "${KAFKA_DOWNLOAD_URL}" || { echo "kakaocloud: Kafka 다운로드 실패"; exit 1; }
tar -xzf /home/ubuntu/"${KAFKA_TGZ}" -C /home/ubuntu || { echo "kakaocloud: Kafka 압축 해제 실패"; exit 1; }
rm /home/ubuntu/"${KAFKA_TGZ}" || { echo "kakaocloud: 임시 파일 삭제 실패"; exit 1; }
mv /home/ubuntu/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION} "${KAFKA_INSTALL_DIR}" || { echo "kakaocloud: Kafka 디렉토리 이동 실패"; exit 1; }

################################################################################
# 5. Confluent Hub Client 설치
################################################################################
echo "kakaocloud: 5. Confluent Hub Client 설치 시작"
sudo mkdir -p /confluent-hub/plugins || { echo "kakaocloud: Confluent Hub 디렉토리 생성 실패"; exit 1; }
sudo mkdir -p "$CONFLUENT_HUB_DIR" || { echo "kakaocloud: Confluent Hub 디렉토리 생성 실패"; exit 1; }
cd "$CONFLUENT_HUB_DIR" || { echo "kakaocloud: Confluent Hub 디렉토리 이동 실패"; exit 1; }
aria2c -x 16 -s 16 -o "$CONFLUENT_HUB_FILE" "$CONFLUENT_HUB_URL" || { echo "kakaocloud: Confluent Hub Client 다운로드 실패"; exit 1; }
sudo tar -zxf "$CONFLUENT_HUB_FILE" || { echo "kakaocloud: Confluent Hub Client 압축 해제 실패"; exit 1; }
sudo chown -R ubuntu:ubuntu /confluent-hub || { echo "kakaocloud: Confluent Hub 소유권 변경 실패"; exit 1; }

################################################################################
# 6. .bashrc에 JAVA_HOME 및 PATH 등록
################################################################################
echo "kakaocloud: 6. Java 환경 변수 등록 시작"
sed -i '/^export JAVA_HOME=/d' /home/ubuntu/.bashrc
sed -i '/^export PATH=.*\\$JAVA_HOME\/bin/d' /home/ubuntu/.bashrc
sed -i '/^export CLASSPATH=.*\\$JAVA_HOME/d' /home/ubuntu/.bashrc

cat <<EOF >> /home/ubuntu/.bashrc
export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
export PATH="\$JAVA_HOME/bin:\$PATH"
export CLASSPATH="\$CLASSPATH:\$JAVA_HOME/lib/ext:\$JAVA_HOME/tools.jar"
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: Java 환경 변수 등록 실패"; exit 1; fi
source /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 재적용 실패"; exit 1; }

################################################################################
# 7. 임시 connect-standalone.properties 파일 생성 (Confluent Hub Client 요구사항 충족용)
################################################################################
sudo mkdir -p "${KAFKA_INSTALL_DIR}/config" || { echo "kakaocloud: Kafka Connect config 디렉토리 생성 실패"; exit 1; }
cat <<EOF > "${KAFKA_INSTALL_DIR}/config/connect-standalone.properties"
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVERS}
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false
offset.storage.file.filename=/tmp/connect.offsets
offset.flush.interval.ms=10000
plugin.path=/confluent-hub/plugins
listeners=http://0.0.0.0:${CONNECT_REST_PORT}
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: 임시 connect-standalone.properties 생성 실패"; exit 1; fi
sudo chown ubuntu:ubuntu "${KAFKA_INSTALL_DIR}/config/connect-standalone.properties" || { echo "kakaocloud: 임시 connect-standalone.properties 권한 변경 실패"; exit 1; }


################################################################################
# 8. S3 Sink Connector 설치
################################################################################
echo "kakaocloud: 7. S3 Sink Connector 설치 시작"
/confluent-hub/bin/confluent-hub install confluentinc/kafka-connect-s3:latest \
  --component-dir /confluent-hub/plugins \
  --worker-configs "${KAFKA_INSTALL_DIR}/config/connect-standalone.properties" \
  --no-prompt || { echo "kakaocloud: S3 Sink Connector 설치 실패"; exit 1; }

################################################################################
# 9. AWS CLI 설치
################################################################################
echo "kakaocloud: 8. AWS CLI 설치 시작"
cd /home/ubuntu || { echo "kakaocloud: 홈 디렉토리 이동 실패"; exit 1; }
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip" -o "${AWS_CLI_ZIP}" || { echo "kakaocloud: AWS CLI 다운로드 실패"; exit 1; }
unzip "${AWS_CLI_ZIP}" || { echo "kakaocloud: AWS CLI 압축 해제 실패"; exit 1; }
sudo ./aws/install || { echo "kakaocloud: AWS CLI 설치 실패"; exit 1; }
rm -rf aws "${AWS_CLI_ZIP}" || { echo "kakaocloud: AWS CLI 설치 후 정리 실패"; exit 1; }
AWS_VERSION=$(aws --version 2>&1 || true)

################################################################################
# 10. AWS CLI configure 파일 설정
################################################################################
echo "kakaocloud: 9. AWS CLI 설정 시작"
sudo -u ubuntu -i aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID_VALUE" || { echo "kakaocloud: AWS CLI aws_access_key_id 설정 실패"; exit 1; }
sudo -u ubuntu -i aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY_VALUE" || { echo "kakaocloud: AWS CLI aws_secret_access_key 설정 실패"; exit 1; }
sudo -u ubuntu -i aws configure set default.region "$AWS_DEFAULT_REGION_VALUE" || { echo "kakaocloud: AWS CLI default.region 설정 실패"; exit 1; }
sudo -u ubuntu -i aws configure set default.output "$AWS_DEFAULT_OUTPUT_VALUE" || { echo "kakaocloud: AWS CLI default.output 설정 실패"; exit 1; }
source /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 재적용 실패"; exit 1; }

################################################################################
# 11. Kafka Connect 설정 폴더 권한 부여
################################################################################
echo "kakaocloud: 10. Kafka Connect 설정 폴더 권한 부여 시작"
sudo mkdir -p "${KAFKA_INSTALL_DIR}/config" || { echo "kakaocloud: Kafka 설정 폴더 생성 실패"; exit 1; }
sudo chown -R ubuntu:ubuntu "${KAFKA_INSTALL_DIR}" || { echo "kakaocloud: Kafka 설치 디렉토리 권한 변경 실패"; exit 1; }

################################################################################
# 12. 커스텀 파티셔너, 파일네임 플러그인 다운로드 (선택적)
################################################################################
echo "kakaocloud: 11. 커스텀 플러그인 다운로드 시작"
sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-partitioner-1.0-SNAPSHOT.jar \
  "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab03/kafka_connector/custom-partitioner-1.0-SNAPSHOT.jar" || { echo "kakaocloud: custom-partitioner 다운로드 실패"; exit 1; }
sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-filename-1.0-SNAPSHOT.jar \
  "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab03/kafka_connector/custom-filename-1.0-SNAPSHOT.jar" || { echo "kakaocloud: custom-filename 다운로드 실패"; exit 1; }

################################################################################
# 13. s3-sink-connector.json 생성 (Distributed 모드용)
################################################################################
echo "kakaocloud: 12. s3-sink-connector.json 생성 시작"
cat <<EOF > "${KAFKA_INSTALL_DIR}/config/s3-sink-connector.json"
{
  "name": "s3-sink-connector-shopdb-all-tables",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "1",
    "topics": "${DEBEZIUM_TOPICS}",
    "s3.region": "${AWS_DEFAULT_REGION_VALUE}",
    "s3.bucket.name": "${BUCKET_NAME}",
    "s3.part.size": "5242880",
    "aws.access.key.id": "${AWS_ACCESS_KEY_ID_VALUE}",
    "aws.secret.access.key": "${AWS_SECRET_ACCESS_KEY_VALUE}",
    "store.url": "https://objectstorage.${AWS_DEFAULT_REGION_VALUE}.kakaocloud.com",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter.schemas.enable": "false",
    "flush.size": "10",
    "rotate.schedule.interval.ms": "5000",
    "timestamp.extractor": "RecordField",
    "timestamp.field": "ts_ms",
    "topics.dir": "raw_cdc_events",
    "path.format": "shopdb/${topic}/year=yyyy/month=MM/day=dd/hour=HH",
    "locale": "en-US",
    "timezone": "Asia/Seoul",
    "behavior.on.null.values": "ignore"
  }
}
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: s3-sink-connector.json 생성 실패"; exit 1; fi
sudo chown ubuntu:ubuntu "${KAFKA_INSTALL_DIR}/config/s3-sink-connector.json" || { echo "소유권 변경 실패"; exit 1; }


################################################################################
# 14. worker.properties 생성 (Distributed 모드용)
################################################################################
echo "kakaocloud: 13. worker.properties 생성 시작"
cat <<EOF > "${KAFKA_INSTALL_DIR}/config/worker.properties"
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVERS}

# Distributed 모드 관련 필수 설정
group.id=connect-cluster-s3-sink
config.storage.topic=connect-configs-s3
offset.storage.topic=connect-offsets-s3
status.storage.topic=connect-statuses-s3

# 개발/테스트 환경에서는 복제 인자 1로 시작 가능. 프로덕션은 3 이상 권장.
config.storage.replication.factor=1
offset.storage.replication.factor=1
status.storage.replication.factor=1

# Kafka Connect 내부 데이터 변환기 (스키마를 포함하지 않는 JSON)
internal.key.converter=org.apache.kafka.connect.json.JsonConverter
internal.value.converter=org.apache.kafka.connect.json.JsonConverter
internal.key.converter.schemas.enable=false
internal.value.converter.schemas.enable=false

# Kafka 토픽 데이터 변환기 (S3 Sink에 적합한 JSON)
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false

# 오프셋 커밋 주기
offset.flush.interval.ms=10000
offset.flush.timeout.ms=5000

# 플러그인 경로
plugin.path=/confluent-hub/plugins

# REST API 리스너 설정
listeners=http://0.0.0.0:${CONNECT_REST_PORT}
rest.advertised.host.name=$(hostname -I | awk '{print $1}')
rest.advertised.port=${CONNECT_REST_PORT}
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: worker.properties 생성 실패"; exit 1; fi
sudo chown ubuntu:ubuntu "${KAFKA_INSTALL_DIR}/config/worker.properties" || { echo "소유권 변경 실패"; exit 1; }


################################################################################
# 15. kafka-connect systemd 서비스 등록
################################################################################
echo "kakaocloud: 14. Kafka Connect 서비스 등록 시작"
cat <<EOF | sudo tee /etc/systemd/system/kafka-connect.service
[Unit]
Description=Kafka Connect Distributed Service
After=network.target

[Service]
User=ubuntu
ExecStart=${KAFKA_INSTALL_DIR}/bin/connect-distributed.sh \
  ${KAFKA_INSTALL_DIR}/config/worker.properties
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: Kafka Connect 서비스 등록 실패"; exit 1; fi

################################################################################
# 16. Schema Registry 관련
################################################################################
echo "kakaocloud: 15. Schema Registry 관련 설치 건너뜀 (JSON 포맷 사용)"
# 이 섹션은 완전히 비워둠 (이전 스크립트에서 불필요한 설치/설정 로직 제거됨)


echo "kakaocloud: Setup 완료"
