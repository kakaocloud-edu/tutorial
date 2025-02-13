# Data Query 가이드

## 1. Object Storage 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 일반 버킷
2. 권한 설정
   1. data-query-result 클릭
   2. 권한 클릭
   3. 역할 추가 클릭
   4. 역할 추가
      - 서비스 계정: `{프로젝트 이름}@data-query.kc.serviceaccount.com`
      - 역할: `스토리지 편집자`


## 2. 데이터 원본 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Query > 데이터 원본 관리
2. 데이터 원본 생성 클릭

   - 기본 정보
   	- 데이터 원본 이름: `data_origin`
   	- 설명(선택): `없음`
   - 상세 정보
   	- 데이터 원본 유형: `MySQL`
   	- 인스턴스 그룹: `data_catalog` (data catalog에서 생성한 DB)
   - 연결 계정 정보
   	- ID: `admin`
   	- PW: `admin1234'
   	- 연결 테스트 버튼 클릭 (연결 테스트 완료 후에 생성 가능)
   
3. 생성 버튼 클릭


## 3. Data Query 실습
### 1. 쿼리 결과 저장 위치 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Query > 쿼리 편집기
2. 설정 클릭
   
   - 쿼리 결과 저장 위치
   - 관리 버튼 클릭
	- 버킷: `data-query-result`
 	- 상세 경로(선택): `없음`

- **Note**: 예상 파일 저장 형식
  
  ```
  {버킷 이름}/{하위 상세 경로}/{YYYY}/{MM}/{DD}/{쿼리 ID}.csv
  {버킷 이름}/{하위 상세 경로}/{YYYY}/{MM}/{DD}/{쿼리 ID}.metadata
  ```

### 2. 쿼리 실습
1. 콘솔 -> Analytics -> Data Query -> 쿼리 편집기
2. 편집기 설정 정보 확인하며 실습 진행
  
3. 시간당 PV(페이지 뷰) count 쿼리
   - 데이터 원본: `data_orign`
   - 데이터 베이스: `shopdb`
   ```
   SELECT
    DATE_FORMAT(searched_at, '%Y-%m-%d %H:00:00') AS hour,
    COUNT(*) AS pv_count
   FROM
       search_logs
   GROUP BY
       DATE_FORMAT(searched_at, '%Y-%m-%d %H:00:00')
   ORDER BY
     hour DESC;
   ```
   ![image](https://github.com/user-attachments/assets/7cfcdc3b-dc3f-47b9-a400-9c7212846f96)
</br>


5. 세션 쿠키(session_id) 기반 방문자 수 추출
   - 데이터 원본: `data_orign`
   - 데이터 베이스: `shopdb`
    ```
    SELECT
        session_id,
        COUNT(DISTINCT user_id) AS visitors_count
    FROM
        sessions
    WHERE
        login_time IS NOT NULL
    GROUP BY
        session_id
    ORDER BY
        visitors_count DESC;
    ```
    ![image](https://github.com/user-attachments/assets/417766ba-bca4-4214-b31a-e1210b9caead)
</br>

7. 상품 상세 페이지 접근 로그를 집계하여 인기 상품 상위 5개 추출
   - 데이터 원본: `data_catalog`
   ```
	 WITH parsed AS (
	   SELECT 
	     endpoint,
	     query_params,
	     CAST(status AS integer) AS status_int
	   FROM db3_lsh.partition_test
	   WHERE endpoint = '/search'
	 ),
	 extracted AS (
	   SELECT 
	     endpoint,
	     -- query_params가 "query=Bluetooth"와 같은 형식일 때, 정규식을 통해 "Bluetooth"만 추출
	     regexp_extract(query_params, 'query=([^&]+)', 1) AS search_term,
	     status_int
	   FROM parsed
	 )
	 SELECT 
	   endpoint,
	   search_term AS subcategory,
	   COUNT(*) AS total;
	
	 FROM extracted
	 GROUP BY endpoint, search_term
	 ORDER BY total DESC
	 LIMIT 5;
    ```
   ![image](https://github.com/user-attachments/assets/e3024c3d-bc9f-47a9-8437-9a168c7cc34b)
</br>


8. HTTP status code별 count로 에러율 추출
   - 데이터 원본: `data_catalog`
   - subcategory는 제외한 상태
    ```
	WITH parsed AS (
	  SELECT 
	    endpoint,
	    request,
	    CAST(status AS integer) AS status_int
	  FROM db3_lsh.partition_test
	),
	extracted AS (
	  SELECT 
	    endpoint,
	    -- /search인 경우, request에서 ?query= 이후의 값을 추출하여 subcategory로 사용하고, 아니면 '-'로 처리
	    CASE 
	      WHEN endpoint = '/search'
	      THEN regexp_extract(request, '^(?:GET|POST|PUT|DELETE)\\s+[^\\s\\?]+\\?query=([^\\s]+)', 1)
	      ELSE '-' 
	    END AS subcategory,
	    status_int
	  FROM parsed
	)
	SELECT 
	  endpoint,
	  subcategory,
	  COUNT(*) AS total,
	  SUM(CASE WHEN status_int >= 400 THEN 1 ELSE 0 END) AS error_count,
	  ROUND(SUM(CASE WHEN status_int >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate_percentage
	FROM extracted
	GROUP BY endpoint, subcategory
	ORDER BY endpoint;

    ```
    ![image](https://github.com/user-attachments/assets/c4594cd2-9572-44db-8634-c1e174d4a2d6)
