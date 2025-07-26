## 실시간 분석 대시보드 구축

Kafka로 들어오는 데이터를 Druid에서 실시간으로 수집 및 가공하고, Superset을 통해 분석 결과를 시각화하여 대시보드를 만드는 실습입니다.

## 1. Druid 확장 설정

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `api-server-1` 인스턴스 SSH 접속
    - `api-server-1` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력
    
    #### lab3-1-2-1
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우 아래와 같이 키페어 권한 조정
    
    #### lab3-1-2-2
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### lab3-1-2-3
    
    ```bash
    ssh -i keypair.pem ubuntu@{api-server-1의 public ip 주소}
    ```
    
    - **Note**: {api-server-1의 public ip 주소} 부분을 복사한 각 IP 주소로 교체
    
    #### lab3-1-2-4
    
    ```bash
    yes
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우, cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 실행
    
    #### lab3-1-2-5
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```
    
3. 마스터, 워커 노드(`HadoopMST-hadoop-eco-1`, `HadoopWRK-hadoop-eco-1, 2`)에 각각 Public IP 연결
    - 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭
4. 마스터, 워커 노드(`HadoopMST-hadoop-eco-1`, `HadoopWRK-hadoop-eco-1, 2`)에 SSH 접속
    - 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력
    
    #### lab3-1-4-1
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우 아래와 같이 키페어 권한 조정
    
    #### lab3-1-4-2
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### lab3-1-4-3
    
    ```bash
    ssh -i keypair.pem ubuntu@{마스터 또는 워커 노드의 public ip 주소}
    ```
    
    - **Note**: {마스터 또는 워커 노드의 public ip 주소} 부분을 복사한 각 IP 주소로 교체
    
    #### lab3-1-4-4
    
    ```bash
    yes
    ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우, cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 실행
    
    #### lab3-1-4-5
    
    ```bash
    icacls.exe keypair.pem /reset
    icacls.exe keypair.pem /grant:r %username%:(R)
    icacls.exe keypair.pem /inheritance:r
    ```
    
5. Druid 확장 모듈 목록 확인

    #### lab3-1-5

    ```bash
    ls -l /opt/apache-druid-25.0.0/extensions/
    ```
    ![image](https://github.com/user-attachments/assets/70e24570-32d5-4acb-bcd0-1fcc3e4f8f50)


6. 마스터, 워커 노드 모두에서 Druid 설정 파일에서 druid.extensions.loadList 값 추가

    #### lab3-1-6

    ```bash
    sudo sed -i 's|druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions", "druid-parquet-extensions", "mysql-metadata-storage", "druid-hdfs-storage", "druid-kafka-indexing-service", "druid-datasketches", "druid-multi-stage-query"]|' /opt/apache-druid-25.0.0/conf/druid/cluster/_common/common.runtime.properties && \
    sudo sed -i 's|druid.extensions.loadList=.*|druid.extensions.loadList=["druid-avro-extensions", "druid-hdfs-storage", "druid-kafka-indexing-service", "druid-datasketches", "druid-multi-stage-query"]|' /opt/apache-druid-25.0.0/conf/druid/auto/_common/common.runtime.properties
    ```
    
7. 마스터, 워커 노드 모두에서 Druid 관련 서비스 재시작

    #### lab3-1-7

    ```bash
    sudo systemctl restart 'druid-*'
    ```


## 2. **Druid를 활용한 데이터 수집 및 가공**

1. 마스터 노드(`HadoopMST-hadoop-eco-1`)의 Public IP를 이용하여 웹 브라우저에서 Druid에 접속

    #### lab3-2-1
 
    ```
    http://{MASTER_NODE_PUBLIC_IP}:3008
    ```
    
    ![image](https://github.com/user-attachments/assets/b56858d8-2998-4e10-b398-59c61f1ac0f4)

    
2. `data-stream-vm`의 Public IP 복사 후 메모장에 붙여넣기
3. 카카오 클라우드 콘솔 > Advanced Managed Kafka > 클러스터
4. `kafka` 클러스터 클릭
5. 부트스트랩 서버 복사 후 메모장에 붙여넣기
6. Load Data > Streaming > Start a new streaming spec 버튼 클릭
7. `Edit Spec` 버튼 클릭 후 아래 spec 입력
    - **Note**: Kafka 부트스트랩 서버, data-stream-vm의 Public IP를 복사해둔 값으로 변경

    #### lab3-2-7

    ```
    {
      // Ingestion 타입: Kafka 스트리밍
      "type": "kafka",
      "spec": {
        // ─────────────────────────────────────────────────
        // 1) 입력 설정
        // ─────────────────────────────────────────────────
        "ioConfig": {
          // 입력 타입
          "type": "kafka",

          "consumerProperties": {
            // Kafka 브로커 주소 (필수)
            "bootstrap.servers": "{Kafka 부트스트랩 서버}"
          },
          // 구독할 토픽 (필수)
          "topic": "nginx-topic",

          "inputFormat": {
            // 메시지 포맷 (필수)
            "type": "avro_stream",
            "avroBytesDecoder": {
              // Avro 스키마 조회 방식 (필수)
              "type": "schema_registry",
              // Schema Registry URL (필수)
              "url": "http://{data-stream-vm의 Public IP}:8081"
            }
          },

          // Earliest 오프셋부터 읽을지 여부 (선택, default=false)
          "useEarliestOffset": true
        },

        // ─────────────────────────────────────────────────
        // 2) 적재 작업의 성능, 리소스 관련 세부 설정
        // ─────────────────────────────────────────────────
        "tuningConfig": {
          // Kafka용 튜닝
          "type": "kafka"
        },

        // ─────────────────────────────────────────────────
        // 3) 적재할 데이터의 구조와 분석 기준을 정의
        // ─────────────────────────────────────────────────
        "dataSchema": {
          // Druid datasource 이름 (필수)
          "dataSource": "nginx-topic",

          "timestampSpec": {
            // 타임스탬프가 저장된 컬럼 (필수)
            "column": "timestamp",
            // 자동 포맷 감지 (선택, default="auto")
            "format": "auto"
          },

          "dimensionsSpec": {
            // Druid가 집계, 분석 시 기준으로 삼을 컬럼 목록 (선택)
            "dimensions": [
              "remote_addr",
              "request",
              {
                "name": "status",
                "type": "long"
              },
              {
                "name": "body_bytes_sent",
                "type": "long"
              },
              "http_referer",
              "session_id",
              "user_id",
              {
                "name": "request_time",
                "type": "double"
              },
              {
                "name": "upstream_response_time",
                "type": "double"
              },
              "endpoint",
              "method",
              "query_params",
              "product_id",
              "host"
            ]
          },
          "granularitySpec": {
            // 쿼리 기본 단위 (필수)
            "queryGranularity": "none",
            // 롤업 수행 여부 (필수)
            "rollup": false,
            // 세그먼트 생성 단위 (필수)
            "segmentGranularity": "all"
          }
        }
      }
    }
    ```
    
8. Parse data 버튼 클릭 후 데이터 확인
    
    ![image](https://github.com/user-attachments/assets/fadbd7ce-3df3-402d-8a8d-f07547a8efcb)

    
9. `Edit Spec` 버튼 클릭 후 `Submit` 버튼 클릭
10. 페이지 새로고침 후 nginx-topic Supervisors, Task의 Status가 RUNNING인 것을 확인
    
    ![image](https://github.com/user-attachments/assets/813bde00-86a7-40cd-bc31-6cb120911830)

    
11. Load Data > Streaming > Start a new streaming spec 버튼 클릭        
12. `Edit Spec` 버튼 클릭 후 아래 orders spec 입력

    - **Note**: Kafka 부트스트랩 서버를 복사해둔 값으로 변경

        #### lab3-2-12

        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_orders_changes",
              "timestampSpec": {
                "column": "order_time",
                "format": "micro"
              },
              "dimensionsSpec": {
                "dimensions": [
                  { "name": "order_id", "type": "string" },
                  { "name": "user_id", "type": "string" },
                  { "name": "session_id", "type": "string" },
                  { "name": "product_id", "type": "string" },
                  { "name": "price", "type": "double" },
                  { "name": "quantity", "type": "long" },
                  { "name": "order_time", "type": "timestamp" },
                  { "name": "operation_type", "type": "string" },
                  { "name": "__deleted", "type": "boolean" }
                ]
              },
              "granularitySpec": {
                "type": "uniform",
                "segmentGranularity": "all",
                "queryGranularity": "MINUTE",
                "rollup": false
              }
            },
            "tuningConfig": {
              "type": "kafka",
              "maxRowsPerSegment": 5000000,
              "maxBytesInMemory": 25000000
            },
            "ioConfig": {
              "topic": "mysql-server.shopdb.orders",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-orders"
              },
              "taskCount": 1,
              "replicas": 1,
              "taskDuration": "PT1H",
              "completionTimeout": "PT20M",
              "inputFormat": {
                "type": "json",
                "flattenSpec": {
                  "useFieldDiscovery": false,
                  "fields": [
                    {
                      "type": "jq",
                      "name": "order_id",
                      "expr": ".before.order_id // .after.order_id"
                    },
                    {
                      "type": "jq",
                      "name": "user_id",
                      "expr": ".before.user_id // .after.user_id"
                    },
                    {
                      "type": "jq",
                      "name": "session_id",
                      "expr": ".before.session_id // .after.session_id"
                    },
                    {
                      "type": "jq",
                      "name": "product_id",
                      "expr": ".before.product_id // .after.product_id"
                    },
                    {
                      "type": "jq",
                      "name": "price",
                      "expr": ".before.price // .after.price"
                    },
                    {
                      "type": "jq",
                      "name": "quantity",
                      "expr": ".before.quantity // .after.quantity"
                    },
                    {
                      "type": "jq",
                      "name": "order_time",
                      "expr": ".before.order_time // .after.order_time"
                    },
                    {
                      "type": "jq",
                      "name": "operation_type",
                      "expr": ".op"
                    },
                    {
                      "type": "jq",
                      "name": "__deleted",
                      "expr": ".op == \"d\""
                    }
                  ]
                }
              },
              "type": "kafka",
              "useEarliestOffset": true
            }
          }
        }
        ```
        
