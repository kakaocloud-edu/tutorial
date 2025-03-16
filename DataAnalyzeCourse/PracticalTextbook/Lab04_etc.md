# 데이터 분석 지표 쿼리문 정리

특정 기간 동안의 다양한 웹 로그 및 DB 로그를 활용해 주요 지표를 조회하는 SQL/쿼리문 예시입니다.

---

## 1. 총 요청 수 (Total Requests)

**설명**: 특정 기간 동안의 총 HTTP 요청 수  
**데이터 소스**: ALB Access Log

#### lab4-etc-1

```sql
SELECT 
    COUNT(*) AS request_count
FROM alb_data
WHERE request_creation_time 
    BETWEEN '2025/02/14 09:00:00:00' 
    AND '2025/02/14 10:00:00:00';
```
![image](https://github.com/user-attachments/assets/e1639091-9444-49c1-95e8-7acede5d7783)


## 2. 고유 방문자 수 (Unique Visitors)

**설명**: 특정 기간 동안의 고유 사용자 수  
**데이터 소스**: MySQL DB  

1. 세션 기준

    #### lab4-etc-2-1
    
    ```sql
    SELECT date_format(created_at, '%Y-%m-%d %H:00:00') AS hour,
         count(distinct session_id) AS unique_visitors
    FROM sessions
    WHERE created_at BETWEEN TIMESTAMP '2025-02-14 00:00:00'
                        AND TIMESTAMP '2025-02-14 23:59:59'
    GROUP BY 1
    ORDER BY 1;
    ```
    ![image](https://github.com/user-attachments/assets/dd0ca9b1-450f-434c-88c5-85e16893f243)

2. 사용자 기준

    #### lab4-etc-2-2
    
    ```sql
    SELECT date_format(login_time, '%Y-%m-%d %H:00:00') AS hour,
         count(distinct user_id) AS unique_visitors
    FROM sessions
    WHERE user_id IS NOT NULL
    AND login_time BETWEEN TIMESTAMP '2025-02-14 00:00:00'
                        AND TIMESTAMP '2025-02-14 23:59:59'
    GROUP BY 1
    ORDER BY 1;
    ```
    ![image](https://github.com/user-attachments/assets/98f50726-d6cd-4704-aa84-8ea30aea0ba0)


## 3. HTTP 메서드 분포 (HTTP Method Distribution)

**설명**: 각 HTTP 메서드(GET, POST 등)의 비율  
**데이터 소스**: ALB Access Log

  #### lab4-etc-3
  
  ```sql
  SELECT 
      COALESCE(method, 'UNKNOWN') AS method,
      COUNT(*) AS count,
      ROUND(COUNT(*) * 100.0 / total.total_count, 2) AS percentage
  FROM (
      SELECT regexp_extract(trim(request), '^"?([A-Z]+)', 1) AS method
      FROM alb_data
  ) t
  CROSS JOIN (
      SELECT COUNT(*) AS total_count
      FROM alb_data
  ) total
  GROUP BY COALESCE(method, 'UNKNOWN'), total.total_count
  ORDER BY method;
  ```
  ![image](https://github.com/user-attachments/assets/3e744b46-6124-4643-8d71-f2504b3c283c)


## 4. HTTP 상태 코드 분포 (HTTP Status Code Distribution)

**설명**: 각 HTTP 상태 코드(2xx, 3xx, 4xx, 5xx)의 비율  
**데이터 소스**: ALB Access Log

  #### lab4-etc-4
  
  ```sql
  SELECT 
      target_status_code,
      COUNT(*) AS code_count,
      ROUND(COUNT(*) * 100.0 / total.total_count, 2) AS percentage
  FROM alb_data
  CROSS JOIN (
      SELECT COUNT(*) AS total_count
      FROM alb_data
  ) AS total
  GROUP BY target_status_code, total.total_count
  ORDER BY target_status_code;
  ```
  ![image](https://github.com/user-attachments/assets/95b43e80-3d0f-46f6-a7d4-edccb2dd0036)

## 5. 트래픽 소스 (Traffic Sources)

**설명**: 트래픽의 출처(`Referer`)에 따른 분포  
**데이터 소스**: Nginx Log

  #### lab4-etc-5
  
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
  ![image](https://github.com/user-attachments/assets/a8eea25a-7327-495a-94d0-369b7fc832c9)

## 6. 신규 사용자 수 (New Users)

**설명**: 특정 기간 동안 신규로 가입한 사용자 수  
**데이터 소스**: MySQL DB

  #### lab4-etc-6
  
  ```sql
  SELECT 
    COUNT(DISTINCT user_id) AS new_users
  FROM users_logs
  WHERE event_type = 'CREATED'
    AND event_time BETWEEN TIMESTAMP '2025-02-14 00:00:00'
                       AND TIMESTAMP '2025-02-14 23:59:59';
  ```
  ![image](https://github.com/user-attachments/assets/3c11745f-04b5-4e2e-875b-354866553e69)

## 7. 활성 사용자 수 (Active Users) (join 하는 케이스)

**설명**: 특정 기간 동안 활동한 사용자 수 (월별)  
**데이터 소스**: MySQL DB, Nginx log  

Kafka 데이터 기준으로 SELECT 진행  
`session_id`를 기준으로 join하여 한달 기준 활성 사용자 수 조회

  #### lab4-etc-7
  
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

  #### lab4-etc-8
  
  ```sql
  SELECT
      COUNT(*) AS session_count,
      ROUND(AVG(date_diff('second', login_time, logout_time)), 2) AS avg_session_duration_seconds
  FROM shopdb.sessions
  WHERE login_time >= CAST('2025-02-14 00:00:00' AS timestamp)
    AND login_time < CAST('2025-02-15 00:00:00' AS timestamp)
    AND logout_time IS NOT NULL;
  ```
  ![image](https://github.com/user-attachments/assets/cd7ab4ee-1a09-4f06-a0df-4816153b8f38)

## 9. 사용자 재방문율 (User Retention Rate) (실제 트래픽 쌓는중, 다시)

**설명**: 특정 기간 동안 재방문한 사용자 비율  
**데이터 소스**: MySQL DB  

아래는 임의 데이터 예시로 2월 13일, 2월 14일 사용자의 재방문 비율을 계산한 코드이다.

  #### lab4-etc-9-1
  
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
  
  #### lab4-etc-9-2
  
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
  ![image](https://github.com/user-attachments/assets/435065df-1a0d-4336-bce5-aec8d8564b68)

## 10. 총 페이지뷰 수 (Total Page Views)

**설명**: 특정 기간 동안의 총 페이지뷰 수  
**데이터 소스**: ALB Access Log, Nginx 로그

다음 예시는 2월 13일 기준이며, `/products` 경로에 대한 요청 횟수를 조회하는 예시이다.

  #### lab4-etc-10
  
  ```sql
  WITH page_filter AS (
    SELECT 'products' AS page, '/products' AS pattern
  )
  SELECT 
    pf.page,
    COUNT(*) AS pageview_count
  FROM data_catalog.database1.alb_data d
  JOIN page_filter pf 
    ON d.request LIKE CONCAT('%', pf.pattern, '%')
  WHERE date_parse(request_creation_time, '%Y/%m/%d %H:%i:%s:%f')
        BETWEEN TIMESTAMP '2025-02-13 00:00:00'
            AND TIMESTAMP '2025-02-13 23:59:59'
  GROUP BY pf.page;
  ```
  ![image](https://github.com/user-attachments/assets/2a9c61db-3fde-4dd5-890e-c919a2dddc3d)

## 11. 세션 기반 방문자 수 (Unique Visitors)

**설명**: 특정 기간 동안의 고유 사용자 수  
**데이터 소스**: MySQL DB

다음 예시는 2월 14일 기준, `user_id`로 고유 방문자 수를 조회한다.

  #### lab4-etc-11
  
  ```sql
  SELECT 
    COUNT(DISTINCT user_id) AS unique_visitors
  FROM sessions
  WHERE login_time BETWEEN TIMESTAMP '2025-02-14 00:00:00' 
                      AND TIMESTAMP '2025-02-14 23:59:59';
  ```
  ![image](https://github.com/user-attachments/assets/5284b7a2-b2e4-4e76-87bd-a40f0a17afcc)


## 12. HTTP 응답 코드별 요청 수 (Requests by HTTP Status Code)

**설명**: 각 HTTP 상태 코드(200, 404, 500 등)에 따른 요청 수  
**데이터 소스**: ALB Access Log

  #### lab4-etc-12
  
  ```sql
  SELECT 
    target_status_code AS status_code,
    COUNT(*) AS request_count
  FROM data_catalog.database1.alb_data
  GROUP BY target_status_code
  ORDER BY request_count DESC;
  ```
  ![image](https://github.com/user-attachments/assets/be3c0795-dec7-4cba-98c3-1f1164ce5c4c)

## 13. 인기 상품 클릭 수 (Product Clicks)

1. Nginx 로그만을 활용하여 인기 상품 클릭 수 쿼리
    **설명**: 특정 기간 동안 클릭된 상품의 수  
    **데이터 소스**: Nginx 로그
    
    #### lab4-etc-13-1
    
    ```sql
    SELECT 
    regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
    COUNT(*) AS click_count
    FROM data_catalog.database1.kafka_data
    WHERE endpoint = '/product'
    GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
    ORDER BY click_count DESC;
    ```
    ![image](https://github.com/user-attachments/assets/8b9be25e-d4c8-4762-8d7b-28d87d553d79)

2. Nginx 로그와 MySQL 데이터를 join하여 인기 상품 클릭 수 쿼리
    **설명**: 특정 기간 동안 클릭된 상품의 수  
    **데이터 소스**: Nginx 로그
    
    #### lab4-etc-13-2
    
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
    ![image](https://github.com/user-attachments/assets/c9850bcf-25ae-4029-8785-0990f99a02b3)


## 14. 카테고리별 페이지뷰 수 (Page Views by Category)

**설명**: 각 카테고리별로 발생한 페이지뷰 수  
**데이터 소스**: Nginx 로그

  #### lab4-etc-14
  
  ```sql
  SELECT 
    regexp_extract(query_params, 'name=([^&]+)', 1) AS category,
    COUNT(*) AS pageview_count
  FROM data_catalog.database1.kafka_data
  WHERE endpoint = '/category'
  GROUP BY regexp_extract(query_params, 'name=([^&]+)', 1)
  ORDER BY pageview_count DESC;
  ```
  ![image](https://github.com/user-attachments/assets/e1a221c9-268d-4cf8-96fb-3dbc764cc3e8)
