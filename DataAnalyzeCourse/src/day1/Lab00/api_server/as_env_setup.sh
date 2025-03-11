#!/bin/bash

# 하나라도 실패하면 종료
set -e
# 파이프라인 중 하나라도 실패하면 전체 실패
set -o pipefail

###############################################################################
# 로그 설정
###############################################################################
LOGFILE="/home/ubuntu/setup.log"
exec &> >(tee -a "$LOGFILE")  # 모든 echo 출력도 setup.log에 기록

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
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
export LOGSTASH_ENV_FILE="$LOGSTASH_ENV_FILE"
EOF
)

echo "$BASHRC_EXPORT" >> /home/ubuntu/.bashrc

# 새로 추가된 값 반영
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
# 5) api_full_setup.sh & setup_db.sh 다운로드, 실행
###############################################################################
log "kakaocloud: 5. 스크립트 다운로드 링크 유효성 체크"

# /home/ubuntu/tutorial 디렉터리가 없으면 clone, 있으면 스킵
if [ ! -d "/home/ubuntu/tutorial" ]; then
    sudo git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || {
        echo "kakaocloud: Failed to git clone"; exit 1;
    }
else
    echo "kakaocloud: /home/ubuntu/tutorial already exists, skipping clone"
fi

# DataAnalyzeCourse/src/day1/Lab00/api_server 폴더가 누락되었으면 재시도
if [ ! -d "/home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab00/api_server" ]; then
    echo "kakaocloud: The previous clone seems incomplete, re-cloning..."
    sudo rm -rf /home/ubuntu/tutorial
    sudo git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || {
        echo "kakaocloud: Failed to git clone"; exit 1;
    }
fi

# 1) api_full_setup.sh, setup_db.sh → /home/ubuntu
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab00/api_server/api_full_setup.sh /home/ubuntu/api_full_setup.sh || {
    echo "kakaocloud: Failed to copy api_full_setup.sh"; exit 1;
}
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab00/api_server/setup_db.sh /home/ubuntu/setup_db.sh || {
    echo "kakaocloud: Failed to copy setup_db.sh"; exit 1;
}

# 2) filebeat.yml → /etc/filebeat
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab00/api_server/filebeat.yml /etc/filebeat/filebeat.yml || {
    echo "kakaocloud: Failed to copy filebeat.yml"; exit 1;
}

# 3) logs-to-pubsub.conf, logs-to-kafka.conf → /etc/logstash/conf.d
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab00/api_server/logs-to-pubsub.conf /etc/logstash/conf.d/logs-to-pubsub.conf || {
    echo "kakaocloud: Failed to copy logs-to-pubsub.conf"; exit 1;
}
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab00/api_server/logs-to-kafka.conf /etc/logstash/conf.d/logs-to-kafka.conf || {
    echo "kakaocloud: Failed to copy logs-to-kafka.conf"; exit 1;
}

chmod +x api_full_setup.sh setup_db.sh \
  || { log "kakaocloud: Failed to chmod api_full_setup.sh or setup_db.sh"; exit 1; }

log "kakaocloud: Executing api_full_setup.sh & setup_db.sh"
sudo -E /home/ubuntu/api_full_setup.sh \
  || { log "kakaocloud: api_full_setup.sh execution failed"; exit 1; }
sudo -E /home/ubuntu/setup_db.sh \
  || { log "kakaocloud: setup_db.sh execution failed"; exit 1; }
log "kakaocloud: api_full_setup.sh & setup_db.sh 완료"

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

# 실습에 사용되는 폴더만 남기기 위해 tutorial 리포지토리 삭제
sudo rm -rf /home/ubuntu/tutorial || {
    log "kakaocloud: Failed to remove the tutorial repository"; exit 1;
}

log "kakaocloud: All steps in as_env_setup.sh have completed successfully"
