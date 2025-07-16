# Core Hadoop, PySpark 실습
Hadoop 클러스터 환경에서 실시간 스트리밍 데이터와 배치 데이터를 통합 처리하여 사용자 행동 예측 데이터셋을 구축하고 PySpark를 활용하여 데이터를 검증하는 실습입니다.

## **1. Spark 및 Avro 환경 설정**
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
    
    
    **lab7-1-3-2**
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    ```
    chmod 400 keypair.pem
    ```
    
    **lab7-1-3-3**
    
    ```
    ssh -i keypair.pem ubuntu@{s3-sink-connector public ip주소}
    ```
    
    **lab7-1-3-4**
    
    ```
    yes
    ```
    
4. Avro 직렬화를 위한 의존성 설치
    
    **lab7-1-4-1**
    
    ```java
    mkdir -p /home/ubuntu/jars
    ```
    
    **lab7-1-4-2**
    ```java
    wget https://packages.confluent.io/maven/io/confluent/kafka-avro-serializer/7.2.1/kafka-avro-serializer-7.2.1.jar \
         -O /home/ubuntu/jars/kafka-avro-serializer-7.2.1.jar
    ```
    

5. nginx_log.avsc 스키마 파일 구성
    
    **lab7-1-5**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/nginx_log.avsc
    ```
    

## 2. PySpark를 활용한 일괄 정제

1. 배치 정제 파일 다운로드
   - **Note**: 스크립트에 대한 자세한 내용은 아래 파일 참고
     - [historical_data_refiner.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day2/Lab07/historical_data_refiner.py)
                  
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
    - **Note**: `{실습 진행 날짜}`을 개인 환경에 맞게 수정 필요 (ex. dt=2025-06-30)
    
    **lab7-2-10**
    
    ```java
    output_data_path = "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction_batch/{실습 진행 날짜}/"
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
    ![image](https://github.com/user-attachments/assets/a2c93be1-cc4f-48c8-9f93-c9a2b578c01c)

    

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
        - [streaming_data_processor.sh](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day2/Lab07/streaming_data_processor.py)
    
    
    **lab7-3-1**
    
    ```java
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day2/Lab07/streaming_data_processor.py
    ```
    

2. `BOOTSTRAP_SERVERS`, `API_VM_IP`값을 실제 주소로 변경
    - **Note**: `{실제 Kafka 클러스터 부트스트랩 서버값}`을 개인 환경에 맞게 수정 필요
    - **Note**: `{api-server-1의 Public IP}`을 개인 환경에 맞게 수정 필요
    
    **lab7-3-2**
    
    ```bash
    sed -i 's/KAFKA_BOOTSTRAP_SERVERS/{실제 Kafka 클러스터 부트스트랩 서버값}/g' streaming_data_processor.py
    ```

    **lab7-3-2-2**

    ```bash
    sed -i "s/API_VM_IP/{api-server-1의 Public IP}/g" streaming_data_processor.py
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
    ![image](https://github.com/user-attachments/assets/301e9cf7-06eb-4855-bedd-7488c3ac3a4f)

    

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
