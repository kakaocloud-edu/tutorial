#!/usr/bin/env python3
import os
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, expr, when, coalesce, lit, broadcast, # broadcast 임포트
    date_format, unix_timestamp, to_timestamp,
    lag, lead, row_number, round,
    sum as spark_sum,
    max as spark_max
)
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType,
    IntegerType, TimestampType, DoubleType
)
from delta.tables import DeltaTable

# --- S3 데이터 소스 경로 정의 ---
NGINX_LOGS_S3_PATH = "s3a://data-catalog-bucket/kafka-nginx-log/nginx-topic/"
CDC_EVENTS_S3_BASE_PATH = "s3a://data-catalog-bucket/raw_cdc_events/mysql-server.shopdb."
USERS_CDC_S3_PATH = f"{CDC_EVENTS_S3_BASE_PATH}users/"
SESSIONS_CDC_S3_PATH = f"{CDC_EVENTS_S3_BASE_PATH}sessions/"

# --- 상태 저장용 Delta 테이블 경로 설정 (배치 전용) ---
STATE_TABLE_PATH_BATCH = "s3a://data-catalog-bucket/data-catalog-dir/session_state_batch/"
state_schema = StructType() \
    .add("session_id", StringType()).add("search_count", LongType()) \
    .add("cart_item_count", LongType()).add("page_depth", LongType()) \
    .add("last_event_time", TimestampType())

# --- 최종 정제 결과 저장 공간 (배치 전용) ---
FINAL_OUTPUT_PATH_BATCH = "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction_batch/"

# --- Nginx 로그 Parquet 파일의 스키마 정의 ---
nginx_log_schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("remote_addr", StringType(), True), StructField("request", StringType(), True),
    StructField("status", StructType([StructField("member0", StringType(), True), StructField("member1", IntegerType(), True)]), True),
    StructField("body_bytes_sent", StructType([StructField("member0", StringType(), True), StructField("member1", IntegerType(), True)]), True),
    StructField("http_referer", StringType(), True), StructField("http_user_agent", StringType(), True),
    StructField("session_id", StringType(), True), StructField("user_id", StringType(), True),
    StructField("request_time", StructType([StructField("member0", StringType(), True), StructField("member1", DoubleType(), True)]), True),
    StructField("upstream_response_time", StructType([StructField("member0", StringType(), True), StructField("member1", DoubleType(), True)]), True),
    StructField("endpoint", StringType(), True), StructField("method", StringType(), True),
    StructField("query_params", StringType(), True), StructField("product_id", StringType(), True),
    StructField("request_body", StringType(), True), StructField("x_forwarded_for", StringType(), True),
    StructField("host", StringType(), True)
])

# ==============================================================================
# 1. 데이터 로드 함수 정의 (S3 소스)
# ==============================================================================
def load_debezium_users_batch(spark, path):
    try:
        raw_df = spark.read.json(path)
        if raw_df.rdd.isEmpty(): return spark.createDataFrame([], StructType([StructField("user_info_id", StringType(), True), StructField("gender", StringType(), True), StructField("age", IntegerType(), True)]))
        parsed_df = raw_df.select(col("op").alias("operation"), col("after.user_id").alias("user_info_id"), col("after.gender").alias("gender"), col("after.age").cast("int").alias("age"))
        return parsed_df.filter(col("operation").isin(["c", "u", "r"]) & col("user_info_id").isNotNull() & (col("user_info_id") != "") & col("gender").isin(["M", "F"]) & col("age").between(1, 120)).dropDuplicates(["user_info_id"])
    except Exception as e: return spark.createDataFrame([], StructType([StructField("user_info_id", StringType(), True), StructField("gender", StringType(), True), StructField("age", IntegerType(), True)]))

def load_debezium_sessions_batch(spark, path):
    try:
        raw_df = spark.read.json(path)
        if raw_df.rdd.isEmpty(): return spark.createDataFrame([], StructType([StructField("session_id", StringType(), True), StructField("session_user_id", StringType(), True)]))
        sessions_df = raw_df.select(col("op").alias("operation"), col("after.session_id").alias("session_id"), col("after.user_id").alias("session_user_id"))
        return sessions_df.filter(col("operation").isin(["c", "u", "r"]) & col("session_id").isNotNull()).dropDuplicates(["session_id"])
    except Exception as e: return spark.createDataFrame([], StructType([StructField("session_id", StringType(), True), StructField("session_user_id", StringType(), True)]))

