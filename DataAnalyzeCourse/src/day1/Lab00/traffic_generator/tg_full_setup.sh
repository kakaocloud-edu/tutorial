#!/bin/bash
# setup_all.sh

echo "kakaocloud: 3.Variables validity test start"
required_variables=(
    DOMAIN_ID PROJECT_ID CREDENTIAL_ID CREDENTIAL_SECRET API_BASE_URL 
    TOPIC_NAME SUB_NAME TOPIC_NAME_MK OBJECT_STORAGE_SUBSCRIPTION_NAME 
    OBJECT_STORAGE_BUCKET PUBSUB_ENDPOINT
)

for var in "${required_variables[@]}"; do
    [[ -z "${!var}" ]] && { echo "kakaocloud: 필수 환경변수 $var 가 설정되지 않았습니다. 스크립트를 종료합니다."; exit 1; }
done
echo "kakaocloud: Variables are valid"

# 기존 /home/ubuntu/tutorial 디렉토리가 존재하면 삭제
if [ -d "/home/ubuntu/tutorial" ]; then
    rm -rf "/home/ubuntu/tutorial" || { echo "kakaocloud: Failed to remove existing tutorial directory"; exit 1; }
    echo "kakaocloud: Existing tutorial directory removed"
fi

# Git 클론
cd /home/ubuntu
git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || { echo "kakaocloud: Failed to git clone"; exit 1; }

# DataAnalyzeCourse 디렉토리만 복사
cp -r /home/ubuntu/tutorial/DataAnalyzeCourse /home/ubuntu/ || { echo "kakaocloud: Failed to copy DataAnalyzeCourse"; exit 1; }

# 깃 클론한 디렉토리 삭제
rm -rf /home/ubuntu/tutorial || { echo "kakaocloud: Failed to remove tutorial directory"; exit 1; }

echo "kakaocloud: DataAnalyzeCourse copied successfully"

echo "4. config.yml 파일 생성"
CONFIG_DIR="/home/ubuntu/DataAnalyzeCourse/src/day1"
mkdir -p "$CONFIG_DIR" || { echo "kakaocloud: Failed to create $CONFIG_DIR"; exit 1; }

cat <<EOF > "$CONFIG_DIR/config.yml"
# 공용 설정 파일: config.yml

pubsub:
  endpoint: "$PUBSUB_ENDPOINT"
  domain_id: "$DOMAIN_ID"
  project_id: "$PROJECT_ID"
  topic_name: "$TOPIC_NAME"
  topic_name_mk: "$TOPIC_NAME_MK"
  topic_description: ""
  topic_retention_duration: "600s"
  sub_name: "$SUB_NAME"
  credential_id: "$CREDENTIAL_ID"
  credential_secret: "$CREDENTIAL_SECRET"

object_storage_subscription:
  name: "$OBJECT_STORAGE_SUBSCRIPTION_NAME"
  bucket: "$OBJECT_STORAGE_BUCKET"
  export_interval_min: 10
  file_prefix: ""
  file_suffix: ".log"
  channel_count: 4
  max_channel_count: 10
  is_export_enabled: true

logging:
  filename: "traffic_generator.log"
  level: "INFO"

threads:
  num_users: 5
  max_threads: 5
  actions_per_user: 30

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

echo "5. Go SDK 설치 및 설정"

sudo apt update || { echo "kakaocloud: Failed to update apt repository"; exit 1; }

# Go 다운로드 및 설치 (예: Go 1.20.5)
GO_VERSION="1.20.5"
GO_TAR_FILE="go${GO_VERSION}.linux-amd64.tar.gz"
GO_DOWNLOAD_URL="https://go.dev/dl/${GO_TAR_FILE}"

echo "Go ${GO_VERSION} 다운로드 및 설치 중..."
wget "$GO_DOWNLOAD_URL" -O "/tmp/$GO_TAR_FILE" || { echo "kakaocloud: Failed to download Go tarball"; exit 1; }

# 파일 무결성 체크: Go 1.20.5 tarball은 약 100MB 이상이어야 함 (최소 50MB로 체크)
MIN_SIZE=52428800
FILE_SIZE=$(stat -c%s "/tmp/$GO_TAR_FILE")
if [ "$FILE_SIZE" -lt "$MIN_SIZE" ]; then
  echo "오류: 다운로드된 Go tarball 크기가 너무 작습니다. (파일 크기: $FILE_SIZE bytes)"
  exit 1
