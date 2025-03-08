#!/bin/bash
# setup_initial.sh
# 이 스크립트는 환경 변수를 설정한 후, GitHub 저장소에서 필요한 스크립트를 다운로드하고 실행합니다.

set -e  # 오류 발생 시 스크립트 종료

echo "kakaocloud: 1.Starting environment variable setup"
# 환경 변수 정의
command=$(cat <<EOF
export DOMAIN_ID="{조직 ID}"
export PROJECT_ID="{프로젝트 ID}"
export CREDENTIAL_ID="{액세스 키 ID}"
export CREDENTIAL_SECRET="{보안 액세스 키}"
export API_BASE_URL="{ALB의 Public IP}"
export TOPIC_NAME="test-topic"
export SUB_NAME="test-pull-sub"
export TOPIC_NAME_MK="log-topic"
export OBJECT_STORAGE_SUBSCRIPTION_NAME="log-obj-sub"
export OBJECT_STORAGE_BUCKET="pubsub-nginx-log"
export PUBSUB_ENDPOINT="https://pub-sub.kr-central-2.kakaocloud.com"
EOF
)

# 환경 변수 적용
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc
echo "kakaocloud: Environment variable setup completed"

echo "kakaocloud: 2.Checking the validity of the script download site"
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/traffic_generator/tg_full_setup.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
echo "kakaocloud: Script download site is valid"

wget https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/traffic_generator/tg_full_setup.sh
chmod +x setup_all.sh
sudo -E ./setup_all.sh
