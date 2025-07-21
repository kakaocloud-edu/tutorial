#!/usr/bin/env python3

import os
import time
import requests
import json
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, expr, when, coalesce, lit, broadcast, concat,
    date_format, unix_timestamp, to_timestamp,
    lag, lead, row_number, round,
    trim,
    sum as spark_sum,
    max as spark_max
)
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType,
    IntegerType, TimestampType, DoubleType, BooleanType
)
from pyspark.sql.utils import AnalysisException
from delta.tables import DeltaTable

# --- 환경 변수 로드 ---
print("[CONFIG] 환경 변수 로드 시작")
SCHEMA_REGISTRY_URL = f"http://SCHEMA_REGISTRY_SERVER:8081"
print(f"[CONFIG] SCHEMA_REGISTRY_URL: {SCHEMA_REGISTRY_URL}")

# --- 로깅 함수 정의 ---
def log_time(message):
    """현재 시간과 함께 메시지를 출력하는 함수"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

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

# ----------------------------------------------------------------------------
# Schema Registry 유틸리티 함수
# ----------------------------------------------------------------------------
def get_latest_schema_from_registry(subject_name):
    """
    Schema Registry에서 특정 주제(Subject)의 최신 Avro 스키마를 가져옵니다.
    네트워크 요청을 통해 스키마를 동적으로 로드합니다.
    """
    log_time(f"스키마 레지스트리에서 스키마 요청 시작: {subject_name}")
    url = f"{SCHEMA_REGISTRY_URL}/subjects/{subject_name}/versions/latest"
    log_time(f"요청 URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        schema_info = response.json()
        log_time(f"스키마 성공적으로 가져옴: {subject_name}")
        log_time(f"스키마 크기: {len(schema_info['schema'])} characters")
        return schema_info['schema']
    except requests.exceptions.RequestException as e:
        log_time(f"스키마 로드 실패: {e}")
        log_time(f"실패 URL: {url}")
        raise ConnectionError(f"Failed to connect to Schema Registry or retrieve schema: {e}. Check URL and network connectivity.")

def convert_avro_to_spark_schema(avro_schema_str):
    """
    Avro 스키마 문자열을 Spark DataFrame 스키마로 변환합니다.
    """
    try:
        avro_schema = json.loads(avro_schema_str)
        log_time("Avro 스키마를 Spark 스키마로 변환 중...")
        
        # 기본적으로 Spark가 Avro 스키마를 자동으로 처리할 수 있도록 
        # 스키마 문자열 자체를 반환하고, 실제 변환은 Spark에 위임
        return avro_schema_str
        
    except json.JSONDecodeError as e:
        log_time(f"Avro 스키마 파싱 실패: {e}")
        raise ValueError(f"Invalid Avro schema format: {e}")

# ==============================================================================
# 1. 데이터 로드 함수 정의 (S3 소스)
# ==============================================================================

def load_debezium_users_batch(spark, path):
    empty_df = spark.createDataFrame([], StructType([
        StructField("user_info_id", StringType(), True), 
        StructField("gender", StringType(), True), 
        StructField("age", IntegerType(), True)
    ]))
    
    try:
        log_time(f"사용자 데이터 로드 시작: {path}")
        raw_df = spark.read.json(path)
        if raw_df.rdd.isEmpty(): 
            log_time("사용자 데이터가 비어있음")
            return empty_df
        
        parsed_df = raw_df.select(
            col("op").alias("operation"), 
            col("after.user_id").alias("user_info_id"), 
            col("after.gender").alias("gender"), 
            col("after.age").cast("int").alias("age")
        )
        
        result_df = parsed_df.filter(
            col("operation").isin(["c", "u", "r"]) & 
            col("user_info_id").isNotNull() & 
            (col("user_info_id") != "") & 
            col("gender").isin(["M", "F"]) & 
            col("age").between(1, 120)
        ).dropDuplicates(["user_info_id"])
        
        log_time(f"사용자 데이터 로드 완료: {result_df.count()}개")
        return result_df
        
    except AnalysisException:
        log_time(f"경고: 사용자 데이터 경로를 찾을 수 없습니다: {path}")
        return empty_df

def load_debezium_sessions_batch(spark, path):
    empty_df = spark.createDataFrame([], StructType([
        StructField("session_id", StringType(), True), 
        StructField("session_user_id", StringType(), True)
    ]))
    
    try:
        log_time(f"세션 데이터 로드 시작: {path}")
        raw_df = spark.read.json(path)
        if raw_df.rdd.isEmpty(): 
            log_time("세션 데이터가 비어있음")
            return empty_df
        
        sessions_df = raw_df.select(
            col("op").alias("operation"), 
            col("after.session_id").alias("session_id"), 
            col("after.user_id").alias("session_user_id")
        )
        
        result_df = sessions_df.filter(
            col("operation").isin(["c", "u", "r"]) & 
            col("session_id").isNotNull()
        ).dropDuplicates(["session_id"])
        
        log_time(f"세션 데이터 로드 완료: {result_df.count()}개")
        return result_df
        
    except AnalysisException:
        log_time(f"경고: 세션 데이터 경로를 찾을 수 없습니다: {path}")
        return empty_df

def load_nginx_logs_batch(spark, path, nginx_schema_str):
    empty_df = spark.createDataFrame([], StructType([
        StructField("session_id", StringType(), True), 
        StructField("user_id", StringType(), True), 
        StructField("endpoint", StringType(), True), 
        StructField("method", StringType(), True), 
        StructField("query_params", StringType(), True),
        StructField("search_keyword", StringType(), True),
        StructField("product_id", StringType(), True), 
        StructField("request_body", StringType(), True), 
        StructField("event_time", TimestampType(), True),
        StructField("request_time", DoubleType(), True),
        StructField("current_state", StringType(), True)
    ]))
    
    try:
        log_time(f"Nginx 로그 데이터 로드 시작: {path}")
        log_time("Parquet 파일 로드")
        
        # Parquet 파일 로드
        raw_df = spark.read.option("recursiveFileLookup", "true").parquet(path)
        
        if raw_df.rdd.isEmpty(): 
            log_time("Nginx 로그 데이터가 비어있음")
            return empty_df
        
        # 전체 데이터 수 확인
        total_count = raw_df.count()
        log_time(f"전체 원본 데이터 수: {total_count}")
        
        # 동적으로 컬럼 존재 여부 확인
        available_columns = raw_df.columns
        
        # 필요한 컬럼들이 존재하는지 확인하고 선택
        select_columns = []
        
        if "session_id" in available_columns:
            select_columns.append(col("session_id"))
        else:
            log_time("경고: session_id 컬럼이 없습니다")
            return empty_df
            
        if "user_id" in available_columns:
            select_columns.append(when(col("user_id") == "", lit(None)).otherwise(col("user_id")).alias("user_id"))
        else:
            select_columns.append(lit(None).alias("user_id"))
            
        if "endpoint" in available_columns:
            select_columns.append(col("endpoint"))
        else:
            log_time("경고: endpoint 컬럼이 없습니다")
            return empty_df
            
        if "method" in available_columns:
            select_columns.append(col("method"))
        else:
            select_columns.append(lit(None).alias("method"))
            
        if "query_params" in available_columns:
            # /search가 아닌 경우만 query_params 처리, /search인 경우는 null
            select_columns.append(
                when(col("endpoint") == "/search", lit(None))
                .when(col("query_params").rlike("query=([^&]+)"), 
                     expr("regexp_extract(query_params, 'query=([^&]+)', 1)"))
                .when(col("query_params").isNotNull() & (col("query_params") != ""), 
                      col("query_params"))
                .otherwise(lit(None))
                .alias("query_params")
            )
            # 검색 키워드는 /search인 경우만 추출
            select_columns.append(
                when((col("endpoint") == "/search") & col("query_params").rlike("query=([^&]+)"), 
                     expr("regexp_extract(query_params, 'query=([^&]+)', 1)"))
                .otherwise(lit(None))
                .alias("search_keyword")
            )
        else:
            select_columns.append(lit(None).alias("query_params"))
            select_columns.append(lit(None).alias("search_keyword"))
            
        if "product_id" in available_columns:
            select_columns.append(when(col("product_id") == "", lit(None)).otherwise(col("product_id")).alias("product_id"))
        else:
            select_columns.append(lit(None).alias("product_id"))
            
        if "request_body" in available_columns:
            select_columns.append(col("request_body"))
        else:
            select_columns.append(lit(None).alias("request_body"))
            
        if "timestamp" in available_columns:
            # 여러 형식 시도
            select_columns.append(
                coalesce(
                    # 형식 1: "dd/MMM/yyyy:HH:mm:ss Z"
                    to_timestamp(col("timestamp"), "dd/MMM/yyyy:HH:mm:ss Z"),
                    # 형식 2: "yyyy-MM-dd HH:mm:ss"
                    to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"),
                    # 형식 3: "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
                    to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"),
                    # 형식 4: epoch timestamp
                    when(col("timestamp").rlike("^[0-9]+$"), 
                         to_timestamp(col("timestamp").cast("long"))),
                    # 기본값: 현재 시간
                    lit(None)
                ).alias("event_time")
            )
        else:
            log_time("경고: timestamp 컬럼이 없습니다")
            return empty_df
            
        # request_time 처리 개선 (복잡한 구조체 타입 처리)
        if "request_time" in available_columns:
            try:
                # 구조체 타입인 경우를 고려한 처리
                select_columns.append(
                    when(col("request_time").isNotNull(), 
                         # 구조체의 member1 필드 사용 (Double 타입)
                         coalesce(col("request_time.member1"), 
                                 # 만약 member1이 없으면 member0을 double로 캐스팅 시도
                                 col("request_time.member0").cast(DoubleType()),
                                 # 그것도 실패하면 전체를 문자열로 변환 후 double로 캐스팅
                                 expr("cast(request_time as string)").cast(DoubleType()),
                                 lit(0.0)))
                    .otherwise(lit(0.0))
                    .alias("request_time")
                )
            except Exception as e:
                log_time(f"request_time 처리 중 오류: {e}")
                select_columns.append(lit(0.0).alias("request_time"))
        else:
            select_columns.append(lit(0.0).alias("request_time"))
        
        # 변환된 DataFrame 생성
        log_time("데이터 변환 시작")
        transformed_df = raw_df.select(*select_columns)
        
        # 변환 후 데이터 수 확인
        transformed_count = transformed_df.count()
        log_time(f"변환 후 데이터 수: {transformed_count}")
        
        # current_state 생성 로직 간소화 - 단순히 endpoint만 사용
        log_time("current_state를 endpoint로 간소화")
        with_current_state = transformed_df.withColumn("current_state", col("endpoint"))
        
        # 단계별 필터링 확인
        log_time("필터링 조건별 데이터 수 확인:")
        
        # 1. session_id 체크
        session_id_ok = with_current_state.filter(col("session_id").isNotNull()).count()
        log_time(f"session_id not null: {session_id_ok}")
        
        # 2. session_id trim 체크
        session_id_trim_ok = with_current_state.filter(
            (col("session_id").isNotNull()) & (trim(col("session_id")) != "")
        ).count()
        log_time(f"session_id not null and not empty: {session_id_trim_ok}")
        
        # 3. endpoint 체크
        endpoint_ok = with_current_state.filter(
            (col("session_id").isNotNull()) & 
            (trim(col("session_id")) != "") & 
            col("endpoint").isNotNull()
        ).count()
        log_time(f"endpoint not null: {endpoint_ok}")
        
        # 4. event_time 체크
        event_time_ok = with_current_state.filter(
            (col("session_id").isNotNull()) & 
            (trim(col("session_id")) != "") & 
            col("endpoint").isNotNull() & 
            col("event_time").isNotNull()
        ).count()
        log_time(f"event_time not null: {event_time_ok}")
        
        # 최종 필터링 적용
        result_df = with_current_state.filter(
            (col("session_id").isNotNull()) &
            (trim(col("session_id")) != "") &
            col("endpoint").isNotNull() &
            col("event_time").isNotNull()
        )
        
        result_count = result_df.count()
        log_time(f"최종 필터링 후 데이터 수: {result_count}")
        
        # 만약 event_time이 문제라면 조건 완화
        if result_count == 0 and event_time_ok == 0:
            log_time("event_time 조건 때문에 데이터가 모두 제거됨. 조건 완화 시도")
            result_df = with_current_state.filter(
                (col("session_id").isNotNull()) &
                (trim(col("session_id")) != "") &
                col("endpoint").isNotNull()
            )
            result_count = result_df.count()
            log_time(f"event_time 조건 제거 후 데이터 수: {result_count}")
        
        log_time(f"Nginx 로그 데이터 로드 완료: {result_count}개")
        return result_df
        
    except AnalysisException as e:
        if "Path does not exist" in str(e):
            log_time(f"정보: Nginx 로그 경로를 찾을 수 없습니다: {path}")
        else:
            log_time(f"Nginx 로그 데이터 로드 중 오류 발생: {e}")
        return empty_df
    except Exception as e:
        log_time(f"Nginx 로그 데이터 로드 중 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        return empty_df

# ==============================================================================
# 2. 사용자 행동 데이터 처리 함수
# ==============================================================================

def process_user_behavior_batch(logs_df, sessions_df, users_df, spark):
    try:
        log_time("사용자 행동 데이터 처리 시작")
        
        if logs_df.rdd.isEmpty():
            log_time("처리할 Nginx 로그 데이터가 없어 건너뜁니다.")
            return
        
        is_delta_table = DeltaTable.isDeltaTable(spark, STATE_TABLE_PATH_BATCH)
        
        if is_delta_table:
            state_df = spark.read.format("delta").load(STATE_TABLE_PATH_BATCH)
            log_time(f"기존 상태 테이블 로드 완료: {state_df.count()}개")
        else:
            log_time(f"정보: Delta 상태 테이블({STATE_TABLE_PATH_BATCH})이 없어, 빈 상태로 시작합니다.")
            state_df = spark.createDataFrame([], state_schema)
        
        log_time("로그, 세션, 사용자 데이터 조인 시작")
        
        logs_sessions_joined = logs_df.alias("l") \
            .join(broadcast(sessions_df.alias("s")), col("l.session_id") == col("s.session_id"), "left")
        
        base_with_userid = logs_sessions_joined.withColumn("final_user_id", coalesce(col("l.user_id"), col("s.session_user_id")))
        
        enriched = base_with_userid \
            .join(broadcast(users_df.alias("u")), col("final_user_id") == col("u.user_info_id"), "left") \
            .select(
                col("l.session_id").alias("session_id"), 
                col("final_user_id").alias("user_id"),
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
        
        log_time("데이터 조인 완료. 캐싱 및 카운팅 시작")
        
        enriched.cache()
        enriched_count = enriched.count()
        log_time(f"캐싱 및 카운팅 완료. Enriched DF 레코드 수: {enriched_count}")
        
        if enriched_count == 0:
            spark.catalog.clearCache()
            return
        
        log_time("윈도우 함수 및 상태 계산 시작")
        
        window_spec = Window.partitionBy("session_id").orderBy("event_time")
        
        # 세션별 첫 번째 이벤트 시간 계산
        session_window = Window.partitionBy("session_id").orderBy("event_time").rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
        
        # 검색과 장바구니 추가 카운트 계산 (endpoint 기준으로)
        batch_flagged = enriched.withColumn("batch_search", when(col("endpoint").like("/search%"), 1).otherwise(0)) \
            .withColumn("batch_cart", when(col("endpoint") == "/cart/add", 1).otherwise(0)) \
            .withColumn("prev_state", lag("current_state", 1).over(window_spec)) \
            .withColumn("prev_time", lag("event_time", 1).over(window_spec)) \
            .withColumn("session_start_time", expr("first_value(event_time) OVER (PARTITION BY session_id ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)"))
        
        # 중복 제거 후 추가 컬럼들 계산
        dedup = batch_flagged.filter(col("prev_time").isNull() | (~((col("current_state") == col("prev_state")) & (col("event_time") == col("prev_time")))))
        
        dedup = dedup.withColumn("batch_search_cum", expr("sum(batch_search) OVER (PARTITION BY session_id ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)")) \
            .withColumn("batch_cart_cum", expr("sum(batch_cart) OVER (PARTITION BY session_id ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)")) \
            .withColumn("current_product_id", when(col("product_id").isNotNull() & (col("product_id") != ""), col("product_id").cast(IntegerType())).otherwise(lit(None))) \
            .withColumn("session_duration", (unix_timestamp(col("event_time")) - unix_timestamp(col("session_start_time"))).cast(DoubleType()))
        
        # 세션별 평균 응답 시간 계산
        session_avg_response = dedup.groupBy("session_id").agg(
            expr("avg(request_time)").alias("avg_response_time")
        )
        
        # merged DataFrame에 조인
        merged = dedup.alias("b").join(state_df.alias("s"), col("b.session_id") == col("s.session_id"), "left") \
            .join(session_avg_response.alias("r"), col("b.session_id") == col("r.session_id"), "left") \
            .select(
                col("b.session_id"), 
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
                lead(col("b.current_state"), 1).over(Window.partitionBy(col("b.session_id")).orderBy(col("b.event_time"))).alias("next_state"),
                round(coalesce(col("r.avg_response_time"), lit(0.0)), 3).alias("avg_response_time"),
                col("b.current_product_id"),
                round(col("b.session_duration"), 1).alias("session_duration"),
                col("b.query_params"),
                col("b.search_keyword"),
                col("b.product_id")
            ).withColumn("last_action_elapsed",
                when(col("prev_time").isNotNull(), (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_time"))).cast(DoubleType()))
                .when(col("prev_batch_time").isNotNull(), (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_batch_time"))).cast(DoubleType()))
                .otherwise(lit(0.0)))
        
        merged = merged.withColumn("page_depth", col("prev_page_depth") + row_number().over(Window.partitionBy("session_id").orderBy("event_time"))).drop("prev_page_depth", "prev_time", "prev_batch_time")
        
        final_df = merged.withColumn("search_count", col("search_count").cast(IntegerType())) \
            .withColumn("cart_item_count", col("cart_item_count").cast(IntegerType())) \
            .withColumn("page_depth", col("page_depth").cast(IntegerType())) \
            .withColumn("last_action_elapsed", round(col("last_action_elapsed"), 1)) \
            .dropDuplicates(["session_id", "user_id", "current_state", "page_depth"])
        
        log_time("윈도우 함수 및 상태 계산 완료. 최종 DF 생성 및 persist 시작")
        
        final_df.persist()
        final_df_count = final_df.count()
        log_time(f"최종 DF persist 및 카운팅 완료. 레코드 수: {final_df_count}")
        
        if final_df_count == 0:
            log_time("최종 DataFrame이 비어있어 저장 및 상태 업데이트를 건너뜁니다.")
            final_df.unpersist()
            return
        
        log_time("최종 결과 Parquet으로 저장 시작")
        
        # 최종 결과 저장 - endpoint 컬럼 제거됨
        final_df.select(
            col("session_id"),
            col("user_id"),
            col("gender"),
            col("age"),
            col("current_state"),
            col("search_count"),
            col("cart_item_count"),
            col("page_depth"),
            col("last_action_elapsed"),
            col("next_state"),
            date_format(col("event_time"), "yyyy-MM-dd HH:mm:ss").alias("timestamp"),
            col("avg_response_time"),
            col("current_product_id"),
            col("session_duration"),
            col("query_params"),
            col("search_keyword"),
            col("product_id")
        ) \
        .write.mode("append").format("parquet") \
        .option("maxRecordsPerFile", 500000).save(FINAL_OUTPUT_PATH_BATCH)
        
        log_time("최종 결과 저장 완료")
        
        log_time("새로운 상태 계산 시작")
        
        new_state = final_df.groupBy("session_id").agg(
            spark_max("search_count").alias("search_count"), 
            spark_max("cart_item_count").alias("cart_item_count"), 
            spark_max("page_depth").alias("page_depth"), 
            spark_max("event_time").alias("last_event_time")
        )
        
        log_time("새로운 상태 계산 완료")
        
        final_df.unpersist()
        
        if is_delta_table:
            log_time("기존 Delta 상태 테이블에 새로운 상태를 병합합니다.")
            DeltaTable.forPath(spark, STATE_TABLE_PATH_BATCH).alias("s").merge(
                new_state.alias("n"), "s.session_id = n.session_id"
            ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
        else:
            log_time("Delta 상태 테이블이 없으므로, 현재 상태로 새로 생성합니다.")
            new_state.write.format("delta").mode("overwrite").save(STATE_TABLE_PATH_BATCH)
        
        log_time("상태 업데이트 완료.")
        log_time(f"배치 처리 성공 - 최종 레코드 수: {final_df_count}")
        
    except Exception as e:
        log_time(f"배치 처리 중 에러 발생: {str(e)}")
        import traceback; traceback.print_exc(); raise e
    finally:
        spark.catalog.clearCache()

# ==============================================================================
# 3. Main: 배치 정의 및 실행
# ==============================================================================

if __name__ == "__main__":
    log_time("애플리케이션 시작")
    log_time("Spark 세션 생성 시작")
    
    spark = (
        SparkSession.builder
        .appName("S3BatchUserBehaviorProcessorWithSchemaRegistry")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )
    
    spark.sparkContext.setLogLevel("WARN")
    log_time("Spark 세션 생성 완료")
    
    try:
        log_time("Schema Registry에서 Nginx 스키마 로드 시작")
        nginx_schema_str = get_latest_schema_from_registry("nginx-topic-value")
        log_time("Nginx 스키마 로드 성공")
        
        log_time("S3에서 Nginx 로그 데이터 로드 시작")
        logs_df = load_nginx_logs_batch(spark, NGINX_LOGS_S3_PATH, nginx_schema_str)
        logs_count = logs_df.count()
        log_time(f"Nginx 로그 데이터 로드 완료. 레코드 수: {logs_count}")
        
        if logs_count > 0:
            log_time("S3에서 Debezium Users 데이터 로드 시작")
            users_df = load_debezium_users_batch(spark, USERS_CDC_S3_PATH)
            
            log_time("S3에서 Debezium Sessions 데이터 로드 시작")
            sessions_df = load_debezium_sessions_batch(spark, SESSIONS_CDC_S3_PATH)
            
            process_user_behavior_batch(logs_df, sessions_df, users_df, spark)
            log_time("사용자 행동 데이터 배치 처리 완료.")
        else:
            log_time("처리할 Nginx 로그가 없으므로 배치를 종료합니다.")
            
    except Exception as e:
        log_time(f"메인 처리 중 에러 발생: {str(e)}")
        import traceback; traceback.print_exc()
    finally:
        log_time("Spark 세션 종료 시작")
        spark.stop()
        log_time("Spark 세션 종료 완료")
        log_time("애플리케이션 종료")
