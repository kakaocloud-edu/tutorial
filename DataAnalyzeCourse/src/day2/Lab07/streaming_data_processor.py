import os
import requests
import json
from pyspark.sql.avro.functions import from_avro
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, expr, when, coalesce, first,
    date_format, unix_timestamp, lit,
    lag, lead, row_number, round,
    get_json_object, sum as spark_sum,
    max as spark_max,
    to_timestamp,
    from_utc_timestamp, 
    to_utc_timestamp
)
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType,
    IntegerType, TimestampType, DoubleType
)
from delta.tables import DeltaTable

# ----------------------------------------------------------------------------
# 서비스 설정 값 (스크립트 실행 전, sed 등으로 변경할 수 있도록 여기에 정의)
# ----------------------------------------------------------------------------
BOOTSTRAP_SERVERS = "KAFKA_BOOTSTRAP_SERVERS" 
SCHEMA_REGISTRY_URL = "http://API_VM_IP:8081" 

# ----------------------------------------------------------------------------
# Schema Registry 유틸리티 함수
# ----------------------------------------------------------------------------
def get_latest_schema_from_registry(subject_name):
    """
    Schema Registry에서 특정 주제(Subject)의 최신 Avro 스키마를 가져옵니다.
    네트워크 요청을 통해 스키마를 동적으로 로드합니다.
    """
    url = f"{SCHEMA_REGISTRY_URL}/subjects/{subject_name}/versions/latest"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        schema_info = response.json()
        print(f"Successfully fetched schema for subject '{subject_name}' from Schema Registry.")
        return schema_info['schema']
    except requests.exceptions.RequestException as e:
        print(f"Schema Registry에서 스키마 로드 실패: {e}")
        print(f"URL: {url}")
        raise ConnectionError(f"Failed to connect to Schema Registry or retrieve schema: {e}. Check URL and network connectivity.")

# ----------------------------
# 1) Debezium JSON 파싱
# ----------------------------
def load_debezium_users_fixed(spark, topic):
    """Debezium users 토픽에서 데이터를 로드하고 파싱합니다."""
    try:
        raw_df = (
            spark.read
                 .format("kafka")
                 .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS) 
                 .option("subscribe", topic)
                 .option("startingOffsets", "earliest")
                 .load()
        )
        if raw_df.rdd.isEmpty():
            print(f"Debezium users topic '{topic}' is empty. Returning empty DataFrame.")
            return spark.createDataFrame([], StructType([
                StructField("user_info_id", StringType(), True),
                StructField("gender", StringType(), True),
                StructField("age", IntegerType(), True)
            ]))

        parsed_df = raw_df.selectExpr("CAST(value AS STRING) AS json_str").select(
            get_json_object("json_str", "$.op").alias("operation"),
            get_json_object("json_str", "$.after.user_id").alias("user_info_id"),
            get_json_object("json_str", "$.after.gender").alias("gender"),
            get_json_object("json_str", "$.after.age").cast("int").alias("age"),
            get_json_object("json_str", "$.ts_ms").cast("timestamp").alias("cdc_timestamp")
        )

        final_df = parsed_df.filter(
            col("operation").isin(["c", "u", "r"]) &
            col("user_info_id").isNotNull() &
            (col("user_info_id") != lit("")) &
            col("gender").isin(["M", "F"]) &
            col("age").between(1, 120)
        ).dropDuplicates(["user_info_id"])

        return final_df
    except Exception as e:
        print(f"사용자 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return spark.createDataFrame([], StructType([
            StructField("user_info_id", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("age", IntegerType(), True)
        ]))

