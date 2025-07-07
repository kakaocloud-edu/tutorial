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
    
3. 마스터, 워커 노드(`HadoopMST-hadoop-dataflow-1`, `HadoopWRK-hadoop-dataflow-1, 2`)에 각각 Public IP 연결
    - 각 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭
    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭
4. 마스터, 워커 노드(`HadoopMST-hadoop-dataflow-1`, `HadoopWRK-hadoop-dataflow-1, 2`)에 SSH 접속
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

1. 마스터 노드(`HadoopMST-hadoop-dataflow-1`)의 Public IP를 이용하여 웹 브라우저에서 Druid에 접속

    #### lab3-2-1
 
    ```
    http://${MASTER_NODE_PUBLIC_IP}:3008
    ```
    
    ![image](https://github.com/user-attachments/assets/b56858d8-2998-4e10-b398-59c61f1ac0f4)

    
2. `api-server-1`의 Public IP 복사 후 메모장에 붙여넣기
3. 카카오 클라우드 콘솔 > Advanced Managed Kafka > 클러스터
4. `kafka` 클러스터 클릭
5. 부트스트랩 서버 복사 후 메모장에 붙여넣기
6. Load Data > Streaming > Start a new streaming spec 버튼 클릭
7. `Edit Spec` 버튼 클릭 후 아래 spec 입력
    - **Note**: Kafka 부트스트랩 서버, api-server-1의 Public IP를 복사해둔 값으로 변경

    #### lab3-2-7

    ```bash
    {
      // Ingestion 유형
      "type": "kafka",
      "spec": {
        // ─────────────────────────────────────────────────
        // 1) 어디에서, 어떻게 데이터를 읽을지 지정
        // ─────────────────────────────────────────────────
        "ioConfig": {
          // 입력 유형
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
              "url": "http://{api-server-1의 Public IP}:8081"
            }
          },
    
          // Earliest 오프셋부터 읽을지 여부 (선택, default=false)
          "useEarliestOffset": false
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
              "gender",
              "method",
              {
                "type": "long",
                "name": "body_bytes_sent"
              },
              "session_id",
              "http_user_agent",
              "x_forwarded_for",
              "endpoint",
              {
                "type": "double",
                "name": "request_time"
              },
              "request_body",
              "user_id",
              "http_referer",
              "query_params",
              "product_id",
              "host",
              {
                "type": "double",
                "name": "upstream_response_time"
              },
              "category",
              "age",
              {
                "type": "long",
                "name": "status"
              }
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
12. `Edit Spec` 버튼 클릭 후 아래 spec 입력
    - **Note**: Kafka 부트스트랩 서버를 복사해둔 값으로 변경
    - users

        #### lab3-2-12-1
        
        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_users_changes",
              "timestampSpec": {
                "column": "updated_at",
                "format": "micro"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "user_id",
                  "name",
                  "email",
                  "gender",
                  "age",
                  "updated_at",
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
              "topic": "mysql-server.shopdb.users",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-users"
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
                      "name": "user_id",
                      "expr": ".before.user_id // .after.user_id"
                    },
                    {
                      "type": "jq",
                      "name": "name",
                      "expr": ".before.name // .after.name"
                    },
                    {
                      "type": "jq",
                      "name": "email",
                      "expr": ".before.email // .after.email"
                    },
                    {
                      "type": "jq",
                      "name": "gender",
                      "expr": ".before.gender // .after.gender"
                    },
                    {
                      "type": "jq",
                      "name": "age",
                      "expr": ".before.age // .after.age"
                    },
                    {
                      "type": "jq",
                      "name": "updated_at",
                      "expr": ".before.updated_at // .after.updated_at"
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
        
    - products
        
        #### lab3-2-12-2

        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_products_changes",
              "timestampSpec": {
                "column": "!!!_no_such_column_!!!",
                "missingValue": "2010-01-01T00:00:00Z"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "id",
                  "name",
                  "price",
                  "category",
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
              "topic": "mysql-server.shopdb.products",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-products"
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
                      "name": "id",
                      "expr": ".before.id // .after.id"
                    },
                    {
                      "type": "jq",
                      "name": "name",
                      "expr": ".before.name // .after.name"
                    },
                    {
                      "type": "jq",
                      "name": "price",
                      "expr": ".before.price // .after.price"
                    },
                    {
                      "type": "jq",
                      "name": "category",
                      "expr": ".before.category // .after.category"
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
        
    - orders
        
        #### lab3-2-12-3

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
        
    - cart
        
        #### lab3-2-12-4

        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_cart_changes",
              "timestampSpec": {
                "column": "added_at",
                "format": "millis"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "cart_id",
                  "session_id",
                  "user_id",
                  "product_id",
                  "quantity",
                  "price",
                  "added_at",
                  "updated_at",
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
              "topic": "mysql-server.shopdb.cart",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-cart"
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
                      "name": "quantity",
                      "expr": ".before.quantity // .after.quantity"
                    },
                    {
                      "type": "jq",
                      "name": "price",
                      "expr": ".before.price // .after.price"
                    },
                    {
                      "type": "jq",
                      "name": "added_at",
                      "expr": ".before.added_at // .after.added_at"
                    },
                    {
                      "type": "jq",
                      "name": "updated_at",
                      "expr": ".before.updated_at // .after.updated_at"
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
        
    - cart_logs
        
        #### lab3-2-12-5

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
        
13. 페이지 새로고침 후 각 Supervisors, Task의 Status가 RUNNING인 것을 확인
14. Query 메뉴 클릭
15. 테이블 JOIN 쿼리를 실행

    - orders, users 테이블 JOIN

        #### lab3-2-15-1
    
        ```sql
        INSERT INTO dw_orders_users
        SELECT
          o.__time            AS __time,
          o.order_id,
          o.user_id,
          u.gender,
          CAST(u.age AS INTEGER) AS age,
          o.product_id,
          o.price,
          o.quantity
        FROM shopdb_orders_changes o
        LEFT JOIN shopdb_users_changes u
          ON o.user_id = u.user_id
        WHERE o.__deleted='false'
          AND u.__deleted='false'
        PARTITIONED BY DAY
        ```
        
    - cart, orders, products 테이블 JOIN
        
        #### lab3-2-15-2
    
        ```sql
        INSERT INTO dw_cart_orders_products
        SELECT
          c.__time         AS __time,
          c.cart_id,
          c.user_id,
          c.event_type,
          c.event_time,
          o.order_id,
          o.order_time,
          p.id             AS product_id,
          p.category,
          c.new_quantity   AS cart_qty,
          o.quantity       AS order_qty
        FROM shopdb_cart_logs_changes c
        LEFT JOIN shopdb_orders_changes o
          ON c.user_id = o.user_id
             AND c.product_id = o.product_id
             AND DATE_TRUNC('DAY', CAST(c.event_time AS TIMESTAMP))
               = DATE_TRUNC('DAY', CAST(o.order_time AS TIMESTAMP))
        LEFT JOIN shopdb_products_changes p
          ON c.product_id = p.id
        WHERE c.__deleted = 'false'
          AND p.__deleted = 'false'
        PARTITIONED BY DAY
        ```
        
    - 일별 사용자, 상품 주문 건수를 집계하여 테이블에 저장
        
        #### lab3-2-15-3
    
        ```sql
        INSERT INTO dw_user_product_order_cnt
        SELECT
          __time,
          user_id,
          product_id,
          COUNT(*) AS cnt
        FROM dw_orders_users
        GROUP BY 1,2,3
        PARTITIONED BY DAY
        ```

    - 일별 사용자, 상품 주문 건수 집계를 바탕으로 재구매율 논리 추가

        #### lab3-2-15-4
              
        ```sql
        INSERT INTO dw_user_product_order_cnt
        SELECT
          __time,
          user_id,
          product_id,
          COUNT(*) AS cnt
        FROM dw_orders_users
        GROUP BY 1,2,3
        PARTITIONED BY DAY
        ```
    

## 3. **Superset을 활용한 데이터 시각화**

1. 마스터 노드(`HadoopMST-hadoop-dataflow-1`)의 Public IP를 이용하여 웹 브라우저에서 Superset에 접속
    
    #### lab3-3-1

    ```
    http://${MASTER_NODE_PUBLIC_IP}:4000
    ```
    
2. Dataflow 유형 클러스터 생성 시 입력한 관리자 아이디, 비밀번호를 이용하여 로그인
    - USERNAME: `admin`
    - PASSWORD: `Admin1234!`
    - SIGN IN 버튼 클릭
3. Datasets 메뉴 클릭 후 + DATASET 버튼 클릭
4. DATASET 추가
    - DATABASE: `druid`
    - SCHEMA: `druid`
    - Select database table: `Druid에서 생성한 모든 Dataset`
    - CREATE DATASET AND CREATE CHART 버튼 클릭
5. 누적 방문자 수 시각화
    - Datasets 메뉴 클릭 후 nginx-topic Dataset 클릭
    - Big Number 차트 생성
        - BIG NUMBER 선택
        - METRICS
            - SIMPLE 탭 클릭
            - COLUMN: session_id
            - AGGREGATE: COUNT_DISTINCT
            - SAVE 버튼 클릭
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/f8f0a53d-3cad-4806-9a83-dd8eb1a6f405)

        
        - SAVE 버튼 클릭
        - 저장 정보 입력
            - CHAR NAME: Big Number
            - ADD TO DASHBOARD: 빈 칸
        - SAVE 버튼 클릭
    - Time-series Area 차트 생성
        - Datasets 메뉴 클릭 후 nginx-topic 클릭
        - TIME-SERIES AREA CHART 선택
        - SELECT 버튼 클릭
        - TIME GRAIN: Minute
        - METRICS
            - SIMPLE 탭 클릭
            - COLUMN: session_id
            - AGGREGATE: COUNT_DISTINCT
            - SAVE 버튼 클릭
        - 하단 Advanced analytics 항목 클릭
            - Rolling window(ROLLING FUNCTION): cumsum
        - CREATE CHART 버튼 클릭
        
        ![image](https://github.com/user-attachments/assets/f28e37f0-0ea4-4228-9a99-2ada1033c42d)

        
        - SAVE 버튼 클릭
        - 저장 정보 입력
            - CHAR NAME: Time-series Area Chart
            - ADD TO DASHBOARD: 빈 칸
        - SAVE 버튼 클릭
    - Dashboards 메뉴 클릭 후 + DASHBOARD 버튼 클릭
    - Big Number, Time-series Area Chart를 빈 공간에 배치
    - [ untitled dashboard ]를 지운 후 누적 방문자 수 제목을 제목으로 입력
    - SAVE 버튼 클릭
6. 연령대별 상품 매출 시각화
    - Datasets 메뉴 클릭 후 dw_orders_users의 수정 버튼 클릭
    - METRICS 탭 클릭 후 + ADD ITEM 버튼 클릭
    - Metric: `총매출`
    - SQL expression
     
        #### lab3-3-6-1
   
        ```bash
        SUM(price * quantity)
        ```
        
    - CALCULATED COLUMNS 탭 클릭  후 + ADD ITEM 버튼 클릭
    - Column: `age_group`
    - SQL EXPRESSION
        

        #### lab3-3-6-2
        ```bash
        CASE
          WHEN age BETWEEN 10 AND 19 THEN '10대'
          WHEN age BETWEEN 20 AND 29 THEN '20대'
          WHEN age BETWEEN 30 AND 39 THEN '30대'
          WHEN age BETWEEN 40 AND 49 THEN '40대'
          WHEN age BETWEEN 50 AND 59 THEN '50대'
          ELSE '60대 이상'
        END
        ```
        
    - SAVE 버튼 클릭
    - dw_orders_users 클릭
    - TIME-SERIES LINE CHART 선택
    - TIME GRAIN: `Hour`
    - METRICS: `총매출`
    - DIENSIONS: `age_group`
    - CREATE CHART 버튼 클릭
    
    ![image](https://github.com/user-attachments/assets/671bda92-7857-4e2b-86bb-5e2f5d22cfff)

    
7. 상품별 재구매율 Top5 시각화
    - Datasets 메뉴 클릭 후 dw_user_product_order_cnt의 수정 버튼 클릭
    - METRICS 탭 클릭 후 + ADD ITEM 버튼 클릭
    - Metric: `재구매율(%)`
    - SQL expression

        #### lab3-3-7

        ```bash
        (
          APPROX_COUNT_DISTINCT(CASE WHEN cnt > 1 THEN user_id END)
          * 100.0
          / APPROX_COUNT_DISTINCT(user_id)
        )
        ```
        
    - SAVE 버튼 클릭
    - dw_user_product_order_cnt 클릭
    - TIME-SERIES LINE CHART 선택
    - TIME GRAIN: `Month`
    - METRICS: `재구매율(%)`
    - DIENSIONS: `product_id`
    - SERIES LIMIT: 5
    - CREATE CHART 버튼 클릭
    
    ![image](https://github.com/user-attachments/assets/e13c94d4-c68d-403f-b84d-8e950616eea7)

    
8. 시간대별 매출 및 성장률
    - Datasets 메뉴 클릭 후 shopdb_orders_changes의 수정 버튼 클릭
    - METRICS 탭 클릭 후 + ADD ITEM 버튼 클릭
    - Metric: `총매출`
    - SQL expression
        
        #### lab3-3-8

        ```bash
        SUM(price * quantity)
        ```
        
    - SAVE 버튼 클릭
    - Datasets 메뉴 클릭 후 shopdb_orders_changes 클릭
    - TIME-SERIES AREA CHART 선택
    - TIME GRAIN: `Hour`
    - METRICS: `총매출`
    - CREATE CHART 버튼 클릭
    
    ![image](https://github.com/user-attachments/assets/6578228d-0ae0-4829-851f-17ddc3e3618b)

    
9. 장바구니 행동 분석
    - Datasets 메뉴 클릭 후 shopdb_cart_logs_changes의 수정 버튼 클릭
    - CALCULATED COLUMNS 탭 클릭
    - Column: `event_type_ko`
    - SQL EXPRESSION
        
        #### lab3-3-9

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
    - shopdb_cart_logs_changes 클릭
    - TIME-SERIES LINE CHART 선택
    - TIME GRAIN: `Hour`
    - METRICS
        - SIMPLE 탭 클릭
        - COLUMN: `cart_id`
        - AGGREGATE: `COUNT`
        - SAVE 버튼 클릭
    - DIENSIONS: `event_type_ko`
    - CREATE CHART 버튼 클릭
    
    ![image](https://github.com/user-attachments/assets/7342ca12-d969-45b5-bd76-6edfaa10715f)