fi

sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "/tmp/$GO_TAR_FILE" || { echo "kakaocloud: Failed to extract Go tarball"; exit 1; }
rm "/tmp/$GO_TAR_FILE"

# PATH 업데이트 (현재 세션 및 영구 적용)
export PATH=$PATH:/usr/local/go/bin
if ! grep -q 'export PATH=\$PATH:/usr/local/go/bin' "/home/ubuntu/.bashrc"; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> "/home/ubuntu/.bashrc"
fi

echo "Go 설치 완료. 버전 정보:"
/usr/local/go/bin/go version

# GOPATH 및 GOCACHE 설정 (일반 사용자용)
export GOPATH="/home/ubuntu/go"
export GOCACHE="/home/ubuntu/.cache/go-build"
if ! grep -q 'export GOPATH=' "/home/ubuntu/.bashrc"; then
    echo "export GOPATH=$GOPATH" >> "/home/ubuntu/.bashrc"
fi
if ! grep -q 'export GOCACHE=' "/home/ubuntu/.bashrc"; then
    echo "export GOCACHE=$GOCACHE" >> "/home/ubuntu/.bashrc"
fi

# Pub/Sub SDK 다운로드 및 설치
GOSDK_DIR="/home/ubuntu/gosdk"
# GOSDK_DIR이 이미 있다면 삭제 후 새로 생성
if [ -d "$GOSDK_DIR" ]; then
    sudo rm -rf "$GOSDK_DIR" || { echo "kakaocloud: Failed to remove existing GOSDK_DIR"; exit 1; }
fi
mkdir -p "$GOSDK_DIR"
cd "$GOSDK_DIR" || { echo "kakaocloud: Failed to navigate to $GOSDK_DIR"; exit 1; }

PUBSUB_SDK_URL="https://objectstorage.kr-central-2.kakaocloud.com/v1/e9130193fc734337b2b0c1da50e44395/pubsub-sdk/go/v1.0.0/pubsub.tgz"
echo "Pub/Sub SDK 다운로드 및 압축 해제 중..."

# 기존 pubsub.tgz 파일이 있다면 삭제
if [ -f "pubsub.tgz" ]; then
    sudo rm -f pubsub.tgz || { echo "kakaocloud: Failed to remove existing pubsub.tgz"; exit 1; }
fi

sudo wget "$PUBSUB_SDK_URL" -O pubsub.tgz || { echo "kakaocloud: Failed to download Pub/Sub SDK"; exit 1; }
sudo tar -xf pubsub.tgz || { echo "kakaocloud: Failed to extract Pub/Sub SDK"; exit 1; }
sudo rm -f pubsub.tgz

# 변경: GOSDK_DIR의 소유권을 현재 사용자로 변경하여 이후 권한 문제 방지
sudo chown -R $(whoami):$(whoami) "$GOSDK_DIR"

# GO_SDK 디렉토리 (~/DataAnalyzeCourse/src/TrafficGenerator/GO_SDK)에서 실행
# 경로 이동하는 로직필요
cd /home/ubuntu/DataAnalyzeCourse/src/TrafficGenerator/GO_SDK

# go.mod 파일이 없으면 초기화
if [ ! -f go.mod ]; then
    /usr/local/go/bin/go mod init trafficgenerator-go-sdk || { echo "kakaocloud: Failed to initialize Go module"; exit 1; }
fi

# Pub/Sub SDK 의존성 추가 및 로컬 경로 교체 (버전은 v0.0.0 사용)
# 원격에서 의존성을 가져오지만, 실제 사용할 버전은 로컬에 있는 모듈과 일치시킵니다.
 /usr/local/go/bin/go mod edit -require github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go@v0.0.0 || { echo "kakaocloud: Failed to add Pub/Sub SDK dependency"; exit 1; }
 /usr/local/go/bin/go mod edit -replace github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go=/home/ubuntu/gosdk || { echo "kakaocloud: Failed to replace Pub/Sub SDK local path"; exit 1; }
 /usr/local/go/bin/go mod tidy || { echo "kakaocloud: Failed to tidy Go modules"; exit 1; }



 sudo apt install -y python3 python3-pip || { echo "kakaocloud: Failed to install python3 and pip"; exit 1; }
 pip3 install --user requests pyyaml || { echo "kakaocloud: Failed to install Python dependencies"; exit 1; }


 echo "========================================"
echo "자동화 임시 완료스크립트 실행 완료."
echo "========================================"








