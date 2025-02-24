# Data Query 가이드

## 1. Object Storage 버킷 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 일반 버킷
2. 권한 설정
   #### kafka-nginx-log 권한 설정
   - `kafka-nginx-log` 버킷 클릭
      - 권한 탭 클릭
      - 역할 추가 버튼 클릭
      - 역할 추가
         - 사용자 계정: `없음`
         - 서비스 계정: `{프로젝트 이름}@data-query.kc.serviceagent.com`
         - 역할: `스토리지 편집자`
       - 저장 버튼 클릭


   #### alb_log 권한 설정
   - 좌측 상단의 일반 버킷 탭 클릭
   - `alb_log` 버킷 클릭 
      - 권한 탭 클릭
      - 역할 추가 버튼 클릭
      - 역할 추가
         - 사용자 계정: `없음`
         - 서비스 계정: `{프로젝트 이름}@data-query.kc.serviceagent.com`
         - 역할: `스토리지 편집자`
      - 저장 버튼 클릭


## 2. 데이터 원본 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Query > 데이터 원본 관리
2. 데이터 원본 생성 버튼 클릭
   - 기본 정보
      - 데이터 원본 이름: `data_origin`
      - 설명(선택): `없음`
   - 상세 정보
      - 데이터 원본 유형: `MySQL`
      - 인스턴스 그룹: `database` (MySQL에서 생성한 DB)
   - 연결 계정 정보
      - ID: `admin`
      - PW: `admin1234`
      - `연결 테스트` 클릭 (연결 테스트 완료 후에 생성 가능)
4. 생성 버튼 클릭


## 3. Data Query 실습
### 1. 쿼리 결과 저장 위치 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Query > 쿼리 편집기
2. 설정 탭 클릭 
   - `관리` 버튼 클릭
      - 버킷: `data-query-result`
      - 상세 경로(선택): `없음`

- **Note**: 예상 파일 저장 형식
  
  ```
  {버킷 이름}/{하위 상세 경로}/{YYYY}/{MM}/{DD}/{쿼리 ID}.csv
  {버킷 이름}/{하위 상세 경로}/{YYYY}/{MM}/{DD}/{쿼리 ID}.metadata
  ```

### 2. 쿼리 실습
1. `편집기` 탭 클릭
2. 편집기 설정 정보 확인하며 실습 진행
   - **Note**: 더 다양한 쿼리문은 아래 링크 참고
   - https://fantasy-brand-461.notion.site/19adbb08775280979a70d7d671c03a1e?pvs=4
     

