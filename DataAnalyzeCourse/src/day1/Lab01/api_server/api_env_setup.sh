#!/bin/bash

# 하나라도 실패하면 종료
set -e
# 파이프라인 중 하나라도 실패하면 전체 실패
set -o pipefail

###############################################################################
# 1) ~/.bashrc에 환경 변수 설정
###############################################################################
echo "kakaocloud: 3. 환경 변수를 ~/.bashrc에 추가"
BASHRC_EXPORT=$(cat <<EOF
export MYSQL_HOST="$MYSQL_HOST"
export DOMAIN_ID="$DOMAIN_ID"
export PROJECT_ID="$PROJECT_ID"
export PUBSUB_TOPIC_NAME="$PUBSUB_TOPIC_NAME"
export KAFKA_TOPIC_NAME="$KAFKA_TOPIC_NAME"
export CREDENTIAL_ID="$CREDENTIAL_ID"
export CREDENTIAL_SECRET="$CREDENTIAL_SECRET"
export LOGSTASH_KAFKA_ENDPOINT="$LOGSTASH_KAFKA_ENDPOINT"
export SCHEMA_REGISTRY_URL="$SCHEMA_REGISTRY_URL"
export LOGSTASH_ENV_FILE="$LOGSTASH_ENV_FILE"
EOF
)

echo "$BASHRC_EXPORT" >> /home/ubuntu/.bashrc

# 새로 추가된 값 반영
source /home/ubuntu/.bashrc
###############################################################################
# 2) filebeat / logstash 설치
###############################################################################
echo "kakaocloud: 4. filebeat, logstash 다운로드"
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add - \
  || { echo "kakaocloud: filebeat, logstash GPG 키 추가 실패"; exit 1; }
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/beats.list > /dev/null \
  || { echo "kakaocloud: beats.list 추가 실패"; exit 1; }

sudo apt-get update \
  || { echo "kakaocloud: apt-get update 실패"; exit 1; }
sudo apt-get install -y filebeat logstash \
  || { echo "kakaocloud: filebeat, logstash 설치 실패"; exit 1; }

sudo systemctl enable filebeat \
  || { echo "kakaocloud: filebeat enable 실패"; exit 1; }
sudo systemctl start filebeat  \
  || { echo "kakaocloud: filebeat start 실패"; exit 1; }

sudo systemctl enable logstash \
  || { echo "kakaocloud: logstash enable 실패"; exit 1; }
sudo systemctl start logstash  \
  || { echo "kakaocloud: logstash start 실패"; exit 1; }

echo "kakaocloud: 5. filebeat, logstash 환경 변수 설정"
sudo chmod 777 /etc/default/logstash \
  || { echo "kakaocloud: /etc/default/logstash 권한 변경 실패"; exit 1; }

cat <<EOF | sudo tee -a /etc/default/logstash > /dev/null \
  || { echo "kakaocloud: logstash 환경 변수 설정 실패"; exit 1; }

# === Additional Env for Pub/Sub ===
CREDENTIAL_ID="$CREDENTIAL_ID"
CREDENTIAL_SECRET="$CREDENTIAL_SECRET"
DOMAIN_ID="$DOMAIN_ID"
PROJECT_ID="$PROJECT_ID"
PUBSUB_TOPIC_NAME="$PUBSUB_TOPIC_NAME"
KAFKA_TOPIC_NAME="$KAFKA_TOPIC_NAME"
SCHEMA_REGISTRY_URL="$SCHEMA_REGISTRY_URL"
LOGSTASH_KAFKA_ENDPOINT="$LOGSTASH_KAFKA_ENDPOINT"

export CREDENTIAL_ID CREDENTIAL_SECRET DOMAIN_ID PROJECT_ID TOPIC_NAME_PUBSUB KAFKA_TOPIC_NAME MYSQL_HOST SCHEMA_REGISTRY_URL LOGSTASH_KAFKA_ENDPOINT
EOF

sudo systemctl daemon-reload \
  || { echo "kakaocloud: systemctl daemon-reload 실패"; exit 1; }
sudo systemctl restart logstash \
  || { echo "kakaocloud: logstash restart 실패"; exit 1; }



###############################################################################
# 3) flask_app.service 환경 변수 설정
###############################################################################
SERVICE_FILE="/etc/systemd/system/flask_app.service"
OVERRIDE_DIR="/etc/systemd/system/flask_app.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/env.conf"

echo "kakaocloud: 6. flask_app.service 환경 변수 설정"

