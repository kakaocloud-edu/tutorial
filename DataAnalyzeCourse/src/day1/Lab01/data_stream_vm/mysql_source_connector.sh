#!/bin/bash

#------------------------------------------
# 0. 초기 환경 설정 및 로그 리디렉션
#------------------------------------------
# 환경 변수 파일을 소싱하여 설정 로드 (외부 스크립트에 의해 실행될 때)
# 이 스크립트가 직접 실행될 경우를 대비해 한번 더 source.
if [ -f "/tmp/env_vars.sh" ]; then
    source /tmp/env_vars.sh
    # LOGFILE 변수가 env_vars.sh에 정의되어 있다고 가정
    if [ -z "$LOGFILE" ]; then
        LOGFILE="/home/ubuntu/setup_mysql_source_connector.log"
    fi
else
    # env_vars.sh가 없는 경우를 대비한 기본 LOGFILE
    LOGFILE="/home/ubuntu/setup_mysql_source_connector.log"
    echo "kakaocloud: 경고: /tmp/env_vars.sh 파일을 찾을 수 없습니다. 환경 변수가 외부에서 설정되어야 합니다."
fi

exec > >(tee -a "$LOGFILE") 2>&1

#------------------------------------------
# 1. 메인 스크립트 내부 설정 변수 (env_vars.sh에서 오지 않는 값들)
#------------------------------------------
# Kafka Connect 및 Debezium 관련 설정
KAFKA_VERSION="3.7.1"
KAFKA_SCALA_VERSION="2.13"
KAFKA_TGZ="kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz"
KAFKA_DOWNLOAD_URL="https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${KAFKA_TGZ}"
KAFKA_INSTALL_DIR="/home/ubuntu/kafka"

DEBEZIUM_MYSQL_CONNECTOR_VERSION="3.0.2.Final"
DEBEZIUM_MYSQL_CONNECTOR_URL="https://repo1.maven.org/maven2/io/debezium/debezium-connector-mysql/${DEBEZIUM_MYSQL_CONNECTOR_VERSION}/debezium-connector-mysql-${DEBEZIUM_MYSQL_CONNECTOR_VERSION}-plugin.tar.gz"
DEBEZIUM_MYSQL_CONNECTOR_TGZ="debezium-connector-mysql-${DEBEZIUM_MYSQL_CONNECTOR_VERSION}-plugin.tar.gz"

# 이 VM의 Kafka Connect REST API 포트
CONNECT_REST_PORT="8084"

#------------------------------------------
# 2. 필수 환경변수 검증 (env_vars.sh에서 로드되는 변수들)
#------------------------------------------
required_env_vars=(
  KAFKA_BOOTSTRAP_SERVER
  MYSQL_DB_HOSTNAME MYSQL_DB_PORT MYSQL_DB_USER MYSQL_DB_PASSWORD
  MYSQL_SERVER_ID MYSQL_SERVER_NAME
)

echo "kakaocloud: 3. 필수 환경 변수 검증 시작"
for var in "${required_env_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "kakaocloud: 오류: 필수 환경 변수 $var 가 설정되지 않았습니다. 스크립트를 종료합니다."
        exit 1
    fi
done

# KAFKA_BOOTSTRAP_SERVER 변수 이름을 KAFKA_BOOTSTRAP_SERVERS로 통일 (내부적으로)
KAFKA_BOOTSTRAP_SERVERS="$KAFKA_BOOTSTRAP_SERVER"


################################################################################
# 3. 시스템 업데이트 및 필수 패키지 설치
################################################################################
echo "kakaocloud: 4. 시스템 업데이트 및 필수 패키지 설치 시작"
sudo apt update -y || { echo "kakaocloud: apt update 실패"; exit 1; }
sudo apt install -y python3 python3-pip openjdk-21-jdk unzip jq aria2 curl || { echo "kakaocloud: 필수 패키지 설치 실패"; exit 1; }

