# Hadoop Eco의 Hive로 aggregated 테이블 생성 및 데이터 적재 과정

Hadoop Eco의 Hive를 활용하여 이미 만들어진 Nginx 로그 데이터 테이블과 MySQL 데이터 테이블을 사용하여 Aggregated 테이블을 생성합니다.

---
## 1. Hadoop-Eco 마스터 노드 정보 조회 (약 1분 소요)

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `HadoopMST-core-hadoop-1` 인스턴스의 기본 프라이빗 ip 복사

    <img width="1596" height="162" alt="1  mst private ip 확인" src="https://github.com/user-attachments/assets/e4e8b0b8-3b30-42fa-ac67-4b8ff9f4c600" />

## 2. Hive에서 aggregated_logs 테이블 생성 (약 5분 소요)

1. 사용하던 `HadoopMST-hadoop-eco-1`에서 Hive에 접속

    #### **lab5-2-1**

    ```bash
    hive
    ```

2. aggregated_logs 테이블 생성

    - LOCATION에 `{HadoopMST-hadoop-eco-1 private ip주소}` 개인 환경에 맞게 수정
    - **Note**: 8020번 포트는 Hadoop의 HDFS의 RPC 통신 포트

    #### **lab5-2-2**

    ```bash
    CREATE TABLE IF NOT EXISTS aggregated_logs (
      session_id         STRING,
      user_id            STRING,
      product_id         STRING,
      event_type         STRING,
      event_count        INT,
      total_request_time DOUBLE,
      last_active_time   STRING,
      success_status     INT
    )
    STORED AS PARQUET
    LOCATION 'hdfs://{HadoopMST-hadoop-eco-1 private ip주소}:8020/apps/hive/warehouse/aggregated_logs/';
    ```

3. 파티션 설정 및 jar 등록

    - Hive 메타스토어에 저장된 테이블 정보를 Hadoop Eco와 공유해주는 HCatalog 코어 라이브러리 추가 

    #### **lab5-2-3**

    ```bash
    ADD JAR /opt/apache-hive-3.1.3-bin/lib/hive-hcatalog-core-3.1.3.jar;
    ```

4. aggregated_logs 테이블에 데이터 적재

    #### **lab5-2-4**
    > - Nginx 웹로그와 MySQL 주문 데이터를 통합하여, 사용자별·상품별로 페이지 조회 및 주문 활동을 한눈에 볼 수 있는 요약 테이블(aggregated_logs) 을 생성
    > - 사용자 요약 테이블이라고 볼 수 있음
    > - 데이터 한 줄(row)은 바로 “하나의 세션(session)에서 특정 상품(product)에 대해 사용자가 어떤 행동을 했는가”를 요약한 기록
    ```bash
    INSERT OVERWRITE TABLE aggregated_logs
    SELECT
      COALESCE(NULLIF(t.session_id, ''), 'anonymous') AS session_id,
      COALESCE(NULLIF(t.user_id,    ''), 'guest')     AS user_id,
      COALESCE(NULLIF(t.product_id, ''), 'NULL')      AS product_id,
    
      CASE WHEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END) > 0
           THEN 'order'
           ELSE 'pageview'
      END                                             AS event_type,
    
      CASE WHEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END) > 0
           THEN SUM(CASE WHEN t.src='order' THEN 1 ELSE 0 END)
           ELSE SUM(CASE WHEN t.src='pageview' THEN 1 ELSE 0 END)
      END                                             AS event_count,
    
      ROUND(SUM(t.request_time), 3)                  AS total_request_time,
    
      DATE_FORMAT(MAX(t.log_ts), 'yyyy-MM-dd HH:mm:ss') AS last_active_time,
    
      SUM(
        CASE WHEN t.status = 200 THEN 1 ELSE 0 END
      )                                             AS success_count
    
    FROM (
      SELECT
        n.session_id,
        n.user_id,
        CAST(n.product_id AS STRING)           AS product_id,
        'pageview'                             AS src,
        CAST(n.request_time.member1 AS DOUBLE) AS request_time,
        CAST(n.`timestamp` AS TIMESTAMP)       AS log_ts,
        n.status.member1                       AS status
      FROM external_nginx_log n
      WHERE n.product_id IS NOT NULL
    
      UNION ALL
    
      SELECT DISTINCT
        o.after.session_id                     AS session_id,
        o.after.user_id                        AS user_id,
        CAST(o.after.product_id AS STRING)     AS product_id,
        'order'                                AS src,
        0.0                                    AS request_time,
        CAST(from_unixtime(o.after.order_time DIV 1000000) AS TIMESTAMP) AS log_ts,
        200                                    AS status
      FROM mysql_orders o
      JOIN external_nginx_log n
        ON o.after.session_id = n.session_id
       AND CAST(o.after.product_id AS STRING) = CAST(n.product_id AS STRING)
    ) t
    WHERE
      COALESCE(NULLIF(t.session_id, ''), 'anonymous') <> 'anonymous'
      AND t.product_id       IS NOT NULL
      AND t.product_id <> ''
      AND t.product_id <> 'NULL'
    GROUP BY t.session_id, t.user_id, t.product_id;
    ```
    > - session_id: 사용자의 방문 세션을 식별하는 고유 ID (브라우저·앱 단위의 접속 식별자)
    > - user_id: 사용자를 구분하는 ID (user_xxx는 로그인 사용자, guest는 비로그인 방문자)
    > - product_id: 사용자가 조회하거나 구매한 상품의 고유 식별 번호
    > - event_type: 사용자의 행동 유형 (pageview = 상품 조회, order = 주문 발생)
    > - event_count: 해당 세션과 상품 조합에서 발생한 이벤트 횟수
    > - total_request_time: 해당 상품 관련 요청의 총 처리 시간(초 단위)
    > - last_active_time: 해당 세션에서 마지막으로 활동한 시각 (가장 최근 로그 타임스탬프)
    > - success_count: 성공적으로 처리된 요청의 개수 (HTTP 200 응답 수)
    
