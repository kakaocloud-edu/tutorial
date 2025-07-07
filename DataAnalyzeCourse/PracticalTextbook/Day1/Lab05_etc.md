# 데이터 분석 지표 쿼리문 정리

특정 기간 동안의 다양한 웹 로그 및 DB 로그를 활용해 주요 지표를 조회하는 SQL/쿼리문 예시입니다.

---



## 2. 고유 방문자 수 (Unique Visitors)

**설명**: 특정 기간 동안의 고유 사용자 수  
**데이터 소스**: MySQL DB  

1. 세션 기준

    #### lab5-etc-2-1
    
    ```sql
    SELECT date_format(created_at, '%Y-%m-%d %H:00:00') AS hour,
         count(distinct session_id) AS unique_visitors
    FROM sessions
    WHERE created_at BETWEEN TIMESTAMP '2025-07-01 00:00:00'
                        AND TIMESTAMP '2025-07-31 23:59:59'
    GROUP BY 1
    ORDER BY 1;
    ```

2. 사용자 기준

    #### lab5-etc-2-2
    
    ```sql
    SELECT date_format(login_time, '%Y-%m-%d %H:00:00') AS hour,
         count(distinct user_id) AS unique_visitors
    FROM sessions
    WHERE user_id IS NOT NULL
    AND login_time BETWEEN TIMESTAMP '2025-07-01 00:00:00'
                        AND TIMESTAMP '2025-07-31 23:59:59'
    GROUP BY 1
    ORDER BY 1;
    ```





## 5. 트래픽 소스 (Traffic Sources)

**설명**: 트래픽의 출처(`Referer`)에 따른 분포  
**데이터 소스**: Nginx Log

**필드**: http_referer

  #### lab5-etc-5
  
  ```sql
  SELECT 
      COALESCE(source, 'DIRECT') AS traffic_source,
      COUNT(*) AS count,
      ROUND(COUNT(*) * 100.0 / total.total_count, 2) AS percentage
  FROM (
      SELECT 
           CASE 
               WHEN http_referer IS NULL OR http_referer = '' THEN 'DIRECT'
               ELSE regexp_extract(http_referer, '^(?:https?://)?([^/]+)', 1)
           END AS source
      FROM kafka_data
  ) t
  CROSS JOIN (
      SELECT COUNT(*) AS total_count
      FROM kafka_data
  ) total
  GROUP BY source, total.total_count
  ORDER BY count DESC;
  ```

## 6. 신규 사용자 수 (New Users)

**설명**: 특정 기간 동안 신규로 가입한 사용자 수  
**데이터 소스**: MySQL DB

  #### lab5-etc-6
  
  ```sql
    SELECT
        CAST(DATE_PARSE(n.timestamp, '%Y-%m-%dT%H:%i:%s.000Z') AS DATE) AS activity_date,
        COUNT(DISTINCT s.user_id) AS active_users
    FROM data_origin.shopdb.sessions s
    JOIN data_catalog.data_catalog_database.kafka_log_table n
      ON s.session_id = n.session_id
    WHERE n.timestamp BETWEEN '2025-07-01' AND '2025-07-31'
    GROUP BY CAST(DATE_PARSE(n.timestamp, '%Y-%m-%dT%H:%i:%s.000Z') AS DATE)
    ORDER BY activity_date;
  ```

## 7. 활성 사용자 수 (Active Users) (join 하는 케이스)

**설명**: 특정 기간 동안 활동한 사용자 수 (월별)  
**데이터 소스**: MySQL DB, Nginx log  

Kafka 데이터 기준으로 SELECT 진행  
`session_id`를 기준으로 join하여 한달 기준 활성 사용자 수 조회

**필드**: session_id, timestamp

  #### lab5-etc-7
  
  ```sql
  SELECT
      CAST(DATE_PARSE(n.timestamp, '%Y-%m-%dT%H:%i:%s.000Z') AS DATE) AS activity_date,
      COUNT(DISTINCT s.user_id) AS active_users
  FROM data_origin.shopdb.sessions s
  JOIN data_catalog_test.dc_database.kafka_data n
    ON s.session_id = n.session_id
  WHERE n.timestamp BETWEEN '2025-02-01' AND '2025-02-28'
  GROUP BY CAST(DATE_PARSE(n.timestamp, '%Y-%m-%dT%H:%i:%s.000Z') AS DATE)
  ORDER BY activity_date;
  ```

## 8. 세션 수 및 평균 세션 길이 (Session Count & Average Session Length)

**설명**: 특정 기간 동안의 세션 수 및 평균 세션 지속 시간  
**데이터 소스**: MySQL DB

  #### lab5-etc-8
  
  ```sql
  SELECT
      COUNT(*) AS session_count,
      ROUND(AVG(date_diff('second', login_time, logout_time)), 2) AS avg_session_duration_seconds
  FROM shopdb.sessions
  WHERE login_time >= CAST('2025-02-14 00:00:00' AS timestamp)
    AND login_time < CAST('2025-02-15 00:00:00' AS timestamp)
    AND logout_time IS NOT NULL;
  ```

## 9. 사용자 재방문율 (User Retention Rate) (실제 트래픽 쌓는중, 다시)

**설명**: 특정 기간 동안 재방문한 사용자 비율  
**데이터 소스**: MySQL DB  

