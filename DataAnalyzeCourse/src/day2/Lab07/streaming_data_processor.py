#!/usr/bin/env python3
import os
from pyspark.sql.avro.functions import from_avro
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, expr, when, coalesce, first,
    date_format, unix_timestamp, lit,
    lag, lead, row_number, round,
    get_json_object, sum as spark_sum,
    max as spark_max
)
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType,
    IntegerType, TimestampType, DoubleType
)
from delta.tables import DeltaTable

# ----------------------------
# 1) Debezium JSON 파싱 (문자열 비교 수정 포함)
# ----------------------------
def load_debezium_users_fixed(spark, topic):
    try:
        raw_df = (
            spark.read
                .format("kafka")
                .option("kafka.bootstrap.servers", "BOOTSTRAP_SERVERS")
                .option("subscribe", topic)
                .option("startingOffsets", "earliest")
                .load()
        )
        if raw_df.count() == 0:
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
        return spark.createDataFrame([], StructType([
            StructField("user_info_id", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("age", IntegerType(), True)
        ]))

def load_debezium_sessions_fixed(spark, topic):
    try:
        raw_df = (
            spark.read
                .format("kafka")
                .option("kafka.bootstrap.servers", "BOOTSTRAP_SERVERS")
                .option("subscribe", topic)
                .option("startingOffsets", "earliest")
                .load()
        )
        if raw_df.count() == 0:
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
# ------------------------------------------------
def load_kafka_avro_stream(spark, topic, avro_schema_str):
    raw = (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "BOOTSTRAP_SERVERS")
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
        col("d.timestamp").cast("timestamp").alias("event_time")
    ).filter(
        col("session_id").isNotNull() &
        col("endpoint").isNotNull() &
        col("event_time").isNotNull()
    )

# ------------------------------------------------
# 4) foreach_batch - 중복 컬럼/행 모호성 완전 제거
# ------------------------------------------------
def foreach_batch_nodup(logs_df, batch_id):
    try:
        spark = logs_df.sparkSession
        if logs_df.rdd.isEmpty():
            print(f"Batch {batch_id}: Empty batch, skipping...")
            return

        # 상태 불러오기
        if DeltaTable.isDeltaTable(spark, STATE_TABLE_PATH):
            state_df = spark.read.format("delta").load(STATE_TABLE_PATH)
        else:
            state_df = spark.createDataFrame([], state_schema)

        # CDC 데이터
        sessions = load_debezium_sessions_fixed(spark, "mysql-server.shopdb.sessions")
        users = load_debezium_users_fixed(spark, "mysql-server.shopdb.users")

        # alias 부여
        logs_df = logs_df.alias("l")
        sessions = sessions.alias("s")
        users = users.alias("u")

        # 조인 및 중복 컬럼 제거
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

        # 윈도우는 반드시 명시적으로 session_id 컬럼 사용
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
            print(f"Batch {batch_id}: Final DataFrame is empty, skipping...")
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

        print(f"Batch {batch_id} processed successfully - Final records: {final_df.count()}")

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
            .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    try:
        with open("nginx_log.avsc", "r") as f:
            nginx_avro_schema = f.read()
    except FileNotFoundError:
        print("nginx_log.avsc file not found!")
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
        print("Stopping stream...")
        query.stop()
        spark.stop()
