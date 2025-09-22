# Core Hadoop, PySpark 실습
Hadoop 클러스터 환경에서 실시간 스트리밍 데이터와 배치 데이터를 통합 처리하여 사용자 행동 예측 데이터셋을 구축하고 PySpark를 활용하여 데이터를 검증하는 실습입니다.

## **1. Spark 및 Avro 환경 설정**
1. 사용하던 `HadoopMST-core-hadoop-1`에서 Avro 직렬화를 위한 의존성 설치
    
    #### **lab7-1-1-1**
    
    ```java
    mkdir -p /home/ubuntu/jars
    ```
    
    #### **lab7-1-1-2**
   
    ```java
    wget https://packages.confluent.io/maven/io/confluent/kafka-avro-serializer/7.2.1/kafka-avro-serializer-7.2.1.jar \
         -O /home/ubuntu/jars/kafka-avro-serializer-7.2.1.jar
    ```
    

## 2. PySpark를 활용한 일괄 정제

1. 배치 정제 파일 다운로드
   - **Note**: 스크립트에 대한 자세한 내용은 아래 파일 참고
     - [historical_data_refiner.py](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day2/Lab07/historical_data_refiner.py)
                  
    #### **lab7-2-1**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/historical_data_refiner.py
    ```

2. `SCHEMA_REGISTRY_SERVER` 값을 실제 주소로 변경
    
    #### **lab7-2-2**

    ```bash
    sed -i "s/SCHEMA_REGISTRY_SERVER/${SCHEMA_REGISTRY_SERVER}/g" historical_data_refiner.py
    ```

    
3. 배치 정제 실행
    
    #### **lab7-2-3**
    
    ```java
    nohup spark-submit \
      --master yarn \
      --deploy-mode client \
      --packages io.delta:delta-spark_2.12:3.1.0 \
      historical_data_refiner.py > historical_data_refiner.log 2>&1 &
    ```
    
4. 배치 정제 프로세스 모니터링
    
    #### **lab7-3-4**
    
    ```java
    tail -f historical_data_refiner.log 
    ```
    
    <img width="1714" height="920" alt="image" src="https://github.com/user-attachments/assets/6a6473d9-7984-4f5f-81be-12572087f3d2" />

    

5. `ctrl` + `c`로 모니터링 종료

    - **Note**: 맥북은 “command” + “c”    

6. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
7. `data-catalog-bucket` 클릭
8. 배치 정제 결과가 저장된 디렉터리로 이동 후 버킷 내 적재된 배치 정제 결과 확인 
    - **Note**: `data-catalog-bucket/data-catalog-dir/user_behavior_batch`디렉터리로 이동
   <img width="1695" height="932" alt="image" src="https://github.com/user-attachments/assets/9652d39e-5546-4c63-9f36-c604b3b37ffc" />

9. 배치 정제 결과 데이터 검증을 위한 PySpark 셸 실행
    
    #### **lab7-2-9**
    
    ```java
    pyspark
    ```
    

10. 현재 PySpark 셸 세션에서 S3 접근을 위한 Hadoop 설정값 구성
    
    #### **lab7-2-10**
    
    ```java
    hconf = spark.sparkContext._jsc.hadoopConfiguration()
    hconf.set("fs.s3a.endpoint", "https://objectstorage.kr-central-2.kakaocloud.com")
    hconf.set("fs.s3a.path.style.access", "true")
    hconf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    ```
    
11. 데이터 경로 정의
    
    #### **lab7-2-11**
    
    ```java
    output_data_path = "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction_batch/"
    ```
    

12. Parquet 파일을 DataFrame으로 로드
    
    #### **lab7-2-12**
    
    ```java
    df_enriched = spark.read.parquet(output_data_path)
    ```
    

13. 스키마 구조 출력
    
    #### **lab7-2-13**
    
    ```java
    df_enriched.printSchema()
    ```
    <img width="491" height="377" alt="스키마구조" src="https://github.com/user-attachments/assets/c3da899f-b6a6-49e6-85e7-3c548a123e8e" />


    

14. 상위 100개 레코드 출력
    
    #### **lab7-2-14**
    
    ```java
    (df_enriched
     .orderBy("session_id", "page_depth")
     .show(100, truncate=False))
    ```

    <img width="2467" height="915" alt="image" src="https://github.com/user-attachments/assets/aabb6e5b-f682-4f46-966c-e6ea0a3103bb" />

    
15. Pyspark 셸 종료
    
    #### **lab7-2-15**
    
    ```java
    exit();
    ```
    

## 3. Pyspark를 활용한 실시간 정제

1. 실시간 정제 로직 파일 생성
    - **Note**: 스크립트에 대한 자세한 내용은 아래 파일 참고
        - [streaming_data_processor.py](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day2/Lab07/streaming_data_processor.py)
    
    
    #### **lab7-3-1**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/streaming_data_processor.py
    ```
    