def load_nginx_logs_batch(spark, path):
    try:
        raw_df = spark.read.option("recursiveFileLookup", "true").schema(nginx_log_schema).parquet(path)
        if raw_df.rdd.isEmpty(): return spark.createDataFrame([], StructType([StructField("session_id", StringType(), True), StructField("user_id", StringType(), True), StructField("endpoint", StringType(), True), StructField("method", StringType(), True), StructField("query_params", StringType(), True), StructField("product_id", StringType(), True), StructField("request_body", StringType(), True), StructField("event_time", TimestampType(), True)]))
        transformed_df = raw_df.select(col("session_id"), when(col("user_id") == "", lit(None)).otherwise(col("user_id")).alias("user_id"), col("endpoint"), col("method"), col("query_params"), col("product_id"), col("request_body"), to_timestamp(col("timestamp")).alias("event_time"))
        return transformed_df.filter(col("session_id").isNotNull() & col("endpoint").isNotNull() & col("event_time").isNotNull())
    except Exception as e: return spark.createDataFrame([], StructType([StructField("session_id", StringType(), True), StructField("user_id", StringType(), True), StructField("endpoint", StringType(), True), StructField("method", StringType(), True), StructField("query_params", StringType(), True), StructField("product_id", StringType(), True), StructField("request_body", StringType(), True), StructField("event_time", TimestampType(), True)]))

# ==============================================================================
# 2. 사용자 행동 데이터 처리 함수 (성능 최적화)
# ==============================================================================

