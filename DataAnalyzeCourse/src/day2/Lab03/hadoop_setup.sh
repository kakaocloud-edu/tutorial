#!/bin/bash
set -euxo pipefail
sleep 380

# extensions.loadList 업데이트
echo "kakaocloud: 1. extensions.loadList 업데이트"
sudo sed -i 's|^druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions","druid-parquet-extensions","mysql-metadata-storage","druid-hdfs-storage","druid-kafka-indexing-service","druid-datasketches","druid-multi-stage-query"]|' \
  /opt/apache-druid-25.0.0/conf/druid/cluster/_common/common.runtime.properties || { echo "kakaocloud: cluster/_common 업데이트 실패"; exit 1; }
sudo sed -i 's|^druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions","druid-hdfs-storage","druid-kafka-indexing-service","druid-datasketches","druid-multi-stage-query"]|' \
  /opt/apache-druid-25.0.0/conf/druid/auto/_common/common.runtime.properties || { echo "kakaocloud: auto/_common 업데이트 실패"; exit 1; }

# 마스터, 워커 노드 모두에서 Druid 관련 서비스 재시작
echo "kakaocloud: 2. extensions.loadList 업데이트"
sudo systemctl restart 'druid-*' || { echo "kakaocloud: Druid 관련 서비스 재시작 실패"; exit 1; }

echo "kakaocloud: Setup 완료"