13. `Edit Spec` 버튼 클릭 후 아래 cart_logs spec 입력

    - **Note**: Kafka 부트스트랩 서버를 복사해둔 값으로 변경

        #### lab3-2-13

        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_cart_logs_changes",
              "timestampSpec": {
                "column": "event_time",
                "format": "millis"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "log_id",
                  "cart_id",
                  "session_id",
                  "user_id",
                  "product_id",
                  "old_quantity",
                  "new_quantity",
                  "price",
                  "event_type",
                  "event_time",
                  "operation_type",
                  {
                    "name": "__deleted",
                    "type": "boolean"
                  }
                ]
              },
              "granularitySpec": {
                "type": "uniform",
                "segmentGranularity": "all",
                "queryGranularity": "MINUTE",
                "rollup": false
              }
            },
            "tuningConfig": {
              "type": "kafka",
              "maxRowsPerSegment": 5000000,
              "maxBytesInMemory": 25000000
            },
            "ioConfig": {
              "topic": "mysql-server.shopdb.cart_logs",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-cart_logs"
              },
              "taskCount": 1,
              "replicas": 1,
              "taskDuration": "PT1H",
              "completionTimeout": "PT20M",
              "inputFormat": {
                "type": "json",
                "flattenSpec": {
                  "useFieldDiscovery": false,
                  "fields": [
                    {
                      "type": "jq",
                      "name": "log_id",
                      "expr": ".before.log_id // .after.log_id"
                    },
                    {
                      "type": "jq",
                      "name": "cart_id",
                      "expr": ".before.cart_id // .after.cart_id"
                    },
                    {
                      "type": "jq",
                      "name": "session_id",
                      "expr": ".before.session_id // .after.session_id"
                    },
                    {
                      "type": "jq",
                      "name": "user_id",
                      "expr": ".before.user_id // .after.user_id"
                    },
                    {
                      "type": "jq",
                      "name": "product_id",
                      "expr": ".before.product_id // .after.product_id"
                    },
                    {
                      "type": "jq",
                      "name": "old_quantity",
                      "expr": ".before.old_quantity // .after.old_quantity"
                    },
                    {
                      "type": "jq",
                      "name": "new_quantity",
                      "expr": ".before.new_quantity // .after.new_quantity"
                    },
                    {
                      "type": "jq",
                      "name": "price",
                      "expr": ".before.price // .after.price"
                    },
                    {
                      "type": "jq",
                      "name": "event_type",
                      "expr": ".before.event_type // .after.event_type"
                    },
                    {
                      "type": "jq",
                      "name": "event_time",
                      "expr": ".before.event_time // .after.event_time"
                    },
                    {
                      "type": "jq",
                      "name": "operation_type",
                      "expr": ".op"
                    },
                    {
                      "type": "jq",
                      "name": "__deleted",
                      "expr": ".op == \"d\""
                    }
                  ]
                }
              },
              "type": "kafka",
              "useEarliestOffset": true
            }
          }
        }
        ```
        
14. 페이지 새로고침 후 각 Supervisors, Task의 Status가 RUNNING인 것을 확인

## 3. **Superset을 활용한 데이터 시각화**

1. 마스터 노드(`HadoopMST-hadoop-eco-1`)의 Public IP를 이용하여 웹 브라우저에서 Superset에 접속
    
    #### lab3-3-1

    ```
    http://{MASTER_NODE_PUBLIC_IP}:4000
    ```
    
2. Dataflow 유형 클러스터 생성 시 입력한 관리자 아이디, 비밀번호를 이용하여 로그인
    - USERNAME: `admin`
    - PASSWORD: `Admin1234!`
    - SIGN IN 버튼 클릭
3. 누적 방문자 수 시각화
    - Datasets 메뉴 클릭 후 `+ DATASET` 버튼 클릭
    - DATASET 추가
        - DATABASE: `druid`
        - SCHEMA: `druid`
        - Select database table: `nginx-topic`
        - `CREATE DATASET AND CREATE CHART` 버튼 클릭
    - Big Number 차트 생성
        - Big Number 차트 선택 후 CREATE NEW CHART 버튼 클릭
        - METRICS
            - SIMPLE 탭 클릭
            - COLUMN: `session_id`
            - AGGREGATE: `COUNT`
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        <img width="1920" height="925" alt="image" src="https://github.com/user-attachments/assets/664f8f7f-3c5c-4a8b-867a-5b5e6e18c4d3" />
        
        - SAVE 버튼 클릭
        - 저장 정보 입력
            - CHAR NAME: `Big Number`
            - ADD TO DASHBOARD: `빈 칸`
        - SAVE 버튼 클릭
    - Time-series Area 차트 생성
        - TIME-SERIES AREA CHART 선택
        - TIME GRAIN: `Minute`
        - METRICS: `COUNT(session_id)` 확인
        - Advanced analytics 클릭
            - Rolling window(ROLLING FUNCTION): `cumsum`
        - UPDATE CHART 버튼 클릭
        
        <img width="1920" height="925" alt="image" src="https://github.com/user-attachments/assets/33666530-7da5-4a5d-90d0-1b81fd59e862" />

        
        - SAVE 버튼 클릭
        - 저장 정보 입력
            - CHAR NAME: `Time-series Area Chart`
            - ADD TO DASHBOARD: `빈 칸`
        - SAVE 버튼 클릭
    - Dashboards 메뉴 클릭 후 `+ DASHBOARD` 버튼 클릭
    - `[ untitled dashboard ]` 제목을 지운 후 `누적 방문자 수` 입력
    -  `Big Number`, `Time-series Area Chart`를 빈 공간에 배치
    - SAVE 버튼 클릭

4. 조회→장바구니→결제 전환률 시각화
    - SQL > SQL Lab 메뉴 클릭
    - 엔드포인트 단계별 발생 횟수 집계 쿼리 입력 후 RUN 버튼 클릭

   #### lab3-3-4

    ```
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
    - 쿼리 결과 확인
    - CREATE CHART 버튼 클릭
    - View all charts 클릭
    - Funnel Chart 검색 > Funnel Chart 선택 > SELECT 버튼 클릭
    - FUNNEL 차트 확인
    - DIMENSIONS: stage
    - METRICS
        - COLUMN: cnt
        - AGGREGATE: SUM
        - SAVE 버튼 클릭
    - UPDATE CHART 버튼 클릭
    
    <img width="1920" height="925" alt="image" src="https://github.com/user-attachments/assets/b5b6cc47-e538-4603-aefe-0ec1796dc91f" />

    - SAVE 버튼 클릭
    - 저장 정보 입력
        - CHART NAME: `조회→장바구니→결제 전환률`
        - DATASET NAME: `단계별 횟수 집계`
        - ADD TO DASHBOARD: `빈 칸`
        - SAVE 버튼 클릭
    
