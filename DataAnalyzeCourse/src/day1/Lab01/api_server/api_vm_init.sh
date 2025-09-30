#!/bin/bash
# api_vm_init.sh
# 프로젝트 및 인증 정보
export DOMAIN_ID="{조직 ID}"
export PROJECT_ID="{프로젝트 ID}"
export CREDENTIAL_ID="{액세스 키 ID}"
export CREDENTIAL_SECRET="{보안 액세스 키}"

# 데이터베이스 설정
export MYSQL_HOST="{MySQL 엔드포인트}"

# 스키마 레지스트리 설정
export SCHEMA_REGISTRY_URL="{data-stream-vm의 Private IP}"

# Pub/Sub 및 Kafka 설정
export LOGSTASH_KAFKA_ENDPOINT="{Kafka 부트스트랩 서버}"
export PUBSUB_TOPIC_NAME="log-topic"
export KAFKA_TOPIC_NAME="nginx-topic"

# 로그 및 환경 설정
export LOGSTASH_ENV_FILE="/etc/default/logstash"
export ENV_SETUP_SCRIPT_URL="https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/api_server/api_env_setup.sh"

echo "kakaocloud: 1. api server VM 환경 설정용 api_env_setup.sh 다운로드"
curl --output /dev/null --silent --head --fail "$ENV_SETUP_SCRIPT_URL" || {
  echo "kakaocloud: api_env_setup.sh 다운로드 링크가 유효하지 않습니다."
  exit 1
}

wget -O api_env_setup.sh "$ENV_SETUP_SCRIPT_URL"

echo "kakaocloud: 2. api_env_setup.sh 실행"
chmod +x api_env_setup.sh
sudo -E ./api_env_setup.sh
