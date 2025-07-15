# Hadoop Eco의 Hive로 aggregated 테이블 생성 및 데이터 적재 과정

Hadoop Eco의 Hive를 활용하여 이미 만들어진 Nginx 로그 데이터 테이블과 MySQL 데이터 테이블을 사용하여 Aggregated 테이블을 생성합니다.

---
## 1. Hadoop-Eco 마스터 노드 정보 조회

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `HadoopMST-core-hadoop-1` 인스턴스의 `private ip` 복사 및 클립보드 등에 붙여넣기

## 2. Hive에서 aggregated_logs 테이블 생성

1. 사용하던 `HadoopMST-core-hadoop-1`에서 hive에 접속

    #### **lab5-2-1**

    ```bash
    hive
    ```  

2. aggregated_logs 테이블 생성

    - LOCATION에 `{HadoopMST-core-hadoop-1 private ip주소}` 입력

    #### **lab5-2-2**

    ```bash
    CREATE TABLE IF NOT EXISTS aggregated_logs (
      session_id         STRING,
      user_id            STRING,
      product_id         STRING,
      event_type         STRING,
      event_count        INT,
      total_request_time DOUBLE,
      last_active_time   STRING,
      success_count      INT
    )
    STORED AS PARQUET
    LOCATION 'hdfs://{HadoopMST-core-hadoop-1 private ip주소}:8020/apps/hive/warehouse/aggregated_logs/';
    ```

3. 파티션 설정 및 jar 등록

    - Hive 메타스토어에 저장된 테이블 정보를 Hadoop Eco와 공유해주는 HCatalog 코어 라이브러리 추가 

    #### **lab5-2-3**

    ```bash
    ADD JAR /opt/apache-hive-3.1.3-bin/lib/hive-hcatalog-core-3.1.3.jar;
    ```

4. aggregated_logs 테이블에 데이터 적재

    #### **lab5-2-4**

    ```bash
    INSERT OVERWRITE TABLE aggregated_logs
    SELECT
      COALESCE(NULLIF(t.session_id, ''), 'anonymous') AS session_id,
      COALESCE(NULLIF(t.user_id,    ''), 'guest')     AS user_id,
      COALESCE(NULLIF(t.product_id, ''), 'NULL')      AS product_id,
    
      CASE WHEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END) > 0
           THEN 'order'
           ELSE 'pageview'
      END                                             AS event_type,
    
      CASE WHEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END) > 0
           THEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END)
           ELSE SUM(CASE WHEN t.src='pageview' THEN 1 ELSE 0 END)
      END                                             AS event_count,
    
      ROUND(SUM(t.request_time), 3)                  AS total_request_time,
    
      DATE_FORMAT(MAX(t.log_ts), 'yyyy-MM-dd HH:mm:ss') AS last_active_time,
    
      SUM(
        CASE WHEN t.status = 200 THEN 1 ELSE 0 END
      )                                             AS success_count
    
    FROM (
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
    GROUP BY t.session_id, t.user_id, t.product_id;
    ```

5. aggregated_logs 테이블에 적재된 데이터 결과 확인

    #### **lab5-2-5**

    ```bash
    select * from aggregated_logs limit 10;
    ```

    - 아래와 같은 형식의 내용 확인
   
    ![aggregated_logs 확인](https://github.com/user-attachments/assets/971fac03-b72e-47e2-b8e4-6e9bde95205b)

6. Hadoop Eco의 HDFS 경로 확인

    - **Note**: HDFS는 원시 형태의 다양한 데이터를 저장해두는 분산 스토리지 계층이자 데이터 레이크이다.
    - `HDFS 경로` 복사 후 클립보드 등에 붙여넣기

    #### **lab5-2-6**

    ```bash
    SET hive.metastore.warehouse.dir;
    ```

    - 아래와 같은 형식의 내용 확인

    ![hive에서 hdfs 경로 확인](https://github.com/user-attachments/assets/5f3fd033-491c-461e-a283-4d8ee892e1c8)

7. `ctrl` + `c`로 종료

8. Hadoop Eco의 HDFS에 생성된 aggregated_logs 테이블 확인

    - `HDFS 경로`로 `{hive.metastore.warehouse.dir}` 수정

    #### **lab5-2-8**

    ```bash
    hdfs dfs -ls {hive.metastore.warehouse.dir}
    ```

    - 아래와 같은 형식의 내용 확인

    <img width="1500" height="73" alt="Image" src="https://github.com/user-attachments/assets/8770eb63-5550-497a-a596-bf26b25edd8e" />



