# 기타 Superset 지표

## 1. Druid를 활용한 데이터 수집 및 가공

1. Load Data > Streaming > Start a new streaming spec 버튼 클릭
2. `Edit Spec` 버튼 클릭 후 아래 spec 입력
    - **Note**: Kafka 부트스트랩 서버를 복사해둔 값으로 변경
    - users
        
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
        
    - users_logs
        
        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_users_logs_changes",
              "timestampSpec": {
                "column": "event_time",
                "format": "millis"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "history_id",
                  "user_id",
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
              "topic": "mysql-server.shopdb.users_logs",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-users_logs"
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
                      "name": "history_id",
                      "expr": ".before.history_id // .after.history_id"
                    },
                    {
                      "type": "jq",
                      "name": "user_id",
                      "expr": ".before.user_id // .after.user_id"
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
        
    - products
        
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
        
    - sessions
        
        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_sessions_changes",
              "timestampSpec": {
                "column": "created_at",
                "format": "micro"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "session_id",
                  "user_id",
                  "created_at",
                  "login_time",
                  "logout_time",
                  "last_active",
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
              "topic": "mysql-server.shopdb.sessions",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-sessions"
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
                      "name": "created_at",
                      "expr": ".before.created_at // .after.created_at"
                    },
                    {
                      "type": "jq",
                      "name": "login_time",
                      "expr": ".before.login_time // .after.login_time"
                    },
                    {
                      "type": "jq",
                      "name": "logout_time",
                      "expr": ".before.logout_time // .after.logout_time"
                    },
                    {
                      "type": "jq",
                      "name": "last_active",
                      "expr": ".before.last_active // .after.last_active"
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
        
    - reviews
        
        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_reviews_changes",
              "timestampSpec": {
                "column": "review_time",
                "format": "micro"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "review_id",
                  "user_id",
                  "session_id",
                  "product_id",
                  "rating",
                  "review_time",
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
              "topic": "mysql-server.shopdb.reviews",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-reviews"
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
                      "name": "review_id",
                      "expr": ".before.review_id // .after.review_id"
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
                      "name": "rating",
                      "expr": ".before.rating // .after.rating"
                    },
                    {
                      "type": "jq",
                      "name": "review_time",
                      "expr": ".before.review_time // .after.review_time"
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
        
    - search_logs
        
        ```bash
        {
          "type": "kafka",
          "spec": {
            "dataSchema": {
              "dataSource": "shopdb_search_logs_changes",
              "timestampSpec": {
                "column": "searched_at",
                "format": "millis"
              },
              "dimensionsSpec": {
                "dimensions": [
                  "log_id",
                  "session_id",
                  "search_query",
                  "searched_at",
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
              "topic": "mysql-server.shopdb.search_logs",
              "consumerProperties": {
                "bootstrap.servers": "{Kafka 부트스트랩 서버}",
                "group.id": "druid-shopdb-search_logs"
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
                      "name": "session_id",
                      "expr": ".before.session_id // .after.session_id"
                    },
                    {
                      "type": "jq",
                      "name": "search_query",
                      "expr": ".before.search_query // .after.search_query"
                    },
                    {
                      "type": "jq",
                      "name": "searched_at",
                      "expr": ".before.searched_at // .after.searched_at"
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
        
3. 페이지 새로고침 후 각 Supervisors, Task의 Status가 RUNNING인 것을 확인
4. Query 메뉴 클릭
5. 테이블 JOIN 쿼리를 실행

    - orders, users 테이블 JOIN
    
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
        
    - 일별 사용자, 상품 주문 건수를 집계하여 테이블에 저장
            
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
        
    - cart, orders, products 테이블 JOIN
            
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

    - 일별 사용자, 상품 주문 건수 집계를 바탕으로 재구매율 논리 추가
              
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

## 2. Superset을 활용한 데이터 시각화

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
