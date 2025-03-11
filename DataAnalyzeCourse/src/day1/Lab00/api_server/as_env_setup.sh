#!/bin/bash

# 하나라도 실패하면 종료
set -e
set -o pipefail

###############################################################################
# 로그 설정
###############################################################################
LOGFILE="/home/ubuntu/as_script.log"

# log 함수: 메시지를 화면 + 로그 파일에 동시에 출력
log() {
  local MESSAGE="[`date '+%Y-%m-%d %H:%M:%S'`] $1"
  echo "$MESSAGE"
  echo "$MESSAGE" >> "$LOGFILE"
}

echo "kakaocloud: 1. Writing environment variables to ~/.bashrc"

BASHRC_EXPORT=$(cat <<EOF
export MYSQL_HOST="$MYSQL_HOST"
export DOMAIN_ID="$DOMAIN_ID"
export PROJECT_ID="$PROJECT_ID"
export PUBSUB_TOPIC_NAME="$PUBSUB_TOPIC_NAME"
export KAFKA_TOPIC_NAME="$KAFKA_TOPIC_NAME"
export CREDENTIAL_ID="$CREDENTIAL_ID"
export CREDENTIAL_SECRET="$CREDENTIAL_SECRET"
export LOGSTASH_KAFKA_ENDPOINT="$LOGSTASH_KAFKA_ENDPOINT"
export LOGSTASH_ENV_FILE="$LOGSTASH_ENV_FILE"
EOF
)

echo "$BASHRC_EXPORT" >> /home/ubuntu/.bashrc

# 새로 추가된 값 반영
source /home/ubuntu/.bashrc
echo "kakaocloud: ~/.bashrc updated with environment variables."

###############################################################################
# 2) filebeat / logstash 설치 (기존 로직 그대로)
###############################################################################
log "kakaocloud: 2. Installing filebeat/logstash and appending environment variables"

curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add - \
  || { log "kakaocloud: Failed to add Elasticsearch GPG key"; exit 1; }

echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/beats.list > /dev/null \
  || { log "kakaocloud: Failed to add beats.list"; exit 1; }

sudo apt-get update \
  || { log "kakaocloud: apt-get update failed"; exit 1; }
sudo apt-get install -y filebeat logstash \
  || { log "kakaocloud: Failed to install filebeat & logstash"; exit 1; }

sudo systemctl enable filebeat \
  || { log "kakaocloud: Failed to enable filebeat"; exit 1; }
sudo systemctl start filebeat \
  || { log "kakaocloud: Failed to start filebeat"; exit 1; }

sudo systemctl enable logstash \
  || { log "kakaocloud: Failed to enable logstash"; exit 1; }
sudo systemctl start logstash \
  || { log "kakaocloud: Failed to start logstash"; exit 1; }

sudo chmod 777 /etc/default/logstash \
  || { log "kakaocloud: Failed to chmod /etc/default/logstash"; exit 1; }

cat <<EOF | sudo tee -a /etc/default/logstash > /dev/null \
  || { log "kakaocloud: Failed to add environment variables to /etc/default/logstash"; exit 1; }

# === Additional Env for Pub/Sub ===
CREDENTIAL_ID="$CREDENTIAL_ID"
CREDENTIAL_SECRET="$CREDENTIAL_SECRET"
DOMAIN_ID="$DOMAIN_ID"
PROJECT_ID="$PROJECT_ID"
PUBSUB_TOPIC_NAME="$PUBSUB_TOPIC_NAME"
KAFKA_TOPIC_NAME="$KAFKA_TOPIC_NAME"
LOGSTASH_KAFKA_ENDPOINT="$LOGSTASH_KAFKA_ENDPOINT"

export CREDENTIAL_ID CREDENTIAL_SECRET DOMAIN_ID PROJECT_ID TOPIC_NAME_PUBSUB KAFKA_TOPIC_NAME MYSQL_HOST LOGSTASH_KAFKA_ENDPOINT
EOF

sudo systemctl daemon-reload \
  || { log "kakaocloud: Failed systemctl daemon-reload"; exit 1; }
sudo systemctl restart logstash \
  || { log "kakaocloud: Failed to restart logstash"; exit 1; }

log "kakaocloud: filebeat / logstash installation and environment variable configuration complete"

###############################################################################
# 4) (선택) Flask 앱 서비스
###############################################################################
SERVICE_FILE="/etc/systemd/system/flask_app.service"
OVERRIDE_DIR="/etc/systemd/system/flask_app.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/env.conf"

log "kakaocloud: 4. Setting environment variables for flask_app.service"

if [ -f "$SERVICE_FILE" ]; then
  sudo mkdir -p "$OVERRIDE_DIR" \
    || { log "kakaocloud: Failed to create $OVERRIDE_DIR"; exit 1; }
  cat <<EOF | sudo tee "$OVERRIDE_FILE" > /dev/null \
    || { log "kakaocloud: Failed to override flask_app.service env"; exit 1; }
