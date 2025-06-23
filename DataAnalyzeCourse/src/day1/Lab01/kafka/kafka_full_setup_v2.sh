#!/bin/bash

#------------------------------------------
# 설정 변수
#------------------------------------------
# Kafka 설정
KAFKA_VERSION="3.7.1"
KAFKA_SCALA_VERSION="2.13"
KAFKA_TGZ="kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz"
KAFKA_DOWNLOAD_URL="https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${KAFKA_TGZ}"
KAFKA_INSTALL_DIR="/home/ubuntu/kafka"

# Confluent Hub Client 설정
CONFLUENT_HUB_DIR="/confluent-hub"
CONFLUENT_HUB_URL="http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz"
CONFLUENT_HUB_FILE="confluent-hub-client-latest.tar.gz"

# AWS CLI 설정
AWS_CLI_VERSION="2.22.0"
AWS_CLI_ZIP="awscliv2.zip"
AWS_CLI_DOWNLOAD_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip"


#------------------------------------------
# 필수 환경변수 검증
#------------------------------------------
required_variables=(
  KAFKA_BOOTSTRAP_SERVER BUCKET_NAME
  AWS_ACCESS_KEY_ID_VALUE AWS_SECRET_ACCESS_KEY_VALUE
  AWS_DEFAULT_REGION_VALUE AWS_DEFAULT_OUTPUT_VALUE
)

echo "kakaocloud: 3. 필수 환경변수 검증 시작"
for var in "${required_variables[@]}"; do
    if [ -z "${!var}" ]; then
        echo "kakaocloud: 필수 환경변수 $var 가 설정되지 않았습니다. 스크립트를 종료합니다."
        exit 1
    fi
done

################################################################################
# 1. apt 업데이트 및 필수 패키지 설치
################################################################################
echo "kakaocloud: 4. 시스템 업데이트 및 필수 패키지 설치 시작"
sudo apt-get update -y || { echo "kakaocloud: apt-get update 실패"; exit 1; }
sudo apt-get install -y python3 python3-pip openjdk-21-jdk unzip jq aria2 curl || { echo "kakaocloud: 필수 패키지 설치 실패"; exit 1; }

################################################################################
# 2. Kafka 다운로드 및 설치
################################################################################
echo "kakaocloud: 5. Kafka 설치 시작"
aria2c -x 16 -s 16 -d /home/ubuntu -o "${KAFKA_TGZ}" "${KAFKA_DOWNLOAD_URL}" || { echo "kakaocloud: Kafka 다운로드 실패"; exit 1; }
tar -xzf /home/ubuntu/"${KAFKA_TGZ}" -C /home/ubuntu || { echo "kakaocloud: Kafka 압축 해제 실패"; exit 1; }
rm /home/ubuntu/"${KAFKA_TGZ}" || { echo "kakaocloud: 임시 파일 삭제 실패"; exit 1; }
mv /home/ubuntu/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION} "${KAFKA_INSTALL_DIR}" || { echo "kakaocloud: Kafka 디렉토리 이동 실패"; exit 1; }

################################################################################
# 3. Confluent Hub Client 설치
################################################################################
echo "kakaocloud: 6. Confluent Hub Client 설치 시작"
sudo mkdir -p /confluent-hub/plugins || { echo "kakaocloud: Confluent Hub 디렉토리 생성 실패"; exit 1; }
sudo mkdir -p "$CONFLUENT_HUB_DIR" || { echo "kakaocloud: Confluent Hub 디렉토리 생성 실패"; exit 1; }
cd "$CONFLUENT_HUB_DIR" || { echo "kakaocloud: Confluent Hub 디렉토리 이동 실패"; exit 1; }
aria2c -x 16 -s 16 -o "$CONFLUENT_HUB_FILE" "$CONFLUENT_HUB_URL" || { echo "kakaocloud: Confluent Hub Client 다운로드 실패"; exit 1; }
sudo tar -zxf "$CONFLUENT_HUB_FILE" || { echo "kakaocloud: Confluent Hub Client 압축 해제 실패"; exit 1; }
sudo chown -R ubuntu:ubuntu /confluent-hub || { echo "kakaocloud: Confluent Hub 소유권 변경 실패"; exit 1; }

