#!/bin/bash


# ------------------------------------------------------------------------------
# 0. 부팅 후 대기 (시스템/네트워크 안정화 대기)
# ------------------------------------------------------------------------------

# 로그 파일 경로 설정
LOGFILE="/home/ubuntu/setup.log"

# 로그 기록 함수
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGFILE"
}

log "Step 0: 시스템 안정화 대기 후 스크립트 시작"

# ------------------------------------------------------------------------------
# 1. apt 패키지 목록 업데이트 및 업그레이드
# ------------------------------------------------------------------------------
log "Step 1: apt 패키지 목록 업데이트 시작"
sudo apt update -y
log "Step 1: apt 패키지 목록 업데이트 완료"

# (선택) 업그레이드 단계: 필요한 경우 아래 주석 해제
# log "Step 1-1: apt 시스템 업그레이드 시작"
# sudo apt upgrade -y
# log "Step 1-1: apt 시스템 업그레이드 완료"

# ------------------------------------------------------------------------------
# 2. 필요한 패키지 설치
# ------------------------------------------------------------------------------
log "Step 2: 필요한 패키지 설치 시작"
sudo apt install -y python3 python3-pip openjdk-21-jdk unzip jq aria2
log "Step 2: 필요한 패키지 설치 완료"

# ------------------------------------------------------------------------------
# 3. Kafka 다운로드 및 설치 (aria2 이용해 병렬 다운로드)
# ------------------------------------------------------------------------------
log "Step 3: Kafka 다운로드 및 설치 시작 (aria2 사용)"
KAFKA_URL="https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz"
KAFKA_TGZ="/home/ubuntu/kafka_2.13-3.7.1.tgz"

# aria2: -x 16, -s 16 => 최대 16개 연결, 분할 다운로드
aria2c -x 16 -s 16 -d /home/ubuntu -o kafka_2.13-3.7.1.tgz "$KAFKA_URL" >> "$LOGFILE" 2>&1

tar -xzf "$KAFKA_TGZ" -C /home/ubuntu >> "$LOGFILE" 2>&1
rm "$KAFKA_TGZ" >> "$LOGFILE" 2>&1
mv /home/ubuntu/kafka_2.13-3.7.1 /home/ubuntu/kafka >> "$LOGFILE" 2>&1
log "Step 3: Kafka 다운로드 및 설치 완료"

# ------------------------------------------------------------------------------
# 4. Confluent Hub Client 설치 (마찬가지로 aria2로 다운로드)
# ------------------------------------------------------------------------------
log "Step 4: Confluent Hub Client 설치 시작"
sudo mkdir -p /confluent-hub/plugins

CONFLUENT_HUB_DIR="/confluent-hub"
CONFLUENT_HUB_URL="http://client.hub.confluent.io/confluent-hub-client-latest.tar.gz"
CONFLUENT_HUB_FILE="confluent-hub-client-latest.tar.gz"

cd /
sudo mkdir -p "$CONFLUENT_HUB_DIR"
cd "$CONFLUENT_HUB_DIR"

# aria2 다운로드
aria2c -x 16 -s 16 -o "$CONFLUENT_HUB_FILE" "$CONFLUENT_HUB_URL"

sudo tar -zxvf "$CONFLUENT_HUB_FILE"
log "Step 4: Confluent Hub Client 설치 완료"

# ------------------------------------------------------------------------------
# 5. .bashrc에 환경 변수 등록
# ------------------------------------------------------------------------------
log "Step 5: .bashrc에 환경 변수 등록 시작"
cat <<'EOF' >> /home/ubuntu/.bashrc
# Confluent 설정
export CONFLUENT_HOME='/confluent-hub'
export PATH="$PATH:$CONFLUENT_HOME/bin"

# Java 설정
export JAVA_HOME='/usr/lib/jvm/java-21-openjdk-amd64'
export PATH="$JAVA_HOME/bin:$PATH"
EOF
log "Step 5: .bashrc에 환경 변수 등록 완료"

# ------------------------------------------------------------------------------
# 6. .bashrc 적용
# ------------------------------------------------------------------------------
log "Step 6: .bashrc 적용 (source) 시작"
# (실제 ssh 세션과는 쉘 프로세스가 달라 영구 반영되진 않지만, 현재 쉘에는 적용됨)
source /home/ubuntu/.bashrc
log "Step 6: .bashrc 적용 완료"

# ------------------------------------------------------------------------------
# 완료
# ------------------------------------------------------------------------------
log "Setup 완료"
