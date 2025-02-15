#!/bin/bash
# setup_initial.sh
# 이 스크립트는 환경 변수를 설정한 후,
# GitHub 저장소 전체를 클론하는 대신, DataAnalyzeCourse/src/TrafficGenerator/setup_all.sh 파일을 wget으로 다운로드 받고,
# 다운로드한 스크립트를 실행합니다.
#
# (환경 변수들은 스크립트 내에서 직접 정의합니다.)

set -e

echo "========================================"
echo "1. 환경 변수 설정 시작"
echo "========================================"

# ----------------------------------------
# 1. 환경 변수 정의 (필요에 따라 실제 값으로 수정)
# ----------------------------------------
export DOMAIN_ID="{조직 ID}"
export PROJECT_ID="{프로젝트 ID}"
export TOPIC_NAME="{콘솔에서 생성한 토픽 이름(test-topic)}"
export SUB_NAME="{콘솔에서 생성한 Pull Subscription 이름(pull-subscription)}"
export CREDENTIAL_ID="{액세스 키 ID}"
export CREDENTIAL_SECRET="{보안 액세스 키}"
export API_BASE_URL="{ALB의 Public IP}"
export TOPIC_NAME_MK="{log 적재용 토픽 이름(log-topic)}"
export OBJECT_STORAGE_SUBSCRIPTION_NAME="{실습용 Object Storage Subscription 이름(obj-subscription)}"
export OBJECT_STORAGE_BUCKET="{로그 적재용 Object Storage 버킷 이름(pubsub-nginx-log)}"

export PUBSUB_ENDPOINT="https://pub-sub.kr-central-2.kakaocloud.com"
export TOPIC_DESCRIPTION=""
export TOPIC_RETENTION_DURATION="600s"
export EXPORT_INTERVAL_MIN=10
export FILE_PREFIX=""
export FILE_SUFFIX=".log"
export CHANNEL_COUNT=4
export MAX_CHANNEL_COUNT=10
export IS_EXPORT_ENABLED=true
export LOG_FILENAME="traffic_generator.log"
export LOG_LEVEL="INFO"
export NUM_USERS=5
export MAX_THREADS=5
export ACTIONS_PER_USER=30

echo "환경 변수 설정 완료."

# ----------------------------------------
# 환경 변수 영구 적용 (.bashrc에 추가)
# ----------------------------------------
echo "========================================"
echo "환경 변수를 ~/.bashrc에 추가 중..."
vars=(
  PUBSUB_ENDPOINT DOMAIN_ID PROJECT_ID TOPIC_NAME SUB_NAME TOPIC_DESCRIPTION TOPIC_RETENTION_DURATION
  CREDENTIAL_ID CREDENTIAL_SECRET API_BASE_URL TOPIC_NAME_MK OBJECT_STORAGE_SUBSCRIPTION_NAME
  OBJECT_STORAGE_BUCKET EXPORT_INTERVAL_MIN FILE_PREFIX FILE_SUFFIX CHANNEL_COUNT MAX_CHANNEL_COUNT
  IS_EXPORT_ENABLED LOG_FILENAME LOG_LEVEL NUM_USERS MAX_THREADS ACTIONS_PER_USER
)
for var in "${vars[@]}"; do
  # 이미 .bashrc에 해당 변수 정의가 없으면 추가
  if ! grep -q "export $var=" ~/.bashrc; then
    echo "export $var=\"${!var}\"" >> ~/.bashrc
  fi
done
echo "~/.bashrc에 환경 변수 추가 완료."

# ----------------------------------------
# 2. GitHub 파일 다운로드 (DataAnalyzeCourse/src/TrafficGenerator/setup_all.sh)
# ----------------------------------------
echo "========================================"
echo "GitHub 파일 다운로드 시작"
echo "========================================"

# 다운로드할 파일의 Raw URL (브랜치가 main이라고 가정)
FILE_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/setup_all.sh"

# 다운로드할 위치 (원래 클론 디렉토리와 유사하게 구성)
DEST_DIR="$HOME/syu-DataAnalyze/TrafficGenerator"
mkdir -p "$DEST_DIR"
DEST_FILE="$DEST_DIR/setup_all.sh"

echo "파일 다운로드: $FILE_URL -> $DEST_FILE"
wget "$FILE_URL" -O "$DEST_FILE"

# 다운로드 받은 파일의 소유권을 ubuntu 사용자로 변경 (필요시)
sudo chown -R ubuntu:ubuntu "$HOME/syu-DataAnalyze"

echo "GitHub 파일 다운로드 완료."

# ----------------------------------------
# 3. setup_all.sh 실행
# ----------------------------------------
echo "========================================"
echo "setup_all.sh 실행 시작"
echo "========================================"

if [ -f "$DEST_FILE" ]; then
    echo "setup_all.sh 스크립트를 실행합니다."
    chmod +x "$DEST_FILE"
    # sudo -E를 사용하여 환경 변수 보존 및 ubuntu 사용자로 실행
    sudo -E -u ubuntu bash "$DEST_FILE"
else
    echo "setup_all.sh 스크립트를 찾을 수 없습니다: $DEST_FILE"
    echo "나중에 setup_all.sh를 수동으로 실행해 주시기 바랍니다."
fi

echo "========================================"
echo "환경 변수 설정 및 초기화 작업 완료."
echo "========================================"
