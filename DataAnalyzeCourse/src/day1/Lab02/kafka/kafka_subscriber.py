#!/usr/bin/env python3
from kafka import KafkaConsumer, TopicPartition
import os
import time

#################################
# 사용자 수정 가능한 설정 변수
#################################
TOPIC = 'python-topic'                          # 구독할 토픽
CONSUMER_GROUP = 'python-consumer-group'        # 컨슈머 그룹 ID
BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
if not BOOTSTRAP_SERVERS:
    raise ValueError("환경 변수 'KAFKA_BOOTSTRAP_SERVERS'가 설정되어 있지 않습니다.")
BOOTSTRAP_SERVERS_LIST = [server.strip() for server in BOOTSTRAP_SERVERS.split(',')]
PARTITION = 0                                   # 메시지를 읽을 파티션 (예: 0)
# 시작 오프셋은 0부터 시작해서 모든 메시지를 읽고, commit_threshold에 도달하면 종료하도록 할 수 있음
START_OFFSET = 0                               
AUTO_OFFSET_RESET = 'earliest'                  # 오프셋이 없을 경우 설정 (예: 'earliest')

# 수동 커밋할 오프셋(예: 오프셋 2까지 커밋)
commit_threshold = 2

#################################
# Kafka Consumer 생성 및 설정
#################################
consumer = KafkaConsumer(
    bootstrap_servers=BOOTSTRAP_SERVERS_LIST,
    auto_offset_reset=AUTO_OFFSET_RESET,
    enable_auto_commit=False,
    group_id=CONSUMER_GROUP
)

# 특정 토픽의 원하는 파티션만 할당
topic_partition = TopicPartition(TOPIC, PARTITION)
consumer.assign([topic_partition])
# 지정한 오프셋부터 읽도록 설정
consumer.seek(topic_partition, START_OFFSET)
print(f"Partition {PARTITION}의 시작 오프셋을 {START_OFFSET}로 설정")

#################################
# 메인 함수
#################################
def main():
    for message in consumer:
        # 메시지와 오프셋을 출력
        print(f"받은 메시지: {message.value.decode('utf-8')}, 오프셋: {message.offset}")
        
        # 1초 대기
        time.sleep(1)
        
        # 만약 메시지의 오프셋이 commit_threshold와 같다면 커밋 후 종료
        if message.offset == commit_threshold:
            consumer.commit()  # commit 시 실제 커밋 값은 message.offset+1이 됨
            print(f"오프셋 {message.offset}까지 커밋 완료")
            break

if __name__ == "__main__":
    main()
