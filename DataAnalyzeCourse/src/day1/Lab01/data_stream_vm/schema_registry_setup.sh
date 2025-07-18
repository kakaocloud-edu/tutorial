#!/usr/bin/env bash
set -euo pipefail

# 환경설정
CONFLUENT_VERSION="7.5.3"
CONFLUENT_HOME="/opt/confluent"
SCHEMA_REGISTRY_PROP="${CONFLUENT_HOME}/etc/schema-registry/schema-registry.properties"
SCHEMA_REGISTRY_PORT="8081"

# 환경변수 가져오기 (외부에서 설정된 경우)
if [ -f "/tmp/env_vars.sh" ]; then
    source /tmp/env_vars.sh
fi

# 기본값 설정 (환경변수가 없는 경우)
if [ -z "${KAFKA_BOOTSTRAP_SERVER:-}" ]; then
    echo "kakaocloud: 경고: KAFKA_BOOTSTRAP_SERVER 환경변수가 설정되지 않았습니다."
    echo "kakaocloud: 스크립트 실행 전에 환경변수를 설정해주세요."
    exit 1
fi

################################################################################
# 1. Java & Confluent 설치
################################################################################
echo "kakaocloud: 11. apt 업데이트 및 Java 설치"
sudo apt-get update -y || {
    echo "kakaocloud: apt 업데이트 실패"; exit 1;
}
sudo apt-get install -y openjdk-11-jdk wget curl jq || {
    echo "kakaocloud: Java 설치 실패"; exit 1;
}

echo "kakaocloud: 12. Confluent 패키지 다운로드 및 설치"
sudo wget https://packages.confluent.io/archive/7.5/confluent-community-7.5.3.tar.gz || {
    echo "kakaocloud: Confluent 패키지 다운로드 실패"; exit 1;
}
sudo tar -xzf confluent-community-7.5.3.tar.gz || {
    echo "kakaocloud: Confluent 패키지 압축 해제 실패"; exit 1;
}
sudo mv confluent-7.5.3 /opt/confluent || {
    echo "kakaocloud: Confluent 패키지 이동 실패"; exit 1;
}
sudo rm -f confluent-community-7.5.3.tar.gz || {
    echo "kakaocloud: 임시 파일 삭제 실패"; exit 1;
}

################################################################################
# 2. 환경변수 설정
################################################################################
echo "kakaocloud: 13. 환경변수 설정"
grep -qxF "export CONFLUENT_HOME=${CONFLUENT_HOME}" ~/.bashrc || \
  echo 'export CONFLUENT_HOME=/opt/confluent' >> ~/.bashrc
grep -qxF 'export PATH=$PATH:$CONFLUENT_HOME/bin' ~/.bashrc || \
  echo 'export PATH=$PATH:$CONFLUENT_HOME/bin' >> ~/.bashrc

# 현재 셸에도 적용
export CONFLUENT_HOME="${CONFLUENT_HOME}"
export PATH="$PATH:${CONFLUENT_HOME}/bin"

# 디렉토리 권한 설정
sudo chown -R ubuntu:ubuntu "${CONFLUENT_HOME}" || {
    echo "kakaocloud: Confluent 디렉토리 권한 설정 실패"; exit 1;
}

################################################################################
# 3. Schema Registry 설정
################################################################################
echo "kakaocloud: 14. Schema Registry 설정"

# 기존 설정 파일 백업
sudo cp "${SCHEMA_REGISTRY_PROP}" "${SCHEMA_REGISTRY_PROP}.backup" || {
    echo "kakaocloud: 설정 파일 백업 실패"; exit 1;
}

# Kafka broker 주소 변경
sudo sed -i "s|kafkastore.bootstrap.servers=.*|kafkastore.bootstrap.servers=${KAFKA_BOOTSTRAP_SERVER}|g" \
    "${SCHEMA_REGISTRY_PROP}" || {
    echo "kakaocloud: Kafka broker 주소 변경 실패"; exit 1;
}

# 외부 접근을 위한 리스너 설정
sudo sed -i "s|#listeners=.*|listeners=http://0.0.0.0:${SCHEMA_REGISTRY_PORT}|g" \
    "${SCHEMA_REGISTRY_PROP}" || {
    echo "kakaocloud: 리스너 설정 변경 실패"; exit 1;
}

# listeners 설정이 없으면 추가
if ! grep -q "^listeners=" "${SCHEMA_REGISTRY_PROP}"; then
    echo "listeners=http://0.0.0.0:${SCHEMA_REGISTRY_PORT}" >> "${SCHEMA_REGISTRY_PROP}" || {
        echo "kakaocloud: 리스너 설정 추가 실패"; exit 1;
    }
fi

################################################################################
# 4. systemd 서비스 등록
################################################################################
echo "kakaocloud: 15. systemd 유닛 파일 생성 및 Schema Registry 서비스 등록"
cat <<EOF | sudo tee /etc/systemd/system/schema-registry.service
[Unit]
Description=Confluent Schema Registry
Documentation=https://docs.confluent.io/platform/current/schema-registry/index.html
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
Environment="KAFKA_HEAP_OPTS=-Xms256M -Xmx512M"
Environment="SCHEMA_REGISTRY_HEAP_OPTS=-Xms256M -Xmx512M"
Environment="CONFLUENT_HOME=${CONFLUENT_HOME}"
ExecStart=${CONFLUENT_HOME}/bin/schema-registry-start ${CONFLUENT_HOME}/etc/schema-registry/schema-registry.properties
ExecStop=${CONFLUENT_HOME}/bin/schema-registry-stop
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
if [ $? -ne 0 ]; then echo "kakaocloud: Schema Registry Service 파일 작성 실패"; exit 1; fi

################################################################################
# 5. 서비스 시작
################################################################################
echo "kakaocloud: 16. Schema Registry 서비스 시작"
sudo systemctl daemon-reload || { echo "kakaocloud: daemon-reload 실패"; exit 1; }
sudo systemctl enable schema-registry.service || { echo "kakaocloud: schema-registry 서비스 자동 시작 설정 실패"; exit 1; }
sudo systemctl start schema-registry.service || { echo "kakaocloud: schema-registry 서비스 시작 실패"; exit 1; }

# 서비스 시작 대기
sleep 30

sudo systemctl status schema-registry.service || { echo "kakaocloud: schema-registry 서비스 상태 확인 실패"; exit 1; }

################################################################################
# 6. 연결 테스트
################################################################################
echo "kakaocloud: 17. Schema Registry 연결 테스트"
HOST_IP=$(hostname -I | awk '{print $1}')
SCHEMA_REGISTRY_URL="http://localhost:${SCHEMA_REGISTRY_PORT}"

# 연결 테스트 (최대 10번 시도)
for i in {1..10}; do
    if curl -f -s "${SCHEMA_REGISTRY_URL}/subjects" > /dev/null; then
        echo "kakaocloud: 18. Schema Registry 연결 성공 (시도: $i)"
        break
    else
        echo "kakaocloud: Schema Registry 연결 실패 (시도: $i/10)"
        if [ $i -eq 10 ]; then
            echo "kakaocloud: ✗ Schema Registry 연결 최종 실패"
            sudo journalctl -u schema-registry -n 20
            exit 1
        fi
        sleep 5
    fi
done


# 등록된 스키마 목록 확인
curl -s "${SCHEMA_REGISTRY_URL}/subjects" | jq . || echo "[]"

echo "kakaocloud: Setup 완료"