################################################################################
# 4. Kafka 다운로드 및 설치
################################################################################
echo "kakaocloud: 5. Kafka 설치 시작"
aria2c -x 16 -s 16 -d /home/ubuntu -o "${KAFKA_TGZ}" "${KAFKA_DOWNLOAD_URL}" || { echo "kakaocloud: Kafka 다운로드 실패"; exit 1; }
tar -xzf /home/ubuntu/"${KAFKA_TGZ}" -C /home/ubuntu || { echo "kakaocloud: Kafka 압축 해제 실패"; exit 1; }
rm /home/ubuntu/"${KAFKA_TGZ}" || { echo "kakaocloud: 임시 파일 삭제 실패"; exit 1; }
mv /home/ubuntu/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION} "${KAFKA_INSTALL_DIR}" || { echo "kakaocloud: Kafka 디렉토리 이동 실패"; exit 1; }

################################################################################
# 5. .bashrc에 JAVA_HOME 및 PATH 등록
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
# 6. Debezium MySQL 커넥터 플러그인 다운로드 및 설치
################################################################################
echo "kakaocloud: 7. Debezium MySQL Connector 플러그인 다운로드 및 설치 시작"
# Kafka Connect 플러그인 디렉토리 생성
sudo mkdir -p "${KAFKA_INSTALL_DIR}/plugins" || { echo "kakaocloud: Kafka Connect 플러그인 디렉토리 생성 실패"; exit 1; }
sudo chown -R ubuntu:ubuntu "${KAFKA_INSTALL_DIR}/plugins" || { echo "kakaocloud: 플러그인 디렉토리 권한 설정 실패"; exit 1; }

# Debezium MySQL Connector 플러그인 다운로드
sudo wget "${DEBEZIUM_MYSQL_CONNECTOR_URL}" -O "${DEBEZIUM_MYSQL_CONNECTOR_TGZ}" || { echo "kakaocloud: Debezium MySQL Connector 플러그인 다운로드 실패"; exit 1; }

# 다운로드된 플러그인 압축을 Kafka Connect 플러그인 디렉토리에 해제
sudo tar -xzf "${DEBEZIUM_MYSQL_CONNECTOR_TGZ}" -C "${KAFKA_INSTALL_DIR}/plugins/" || { echo "kakaocloud: Debezium 플러그인 압축 해제 실패"; exit 1; }

# 다운로드된 tar.gz 파일 삭제
sudo rm "${DEBEZIUM_MYSQL_CONNECTOR_TGZ}" || { echo "kakaocloud: 임시 Debezium tar.gz 파일 삭제 실패"; exit 1; }

ls -F "${KAFKA_INSTALL_DIR}/plugins/debezium-connector-mysql/" || { echo "kakaocloud: Debezium 플러그인 확인 실패"; exit 1; }


################################################################################
# 7. Kafka Connect 분산 모드 설정 (worker.properties)
################################################################################
echo "kakaocloud: 8. Kafka Connect 분산 모드 설정 (worker.properties) 시작"
cat <<EOF > "${KAFKA_INSTALL_DIR}/config/worker.properties"
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVERS}

group.id=connect-cluster-mysql-source
config.storage.topic=connect-configs-mysql
offset.storage.topic=connect-offsets-mysql
status.storage.topic=connect-statuses-mysql

config.storage.replication.factor=1
offset.storage.replication.factor=1
status.storage.replication.factor=1

internal.key.converter=org.apache.kafka.connect.json.JsonConverter
internal.value.converter=org.apache.kafka.connect.json.JsonConverter
internal.key.converter.schemas.enable=false
internal.value.converter.schemas.enable=false

key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false

offset.flush.interval.ms=10000
offset.flush.timeout.ms=5000

plugin.path=${KAFKA_INSTALL_DIR}/plugins

