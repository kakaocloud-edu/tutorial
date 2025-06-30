# hadoop eco의 hive로 user cart metrics 테이블 생성 및 spark로 mysql에 데이터 마트 구축

hadoop eco의 hive를 활용하여 이미 만들어진 aggregated logs 테이블과 mysql 데이터 테이블을 사용하여 user cart metrics 테이블을 생성합니다. 만들어진 user cart metrics를 mysql에 적재하여 데이터 마트를 구축합니다.

---
## 1. hadoop-eco 마스터 노드에 접속

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `HadoopMST-core-hadoop-1` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭

    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭

3. `HadoopMST-core-hadoop-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭

    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력

    #### **lab5-1-3-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab5-1-3-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab5-1-3-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{HadoopMST-core-hadoop-1 public ip주소}
    ```
    
    #### **lab5-1-3-4**
    
    ```bash
    yes
    ```

## 2. hive에서 user cart metrics 테이블 생성

1. hive에 접속

    #### **lab6-2-1**

    ```bash
    hive
    ```

2. user cart metrics 테이블 생성

    #### **lab6-2-2**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS user_cart_metrics_temp (
      user_id            STRING,
      order_count        BIGINT,
      pageview_count     BIGINT,
      total_request_time DOUBLE,
      avg_request_time   DOUBLE,
      last_active_time   STRING
    )
    STORED AS PARQUET
    LOCATION 's3a://data-catalog-bucket/hive-tables/user_cart_metrics_temp/';
    ```

3. user cart metrics 테이블에 데이터 적재

    #### **lab6-2-3**

    ```bash
    INSERT OVERWRITE TABLE user_cart_metrics_temp
    SELECT
      COALESCE(NULLIF(user_id, ''), 'NULL') AS user_id,
      SUM(CASE WHEN event_type = 'order'    THEN event_count ELSE 0 END) AS order_count,
      SUM(CASE WHEN event_type = 'pageview' THEN event_count ELSE 0 END) AS pageview_count,
      ROUND(SUM(total_request_time), 3)                                    AS total_request_time,
      CASE
        WHEN SUM(event_count) = 0
          THEN 0.0
        ELSE
          ROUND(
            SUM(total_request_time)
            / SUM(event_count)
          , 3)
      END                                                                  AS avg_request_time,
      COALESCE(NULLIF(MAX(last_active_time), ''), 'NULL')                 AS last_active_time
    FROM aggregated_logs
    WHERE
      user_id <> 'guest'
      AND unix_timestamp(last_active_time, 'yyyy-MM-dd HH:mm:ss')
          BETWEEN unix_timestamp('2025-06-29 06:00:00', 'yyyy-MM-dd HH:mm:ss')
              AND unix_timestamp('2025-06-29 07:00:00', 'yyyy-MM-dd HH:mm:ss')
    GROUP BY
      COALESCE(NULLIF(user_id, ''), 'NULL')
    ;
    ```

4. user cart metrics 테이블에 적재된 데이터 확인

    #### **lab6-2-4**

    ```bash
    select * from user_cart_metrics_temp limit 10;
    ```

    - 아래와 비슷한 결과 확인

    ```bash
    user_06b63f     1       3       0.048   0.012   2025-06-29 06:22:18
    user_081fa7     0       5       0.085   0.017   2025-06-29 06:49:09
    user_0c0d95     0       1       0.014   0.014   2025-06-29 06:13:16
    ```

5. `ctrl` + `c`로 hive 종료


## 3. spark에서 mysql로 데이터 마트 구축

1. spark 설정파일을 hive와 같게 설정

    #### **lab6-3-1**

    ```bash
    cp /opt/apache-hive-3.1.3-bin/conf/hive-site.xml /opt/spark-3.5.2-bin-hadoop3/conf/
    ```

2. pyspark 실행

    #### **lab6-3-2**

    ```bash
    pyspark \
      --packages org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.12.375 \
      --jars /opt/hive/lib/mysql-connector-j-8.0.33.jar,/opt/hive/lib/hive-hcatalog-core-3.1.3.jar \
      --conf spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive=true
    ```

3. spark에서 session 시작

    #### **lab6-3-3**

    ```bash
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder \
        .appName("UserMetricsToMySQL") \
        .enableHiveSupport() \
        .getOrCreate()
    ```

4. hive의 메타스토어에 있는 user cart metrics temp 테이블 spark로 가져온 후 확인

    #### **lab6-3-4-1**

    ```bash
    df = spark.table("default.user_cart_metrics_temp")
    ```

    #### **lab6-3-4-2**

    ```bash
    df.show(5)
    ```

    - 아래와 비슷한 결과 확인

    ```bash
    +-----------+-----------+--------------+------------------+----------------+-------------------+
    |    user_id|order_count|pageview_count|total_request_time|avg_request_time|   last_active_time|
    +-----------+-----------+--------------+------------------+----------------+-------------------+
    |user_0553b5|          2|             2|             0.133|           0.033|2025-06-29 06:23:58|
    |user_167234|          0|             6|             0.131|           0.022|2025-06-29 06:28:55|
    |user_169ee4|          2|             4|             0.076|           0.013|2025-06-29 06:28:54|
    |user_190000|          0|             3|             0.038|           0.013|2025-06-29 06:16:23|
    |user_3623d8|          0|             1|             0.037|           0.037|2025-06-29 06:27:30|
    +-----------+-----------+--------------+------------------+----------------+-------------------+
    ```

5. jdbc로 mysql과 연결 후 적재

    - mysql 엔드포인트 입력

    #### **lab6-3-5-1**

    ```bash
    jdbc_url = "jdbc:mysql://{mysql 엔드포인트}:3306/shopdb?useSSL=false"
    
    connection_properties = {
        "user": "admin",
        "password": "admin1234",
        "driver": "com.mysql.cj.jdbc.Driver"
    };
    ```

    #### **lab6-3-5-2**

    ```bash
    df.write \
        .mode("overwrite") \
        .jdbc(url=jdbc_url, table="user_cart_metrics", properties=connection_properties)
    ```


## 4. 데이터 마트를 이용한 data query 진행











