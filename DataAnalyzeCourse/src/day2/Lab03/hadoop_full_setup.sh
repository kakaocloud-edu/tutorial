#!/bin/bash
set -euxo pipefail

# 1. OpenJDK 17 설치
echo "kakaocloud: 1. OpenJDK 17 설치"
sudo apt update || { echo "kakaocloud: 1. OpenJDK 17 설치 - apt update 실패"; exit 1; }
sudo apt install -y openjdk-17-jdk || { echo "kakaocloud: OpenJDK 17 설치 - openjdk 설치 실패"; exit 1; }

# 2. 환경 변수 설정 (/etc/profile.d/druid.sh)
echo "kakaocloud: 2. 환경 변수 설정"
cat << 'EOF' | sudo tee /etc/profile.d/druid.sh || { echo "kakaocloud: druid.sh 쓰기 실패"; exit 1; }
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
EOF
source /etc/profile.d/druid.sh || { echo "kakaocloud: druid.sh 적용 실패"; exit 1; }

# 3. Druid 33.0.0 다운로드 및 압축 해제
echo "kakaocloud: 3. Druid 33.0.0 다운로드 및 압축 해제"
cd /opt || { echo "kakaocloud: 디렉터리 이동 실패"; exit 1; }
sudo wget -q https://downloads.apache.org/druid/33.0.0/apache-druid-33.0.0-bin.tar.gz || { echo "kakaocloud: Druid 다운로드 실패"; exit 1; }
sudo tar -xzf apache-druid-33.0.0-bin.tar.gz || { echo "kakaocloud: Druid 압축 해제 실패"; exit 1; }

# 4. 기존 설정 파일 복사 및 MySQL 드라이버 복사
echo "kakaocloud: 4. 기존 설정 파일 복사 및 MySQL 드라이버 복사"
sudo cp -r /opt/apache-druid-25.0.0/conf /opt/apache-druid-33.0.0/ || { echo "kakaocloud: 설정 파일 복사 실패"; exit 1; }
sudo cp /opt/apache-druid-25.0.0/extensions/mysql-metadata-storage/mysql-connector-java-5.1.49.jar \
         /opt/apache-druid-33.0.0/extensions/mysql-metadata-storage/ || { echo "kakaocloud: MySQL 드라이버 복사 실패"; exit 1; }

# 5. 심볼릭 링크 갱신
echo "kakaocloud: 5. 심볼릭 링크 갱신"
sudo ln -sfn /opt/apache-druid-33.0.0 /opt/druid || { echo "kakaocloud: 심볼릭 링크 갱신 실패"; exit 1; }

# 6. 기존 supervise 프로세스 종료
echo "kakaocloud: 6. 기존 supervise 프로세스 종료"
sudo pkill -f /opt/druid/bin/supervise || true

# 7. 로그 디렉터리 및 파일 권한 설정
echo "kakaocloud: 7. 로그 디렉터리 및 파일 권한 설정"
sudo mkdir -p /opt/druid/log || { echo "kakaocloud: 로그 디렉터리 생성 실패"; exit 1; }
sudo touch /opt/druid/log/supervise.log || { echo "kakaocloud: supervise.log 생성 실패"; exit 1; }
sudo chown ubuntu:ubuntu /opt/druid/log/supervise.log || { echo "kakaocloud: 소유권 변경 실패"; exit 1; }
sudo chmod 664 /opt/druid/log/supervise.log || { echo "kakaocloud: 권한 변경 실패"; exit 1; }

# 8. 락 파일(.lock) 삭제
echo "kakaocloud: 8. 락 파일(.lock) 삭제"
sudo rm -f /opt/apache-druid-33.0.0/var/sv/.lock || { echo "kakaocloud: .lock 삭제 실패"; exit 1; }

# 9. dummy trustStore 생성
echo "kakaocloud: 9. dummy trustStore 생성"
sudo keytool -genkeypair -alias temp \
  -keystore /opt/apache-druid-33.0.0/dummy.jks \
  -storepass changeit \
  -keypass changeit \
  -dname "CN=temp" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 3650 || { echo "kakaocloud: dummy.jks 생성 실패"; exit 1; }

# 10. common.runtime.properties 옵션 추가
echo "kakaocloud: 10. common.runtime.properties 옵션 추가"
for file in /opt/apache-druid-*/conf/druid/*/_common/common.runtime.properties; do
  sudo grep -q "druid.enableTlsPort" "$file" || \
    echo "druid.enableTlsPort=false" | sudo tee -a "$file" > /dev/null || { echo "kakaocloud: druid.enableTlsPort 추가 실패 ($file)"; exit 1; }
  sudo grep -q "druid.client.https.trustStorePath" "$file" || \
    echo "druid.client.https.trustStorePath=/opt/apache-druid-33.0.0/dummy.jks" | sudo tee -a "$file" > /dev/null || { echo "kakaocloud: trustStorePath 추가 실패 ($file)"; exit 1; }
  sudo grep -q "druid.client.https.trustStorePassword" "$file" || \
    echo "druid.client.https.trustStorePassword=changeit" | sudo tee -a "$file" > /dev/null || { echo "kakaocloud: trustStorePassword 추가 실패 ($file)"; exit 1; }
  sudo grep -q "druid.client.https.trustStoreType" "$file" || \
    echo "druid.client.https.trustStoreType=JKS" | sudo tee -a "$file" > /dev/null || { echo "kakaocloud: trustStoreType 추가 실패 ($file)"; exit 1; }
done
sudo ufw allow 3008/tcp || { echo "kakaocloud: 10. ufw 포트 허용 실패"; exit 1; }

# 11. JAVA_OPTS 환경 변수 설정
echo "kakaocloud: 11. JAVA_OPTS 환경 변수 설정"
cat << 'EOF' | sudo tee /etc/profile.d/druid_java_opts.sh || { echo "kakaocloud: JAVA_OPTS 파일 쓰기 실패"; exit 1; }
export JAVA_OPTS="\
  -Ddruid.enableTlsPort=false \
  -Ddruid.client.https.trustStorePath=/opt/apache-druid-33.0.0/dummy.jks \
  -Ddruid.client.https.trustStorePassword=changeit \
  -Ddruid.client.https.trustStoreType=JKS"
EOF
source /etc/profile.d/druid_java_opts.sh || { echo "kakaocloud: JAVA_OPTS 적용 실패"; exit 1; }

# 12. extensions.loadList 업데이트
echo "kakaocloud: 12. extensions.loadList 업데이트"
sudo sed -i 's|^druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions","druid-parquet-extensions","mysql-metadata-storage","druid-hdfs-storage","druid-kafka-indexing-service","druid-datasketches","druid-multi-stage-query"]|' \
  /opt/apache-druid-33.0.0/conf/druid/cluster/_common/common.runtime.properties || { echo "kakaocloud: cluster/_common 업데이트 실패"; exit 1; }
sudo sed -i 's|^druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions","druid-hdfs-storage","druid-kafka-indexing-service","druid-datasketches","druid-multi-stage-query"]|' \
  /opt/apache-druid-33.0.0/conf/druid/auto/_common/common.runtime.properties || { echo "kakaocloud: auto/_common 업데이트 실패"; exit 1; }

# 13. worker.capacity 조정
echo "kakaocloud: 13. worker.capacity 조정"
sudo sed -i 's/^druid\.worker\.capacity=4$/druid.worker.capacity=8/' /opt/druid/conf/druid/cluster/data/middleManager/runtime.properties \
  || { echo "kakaocloud: worker.capacity 조정 실패"; exit 1; }

echo "kakaocloud: Setup 완료"
