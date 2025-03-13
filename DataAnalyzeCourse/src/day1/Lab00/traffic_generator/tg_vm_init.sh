#!/bin/bash
# tg_vm_init.sh
set -e  # 오류 발생 시 스크립트 종료

echo "kakaocloud: 1.환경 변수 설정 시작"
# 환경 변수 정의
command=$(cat <<EOF
# 프로젝트 및 인증 정보
export DOMAIN_ID="{조직 ID}"
export PROJECT_ID="{프로젝트 ID}"
export CREDENTIAL_ID="{액세스 키 ID}"
export CREDENTIAL_SECRET="{보안 액세스 키}"

# 생성한 리소스의 값
export API_BASE_URL="{ALB의 Public IP}"
export TOPIC_NAME="test-topic"
export SUB_NAME="test-pull-sub"

# 생성할 Pub/Sub 리소스 정보
export TOPIC_NAME_MK="log-topic"
export OBJECT_STORAGE_SUBSCRIPTION_NAME="log-obj-sub"
export OBJECT_STORAGE_BUCKET="pubsub-nginx-log"
export PUBSUB_ENDPOINT="https://pub-sub.kr-central-2.kakaocloud.com"

# Kafka 실행에 필요한 경로 및 정보
export KAFKA_HOME=/opt/kafka
export PATH=$PATH:$KAFKA_HOME/bin
EOF
)

# 환경 변수 적용
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc

echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/traffic_generator/tg_full_setup.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }

wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab00/traffic_generator/tg_full_setup.sh
chmod +x tg_full_setup.sh
sudo -E ./tg_full_setup.sh