5. 시간대별 매출 및 성장률 시각화
    - Datasets 메뉴 클릭 후 `+ DATASET` 버튼 클릭
    - DATASET 추가
        - DATABASE: `druid`
        - SCHEMA: `druid`
        - Select database table: `shopdb_orders_changes`
        - `CREATE DATASET AND CREATE CHART` 버튼 클릭
    - Datasets 메뉴 클릭 후 `shopdb_orders_changes` Dataset 수정 버튼 클릭
    - METRICS 탭 클릭 후 `+ ADD ITEM` 버튼 클릭
    - Metric 설정 
        - Metric: `총매출`
        - SQL expression
            
            #### lab3-3-5
    
            ```bash
            SUM(price * quantity)
            ```
            
        - SAVE 버튼 클릭
        - OK 버튼 클릭
    - shopdb_orders_changes 클릭
    - Time-series Area Chart 클릭
    - TIME GRAIN: `Hour`
    - METRICS: `총매출`
    - CREATE CHART 버튼 클릭
    
    <img width="2898" height="1014" alt="Image" src="https://github.com/user-attachments/assets/b947a83f-a116-440a-b5cc-e65ed1b4fb00" />
    
    - SAVE 버튼 클릭
        - 저장 정보 입력
        - CHART NAME: `시간대별 매출 및 성장률`
        - ADD TO DASHBOARD: `빈 칸`
        - SAVE 버튼 클릭
    