if [ -f "$SERVICE_FILE" ]; then
  sudo mkdir -p "$OVERRIDE_DIR" \
    || { echo "kakaocloud: $OVERRIDE_DIR 생성 실패"; exit 1; }
  cat <<EOF | sudo tee "$OVERRIDE_FILE" > /dev/null \
    || { echo "kakaocloud: flask_app.service env 파일 작성 실패"; exit 1; }
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
    || { echo "kakaocloud: flask_app systemctl daemon-reload 실패"; exit 1; }
  sudo systemctl restart flask_app \
    || { echo "kakaocloud: flask_app.service 재시작 실패"; exit 1; }
  echo "kakaocloud: flask_app.service 재시작 완료"
fi


###############################################################################
# 4) 스크립트 및 실습 진행에 필요한 파일들(api_full_setup.sh, filebeat.yml, logs-to-pubsub.conf, logs-to-kafka.conf) 다운로드 및 실행
###############################################################################
echo "kakaocloud: 7. 스크립트 및 실습 진행에 필요한 파일 다운로드"

# /home/ubuntu/tutorial 디렉터리가 없으면 clone, 있으면 스킵
if [ ! -d "/home/ubuntu/tutorial" ]; then
    sudo git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || {
        echo "kakaocloud: git clone 실패"; exit 1;
    }
else
    echo "kakaocloud: /home/ubuntu/tutorial already exists, skipping clone"
fi

# DataAnalyzeCourse/src/day1/Lab01/api_server 폴더가 누락되었으면 재시도
if [ ! -d "/home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server" ]; then
    echo "kakaocloud: The previous clone seems incomplete, re-cloning..."
    sudo rm -rf /home/ubuntu/tutorial
    sudo git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || {
        echo "kakaocloud: git clone 재시도 실패"; exit 1;
    }
fi

# 1) api_full_setup.sh, setup_db.sh → /home/ubuntu
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server/api_full_setup.sh /home/ubuntu/api_full_setup.sh || {
    echo "kakaocloud: api_full_setup.sh 복사 실패"; exit 1;
}
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server/setup_db.sh /home/ubuntu/setup_db.sh || {
    echo "kakaocloud: setup_db.sh 복사 실패"; exit 1;
}
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server/api_avro_setup.sh /home/ubuntu/api_avro_setup.sh || {
    echo "kakaocloud: api_avro_setup.sh 복사 실패"; exit 1;
}

# 2) filebeat.yml → /etc/filebeat
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server/filebeat.yml /etc/filebeat/filebeat.yml || {
    echo "kakaocloud: filebeat.yml 복사 실패"; exit 1;
}

# 3) logs-to-pubsub.conf → /etc/logstash/conf.d
sudo cp /home/ubuntu/tutorial/DataAnalyzeCourse/src/day1/Lab01/api_server/logs-to-pubsub.conf /etc/logstash/conf.d/logs-to-pubsub.conf || {
    echo "kakaocloud: logs-to-pubsub.conf 복사 실패"; exit 1;
}

sudo chmod +x /home/ubuntu/api_full_setup.sh /home/ubuntu/api_avro_setup.sh \
  || { echo "kakaocloud: api_full_setup.sh, api_avro_setup.sh에 실행 권한 부여 실패"; exit 1; }

echo "kakaocloud: 8. API 서버·파이프라인 가동용 api_full_setup.sh 실행 시작"
sudo -E /home/ubuntu/api_full_setup.sh \
  || { echo "kakaocloud: api_full_setup.sh 실행 실패"; exit 1; }

echo "kakaocloud: 9. Avro 플러그인 설치용 api_arvo_setup.sh 실행 시작"
sudo -E /home/ubuntu/api_avro_setup.sh \
  || { echo "kakaocloud: api_avro_setup.sh 실행 실패"; exit 1; }

###############################################################################
# 5) logstash.yml 구성 및 filebeat,logstash 재시작
###############################################################################
echo "kakaocloud: 11. logstash.yml 구성 시작"
sudo tee /etc/logstash/logstash.yml <<'EOF' > /dev/null \
  || { echo "kakaocloud: Failed to write logstash.yml"; exit 1; }
path.data: /var/lib/logstash
path.logs: /var/log/logstash
path.config: /etc/logstash/conf.d/logs-to-pubsub.conf
EOF

echo "kakaocloud: 12. filebeat, logstash 재시작"
sudo systemctl restart filebeat \
  || { echo "kakaocloud: Failed to restart filebeat"; exit 1; }
sudo systemctl restart logstash \
  || { echo "kakaocloud: Failed to restart logstash"; exit 1; }

echo "kakaocloud: Setup 완료"