5. aggregated_logs 테이블에 적재된 데이터 결과 확인

    #### **lab5-2-5**

    ```bash
    select * from aggregated_logs limit 10;
    ```

    - 아래와 같은 형식의 내용 확인
   
    ![aggregated_logs 확인](https://github.com/user-attachments/assets/971fac03-b72e-47e2-b8e4-6e9bde95205b)

6. 생성한 테이블 목록 확인

    #### **lab5-2-6**

    ```bash
    show tables;
    ```

    - 아래와 같은 형식의 내용 확인
  
    <img width="637" height="299" alt="show tables" src="https://github.com/user-attachments/assets/8f546a49-c47b-4c46-83b1-82c20def85ff" />

7. aggregated_logs 테이블의 정보 조회

    #### **lab5-2-7**

    ```bash
    SHOW CREATE TABLE aggregated_logs;
    ```

    - 아래와 같은 형식의 내용 확인

    <img width="1094" height="603" alt="aggregated_logs 테이블 정보 확인" src="https://github.com/user-attachments/assets/738a56d9-a985-4c07-ba12-1aa20a8fc23c" />

8. Hadoop Eco의 HDFS 경로 확인

    - **Note**: HDFS는 원시 형태의 다양한 데이터를 저장해두는 분산 스토리지 계층이자 데이터 레이크이다.
    - `HDFS 경로` 복사 후 클립보드 등에 붙여넣기

    #### **lab5-2-8**

    ```bash
    SET hive.metastore.warehouse.dir;
    ```

    - 아래와 같은 형식의 내용 확인

    ![hive에서 hdfs 경로 확인](https://github.com/user-attachments/assets/5f3fd033-491c-461e-a283-4d8ee892e1c8)

9. `ctrl` + `c`로 종료

10. Hadoop Eco의 HDFS에 생성된 aggregated_logs 테이블 확인

    - 개개인의 HDFS 경로로 `{hive.metastore.warehouse.dir}` 수정

    #### **lab5-2-10**

    ```bash
    hdfs dfs -ls {hive.metastore.warehouse.dir}
    ```

    - 아래와 같은 형식의 내용 확인

    <img width="1500" height="73" alt="Image" src="https://github.com/user-attachments/assets/8770eb63-5550-497a-a596-bf26b25edd8e" />
