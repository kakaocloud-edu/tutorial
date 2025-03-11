#!/bin/bash

echo "kakaocloud: 1.환경 변수 설정 시작"

cat <<'EOF' > /tmp/env_vars.sh
KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"
BUCKET_NAME="data-catalog"
AWS_DEFAULT_REGION_VALUE="kr-central-2"
AWS_DEFAULT_OUTPUT_VALUE="json"
LOGFILE="/home/ubuntu/setup.log"
EOF

# 환경 변수 적용
source /tmp/env_vars.sh
echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc

echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_full_setup.sh.sh"

curl --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }

wget -q "$SCRIPT_URL" -O kafka_full_setup.sh
chmod +x kafka_full_setup.sh
sudo -E ./kafka_full_setup.sh