[Service]
Environment="MYSQL_HOST=$MYSQL_HOST"
Environment="DOMAIN_ID=$DOMAIN_ID"
Environment="PROJECT_ID=$PROJECT_ID"
Environment="PUBSUB_TOPIC_NAME=$PUBSUB_TOPIC_NAME"
Environment="KAFKA_TOPIC_NAME=$KAFKA_TOPIC_NAME"
Environment="CREDENTIAL_ID=$CREDENTIAL_ID"
Environment="CREDENTIAL_SECRET=$CREDENTIAL_SECRET"
EOF

  sudo systemctl daemon-reload \
    || { log "kakaocloud: Failed systemctl daemon-reload for flask_app"; exit 1; }
  sudo systemctl restart flask_app \
    || { log "kakaocloud: Failed to restart flask_app.service"; exit 1; }
  log "kakaocloud: flask_app.service restarted"
else
  log "kakaocloud: flask_app.service does not exist, skipping override"
fi

###############################################################################
# 5) main_script.sh & setup_db.sh (Sparse-checkout로 api_server 폴더만 가져옴)
###############################################################################
log "kakaocloud: 5. Checking out only 'DataAnalyzeCourse/src/day1/Lab00/api_server' folder using git sparse-checkout"

# 1) sparse-checkout 준비: lab0-api-server 디렉터리에 git init
if [ ! -d "/home/ubuntu/lab0-api-server/.git" ]; then
  mkdir -p /home/ubuntu/lab0-api-server
  cd /home/ubuntu/lab0-api-server
  git init
  git remote add origin https://github.com/kakaocloud-edu/tutorial.git
  git config core.sparseCheckout true

  # sparse-checkout 설정: 필요한 폴더만
  echo "DataAnalyzeCourse/src/day1/Lab00/api_server" >> .git/info/sparse-checkout

  # main 브랜치(또는 필요한 브랜치) pull
  git pull origin main
else
  # 이미 sparse-checkout이 완료된 상태라면 pull 업데이트
  cd /home/ubuntu/lab0-api-server
  git pull origin main
fi

# 2) 이제 /home/ubuntu/lab0-api-server/DataAnalyzeCourse/src/day1/Lab00/api_server 안에 필요한 파일 존재
sudo cp /home/ubuntu/lab0-api-server/DataAnalyzeCourse/src/day1/Lab00/api_server/api_full_setup.sh /home/ubuntu/api_full_setup.sh || {
  log "Failed to copy api_full_setup.sh"
  exit 1
}
sudo cp /home/ubuntu/lab0-api-server/DataAnalyzeCourse/src/day1/Lab00/api_server/setup_db.sh /home/ubuntu/setup_db.sh || {
  log "Failed to copy setup_db.sh"
  exit 1
}
sudo cp /home/ubuntu/lab0-api-server/DataAnalyzeCourse/src/day1/Lab00/api_server/filebeat.yml /etc/filebeat/filebeat.yml || {
  log "Failed to copy filebeat.yml"
  exit 1
}
sudo cp /home/ubuntu/lab0-api-server/DataAnalyzeCourse/src/day1/Lab00/api_server/logs-to-pubsub.conf /etc/logstash/conf.d/logs-to-pubsub.conf || {
  log "Failed to copy logs-to-pubsub.conf"
  exit 1
}
sudo cp /home/ubuntu/lab0-api-server/DataAnalyzeCourse/src/day1/Lab00/api_server/logs-to-kafka.conf /etc/logstash/conf.d/logs-to-kafka.conf || {
  log "Failed to copy logs-to-kafka.conf"
  exit 1
}

chmod +x /home/ubuntu/api_full_setup.sh /home/ubuntu/setup_db.sh \
  || { log "Failed to chmod main_script.sh or setup_db.sh"; exit 1; }

log "kakaocloud: Executing main_script.sh & setup_db.sh with environment variables"
cd /home/ubuntu
sudo -E ./api_full_setup.sh \
  || { log "kakaocloud: api_full_setup.sh execution failed"; exit 1; }
sudo -E ./setup_db.sh \
  || { log "kakaocloud: setup_db.sh execution failed"; exit 1; }
log "kakaocloud: main_script.sh & setup_db.sh completed"

###############################################################################
# 6) Additional logstash.yml overwrite
###############################################################################
sudo tee /etc/logstash/logstash.yml <<'EOF' > /dev/null \
  || { log "kakaocloud: Failed to write logstash.yml"; exit 1; }
path.data: /var/lib/logstash
path.logs: /var/log/logstash
path.config: /etc/logstash/conf.d/logs-to-pubsub.conf
EOF

log "kakaocloud: Overwrote /etc/logstash/logstash.yml"

sudo systemctl restart filebeat \
  || { log "kakaocloud: Failed to restart filebeat"; exit 1; }
sudo systemctl restart logstash \
  || { log "kakaocloud: Failed to restart logstash"; exit 1; }

log "kakaocloud: All steps in as_env_setup.sh have completed successfully"
