# Core Hadoop, PySpark 실습
Hadoop 클러스터 환경에서 실시간 스트리밍 데이터와 배치 데이터를 통합 처리하여 사용자 행동 예측 데이터셋을 구축하고 PySpark를 활용하여 데이터를 검증하는 실습입니다.

## **1. Spark 및 Avro 환경 설정**
1. 사용하던 `HadoopMST-core-hadoop-1`에서 Avro 직렬화를 위한 의존성 설치
    
    **lab7-1-1-1**
    
    ```java
    mkdir -p /home/ubuntu/jars
    ```
    
    **lab7-1-1-2**
    ```java
    wget https://packages.confluent.io/maven/io/confluent/kafka-avro-serializer/7.2.1/kafka-avro-serializer-7.2.1.jar \
         -O /home/ubuntu/jars/kafka-avro-serializer-7.2.1.jar
    ```
    

## 2. PySpark를 활용한 일괄 정제

1. 배치 정제 파일 다운로드
   - **Note**: 스크립트에 대한 자세한 내용은 아래 파일 참고
     - [historical_data_refiner.py](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day2/Lab07/historical_data_refiner.py)
                  
    **lab7-2-1**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/historical_data_refiner.py
    ```
    

2. 배치 정제 실행
    
    **lab7-2-2**
    
    ```java
    nohup spark-submit \
      --master yarn \
      --deploy-mode client \
      --packages io.delta:delta-spark_2.12:3.1.0 \
      historical_data_refiner.py > historical_data_refiner.log 2>&1 &
    ```
    
3. 배치 정제 프로세스 모니터링
    
    **lab7-3-3**
    
    ```java
    tail -f historical_data_refiner.log 
    ```
    

4. 모니터링 종료
    - **Note**: 맥북은 “command” + “c”
    
    **lab7-3-4**
    
    ```java
    "ctrl" + "c"
    ```
    

5. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
6. `data-catalog-bucket` 클릭
7. 배치 정제 결과가 저장된 디렉터리로 이동 후 버킷 내 적재된배치 정제 결과 확인 
    - **Note**: `data-catalog-bucket/data-catalog-dir/user_behavior_batch/dt={실습 진행날짜}/`디렉터리로 이동
   ![결과 이미지](https://github.com/user-attachments/assets/705f5b68-f7d0-4dd0-a368-73dfd152bcf7)

8. 배치 정제 결과 데이터 검증을 위한 PySpark 셸 실행
    
    **lab7-2-8**
    
    ```java
    pyspark
    ```
    

9. 현재 PySpark 셸 세션에서 S3 접근을 위한 Hadoop 설정값 구성
    
    **lab7-2-9**
    
    ```java
    hconf = spark.sparkContext._jsc.hadoopConfiguration()
    hconf.set("fs.s3a.endpoint", "https://objectstorage.kr-central-2.kakaocloud.com")
    hconf.set("fs.s3a.path.style.access", "true")
    hconf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    ```
    
10. 데이터 경로 정의
    
    **lab7-2-10**
    
    ```java
    output_data_path = "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction_batch/"
    ```
    

11. Parquet 파일을 DataFrame으로 로드
    
    **lab7-2-11**
    
    ```java
    df_enriched = spark.read.parquet(output_data_path)
    ```
    

12. 스키마 구조 출력
    
    **lab7-2-12**
    
    ```java
    df_enriched.printSchema()
    ```
    <img width="470" height="314" alt="image" src="https://github.com/user-attachments/assets/c6386e75-96a5-45d3-9878-19087753bca2" />


    

13. 상위 100개 레코드 출력
    
    **lab7-2-13**
    
    ```java
    (df_enriched
     .orderBy("session_id", "page_depth")
     .show(100, truncate=False))
    ```
    ![image](https://github.com/user-attachments/assets/b664d8b4-5da9-4354-8917-d555c18ab5bd)

    
14. Pyspark 셸 종료
    
    **lab7-2-14**
    
    ```java
    exit();
    ```
    

## 3. Pyspark를 활용한 실시간 정제

1. 실시간 정제 로직 파일 생성
    - **Note**: 스크립트에 대한 자세한 내용은 아래 파일 참고
        - [streaming_data_processor.py](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day2/Lab07/streaming_data_processor.py)
    
    
    **lab7-3-1**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/streaming_data_processor.py
    ```
    

2. `BOOTSTRAP_SERVERS`, `API_VM_IP`값을 실제 주소로 변경
    - **Note**: `{실제 Kafka 클러스터 부트스트랩 서버값}`을 개인 환경에 맞게 수정 필요
    - **Note**: `{data-stream-vm의 Public IP}}`을 개인 환경에 맞게 수정 필요
    
    **lab7-3-2**
    
    ```bash
    sed -i 's/KAFKA_BOOTSTRAP_SERVERS/{실제 Kafka 클러스터 부트스트랩 서버값}/g' streaming_data_processor.py
    ```

    **lab7-3-2-2**

    ```bash
    sed -i "s/SCHEMA_REGISTRY_SERVER/{data-stream-vm의 Public IP}/g" streaming_data_processor.py
    ```
    

4. 실시간 정제 작업 실행
    
    **lab7-3-3**
    
    ```java
    nohup spark-submit \
      --master yarn \
      --deploy-mode client \
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,org.apache.spark:spark-avro_2.12:3.5.2,io.delta:delta-spark_2.12:3.1.0 \
      streaming_data_processor.py > streaming_data_processor.log 2>&1 &
    ```
    

5. 정제 프로세스 모니터링
    
    **lab7-3-4**
    
    ```java
    tail -f streaming_data_processor.log 
    ```
    

6. 모니터링 종료
    - **Note**: 맥북은 “command” + “c”
    
    **lab7-3-5**
    
    ```java
    "ctrl" + "c"
    ```
    

7. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
8. `data-catalog-bucket` 클릭
9. 배치 정제 결과가 저장된 디렉터리로 이동 후 버킷 내 적재된배치 정제 결과 확인 
    - **Note**: `data-catalog-bucket/data-catalog-dir/user_behavior_prediction/dt={실습 진행날짜}/`디렉터리로 이동
    ![실시간 결과 이미지](https://github.com/user-attachments/assets/5d205c50-8765-4e64-8fd7-8722f7a3d352)
    

10. 배치 정제 결과 데이터 검증을 위한 PySpark 셸 실행
    
    **lab7-3-9**
    
    ```java
    pyspark
    ```
    

11. 파일 경로 설정

    **lab7-3-10**
    
    ```java
    directory_path= "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction/"
    ```
    

12. Parquet 파일 로드
    
    **lab7-3-11**
    
    ```java
    df_combined = spark.read.parquet(directory_path)
    ```
    

13. 스키마 구조 검증
    
    **lab7-3-12**
    
    ```java
    df_combined.printSchema()
    ```

    <img width="470" height="314" alt="image" src="https://github.com/user-attachments/assets/50ba5362-e45b-4cda-bb69-243c90ec447d" />



    

14. 상위 100개 데이터 샘플 확인
    
    **lab7-3-13**
    
    ```java
    (df_combined
     .orderBy("session_id", "page_depth")
     .show(100, truncate=False))
    ```
    ![image](https://github.com/user-attachments/assets/84c3ca82-51f0-47fb-aa6e-aa325a159eb0)

    

15. 세션 ID별 데이터 분포 확인
    
    **lab7-3-14**
    
    ```java
    df_combined.groupBy("session_id").count().show(truncate=False)
    ```
    
16. Spark 셸 종료
    
    **lab7-3-15**
    
    ```java
    exit()
    ```