################################################################################
# 4. .bashrc에 환경 변수 등록
################################################################################
echo "kakaocloud: 7. 환경 변수 등록 시작"
# 기존 관련 라인 제거
sed -i '/S3_ACCESS_KEY=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/S3_SECRET_ACCESS_KEY=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/AWS_DEFAULT_REGION=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/AWS_DEFAULT_OUTPUT=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/CONFLUENT_HOME=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }
sed -i '/JAVA_HOME=/d' /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 수정 실패"; exit 1; }

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
if [ $? -ne 0 ]; then echo "kakaocloud: 환경 변수 등록 실패"; exit 1; fi

################################################################################
# 5. .bashrc 적용 (비인터랙티브 환경 대비)
################################################################################
source /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 적용 실패"; exit 1; }

################################################################################
# 5.5. 임시 connect-standalone.properties 파일 생성 (Confluent Hub Client 요구사항 충족용)
# Distributed 모드에서는 이 파일을 실제 Kafka Connect 워커가 사용하지 않지만,
# 'confluent-hub install' 명령이 Kafka Connect 설치 경로를 감지하는 데 필요함.
################################################################################
echo "kakaocloud: 5.5. 임시 connect-standalone.properties 파일 생성 시작"
cat <<EOF > /home/ubuntu/kafka/config/connect-standalone.properties
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVER}
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false
offset.storage.file.filename=/tmp/connect.offsets
offset.flush.interval.ms=10000
plugin.path=/confluent-hub/plugins
listeners=http://0.0.0.0:8083
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: 임시 connect-standalone.properties 생성 실패"; exit 1; fi
sudo chown ubuntu:ubuntu /home/ubuntu/kafka/config/connect-standalone.properties || { echo "kakaocloud: 임시 connect-standalone.properties 권한 변경 실패"; exit 1; }


################################################################################
# 6. S3 Sink Connector 설치
################################################################################
echo "kakaocloud: 8. S3 Sink Connector 설치 시작"
# --worker-configs 인자를 임시로 생성한 connect-standalone.properties 파일로 지정
/confluent-hub/bin/confluent-hub install confluentinc/kafka-connect-s3:latest \
  --component-dir /confluent-hub/plugins \
  --worker-configs /home/ubuntu/kafka/config/connect-standalone.properties \
  --no-prompt || { echo "kakaocloud: S3 Sink Connector 설치 실패"; exit 1; }

################################################################################
# 7. AWS CLI 설치
################################################################################
echo "kakaocloud: 9. AWS CLI 설치 시작"
cd /home/ubuntu || { echo "kakaocloud: 홈 디렉토리 이동 실패"; exit 1; }
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip" -o "${AWS_CLI_ZIP}" || { echo "kakaocloud: AWS CLI 다운로드 실패"; exit 1; }
unzip "${AWS_CLI_ZIP}" || { echo "kakaocloud: AWS CLI 압축 해제 실패"; exit 1; }
sudo ./aws/install || { echo "kakaocloud: AWS CLI 설치 실패"; exit 1; }
rm -rf aws "${AWS_CLI_ZIP}" || { echo "kakaocloud: AWS CLI 설치 후 정리 실패"; exit 1; }
AWS_VERSION=$(aws --version 2>&1 || true)

################################################################################
# 8. AWS CLI configure 파일 설정
################################################################################
echo "kakaocloud: 10. AWS CLI 설정 시작"
sudo -u ubuntu -i aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID_VALUE" || { echo "kakaocloud: AWS CLI aws_access_key_id 설정 실패"; exit 1; }
sudo -u ubuntu -i aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY_VALUE" || { echo "kakaocloud: AWS CLI aws_secret_access_key 설정 실패"; exit 1; }
sudo -u ubuntu -i aws configure set default.region "$AWS_DEFAULT_REGION_VALUE" || { echo "kakaocloud: AWS CLI default.region 설정 실패"; exit 1; }
sudo -u ubuntu -i aws configure set default.output "$AWS_DEFAULT_OUTPUT_VALUE" || { echo "kakaocloud: AWS CLI default.output 설정 실패"; exit 1; }
AWS_VERSION=$(aws --version 2>&1)
source /home/ubuntu/.bashrc || { echo "kakaocloud: .bashrc 재적용 실패"; exit 1; }

