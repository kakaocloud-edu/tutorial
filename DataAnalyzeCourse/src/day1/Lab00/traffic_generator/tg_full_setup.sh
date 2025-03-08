#!/bin/bash
# setup_all.sh

# === 설정 변수 (버전, 경로, 환경변수 등) ===
GO_VERSION="1.20.5"
GO_TAR_FILE="go${GO_VERSION}.linux-amd64.tar.gz"
GO_DOWNLOAD_URL="https://go.dev/dl/${GO_TAR_FILE}"
GOSDK_DIR="/home/ubuntu/gosdk"
CONFIG_DIR="/home/ubuntu/DataAnalyzeCourse/src/day1/Lab00/traffic_generator"
GOPATH_VAL="/home/ubuntu/go"
GOCACHE_VAL="/home/ubuntu/.cache/go-build"

# === 스크립트 시작 ===
echo "kakaocloud: 1. 스크립트 시작"

echo "kakaocloud: 2. 필수 환경변수 검증 시작"
required_variables=(
    DOMAIN_ID PROJECT_ID CREDENTIAL_ID CREDENTIAL_SECRET API_BASE_URL 
    TOPIC_NAME SUB_NAME TOPIC_NAME_MK OBJECT_STORAGE_SUBSCRIPTION_NAME 
    OBJECT_STORAGE_BUCKET PUBSUB_ENDPOINT
)
for var in "${required_variables[@]}"; do
    if [ -z "${!var}" ]; then
        echo "kakaocloud: 필수 환경변수 $var 가 설정되지 않았습니다. 스크립트를 종료합니다."
        exit 1
    fi
done

echo "kakaocloud: 3. 기존 tutorial 디렉토리 삭제 확인"
if [ -d "/home/ubuntu/tutorial" ]; then
    rm -rf "/home/ubuntu/tutorial" || { echo "kakaocloud: 기존 tutorial 디렉토리 삭제 실패"; exit 1; }
fi

echo "kakaocloud: 4. Git 클론 시작"
cd /home/ubuntu
git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || { echo "kakaocloud: Git 클론 실패"; exit 1; }

echo "kakaocloud: 5. DataAnalyzeCourse 디렉토리 복사 시작"
cp -r /home/ubuntu/tutorial/DataAnalyzeCourse /home/ubuntu/ || { echo "kakaocloud: DataAnalyzeCourse 복사 실패"; exit 1; }

echo "kakaocloud: 6. Git 클론한 tutorial 디렉토리 삭제 시작"
rm -rf /home/ubuntu/tutorial || { echo "kakaocloud: Git 클론한 tutorial 디렉토리 삭제 실패"; exit 1; }

echo "kakaocloud: 7. config.yml 파일 생성 시작"
mkdir -p "$CONFIG_DIR" || { echo "kakaocloud: config.yml 파일 생성 디렉토리($CONFIG_DIR) 생성 실패"; exit 1; }
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

echo "kakaocloud: 8. Go SDK 설치 및 설정 시작"
sudo apt update || { echo "kakaocloud: apt 업데이트 실패"; exit 1; }
wget "$GO_DOWNLOAD_URL" -O "/tmp/$GO_TAR_FILE" || { echo "kakaocloud: Go tarball 다운로드 실패"; exit 1; }
MIN_SIZE=52428800
FILE_SIZE=$(stat -c%s "/tmp/$GO_TAR_FILE")
if [ "$FILE_SIZE" -lt "$MIN_SIZE" ]; then
  echo "kakaocloud: 오류 - 다운로드된 Go tarball 크기가 너무 작습니다. (파일 크기: $FILE_SIZE bytes)"
  exit 1
fi
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "/tmp/$GO_TAR_FILE" || { echo "kakaocloud: Go tarball 압축 해제 실패"; exit 1; }
rm "/tmp/$GO_TAR_FILE"

export PATH=$PATH:/usr/local/go/bin
if ! grep -q 'export PATH=\$PATH:/usr/local/go/bin' "/home/ubuntu/.bashrc"; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> "/home/ubuntu/.bashrc"
fi

export GOPATH="$GOPATH_VAL"
export GOCACHE="$GOCACHE_VAL"
if ! grep -q 'export GOPATH=' "/home/ubuntu/.bashrc"; then
    echo "export GOPATH=$GOPATH_VAL" >> "/home/ubuntu/.bashrc"
