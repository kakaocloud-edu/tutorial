# hadoop eco의 hive로 aggregated 테이블 생성 및 데이터 적재 과정

hadoop eco의 hive를 활용하여 이미 만들어진 nginx 로그 데이터 테이블과 mysql 데이터 테이블을 사용하여 aggregated 테이블을 생성합니다.

---
## 1. hive에서 aggregated_logs 테이블 생성

1. 사용하던 `HadoopMST-core-hadoop-1`에서 hive에 접속

    #### **lab5-1-1**

    ```bash
    hive
    ```

2. aggregated_logs 테이블 생성

    #### **lab5-1-2**

    ```bash
    CREATE TABLE IF NOT EXISTS aggregated_logs (
      session_id         STRING,
      user_id            STRING,
      product_id         STRING,
      event_type         STRING,
      event_count        INT,
      total_request_time DOUBLE,
      last_active_time   STRING,
      status             INT
    )
    STORED AS PARQUET
    LOCATION 's3a://data-catalog-bucket/hive-tables/aggregated_logs/';
    ```

3. 파티션 설정 및 JAR 등록

    #### **lab5-1-3**

    ```bash
    ADD JAR /opt/apache-hive-3.1.3-bin/lib/hive-hcatalog-core-3.1.3.jar;
    SET hive.exec.dynamic.partition = false;
    SET hive.exec.dynamic.partition.mode = strict;
    ```

4. aggregated logs 테이블에 데이터 적재

    #### **lab5-1-4**

    ```bash
    INSERT OVERWRITE TABLE aggregated_logs
    SELECT
      COALESCE(NULLIF(t.session_id, ''), 'anonymous') AS session_id,
      COALESCE(NULLIF(t.user_id,    ''), 'guest')     AS user_id,
      COALESCE(NULLIF(t.product_id, ''), 'NULL')      AS product_id,
    
      CASE WHEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END) > 0
           THEN 'order' ELSE 'pageview' END             AS event_type,
    
      CASE WHEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END) > 0
           THEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END)
           ELSE SUM(CASE WHEN t.src='pageview' THEN 1 ELSE 0 END)
      END                                             AS event_count,
    
      ROUND(SUM(t.request_time), 3)                  AS total_request_time,
    
      DATE_FORMAT(MAX(t.log_ts), 'yyyy-MM-dd HH:mm:ss') AS last_active_time,
    
      MAX(t.status)                                  AS status
    
    FROM (
      -- (A) pageview 원본 (product_id 가 있는 요청만)
      SELECT
        n.session_id,
        n.user_id,
        CAST(n.product_id AS STRING)           AS product_id,
        'pageview'                             AS src,
        CAST(n.request_time.member1 AS DOUBLE) AS request_time,
        CAST(n.`timestamp` AS TIMESTAMP)       AS log_ts,
        n.status.member1                       AS status
      FROM external_nginx_log n
      WHERE n.product_id IS NOT NULL
    
      UNION ALL
    
      -- (B) “페이지뷰가 한 번이라도 있어야” 포함되는 주문 (중복 제거)
      SELECT DISTINCT
        o.after.session_id                     AS session_id,
        o.after.user_id                        AS user_id,
        CAST(o.after.product_id AS STRING)     AS product_id,
        'order'                                AS src,
        0.0                                    AS request_time,
        CAST(from_unixtime(o.after.order_time DIV 1000000) AS TIMESTAMP) AS log_ts,
        200                                    AS status
      FROM mysql_orders o
      JOIN external_nginx_log n
        ON o.after.session_id = n.session_id
       AND CAST(o.after.product_id AS STRING) = CAST(n.product_id AS STRING)
    ) t
    WHERE
      COALESCE(NULLIF(t.session_id, ''), 'anonymous') <> 'anonymous'
      AND t.product_id       IS NOT NULL
      AND t.product_id <> ''
      AND t.product_id <> 'NULL'
    GROUP BY t.session_id, t.user_id, t.product_id
    ;
    ```

5. aggregated_logs 테이블에 적재된 데이터 결과 확인

    #### **lab5-1-5**

    ```bash
    select * from aggregated_logs limit 10;
    ```

    - 아래와 비슷한 형식의 결과 확인
   
    ```bash
    cc85d37a-b04b-4b89-99aa-c2f70b5b5e5b    guest   112     pageview        1       0.041   2025-06-29 06:19:09     200
    cc85d37a-b04b-4b89-99aa-c2f70b5b5e5b    user_2df7a5     102     pageview        1       0.012   2025-06-29 06:19:20    200
    cc85d37a-b04b-4b89-99aa-c2f70b5b5e5b    user_2df7a5     112     order   1       0.0     2025-06-29 06:19:26     200
    ```











