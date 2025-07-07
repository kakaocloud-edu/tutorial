# 데이터 분석 지표 쿼리문 정리

특정 기간 동안의 다양한 웹 로그 및 DB 로그를 활용해 주요 지표를 조회하는 SQL/쿼리문 예시입니다.

---

## 1. 고유 방문자 수 (Unique Visitors)

**설명**: 특정 기간 동안의 고유 사용자 수

**데이터 소스**: MySQL DB

**필드**: `sessions` (크롤링으로 추가됨)

- 데이터 원본: `data_orign`
- 데이터 베이스: `shopdb`

1. 세션 기준
    
    ### lab5-etc-1-1
    
    ```sql
    SELECT date_format(created_at, '%Y-%m-%d %H:00:00') AS hour,
         count(distinct session_id) AS visitors
    FROM data_origin.shopdb.sessions
    GROUP BY 1
    ORDER BY 1;
    
    ```
    
2. 사용자 기준
    
    ### lab5-etc-1-2
    
    ```sql
    SELECT date_format(login_time, '%Y-%m-%d %H:00:00') AS hour,
         count(distinct user_id) AS visitors
    FROM data_origin.shopdb.sessions
    WHERE user_id IS NOT NULL
    GROUP BY 1
    ORDER BY 1;
    
    ```
    

## 2. 신규 사용자 수 (New Users)

**설명**: 특정 기간 동안 신규로 가입한 사용자 수

**데이터 소스**: MySQL DB

**필드**: `users_logs` (크롤링으로 추가됨)

- 데이터 원본: `data_orign`
- 데이터 베이스: `shopdb`
- 특정 기간 수정

### lab5-etc-2

```sql
SELECT
  date_trunc('hour', event_time) AS signup_hour,
  COUNT(DISTINCT user_id)      AS new_users
FROM data_origin.shopdb.users_logs
WHERE event_type = 'CREATED'
  AND event_time BETWEEN TIMESTAMP '2025-07-01'
                     AND TIMESTAMP '2025-07-31'
GROUP BY 1
ORDER BY 1;
```

## 3. 세션 수 및 평균 세션 길이 (Session Count & Average Session Length)

**설명**: 특정 기간 동안의 세션 수 및 평균 세션 지속 시간

**데이터 소스**: MySQL DB

**필드**: `sessions` (크롤링으로 추가됨)

- 데이터 원본: `data_orign`
- 데이터 베이스: `shopdb`
- 특정 기간 수정

### lab5-etc-3

```sql
SELECT
    CAST(MIN(login_time) AS DATE) AS period_start,
    CAST(MAX(login_time) AS DATE) AS period_end,
    COUNT(*)                       AS session_count,
    ROUND(AVG(date_diff('second', login_time, logout_time)), 2)
                                   AS avg_session_duration_seconds
FROM data_origin.shopdb.sessions
WHERE login_time >= TIMESTAMP '2025-07-01'
  AND login_time <  TIMESTAMP '2025-07-31'
  AND logout_time IS NOT NULL;
```

## 4. 트래픽 소스 (Traffic Sources)

**설명**: 트래픽의 출처(`Referer`)에 따른 분포

**데이터 소스**: Nginx Log

**필드**: `http_referer` (kafka_log_table 필드에 추가)

| 파티션 키 | 컬럼 번호 | 필드 이름     | 데이터 유형 |설명(선택)|
|----------|----------|--------------|------------|------------|
| 미사용   | 4        | http_referer | string     | 빈 칸      |

- 데이터 원본: `data_catalog`
- 데이터 베이스: `data_catalog_database`

