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

---

## 2. 고유 방문자 수 (Unique Visitors)

**설명**: 특정 기간 동안의 고유 사용자 수  
**데이터 소스**: MySQL DB  

### 2.1 세션 기준

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

### 2.2 사용자 기준

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

---

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

---

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

---

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

---

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

---

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
