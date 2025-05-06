#!/usr/bin/env bash
set -euo pipefail

CONFLUENT_VERSION="7.5.3"
CONFLUENT_HOME="/opt/confluent"
SCHEMA_REGISTRY_PROP="${CONFLUENT_HOME}/etc/schema-registry/schema-registry.properties"
SYSTEMD_SR_UNIT="/etc/systemd/system/schema-registry.service"
LOGSTASH_SCHEMA_DIR="/etc/logstash/schema"
AVSC_FILE="${LOGSTASH_SCHEMA_DIR}/nginx_log.avsc"
LOGSTASH_CONF="/etc/logstash/conf.d/logs-to-kafka.conf"

# 1. Java & Confluent 설치
sudo apt-get update -y
sudo apt-get install -y openjdk-11-jdk wget

sudo wget -q "https://packages.confluent.io/archive/${CONFLUENT_VERSION}/confluent-community-${CONFLUENT_VERSION}.tar.gz"
sudo tar -xzf "confluent-community-${CONFLUENT_VERSION}.tar.gz"
sudo mv "confluent-${CONFLUENT_VERSION}" "${CONFLUENT_HOME}"
sudo rm "confluent-community-${CONFLUENT_VERSION}.tar.gz"

# 환경변수
sudo grep -qxF "export CONFLUENT_HOME=${CONFLUENT_HOME}" /home/ubuntu/.bashrc || \
  echo "export CONFLUENT_HOME=${CONFLUENT_HOME}" >> /home/ubuntu/.bashrc
sudo grep -qxF 'export PATH=$PATH:$CONFLUENT_HOME/bin' /home/ubuntu/.bashrc || \
  echo 'export PATH=$PATH:$CONFLUENT_HOME/bin' >> /home/ubuntu/.bashrc
export CONFLUENT_HOME="${CONFLUENT_HOME}"
export PATH="$PATH:${CONFLUENT_HOME}/bin"

# 2. Schema Registry 설정 & 서비스 등록
sudo sed -i \
  "s|PLAINTEXT://localhost:9092|10.0.3.189:9092,10.0.2.254:9092|g" \
  "${SCHEMA_REGISTRY_PROP}"

tee "${SYSTEMD_SR_UNIT}" > /dev/null <<'EOF'
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

systemctl daemon-reload
systemctl enable schema-registry.service
systemctl start  schema-registry.service

# 3. Logstash Avro Codec & 스키마
sudo /usr/share/logstash/bin/logstash-plugin install --no-verify logstash-codec-avro_schema_registry

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
    { "name":"status",  "type":[ "null", "string", "int" ], "default": null },
    { "name":"body_bytes_sent", "type":[ "null", "string", "int" ], "default": null },
    { "name":"http_referer", "type":[ "null","string" ],  "default": null },
    { "name":"http_user_agent","type":"string" },
    { "name":"session_id","type":[ "null","string" ],  "default": null },
    { "name":"user_id","type":[ "null","string" ],  "default": null },
    { "name":"age","type":[ "null", "string", "int" ], "default": null },
    { "name":"gender","type":[ "null","string" ],  "default": null },
    { "name":"request_time","type":[ "null", "string", "double" ], "default": null },
    { "name":"upstream_response_time","type":[ "null", "string", "double" ], "default": null },
    { "name":"endpoint","type":"string" },
    { "name":"method","type":"string" },
    { "name":"query_params","type":[ "null","string" ],  "default": null },
    { "name":"product_id","type":[ "null","string" ],  "default": null },
    { "name":"request_body","type":[ "null","string" ],  "default": null },
    { "name":"category","type":[ "null","string" ],  "default": null },
    { "name":"x_forwarded_for","type":[ "null","string" ],  "default": null },
    { "name":"host","type":"string" }
  ]
}
EOF

sudo tee "${LOGSTASH_CONF}" > /dev/null <<'EOF'
input { beats { port => 5045 } }
filter {
  json { source => "message" remove_field => ["message"] }
  if "_jsonparsefailure" in [tags] { drop {} }
  if [timestamp] {
    date { match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ] target => "timestamp" }
    ruby { code => "event.set('timestamp', event.get('timestamp').time.strftime('%Y-%m-%d %H:%M:%S'))" }
  }
  mutate { convert => { "status"=>"integer" "body_bytes_sent"=>"integer" "request_time"=>"float" "upstream_response_time"=>"float" } }
  mutate { remove_field => ["@version","@timestamp","agent","cloud","ecs","input","log","tags"] }
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

sudo systemctl restart logstash
echo "=== 설정 완료 ==="
