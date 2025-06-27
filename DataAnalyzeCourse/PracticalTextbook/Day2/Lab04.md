# hadoop eco의 hive로 테이블 생성 및 hue 쿼리

hadoop eco의 hive를 활용하여 nginx 로그 데이터와 mysql 데이터를 사용하여 external 테이블로 생성합니다. 생성된 테이블을 이용하여 hue로 쿼리를 진행하는 실습입니다.

---
## 1. 생성한 hadoop-eco 마스터 노드에 접속

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

    #### **lab4-1-3-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab4-1-3-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab4-1-3-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{HadoopMST-core-hadoop-1 public ip주소}
    ```
    
    #### **lab4-1-3-4**
    
    ```bash
    yes
    ```


## 2. hive에 external 테이블 생성

1. hive에 접속

    #### **lab4-2-1**

    ```bash
    hive
    ```

2. external nginx log 테이블 생성

    #### **lab4-2-2**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS external_nginx_log (
    `timestamp`              STRING,
    remote_addr              STRING,
    request                  STRING,
    status                   STRUCT<member0:INT, member1:INT>,
    body_bytes_sent          STRUCT<member0:BIGINT, member1:BIGINT>,
    http_referer             STRING,
    http_user_agent          STRING,
    session_id               STRING,
    user_id                  STRING,
    request_time             STRUCT<member0:DOUBLE, member1:DOUBLE>,
    upstream_response_time   STRUCT<member0:DOUBLE, member1:DOUBLE>,
    endpoint                 STRING,
    method                   STRING,
    query_params             STRING,
    product_id               STRING,
    request_body             STRING,
    x_forwarded_for          STRING,
    host                     STRING
    )
    STORED AS PARQUET
    LOCATION 's3a://data-catalog-bucket/kafka-nginx-log/nginx-topic/';
    ```

3. 생성된 external nginx log 테이블 확인

    #### **lab4-2-3**

    ```bash
    SELECT
    remote_addr,
    request,
    method,
    status.member1               AS http_status,
    body_bytes_sent.member1      AS bytes_sent,
    request_time.member1         AS resp_time,
    upstream_response_time.member1 AS up_resp_time,
    CAST(`timestamp` AS TIMESTAMP) AS event_time,
    http_referer,
    session_id,
    user_id,
    query_params,
    product_id,
    x_forwarded_for,
    host,
    http_user_agent,
    endpoint
    FROM external_nginx_log
    LIMIT 10;
    ```

4. mysql users 테이블 생성

     #### **lab4-2-4**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS mysql_users (
      after STRUCT<
        user_id:    STRING,
        name:       STRING,
        email:      STRING,
        gender:     STRING,
        age:        INT,
        updated_at: BIGINT
      >,
      ts_ms BIGINT
    )
    ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
    LOCATION 's3a://data-catalog-bucket/raw_cdc_events/mysql-server.shopdb.users/';
    ```

5. 생성된 mysql users 테이블 확인

     #### **lab4-2-5**

    ```bash
    SELECT * FROM mysql_users LIMIT 10;
    ```

6. mysql orders 테이블 생성

     #### **lab4-2-6**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS mysql_orders (
      after STRUCT<
        quantity:    INT,
        user_id:     STRING,
        price:       STRING,
        product_id:  STRING,
        session_id:  STRING,
        order_time:  BIGINT,
        order_id:    STRING
      >,
      ts_ms BIGINT
    )
    ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
    LOCATION 's3a://data-catalog-bucket/raw_cdc_events/mysql-server.shopdb.orders/';
    ```

7. 생성된 mysql orders 테이블 확인

     #### **lab4-2-7**

    ```bash
    select * from mysql_orders limit 10;
    ```

8. mysql products 테이블 생성

     #### **lab4-2-8**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS mysql_products (
      after STRUCT<
        price:    STRING,
        name:     STRING,
        id:       STRING,
        category: STRING
      >,
      ts_ms BIGINT
    )
    ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
    LOCATION 's3a://data-catalog-bucket/raw_cdc_events/mysql-server.shopdb.products/';
    ```

9. 생성된 mysql products 테이블 확인

     #### **lab4-2-9**

    ```bash
    select * from mysql_products limit 10;
    ```

10. hue 쿼리를 위한 view 생성

     #### **lab4-2-10-1**

    ```bash
    CREATE VIEW hive_users_flat AS
    SELECT
      after.user_id    AS user_id,
      after.name       AS name,
      after.email      AS email,
      after.gender     AS gender,
      after.age        AS age,
      after.updated_at AS updated_at,
      ts_ms            AS ts_ms
    FROM mysql_users;
    ```

    #### **lab4-2-10-2**

    ```bash
    CREATE VIEW hive_orders_flat AS
    SELECT
      after.order_id    AS order_id,
      after.user_id     AS user_id,
      after.product_id  AS product_id,
      after.quantity    AS quantity,
      CAST(after.price AS DOUBLE) AS price,
      CAST(FROM_UNIXTIME(after.order_time DIV 1000000) AS TIMESTAMP) AS order_ts,
      after.session_id  AS session_id,
      ts_ms             AS ts_ms
    FROM mysql_orders;
    ```

    #### **lab4-2-10-3**

    ```bash
    CREATE VIEW hive_products_flat AS
    SELECT
      after.id       AS product_id,
      after.name     AS name,
      after.category AS category,
      CAST(after.price AS DOUBLE) AS price,
      ts_ms          AS ts_ms
    FROM mysql_products;
    ```


## 3. hue를 이용한 쿼리를 통해 지표 분석

1. 


   
