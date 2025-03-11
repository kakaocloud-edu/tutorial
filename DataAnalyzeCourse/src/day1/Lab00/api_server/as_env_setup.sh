#!/bin/bash

# 스크립트 실행 중 하나라도 실패하면 종료
set -e
# 파이프라인(|) 중 하나라도 실패하면 전체 실패
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

# 각 명령어 실행 시간 측정을 위한 간단한 래퍼 함수
measure_time() {
  local start=$(date +%s)
  # "$@" : 스크립트로 전달된 전체 명령을 그대로 실행
  "$@"
  local end=$(date +%s)
  local duration=$(( end - start ))
  # 실행된 전체 명령어를 문자열로 찍어주고, 걸린 시간을 로깅
  log "CMD: $* took $duration seconds"
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

# 시간 측정 예시 (echo 명령)
start_time=$(date +%s)
echo "$BASHRC_EXPORT" >> /home/ubuntu/.bashrc
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
log "CMD: echo \"\$BASHRC_EXPORT\" >> /home/ubuntu/.bashrc took $elapsed seconds"

start_time=$(date +%s)
source /home/ubuntu/.bashrc
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
log "CMD: source /home/ubuntu/.bashrc took $elapsed seconds"

echo "kakaocloud: ~/.bashrc에 환경 변수를 추가 완료."

###############################################################################
# 2) filebeat / logstash 설치
###############################################################################
log "kakaocloud: 2. filebeat / logstash 설치 후 환경 변수 추가"

measure_time curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch
  | sudo apt-key add -

measure_time sh -c "echo \"deb https://artifacts.elastic.co/packages/7.x/apt stable main\" | sudo tee /etc/apt/sources.list.d/beats.list > /dev/null"

measure_time sudo apt-get update
measure_time sudo apt-get install -y filebeat logstash

measure_time sudo systemctl enable filebeat
measure_time sudo systemctl start filebeat

measure_time sudo systemctl enable logstash
measure_time sudo systemctl start logstash

measure_time sudo chmod 777 /etc/default/logstash

start_time=$(date +%s)
cat <<EOF | sudo tee -a /etc/default/logstash > /dev/null
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
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
log "CMD: cat <<EOF ... >> /etc/default/logstash took $elapsed seconds"

measure_time sudo systemctl daemon-reload
measure_time sudo systemctl restart logstash

log "kakaocloud: filebeat / logstash 설치 및 환경 변수 설정 완료"

###############################################################################
# 4) (선택) Flask 앱 서비스(flask_app.service)에 같은 변수 쓰기
###############################################################################
SERVICE_FILE="/etc/systemd/system/flask_app.service"
OVERRIDE_DIR="/etc/systemd/system/flask_app.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/env.conf"

log "kakaocloud: 4. Setting environment variables for flask_app.service"

if [ -f "$SERVICE_FILE" ]; then
  measure_time sudo mkdir -p "$OVERRIDE_DIR"
  start_time=$(date +%s)
  cat <<EOF | sudo tee "$OVERRIDE_FILE" > /dev/null
[Service]
Environment="MYSQL_HOST=$MYSQL_HOST"
Environment="DOMAIN_ID=$DOMAIN_ID"
Environment="PROJECT_ID=$PROJECT_ID"
Environment="PUBSUB_TOPIC_NAME=$PUBSUB_TOPIC_NAME"
Environment="KAFKA_TOPIC_NAME=$KAFKA_TOPIC_NAME"
Environment="CREDENTIAL_ID=$CREDENTIAL_ID"
Environment="CREDENTIAL_SECRET=$CREDENTIAL_SECRET"
EOF
  end_time=$(date +%s)
  elapsed=$(( end_time - start_time ))
  log "CMD: cat <<EOF ... > $OVERRIDE_FILE took $elapsed seconds"

  measure_time sudo systemctl daemon-reload
  measure_time sudo systemctl restart flask_app
  log "kakaocloud: flask_app.service 재시작 완료"
else
  log "kakaocloud: flask_app.service가 없어 override를 생략합니다."
fi

###############################################################################
# 5) api_full_setup.sh & setup_db.sh 다운로드, 실행
###############################################################################
log "kakaocloud: 5. 스크립트 다운로드 링크 유효성 체크"

measure_time curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/api_full_setup.sh"
measure_time curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/setup_db.sh"

log "kakaocloud: main_script.sh & setup_db.sh 링크 모두 유효"

measure_time wget -O api_full_setup.sh "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/api_full_setup.sh"
measure_time wget -O setup_db.sh "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/setup_db.sh"

measure_time chmod +x api_full_setup.sh setup_db.sh

log "kakaocloud: Executing api_full_setup.sh & setup_db.sh"

measure_time sudo -E /home/ubuntu/api_full_setup.sh
measure_time sudo -E /home/ubuntu/setup_db.sh

log "kakaocloud: api_full_setup.sh & setup_db.sh 완료"

start_time=$(date +%s)
sudo tee /etc/logstash/logstash.yml <<'EOF' > /dev/null || { log "kakaocloud: Failed to write logstash.yml"; exit 1; }
path.data: /var/lib/logstash
path.logs: /var/log/logstash
path.config: /etc/logstash/conf.d/logs-to-pubsub.conf
EOF
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
log "CMD: sudo tee /etc/logstash/logstash.yml took $elapsed seconds"

log "kakaocloud: 파일 다운로드 및 logstash.yml 구성 완료"

measure_time sudo systemctl restart filebeat
measure_time sudo systemctl restart logstash

# 실습에 사용되는 폴더만 남기기 위해 tutorial 리포지토리 삭제
measure_time sudo rm -rf /home/ubuntu/tutorial

log "kakaocloud: All steps in as_env_setup.sh have completed successfully"
