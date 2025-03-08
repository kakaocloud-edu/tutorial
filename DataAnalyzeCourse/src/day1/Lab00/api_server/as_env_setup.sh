#!/bin/bash

##########################################################################
# 2) filebeat / logstash 설치
##########################################################################

echo "kakaocloud: 2. filebeat / logstash 설치 후 환경 변수 추가"

curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/beats.list

sudo apt-get update
# 설치 중 사용자 입력이 없도록 -y 옵션
sudo apt-get install -y filebeat
sudo apt-get install -y logstash

sudo systemctl enable filebeat
sudo systemctl start filebeat
sudo systemctl enable logstash
sudo systemctl start logstash

sudo chmod 777 /etc/default/logstash

sudo bash -c "cat <<EOF >> $LOGSTASH_ENV_FILE

# === Additional Env for Pub/Sub ===
CREDENTIAL_ID=\"$CREDENTIAL_ID\"
CREDENTIAL_SECRET=\"$CREDENTIAL_SECRET\"
DOMAIN_ID=\"$DOMAIN_ID\"
PROJECT_ID=\"$PROJECT_ID\"
PUBSUB_TOPIC_NAME=\"$PUBSUB_TOPIC_NAME\"
KAFKA_TOPIC_NAME=\"$KAFKA_TOPIC_NAME\"
LOGSTASH_KAFKA_ENDPOINT=\"$LOGSTASH_KAFKA_ENDPOINT\"

export CREDENTIAL_ID CREDENTIAL_SECRET DOMAIN_ID PROJECT_ID TOPIC_NAME_PUBSUB KAFKA_TOPIC_NAME MYSQL_HOST LOGSTASH_KAFKA_ENDPOINT
EOF"

sudo systemctl daemon-reload
sudo systemctl restart logstash

##########################################################################
# 4) (선택) Flask 앱 서비스(flask_app.service)에 같은 변수 쓰기
##########################################################################

SERVICE_FILE="/etc/systemd/system/flask_app.service"
OVERRIDE_DIR="/etc/systemd/system/flask_app.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/env.conf"

if [ -f "$SERVICE_FILE" ]; then
  echo "kakaocloud: flask_app.service override 설정을 진행합니다."
  sudo mkdir -p "$OVERRIDE_DIR"
  sudo bash -c "cat <<EOF > $OVERRIDE_FILE
[Service]
Environment=\"MYSQL_HOST=$MYSQL_HOST\"
Environment=\"DOMAIN_ID=$DOMAIN_ID\"
Environment=\"PROJECT_ID=$PROJECT_ID\"
Environment=\"PUBSUB_TOPIC_NAME=$PUBSUB_TOPIC_NAME\"
Environment=\"KAFKA_TOPIC_NAME=$KAFKA_TOPIC_NAME\"
Environment=\"CREDENTIAL_ID=$CREDENTIAL_ID\"
Environment=\"CREDENTIAL_SECRET=$CREDENTIAL_SECRET\"
EOF"
  sudo systemctl daemon-reload
  sudo systemctl restart flask_app
  echo "kakaocloud: flask_app.service 재시작 완료."
else
  echo "kakaocloud: flask_app.service가 없어 override를 생략합니다."
fi

##########################################################################
# 5) main_script.sh & setup_db.sh 다운로드, 실행
##########################################################################

echo "kakaocloud: 5. 스크립트 다운로드 링크 유효성 체크"
curl --output /dev/null --silent --head --fail \
  "https://github.com/lys0611/DA-api-svr-script/raw/refs/heads/main/as_full_setup.sh" || {
    echo "main_script.sh 다운로드 링크가 유효하지 않습니다."
    exit 1
  }

curl --output /dev/null --silent --head --fail \
  "https://github.com/lys0611/DA-api-svr-script/raw/refs/heads/main/setup_db.sh" || {
    echo "setup_db.sh 다운로드 링크가 유효하지 않습니다."
    exit 1
  }

echo "kakaocloud: 스크립트 다운로드 링크가 모두 유효합니다."
echo "kakaocloud: 6. 실제 스크립트 다운로드 및 실행 권한 설정"

wget -O main_script.sh \
  "https://github.com/lys0611/DA-api-svr-script/raw/refs/heads/main/as_full_setup.sh"

wget -O setup_db.sh \
  "https://github.com/lys0611/DA-api-svr-script/raw/refs/heads/main/setup_db.sh"

chmod +x main_script.sh
chmod +x setup_db.sh

echo "kakaocloud: 7. 스크립트 실행을 시작합니다."
sudo -E ./main_script.sh
sudo -E ./setup_db.sh

##########################################################################
# 3) filebeat.yml & logs-to-pubsub.conf 다운로드
##########################################################################

echo "kakaocloud: 3. filebeat.yml과 logs-to-pubsub.conf를 다운로드합니다."
sudo wget -O /etc/filebeat/filebeat.yml \
  "https://github.com/lys0611/DA-api-svr-script/raw/refs/heads/main/filebeat.yml"

sudo wget -O /etc/logstash/conf.d/logs-to-pubsub.conf \
  "https://github.com/lys0611/DA-api-svr-script/raw/refs/heads/main/logs-to-pubsub.conf"

sudo wget -O /etc/logstash/conf.d/logs-to-kafka.conf \
  "https://github.com/lys0611/DA-api-svr-script/raw/refs/heads/main/logs-to-kafka.conf"


sudo tee /etc/logstash/logstash.yml <<'EOF'
path.data: /var/lib/logstash
path.logs: /var/log/logstash
path.config: /etc/logstash/conf.d/logs-to-pubsub.conf
EOF


echo "kakaocloud: filebeat.yml 및 logs-to-pubsub.conf 파일 다운로드 완료."

echo "kakaocloud: filebeat, logstash 서비스를 다시 시작합니다."
sudo systemctl restart filebeat
sudo systemctl restart logstash

echo "kakaocloud: 모든 작업 완료"
