#!/usr/bin/env bash
set -euo pipefail

###############
# 환경설정
###############

CONFLUENT_VERSION="7.5.3"
CONFLUENT_HOME="/opt/confluent"
SCHEMA_REGISTRY_PROP="${CONFLUENT_HOME}/etc/schema-registry/schema-registry.properties"
SYSTEMD_SR_UNIT="/etc/systemd/system/schema-registry.service"
LOGSTASH_SCHEMA_DIR="/etc/logstash/schema"
LOGSTASH_CONF="/etc/logstash/conf.d/logs-to-kafka.conf"
AVSC_FILE="${LOGSTASH_SCHEMA_DIR}/nginx_log.avsc"

###############
# 1. Java & Confluent 설치
###############

echo "[1/8] apt 업데이트 및 Java 설치"
sudo apt-get update -y
sudo apt-get install -y openjdk-11-jdk wget

echo "[2/8] Confluent 패키지 다운로드 및 설치"
wget -q "https://packages.confluent.io/archive/${CONFLUENT_VERSION}/confluent-community-${CONFLUENT_VERSION}.tar.gz"
tar -xzf "confluent-community-${CONFLUENT_VERSION}.tar.gz"
sudo mv "confluent-${CONFLUENT_VERSION}" "${CONFLUENT_HOME}"
rm "confluent-community-${CONFLUENT_VERSION}.tar.gz"

echo "[3/8] 환경변수 설정"
grep -qxF "export CONFLUENT_HOME=${CONFLUENT_HOME}" ~/.bashrc || \
  echo "export CONFLUENT_HOME=${CONFLUENT_HOME}" >> ~/.bashrc
grep -qxF 'export PATH=$PATH:$CONFLUENT_HOME/bin' ~/.bashrc || \
  echo 'export PATH=$PATH:$CONFLUENT_HOME/bin' >> ~/.bashrc
# 현재 셸에도 적용
export CONFLUENT_HOME="${CONFLUENT_HOME}"
export PATH="$PATH:${CONFLUENT_HOME}/bin"

###############
# 2. Schema Registry 설정 & 서비스 등록
###############

echo "[4/8] schema-registry.properties 내 Kafka broker 주소 변경"
sudo sed -i \
  "s|PLAINTEXT://localhost:9092|10.0.3.189:9092,10.0.2.254:9092|g" \
  "${SCHEMA_REGISTRY_PROP}"

echo "[5/8] systemd 서비스 유닛 생성: ${SYSTEMD_SR_UNIT}"
sudo tee "${SYSTEMD_SR_UNIT}" > /dev/null <<'EOF'
[Unit]
Description=Confluent Schema Registry
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/opt/confluent/bin/schema-registry-start \
           /opt/confluent/etc/schema-registry/schema-registry.properties
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "[6/8] systemd 데몬 리로드 및 schema-registry 서비스 활성화/시작"
sudo systemctl daemon-reload
sudo systemctl enable schema-registry.service
sudo systemctl start  schema-registry.service

###############
# 3. Logstash Avro 플러그인 & 스키마
###############

echo "[7/8] Logstash Avro codec 플러그인 설치"
sudo /usr/share/logstash/bin/logstash-plugin install logstash-codec-avro_schema_registry

echo "[8/8] Avro 스키마 및 Logstash 설정 파일 생성"
sudo mkdir -p "${LOGSTASH_SCHEMA_DIR}"

sudo tee "${AVSC_FILE}" > /dev/null <<'EOF'
{
  "namespace": "nginx.log",
  "type": "record",
  "name": "NginxAccessLog",
  "fields": [
    { "name":"timestamp",              "type":"string" },
    { "name":"remote_addr",            "type":"string" },
    { "name":"request",                "type":"string" },
    {
      "name":"status",
      "type":[ "null", "string", "int" ],
      "default": null
    },
    {
      "name":"body_bytes_sent",
      "type":[ "null", "string", "int" ],
      "default": null
    },
    { "name":"http_referer",           "type":[ "null","string" ],  "default": null },
    { "name":"http_user_agent",        "type":"string" },
    { "name":"session_id",             "type":[ "null","string" ],  "default": null },
    { "name":"user_id",                "type":[ "null","string" ],  "default": null },
    {
      "name":"age",
      "type":[ "null", "string", "int" ],
      "default": null
    },
    { "name":"gender",                 "type":[ "null","string" ],  "default": null },
    {
      "name":"request_time",
      "type":[ "null", "string", "double" ],
      "default": null
    },
    {
      "name":"upstream_response_time",
      "type":[ "null", "string", "double" ],
      "default": null
    },
    { "name":"endpoint",               "type":"string" },
    { "name":"method",                 "type":"string" },
    { "name":"query_params",           "type":[ "null","string" ],  "default": null },
    { "name":"product_id",             "type":[ "null","string" ],  "default": null },
    { "name":"request_body",           "type":[ "null","string" ],  "default": null },
    { "name":"category",               "type":[ "null","string" ],  "default": null },
    { "name":"x_forwarded_for",        "type":[ "null","string" ],  "default": null },
    { "name":"host",                   "type":"string" }
  ]
}
EOF

sudo tee "${LOGSTASH_CONF}" > /dev/null <<'EOF'
input {
  beats {
    port => 5045
  }
}

filter {
  json {
    source       => "message"
    remove_field => ["message"]
  }

  if "_jsonparsefailure" in [tags] {
    drop { }
  }

  if [timestamp] {
    date {
      match  => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
      target => "timestamp"
    }
    ruby {
      code => "event.set('timestamp', event.get('timestamp').time.strftime('%Y-%m-%d %H:%M:%S'))"
    }
  }

  mutate {
    convert => {
      "status"                  => "integer"
      "body_bytes_sent"         => "integer"
      "request_time"            => "float"
      "upstream_response_time"  => "float"
    }
  }

  mutate {
    remove_field => [
      "@version", "@timestamp", "agent", "cloud", "ecs", "input", "log", "tags"
    ]
  }
}

output {
  kafka {
    bootstrap_servers => "${LOGSTASH_KAFKA_ENDPOINT}"
    topic_id          => "nginx-topic"

    codec => avro_schema_registry {
      endpoint        => "http://localhost:8081"
      schema_uri      => "/etc/logstash/schema/nginx_log.avsc"
      subject_name    => "nginx-topic-value"
      register_schema => true
    }
  }
}
EOF

echo "완료! 이제 Logstash를 재시작하세요:"
echo "  sudo systemctl restart logstash"
