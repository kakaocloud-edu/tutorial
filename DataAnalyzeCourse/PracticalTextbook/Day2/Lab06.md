# Spark-MySQL 데이터 마트 구축

Hadoop Eco의 Spark를 활용하여 이미 만들어진 aggregated_logs 테이블과 MySQL 데이터 테이블을 사용하여 user cart metrics temp 테이블을 생성합니다. 만들어진 user cart metrics temp 테이블을 MySQL에 적재하여 데이터 마트를 구축합니다.

---
## 1. Spark를 활용한 user cart metrics temp 테이블 생성 및 MySQL 에 적재하여 데이터 마트 구축 

1. Spark 설정파일을 Hive와 같게 설정

    #### **lab6-2-1**

    ```bash
    cp /opt/apache-hive-3.1.3-bin/conf/hive-site.xml /opt/spark-3.5.2-bin-hadoop3/conf/
    ```

2. pyspark 실행

    #### **lab6-2-2**

    ```bash
    pyspark \
      --packages org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.12.375 \
      --jars /opt/hive/lib/mysql-connector-j-8.0.33.jar,/opt/hive/lib/hive-hcatalog-core-3.1.3.jar \
      --conf spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive=true
    ```

3. Spark에서 session 시작

    #### **lab6-2-3**

    ```bash
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder \
        .appName("UserMetricsToMySQL") \
        .enableHiveSupport() \
        .getOrCreate()
    ```

4. Hive의 메타스토어에 있는 user_cart_metrics_temp 테이블을 Spark로 가져온 후 확인

    #### **lab6-2-4-1**

    ```bash
    df = spark.table("default.user_cart_metrics_temp")
    ```

    #### **lab6-2-4-2**

    ```bash
    df.show(5)
    ```

    - 아래와 같은 형식의 내용 확인

![df show](https://github.com/user-attachments/assets/c53a7a9f-6922-4a98-96d6-a760381c5e01)

5. jdbc로 MySQL과 연결 후 적재

    - mysql 엔드포인트 입력

    #### **lab6-2-5-1**

    ```bash
    jdbc_url = "jdbc:mysql://{mysql 엔드포인트}:3306/shopdb?useSSL=false"
    
    connection_properties = {
        "user": "admin",
        "password": "admin1234",
        "driver": "com.mysql.cj.jdbc.Driver"
    };
    ```

    #### **lab6-2-5-2**

    ```bash
    df.write \
        .mode("overwrite") \
        .jdbc(url=jdbc_url, table="user_cart_metrics", properties=connection_properties)
    ```

6. `ctrl` + `d`로 종료

## 3. 데이터 마트를 이용한 Data Query 진행

1. 카카오 클라우드 콘솔 > Analytics > Data Query
2. 쿼리 편집기 탭 클릭
3. user cart metrics 테이블 10개 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `Query1` 탭 아래 쿼리문 입력

    #### **lab6-3-3**

    ```bash
    SELECT * FROM data_origin.shopdb.user_cart_metrics LIMIT 10
    ```
    
![쿼리1](https://github.com/user-attachments/assets/4c7ef33f-fdc5-4d58-9fe6-3ed2beb34836)

4. Top 10 사용자별 주문 횟수 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query2` 탭 아래 쿼리문 입력

    #### **lab6-3-4**

    ```bash
    SELECT
      user_id,
      order_count,
      pageview_count,
      total_request_time,
      avg_request_time,
      last_active_time
    FROM shopdb.user_cart_metrics
    ORDER BY order_count DESC
    LIMIT 10;
    ```
    
![쿼리2](https://github.com/user-attachments/assets/6e9e3a73-810d-4a14-bd77-526539996f23)

5. Top 10 사용자별 페이지뷰 횟수 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query3` 탭 아래 쿼리문 입력

    #### **lab6-3-5**

    ```bash
    SELECT
      user_id,
      pageview_count,
      order_count,
      total_request_time,
      avg_request_time,
      last_active_time
    FROM shopdb.user_cart_metrics
    ORDER BY pageview_count DESC
    LIMIT 10;
    ```
    
![쿼리3](https://github.com/user-attachments/assets/11a4d8a7-5ba0-4b15-b41c-fb5bc98e5ae8)

6. 사용자별 평균 요청 시간 상위 10명 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query4` 탭 아래 쿼리문 입력

    #### **lab6-3-6**

    ```bash
    SELECT
      user_id,
      avg_request_time,
      total_request_time,
      order_count + pageview_count AS total_events,
      last_active_time
    FROM shopdb.user_cart_metrics
    WHERE total_request_time > 0 
    ORDER BY avg_request_time DESC
    LIMIT 10;
    ```
    
![쿼리4](https://github.com/user-attachments/assets/6121261c-486f-45ee-b3dc-8c19489c00b2)

7. 특정 기간에 마지막 활동이 있었던 사용자 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query5` 탭 아래 쿼리문 입력
    - `WHERE last_active_time LIKE 'YYYY-MM-DD%'` 에서 `'YYYY-MM-DD%'`부분 실습 날짜로 변경

    #### **lab6-3-7**

    ```bash
    SELECT
      user_id,
      order_count,
      pageview_count,
      total_request_time,
      avg_request_time,
      last_active_time
    FROM shopdb.user_cart_metrics
    WHERE last_active_time LIKE 'YYYY-MM-DD%'
    ORDER BY last_active_time DESC;
    ```

![쿼리5](https://github.com/user-attachments/assets/b593cefb-49e3-41c1-9f2b-148be17bbf39)