################################################################################
# 9. Kafka 설정 폴더 생성 및 권한 부여
################################################################################
echo "kakaocloud: 11. Kafka 설정 폴더 생성 및 권한 부여 시작"
sudo mkdir -p /opt/kafka/config || { echo "kakaocloud: Kafka 설정 폴더 생성 실패"; exit 1; }
sudo chown -R ubuntu:ubuntu /opt/kafka || { echo "kakaocloud: Kafka 설정 폴더 권한 변경 실패"; exit 1; }

################################################################################
# 10. 커스텀 파티셔너, 파일네임 플러그인 다운로드
################################################################################
echo "kakaocloud: 12. 커스텀 플러그인 다운로드 시작 (JSON 포맷에서는 보통 불필요)"
# 이 커스텀 플러그인들이 S3 Sink Connector의 lib 디렉토리에 설치되도록 경로를 지정
sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-partitioner-1.0-SNAPSHOT.jar \
  "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab03/kafka_connector/custom-partitioner-1.0-SNAPSHOT.jar" || { echo "kakaocloud: custom-partitioner 다운로드 실패"; exit 1; }
sudo wget -O /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib/custom-filename-1.0-SNAPSHOT.jar \
  "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab03/kafka_connector/custom-filename-1.0-SNAPSHOT.jar" || { echo "kakaocloud: custom-filename 다운로드 실패"; exit 1; }

################################################################################
# 11. s3-sink-connector.json 생성
################################################################################
echo "kakaocloud: 13. s3-sink-connector.json 생성 시작"
# Distributed 모드에서는 .properties 파일 대신 JSON을 사용하며, 환경 변수를 직접 삽입
cat <<EOF > /opt/kafka/config/s3-sink-connector.json
{
  "name": "s3-sink-connector-shopdb-users",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "1",
    "topics": "mysql-server-lsh.shopdb.users",
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
    "flush.size": "1000",
    "timestamp.extractor": "RecordField",
    "timestamp.field": "ts_ms",
    "topics.dir": "raw_cdc_events",
    "path.format": "'shopdb'/'users'/'year='yyyy/'month='MM/'day='dd/'hour='HH",
    "locale": "en-US",
    "timezone": "Asia/Seoul"
    // "custom.replacements": "==:_" // 필요시 주석 해제 (파일명에 영향을 줄 수 있음)
    // "partitioner.class": "com.mycompany.connect.FlexibleTimeBasedPartitioner" // custom partitioner를 사용할 경우 활성화
  }
}
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: s3-sink-connector.json 생성 실패"; exit 1; fi


################################################################################
# 12. worker.properties 생성 (Distributed 모드용)
################################################################################
echo "kakaocloud: 14. worker.properties 생성 시작 (Distributed 모드)"
cat <<EOF > /opt/kafka/config/worker.properties
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVER}

# Distributed 모드 관련 필수 설정
group.id=connect-cluster-shopdb # 모든 워커는 동일한 group.id 사용
config.storage.topic=connect-configs # 커넥터 설정 저장 토픽
offset.storage.topic=connect-offsets # 오프셋 저장 토픽
status.storage.topic=connect-statuses # 커넥터 상태 저장 토픽

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
listeners=http://0.0.0.0:8083 # 워커와 커넥터 등록을 위한 API 엔드포인트
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: worker.properties 생성 실패"; exit 1; fi

################################################################################
# 13. kafka-connect systemd 서비스 등록 (Distributed 모드용으로 수정)
################################################################################
echo "kakaocloud: 15. Kafka Connect 서비스 등록 시작 (Distributed 모드)"
cat <<EOF | sudo tee /etc/systemd/system/kafka-connect.service
[Unit]
Description=Kafka Connect Distributed Service
After=network.target

[Service]
User=ubuntu
# connect-standalone.sh 대신 connect-distributed.sh 사용
ExecStart=/home/ubuntu/kafka/bin/connect-distributed.sh \
  /opt/kafka/config/worker.properties # worker.properties 파일만 전달
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: Kafka Connect 서비스 등록 실패"; exit 1; fi

