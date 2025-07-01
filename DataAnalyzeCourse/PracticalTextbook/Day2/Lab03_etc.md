# 기타 Superset 지표

1. 제품별 장바구니→주문 전환율(dw_cart_orders_products)
    - Time-series Bar Chart
        - dw_cart_orders_products Dataset 수정 버튼 클릭
        - METRICS 탭 클릭
        - METRIC 추가
            - [+ ADD ITEM] 버튼 클릭
            
            | Metric | Label | SQL expression |
            | --- | --- | --- |
            | cart_count | 빈 칸 | COUNT(DISTINCT CASE WHEN event_type = 'ADDED' THEN cart_id ELSE NULL END) |
            | order_count | 빈 칸 | COUNT(DISTINCT CASE WHEN event_type = 'CHECKED_OUT' THEN cart_id ELSE NULL END) |
            | conversion_rate | 빈 칸 | COUNT(DISTINCT CASE WHEN event_type = 'CHECKED_OUT' THEN cart_id ELSE NULL END)
            * 100.0
            / COUNT(DISTINCT CASE WHEN event_type = 'ADDED' THEN cart_id ELSE NULL END) |
        - Time-series Bar Chart 클릭
        - Time Grain: Year
        - Metrics: conversion_rate
        - Dimension: product_id
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/c0f99d76-4264-4c11-a48b-c788a224f334)

        
2. 조회→장바구니→결제 전환률(nginx-topic)
    - Funnel Chart
        - 상단 SQL > SQL Lab 메뉴 클릭
        - 엔드포인트 단계별 발생 횟수 집계 쿼리 입력
            
            ```sql
            SELECT
              CASE endpoint
                WHEN '/product'   THEN 'Pageview'
                WHEN '/cart/add'  THEN 'CartAdd'
                WHEN '/checkout'  THEN 'Checkout'
                ELSE NULL
              END AS stage,
              COUNT(*) AS cnt
            FROM "nginx-topic"
            WHERE endpoint IN ('/product','/cart/add','/checkout')
            GROUP BY 1
            ```
            
        - RUN 버튼 클릭
        - CREATE CHART 버튼 클릭
        - View all charts 클릭
        - Advanced-Analytics 탭 클릭 후 Funnel Chart 차트 선택
        - SELECT 버튼 클릭
        - Dimensions: stage
        - Metric
            - COLUMN: cnt
            - AGGREGATE: SUM
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/ee8e4df0-95c6-403c-b55f-c4afdf3267ad)


3. 남녀 사용자 비율(nginx-topic)
    - Pie Chart
        - Dimensions: user_gender
        - Metric
            - SIMPLE 탭 클릭
            - COLUMN: topic_session_id
            - AGGREGATE: COUNT
            - SAVE 버튼 클릭
        - FILTERS
            - user_gender
            - Not equal to (≠)
            - 빈 칸
            - SAVE 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/213f6c13-b57a-49e2-a24d-42077740aea0)

        
