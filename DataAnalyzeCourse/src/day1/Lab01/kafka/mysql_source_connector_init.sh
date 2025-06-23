#!/bin/bash

echo "kakaocloud: 1. 환경 변수 설정 시작"

cat <<'EOF' > /tmp/env_vars.sh
# Kafka 설정
export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
export MYSQL_DB_HOSTNAME="{MySQL 엔드포인트}"

# 로그 파일 경로
export LOGFILE="/home/ubuntu/setup.log"

# ===============================================
# MySQL 접속 정보
# ===============================================
export MYSQL_DB_PORT="3306"
export MYSQL_DB_USER="admin"
export MYSQL_DB_PASSWORD="admin1234"
export MYSQL_SERVER_ID="184054"
export MYSQL_SERVER_NAME="mysql-server"
EOF

# 환경 변수 적용
source /tmp/env_vars.sh
echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc # .bashrc에 추가하여 영구 적용

echo "kakaocloud: 2. 스크립트 다운로드 사이트 유효성 검사 시작"
# SCRIPT_URL은 mysql_source_connector.sh 스크립트의 실제 GitHub raw URL이어야 합니다.
# 이 URL은 이전에 제가 제공한 마지막 스크립트의 내용과 동일해야 합니다.
SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/kafka/mysql_source_connector.sh"

curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
wget -q "$SCRIPT_URL" -O mysql_source_connector.sh

chmod +x mysql_source_connector.sh
sudo -E ./mysql_source_connector.sh
