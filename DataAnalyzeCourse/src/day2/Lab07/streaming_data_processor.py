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
    max as spark_max,
    to_timestamp,
    from_utc_timestamp, 
    to_utc_timestamp,
    trim
)
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType,
    IntegerType, TimestampType, DoubleType, BooleanType
)
from delta.tables import DeltaTable


# --- 환경 변수 로드 ---
def log_time(message):
    """현재 시간과 함께 메시지를 출력하는 함수"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


log_time("실시간 스트림 처리 환경 변수 로드 시작")
BOOTSTRAP_SERVER = "KAFKA_BOOTSTRAP_SERVERS"
SCHEMA_REGISTRY_URL = f"http://SCHEMA_REGISTRY_SERVER:8081"
log_time(f"Kafka Bootstrap Server: {BOOTSTRAP_SERVER}")
log_time(f"Schema Registry URL: {SCHEMA_REGISTRY_URL}")


# ----------------------------------------------------------------------------
# Schema Registry 유틸리티 함수
# ----------------------------------------------------------------------------
def get_latest_schema_from_registry(subject_name):
    """
    Schema Registry에서 특정 주제(Subject)의 최신 Avro 스키마를 가져옵니다.
    네트워크 요청을 통해 스키마를 동적으로 로드합니다.
    """
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
        raise ConnectionError(f"Failed to connect to Schema Registry or retrieve schema: {e}. Check URL and network connectivity.")


# ----------------------------
# 1) Debezium JSON 파싱 (MySQL CDC)
# ----------------------------
def load_debezium_users_json(spark, topic):
    """Debezium users 토픽에서 JSON 데이터를 로드하고 파싱합니다."""
    try:
        log_time(f"실시간 CDC 사용자 토픽 연결: {topic}")
        
        raw_df = (
            spark.read
                 .format("kafka")
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
        import traceback
        traceback.print_exc()
        return spark.createDataFrame([], StructType([
            StructField("user_info_id", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("age", IntegerType(), True)
        ]))


def load_debezium_sessions_json(spark, topic):
    """Debezium sessions 토픽에서 JSON 데이터를 로드하고 파싱합니다."""
    try:
        log_time(f"실시간 CDC 세션 토픽 연결: {topic}")
        
        raw_df = (
            spark.read
                 .format("kafka")
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
            col("operation").isin(["c", "u", "r"]) &
            col("session_id").isNotNull()
        ).dropDuplicates(["session_id"])


        session_count = sessions_df.count()
        log_time(f"실시간 CDC 세션 데이터 처리 완료: {session_count}개")
        return sessions_df
        
    except Exception as e:
        log_time(f"실시간 CDC 세션 로드 실패: {e}")
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


log_time(f"실시간 세션 상태 테이블 경로: {STATE_TABLE_PATH}")


# ------------------------------------------------
# 3) nginx Avro 토픽을 스트림(readStream)으로 로드
# ------------------------------------------------
def load_kafka_avro_stream(spark, topic, avro_schema_str):
    """
    Kafka에서 Avro 형식의 Nginx 로그를 스트림으로 로드하고 파싱합니다.
    구조체 타입의 request_time을 올바르게 처리합니다.
    """
    log_time(f"실시간 Kafka Avro 스트림 초기화: {topic}")
    log_time(f"스트림용 스키마 크기: {len(avro_schema_str)} characters")
    
    raw = (
        spark.readStream
             .format("kafka")
             .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER)
             .option("subscribe", topic)
             .option("startingOffsets", "latest")
             .option("failOnDataLoss", "false")
             .option("maxOffsetsPerTrigger", 200)
             .load()
        .select(expr("substring(value, 6, length(value)-5)").cast("binary").alias("avro"))
        .select(from_avro(col("avro"), avro_schema_str, {"mode": "PERMISSIVE"}).alias("d"))
    )


    log_time("실시간 Avro 스트림 디코딩 및 파싱 시작")
    
    # 구조체 타입 필드들을 올바르게 처리
    result_df = raw.select(
        col("d.session_id"),
        when(col("d.user_id") == "", lit(None)).otherwise(col("d.user_id")).alias("user_id"),
        col("d.endpoint"),
        col("d.method"),
        # query_params 처리: /search가 아닌 경우만 처리, /search인 경우는 null
        when(col("d.endpoint") == "/search", lit(None))
        .when(col("d.query_params").rlike("query=([^&]+)"), 
              expr("regexp_extract(d.query_params, 'query=([^&]+)', 1)"))
        .when(col("d.query_params").isNotNull() & (col("d.query_params") != ""), 
              col("d.query_params"))
        .otherwise(lit(None))
        .alias("query_params"),
        # search_keyword 처리: /search인 경우만 추출
        when((col("d.endpoint") == "/search") & col("d.query_params").rlike("query=([^&]+)"), 
             expr("regexp_extract(d.query_params, 'query=([^&]+)', 1)"))
        .otherwise(lit(None))
        .alias("search_keyword"),
        when(col("d.product_id") == "", lit(None)).otherwise(col("d.product_id")).alias("product_id"),
        # request_body가 스키마에 없으므로 null로 대체
        lit(None).cast(StringType()).alias("request_body"),
        # request_time 처리: 구조체에서 안전하게 값 추출 (배치와 동일한 방식)
        coalesce(
            col("d.request_time.member1"), 
            col("d.request_time.member0").cast(DoubleType()), 
            lit(0.0)
        ).alias("request_time"),
        # timestamp 처리
        to_timestamp(col("d.timestamp"), "yyyy-MM-dd HH:mm:ss").alias("event_time"),
        # current_state 간소화: 단순히 endpoint만 사용
        col("d.endpoint").alias("current_state"),
        # 디버깅용 원본 timestamp
        col("d.timestamp").alias("raw_timestamp")
    ).filter(
        # 필터링 조건
        col("session_id").isNotNull() &
        (col("session_id") != "") &
        col("endpoint").isNotNull()
    )
    
    return result_df


# ------------------------------------------------
# 4) foreach_batch - JSON CDC 처리 버전
# ------------------------------------------------
def foreach_batch_debug(logs_df, batch_id):
    """
    세션별 page_depth와 session_duration을 올바르게 계산하는 배치 처리 함수
    """
    try:
        log_time(f"실시간 스트림 배치 {batch_id} 처리 시작")
        spark = logs_df.sparkSession
        
        # 단계별 디버깅
        log_time(f"스트림 배치: 수신 데이터 존재 여부 확인")
        if logs_df.rdd.isEmpty():
            log_time(f"스트림 배치: 수신 데이터 없음, 다음 배치 대기")
            return


        # 원본 데이터 확인
        log_time(f"스트림 배치: 수신 로그 데이터 카운트 중")
        batch_count = logs_df.count()
        log_time(f"스트림 배치: 수신된 로그 레코드 수: {batch_count}")


        if batch_count > 0:
            # 샘플 데이터 출력
            log_time(f"스트림 배치: 수신 데이터 샘플 검증")
            sample_data = logs_df.limit(3).collect()
            
            # event_time null 체크
            null_event_time_count = logs_df.filter(col("event_time").isNull()).count()
            log_time(f"스트림 배치: event_time 누락 레코드: {null_event_time_count}")
            
            # 개별 조건별 확인
            session_ok = logs_df.filter(col("session_id").isNotNull() & (col("session_id") != "")).count()
            endpoint_ok = logs_df.filter(col("endpoint").isNotNull()).count()
            event_time_ok = logs_df.filter(col("event_time").isNotNull()).count()
            
            
            # 필터링 후 데이터 확인
            filtered_df = logs_df.filter(
                col("session_id").isNotNull() & 
                (col("session_id") != "") &
                col("endpoint").isNotNull() &
                col("event_time").isNotNull()
            )
            filtered_count = filtered_df.count()
            log_time(f"스트림 배치: 전체 유효성 검사 통과 레코드: {filtered_count}")
            
            if filtered_count == 0:
                log_time(f"스트림 배치: 모든 데이터가 필터링됨, 디버그 모드로 저장")
                
                # 조건 완화: event_time 조건만 제거
                relaxed_df = logs_df.filter(
                    col("session_id").isNotNull() & 
                    (col("session_id") != "") &
                    col("endpoint").isNotNull()
                )
                relaxed_count = relaxed_df.count()
                log_time(f"스트림 배치: event_time 조건 제거 후 데이터 수: {relaxed_count}")
                
                if relaxed_count > 0:
                    # 조건 완화된 데이터로 저장
                    relaxed_df.select(
                        col("session_id"),
                        col("user_id"),
                        col("endpoint"),
                        col("raw_timestamp"),
                        col("event_time"),
                        col("current_state"),
                        col("query_params"),
                        col("search_keyword"),
                        col("product_id"),
                        lit(1).alias("page_depth"),
                        lit("DEBUG").alias("status")
                    ).write.mode("append").format("parquet") \
                     .option("maxRecordsPerFile", 500000) \
                     .save("s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction_debug/")
                    
                    log_time(f"스트림 배치: 디버그 데이터 저장 완료: {relaxed_count}개")
                
                return
            
            # 정상 처리: 필터링된 데이터로 저장
            log_time(f"스트림 배치: 정상 데이터로 실시간 처리 진행")
            
            # JSON 방식으로 CDC 데이터 로드
            try:
                log_time(f"스트림 배치: 실시간 CDC 참조 데이터 로드")
                sessions = load_debezium_sessions_json(spark, "mysql-server.shopdb.sessions")
                users = load_debezium_users_json(spark, "mysql-server.shopdb.users")
                log_time(f"스트림 배치: 실시간 CDC 참조 데이터 준비 완료")
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


            # 데이터 조인
            log_time(f"스트림 배치: 실시간 데이터 조인 시작")
            enriched = (
                filtered_df.alias("l")
                .join(sessions.alias("s"), col("l.session_id") == col("s.session_id"), "left")
                .join(users.alias("u"), 
                      (col("l.user_id") == col("u.user_info_id")) |
                      (col("s.session_user_id") == col("u.user_info_id")), "left")
                .select(
                    col("l.session_id"),
                    coalesce(col("l.user_id"), col("s.session_user_id")).alias("user_id"),
                    coalesce(col("u.gender"), lit(None)).alias("gender"),
                    coalesce(col("u.age"), lit(None)).alias("age"),
                    col("l.event_time"),
                    col("l.current_state"),
                    col("l.endpoint"),
                    col("l.method"),
                    col("l.query_params"),
                    col("l.search_keyword"),
                    col("l.product_id"),
                    col("l.request_body"),
                    col("l.request_time")
                )
            )
            
            enriched_count = enriched.count()
            log_time(f"스트림 배치: 실시간 데이터 조인 완료: {enriched_count}개")
            
            # 윈도우 함수로 세션별 계산
            log_time(f"스트림 배치: 실시간 세션 상태 계산 시작")
            
            # 세션별 시간 순 윈도우
            session_window = Window.partitionBy("session_id").orderBy(
                "event_time", 
                "endpoint", 
                coalesce("product_id", lit("")),
                coalesce("query_params", lit(""))
            )

            # 세션별 전체 범위 윈도우 (첫 번째 이벤트 시간 계산용)
            session_full_window = Window.partitionBy("session_id").orderBy(
                "event_time", 
                "endpoint"
            ).rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)

            # 계산된 컬럼들 추가
            calculated_df = enriched.withColumn(
                # page_depth: 세션별 순서 (1부터 시작) - 이제 결정적 순서 보장
                "page_depth", row_number().over(session_window)
            ).withColumn(
                # 세션 시작 시간 (세션별 첫 번째 이벤트 시간)
                "session_start_time", first("event_time").over(session_full_window)
            ).withColumn(
                # session_duration: 세션 시작부터 현재까지 경과 시간 (초)
                "session_duration",
                round((unix_timestamp(col("event_time")) - unix_timestamp(col("session_start_time"))).cast(DoubleType()), 1)
            )
            
            # 계산된 컬럼들 추가
            calculated_df = enriched.withColumn(
                # page_depth: 세션별 순서 (1부터 시작)
                "page_depth", row_number().over(session_window)
            ).withColumn(
                # 세션 시작 시간 (세션별 첫 번째 이벤트 시간)
                "session_start_time", first("event_time").over(session_full_window)
            ).withColumn(
                # session_duration: 세션 시작부터 현재까지 경과 시간 (초)
                "session_duration", 
                round((unix_timestamp(col("event_time")) - unix_timestamp(col("session_start_time"))).cast(DoubleType()), 1)
            ).withColumn(
                # search_count: 현재까지 세션에서 /search 횟수
                "search_count", 
                spark_sum(when(col("endpoint").like("/search%"), 1).otherwise(0)).over(
                    session_window.rowsBetween(Window.unboundedPreceding, Window.currentRow)
                )
            ).withColumn(
                # cart_item_count: 현재까지 세션에서 /cart/add 횟수
                "cart_item_count", 
                spark_sum(when(col("endpoint") == "/cart/add", 1).otherwise(0)).over(
                    session_window.rowsBetween(Window.unboundedPreceding, Window.currentRow)
                )
            ).withColumn(
                # 이전 이벤트 시간 (지연 시간 계산용)
                "prev_event_time", lag("event_time", 1).over(session_window)
            ).withColumn(
                # last_action_elapsed: 이전 액션으로부터 경과 시간
                "last_action_elapsed",
                round(when(col("prev_event_time").isNotNull(), 
                          (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_event_time"))).cast(DoubleType())
                     ).otherwise(0.0), 1)
            ).withColumn(
                # next_state: 다음 상태 (현재는 동일하게 설정)
                "next_state", lead("current_state", 1).over(session_window)
            )
            
            calculated_count = calculated_df.count()
            log_time(f"스트림 배치: 실시간 세션 상태 계산 완료: {calculated_count}개")
            
            # 세션별 평균 응답 시간 계산
            session_avg_response = calculated_df.groupBy("session_id").agg(
                round(expr("avg(request_time)"), 3).alias("avg_response_time")
            )
            
            # 최종 데이터 조인 및 저장
            final_df = calculated_df.alias("c").join(
                session_avg_response.alias("r"), 
                col("c.session_id") == col("r.session_id"), "left"
            ).select(
                col("c.session_id"),
                col("c.user_id"),
                col("c.gender"),
                col("c.age"),
                col("c.current_state"),
                col("c.search_count"),
                col("c.cart_item_count"),
                col("c.page_depth"),
                col("c.last_action_elapsed"),
                coalesce(col("c.next_state"), col("c.current_state")).alias("next_state"),
                date_format(col("c.event_time"), "yyyy-MM-dd HH:mm:ss").alias("timestamp"),
                coalesce(col("r.avg_response_time"), col("c.request_time")).alias("avg_response_time"),
                col("c.product_id").cast(IntegerType()).alias("current_product_id"),
                col("c.session_duration"),
                col("c.query_params"),
                col("c.search_keyword"),
                col("c.product_id")
            )
            
            final_count = final_df.count()
            log_time(f"스트림 배치: 실시간 최종 데이터 생성 완료: {final_count}개")
            
            # Parquet 저장
            final_df.write.mode("append").format("parquet") \
                    .option("maxRecordsPerFile", 500000) \
                    .save("s3a://data-catalog-bucket/data-catalog-dir/user_behavior_prediction/")
            
            log_time(f"스트림 배치: 실시간 처리 결과 저장 완료: {final_count}개")
            
        
    except Exception as e:
        log_time(f"스트림 배치: 실시간 처리 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()



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
    
    # WARN AdminClientConfig 경고를 숨기는 코드
    try:
        jvm = spark.sparkContext._jvm
        jvm.org.apache.log4j.Logger.getLogger("org.apache.kafka.clients.admin.AdminClientConfig").setLevel(jvm.org.apache.log4j.Level.ERROR)
        jvm.org.apache.log4j.Logger.getLogger("org.apache.kafka.clients.consumer.ConsumerConfig").setLevel(jvm.org.apache.log4j.Level.ERROR)
        jvm.org.apache.log4j.Logger.getLogger("org.apache.spark.sql.catalyst.analysis.ResolveWriteToStream").setLevel(jvm.org.apache.log4j.Level.ERROR)
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


    # 체크포인트 초기화
    log_time("실시간 스트림 체크포인트 설정")
    checkpoint_path = "/tmp/checkpoint/realtime_json_cdc"
    
    log_time("실시간 Kafka Avro 스트림 연결 시작")
    logs_df = load_kafka_avro_stream(spark, "nginx-topic", nginx_avro_schema) 


    log_time("실시간 스트림 처리 쿼리 시작 (30초 간격)")
    query = (logs_df.writeStream
        .foreachBatch(foreach_batch_debug)  # 디버그 함수 사용
        .option("checkpointLocation", checkpoint_path) 
        .trigger(processingTime="30 seconds")  # 더 짧은 간격
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
        import traceback
        traceback.print_exc()
        query.stop()
        spark.stop()
        log_time("실시간 스트림 애플리케이션 오류 종료")