fi
if ! grep -q 'export GOCACHE=' "/home/ubuntu/.bashrc"; then
    echo "export GOCACHE=$GOCACHE_VAL" >> "/home/ubuntu/.bashrc"
fi

echo "kakaocloud: 9. Pub/Sub SDK 다운로드 및 설치 시작"
if [ -d "$GOSDK_DIR" ]; then
    sudo rm -rf "$GOSDK_DIR" || { echo "kakaocloud: 기존 GOSDK_DIR 삭제 실패"; exit 1; }
fi
mkdir -p "$GOSDK_DIR"
cd "$GOSDK_DIR" || { echo "kakaocloud: GOSDK_DIR로 이동 실패"; exit 1; }
PUBSUB_SDK_URL="https://objectstorage.kr-central-2.kakaocloud.com/v1/e9130193fc734337b2b0c1da50e44395/pubsub-sdk/go/v1.0.0/pubsub.tgz"
if [ -f "pubsub.tgz" ]; then
    sudo rm -f pubsub.tgz || { echo "kakaocloud: 기존 pubsub.tgz 삭제 실패"; exit 1; }
fi
sudo wget "$PUBSUB_SDK_URL" -O pubsub.tgz || { echo "kakaocloud: Pub/Sub SDK 다운로드 실패"; exit 1; }
sudo tar -xf pubsub.tgz || { echo "kakaocloud: Pub/Sub SDK 압축 해제 실패"; exit 1; }
sudo rm -f pubsub.tgz

echo "kakaocloud: 10. Go 작업 디렉토리로 이동 (DataAnalyzeCourse/src/day1/Lab01/go)"
cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/go || { echo "kakaocloud: Go 작업 디렉토리로 이동 실패"; exit 1; }

echo "kakaocloud: 11. Go 모듈 초기화 검사"
if [ ! -f go.mod ]; then
    /usr/local/go/bin/go mod init trafficgenerator-go-sdk || { echo "kakaocloud: Go 모듈 초기화 실패"; exit 1; }
fi

echo "kakaocloud: 12. Pub/Sub SDK 의존성 추가 및 로컬 경로 교체 시작"
 /usr/local/go/bin/go mod edit -require github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go@v0.0.0 || { echo "kakaocloud: Pub/Sub SDK 의존성 추가 실패"; exit 1; }
 /usr/local/go/bin/go mod edit -replace github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go=/home/ubuntu/gosdk || { echo "kakaocloud: Pub/Sub SDK 로컬 경로 교체 실패"; exit 1; }

echo "kakaocloud: 13. go mod tidy 실행 시작"
 /usr/local/go/bin/go mod tidy || { echo "kakaocloud: go mod tidy 실패"; exit 1; }

echo "kakaocloud: 14. Python3 및 pip 설치 시작"
sudo apt install -y python3 python3-pip || { echo "kakaocloud: Python3 및 pip 설치 실패"; exit 1; }

echo "kakaocloud: 15. Python dependencies (requests, pyyaml) 설치 시작"
pip3 install --user requests pyyaml || { echo "kakaocloud: Python dependencies 설치 실패"; exit 1; }

# 전체 권한 문제 방지를 위한 소유권 변경 (하위 모든 경로 적용)
sudo chown -R ubuntu:ubuntu /home/ubuntu/go /home/ubuntu/gosdk /home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/go

# --- 하단부 추가: OpenJDK 및 Apache Kafka 설치 ---
echo "kakaocloud: 16. OpenJDK 21 설치 시작"
sudo apt install -y openjdk-21-jdk || { echo "kakaocloud: OpenJDK 21 설치 실패"; exit 1; }

echo "kakaocloud: 17. Apache Kafka 설치 시작"
cd /opt || { echo "kakaocloud: /opt 디렉토리 이동 실패"; exit 1; }
sudo wget -qO- https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz | sudo tar -xz || { echo "kakaocloud: Kafka 압축 해제 실패"; exit 1; }
sudo mv kafka_2.13-3.7.1 kafka || { echo "kakaocloud: Kafka 디렉토리 이름 변경 실패"; exit 1; }

# 현재 쉘 세션의 PATH에 변경 내용 적용
source ~/.bashrc

echo "========================================"
echo "kakaocloud: 자동화 임시 완료스크립트 실행 완료."
echo "========================================"
