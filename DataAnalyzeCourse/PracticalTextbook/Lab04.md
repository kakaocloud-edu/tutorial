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
   - 왼쪽의 일반 버킷 클릭
   - `alb_log` 버킷 클릭 
      - 권한 버튼 클릭
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
2. 설정 클릭
   
   - 쿼리 결과 저장 위치
   - `관리` 클릭
      - 버킷: `data-query-result`
      - 상세 경로(선택): `없음`

- **Note**: 예상 파일 저장 형식
  
  ```
  {버킷 이름}/{하위 상세 경로}/{YYYY}/{MM}/{DD}/{쿼리 ID}.csv
  {버킷 이름}/{하위 상세 경로}/{YYYY}/{MM}/{DD}/{쿼리 ID}.metadata
  ```

### 2. 쿼리 실습
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Query > 쿼리 편집기
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
   FROM data_catalog.dc_database.kafka_data
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
      FROM data_catalog.dc_database.kafka_data
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

