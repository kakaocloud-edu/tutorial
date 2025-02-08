
#!/bin/bash
# setup_all.sh
# 이 스크립트는 ~/syu-DataAnalyze/TrafficGenerator 디렉토리에 config.yml을 생성하고,
# Go SDK 및 REST API 환경 설정을 자동으로 진행합니다.
# (환경 변수들은 setup_initial.sh에서 이미 설정된 상태라고 가정합니다.)

set -e

# 일반 사용자 홈 디렉토리 (예: ubuntu)
if [ -d "/home/ubuntu" ]; then
    USER_HOME="/home/ubuntu"
else
    USER_HOME="$HOME"
fi

###############################################################################
# 4. config.yml 파일 생성 (~/syu-DataAnalyze/TrafficGenerator)
###############################################################################
echo "========================================"
echo "4. config.yml 파일 생성"
echo "========================================"

CONFIG_DIR="$USER_HOME/syu-DataAnalyze/TrafficGenerator"
mkdir -p "$CONFIG_DIR"

cat <<EOF > "$CONFIG_DIR/config.yml"
# 공용 설정 파일: config.yml

pubsub:
  endpoint: "$PUBSUB_ENDPOINT"
  domain_id: "$DOMAIN_ID"
  project_id: "$PROJECT_ID"
  topic_name: "$TOPIC_NAME"
  topic_name_mk: "$TOPIC_NAME_MK"
  topic_description: "$TOPIC_DESCRIPTION"
  topic_retention_duration: "$TOPIC_RETENTION_DURATION"
  sub_name: "$SUB_NAME"
  credential_id: "$CREDENTIAL_ID"
  credential_secret: "$CREDENTIAL_SECRET"

object_storage_subscription:
  name: "$OBJECT_STORAGE_SUBSCRIPTION_NAME"
  bucket: "$OBJECT_STORAGE_BUCKET"
  export_interval_min: $EXPORT_INTERVAL_MIN
  file_prefix: "$FILE_PREFIX"
  file_suffix: "$FILE_SUFFIX"
  channel_count: $CHANNEL_COUNT
  max_channel_count: $MAX_CHANNEL_COUNT
  is_export_enabled: $IS_EXPORT_ENABLED

logging:
  filename: "$LOG_FILENAME"
  level: "$LOG_LEVEL"

threads:
  num_users: $NUM_USERS
  max_threads: $MAX_THREADS
  actions_per_user: $ACTIONS_PER_USER

api:
  base_url: "$API_BASE_URL"
  endpoints:
    add_user: "add_user"
    delete_user: "delete_user"
    login: "login"
    logout: "logout"
    products: "products"
    product_detail: "product"
    search: "search"
    checkout_history: "checkout_history"
    categories: "categories"
    category: "category"
    cart_view: "cart/view"
    cart_add: "cart/add"
    cart_remove: "cart/remove"
    checkout: "checkout"
    add_review: "add_review"
    error_page: "error"
  time_sleep_range:
    min: 0.1
    max: 1.0

age_threshold:
  young: 25
  middle: 50
EOF

echo "config.yml 생성 완료."

###############################################################################
# 5. Go SDK 설치 및 설정
###############################################################################
echo "========================================"
echo "5. Go SDK 설치 및 설정"
echo "========================================"

sudo apt update

# Go 다운로드 및 설치 (예: Go 1.20.5)
GO_VERSION="1.20.5"
GO_TAR_FILE="go${GO_VERSION}.linux-amd64.tar.gz"
GO_DOWNLOAD_URL="https://go.dev/dl/${GO_TAR_FILE}"

echo "Go ${GO_VERSION} 다운로드 및 설치 중..."
wget "$GO_DOWNLOAD_URL" -O "/tmp/$GO_TAR_FILE"

# 파일 무결성 체크: Go 1.20.5 tarball은 약 100MB 이상이어야 함 (최소 50MB로 체크)
MIN_SIZE=52428800
FILE_SIZE=$(stat -c%s "/tmp/$GO_TAR_FILE")
if [ "$FILE_SIZE" -lt "$MIN_SIZE" ]; then
  echo "오류: 다운로드된 Go tarball 크기가 너무 작습니다. (파일 크기: $FILE_SIZE bytes)"
  exit 1
fi

sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "/tmp/$GO_TAR_FILE"
rm "/tmp/$GO_TAR_FILE"

# PATH 업데이트 (현재 세션 및 영구 적용)
export PATH=$PATH:/usr/local/go/bin
if ! grep -q 'export PATH=\$PATH:/usr/local/go/bin' "$USER_HOME/.bashrc"; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> "$USER_HOME/.bashrc"
fi

echo "Go 설치 완료. 버전 정보:"
/usr/local/go/bin/go version

# GOPATH 및 GOCACHE 설정 (일반 사용자용)
export GOPATH="$USER_HOME/go"
export GOCACHE="$USER_HOME/.cache/go-build"
if ! grep -q 'export GOPATH=' "$USER_HOME/.bashrc"; then
    echo "export GOPATH=$GOPATH" >> "$USER_HOME/.bashrc"
