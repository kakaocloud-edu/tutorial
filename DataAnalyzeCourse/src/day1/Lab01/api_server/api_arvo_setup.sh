#!/usr/bin/env bash
set -euo pipefail

# 환경설정
CONFLUENT_VERSION="7.5.3"
CONFLUENT_HOME="/opt/confluent"
SCHEMA_REGISTRY_PROP="${CONFLUENT_HOME}/etc/schema-registry/schema-registry.properties"
SYSTEMD_SR_UNIT="/etc/systemd/system/schema-registry.service"
LOGSTASH_SCHEMA_DIR="/etc/logstash/schema"
LOGSTASH_CONF="/etc/logstash/conf.d/logs-to-kafka.conf"
AVSC_FILE="${LOGSTASH_SCHEMA_DIR}/nginx_log.avsc"

# 1. Java & Confluent 설치
echo "apt 업데이트 및 Java 설치"
sudo apt-get update -y || {
    echo "kakaocloud: apt 업데이트 실패"; exit 1;
}
sudo apt-get install -y openjdk-11-jdk wget || {
    echo "kakaocloud: Java 설치 실패"; exit 1;
}

echo "Confluent 패키지 다운로드 및 설치"
sudo wget https://packages.confluent.io/archive/7.5/confluent-community-7.5.3.tar.gz || {
    echo "kakaocloud: Confluent 패키지 다운로드 실패"; exit 1;
}
sudo tar -xzvf confluent-community-7.5.3.tar.gz || {
    echo "kakaocloud: Confluent 패키지 압축 해제 실패"; exit 1;
}
sudo mv confluent-7.5.3 /opt/confluent || {
    echo "kakaocloud: Confluent 패키지 이동 실패"; exit 1;
}

echo "환경변수 설정"
grep -qxF "export CONFLUENT_HOME=${CONFLUENT_HOME}" ~/.bashrc || \
  echo 'export CONFLUENT_HOME=/opt/confluent' >> ~/.bashrc
grep -qxF 'export PATH=$PATH:$CONFLUENT_HOME/bin' ~/.bashrc || \
  echo 'export PATH=$PATH:$CONFLUENT_HOME/bin' >> ~/.bashrc
# 현재 셸에도 적용
export CONFLUENT_HOME="${CONFLUENT_HOME}"
export PATH="$PATH:${CONFLUENT_HOME}/bin"

# 2. Schema Registry 설정 & 서비스 등록
echo "schema-registry.properties 내 Kafka broker 주소 변경"
sudo sed -i "s|PLAINTEXT://localhost:9092|${LOGSTASH_KAFKA_ENDPOINT}|g" /opt/confluent/etc/schema-registry/schema-registry.properties || {
    echo "kakaocloud: Kafka broker 주소 변경 실패"; exit 1;
}

# 3. Logstash Avro 플러그인 & 스키마
echo "Logstash Avro codec 플러그인 설치"
sudo /usr/share/logstash/bin/logstash-plugin install logstash-codec-avro_schema_registry || {
    echo "kakaocloud: Logstash Avro codec 플러그인 설치 실패"; exit 1;
}

echo "Avro 스키마 및 Logstash 설정 파일 생성"
sudo mkdir -p /etc/logstash/schema || {
    echo "kakaocloud: Avro 스키마 및 Logstash 설정 파일 생성 실패"; exit 1;
}

sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server/nginx_log.avsc /etc/logstash/schema/nginx_log.avsc || {
    echo "kakaocloud: nginx_log.avsc 복사 실패"; exit 1;
}
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server/logs-to-kafka.conf /etc/logstash/conf.d/logs-to-kafka.conf || {
    echo "kakaocloud: logs-to-kafka.conf 복사 실패"; exit 1;
}

sudo systemctl restart logstash

echo "kakaocloud: 11. systemd 유닛 파일 생성 및 Schema Registry 서비스 등록 시작"
cat <<EOF | sudo tee /etc/systemd/system/schema-registry.service
[Unit]
Description=Confluent Schema Registry
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/opt/confluent/bin/schema-registry-start /opt/confluent/etc/schema-registry/schema-registry.properties
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: Schema Registry Service 파일 작성 실패"; exit 1; fi

sudo systemctl daemon-reload || { echo "kakaocloud: daemon-reload 실패"; exit 1; }
sudo systemctl enable schema-registry.service || { echo "kakaocloud: schema-registry 서비스 자동 시작 설정 실패"; exit 1; }
sudo systemctl start schema-registry.service || { echo "kakaocloud: schema-registry 서비스 시작 실패"; exit 1; }
sudo systemctl status schema-registry.service || { echo "kakaocloud: schema-registry 서비스 상태 확인 실패"; exit 1; }

# 실습에 사용되는 폴더만 남기기 위해 tutorial 리포지토리 삭제
sudo rm -rf /home/ubuntu/tutorial || {
    echo "kakaocloud: Failed to remove the tutorial repository"; exit 1;
}
