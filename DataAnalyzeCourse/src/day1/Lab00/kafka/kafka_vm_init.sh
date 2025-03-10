#!/bin/bash

################################################################################
# 0. 초기 설정
################################################################################

echo "kakaocloud: 1.환경 변수 설정 시작"
# 환경 변수 정의
command=$(cat <<EOF
export KAFKA_BOOTSTRAP_SERVER="{Kafka 부트스트랩 서버}"
export AWS_ACCESS_KEY_ID_VALUE="{콘솔에서 발급한 S3 액세스 키의 인증 키 값}"
export AWS_SECRET_ACCESS_KEY_VALUE="{콘솔에서 발급한 S3 액세스 키의 보안 액세스 키 값}"

export BUCKET_NAME="data-catalog"
export AWS_DEFAULT_REGION_VALUE="kr-central-2"
export AWS_DEFAULT_OUTPUT_VALUE="json"

export LOGFILE="/home/ubuntu/setup.log"
EOF
)

# 환경 변수 적용
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc

echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_full_setup.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }

wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab00/kafka/kafka_full_setup.sh || { echo "kakaocloud: kafka_full_setup.sh 다운로드 실패"; exit 1; }
chmod +x kafka_full_setup.sh || { echo "kakaocloud: kafka_full_setup.sh chmod 실패"; exit 1; }
sudo -E ./kafka_full_setup.sh || { echo "kakaocloud: kafka_full_setup.sh 실행 실패"; exit 1; }