4. 시간대별 주문 건수 (shopdb_orders_changes)
    - Calendar Heatmap
        - View all charts 클릭
        - Calendar Heatmap 검색 후 SELECT 버튼 클릭
        - Time Range
            - RANGE TYPE: Custom
            - START (INCLUSIVE)
                - Specific Date/Time
                - 실습 당일 00시 00분
            - END (EXCLUSIVE): Now
            - APPLY 버튼 클릭
        - Domain: hour
        - Subdomain: min
        - Metrics
            - SIMPLE 탭 클릭
            - COLUMN: order_id
            - AGGREGATE: COUNT
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/cfbd60c7-f284-4d14-a89c-68b3f738534c)

        
5. 상품별 매출 TOP 10 (shopdb_orders_changes)
    - Time-series Bar Chart
        - shopdb_orders_changes Dataset 수정 버튼 클릭
        - Column 추가
            - CALCULATED COLUMNS 탭 클릭
            - ADD ITEM 버튼 클릭
            
            | Column | SQL EXPRESSION | DATA TYPE |
            | --- | --- | --- |
            | product_name | CASE
            WHEN product_id = '101' THEN 'Wireless Earbuds'
            WHEN product_id = '102' THEN 'Bluetooth Speaker'
            WHEN product_id = '103' THEN 'Sneakers'
            WHEN product_id = '104' THEN 'Backpack'
            WHEN product_id = '105' THEN 'Coffee Mug'
            WHEN product_id = '106' THEN 'Gaming Mouse'
            WHEN product_id = '107' THEN 'Sunglasses'
            WHEN product_id = '108' THEN 'Laptop Stand'
            WHEN product_id = '109' THEN 'Gaming Keyboard'
            WHEN product_id = '110' THEN 'Game Console'
            WHEN product_id = '111' THEN 'Python Programming Book'
            WHEN product_id = '112' THEN 'Science Fiction Novel'
            WHEN product_id = '113' THEN 'Fashionable Hat'
            WHEN product_id = '114' THEN 'Air Fryer'
            WHEN product_id = '115' THEN 'Vacuum Cleaner'
            WHEN product_id = '116' THEN 'Coffee Machine'
            WHEN product_id = '117' THEN 'Jeans'
            WHEN product_id = '118' THEN 'Smartphone'
            WHEN product_id = '119' THEN 'Tablet'
            WHEN product_id = '120' THEN 'Dress'
            WHEN product_id = '121' THEN 'Gaming Headset'
            WHEN product_id = '122' THEN 'Cookbook'
            WHEN product_id = '123' THEN 'Thriller Novel'
            WHEN product_id = '124' THEN 'T-Shirt'
            END | STRING |
            - SAVE 버튼 클릭
        - shopdb_orders_changes Dataset 클릭
        - Time-series Bar Chart 클릭
        - Metrics: sales(원)
        - Dimensions: product_name
        - Series limit: 10
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/7e261c24-cc4e-4dcb-8c50-268092efcc11)

        
6. 일별 신규 가입자 수(shopdb_users_changes)
    - Time-series Bar Chart
        - Time-series Bar Chart 선택
        - Metrics
            - SIMPLE 탭 선택
            - COLUMN: user_id
            - AGGREGATE: COUNT_DISTINCT
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/eaf33a52-cd6a-4ad6-8a6a-617cfd23d6fc)

        
7. 고객 세그먼트별(성별, 연령대) 사용자 비율 (shopdb_users_changes)
    - Pie Chart
        - shopdb_users_changes Dataset 수정 버튼 클릭
        - Column 추가
            - CALCULATED COLUMNS 탭 클릭
            - ADD ITEM 버튼 클릭
            
            | Column | SQL EXPRESSION | DATA TYPE |
            | --- | --- | --- |
            | age_group | CASE
            WHEN CAST(age AS INTEGER) BETWEEN 10 AND 19 THEN '10대'
            WHEN CAST(age AS INTEGER) BETWEEN 20 AND 29 THEN '20대'
            WHEN CAST(age AS INTEGER) BETWEEN 30 AND 39 THEN '30대'
            WHEN CAST(age AS INTEGER) BETWEEN 40 AND 49 THEN '40대'
            WHEN CAST(age AS INTEGER) BETWEEN 50 AND 59 THEN '50대'
            WHEN CAST(age AS INTEGER) >= 60 THEN '60대 이상'
            ELSE '미상'
            END | STRING |
            - SAVE 버튼 클릭
        - Pie Chart 클릭
        - Dimensions: age_group, gender
        - Metrics
            - SIMPLE 탭 클릭
            - COLUMN: user_id
            - AGGREGATE: COUNT_DISTINCT
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/41054415-182d-4c14-969e-db882b6608b6)

        
8. 고객 행동 이력 기반 가입/탈퇴 수(shopdb_users_logs_changes)
    - Time-series Area Chart
        - Time-series Area Chart 클릭
        - Time Grain: Hour
        - Metrics
            - SIMPLE 탭 클릭
            - COLUMN: user_id
            - AGGREGATE: COUNT
            - SAVE 버튼 클릭
        - Dimensions: event_type
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/535ad459-1905-44d6-a67a-ad59782a1eff)

        
9. 세션당 평균 체류 시간(shopdb_sessions_changes)
    - Time-series Bar Chart
        - shopdb_sessions_changes Dataset 수정 버튼 클릭
        - METRICS 탭 클릭
        - METRIC 추가
            - [+ ADD ITEM] 버튼 클릭
            
            | Metric | Label | SQL expression |
            | --- | --- | --- |
            | Average Session Duration | 빈 칸 | AVG( (CAST(logout_time AS DOUBLE) - CAST(login_time AS DOUBLE)) / 1000000 ) |
        - Time-series Bar Chart 클릭
        - Time Grain: Hour
        - Metrics: Average Session Duration
        - Filters
            - logout_time
            - Not equal to (≠)
            - 빈 칸
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/c11a9cdf-c013-4af3-9af6-ef2a6607eb51)

        
10. 재방문 방문자 수 (shopdb_sessions_changes)
    - Time-series Bar Chart
        - Time-series Bar Chart 클릭
        - Time Grain: Hour
        - Metrics
            - SIMPLE 탭 클릭
            - COLUMN: session_id
            - AGGREGATE: COUNT_DISTINCT
            - SAVE 버튼 클릭
        - Filters
            - CUSTOM SQL 탭 클릭
            - HAVING 선택
            - COUNT(DISTINCT session_id) >= 2
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/3c1792ed-52b1-4621-b8f8-776f41e9e26d)

        
11. 인기 검색어 트렌드 (shopdb_search_logs_changes)
    - Word Cloud
        - View all charts 클릭
        - Word Cloud 검색 후 SELECT 버튼 클릭
        - Dimension: search_query
        - Metric
            - COLUMN: search_query
            - AGGREGATE: COUNT
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/045a849a-0070-461a-b738-d3e72f63ad8e)

        
12. 상품별 평균 평점 및 리뷰 참여도 (shopdb_reviews_changes)
    - Time-series Bar Chart
        - shopdb_reviews_changes Dataset 수정 버튼 클릭
        - Column 추가
            - CALCULATED COLUMNS 탭 클릭
            - ADD ITEM 버튼 클릭
            
            | Column | SQL EXPRESSION | DATA TYPE |
            | --- | --- | --- |
            | product_name | CASE
            WHEN product_id = '101' THEN 'Wireless Earbuds'
            WHEN product_id = '102' THEN 'Bluetooth Speaker'
            WHEN product_id = '103' THEN 'Sneakers'
            WHEN product_id = '104' THEN 'Backpack'
            WHEN product_id = '105' THEN 'Coffee Mug'
            WHEN product_id = '106' THEN 'Gaming Mouse'
            WHEN product_id = '107' THEN 'Sunglasses'
            WHEN product_id = '108' THEN 'Laptop Stand'
            WHEN product_id = '109' THEN 'Gaming Keyboard'
            WHEN product_id = '110' THEN 'Game Console'
            WHEN product_id = '111' THEN 'Python Programming Book'
            WHEN product_id = '112' THEN 'Science Fiction Novel'
            WHEN product_id = '113' THEN 'Fashionable Hat'
            WHEN product_id = '114' THEN 'Air Fryer'
            WHEN product_id = '115' THEN 'Vacuum Cleaner'
            WHEN product_id = '116' THEN 'Coffee Machine'
            WHEN product_id = '117' THEN 'Jeans'
            WHEN product_id = '118' THEN 'Smartphone'
            WHEN product_id = '119' THEN 'Tablet'
            WHEN product_id = '120' THEN 'Dress'
            WHEN product_id = '121' THEN 'Gaming Headset'
            WHEN product_id = '122' THEN 'Cookbook'
            WHEN product_id = '123' THEN 'Thriller Novel'
            WHEN product_id = '124' THEN 'T-Shirt'
            END | STRING |
            - SAVE 버튼 클릭
        - Time-series Bar Chart 클릭
        - Metrics
            - SIMPLE 탭 클릭
            - COLUMN: rating
            - AGGREGATE: AVG
            - SAVE 버튼 클릭
        - Dimensions: product_name
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/8454d116-9f83-486b-aa39-155fd0b2fe14)