################################################################################
# 14. Schema Registry 다운로드 및 설치 (JSON 포맷 사용 시 불필요하므로 주석 처리)
################################################################################
echo "kakaocloud: 16. Schema Registry 다운로드 및 설치 시작 (JSON 포맷 사용 시 불필요하므로 건너뜀)"
# sudo wget https://packages.confluent.io/archive/7.5/confluent-7.5.3.tar.gz || { echo "kakaocloud: Schema Registry 다운로드 실패"; exit 1; }
# sudo tar -xzvf confluent-7.5.3.tar.gz -C /confluent-hub/plugins || { echo "kakaocloud: Schema Registry 압축 해제 실패"; exit 1; }
# sudo rm confluent-7.5.3.tar.gz || { echo "kakaocloud: Schema Registry 압축파일 삭제 실패"; exit 1; }

################################################################################
# 15. systemd 유닛 파일 생성 및 Schema Registry 서비스 등록 (JSON 포맷 사용 시 불필요하므로 주석 처리)
################################################################################
echo "kakaocloud: 17. systemd 유닛 파일 생성 및 Schema Registry 서비스 등록 시작 (JSON 포맷 사용 시 불필요하므로 건너뜀)"
# cat <<EOF > /etc/systemd/system/schema-registry.service
# [Unit]
# Description=Confluent Schema Registry
# After=network.target

# [Service]
# Type=simple
# User=ubuntu
# ExecStart=/confluent-hub/plugins/confluent-7.5.3/bin/schema-registry-start /confluent-hub/plugins/confluent-7.5.3/etc/schema-registry/schema-registry.properties
# Restart=on-failure
# RestartSec=5s

# [Install]
# WantedBy=multi-user.target
# EOF
# if [ $? -ne 0 ]; then echo "kakaocloud: Schema Registry Service 파일 작성 실패"; exit 1; fi

# sudo systemctl daemon-reload || { echo "kakaocloud: daemon-reload 실패"; exit 1; }
# sudo systemctl enable schema-registry.service || { echo "kakaocloud: schema-registry 서비스 생성 실패"; exit 1; }
# sudo systemctl start schema-registry.service || { echo "kakaocloud: schema-registry 서비스 시작 실패"; exit 1; }

################################################################################
# 16. S3 커넥터 플러그인 경로에 Avro 컨버터 설치 및 설정 (JSON 포맷 사용 시 불필요하므로 주석 처리)
################################################################################
echo "kakaocloud: 18. Avro 컨버터 설치 및 설정 시작 (JSON 포맷 사용 시 불필요하므로 건너뜀)"
# sudo wget https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day2/Lab01/confluentinc-kafka-connect-avro-converter-7.5.3.zip || { echo "kakaocloud: confluentinc-kafka-connect-avro-converter 다운로드 실패"; exit 1; }
# unzip confluentinc-kafka-connect-avro-converter-7.5.3.zip || { echo "kakaocloud: confluentinc-kafka-connect-avro-converter 압축 해제 실패"; exit 1; }
# sudo rm confluentinc-kafka-connect-avro-converter-7.5.3.zip || { echo "kakaocloud: confluentinc-kafka-connect-avro-converter 압축파일 삭제 실패"; exit 1; }
# sudo mv confluentinc-kafka-connect-avro-converter-7.5.3/lib/*.jar /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib || { echo "kakaocloud: confluentinc-kafka-connect-avro-converter 파일 이동 실패"; exit 1; }
# sudo wget -P /confluent-hub/plugins/confluentinc-kafka-connect-s3/lib \
#   https://repo1.maven.org/maven2/com/google/guava/guava/30.1.1-jre/guava-30.1.1-jre.jar \
#   https://packages.confluent.io/maven/io/confluent/kafka-connect-protobuf-converter/7.5.3/kafka-connect-protobuf-converter-7.5.3.jar \
#   https://packages.confluent.io/maven/io/confluent/kafka-protobuf-serializer/7.5.3/kafka-protobuf-serializer-7.5.3.jar \
#   https://packages.confluent.io/maven/io/confluent/common-config/7.5.3/common-config-7.5.3.jar \
#   https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/3.25.1/protobuf-java-3.25.1.jar \
#   https://repo1.maven.org/maven2/com/google/guava/failureaccess/1.0.2/failureaccess-1.0.2.jar || { echo -e "\nERROR: S3 커넥터 추가 의존성 다운로드 실패"; exit 1; }

################################################################################
# 완료
################################################################################
echo "kakaocloud: Setup 완료"
