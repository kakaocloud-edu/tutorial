#!/usr/bin/env python3

import os
import time
import requests
import json
from pyspark.sql.avro.functions import from_avro
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, expr, when, coalesce, first, concat,
    date_format, unix_timestamp, lit,
    lag, lead, row_number, round,
    get_json_object, sum as spark_sum,
    max as spark_max, min as spark_min,
    to_timestamp,
    from_utc_timestamp,
    to_utc_timestamp,
    trim,
    sha2, concat_ws,
    avg as spark_avg,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType,
    IntegerType, TimestampType, DoubleType, BooleanType
)
from delta.tables import DeltaTable


# --- 환경 변수 로드 ---
def log_time(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


log_time("실시간 스트림 처리 환경 변수 로드 시작")
BOOTSTRAP_SERVER = "KAFKA_BOOTSTRAP_SERVER"
SCHEMA_REGISTRY_URL = f"http://SCHEMA_REGISTRY_SERVER:8081"
log_time(f"Kafka Bootstrap Server: {BOOTSTRAP_SERVER}")
log_time(f"Schema Registry URL: {SCHEMA_REGISTRY_URL}")


# ----------------------------------------------------------------------------
# Schema Registry 유틸리티 함수
# ----------------------------------------------------------------------------
def get_latest_schema_from_registry(subject_name):
    log_time(f"실시간 처리용 Avro 스키마 요청: {subject_name}")
    url = f"{SCHEMA_REGISTRY_URL}/subjects/{subject_name}/versions/latest"
    log_time(f"스키마 레지스트리 요청 URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        schema_info = response.json()
        log_time(f"실시간 스키마 로드 성공: {subject_name}")
        log_time(f"로드된 스키마 크기: {len(schema_info['schema'])} characters")
        return schema_info['schema']
    except requests.exceptions.RequestException as e:
        log_time(f"실시간 스키마 로드 실패: {e}")
        log_time(f"실패한 요청 URL: {url}")
        raise ConnectionError(
            f"Failed to connect to Schema Registry or retrieve schema: {e}. "
            f"Check URL and network connectivity."
        )


# ----------------------------
# 1) Debezium JSON 파싱 (MySQL CDC)
# ----------------------------
def load_debezium_users_json(spark, topic):
    try:
        log_time(f"실시간 CDC 사용자 토픽 연결: {topic}")
        raw_df = (
            spark.read.format("kafka")
            .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER)
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")
            .load()
        )
        if raw_df.rdd.isEmpty():
            log_time(f"실시간 사용자 토픽 '{topic}' 현재 데이터 없음, 빈 DataFrame 반환")
            return spark.createDataFrame([], StructType([
                StructField("user_info_id", StringType(), True),
                StructField("gender", StringType(), True),
                StructField("age", IntegerType(), True)
            ]))

        log_time("실시간 CDC 사용자 JSON 파싱 시작")
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

        user_count = final_df.count()
        log_time(f"실시간 CDC 사용자 데이터 처리 완료: {user_count}개")
        return final_df
    except Exception as e:
        log_time(f"실시간 CDC 사용자 로드 실패: {e}")
        import traceback; traceback.print_exc()
        return spark.createDataFrame([], StructType([
            StructField("user_info_id", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("age", IntegerType(), True)
        ]))


def load_debezium_sessions_json(spark, topic):
    try:
        log_time(f"실시간 CDC 세션 토픽 연결: {topic}")
        raw_df = (
            spark.read.format("kafka")
            .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER)
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")
            .load()
        )
        if raw_df.rdd.isEmpty():
            log_time(f"실시간 세션 토픽 '{topic}' 현재 데이터 없음, 빈 DataFrame 반환")
            return spark.createDataFrame([], StructType([
                StructField("session_id", StringType(), True),
                StructField("session_user_id", StringType(), True)
            ]))

        log_time("실시간 CDC 세션 JSON 파싱 시작")
        sessions_df = raw_df.selectExpr("CAST(value AS STRING) AS json_str").select(
            get_json_object("json_str", "$.op").alias("operation"),
            get_json_object("json_str", "$.after.session_id").alias("session_id"),
            get_json_object("json_str", "$.after.user_id").alias("session_user_id")
        ).filter(
            col("operation").isin(["c", "u", "r"]) & col("session_id").isNotNull()
        ).dropDuplicates(["session_id"])

        session_count = sessions_df.count()
        log_time(f"실시간 CDC 세션 데이터 처리 완료: {session_count}개")
        return sessions_df
    except Exception as e:
        log_time(f"실시간 CDC 세션 로드 실패: {e}")
        import traceback; traceback.print_exc()
        return spark.createDataFrame([], StructType([
            StructField("session_id", StringType(), True),
            StructField("session_user_id", StringType(), True)
        ]))


# -----------------------------------
# 2) 상태 저장용 Delta 테이블 설정
# -----------------------------------
STATE_TABLE_PATH = "s3a://data-catalog-bucket/data-catalog-dir/session_state/"
state_schema = StructType() \
    .add("session_id",          StringType()) \
    .add("search_count",        LongType()) \
    .add("cart_item_count",     LongType()) \
    .add("page_depth",          LongType()) \
    .add("last_event_time",     TimestampType()) \
    .add("session_start_time",  TimestampType())

log_time(f"실시간 세션 상태 테이블 경로: {STATE_TABLE_PATH}")


def ensure_delta_table(spark, path, schema):
    if not DeltaTable.isDeltaTable(spark, path):
        log_time(f"Delta 테이블 생성: {path}")
        spark.createDataFrame([], schema).write.format("delta").mode("overwrite").save(path)
    else:
        log_time(f"Delta 테이블 확인: {path}")


def get_state_df(spark):
    ensure_delta_table(spark, STATE_TABLE_PATH, state_schema)
    return DeltaTable.forPath(spark, STATE_TABLE_PATH).toDF().select(
        col("session_id").alias("sid"),
        col("page_depth").alias("prev_depth"),
        col("last_event_time").alias("prev_last_event_time"),
        col("search_count").alias("prev_search"),
        col("cart_item_count").alias("prev_cart"),
        col("session_start_time").alias("prev_session_start_time")
    )


def upsert_state(spark, updates_df):
    dt = DeltaTable.forPath(spark, STATE_TABLE_PATH)
    (
        dt.alias("t")
        .merge(
            updates_df.alias("s"),
            "t.session_id = s.session_id"
        )
        .whenMatchedUpdate(set={
            "page_depth":          col("s.page_depth"),
            "last_event_time":     col("s.last_event_time"),
            "search_count":        col("s.search_count"),
            "cart_item_count":     col("s.cart_item_count"),
            "session_start_time":  col("s.session_start_time")
        })
        .whenNotMatchedInsert(values={
            "session_id":          col("s.session_id"),
            "page_depth":          col("s.page_depth"),
            "last_event_time":     col("s.last_event_time"),
            "search_count":        col("s.search_count"),
            "cart_item_count":     col("s.cart_item_count"),
            "session_start_time":  col("s.session_start_time")
        })
        .execute()
    )
    log_time("상태 테이블 upsert 완료")


# ------------------------------------------------
# 3) nginx Avro 토픽을 스트림(readStream)으로 로드
# ------------------------------------------------
def load_kafka_avro_stream(spark, topic, avro_schema_str):
    log_time(f"실시간 Kafka Avro 스트림 초기화: {topic}")
    log_time(f"스트림용 스키마 크기: {len(avro_schema_str)} characters")
    raw = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .option("maxOffsetsPerTrigger", 600)
        .load()
        .select(expr("substring(value, 6, length(value)-5)").cast("binary").alias("avro"))
        .select(from_avro(col("avro"), avro_schema_str, {"mode": "PERMISSIVE"}).alias("d"))
    )

    log_time("실시간 Avro 스트림 디코딩 및 파싱 시작")
    result_df = raw.select(
        col("d.session_id"),
        when(col("d.user_id") == "", lit(None)).otherwise(col("d.user_id")).alias("user_id"),
        col("d.endpoint"),
        col("d.method"),
        when(col("d.endpoint") == "/search", lit(None))
        .when(col("d.endpoint") == "/product", lit(None))
        .when(col("d.query_params").rlike("query=([^&]+)"),
              expr("regexp_extract(d.query_params, 'query=([^&]+)', 1)"))
        .when(col("d.query_params").isNotNull() & (col("d.query_params") != ""),
              expr("regexp_replace(d.query_params, '^name=', '')"))
        .otherwise(lit(None)).alias("category_name"),
        when((col("d.endpoint") == "/search") & col("d.query_params").rlike("query=([^&]+)"),
             expr("regexp_extract(d.query_params, 'query=([^&]+)', 1)"))
        .otherwise(lit(None)).alias("search_keyword"),
        when(col("d.product_id") == "", lit(None)).otherwise(col("d.product_id")).alias("product_id"),
        lit(None).cast(StringType()).alias("request_body"),
        coalesce(col("d.request_time.member1"), col("d.request_time.member0").cast(DoubleType()), lit(0.0)).alias("request_time"),
        to_timestamp(col("d.timestamp"), "yyyy-MM-dd HH:mm:ss").alias("event_time"),
        col("d.endpoint").alias("current_state"),
        col("d.timestamp").alias("raw_timestamp"),
        col("d.remote_addr").alias("remote_addr"),
        col("d.request").alias("request"),
        col("d.status").alias("status"),
        col("d.body_bytes_sent").alias("body_bytes_sent"),
        col("d.upstream_response_time").alias("upstream_response_time"),
        col("d.host").alias("host"),
    ).filter(
        col("session_id").isNotNull() & (col("session_id") != "") & col("endpoint").isNotNull()
    )

    # 합성 event_id
    result_df = result_df.withColumn(
        "event_id",
        sha2(
            concat_ws(
                "§",
                col("session_id"),
                col("raw_timestamp"),
                col("endpoint"),
                col("method"),
                coalesce(col("product_id").cast("string"), lit("∅")),
                coalesce(col("category_name"), lit("∅")),
                coalesce(col("search_keyword"), lit("∅")),
                coalesce(col("remote_addr"), lit("∅")),
                coalesce(col("host"), lit("∅")),
                coalesce(col("request"), lit("∅")),
                coalesce(col("status").cast("string"), lit("∅")),
                coalesce(col("body_bytes_sent").cast("string"), lit("∅")),
                coalesce(col("request_time").cast("string"), lit("∅")),
                coalesce(col("upstream_response_time").cast("string"), lit("∅"))
            ),
            256
        )
    )

    # 워터마크 + 중복제거
    result_df = (
        result_df
        .withWatermark("event_time", "20 minutes")
        .dropDuplicates(["session_id", "event_id"])
    )
    return result_df


