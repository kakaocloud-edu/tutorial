#!/bin/bash
set -euxo pipefail
sleep 800

# extensions.loadList 업데이트
echo "kakaocloud: extensions.loadList 업데이트"
sudo sed -i 's|^druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions","druid-parquet-extensions","mysql-metadata-storage","druid-hdfs-storage","druid-kafka-indexing-service","druid-datasketches","druid-multi-stage-query"]|' \
  /opt/apache-druid-25.0.0/conf/druid/cluster/_common/common.runtime.properties || { echo "kakaocloud: cluster/_common 업데이트 실패"; exit 1; }
sudo sed -i 's|^druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions","druid-hdfs-storage","druid-kafka-indexing-service","druid-datasketches","druid-multi-stage-query"]|' \
  /opt/apache-druid-25.0.0/conf/druid/auto/_common/common.runtime.properties || { echo "kakaocloud: auto/_common 업데이트 실패"; exit 1; }

echo "kakaocloud: Setup 완료"