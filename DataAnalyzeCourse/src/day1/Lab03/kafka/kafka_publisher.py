#!/usr/bin/env python3

from kafka import KafkaProducer
import time
import os

bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

######################
# partiton 번호 지정
######################
partition_number = 0


for i in range(5):
    message = f"메시지 {i+1}"
    # partition 번호 변수 사용
    producer.send('python-topic', value=message.encode('utf-8'), partition=partition_number)
    print(f"전송: {message}")
    time.sleep(1)

producer.flush()
producer.close()
