# Hadoop Eco의 Hive로 테이블 생성 및 Hue 쿼리

Hadoop Eco의 Hive를 활용하여 Nginx 로그 데이터와 MySQL 데이터를 사용하여 External 테이블로 생성합니다. 생성된 테이블을 이용하여 Hue로 쿼리를 진행하는 실습입니다.

---
## 1. Object Storage 버킷 권한 설정 (약 5분 소요)
1. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
2. `data-catalog-bucket` 버킷 설정
      - `data-catalog-bucket` 버킷 클릭
           - 권한 탭 클릭
              - 접근 탭 클릭
              - 접근 설정 버튼 클릭
                 - 액세스 권한
                    - `퍼블릭 액세스 허용 (Read Only)` 선택
                    - 접근 허용 IP 주소: 빈 칸
                    - 저장 버튼 클릭
                  - 확인 버튼 클릭
      - `퍼블릭 액세스`가 `허용 (Read Only)`으로 바뀐 것을 확인

      ![1](https://github.com/user-attachments/assets/dade13de-cdd4-42f9-a1a6-0795281e093b)

## 2. Hadoop-Eco 마스터 노드 접속 (약 1분 소요)

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `HadoopMST-hadoop-eco-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭

    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력

    #### **lab4-2-2-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab4-2-2-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab4-2-2-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{HadoopMST-core-hadoop-1 public ip주소}
    ```
    
    #### **lab4-2-2-4**
    
    ```bash
    yes
    ```


## 3. Hive에 External 테이블 생성 (약 10분 소요)

1. Hive에 접속

    - Hive 연결 시 로깅 관련 경고와 세션 정보 뜨는 것 확인

    #### **lab4-3-1**

    ```bash
    hive
    ```
    
    ![hive 접속 확인](https://github.com/user-attachments/assets/1bf442e7-0139-4e7c-88fe-b83562b9ad7f)

2. external_nginx_log 테이블 생성

    #### **lab4-3-2**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS external_nginx_log (
      `timestamp`              STRING,
      remote_addr              STRING,
      request                  STRING,
      status                   STRUCT<member0:INT, member1:INT>,
      body_bytes_sent          STRUCT<member0:BIGINT, member1:BIGINT>,
      http_referer             STRING,
      session_id               STRING,
      user_id                  STRING,
      request_time             STRUCT<member0:DOUBLE, member1:DOUBLE>,
      upstream_response_time   STRUCT<member0:DOUBLE, member1:DOUBLE>,
      endpoint                 STRING,
      method                   STRING,
      query_params             STRING,
      product_id               STRING,
      host                     STRING
    )
    STORED AS PARQUET
    LOCATION 's3a://data-catalog-bucket/kafka-nginx-log/nginx-topic/';
    ```

3. 생성된 external_nginx_log 테이블 확인

    - 테이블의 컬럼명이 뜨도록 설정
  
     #### **lab4-3-3-1**

    ```bash
    SET hive.cli.print.header=true;
    ``` 

    #### **lab4-3-3-2**

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
      host,
      endpoint
    FROM external_nginx_log
    LIMIT 10;
    ```
    - 아래와 같은 형식의 내용 확인
    
    ![1 external table 확인v1](https://github.com/user-attachments/assets/01a54ded-cb90-47fd-b57d-ce2c59206ccc)

4. mysql_users 테이블 생성

     #### **lab4-3-4**

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

5. 생성된 mysql_users 테이블 확인

     #### **lab4-3-5**

    ```bash
    SELECT
       `after`.user_id    AS user_id,
       `after`.name       AS name,
       `after`.email      AS email,
       `after`.gender     AS gender,
       `after`.age        AS age,
       ts_ms
     FROM mysql_users
     LIMIT 10;
    ```
    - 아래와 같은 형식의 내용 확인
   
    ![2 mysql users 확인v1](https://github.com/user-attachments/assets/0e2f25ba-22b0-44b5-aeba-fa88acba183f)

6. mysql_orders 테이블 생성

     #### **lab4-3-6**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS mysql_orders (
      after STRUCT<
        order_id:    STRING,
        user_id:     STRING,
        product_id:  STRING,
        quantity:    INT,
        price:       STRING,
        session_id:  STRING,
        order_time:  BIGINT
      >,
      ts_ms BIGINT
    )
    ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
    LOCATION 's3a://data-catalog-bucket/raw_cdc_events/mysql-server.shopdb.orders/';
    ```

7. 생성된 mysql_orders 테이블 확인

     #### **lab4-3-7**

    ```bash
    SELECT
      `after`.order_id    AS order_id,
      `after`.user_id     AS user_id,
      `after`.product_id  AS product_id,
      `after`.quantity    AS quantity,
      `after`.price       AS price,
      `after`.session_id  AS session_id,
      `after`.order_time  AS order_time,
      ts_ms               AS ts_ms
    FROM mysql_orders
    LIMIT 10;
    ```
    - 아래와 같은 형식의 내용 확인
    
    ![3 mysql orders 확인v1](https://github.com/user-attachments/assets/3c27665f-8908-48da-bd2d-ad6349d2ed6a)

8. mysql_products 테이블 생성

     #### **lab4-3-8**

    ```bash
    CREATE EXTERNAL TABLE IF NOT EXISTS mysql_products (
      after STRUCT<
        id:       STRING,
        name:     STRING,
        category: STRING,
        price:    STRING
      >,
      ts_ms BIGINT
    )
    ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
    LOCATION 's3a://data-catalog-bucket/raw_cdc_events/mysql-server.shopdb.products/';
    ```

9. 생성된 mysql_products 테이블 확인

     #### **lab4-3-9**

    ```bash
    SELECT
      `after`.id       AS id,
      `after`.name     AS name,
      `after`.category AS category,
      `after`.price    AS price,
      ts_ms            AS ts_ms
    FROM mysql_products
    LIMIT 10;
    ```
    - 아래와 같은 형식의 내용 확인

    ![4 mysql products 확인v1](https://github.com/user-attachments/assets/c90be6b7-4289-405a-a922-a681cf487558)

10. Hue 쿼리를 위한 view 생성

     #### **lab4-3-10-1**

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

    #### **lab4-3-10-2**

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

    #### **lab4-3-10-3**

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

11. 생성한 테이블 목록 확인

    #### **lab4-3-11**

    ```bash
    show tables;
    ```

    - 아래와 같은 테이블 목록 확인
   
    ![table 목록 확인](https://github.com/user-attachments/assets/cc5f9be5-c2ff-4ba1-9472-d1941a112ed4)

12. `ctrl` + `c`로 종료


## 4. Hue 환경 설정 (약 5분 소요)
 
1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `HadoopMST-hadoop-eco-1` 인스턴스의 `기본 퍼블릭 IP` 복사
3. 웹 브라우저 주소창에서 아래 URL 입력을 통해 Hue 접속

    #### **lab4-4-3**

    ```bash
    http://{HadoopMST-core-hadoop-1 public ip주소}:8888
    ```

4. Hue에 로그인

    - hadoop eco 생성 시에 만든 ID와 PW 입력하여 접속
    - ID:`admin`
    - PW:`Admin1234!`

5. 좌측 상단 `default` 데이터베이스 확인
6. 좌측 상단 생성된 테이블 및 뷰 확인

    - 테이블 목록
        - `external_nginx_log`
        - `mysql_orders`
        - `mysql_products`
        - `mysql_users`
  
    - 뷰 목록
        - `hive_orders_flat`
        - `hive_products_flat`
        - `hive_users_flat`

7. 쿼리문 입력창에 jar 파일 입력 후 실행

    - 쿼리문 입력 후 입력창 좌측의 화살표 클릭하여 실행
    - Hive 메타스토어에 저장된 테이블 정보를 Hadoop Eco와 공유해주는 HCatalog 코어 라이브러리 추가 
    
    
    #### **lab4-4-7**

    ```bash
    ADD JAR /opt/apache-hive-3.1.3-bin/lib/hive-hcatalog-core-3.1.3.jar;
    ```

8. jar 파일 입력 실행 성공 확인

    - 아래와 같은 형식의 내용 확인

    <img width="1629" height="581" alt="8  jar 파일 실행" src="https://github.com/user-attachments/assets/a3952fc7-a44b-4fea-9262-72f90b334428" />

## 5. Hue를 이용한 쿼리를 통해 지표 분석 (약 20분 소요)

1. 쿼리문을 통한 지표 분석

    - 쿼리문 입력 후 입력창 좌측의 화살표 클릭하여 실행

2. 로그인율

    - /login 엔드포인트를 호출한 고유 세션 수를 전체 세션 수로 나눠 백분율로 계산

    #### **lab4-5-2**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리1](https://github.com/user-attachments/assets/7350f02b-7ee8-4f6d-83cd-6bf601c93333)

3. 검색 키워드 빈도

    - /search 엔드포인트의 query_params에서 키워드를 추출해 그룹별 등장 횟수를 집계

    #### **lab4-5-3**

    ```bash
    SELECT
      regexp_extract(query_params, 'query=([^&]+)', 1) AS keyword,
      COUNT(*) AS frequency
    FROM external_nginx_log
    WHERE endpoint = '/search'
    GROUP BY regexp_extract(query_params, 'query=([^&]+)', 1)
    ORDER BY frequency DESC;
    ```

    - 아래와 같은 형식의 내용 확인

    ![쿼리2](https://github.com/user-attachments/assets/563daec5-9269-45c8-8631-35178a28cc14)

4. 인기 상품 상위 10개

    - 상품 상세 조회 수(view_count)와 주문 수(order_count)를 더해 만든 popularity_score로 내림차순 정렬 후 상위 10개 추출

    #### **lab4-5-4**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리4](https://github.com/user-attachments/assets/299b3524-ccb6-4079-bf60-7bdce81c898e)

5. 페이지뷰(PV) 추이

    - 로그의 타임스탬프를 날짜·시간별로 변환해 각 그룹별 페이지뷰 수를 집계

    #### **lab4-5-5**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리5](https://github.com/user-attachments/assets/021c432d-3054-4d85-b07e-9ce31fee77cc)

6. 매출 합계

    - 지정 기간 내 모든 주문의 price * quantity를 합산해 총 매출 산출
    - 지정 기간 조정 가능

    #### **lab4-5-6**

    ```bash
    SELECT 
      format_number(ROUND(SUM(price * quantity), 2), 2) AS total_sales
    FROM hive_orders_flat
    WHERE order_ts BETWEEN '2025-01-01' AND '2025-12-31';
    ```

    - 아래와 같은 형식의 내용 확인

    ![쿼리6](https://github.com/user-attachments/assets/222b45c0-7d6a-45da-8165-604bf02562d1)

7. 카테고리별 매출 비중

    - 상품 카테고리별 매출액을 계산한 뒤 전체 매출액 대비 비율(%)로 환산

    #### **lab4-5-7**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리7](https://github.com/user-attachments/assets/464d8326-073f-4437-9013-498e728b7928)

8. 사용자 행동 히스토리 분석

    - 세션별로 주요 엔드포인트 방문 여부를 플래그로 표시하고, 주문 세션 유무를 결합해 사용자 히스토리 파악

    #### **lab4-5-8**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리8](https://github.com/user-attachments/assets/dcf4bdde-8755-4c21-ba32-3872b4a6f9bb)

9. 사용자 나이대별 구매율

    - 연령대·성별로 그룹화한 사용자 중 주문을 한 비율을 계산

    #### **lab4-5-9**

    ```bash
    WITH purchase AS (
      SELECT DISTINCT user_id
      FROM hive_orders_flat
    ),
    agg AS (
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
          COUNT(DISTINCT CASE WHEN p.user_id IS NOT NULL THEN u.user_id END) * 1.0 / COUNT(DISTINCT u.user_id), 2) AS purchase_rate,
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
    )
    SELECT gender, age_group, purchase_rate
    FROM agg
    WHERE gender IS NOT NULL
      AND purchase_rate IS NOT NULL
    ORDER BY gender ASC, age_order DESC;
    ```

    - 아래와 같은 형식의 내용 확인

    ![쿼리9](https://github.com/user-attachments/assets/9e84f561-c876-464b-b3be-b1edcb4e19b7)

10. 검색 키워드와 구매 연관성

    - 키워드별 검색 세션 수와 구매 세션 수를 비교해 전환율(%)을 산출

    #### **lab4-5-10**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리10](https://github.com/user-attachments/assets/cd82fd46-1bbc-40d4-b78a-ff3e5efeb64c)

11. 사용자 재구매율

    - 상품별로 사용자당 주문 횟수를 집계해, 2회 이상 주문한 사용자 비율을 계산

    #### **lab4-5-11**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리11](https://github.com/user-attachments/assets/82ec5a4e-b567-4230-82c9-d7a97145f56a)

12. 주문 당 평균 상품 수

    - 주문별로 담은 상품 수(quantity 합계)의 평균을 산출

    #### **lab4-5-12**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리12](https://github.com/user-attachments/assets/bb12f438-84b7-4d68-aea1-6e49ac0d11b7)

13. URL별 에러 발생 비율

    - 엔드포인트별로 HTTP 상태 코드가 400 이상인 로그 비율을 계산해 에러율로 표시

    #### **lab4-5-13**

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

    - 아래와 같은 형식의 내용 확인

    ![쿼리13](https://github.com/user-attachments/assets/985fac64-db10-48d7-bec5-f1173e26fb35)



   
