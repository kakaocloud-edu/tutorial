# Spark-MySQL 데이터 마트 구축

Hadoop Eco의 Spark를 활용하여 이미 만들어진 aggregated_logs 테이블과 MySQL 데이터 테이블을 사용하여 user cart metrics temp 테이블을 생성합니다. 만들어진 user cart metrics temp 테이블을 MySQL에 적재하여 데이터 마트를 구축합니다.

---
## 1. 사용자 리소스 정보 조회
1. 카카오 클라우드 콘솔 > Data Store > MySQL
2. `database` Instance Group 클릭
3. 우측 상단의 `엔드포인트` 복사 및 클립보드 등에 붙여넣기

   ![스크린샷](https://github.com/user-attachments/assets/c5e2e829-02f1-41dc-9932-e14efddfca1c)  

## 2. Spark로 데이터 마트 테이블 생성 후 적재
1. 사용하던 `HadoopMST-hadoop-eco-1`에서 Spark 설정 파일 업데이트

   - **Note**: 지정한 입력 경로의 모든 하위 디렉토리에 있는 파일까지 읽도록 설정

   #### **lab6-2-1**

   ```bash
   echo "spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive true" | sudo tee -a /opt/spark/conf/spark-defaults.conf
   ```
2. user_cart_metrics.py 다운로드

   - 스크립트: [ `user_cart_metrics.py` ](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day2/Lab06/user_cart_metrics.py)
   - Hive에서 aggregated_logs 테이블을 Spark로 가져온 후 사용자별 장바구니·주문 메트릭을 집계하여 MySQL의 user_cart_metrics 테이블에 저장하는 Spark 스크립트입니다.

    #### **lab6-2-2**

    ```bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day2/Lab06/user_cart_metrics.py
    ```

3. user_cart_metrics.py에 실행 권한 부여

    #### **lab6-2-3**

    ```bash
    chmod +x user_cart_metrics.py
    ```

4. user_cart_metrics.py 실행

   - packages: S3와 같은 스토리지 접근에 필요한 Hadoop-AWS 모듈과 AWS SDK 라이브러리 사용
   - jars: MySQL에 데이터를 쓰기 위한 JDBC 드라이버와 Hive 메타스토어 연결을 위한 HCatalog 코어 JAR 사용

    #### **lab6-2-4**

    ```bash
   spark-submit \
     --packages org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.12.375 \
     --jars /opt/hive/lib/mysql-connector-j-8.0.33.jar,/opt/hive/lib/hive-hcatalog-core-3.1.3.jar \
     user_cart_metrics.py \
     --mysql-endpoint "$MYSQL_HOST" \
     --mysql-user admin \
     --mysql-password admin1234
    ```

    - 아래와 같은 형식의 내용 확인

    <img width="1312" height="534" alt="5  실행완료 화면" src="https://github.com/user-attachments/assets/4ff46c32-1798-414e-9ebb-03468ff05bb1" />

## 3. 데이터 마트를 이용한 Data Query 진행

1. 카카오 클라우드 콘솔 > Analytics > Data Query
2. 쿼리 편집기 탭 클릭
3. user cart metrics 테이블 10개 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `Query1` 탭 아래 쿼리문 입력

    #### **lab6-3-3**

    ```bash
    SELECT * FROM data_origin.shopdb.user_cart_metrics LIMIT 10
    ```
    
    ![쿼리1](https://github.com/user-attachments/assets/4c7ef33f-fdc5-4d58-9fe6-3ed2beb34836)

4. Top 10 사용자별 주문 횟수 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query2` 탭 아래 쿼리문 입력

    #### **lab6-3-4**

    ```bash
    SELECT
      user_id,
      order_count,
      pageview_count,
      total_request_time,
      avg_request_time,
      last_active_time
    FROM shopdb.user_cart_metrics
    ORDER BY order_count DESC
    LIMIT 10;
    ```
    
    ![쿼리2](https://github.com/user-attachments/assets/6e9e3a73-810d-4a14-bd77-526539996f23)

5. Top 10 사용자별 페이지뷰 횟수 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query3` 탭 아래 쿼리문 입력

    #### **lab6-3-5**

    ```bash
    SELECT
      user_id,
      pageview_count,
      order_count,
      total_request_time,
      avg_request_time,
      last_active_time
    FROM shopdb.user_cart_metrics
    ORDER BY pageview_count DESC
    LIMIT 10;
    ```
    
    ![쿼리3](https://github.com/user-attachments/assets/11a4d8a7-5ba0-4b15-b41c-fb5bc98e5ae8)

6. 사용자별 평균 요청 시간 상위 10명 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query4` 탭 아래 쿼리문 입력

    #### **lab6-3-6**

    ```bash
    SELECT
      user_id,
      avg_request_time,
      total_request_time,
      order_count + pageview_count AS total_events,
      last_active_time
    FROM shopdb.user_cart_metrics
    WHERE total_request_time > 0 
    ORDER BY avg_request_time DESC
    LIMIT 10;
    ```
    
    ![쿼리4](https://github.com/user-attachments/assets/6121261c-486f-45ee-b3dc-8c19489c00b2)

7. 특정 기간에 마지막 활동이 있었던 사용자 조회
    - 데이터 원본: `data_origin`
    - 데이터베이스: `shopdb`
    - 우측 편집기의 `+` 버튼 클릭
    - 우측 편집기의 `Query5` 탭 아래 쿼리문 입력
    - `WHERE last_active_time LIKE 'YYYY-MM-DD%'` 에서 `'YYYY-MM-DD%'`부분 실습 날짜로 변경
    - ex) `'2025-01-01%'`

    #### **lab6-3-7**

    ```bash
    SELECT
      user_id,
      order_count,
      pageview_count,
      total_request_time,
      avg_request_time,
      last_active_time
    FROM shopdb.user_cart_metrics
    WHERE last_active_time LIKE 'YYYY-MM-DD%'
    ORDER BY last_active_time DESC;
    ```

    ![쿼리5](https://github.com/user-attachments/assets/b593cefb-49e3-41c1-9f2b-148be17bbf39)