def load_debezium_sessions_fixed(spark, topic):
    """Debezium sessions 토픽에서 데이터를 로드하고 파싱합니다."""
    try:
        raw_df = (
            spark.read
                 .format("kafka")
                 .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS) 
                 .option("subscribe", topic)
                 .option("startingOffsets", "earliest")
                 .load()
        )
        if raw_df.rdd.isEmpty():
            print(f"Debezium sessions topic '{topic}' is empty. Returning empty DataFrame.")
            return spark.createDataFrame([], StructType([
                StructField("session_id", StringType(), True),
                StructField("session_user_id", StringType(), True)
            ]))

        sessions_df = raw_df.selectExpr("CAST(value AS STRING) AS json_str").select(
            get_json_object("json_str", "$.op").alias("operation"),
            get_json_object("json_str", "$.after.session_id").alias("session_id"),
            get_json_object("json_str", "$.after.user_id").alias("session_user_id")
        ).filter(
            col("operation").isin(["c", "u", "r"]) &
            col("session_id").isNotNull()
        ).dropDuplicates(["session_id"])

        return sessions_df
    except Exception as e:
        print(f"Sessions 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return spark.createDataFrame([], StructType([
            StructField("session_id", StringType(), True),
            StructField("session_user_id", StringType(), True)
        ]))

# -----------------------------------
# 2) 상태 저장용 Delta 테이블 설정
# -----------------------------------
STATE_TABLE_PATH = "s3a://data-catalog-bucket/data-catalog-dir/session_state/" 
state_schema = StructType() \
    .add("session_id",      StringType()) \
    .add("search_count",    LongType()) \
    .add("cart_item_count", LongType()) \
    .add("page_depth",      LongType()) \
    .add("last_event_time", TimestampType())

# ------------------------------------------------
# 3) nginx Avro 토픽을 스트림(readStream)으로 로드
#    - timestamp 파싱 로직 최종 보완: Spark 세션 타임존 설정 활용
# ------------------------------------------------
def load_kafka_avro_stream(spark, topic, avro_schema_str):
    """
    Kafka에서 Avro 형식의 Nginx 로그를 스트림으로 로드하고 파싱합니다.
    """
    raw = (
        spark.readStream
             .format("kafka")
             .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS) 
             .option("subscribe", topic)
             .option("startingOffsets", "latest") 
             .option("failOnDataLoss", "false")
             .option("maxOffsetsPerTrigger", 200) 
             .load()
        .select(expr("substring(value, 6, length(value)-5)").cast("binary").alias("avro"))
        .select(from_avro(col("avro"), avro_schema_str, {"mode": "PERMISSIVE"}).alias("d"))
    )
    
    return raw.select(
        col("d.session_id"),
        when(col("d.user_id") == "", lit(None)).otherwise(col("d.user_id")).alias("user_id"),
        col("d.endpoint"),
        col("d.method"),
        col("d.query_params"),
        col("d.product_id"),
        col("d.request_body"),
        to_timestamp(col("d.timestamp"), "yyyy-MM-dd HH:mm:ss").alias("event_time") 
    ).filter(
        col("session_id").isNotNull() &
        (col("session_id") != "") &  
        col("endpoint").isNotNull() &
        col("event_time").isNotNull() 
    )

