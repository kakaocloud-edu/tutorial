# Data Query 실습
Data Query 기능을 활용하여 NGINX 로그 및 MySQL 데이터를 이용한 다양한 분석 쿼리 실행, 그리고 파티션 테이블 생성을 진행합니다.

---
## 1. 데이터 원본 생성
1. 카카오 클라우드 콘솔 > Analytics > Data Query
2. Data Query 서비스 시작하기
   - 시작하기 버튼 클릭
3. 데이터 원본 관리 탭 클릭
4. 데이터 원본 생성 버튼 클릭
   - 기본 정보
      - 데이터 원본 이름: `data_origin`
      - 설명(선택): 빈 칸
   - 상세 정보
      - 데이터 원본 유형: `MySQL`
      - 인스턴스 그룹: `database`
   - 연결 계정 정보
      - ID: `admin`
      - 비밀번호: `admin1234`
      - `연결 테스트` 버튼 클릭
   - 연결 성공 확인 후 생성 버튼 클릭
5. `data_origin` 데이터 원본 생성 확인
<img width="1920" height="403" alt="111" src="https://github.com/user-attachments/assets/b9ab57f4-d890-4f9c-9f74-1ffdcbc69ebf" />


## 2. Data Query 저장 위치 설정
1. 좌측 쿼리 편집기 탭 클릭
2. 설정 탭 클릭
3. 관리 버튼 클릭
   - 버킷: `data-catalog-bucket`
   - 상세 경로(선택): `data-query-result`
   - 저장 버튼 클릭
4. 쿼리 결과 저장 위치의 Object Storage 경로 확인
![image](https://github.com/user-attachments/assets/3cb7ba6b-09bc-4dc6-a3f5-7b56d77fdaae)


## 3. Data Query 실습
- **Note**: 더 많은 쿼리문은 [Lab04_etc.md](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/PracticalTextbook/Lab05_etc.md) 참고

1. `편집기` 탭 클릭
2. NGINX 로그를 활용하여 HTTP 상태 코드 분포 쿼리
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `data_catalog_database`
   - 우측 편집기의 `Query1` 탭 아래 쿼리문 입력

      #### **lab5-3-2**
      
      ```
      SELECT
         status.member1 AS http_status_code,
         COUNT(*) AS code_count,
         ROUND(COUNT(*) * 100.0 / total.total_count, 2) AS percentage
      FROM
         data_catalog.data_catalog_database.kafka_log_table
      CROSS JOIN (
         SELECT
            COUNT(*) AS total_count
         FROM
            data_catalog.data_catalog_database.kafka_log_table
      ) AS total
      GROUP BY
         status.member1, total.total_count
      ORDER BY
         http_status_code;
      ```
   - 쿼리 결과 탭에서 HTTP 상태 코드 분포 확인
      <img width="981" alt="HTTP 상태 분포" src="https://github.com/user-attachments/assets/d904ba19-bf52-4733-8c6d-b8821da1894c" />


3. NGINX 로그를 활용하여 인기 상품 클릭 수 쿼리
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `data_catalog_database`
   - 우측 편집기의 `+` 버튼 클릭
   - 추가된 `Query2` 탭 아래 쿼리문 입력
   
      #### **lab5-3-3**
      endpoint가 /product인 로그들 중에서, query_params 안에 있는 상품 ID를 뽑아(product_id), 같은 상품끼리 묶어서 몇 번 클릭되었는지(click_count)를 세고, 클릭 수가 많은 순서대로 정렬
      ```
      SELECT 
         regexp_extract(query_params, 'id=([0-9]+)', 1) AS product_id,
         COUNT(*) AS click_count
      FROM data_catalog.data_catalog_database.kafka_log_table
      WHERE endpoint = '/product'
      GROUP BY regexp_extract(query_params, 'id=([0-9]+)', 1)
      ORDER BY click_count DESC;
      ```
   - 쿼리 결과 탭에서 인기 상품 클릭 수 확인
      ![image](https://github.com/user-attachments/assets/eee3ee7e-f397-45cf-8ed3-90ccb80bf531)

4. NGINX 로그와 MySQL 데이터를 활용하여 인기 상품 클릭 수 쿼리
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `data_catalog_database`
   - 우측 편집기의 `+` 버튼 클릭
   - 추가된 `Query3` 탭 아래 쿼리문 입력
   
      #### **lab5-3-4**
      로그 테이블(kafka_log_table)에서 상품별 클릭 수를 계산하고, 그 상품 ID를 이용해서 상품 이름(products 테이블) 과 연결(join)해 어떤 상품이 몇 번 클릭되었는지를 보여주는 쿼리
      ```
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
   - 쿼리 결과 탭에서 Lab2-3-3의 NGINX 로그만 활용할 때보다 인기 상품 클릭 수에 대한 더 많은 정보 확인 가능함을 확인
   ![image](https://github.com/user-attachments/assets/d83ac4aa-2fc0-4b02-9618-bd715ab69549)



6. MySQL 데이터를 활용하여 신규 사용자 수 쿼리
   - 데이터 원본: `data_orign`
   - 데이터 베이스: `shopdb`
   - 우측 편집기의 `+` 버튼 클릭
   - 추가된 `Query4` 탭 아래 쿼리문 입력

      #### **lab5-3-5**
      새로 가입한 사용자 수(new users)가 몇 명인지 세는 쿼리
      ```
      SELECT 
         COUNT(DISTINCT user_id) AS new_users
      FROM data_origin.shopdb.users_logs
      WHERE event_type = 'CREATED';
      ```
   - 쿼리 결과 탭에서 신규 사용자 수 확인
   ![image](https://github.com/user-attachments/assets/b9f095a5-9746-4fdf-9219-e16ab7fd845b)


## 4. 테이블 파티션 생성 실습
1. Data Query를 활용하여 테이블 파티션 생성
   - 데이터 원본: `data_catalog`
   - 데이터 베이스: `data_catalog_database`
   - 우측 편집기의 `+` 버튼 클릭
   - 추가된 `Query5` 탭 아래 쿼리문 입력

   #### **lab5-4-1**

   ```
   CREATE TABLE data_catalog_database.kafka_log_partitioned
   WITH (
     format = 'JSON',
     external_location = 's3a://data-catalog-bucket/data-catalog-dir/tables/partitioned',
     partitioned_by = ARRAY['status_code']
   )
   AS
   SELECT
     endpoint,
     query_params,
     status.member1   AS status_code
   FROM data_catalog_database.kafka_log_table;
   ```

   - 쿼리 결과 성공 확인

2. 카카오 클라우드 콘솔 > Analytics > Data Catalog
3. 좌측 테이블 탭 클릭
4. `kafka_log_partitioned` 테이블 생성 확인 후 클릭
   ![19](https://github.com/user-attachments/assets/4e36de9a-cbac-41ad-a244-4e95808941f1)

5. 파티션 탭 클릭
6. `status` 값에 따라 생성된 파티션 확인
   ![22](https://github.com/user-attachments/assets/680e8b72-f57f-48a7-ba8e-dbad91448956)

7. 각 `status` 값 우측 파일 보기 클릭
8. 파티션에 따라 External 타입으로 저장된 NGINX 로그 데이터 확인
   ![20](https://github.com/user-attachments/assets/d165180c-fa32-410b-abe7-962ee0d1b15f)
