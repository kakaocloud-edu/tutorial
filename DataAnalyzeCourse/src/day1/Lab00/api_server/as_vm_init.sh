#!/bin/bash

# 프로젝트 및 인증 정보
export DOMAIN_ID="{조직 ID}"
export PROJECT_ID="{프로젝트 ID}"
export CREDENTIAL_ID="{액세스 키 ID}"
export CREDENTIAL_SECRET="{보안 액세스 키}"
# 데이터베이스 설정
export MYSQL_HOST="{MySQL 엔드포인트}"
# Pub/Sub 및 Kafka 설정
export PUBSUB_TOPIC_NAME="log-topic"
export KAFKA_TOPIC_NAME="nginx-topic"
export LOGSTASH_KAFKA_ENDPOINT="temp-kafka-bootstrap-server"
# 로그 및 환경 설정
export LOGSTASH_ENV_FILE="/etc/default/logstash"
export ENV_SETUP_SCRIPT_URL="https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/as_env_setup.sh"

echo "kakaocloud: 1. as_env_setup.sh 스크립트를 다운로드합니다."
curl --output /dev/null --silent --head --fail "$ENV_SETUP_SCRIPT_URL" || {
  echo "kakaocloud: as_env_setup.sh 다운로드 링크가 유효하지 않습니다."
  exit 1
}

wget -O as_env_setup.sh "$ENV_SETUP_SCRIPT_URL"
echo "kakaocloud: as_env_setup.sh 스크립트를 다운로드가 완료되었습니다."

echo "kakaocloud: 2. as_env_setup.sh 실행을 시작합니다."
chmod +x as_env_setup.sh
sudo -E ./as_env_setup.sh
echo "kakaocloud: 스크립트 적용이 완료되었습니다."