# ------------------------------------------------
# 4) foreach_batch - JSON CDC 처리 버전
# ------------------------------------------------
def foreach_batch_debug(logs_df, batch_id):
    try:
        log_time(f"실시간 스트림 배치 {batch_id} 처리 시작")
        spark = logs_df.sparkSession

        if logs_df.rdd.isEmpty():
            log_time("스트림 배치: 수신 데이터 없음, 다음 배치 대기")
            return

        batch_count = logs_df.count()
        log_time(f"스트림 배치: 수신된 로그 레코드 수: {batch_count}")

        filtered_df = logs_df.filter(
            col("session_id").isNotNull() & (col("session_id") != "") &
            col("endpoint").isNotNull() & col("event_time").isNotNull()
        )
        filtered_count = filtered_df.count()
        log_time(f"스트림 배치: 전체 유효성 검사 통과 레코드: {filtered_count}")
        if filtered_count == 0:
            return

        # JSON CDC 참조 로드
        try:
            log_time("스트림 배치: 실시간 CDC 참조 데이터 로드")
            sessions = load_debezium_sessions_json(spark, "mysql-server.shopdb.sessions")
            users    = load_debezium_users_json(spark, "mysql-server.shopdb.users")
            log_time("스트림 배치: 실시간 CDC 참조 데이터 준비 완료")
        except Exception as e:
            log_time(f"스트림 배치: CDC 참조 데이터 로드 실패, 빈 데이터로 처리: {e}")
            sessions = spark.createDataFrame([], StructType([
                StructField("session_id", StringType(), True),
                StructField("session_user_id", StringType(), True)
            ]))
            users = spark.createDataFrame([], StructType([
                StructField("user_info_id", StringType(), True),
                StructField("gender", StringType(), True),
                StructField("age", IntegerType(), True)
            ]))

        # 조인
        log_time("스트림 배치: 실시간 데이터 조인 시작")
        enriched = (
            filtered_df.alias("l")
            .join(sessions.alias("s"), col("l.session_id") == col("s.session_id"), "left")
            .join(
                users.alias("u"),
                (col("l.user_id") == col("u.user_info_id")) | (col("s.session_user_id") == col("u.user_info_id")),
                "left"
            )
            .select(
                col("l.session_id"),
                col("l.event_id"),
                coalesce(col("l.user_id"), col("s.session_user_id")).alias("user_id"),
                coalesce(col("u.gender"), lit(None)).alias("gender"),
                coalesce(col("u.age"), lit(None)).alias("age"),
                col("l.event_time"),
                col("l.current_state"),
                col("l.endpoint"),
                col("l.method"),
                col("l.category_name"),
                col("l.search_keyword"),
                col("l.product_id"),
                col("l.request_body"),
                col("l.request_time")
            )
        )

        # 윈도우 정의
        session_order = Window.partitionBy("session_id").orderBy(
            "event_time",
            "event_id",
            "endpoint",
            coalesce(col("product_id"), lit("")),
            coalesce(col("category_name"), lit(""))
        )
        session_full = (
            Window.partitionBy("session_id")
            .orderBy("event_time")
            .rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
        )

        # 배치 내 계산
        calculated_df = (
            enriched
            .withColumn("batch_seq", row_number().over(session_order))
            .withColumn("batch_session_start_time", first("event_time").over(session_full))
            .withColumn(
                "search_count",
                spark_sum(when(col("endpoint").like("/search%"), 1).otherwise(0)).over(
                    session_order.rowsBetween(Window.unboundedPreceding, Window.currentRow)
                )
            )
            .withColumn(
                "cart_item_count",
                spark_sum(when(col("endpoint") == "/cart/add", 1).otherwise(0)).over(
                    session_order.rowsBetween(Window.unboundedPreceding, Window.currentRow)
                )
            )
            .withColumn("prev_event_time", lag("event_time", 1).over(session_order))
            .withColumn(
                "last_action_elapsed",
                round(
                    when(
                        col("prev_event_time").isNotNull(),
                        (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_event_time"))).cast(DoubleType())
                    ).otherwise(0.0),
                    1
                )
            )
            .withColumn("next_state", lead("current_state", 1).over(session_order))
        )

        # --- 상태 조인 및 과거 이벤트 필터링 / 누적합산 ---
        ensure_delta_table(spark, STATE_TABLE_PATH, state_schema)
        prev_state = get_state_df(spark)

        # 각 세션의 배치 내 최소 event_time (세션 시작 후보)
        batch_min_event = calculated_df.groupBy("session_id").agg(
            spark_min("event_time").alias("batch_min_event_time")
        )

        # 조인 후 필요한 상태 컬럼을 일반 이름으로 노출하여 이후 참조 단순화
        with_prev = (
            calculated_df.alias("c")
            .join(prev_state.alias("p"), col("c.session_id") == col("p.sid"), "left")
            .join(batch_min_event.alias("b"), col("c.session_id") == col("b.session_id"), "left")
            # 과거 이벤트 차단
            .filter((col("p.prev_last_event_time").isNull()) | (col("c.event_time") > col("p.prev_last_event_time")))
            .select(
                col("c.*"),
                col("b.batch_min_event_time"),
                col("p.prev_session_start_time"),
                col("p.prev_depth"),
                col("p.prev_search"),
                col("p.prev_cart"),
                col("p.prev_last_event_time")
            )
            # 상태 기반 세션 시작시각 계산
            .withColumn(
                "effective_session_start_time",
                coalesce(col("prev_session_start_time"), col("batch_min_event_time"))
            )
            # 누적값에 이전 상태 합산
            .withColumn(
                "page_depth",
                (coalesce(col("prev_depth"), lit(0).cast(LongType())) + col("batch_seq")).cast(LongType())
            )
            .withColumn(
                "search_count_total",
                (coalesce(col("prev_search"), lit(0).cast(LongType())) + col("search_count")).cast(LongType())
            )
            .withColumn(
                "cart_item_count_total",
                (coalesce(col("prev_cart"), lit(0).cast(LongType())) + col("cart_item_count")).cast(LongType())
            )
            # session_duration = event_time - session_start_time(상태)
            .withColumn(
                "session_duration",
                round((unix_timestamp(col("event_time")) - unix_timestamp(col("effective_session_start_time"))).cast(DoubleType()), 1)
            )
        )

        # 평균 응답시간 (세션 단위)
        session_avg_response = with_prev.groupBy("session_id").agg(
            round(spark_avg("request_time"), 3).alias("avg_response_time")
        )

        final_df = (
            with_prev.alias("c")
            .join(session_avg_response.alias("r"), "session_id", "left")
            .select(
                col("c.session_id"),
                col("c.user_id"),
                col("c.gender"),
                col("c.age"),
                col("c.current_state"),
                col("c.search_count_total").alias("search_count"),
                col("c.cart_item_count_total").alias("cart_item_count"),
                col("c.page_depth"),
                col("c.last_action_elapsed"),
                coalesce(col("c.next_state"), col("c.current_state")).alias("next_state"),
                date_format(col("c.event_time"), "yyyy-MM-dd HH:mm:ss").alias("timestamp"),
                coalesce(col("r.avg_response_time"), col("c.request_time")).alias("avg_response_time"),
                col("c.session_duration"),
                col("c.category_name"),
                col("c.search_keyword"),
                col("c.product_id")
            )
        )

        final_count = final_df.count()
        log_time(f"스트림 배치: 실시간 최종 데이터 생성 완료: {final_count}개")

        (
            final_df.write.mode("append").format("parquet")
            .option("maxRecordsPerFile", 500000)
            .save("s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction/")
        )
        log_time(f"스트림 배치: 실시간 처리 결과 저장 완료: {final_count}개")

        # --- 상태 갱신: 이번 배치 최종값으로 일관화 (max/min) ---
        updates = (
            with_prev
            .groupBy("session_id")
            .agg(
                spark_max("page_depth").cast(LongType()).alias("page_depth"),
                spark_max(col("event_time")).alias("last_event_time"),
                spark_max("search_count_total").cast(LongType()).alias("search_count"),
                spark_max("cart_item_count_total").cast(LongType()).alias("cart_item_count"),
                spark_min("effective_session_start_time").alias("session_start_time")
            )
        )
        upsert_state(spark, updates)

    except Exception as e:
        log_time(f"스트림 배치: 실시간 처리 오류 발생: {str(e)}")
        import traceback; traceback.print_exc()


# -----------------------------------
# 5) main: 스트림 정의 및 실행
# -----------------------------------
if __name__ == "__main__":
    log_time("실시간 사용자 행동 분석 스트림 애플리케이션 시작")
    spark = (
        SparkSession.builder
        .appName("RealtimeUserBehaviorProcessorWithJSONCDC")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    log_time("실시간 처리용 Spark 세션 초기화 완료")
    spark.sparkContext.setLogLevel("WARN")

    try:
        jvm = spark.sparkContext._jvm
        jvm.org.apache.log4j.Logger.getLogger("org.apache.kafka.clients.admin.AdminClientConfig").setLevel(
            jvm.org.apache.log4j.Level.ERROR
        )
        jvm.org.apache.log4j.Logger.getLogger("org.apache.kafka.clients.consumer.ConsumerConfig").setLevel(
            jvm.org.apache.log4j.Level.ERROR
        )
        jvm.org.apache.log4j.Logger.getLogger(
            "org.apache.spark.sql.catalyst.analysis.ResolveWriteToStream"
        ).setLevel(jvm.org.apache.log4j.Level.ERROR)
        log_time("실시간 Kafka 클라이언트 설정 완료")
    except Exception as e:
        log_time(f"Kafka 클라이언트 로그 레벨 설정 실패: {e}")
        log_time("기본 로그 레벨로 진행, WARN 메시지 나타날 수 있음")

    try:
        log_time("실시간 처리용 Schema Registry 연결 시작")
        nginx_avro_schema = get_latest_schema_from_registry("nginx-topic-value")
        log_time("실시간 Nginx Avro 스키마 준비 완료")
    except Exception as e:
        log_time(f"실시간 스키마 로드 치명적 오류: {e}")
        spark.stop()
        exit(1)

    # 체크포인트
    log_time("실시간 스트림 체크포인트 설정")
    checkpoint_path = "/tmp/checkpoint/realtime_json_cdc"

    log_time("실시간 Kafka Avro 스트림 연결 시작")
    logs_df = load_kafka_avro_stream(spark, "nginx-topic", nginx_avro_schema)

    log_time("실시간 스트림 처리 쿼리 시작 (90초 간격)")
    query = (
        logs_df.writeStream
        .foreachBatch(foreach_batch_debug)
        .option("checkpointLocation", checkpoint_path)
        .trigger(processingTime="90 seconds")
        .start()
    )

    log_time("실시간 스트림 처리 실행 중... (종료: Ctrl+C)")
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        log_time("사용자 중단 신호 감지, 실시간 스트림 종료 중...")
        query.stop()
        spark.stop()
        log_time("실시간 스트림 애플리케이션 정상 종료")
    except Exception as e:
        log_time(f"실시간 스트림 처리 오류: {e}")
        import traceback; traceback.print_exc()
        query.stop()
        spark.stop()
        log_time("실시간 스트림 애플리케이션 오류 종료")
