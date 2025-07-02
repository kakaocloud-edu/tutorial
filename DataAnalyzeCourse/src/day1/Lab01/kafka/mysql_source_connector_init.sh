#!/bin/bash

echo "kakaocloud: 1. 환경 변수 설정 시작"

cat <<'EOF' > /tmp/env_vars.sh
export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
export MYSQL_DB_HOSTNAME="{MySQL 엔드포인트}"
export LOGFILE="/home/ubuntu/setup.log"
export MYSQL_DB_PORT="3306"
export MYSQL_DB_USER="admin"
export MYSQL_DB_PASSWORD="admin1234"
export MYSQL_SERVER_ID="184054"
export MYSQL_SERVER_NAME="mysql-server"
EOF

source /tmp/env_vars.sh

if ! grep -q "source /tmp/env_vars.sh" /home/ubuntu/.bashrc; then
    echo "" >> /home/ubuntu/.bashrc
    echo "# Load custom environment variables" >> /home/ubuntu/.bashrc
    echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc
fi

chown ubuntu:ubuntu /tmp/env_vars.sh

echo "kakaocloud: 2. 스크립트 다운로드 사이트 유효성 검사 시작"
SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/kafka/mysql_source_connector.sh"
CONNECTOR_SCRIPT="/home/ubuntu/mysql_source_connector.sh"

curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
wget -q "$SCRIPT_URL" -O "$CONNECTOR_SCRIPT"

chown ubuntu:ubuntu "$CONNECTOR_SCRIPT"
chmod +x "$CONNECTOR_SCRIPT"
sudo -E "$CONNECTOR_SCRIPT"