fi
if ! grep -q 'export GOCACHE=' "$USER_HOME/.bashrc"; then
    echo "export GOCACHE=$GOCACHE" >> "$USER_HOME/.bashrc"
fi

# Pub/Sub SDK 다운로드 및 설치
GOSDK_DIR="$USER_HOME/gosdk"
mkdir -p "$GOSDK_DIR"
cd "$GOSDK_DIR"

PUBSUB_SDK_URL="https://objectstorage.kr-central-2.kakaocloud.com/v1/e9130193fc734337b2b0c1da50e44395/pubsub-sdk/go/v1.0.0/pubsub.tgz"
echo "Pub/Sub SDK 다운로드 및 압축 해제 중..."
wget "$PUBSUB_SDK_URL" -O pubsub.tgz
tar -xf pubsub.tgz
rm pubsub.tgz

# Go 모듈 초기화 (없으면)
if [ ! -f go.mod ]; then
    /usr/local/go/bin/go mod init trafficgenerator-go-sdk
fi

# Pub/Sub SDK 의존성 추가 및 로컬 경로 교체
/usr/local/go/bin/go mod edit -require github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go@v1.0.0
/usr/local/go/bin/go mod edit -replace github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go@v1.0.0=$GOSDK_DIR
/usr/local/go/bin/go mod tidy

# cmd 디렉토리 생성 후 이동
CMD_DIR="$GOSDK_DIR/cmd"
mkdir -p "$CMD_DIR"
cd "$CMD_DIR"

echo "필요한 Go 파일 다운로드 중..."
wget -O config.go https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/GO_SDK/config.go
wget -O publisher.go https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/GO_SDK/publisher.go
wget -O subscriber.go https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/GO_SDK/subscriber.go

/usr/local/go/bin/go get gopkg.in/yaml.v2
/usr/local/go/bin/go mod tidy

# 소유권 변경 (일반 사용자: ubuntu)
sudo chown -R ubuntu:ubuntu "$GOSDK_DIR"
sudo chown -R ubuntu:ubuntu "$USER_HOME/go"
sudo chown -R ubuntu:ubuntu "$USER_HOME/.cache/go-build"

echo "Go SDK 설정 완료."

###############################################################################
# 6. REST API 설치 및 설정
###############################################################################
echo "========================================"
echo "6. REST API 설치 및 설정"
echo "========================================"

REST_API_DIR="$USER_HOME/syu-DataAnalyze/TrafficGenerator/REST_API"
mkdir -p "$REST_API_DIR/VM1" "$REST_API_DIR/VM2"

sudo apt install -y python3 python3-pip

pip3 install --user requests pyyaml

echo "VM1 Python 스크립트 다운로드 중..."
cd "$REST_API_DIR/VM1"
wget -O pub_sub_send.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM1/pub_sub_send.py
wget -O traffic_generator.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM1/traffic_generator.py

echo "VM2 Python 스크립트 다운로드 중..."
cd "$REST_API_DIR/VM2"
wget -O create_subscription.py https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/create_subscription.py
wget -O create_topic.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/create_topic.py
wget -O restapi_pull_sub.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/restapi_pull_sub.py

cd "$REST_API_DIR"
wget -O config.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/config.py



chmod +x "$REST_API_DIR/VM1/"*.py "$REST_API_DIR/VM2/"*.py


echo "REST API 설정 완료."

###############################################################################
# 6.1. syu-DataAnalyze 디렉토리 전체에 대해 ubuntu 사용자에게 모든 권한 부여
###############################################################################
echo "========================================"
echo "전체 syu-DataAnalyze 디렉토리에 대해 ubuntu 사용자에게 모든 권한 부여 (777)"
echo "========================================"
sudo chown -R ubuntu:ubuntu "$USER_HOME/syu-DataAnalyze"
sudo chmod -R 777 "$USER_HOME/syu-DataAnalyze"
echo "모든 권한 부여 완료."

###############################################################################
# 7. 로그 파일 및 디렉토리 권한 수정 (REST API VM1)
###############################################################################
echo "========================================"
echo "로그 파일 및 디렉토리 소유권/쓰기 권한 설정"
echo "========================================"
sudo chown -R ubuntu:ubuntu "$REST_API_DIR/VM1"
chmod -R u+w "$REST_API_DIR/VM1"
echo "로그 파일 및 디렉토리 권한 설정 완료."

###############################################################################
# 8. 환경 변수 변경 사항 적용
###############################################################################
echo "========================================"
echo "환경 변수 변경 사항을 적용합니다."
if [ "$EUID" -ne 0 ]; then
    echo "현재 셸에 '$USER_HOME/.bashrc'를 소스합니다..."
    source "$USER_HOME/.bashrc"
else
    echo "현재 스크립트는 루트 권한으로 실행되었습니다."
    echo "일반 사용자(ubuntu)로 재로그인하거나 다음 명령어를 실행하여 환경 변수가 적용되도록 하세요:"
    echo "source $USER_HOME/.bashrc"
fi

###############################################################################
# 9. 완료 메시지
###############################################################################
echo "========================================"
echo "자동화 스크립트 실행 완료."
echo "Go SDK 및 REST API 설정이 완료되었습니다."
echo "========================================"