6. 장바구니 행동 분석 시각화
    - Datasets 메뉴 클릭 후 `+ DATASET` 버튼 클릭
    - DATASET 추가
        - DATABASE: `druid`
        - SCHEMA: `druid`
        - Select database table: `shopdb_cart_logs_changes`
        - `CREATE DATASET AND CREATE CHART` 버튼 클릭
    - Datasets 메뉴 클릭 후 `shopdb_cart_logs_changes` Dataset 수정 버튼 클릭
    - CALCULATED COLUMNS 탭 클릭 후 `+ ADD ITEM` 버튼 클릭
    - Column 설정
        - Column: `event_type_ko`
        - SQL EXPRESSION
            
            #### lab3-3-6
    
            ```bash
            CASE
            WHEN event_type = 'ADDED'        THEN '추가'        -- 장바구니 담기
            WHEN event_type = 'UPDATED'      THEN '수정'        -- 수량/옵션 변경
            WHEN event_type = 'CHECKED_OUT'  THEN '주문완료'    -- 결제 단계 진입
            WHEN event_type = 'REMOVED'      THEN '삭제'        -- 장바구니 제거
            ELSE '기타'
            END
            ```
            
        - SAVE 버튼 클릭
        - OK 버튼 클릭
    - shopdb_cart_logs_changes 클릭
    - Time-series Line Chart 클릭
    - TIME GRAIN: `Hour`
    - METRICS
        - SIMPLE 클릭
        - COLUMN: `cart_id`
        - AGGREGATE: `COUNT`
        - SAVE 버튼 클릭
    - DIMENSIONS: `event_type_ko`
    - CREATE CHART 버튼 클릭
    
    <img width="1920" height="925" alt="image" src="https://github.com/user-attachments/assets/d5c62c6c-fd7b-4a5d-8d1f-54b72db5b332" />
    
    - SAVE 버튼 클릭
        - 저장 정보 입력
        - CHART NAME: `장바구니 행동 분석`
        - ADD TO DASHBOARD: `빈 칸`
        - SAVE 버튼 클릭