3. 월 별 요청 분석(ALB Access Log)
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `dc_database`
   #### **lab4-1-1**
   ```
   SELECT
      SUBSTRING(time, 1, 7) AS request_time,
      COUNT(*) AS total_requests,
      COUNT(CASE WHEN target_status_code = '200' THEN 1 END) AS success_requests,
      COUNT(CASE WHEN target_status_code <> '200' THEN 1 END) AS error_requests
   FROM alb_data
   GROUP BY SUBSTRING(time, 1, 7)
   ORDER BY SUBSTRING(time, 1, 7);
   ```
   ![Image](https://github.com/user-attachments/assets/5fd20908-dc5b-4560-843f-ec762896b956)
---

4. HTTP 상태 코드 분포(ALB Access Log)
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `dc_database`
   #### **lab4-1-2-1**
   ```
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
   ![Image](https://github.com/user-attachments/assets/c65cb408-a313-490e-bf64-edf978b1f44b)

---
5.  HTTP 상태 코드 분포(NGINX Log)
      - 데이터 원본: `data_catalog`
      - 데이터 베이스: `dc_database`
      #### **lab4-1-2-2**
      ```
      SELECT 
         status,
         COUNT(*) AS code_count,
         ROUND(COUNT(*) * 100.0 / total.total_count, 2) AS percentage
      FROM kafka_data
      CROSS JOIN (
         SELECT COUNT(*) AS total_count
         FROM kafka_data
      ) AS total
      GROUP BY status, total.total_count
      ORDER BY status; 
      ```
      ![Image](https://github.com/user-attachments/assets/875aa029-90c6-4644-9d50-da5859a4be0a)
---
6. HTTP 성공 에러 분포(ALB Access Log + NGINX Log)
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `dc_database`
   #### **lab4-1-2-3**
   ```
   WITH alb_stats AS (
      SELECT 
         COUNT(*) AS total_alb,
         COUNT(CASE WHEN target_status_code LIKE '4%' THEN 1 END) AS error_alb
      FROM alb_data
   ),
   nginx_stats AS (
      SELECT 
         COUNT(*) AS total_nginx,
         COUNT(CASE WHEN status LIKE '4%' THEN 1 END) AS error_nginx
      FROM kafka_data
   )
   SELECT 
      total_alb + total_nginx AS total_count,
      (total_alb + total_nginx) - (error_alb + error_nginx) AS total_success_count,
      error_alb + error_nginx AS total_error_count,
      ROUND(((total_alb + total_nginx) - (error_alb + error_nginx)) * 100.0 / (total_alb + total_nginx), 2) AS total_success_percentage,
      ROUND((error_alb + error_nginx) * 100.0 / (total_alb + total_nginx), 2) AS total_error_percentage
   FROM alb_stats, nginx_stats;
   ```
   ![Image](https://github.com/user-attachments/assets/12e28c1b-a215-4beb-a078-4dddc6489573)

---
7. 인기 상품 클릭 수(NGINX Log)
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `dc_database`
   #### **lab4-1-3-1**
   ```
   SELECT 
      regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
      COUNT(*) AS click_count
   FROM kafka_data
   WHERE endpoint = '/product'
   GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
   ORDER BY click_count DESC;
   ```
   ![Image](https://github.com/user-attachments/assets/1af8302f-a7f7-4f74-b13d-3cbdee723af5)
---

8. 인기 상품 클릭 수(NGINX Log + MySQL)
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `dc_database`
   #### **lab4-1-3-2**
   ```
   SELECT 
      pc.product_id,
      p.name,
      pc.click_count
   FROM (
      SELECT 
         regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
         COUNT(*) AS click_count
      FROM kafka_data
      WHERE endpoint = '/product'
      GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
   ) AS pc
   JOIN data_origin.shopdb.products AS p
      ON pc.product_id = p.id
   ORDER BY pc.click_count DESC;
   ```
   ![Image](https://github.com/user-attachments/assets/7f469340-443d-4ad7-b9b9-63f7b19bcfcf)
---


9. 신규 사용자 수(MySQL)
   - 데이터 원본: `data_orign`
   - 데이터 베이스: `shopdb`
   #### **lab4-1-4**
   ```
   SELECT 
      COUNT(DISTINCT user_id) AS new_users
   FROM users_logs
   WHERE event_type = 'CREATED'
   AND event_time BETWEEN TIMESTAMP '2025-02-14 00:00:00'
      AND TIMESTAMP '2025-02-14 23:59:59';
   ```
   ![Image](https://github.com/user-attachments/assets/8016af05-788b-4548-8a60-a47aeae6aff4)


## 4. 테이블 파티션 생성 실습
1. `kafka_nginx_db` 테이블 데이터 조회로 NGINX 로그 존재 확인
   - 데이터 원본: `data_origin`
   - 데이터베이스: `kafka_nginx_db`
   - `kafka_nginx_raw` 테이블 우측 `⋮` 버튼 클릭
   - 테이블 미리보기 버튼 클릭
   - 쿼리 결과 탭에서 쿼리 결과로 산출된 NGINX 로그 확인
2. 쿼리 입력란 상단 `+` 버튼 클릭
3. 아래 쿼리를 입력하여 `kafka_nginx_raw` 테이블을 status 컬럼을 기준으로 파티션을 나누어 저장하는 새 파티션 테이블 생성
   ```
   CREATE TABLE kafka_nginx_db.kafka_nginx_partitioned
   WITH (
     format = 'JSON',
     external_location = 's3a://kafka-nginx-lys/dc-table/partitioned',
     partitioned_by = ARRAY['status']
   )
   AS
   SELECT
     request,
     method,
     session_id,
     endpoint,
     http_referer,
     query_params,
     timestamp,
     status
   FROM kafka_nginx_db.kafka_nginx_raw;
   ```
   - 형식 설명
      ```
      -- (1) 새로운 테이블 생성 선언
      CREATE TABLE {Data Catalog 데이터베이스명}.{생성할 Data Catalog 테이블명}
      
      -- (2) 테이블 속성 지정
      WITH (
        format = 'JSON',                          -- 파일 형식을 JSON으로 설정
        external_location = 's3a://{Data Catalog에서 설정한 버킷/경로}/{생성할 디렉터리명}',
        -- ↑ 실제 버킷의 경로로, 테이블 데이터가 저장됨
        --   'external_location'을 지정으로 카카오클라우드가 지원하는 Data Catalog 테이블을 External 타입으로 다룸
        
        partitioned_by = ARRAY['status']
        -- ↑ 'status' 컬럼을 기준으로 파티션 생성
      )
      
      AS
      SELECT
        request,
        method,
        session_id,
        endpoint,
        http_referer,
        query_params,
        timestamp,
        status
      -- ↑ 원본 테이블에서 가져올 컬럼들
      
      FROM {Data Catalog 데이터베이스명}.{원본 Data Catalog 테이블명};
      -- ↑ 기존 테이블에서 데이터를 읽어와 새 파티션 테이블에 한 번에 적재
      ```

4. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 카탈로그
5. `kafka_nginx_partitioned` 테이블 클릭
6. 파티션 탭 클릭
7. `status` 값에 따라 생성된 파티션 확인
8. 각 `status` 값 우측 파일 보기 클릭
9. 파티션에 따라 External 타입으로 저장된 NGINX 로그 데이터 확인