# ------------------------------------------------
# 4) foreach_batch - 중복 컬럼/행 모호성 완전 제거 및 상태 관리
# ------------------------------------------------
def foreach_batch_nodup(logs_df, batch_id):
    """
    마이크로 배치별로 데이터를 처리하는 함수입니다.
    세션 상태를 관리하고 중복을 제거하며, CDC 데이터와 조인하여 최종 데이터를 Parquet으로 저장합니다.
    """
    try:
        spark = logs_df.sparkSession
        if logs_df.rdd.isEmpty():
            print(f"Batch {batch_id}: Empty batch, skipping...")
            return

        if DeltaTable.isDeltaTable(spark, STATE_TABLE_PATH):
            state_df = spark.read.format("delta").load(STATE_TABLE_PATH)
        else:
            state_df = spark.createDataFrame([], state_schema)
            print(f"Batch {batch_id}: State Delta table not found at {STATE_TABLE_PATH}. Initializing with empty state.")


        sessions = load_debezium_sessions_fixed(spark, "mysql-server.shopdb.sessions")
        users = load_debezium_users_fixed(spark, "mysql-server.shopdb.users")

        logs_df = logs_df.alias("l")
        sessions = sessions.alias("s")
        users = users.alias("u")

        enriched = (
            logs_df
            .join(sessions, col("l.session_id") == col("s.session_id"), "left")
            .join(users,
                  (col("l.user_id") == col("u.user_info_id")) |
                  (col("s.session_user_id") == col("u.user_info_id")),
                  "left")
            .select(
                col("l.session_id").alias("session_id"),
                coalesce(col("l.user_id"), col("s.session_user_id")).alias("user_id"),
                coalesce(col("u.gender"), lit("Unknown")).alias("gender"),
                coalesce(col("u.age"), lit(0)).alias("age"),
                col("l.event_time"),
                col("l.endpoint").alias("current_state"),
                col("l.method"),
                col("l.query_params"),
                col("l.product_id"),
                col("l.request_body")
            )
        )

        window2 = Window.partitionBy("session_id").orderBy("event_time")

        batch_flagged = (
            enriched
            .withColumn("batch_search", when(col("current_state").like("/search%"), lit(1)).otherwise(lit(0)))
            .withColumn("batch_cart", when(col("current_state") == "/cart/add", lit(1)).otherwise(lit(0)))
            .withColumn("prev_state", lag("current_state", 1).over(window2))
            .withColumn("prev_time", lag("event_time", 1).over(window2))
        )

        dedup = batch_flagged.filter(
            (col("prev_time").isNull()) | 
            (~((col("current_state") == col("prev_state")) & (col("event_time") == col("prev_time"))))
        )

        dedup = dedup \
            .withColumn("batch_search_cum", expr(
                "sum(batch_search) OVER (PARTITION BY session_id ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"
            )) \
            .withColumn("batch_cart_cum", expr(
                "sum(batch_cart) OVER (PARTITION BY session_id ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"
            ))

        merged = (
            dedup.alias("b")
            .join(state_df.alias("s"), col("b.session_id") == col("s.session_id"), "left")
            .select(
                col("b.session_id").alias("session_id"),
                col("b.user_id"),
                col("b.gender"),
                col("b.age"),
                col("b.event_time"),
                col("b.current_state"),
                (coalesce(col("s.search_count"), lit(0)) + col("b.batch_search_cum")).alias("search_count"),
                (coalesce(col("s.cart_item_count"), lit(0)) + col("b.batch_cart_cum")).alias("cart_item_count"),
                coalesce(col("s.page_depth"), lit(0)).alias("prev_page_depth"),
                col("b.prev_time"),
                col("s.last_event_time").alias("prev_batch_time"),
                lead(col("b.current_state"), 1).over(
                    Window.partitionBy(col("b.session_id")).orderBy(col("b.event_time"))
                ).alias("next_state"),
                date_format(col("b.event_time"), "yyyy-MM-dd").alias("dt") 
            )
            .withColumn("last_action_elapsed",
                when(
                    col("prev_time").isNotNull(), 
                    (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_time"))).cast(DoubleType())
                ).when(
                    col("prev_batch_time").isNotNull(), 
                    (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_batch_time"))).cast(DoubleType())
                ).otherwise(lit(0.0)) 
            )
        )

        merged = merged.withColumn(
            "page_depth",
            col("prev_page_depth") + row_number().over(Window.partitionBy("session_id").orderBy("event_time"))
        ).drop("prev_page_depth", "prev_time", "prev_batch_time")

        final_df = (
            merged
            .withColumn("search_count", col("search_count").cast(IntegerType()))
            .withColumn("cart_item_count", col("cart_item_count").cast(IntegerType()))
            .withColumn("page_depth", col("page_depth").cast(IntegerType()))
            .withColumn("last_action_elapsed", round(col("last_action_elapsed"), 2))
            .dropDuplicates(["session_id", "user_id", "current_state", "page_depth"]) 
        )

        if final_df.rdd.isEmpty():
            print(f"Batch {batch_id}: Final DataFrame is empty after processing, skipping write.")
            return

        final_df.select(
            "session_id", "user_id", "gender", "age",
            "current_state", "search_count", "cart_item_count",
            "page_depth", "last_action_elapsed", "next_state", "dt"
        ).repartition(col("dt")) \
            .write.mode("append") \
            .format("parquet") \
            .partitionBy("dt") \
            .option("maxRecordsPerFile", 500000) \
            .save("s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction/") 

        new_state = final_df.groupBy("session_id").agg(
            spark_max("search_count").alias("search_count"),
            spark_max("cart_item_count").alias("cart_item_count"),
            spark_max("page_depth").alias("page_depth"),
            spark_max("event_time").alias("last_event_time")
        )
        
        if DeltaTable.isDeltaTable(spark, STATE_TABLE_PATH):
            DeltaTable.forPath(spark, STATE_TABLE_PATH) \
                .alias("s").merge(
                    new_state.alias("n"),
                    "s.session_id = n.session_id"
                ).whenMatchedUpdateAll() \
                .whenNotMatchedInsertAll() \
                .execute()
        else:
            new_state.write.format("delta").mode("overwrite").save(STATE_TABLE_PATH)
            print(f"Batch {batch_id}: Created new state Delta table at {STATE_TABLE_PATH}.")

        print(f"Batch {batch_id} processed successfully - Final records written: {final_df.count()}")

    except Exception as e:
        print(f"Error processing batch {batch_id}: {str(e)}")
        import traceback
        traceback.print_exc() 
        raise e

# -----------------------------------
# 5) main: 스트림 정의 및 실행
# -----------------------------------
if __name__ == "__main__":
    spark = (
        SparkSession.builder
            .appName("NoDupCDCEnrichedNginxStream")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.sql.adaptive.enabled", "true") 
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") 
            .config("spark.sql.session.timeZone", "UTC") 
            .getOrCreate()
    )
    
    spark.sparkContext.setLogLevel("WARN") 
    
    # WARN AdminClientConfig 경고를 숨기는 코드
    try:
        jvm = spark.sparkContext._jvm
        jvm.org.apache.log4j.Logger.getLogger("org.apache.kafka.clients.admin.AdminClientConfig").setLevel(jvm.org.apache.log4j.Level.ERROR)
        jvm.org.apache.log4j.Logger.getLogger("org.apache.kafka.clients.consumer.ConsumerConfig").setLevel(jvm.org.apache.log4j.Level.ERROR)
        print("Kafka client log levels set to ERROR to suppress AdminClientConfig warnings.")
    except Exception as e:
        print(f"Failed to set Kafka client log levels directly via JVM: {e}")
        print("Continuing with default log levels. WARN messages might appear.")

    try:
        nginx_avro_schema = get_latest_schema_from_registry("nginx-topic-value") 
        print("Nginx Avro schema loaded from Schema Registry successfully.")
    except Exception as e:
        print(f"스키마 로드 중 치명적인 오류 발생. 애플리케이션을 종료합니다: {e}")
        spark.stop() 
        exit(1) 

    logs_df = load_kafka_avro_stream(spark, "nginx-topic", nginx_avro_schema) 

    query = (logs_df.writeStream
        .foreachBatch(foreach_batch_nodup) 
        .option("checkpointLocation", "/tmp/checkpoint/nodup_cdc_enriched") 
        .trigger(processingTime="60 seconds") 
        .start()
    )

    try:
        query.awaitTermination() 
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Stopping stream...")
        query.stop() 
        spark.stop() 
    except Exception as e:
        print(f"Stream query encountered an error: {e}")
        import traceback
        traceback.print_exc()
        query.stop()
        spark.stop()
