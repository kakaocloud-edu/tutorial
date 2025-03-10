#!/bin/bash

MYSQL_HOST="{MySQL 엔드포인트}"
DOMAIN_ID="{조직 ID}"
PROJECT_ID="{프로젝트 ID}"
CREDENTIAL_ID="{액세스 키 ID}"
CREDENTIAL_SECRET="{보안 액세스 키}"
LOGSTASH_KAFKA_ENDPOINT="{Kafka 클러스터 부트스트랩 서버}"

PUBSUB_TOPIC_NAME="test-topic-lys"
KAFKA_TOPIC_NAME="nginx-topic"
LOGSTASH_ENV_FILE="/etc/default/logstash"
ENV_SETUP_SCRIPT_URL="https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/api_server/as_env_setup.sh"

echo "kakaocloud: 2. as_env_setup.sh 스크립트를 다운로드합니다."

# 유효성 체크
curl --output /dev/null --silent --head --fail "$ENV_SETUP_SCRIPT_URL" || {
  echo "kakaocloud: as_env_setup.sh 다운로드 링크가 유효하지 않습니다."
  exit 1
}

echo "kakaocloud: 스크립트 다운로드 링크가 유효합니다. 스크립트를 다운로드합니다."
wget -O as_env_setup.sh "$ENV_SETUP_SCRIPT_URL"
chmod +x as_env_setup.sh

echo "kakaocloud: as_env_setup.sh 실행을 시작합니다."
sudo -E ./as_env_setup.sh

echo "kakaocloud: 모든 작업 완료"
