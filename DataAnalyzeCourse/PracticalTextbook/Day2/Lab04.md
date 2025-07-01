# hadoop eco의 hive로 테이블 생성 및 hue 쿼리

hadoop eco의 hive를 활용하여 nginx 로그 데이터와 mysql 데이터를 사용하여 external 테이블로 생성합니다. 생성된 테이블을 이용하여 hue로 쿼리를 진행하는 실습입니다.

---
## 1. 생성한 hadoop-eco 마스터 노드에 접속

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `HadoopMST-core-hadoop-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭

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

11. `ctrl` + `c`로 종료


## 3. hue를 이용하기 위한 환경 설정

1. 웹 브라우저 주소창에서 아래 URL 입력을 통해 hue 접속

    #### **lab4-3-1**

    ```bash
    http://{HadoopMST-core-hadoop-1 public ip주소}:8888
    ```

2. hue에 로그인

    - hadoop eco 생성 시에 만든 id와 pw 입력하여 접속
    - id:`admin`
    - pw:`Admin1234!`

3. 좌측 상단 `default` 데이터베이스 확인
4. 좌측 상단 생성된 테이블 및 뷰 확인

    - 테이블 목록
        - `external_nginx_log`
        - `mysql_orders`
        - `mysql_products`
        - `mysql_users`
  
    - 뷰 목록
        - `hive_orders_flat`
        - `hive_products_flat`
        - `hive_users_flat`

5. 쿼리문 입력창에 jar 파일 입력 후 실행

    - 쿼리문 입력 후 입력창 좌측의 화살표 클릭하여 실행

    #### **lab4-3-5**

    ```bash
    ADD JAR /opt/apache-hive-3.1.3-bin/lib/hive-hcatalog-core-3.1.3.jar;
    ```


## 4. hue를 이용한 쿼리를 통해 지표 분석

1. 쿼리문을 통한 지표 분석

    - 쿼리문 입력 후 입력창 좌측의 화살표 클릭하여 실행

2. 로그인율

    #### **lab4-4-2**

    ```bash
    SELECT
      COUNT(DISTINCT CASE WHEN endpoint = '/login' THEN session_id END) AS login_sessions,
      COUNT(DISTINCT session_id) AS total_sessions,
      CONCAT(
        CAST(
          ROUND(
            (COUNT(DISTINCT CASE WHEN endpoint = '/login' THEN session_id END) * 1.0 
             / COUNT(DISTINCT session_id)) * 100,
          2
          ) AS STRING
        ), '%'
      ) AS login_rate
    FROM external_nginx_log
    WHERE endpoint = '/login'
       OR endpoint IS NOT NULL;
    ```

3. 검색 키워드 빈도

    #### **lab4-4-3**

    ```bash
    SELECT
      regexp_extract(query_params, 'query=([^&]+)', 1) AS keyword,
      COUNT(*) AS frequency
    FROM external_nginx_log
    WHERE endpoint = '/search'
    GROUP BY regexp_extract(query_params, 'query=([^&]+)', 1)
    ORDER BY frequency DESC;
    ```

4. 장바구니 담기 전환율

    #### **lab4-4-4**

    ```bash
    WITH
    product_sessions AS (
      SELECT DISTINCT session_id
      FROM external_nginx_log
      WHERE endpoint = '/product'
        AND session_id IS NOT NULL
        AND session_id <> ''
    ),
    cart_sessions AS (
      SELECT DISTINCT session_id
      FROM external_nginx_log
      WHERE endpoint = '/cart/add'
        AND session_id IS NOT NULL
        AND session_id <> ''
    ),
    total_p AS (
      SELECT COUNT(*) AS cnt
      FROM product_sessions
    ),
    converted AS (
      SELECT COUNT(*) AS cnt
      FROM product_sessions p
      JOIN cart_sessions c
        ON p.session_id = c.session_id
    )
    
    SELECT
      CASE
        WHEN tp.cnt = 0 THEN '0%'
        ELSE CONCAT(
          CAST(
            ROUND(
              (conv.cnt * 100.0) / tp.cnt
            , 2) AS STRING
          ), '%'
        )
      END AS session_conversion_rate
    FROM total_p tp
    CROSS JOIN converted conv;
    ```

5. 인기 상품 상위 10개

    #### **lab4-4-5**

    ```bash
    WITH product_views AS (
      SELECT 
        CAST(product_id AS STRING) AS product_id, 
        COUNT(*) AS view_count
      FROM external_nginx_log
      WHERE endpoint = '/product'
      GROUP BY product_id
    ),
    product_orders AS (
      SELECT 
        product_id, 
        COUNT(*) AS order_count
      FROM hive_orders_flat
      GROUP BY product_id
    )
    SELECT
      pv.product_id,
      pv.view_count,
      COALESCE(po.order_count, 0) AS order_count,
      (pv.view_count + COALESCE(po.order_count, 0)) AS popularity_score
    FROM product_views pv
    LEFT JOIN product_orders po 
      ON pv.product_id = po.product_id
    ORDER BY popularity_score DESC
    LIMIT 10;
    ```

6. 페이지뷰(PV) 추이

    #### **lab4-4-6**

    ```bash
    SELECT
      from_unixtime(unix_timestamp(CAST(CAST(`timestamp` AS TIMESTAMP) AS STRING), 'yyyy-MM-dd HH:mm:ss'), 'yyyy-MM-dd') AS dt,
      hour(from_unixtime(unix_timestamp(CAST(CAST(`timestamp` AS TIMESTAMP) AS STRING), 'yyyy-MM-dd HH:mm:ss'))) AS hour_of_day,
      COUNT(*) AS page_views
    FROM external_nginx_log
    GROUP BY
      from_unixtime(unix_timestamp(CAST(CAST(`timestamp` AS TIMESTAMP) AS STRING), 'yyyy-MM-dd HH:mm:ss'), 'yyyy-MM-dd'),
      hour(from_unixtime(unix_timestamp(CAST(CAST(`timestamp` AS TIMESTAMP) AS STRING), 'yyyy-MM-dd HH:mm:ss')))
    ORDER BY dt, hour_of_day;
    ```

7. 매출 합계

    - 기간 조정 가능

    #### **lab4-4-7**

    ```bash
    SELECT 
      format_number(ROUND(SUM(price * quantity), 2), 2) AS total_sales
    FROM hive_orders_flat
    WHERE order_ts BETWEEN '2025-01-01' AND '2025-12-31';
    ```

8. 카테고리별 매출 비중

    #### **lab4-4-8**

    ```bash
    SELECT
      p.category,
      ROUND(SUM(o.price * o.quantity), 2) AS category_sales,
      CONCAT(
        CAST(
          ROUND(SUM(o.price * o.quantity) / total.total_sales * 100, 2) AS STRING
        ), '%'
      ) AS sales_ratio
    FROM hive_orders_flat o
    JOIN hive_products_flat p 
      ON o.product_id = p.product_id
    CROSS JOIN (
      SELECT SUM(price * quantity) AS total_sales
      FROM hive_orders_flat
    ) total
    GROUP BY p.category, total.total_sales;
    ```

9. 사용자 행동 경로 분석

    #### **lab4-4-9**

    ```bash
    WITH user_path AS (
      SELECT
        session_id,
        MAX(CASE WHEN endpoint = '/home' THEN 1 ELSE 0 END)     AS visited_home,
        MAX(CASE WHEN endpoint = '/cart/view' THEN 1 ELSE 0 END) AS viewed_product,
        MAX(CASE WHEN endpoint = '/cart/add' THEN 1 ELSE 0 END)  AS added_to_cart,
        MAX(CASE WHEN endpoint = '/login' THEN 1 ELSE 0 END)     AS logged_in
      FROM external_nginx_log
      GROUP BY session_id
    ),
    user_purchase AS (
      SELECT DISTINCT session_id
      FROM hive_orders_flat
    )
    SELECT
      up.session_id,
      up.visited_home,
      up.viewed_product,
      up.added_to_cart,
      up.logged_in,
      CASE WHEN p.session_id IS NOT NULL THEN 1 ELSE 0 END AS purchased
    FROM user_path up
    LEFT JOIN user_purchase p 
      ON up.session_id = p.session_id;
    ```

10. 상품 상세 페이지 방문 후 구매 전환율

    #### **lab4-4-10**

    ```bash
    WITH
      product_sessions AS (
        SELECT DISTINCT session_id
        FROM external_nginx_log
        WHERE endpoint = '/product'
          AND session_id IS NOT NULL
          AND session_id <> ''
      ),
      purchased_sessions AS (
        SELECT DISTINCT session_id
        FROM hive_orders_flat
        WHERE session_id IS NOT NULL
          AND session_id <> ''
      ),
      total_product AS (
        SELECT COUNT(*) AS cnt
        FROM product_sessions
      ),
      converted AS (
        SELECT COUNT(*) AS cnt
        FROM product_sessions p
        JOIN purchased_sessions ps
          ON p.session_id = ps.session_id
      )
    SELECT
      CASE
        WHEN tp.cnt = 0 THEN '0%'
        ELSE CONCAT(
          CAST(
            ROUND(
              (cv.cnt * 100.0) / tp.cnt
            , 2) AS STRING
          ),
          '%'
        )
      END AS detail_to_purchase_rate
    FROM total_product tp
    CROSS JOIN converted cv;
    ``` 

11. 사용자 나이대별 구매율

    #### **lab4-4-11**

    ```bash
    WITH purchase AS (
      SELECT DISTINCT user_id
      FROM hive_orders_flat
    )
    SELECT gender, age_group, purchase_rate
    FROM (
      SELECT
        u.gender,
        CASE
          WHEN u.age < 20 THEN '20대 미만'
          WHEN u.age BETWEEN 20 AND 29 THEN '20대'
          WHEN u.age BETWEEN 30 AND 39 THEN '30대'
          WHEN u.age BETWEEN 40 AND 49 THEN '40대'
          ELSE '50대 이상'
        END AS age_group,
        ROUND(
          COUNT(DISTINCT CASE WHEN p.user_id IS NOT NULL THEN u.user_id END) * 1.0 
          / COUNT(DISTINCT u.user_id), 
        2
        ) AS purchase_rate,
        CASE
          WHEN u.age < 20 THEN 1
          WHEN u.age BETWEEN 20 AND 29 THEN 2
          WHEN u.age BETWEEN 30 AND 39 THEN 3
          WHEN u.age BETWEEN 40 AND 49 THEN 4
          ELSE 5
        END AS age_order
      FROM hive_users_flat u
      LEFT JOIN purchase p 
        ON u.user_id = p.user_id
      GROUP BY 
        u.gender,
        CASE
          WHEN u.age < 20 THEN '20대 미만'
          WHEN u.age BETWEEN 20 AND 29 THEN '20대'
          WHEN u.age BETWEEN 30 AND 39 THEN '30대'
          WHEN u.age BETWEEN 40 AND 49 THEN '40대'
          ELSE '50대 이상'
        END,
        CASE
          WHEN u.age < 20 THEN 1
          WHEN u.age BETWEEN 20 AND 29 THEN 2
          WHEN u.age BETWEEN 30 AND 39 THEN 3
          WHEN u.age BETWEEN 40 AND 49 THEN 4
          ELSE 5
        END
    ) t
    ORDER BY t.gender ASC, t.age_order ASC;
    ``` 

12. 검색 키워드와 구매 연관성

    #### **lab4-4-12**

    ```bash
    WITH search_sessions AS (
      SELECT DISTINCT 
        session_id, 
        regexp_extract(query_params, 'query=([^&]+)', 1) AS keyword
      FROM external_nginx_log
      WHERE endpoint = '/search'
    ),
    purchased_sessions AS (
      SELECT DISTINCT session_id
      FROM hive_orders_flat
    )
    SELECT
      s.keyword,
      COUNT(DISTINCT s.session_id)     AS search_count,
      COUNT(DISTINCT CASE WHEN p.session_id IS NOT NULL THEN s.session_id END) AS purchase_count,
      CONCAT(
        CAST(
          ROUND(
            COUNT(DISTINCT CASE WHEN p.session_id IS NOT NULL THEN s.session_id END) * 1.0 
            / COUNT(DISTINCT s.session_id) * 100, 
          2
          ) AS STRING
        ), '%'
      ) AS conversion_rate
    FROM search_sessions s
    LEFT JOIN purchased_sessions p 
      ON s.session_id = p.session_id
    GROUP BY s.keyword
    ORDER BY conversion_rate DESC;
    ``` 

13. 사용자 재구매율

    #### **lab4-4-13**

    ```bash
    WITH product_user_orders AS (
      SELECT 
        product_id,
        user_id,
        COUNT(DISTINCT order_id) AS order_count
      FROM hive_orders_flat
      GROUP BY product_id, user_id
    )
    SELECT 
      puo.product_id,
      p.name AS product_name,
      CONCAT(
        CAST(
          ROUND(
            SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) * 1.0 
            / COUNT(*) * 100, 
          2
          ) AS STRING
        ), '%'
      ) AS repeat_purchase_rate
    FROM product_user_orders puo
    JOIN hive_products_flat p 
      ON puo.product_id = p.product_id
    GROUP BY puo.product_id, p.name;
    ``` 

14. 주문 당 평균 상품 수

    #### **lab4-4-14**

    ```bash
    SELECT 
      ROUND(AVG(items), 2) AS avg_items_per_order
    FROM (
      SELECT 
        order_id, 
        SUM(quantity) AS items
      FROM hive_orders_flat
      GROUP BY order_id
    ) t;
    ``` 

15. URL별 에러 발생 비율

    #### **lab4-4-15**

    ```bash
    SELECT
      endpoint,
      CONCAT(
        CAST(
          ROUND(
            SUM(CASE WHEN CAST(status.member1 AS INT) >= 400 THEN 1 ELSE 0 END) * 1.0 
            / COUNT(*) * 100,
          2
          ) AS STRING
        ), '%'
      ) AS error_rate
    FROM external_nginx_log
    GROUP BY endpoint;
    ``` 




   
