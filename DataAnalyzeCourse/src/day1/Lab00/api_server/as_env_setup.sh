#!/bin/bash

# 하나라도 실패하면 종료
set -e
# 파이프라인 중 하나라도 실패하면 전체 실패
set -o pipefail

###############################################################################
# 로그 설정
###############################################################################
LOGFILE="/home/ubuntu/as_script.log"

# log 함수: 메시지를 화면 + 로그 파일에 동시에 출력
log() {
  local MESSAGE="[`date '+%Y-%m-%d %H:%M:%S'`] $1"
  echo "$MESSAGE"            # 화면에 출력
  echo "$MESSAGE" >> "$LOGFILE"  # 로그 파일에만 기록
}

echo "kakaocloud: 1. ~/.bashrc에 환경 변수를 설정합니다."

BASHRC_EXPORT=$(cat <<EOF
export MYSQL_HOST="$MYSQL_HOST"
export DOMAIN_ID="$DOMAIN_ID"
export PROJECT_ID="$PROJECT_ID"
export PUBSUB_TOPIC_NAME="$PUBSUB_TOPIC_NAME"
export KAFKA_TOPIC_NAME="$KAFKA_TOPIC_NAME"
export CREDENTIAL_ID="$CREDENTIAL_ID"
export CREDENTIAL_SECRET="$CREDENTIAL_SECRET"
export LOGSTASH_KAFKA_ENDPOINT="$LOGSTASH_KAFKA_ENDPOINT"
EOF
)

eval "$BASHRC_EXPORT"

if ! grep -q "MYSQL_HOST" /home/ubuntu/.bashrc; then
  echo "$BASHRC_EXPORT" >> /home/ubuntu/.bashrc
fi

source /home/ubuntu/.bashrc
echo "kakaocloud: ~/.bashrc에 환경 변수를 추가 완료."

###############################################################################
# 2) filebeat / logstash 설치
###############################################################################
log "kakaocloud: 2. filebeat / logstash 설치 후 환경 변수 추가"

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
sudo systemctl start filebeat  \
  || { log "kakaocloud: Failed to start filebeat"; exit 1; }

sudo systemctl enable logstash \
  || { log "kakaocloud: Failed to enable logstash"; exit 1; }
sudo systemctl start logstash  \
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

log "kakaocloud: filebeat / logstash 설치 및 환경 변수 설정 완료"


###############################################################################
# 4) (선택) Flask 앱 서비스(flask_app.service)에 같은 변수 쓰기
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
  log "kakaocloud: flask_app.service 재시작 완료"
else
  log "kakaocloud: flask_app.service가 없어 override를 생략합니다."
fi


###############################################################################
# 5) main_script.sh & setup_db.sh 다운로드, 실행
###############################################################################
log "kakaocloud: 5. 스크립트 다운로드 링크 유효성 체크"

curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/api_full_setup.sh" \
  || { log "kakaocloud: main_script.sh 링크가 유효하지 않습니다"; exit 1; }
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/setup_db.sh" \
  || { log "kakaocloud: setup_db.sh 링크가 유효하지 않습니다"; exit 1; }

log "kakaocloud: main_script.sh & setup_db.sh 링크 모두 유효"

wget -O main_script.sh "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/api_full_setup.sh" \
  || { log "kakaocloud: Failed to download main_script.sh"; exit 1; }
wget -O setup_db.sh "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/setup_db.sh" \
  || { log "kakaocloud: Failed to download setup_db.sh"; exit 1; }

chmod +x main_script.sh setup_db.sh \
  || { log "kakaocloud: Failed to chmod main_script.sh or setup_db.sh"; exit 1; }

log "kakaocloud: Executing main_script.sh & setup_db.sh"
sudo -E ./main_script.sh \
  || { log "kakaocloud: main_script.sh execution failed"; exit 1; }
sudo -E ./setup_db.sh \
  || { log "kakaocloud: setup_db.sh execution failed"; exit 1; }
log "kakaocloud: main_script.sh & setup_db.sh 완료"


###############################################################################
# 3) filebeat.yml & logs-to-pubsub.conf 다운로드
###############################################################################
log "kakaocloud: 3. filebeat.yml과 logs-to-pubsub.conf, logs-to-kafka.conf를 다운로드합니다."

sudo wget -O /etc/filebeat/filebeat.yml \
  "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/filebeat.yml" \
  || { log "kakaocloud: Failed to download filebeat.yml"; exit 1; }

sudo wget -O /etc/logstash/conf.d/logs-to-pubsub.conf \
  "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/logs-to-pubsub.conf" \
  || { log "kakaocloud: Failed to download logs-to-pubsub.conf"; exit 1; }

sudo wget -O /etc/logstash/conf.d/logs-to-kafka.conf \
  "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/logs-to-kafka.conf" \
  || { log "kakaocloud: Failed to download logs-to-kafka.conf"; exit 1; }

sudo tee /etc/logstash/logstash.yml <<'EOF' > /dev/null \
  || { log "kakaocloud: Failed to write logstash.yml"; exit 1; }
path.data: /var/lib/logstash
path.logs: /var/log/logstash
path.config: /etc/logstash/conf.d/logs-to-pubsub.conf
EOF

log "kakaocloud: 파일 다운로드 및 logstash.yml 구성 완료"

sudo systemctl restart filebeat \
  || { log "kakaocloud: Failed to restart filebeat"; exit 1; }
sudo systemctl restart logstash \
  || { log "kakaocloud: Failed to restart logstash"; exit 1; }

log "kakaocloud: All steps in as_env_setup.sh have completed successfully"
