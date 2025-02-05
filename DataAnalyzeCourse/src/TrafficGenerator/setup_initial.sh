#!/bin/bash
# setup_initial.sh
# 이 스크립트는 환경 변수를 설정하고, GitHub 저장소를 클론한 후,
# 클론된 저장소 내의 TrafficGenerator/setup_all.sh 스크립트를 실행합니다.
#
# (환경 변수들은 스크립트 내에서 직접 정의합니다.)

set -e

echo "========================================"
echo "1. 환경 변수 설정 시작"
echo "========================================"

# ----------------------------------------
# 1. 환경 변수 정의 (필요에 따라 실제 값으로 수정)
# ----------------------------------------
export PUBSUB_ENDPOINT="https://pub-sub.kr-central-2.kakaocloud.com"
export DOMAIN_ID="{조직 ID}"
export PROJECT_ID="{프로젝트 ID}"
export TOPIC_NAME="콘솔에서 생성한 토픽 이름(test-topic)"
export SUB_NAME="콘솔에서 생성한 서브 스크립션 이름(pull-subscription)"
export TOPIC_DESCRIPTION=""
export TOPIC_RETENTION_DURATION="600s"
export CREDENTIAL_ID="{액세스 키 ID}"
export CREDENTIAL_SECRET="{보안 액세스 키}"
export API_BASE_URL="{ALB 주소}"

export TOPIC_NAME_MK="{실습용 토픽 이름(crate-topic)}"
export OBJECT_STORAGE_SUBSCRIPTION_NAME="{실습용 서브스크립션 이름(objectstoragesubscription)"
export OBJECT_STORAGE_BUCKET="{로그 적재용 ObjectStorage 버킷 이름}"
export EXPORT_INTERVAL_MIN=10
export FILE_PREFIX=""
export FILE_SUFFIX=".log"
export CHANNEL_COUNT=4
export MAX_CHANNEL_COUNT=10
export IS_EXPORT_ENABLED=true
export LOG_FILENAME="traffic_generator.log"
export LOG_LEVEL="INFO"
export NUM_USERS=20
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
# 2. GitHub 저장소 클론 (전체 저장소가 클론되어야 함)
# ----------------------------------------
echo "========================================"
echo "GitHub 저장소 클론 시작"
echo "========================================"

REPO_URL="https://github.com/KOlizer/syu-DataAnalyze.git"
CLONE_DIR="$HOME/syu-DataAnalyze"

if [ -d "$CLONE_DIR" ]; then
  if [ -d "$CLONE_DIR/.git" ]; then
    echo "저장소가 이미 클론되어 있습니다. 최신 상태로 업데이트합니다."
    cd "$CLONE_DIR"
    git pull origin main
  else
    echo "디렉토리가 존재하지만 Git 저장소가 아닙니다. 디렉토리를 삭제 후 다시 클론합니다."
    rm -rf "$CLONE_DIR"
    echo "저장소를 클론합니다: $REPO_URL"
    git clone "$REPO_URL" "$CLONE_DIR"
  fi
else
  echo "저장소를 클론합니다: $REPO_URL"
  git clone "$REPO_URL" "$CLONE_DIR"
fi

# 클론 후 ubuntu 소유로 변경 (모든 파일)
sudo chown -R ubuntu:ubuntu "$CLONE_DIR"

echo "GitHub 저장소 클론 완료."

# ----------------------------------------
# 3. setup_all.sh 실행 (TrafficGenerator 디렉토리 내부의 스크립트)
# ----------------------------------------
echo "========================================"
echo "setup_all.sh 실행 시작"
echo "========================================"

SETUP_ALL_SCRIPT="$CLONE_DIR/TrafficGenerator/setup_all.sh"
if [ -f "$SETUP_ALL_SCRIPT" ]; then
    echo "setup_all.sh 스크립트를 실행합니다."
    chmod +x "$SETUP_ALL_SCRIPT"
    # sudo -E를 사용하여 환경 변수 보존 및 ubuntu 사용자로 실행
    sudo -E -u ubuntu bash "$SETUP_ALL_SCRIPT"
else
    echo "setup_all.sh 스크립트를 찾을 수 없습니다: $SETUP_ALL_SCRIPT"
    echo "나중에 setup_all.sh를 수동으로 실행해 주시기 바랍니다."
fi

echo "========================================"
echo "환경 변수 설정 및 초기화 작업 완료."
echo "========================================"