listeners=http://0.0.0.0:${CONNECT_REST_PORT}
rest.advertised.host.name=$(hostname -I | awk '{print $1}')
rest.advertised.port=${CONNECT_REST_PORT}
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: worker.properties 생성 실패"; exit 1; fi
# Kafka 설치 디렉토리 전체의 권한을 변경하여 생성된 config 파일들도 ubuntu 소유가 되도록 합니다.
sudo chown -R ubuntu:ubuntu "${KAFKA_INSTALL_DIR}" || { echo "kakaocloud: Kafka 설치 디렉토리 권한 변경 실패"; exit 1; }


################################################################################
# 8. Kafka Connect 시스템 서비스 등록 및 시작
################################################################################
echo "kakaocloud: 9. Kafka Connect 시스템 서비스 등록 및 시작"
sudo sh -c 'cat << EOF_SERVICE > /etc/systemd/system/kafka-connect.service
[Unit]
Description=Kafka Connect Distributed
Documentation=http://kafka.apache.org/
After=network.target kafka.service

[Service]
Type=simple
User=ubuntu
Environment="KAFKA_HEAP_OPTS=-Xms128M -Xmx512M"
ExecStart='${KAFKA_INSTALL_DIR}'/bin/connect-distributed.sh '${KAFKA_INSTALL_DIR}'/config/worker.properties
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF_SERVICE'
if [ $? -ne 0 ]; then echo "kakaocloud: Kafka Connect 서비스 파일 생성 실패"; exit 1; fi

sudo systemctl daemon-reload || { echo "kakaocloud: systemd daemon-reload 실패"; exit 1; }

sudo systemctl start kafka-connect || { echo "kakaocloud: Kafka Connect 서비스 시작 실패"; exit 1; }

sudo systemctl enable kafka-connect || { echo "kakaocloud: Kafka Connect 서비스 자동 시작 설정 실패"; exit 1; }

sudo systemctl status kafka-connect || { echo "kakaocloud: Kafka Connect 서비스 상태 확인 실패"; exit 1; }


################################################################################
# 9. Debezium Connector 구성 파일 생성 (REST API 배포용)
################################################################################
echo "kakaocloud: 10. Debezium Connector 구성 파일 생성 시작"
sudo mkdir -p "${KAFKA_INSTALL_DIR}/config/connectors" || { echo "kakaocloud: 커넥터 설정 디렉토리 생성 실패"; exit 1; }

# mysql-connector.json 파일 생성 또는 덮어쓰기
sudo tee "${KAFKA_INSTALL_DIR}/config/connectors/mysql-connector.json" << EOF_JSON
{
  "name": "mysql-cdc-shopdb",
  "config": {
    "connector.class":                          "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max":                                "1",
    "database.hostname":                        "${MYSQL_DB_HOSTNAME}",
    "database.port":                            "${MYSQL_DB_PORT}",
    "database.user":                            "${MYSQL_DB_USER}",
    "database.password":                        "${MYSQL_DB_PASSWORD}",
    "database.server.id":                       "${MYSQL_SERVER_ID}",
    "database.server.name":                     "${MYSQL_SERVER_NAME}",
    "topic.prefix":                             "${MYSQL_SERVER_NAME}",
    "database.include.list":                    "shopdb",
    "table.include.list":                       "shopdb.cart,shopdb.cart_logs,shopdb.orders,shopdb.products,shopdb.push_messages,shopdb.reviews,shopdb.search_logs,shopdb.sessions,shopdb.users,shopdb.users_logs",
    "schema.history.internal.kafka.bootstrap.servers": "${KAFKA_BOOTSTRAP_SERVERS}",
    "schema.history.internal.kafka.topic":      "schema-changes.shopdb",
    "topic.creation.enable":                    "true",
    "topic.creation.default.partitions":        "2",
    "topic.creation.default.replication.factor":"1",
    "tombstones.on.delete":                     "true",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter.schemas.enable": "false",
    "decimal.handling.mode": "string",
    "snapshot.mode": "initial"
  }
}
EOF_JSON
if [ $? -ne 0 ]; then echo "kakaocloud: mysql-connector.json 생성 실패"; exit 1; fi

echo "kakaocloud: Setup 완료"
