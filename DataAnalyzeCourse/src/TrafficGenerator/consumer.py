#!/usr/bin/env python3

import os
import time
from kafka import KafkaConsumer

# 환경 변수에서 bootstrap 서버 정보를 가져와 리스트로 변환
bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
if not bootstrap_servers:
    raise ValueError("환경 변수 'KAFKA_BOOTSTRAP_SERVERS'가 설정되어 있지 않습니다.")
bootstrap_servers_list = [server.strip() for server in bootstrap_servers.split(',')]

# enable_auto_commit=False로 설정한 컨슈머 정의 및 토픽 구독
consumer = KafkaConsumer(
    'python-topic',
    bootstrap_servers=bootstrap_servers_list,
    auto_offset_reset='earliest',   # 커밋된 오프셋이 없을 경우 처음부터 읽음
    enable_auto_commit=False,
    group_id='python-consumer-group'
)

# 파티션 할당을 위한 초기 poll 호출
consumer.poll(timeout_ms=1000)

# 할당된 각 파티션에서 시작 오프셋을 2로 설정 (중간부터 메시지 소비 시작)
for partition in consumer.assignment():
    consumer.seek(partition, 2)
    print(f"{partition} 파티션의 시작 오프셋을 2로 설정")

# 메시지 소비 및 수동 커밋
for message in consumer:
    print(f"받은 메시지: {message.value.decode('utf-8')}, 오프셋: {message.offset}")
    consumer.commit()
    print(f"오프셋 {message.offset}까지 커밋 완료")