2. `BOOTSTRAP_SERVER`, `data-stream-vm의 Public IP`값을 실제 주소로 변경
    
    #### **lab7-3-2-1**
    
    ```bash
    sed -i "s/KAFKA_BOOTSTRAP_SERVER/${KAFKA_BOOTSTRAP_SERVERS}/g" streaming_data_processor.py
    ```

    #### **lab7-3-2-2**

    ```bash
    sed -i "s/SCHEMA_REGISTRY_SERVER/${SCHEMA_REGISTRY_SERVER}/g" streaming_data_processor.py
    ```
    

3. 실시간 정제 작업 실행
    
    #### **lab7-3-3**
    
    ```java
    nohup spark-submit \
      --master yarn \
      --deploy-mode client \
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,org.apache.spark:spark-avro_2.12:3.5.2,io.delta:delta-spark_2.12:3.1.0 \
      streaming_data_processor.py > streaming.log 2>&1 &
    ```

4. 프로세스 과정 확인

    #### **lab7-3-4**
    
    ```java
    tail -f streaming.log
    ```

5. `ctrl` + `c`로 모니터링 종료

    - **Note**: 맥북은 “command” + “c” 

6. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
7. `data-catalog-bucket` 클릭
8. 실시간 정제 결과가 저장된 디렉터리로 이동 후 버킷 내 실시간 배치 정제 결과 확인 
    - **Note**: `data-catalog-bucket/data-catalog-dir/user_behavior_prediction_delta/`디렉터리로 이동
    ![실시간 결과 이미지](https://github.com/user-attachments/assets/5d205c50-8765-4e64-8fd7-8722f7a3d352)
    

9. 실시간 정제 결과 데이터 검증을 위한 PySpark 셸 실행
    
    #### **lab7-3-9**
    
    ```java
    pyspark \
      --packages io.delta:delta-spark_2.12:3.1.0 \
      --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
      --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog
    ```
    

10. Object Storage에 적재된 실시간 정제 파일 경로 설정

    #### **lab7-3-10**
    
    ```java
    path = "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction_delta/"
    ```
    

11. Delta 파일 로드
    
    #### **lab7-3-11**
    
    ```java
    df = spark.read.format("delta").load(path)
    ```
    

12. 스키마 구조 검증
    
    #### **lab7-3-12**
    
    ```java
    df.printSchema()
    ```

    <img width="494" height="373" alt="image" src="https://github.com/user-attachments/assets/07a07f23-b154-4681-832f-e67646e5c8a3" />


    
13. 상위 100개 데이터 샘플 확인
    
    #### **lab7-3-13**
    
    ```java
    (df
     .orderBy("session_id", "page_depth", "event_id")
     .show(100, truncate=False)
    )
    ```
    <img width="2179" height="752" alt="image" src="https://github.com/user-attachments/assets/beabee63-4f5d-479a-bbe2-d24bfa274e8f" />

    

14. 세션 ID별 데이터 분포 확인
    
    #### **lab7-3-14**
    
    ```java
    df.groupBy("session_id").count().show(truncate=False)
    ```
    
15. Spark 셸 종료
    
    #### **lab7-3-15**
    
    ```java
    exit()
    ```