def process_user_behavior_batch(logs_df, sessions_df, users_df, spark):
    try:
        if logs_df.rdd.isEmpty():
            print("현재 배치에 처리할 Nginx 로그 데이터가 없어 건너뜁니다.")
            return

        if DeltaTable.isDeltaTable(spark, STATE_TABLE_PATH_BATCH):
            state_df = spark.read.format("delta").load(STATE_TABLE_PATH_BATCH)
        else:
            state_df = spark.createDataFrame([], state_schema)
            print(f"Delta 상태 테이블이 없어 새로 생성합니다: {STATE_TABLE_PATH_BATCH}")

        # [성능 최적화 1: 브로드캐스트 조인] 작은 테이블을 브로드캐스트하여 Shuffle 방지
        logs_sessions_joined = logs_df.alias("l") \
            .join(broadcast(sessions_df.alias("s")), col("l.session_id") == col("s.session_id"), "left")
        
        base_with_userid = logs_sessions_joined.withColumn("final_user_id", coalesce(col("l.user_id"), col("s.session_user_id")))
        
        enriched = base_with_userid \
            .join(broadcast(users_df.alias("u")), col("final_user_id") == col("u.user_info_id"), "left") \
            .select(
                col("l.session_id").alias("session_id"), col("final_user_id").alias("user_id"),
                coalesce(col("u.gender"), lit("Unknown")).alias("gender"), coalesce(col("u.age"), lit(0)).alias("age"),
                col("l.event_time"), col("l.endpoint").alias("current_state"),
                col("l.method"), col("l.query_params"), col("l.product_id"), col("l.request_body")
            )

        # [성능 최적화 2: 캐싱] 복잡한 윈도우 연산 전, 조인 결과를 메모리에 캐시
        enriched.cache()
        # .count()와 같은 액션으로 캐시를 트리거하고, 디버깅을 위해 레코드 수 확인
        print(f"DEBUG: 조인 및 캐싱 후 enriched DF 레코드 수: {enriched.count()}")

        window_spec = Window.partitionBy("session_id").orderBy("event_time")
        batch_flagged = enriched.withColumn("batch_search", when(col("current_state").like("/search%"), 1).otherwise(0)) \
                                .withColumn("batch_cart", when(col("current_state") == "/cart/add", 1).otherwise(0)) \
                                .withColumn("prev_state", lag("current_state", 1).over(window_spec)) \
                                .withColumn("prev_time", lag("event_time", 1).over(window_spec))
        
        dedup = batch_flagged.filter(col("prev_time").isNull() | (~((col("current_state") == col("prev_state")) & (col("event_time") == col("prev_time")))))
        dedup = dedup.withColumn("batch_search_cum", expr("sum(batch_search) OVER (PARTITION BY session_id ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)")) \
                     .withColumn("batch_cart_cum", expr("sum(batch_cart) OVER (PARTITION BY session_id ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"))
        
        merged = dedup.alias("b").join(state_df.alias("s"), col("b.session_id") == col("s.session_id"), "left") \
            .select(
                col("b.session_id"), col("b.user_id"), col("b.gender"), col("b.age"), col("b.event_time"), col("b.current_state"),
                (coalesce(col("s.search_count"), lit(0)) + col("b.batch_search_cum")).alias("search_count"),
                (coalesce(col("s.cart_item_count"), lit(0)) + col("b.batch_cart_cum")).alias("cart_item_count"),
                coalesce(col("s.page_depth"), lit(0)).alias("prev_page_depth"),
                col("b.prev_time"), col("s.last_event_time").alias("prev_batch_time"),
                lead(col("b.current_state"), 1).over(Window.partitionBy(col("b.session_id")).orderBy(col("b.event_time"))).alias("next_state"),
                date_format(col("b.event_time"), "yyyy-MM-dd").alias("dt")
            ).withColumn("last_action_elapsed",
                when(col("prev_time").isNotNull(), (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_time"))).cast(DoubleType()))
                .when(col("prev_batch_time").isNotNull(), (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_batch_time"))).cast(DoubleType()))
                .otherwise(lit(0.0)))
        
        merged = merged.withColumn("page_depth", col("prev_page_depth") + row_number().over(Window.partitionBy("session_id").orderBy("event_time"))).drop("prev_page_depth", "prev_time", "prev_batch_time")
        
        final_df = merged.withColumn("search_count", col("search_count").cast(IntegerType())) \
                         .withColumn("cart_item_count", col("cart_item_count").cast(IntegerType())) \
                         .withColumn("page_depth", col("page_depth").cast(IntegerType())) \
                         .withColumn("last_action_elapsed", round(col("last_action_elapsed"), 2)) \
                         .dropDuplicates(["session_id", "user_id", "current_state", "page_depth"])
        
        if final_df.rdd.isEmpty(): print("모든 처리 후 최종 DataFrame이 비어있어 저장 및 상태 업데이트를 건너뜁니다."); return

        final_df.select("session_id", "user_id", "gender", "age", "current_state", "search_count", "cart_item_count", "page_depth", "last_action_elapsed", "next_state", "dt") \
            .write.mode("append").format("parquet").partitionBy("dt") \
            .option("maxRecordsPerFile", 500000).save(FINAL_OUTPUT_PATH_BATCH)

        new_state = final_df.groupBy("session_id").agg(spark_max("search_count").alias("search_count"), spark_max("cart_item_count").alias("cart_item_count"), spark_max("page_depth").alias("page_depth"), spark_max("event_time").alias("last_event_time"))
        
        if DeltaTable.isDeltaTable(spark, STATE_TABLE_PATH_BATCH):
            DeltaTable.forPath(spark, STATE_TABLE_PATH_BATCH).alias("s").merge(new_state.alias("n"), "s.session_id = n.session_id").whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
        else: new_state.write.format("delta").mode("overwrite").save(STATE_TABLE_PATH_BATCH)
        
        print(f"배치 처리 성공 - 최종 레코드 수: {final_df.count()}")

    except Exception as e:
        print(f"배치 처리 중 에러 발생: {str(e)}")
        import traceback; traceback.print_exc(); raise e
    finally:
        # 사용이 끝난 캐시 메모리 해제
        spark.catalog.clearCache()

# ==============================================================================
# 3. Main: 배치 정의 및 실행
# ==============================================================================
if __name__ == "__main__":
    spark = (
        SparkSession.builder
            .appName("S3BatchUserBehaviorProcessorOptimized")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        print("S3에서 Nginx 로그 데이터 로드 중...")
        logs_df = load_nginx_logs_batch(spark, NGINX_LOGS_S3_PATH)
        print(f"Nginx 로그 데이터 로드 완료. 레코드 수: {logs_df.count()}")

        print("S3에서 Debezium Users 데이터 로드 중...")
        users_df = load_debezium_users_batch(spark, USERS_CDC_S3_PATH)
        print(f"Debezium Users 데이터 로드 완료. 레코드 수: {users_df.count()}")

        print("S3에서 Debezium Sessions 데이터 로드 중...")
        sessions_df = load_debezium_sessions_batch(spark, SESSIONS_CDC_S3_PATH)
        print(f"Debezium Sessions 데이터 로드 완료. 레코드 수: {sessions_df.count()}")

        print("\n사용자 행동 데이터 배치 처리 시작...")
        process_user_behavior_batch(logs_df, sessions_df, users_df, spark)
        print("사용자 행동 데이터 배치 처리 완료.")

    except Exception as e:
        print(f"메인 처리 중 에러 발생: {str(e)}")
        import traceback; traceback.print_exc()
    finally:
        print("\n스파크 세션 종료.")
        spark.stop()