### lab5-etc-4

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
    FROM data_catalog.data_catalog_database.kafka_log_table
) t
CROSS JOIN (
    SELECT COUNT(*) AS total_count
    FROM data_catalog.data_catalog_database.kafka_log_table
) total
GROUP BY source, total.total_count
ORDER BY count DESC;
```

## 5. 카테고리별 페이지뷰 수 (Page Views by Category)

**설명**: 각 카테고리 별로 발생한 페이지뷰 수

**데이터 소스**: Nginx Log

**필드**: `endpoint` , `query_params` (kafka_log_table 필드에 추가)
| 파티션 키 | 컬럼 번호 | 필드 이름     | 데이터 유형 |설명(선택)|
|----------|----------|--------------|------------|------------|
| 미사용   | 5        | endpoint     | string     | 빈 칸      |
| 미사용   | 6        | query_params | string     | 빈 칸      |

- 데이터 원본: `data_catalog`
- 데이터 베이스: `data_catalog_database`

### lab5-etc-5

```sql
SELECT
  regexp_extract(query_params, 'name=([^&]+)', 1) AS category,
  COUNT(*) AS pageview_count
FROM data_catalog.data_catalog_database.kafka_log_table
WHERE endpoint = '/category'
GROUP BY regexp_extract(query_params, 'name=([^&]+)', 1)
ORDER BY pageview_count DESC;

```

## 6. 인기 상품 클릭 수 (Product Clicks)

**설명**: 특정 기간 동안 클릭된 상품의 수

**데이터 소스**: Nginx Log

**필드**: 1. kafka - `endpoint` , `query_params`(kafka_log_table 필드에 추가)

| 파티션 키 | 컬럼 번호 | 필드 이름     | 데이터 유형 |설명(선택)|
|----------|----------|--------------|------------|------------|
| 미사용   | 5        | endpoint     | string     | 빈 칸      |
| 미사용   | 6        | query_params | string     | 빈 칸      |

**필드**: 2. mysql - `sessions` (크롤링으로 추가됨)

- 데이터 원본: `data_catalog`
- 데이터 베이스: `data_catalog_database`
    1. Nginx 로그만을 활용하여 인기 상품 클릭 수 쿼리
    
    ### lab5-etc-6-1
    
    ```sql
    SELECT
    regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
    COUNT(*) AS click_count
    FROM data_catalog.data_catalog_database.kafka_log_table
    WHERE endpoint = '/product'
    GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
    ORDER BY click_count DESC;
    
    ```
    

1. Nginx 로그와 MySQL 데이터를 JOIN하여 인기 상품 클릭 수 쿼리

### lab5-etc-6-2

```sql
SELECT
  pc.product_id,
  p.name,
  pc.click_count
FROM (
  SELECT
      regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
      COUNT(*) AS click_count
  FROM data_catalog.data_catalog_database.kafka_log_table
  WHERE endpoint = '/product'
  GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
) AS pc
JOIN data_origin.shopdb.products AS p
  ON pc.product_id = p.id
ORDER BY pc.click_count DESC;

```

## 7. 활성 사용자 수 (Active Users)

**설명**: 특정 기간 동안 활동한 사용자 수

**데이터 소스**: MySQL DB, Nginx log

**필드**: 1. kafka - `session_id` , `timestamp`(kafka_log_table 필드에 추가)

| 파티션 키 | 컬럼 번호 | 필드 이름     | 데이터 유형 |설명(선택)|
|----------|----------|--------------|------------|------------|
| 미사용   | 7        | session_id   | string     | 빈 칸      |
| 미사용   | 8        | timestamp    | string     | 빈 칸      |

**필드**: 2. mysql - `sessions` (크롤링으로 추가됨)

- 데이터 원본: `data_orign`
- 데이터 베이스: `shopdb`
- 특정 기간 수정

### lab5-etc-7

```sql
SELECT
  CAST(
    DATE_PARSE(n.timestamp, '%Y-%m-%d %H:%i:%s')
  AS DATE)              AS activity_date,
  COUNT(DISTINCT s.user_id) AS active_users
FROM data_origin.shopdb.sessions   AS s
JOIN data_catalog.data_catalog_database.kafka_log_table AS n
  ON s.session_id = n.session_id
WHERE
  CAST(
    DATE_PARSE(n.timestamp, '%Y-%m-%d %H:%i:%s')
  AS DATE)
    BETWEEN DATE '2025-07-01'
        AND DATE '2025-07-31'
GROUP BY 1
ORDER BY 1;
```
