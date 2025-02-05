#!/bin/bash

MYSQL_HOST="{MySQL 엔드포인트}"
DOMAIN_ID="{조직 ID}"
PROJECT_ID="{프로젝트 ID]"
PUBSUB_TOPIC_NAME="{Pub/Sub 토픽 이름(log-topic)}"
KAFKA_TOPIC_NAME="{Kafka 토픽 이름(nginx-topic)}"
CREDENTIAL_ID="{액세스 키 ID}"
CREDENTIAL_SECRET="{보안 액세스 키}"
LOGSTASH_ENV_FILE="/etc/default/logstash"
LOGSTASH_KAFKA_ENDPOINT="{Kafka 클러스터 부트스트랩 서버}"


echo "kakaocloud: 1. ~/.bashrc에 환경 변수를 설정합니다."
##########################################################################
# 1) .bashrc에 기록
##########################################################################

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
  "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/ApiServer/main_script.sh" || {
    echo "main_script.sh 다운로드 링크가 유효하지 않습니다."
    exit 1
  }

curl --output /dev/null --silent --head --fail \
  "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/ApiServer/setup_db.sh" || {
    echo "setup_db.sh 다운로드 링크가 유효하지 않습니다."
    exit 1
  }

echo "kakaocloud: 스크립트 다운로드 링크가 모두 유효합니다."
echo "kakaocloud: 6. 실제 스크립트 다운로드 및 실행 권한 설정"

wget -O main_script.sh \
  "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/ApiServer/main_script.sh"

wget -O setup_db.sh \
  "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/ApiServer/setup_db.sh"

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
  "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/ApiServer/filebeat.yml"

sudo wget -O /etc/logstash/conf.d/logs-to-pubsub.conf \
  "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/ApiServer/logs-to-pubsub.conf"

sudo wget -O /etc/logstash/conf.d/logs-to-kafka.conf \
  "https://github.com/KOlizer/syu-DataAnalyze/raw/refs/heads/main/ApiServer/logs-to-kafka.conf"

echo "kakaocloud: filebeat.yml 및 logs-to-pubsub.conf 파일 다운로드 완료."

echo "kakaocloud: filebeat, logstash 서비스를 다시 시작합니다."
sudo systemctl restart filebeat
sudo systemctl restart logstash

echo "kakaocloud: 모든 작업 완료"
