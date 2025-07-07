# Core Hadoop, PySpark 실습
Hadoop 클러스터 환경에서 실시간 스트리밍 데이터와 배치 데이터를 통합 처리하여 사용자 행동 예측 데이터셋을 구축하고 PySpark를 활용하여 데이터를 검증하는 실습입니다.

## 1. Hive 테이블 생성

1. Beyond Computer Service → Virtual Machine → 인스턴스
2. `HadoopMST-core-hadoop-1` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭
3. `HadoopMST-core-hadoop-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력
    
    **lab7-1-3-1**
    
    ```
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    **lab7-1-3-2**
    
    ```
    chmod 400 keypair.pem
    ```
    
    **lab7-1-3-3**
    
    ```
    ssh -i keypair.pem ubuntu@{s3-sink-connector public ip주소}
    ```
    
    **lab7-1-3-1**
    
    ```
    yes
    ```
    

1. Hive 접속
    
    **lab7-1-4**
    
    ```java
    hive
    ```
    
2. Hive 테이블 생성 및 스키마 정의
    
    **lab7-1-5**
    
    ```java
    CREATE EXTERNAL TABLE IF NOT EXISTS user_behavior (
      session_id          STRING,
      user_id             STRING,
      gender              STRING,
      age                 INT,
      current_state       STRING,
      search_count        INT,
      cart_item_count     INT,
      page_depth          INT,
      last_action_elapsed DOUBLE,
      next_state          STRING
    )
    STORED AS PARQUET
    LOCATION 's3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction/';
    
    ```
    

1. 생성된 테이블 확인
    
    **lab7-1-6**
    
    ```java
    show tables
    ```
    

1. Hive 세션 종료
    
    **lab7-1-7**
    
    ```java
    exit()
    ```
    

## **2. Spark 및 Avro 환경 설정**

1. Spark 설정 파일 업데이트
    
    **lab7-2-1-1**
    
    ```java
    sudo vi /opt/spark/conf/spark-defaults.conf
    ```
    
    **lab7-2-1-2**
    
    ```java
    # 기존 설정들
    gpark.master                             yarn
    spark.serializer                         org.apache.spark.serializer.KryoSerializer
    spark.driver.memory                      2g
    spark.driver.extraJavaOptions            -Dspark.log.dir=/var/log/spark -Dspark.log.file=spark.log
    spark.executor.extraLibraryPath          /opt/hadoop/lib/native
    spark.eventLog.enabled                   true
    spark.eventLog.dir                       hdfs:///var/log/spark/apps
    spark.sql.hive.metastore.jars            /opt/hive/lib/*
    spark.sql.hive.metastore.version         3.1.3
    spark.sql.hive.metastore.sharedPrefixes  com.mysql.jdbc
    
    # 추가해야 할 설정들
    spark.jars                               /opt/hive/lib/hive-hcatalog-core-3.1.3.jar
    spark.driver.extraClassPath              /opt/hive/lib/hive-hcatalog-core-3.1.3.jar
    spark.executor.extraClassPath            /opt/hive/lib/hive-hcatalog-core-3.1.3.jar
    spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive true
    
    ```
    

1. Hive 설정을 Spark로 복사
    
    **lab7-2-2**
    
    ```java
    cp /opt/hive/conf/hive-site.xml /opt/spark-3.5.2-bin-hadoop3/conf/
    ```
    

1. Avro 직렬화를 위한 의존성 설치
    
    **lab7-2-3**
    
    ```java
    # jars 디렉터리 생성
    mkdir -p /home/ubuntu/jars
    
    # Confluent Kafka Avro Serializer JAR 다운로드
    wget https://packages.confluent.io/maven/io/confluent/kafka-avro-serializer/7.2.1/kafka-avro-serializer-7.2.1.jar \
         -O /home/ubuntu/jars/kafka-avro-serializer-7.2.1.jar
    ```
    

1. nginx_log.avsc 스키마 파일 구성
    
    **lab7-2-4**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/nginx_log.avsc
    ```
    

## 3. PySpark를 활용한 일괄 정제 (수정)

1. 배치 정제 파일 다운로드
    
    **lab7-3-1**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/historical_data_refiner.py
    ```
    

2. 배치 정제 실행
    
    **lab7-3-2**
    
    ```java
    spark-submit \
      --master yarn \
      --deploy-mode client \
      --packages io.delta:delta-spark_2.12:3.1.0 \
      --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
      --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
      historical_data_refiner.py
    ```
    

3. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
4. `data-catalog-bucket` 클릭
5. 배치 정제 결과가 저장된 디렉터리로 이동 후 버킷 내 적재된배치 정제 결과 확인 
    - **Note**: `data-catalog-bucket/data-catalog-dir/user_behavior_batch/dt={실습 진행날짜}/`디렉터리로 이동
   ![결과 이미지](https://github.com/user-attachments/assets/705f5b68-f7d0-4dd0-a368-73dfd152bcf7)

6. 배치 정제 결과 데이터 검증을 위한 PySpark 셸 실행
    
    **lab7-3-6**
    
    ```java
    pyspark
    ```
    

7. 현재 PySpark 셸 세션에서 S3 접근을 위한 Hadoop 설정값 구성
    
    **lab7-3-7**
    
    ```java
    hconf = spark.sparkContext._jsc.hadoopConfiguration()
    hconf.set("fs.s3a.endpoint", "https://objectstorage.kr-central-2.kakaocloud.com")
    hconf.set("fs.s3a.path.style.access", "true")
    hconf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    ```
    
8. 데이터 경로 정의
    - **Note**: `{실습 진행 날짜}`을 개인 환경에 맞게 수정 필요 (ex. dt=2025-06-30)
    
    **lab7-3-8**
    
    ```java
    output_data_path = "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_batch/{실습 진행 날짜}/"
    ```
    

9. Parquet 파일을 DataFrame으로 로드
    
    **lab7-3-9**
    
    ```java
    df_enriched = spark.read.parquet(output_data_path)
    ```
    

10. 스키마 구조 출력
    
    **lab7-3-10**
    
    ```java
    df_enriched.printSchema()
    ```
    ![image](https://github.com/user-attachments/assets/a2c93be1-cc4f-48c8-9f93-c9a2b578c01c)

    

11. 상위 100개 레코드 출력
    
    **lab7-3-11**
    
    ```java
    df_enriched.show(100, truncate=False)
    ```
    ![image](https://github.com/user-attachments/assets/fd0460e5-8ef7-44cf-afd3-10b418b4ad0d)

    
12. Pyspark 셸 종료
    
    **lab7-3-12**
    
    ```java
    exit();
    ```
    

## 4. Pyspark를 활용한 실시간 정제

1. 실시간 정제 로직 파일 생성
    
    **lab7-4-1**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/streaming_data_processor.py
    ```
    

2. `BOOTSTRAP_SERVERS` 값을 실제 주소로 변경
    - **Note**: `{실제 Kafka 클러스터 부트스트랩 서버값}`을 개인 환경에 맞게 수정 필요
    
    **lab7-4-2**
    
    ```java
    sed -i 's/BOOTSTRAP_SERVERS/{실제 Kafka 클러스터 부트스트랩 서버값}/g' streaming_data_processor.py
    ```
    

3. 실시간 정제 작업 실행
    
    **lab7-4-3**
    
    ```java
    nohup spark-submit \
      --master yarn \
      --deploy-mode client \
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,org.apache.spark:spark-avro_2.12:3.5.2,io.delta:delta-spark_2.12:3.1.0 \
      streaming_data_processor.py > streaming_data_processor.log 2>&1 &
    ```
    

4. 정제 프로세스 모니터링
    
    **lab7-4-4**
    
    ```java
    tail -f streaming_data_processor.log 
    ```
    

5. 모니터링 종료
    - **Note**: 맥북은 “command” + “c”
    
    **lab7-4-5**
    
    ```java
    "ctrl" + "c"
    ```
    

6. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
7. `data-catalog-bucket` 클릭
8. 배치 정제 결과가 저장된 디렉터리로 이동 후 버킷 내 적재된배치 정제 결과 확인 
    - **Note**: `data-catalog-bucket/data-catalog-dir/user_behavior_prediction/dt={실습 진행날짜}/`디렉터리로 이동
    ![실시간 결과 이미지](https://github.com/user-attachments/assets/5d205c50-8765-4e64-8fd7-8722f7a3d352)
    

9. 배치 정제 결과 데이터 검증을 위한 PySpark 셸 실행
    
    **lab7-4-9**
    
    ```java
    pyspark
    ```
    

10. 파일 경로 설정

    **lab7-4-10**
    
    ```java
    directory_path= "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction/"
    ```
    

11. Parquet 파일 로드
    
    **lab7-4-11**
    
    ```java
    df_combined = spark.read.parquet(directory_path)
    ```
    

12. 스키마 구조 검증
    
    **lab7-4-12**
    
    ```java
    df_combined.printSchema()
    ```
    

13. 상위 100개 데이터 샘플 확인
    
    **lab7-4-13**
    
    ```java
    df_combined.show(100, truncate=False)
    ```
    ![image](https://github.com/user-attachments/assets/1061d169-e1b6-47d7-a837-669b3f03e7dd)

    

14. 세션 ID별 데이터 분포 확인
    
    **lab7-4-14**
    
    ```java
    df_combined.groupBy("session_id").count().show(truncate=False)
    ```
    ![image](https://github.com/user-attachments/assets/d108e260-3801-4711-8236-ba5ff1497b58)

    
15. Spark 셸 종료
    
    **lab7-4-15**
    
    ```java
    exit()
    ```