아래는 임의 데이터 예시로 2월 13일, 2월 14일 사용자의 재방문 비율을 계산한 코드이다.

  #### lab5-etc-9-1
  
  ```sql
  -- 첫 번째 INSERT (2월 13일 데이터)
  INSERT INTO data_origin.shopdb.sessions (session_id, user_id, created_at, login_time, logout_time, last_active)
  VALUES
  ('sess-20250213-001', 'user_A', TIMESTAMP '2025-02-13 09:00:00', TIMESTAMP '2025-02-13 09:00:00', TIMESTAMP '2025-02-13 09:30:00', TIMESTAMP '2025-02-13 09:30:00'),
  ('sess-20250213-002', 'user_B', TIMESTAMP '2025-02-13 10:00:00', TIMESTAMP '2025-02-13 10:00:00', TIMESTAMP '2025-02-13 10:20:00', TIMESTAMP '2025-02-13 10:20:00'),
  ('sess-20250213-003', 'user_433921', TIMESTAMP '2025-02-13 11:00:00', TIMESTAMP '2025-02-13 11:00:00', TIMESTAMP '2025-02-13 11:15:00', TIMESTAMP '2025-02-13 11:15:00');
  
  -- 두 번째 INSERT (2월 14일 데이터)
  INSERT INTO data_origin.shopdb.sessions (session_id, user_id, created_at, login_time, logout_time, last_active)
  VALUES
  ('sess-20250214-001', 'user_A', TIMESTAMP '2025-02-14 09:30:00', TIMESTAMP '2025-02-14 09:30:00', TIMESTAMP '2025-02-14 10:15:00', TIMESTAMP '2025-02-14 10:15:00'),
  ('sess-20250214-002', 'user_C', TIMESTAMP '2025-02-14 10:00:00', TIMESTAMP '2025-02-14 10:00:00', TIMESTAMP '2025-02-14 10:30:00', TIMESTAMP '2025-02-14 10:30:00'),
  ('sess-20250214-003', 'user_433921', TIMESTAMP '2025-02-14 11:00:00', TIMESTAMP '2025-02-14 11:00:00', TIMESTAMP '2025-02-14 11:20:00', TIMESTAMP '2025-02-14 11:20:00');
  ```
  
  #### lab5-etc-9-2
  
  ```sql
  WITH previous AS (
    -- 2월 13일에 접속한 사용자 목록 (이전 기간)
    SELECT DISTINCT user_id
    FROM data_origin.shopdb.sessions
    WHERE login_time BETWEEN TIMESTAMP '2025-02-13 00:00:00'
                           AND TIMESTAMP '2025-02-13 23:59:59'
      AND user_id IS NOT NULL
  ),
  current AS (
    -- 2월 14일에 접속한 사용자 목록 (현재 기간)
    SELECT DISTINCT user_id
    FROM data_origin.shopdb.sessions
    WHERE login_time BETWEEN TIMESTAMP '2025-02-14 00:00:00'
                           AND TIMESTAMP '2025-02-14 23:59:59'
      AND user_id IS NOT NULL
  ),
  joined AS (
    -- 이전 기간 사용자에 대해 2월 14일 재방문 여부를 판단
    SELECT 
      p.user_id,
      CASE WHEN c.user_id IS NOT NULL THEN 'Yes' ELSE 'No' END AS revisited
    FROM previous p
    LEFT JOIN current c ON p.user_id = c.user_id
  ),
  rate AS (
    -- 전체 재방문율 계산 (이전 기간 사용자 중 재방문한 사용자의 비율)
    SELECT 
      ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM previous), 0), 2) AS overall_retention_rate
    FROM joined
    WHERE revisited = 'Yes'
  )
  SELECT 
    j.user_id,
    j.revisited,
    r.overall_retention_rate
  FROM joined j, rate r;
  ```



## 11. 세션 기반 방문자 수 (Unique Visitors)

**설명**: 특정 기간 동안의 고유 사용자 수  
**데이터 소스**: MySQL DB

다음 예시는 2월 14일 기준, `user_id`로 고유 방문자 수를 조회한다.

  #### lab5-etc-11
  
  ```sql
  SELECT 
    COUNT(DISTINCT user_id) AS unique_visitors
  FROM sessions
  WHERE login_time BETWEEN TIMESTAMP '2025-02-14 00:00:00' 
                      AND TIMESTAMP '2025-02-14 23:59:59';
  ```




## 13. 인기 상품 클릭 수 (Product Clicks)

1. Nginx 로그만을 활용하여 인기 상품 클릭 수 쿼리
    **설명**: 특정 기간 동안 클릭된 상품의 수  
    **데이터 소스**: Nginx 로그
    
    #### lab5-etc-13-1
    
    ```sql
    SELECT 
    regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
    COUNT(*) AS click_count
    FROM data_catalog.database1.kafka_data
    WHERE endpoint = '/product'
    GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
    ORDER BY click_count DESC;
    ```

2. Nginx 로그와 MySQL 데이터를 join하여 인기 상품 클릭 수 쿼리
    **설명**: 특정 기간 동안 클릭된 상품의 수  
    **데이터 소스**: Nginx 로그
    
    #### lab5-etc-13-2
    
    ```sql
    SELECT 
      pc.product_id,
      p.name,
      pc.click_count
    FROM (
      SELECT 
          regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
          COUNT(*) AS click_count
      FROM data_catalog_test.dc_database.kafka_data
      WHERE endpoint = '/product'
      GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
    ) AS pc
    JOIN data_origin.shopdb.products AS p
      ON pc.product_id = p.id
    ORDER BY pc.click_count DESC;
    ```

## 14. 카테고리별 페이지뷰 수 (Page Views by Category)

**설명**: 각 카테고리별로 발생한 페이지뷰 수  
**데이터 소스**: Nginx 로그

  #### lab5-etc-14
  
  ```sql
  SELECT 
    regexp_extract(query_params, 'name=([^&]+)', 1) AS category,
    COUNT(*) AS pageview_count
  FROM data_catalog.database1.kafka_data
  WHERE endpoint = '/category'
  GROUP BY regexp_extract(query_params, 'name=([^&]+)', 1)
  ORDER BY pageview_count DESC;
  ```
