# Data Query 가이드

## 1. Object Storage 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 일반 버킷
2. 권한 설정
   - data-query-result 클릭
   - 권한 클릭
   - 역할 추가 버튼 클릭
   - 역할 추가
      - 사용자 계정: `없음`
      - 서비스 계정: `{프로젝트 이름}@data-query.kc.serviceaccount.com`
      - 역할: `스토리지 편집자`
3. `kafka-nginx-log`, `alb_data` 버킷도 동일하게 권한 설정 진행

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
     
  
3. 신규 사용자 수 (New Users)
   - 데이터 원본: `data_orign`
   - 데이터 베이스: `shopdb`
   #### **lab4-1-1**
   ```
   SELECT 
      COUNT(DISTINCT user_id) AS new_users
   FROM users_logs
   WHERE event_type = 'CREATED'
   AND event_time BETWEEN TIMESTAMP '2025-02-14 00:00:00'
      AND TIMESTAMP '2025-02-14 23:59:59';
   ```
   ![Image](https://github.com/user-attachments/assets/8016af05-788b-4548-8a60-a47aeae6aff4)

4. 인기 상품 클릭 수 (Product Clicks)
   - 데이터 원본: `kafka_data`
   - 데이터 베이스: `dc_database`
   #### **lab4-1-2**
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
   ![Image](https://github.com/user-attachments/assets/0aec3dc0-a9ba-4a3b-b0ab-6a82c34e8aa0)

5. 카테고리별 페이지뷰 수 (Page Views by Category)
   - 데이터 원본: `kafka_data`
   - 데이터 베이스: `dc_database`
   #### **lab4-1-3**
   ```
   SELECT
      regexp_extract(query_params, 'name=([^&]+)', 1) AS category,
      COUNT(*) AS pageview_count
   FROM data_catalog.dc_database.kafka_data
   WHERE endpoint = '/category'
   GROUP BY regexp_extract(query_params, 'name=([^&]+)', 1)
   ORDER BY pageview_count DESC;
   ```
   ![Image](https://github.com/user-attachments/assets/15df43b4-7c0f-4be3-bd97-299624e095b1)

---
