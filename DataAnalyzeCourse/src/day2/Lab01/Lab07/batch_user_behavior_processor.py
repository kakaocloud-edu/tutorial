#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, when, coalesce, lit,
    lag, row_number,
    sum as spark_sum,
    date_format, unix_timestamp, round
)
from pyspark.sql.types import IntegerType

# -----------------------------------
# 0) S3 자격증명/엔드포인트 설정
# -----------------------------------
def set_s3_config(spark):
    print("[LOG] set_s3_config(): S3 자격증명 및 엔드포인트 설정 시작")
    hconf = spark.sparkContext._jsc.hadoopConfiguration()

    # KakaoCloud Object Storage 엔드포인트
    hconf.set("fs.s3a.endpoint", "https://objectstorage.kr-central-2.kakaocloud.com")
    hconf.set("fs.s3a.path.style.access", "true")
    hconf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    print("[LOG] set_s3_config(): 설정 완료")


# -----------------------------------
# 1) SparkSession 생성
# -----------------------------------
print("[LOG] Main: SparkSession 생성 시작")
spark = (
    SparkSession.builder
        .appName("BatchEnrichNginxWithMySQL-FixPartition0")
        .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")
print("[LOG] Main: SparkSession 생성 완료")

set_s3_config(spark)

# -----------------------------------
# 2) 경로 정의 (오직 partition_0 안에서 Parquet만 읽도록)
# -----------------------------------
NGINX_BASE_PATH = "s3a://data-catalog-bucket/kafka-nginx-log/nginx-topic/partition_0/"
USERS_BASE_PATH = "s3a://data-catalog-bucket/mysql-data/mysql-server.shopdb.users/"
SESSIONS_BASE_PATH = "s3a://data-catalog-bucket/mysql-data/mysql-server.shopdb.sessions/"
OUTPUT_PATH = "s3a://data-catalog-bucket/data-catalog-dir/user_behavior_batch/"

print(f"[LOG] Main: 경로 설정 완료\n"
      f"  NGINX_BASE_PATH    = {NGINX_BASE_PATH}\n"
      f"  USERS_BASE_PATH    = {USERS_BASE_PATH}\n"
      f"  SESSIONS_BASE_PATH = {SESSIONS_BASE_PATH}\n"
      f"  OUTPUT_PATH        = {OUTPUT_PATH}")


# -----------------------------------
# 3) MySQL CDC(JSON) 읽어서 Users DataFrame 생성
# -----------------------------------
def load_users_cdc(spark):
    print("[LOG] load_users_cdc(): 진입")
    try:
        raw_users = (
            spark.read
                .format("json")
                .option("recursiveFileLookup", "true")
                .load(USERS_BASE_PATH)
        )
        print("[LOG] load_users_cdc(): JSON 파일 읽기 성공")
    except Exception as e:
        print("load_users_cdc(): JSON 파일 로드 실패 →", str(e))
        traceback.print_exc()
        raise

    users_df = (
        raw_users
        .select(
            col("op").alias("operation"),
            col("after.user_id").alias("user_info_id"),
            col("after.gender").alias("gender"),
            col("after.age").cast("int").alias("age"),
            col("ts_ms").cast("timestamp").alias("cdc_timestamp")
        )
        .filter(
            col("operation").isin("c", "u", "r") &
            col("user_info_id").isNotNull() &
            (col("user_info_id") != "") &
            col("gender").isin("M", "F") &
            col("age").between(1, 120)
        )
        .dropDuplicates(["user_info_id"])
        .select("user_info_id", "gender", "age")
    )

    count_users = users_df.count()
    print(f"[LOG] load_users_cdc(): 최종 사용자 레코드 수 = {count_users}")
    return users_df


# -----------------------------------
# 4) MySQL CDC(JSON) 읽어서 Sessions DataFrame 생성
# -----------------------------------
def load_sessions_cdc(spark):
    print("[LOG] load_sessions_cdc(): 진입")
    try:
        raw_sessions = (
            spark.read
                .format("json")
                .option("recursiveFileLookup", "true")
                .load(SESSIONS_BASE_PATH)
        )
        print("[LOG] load_sessions_cdc(): JSON 파일 읽기 성공")
    except Exception as e:
        print("load_sessions_cdc(): JSON 파일 로드 실패 →", str(e))
        traceback.print_exc()
        raise

    sessions_df = (
        raw_sessions
        .select(
            col("op").alias("operation"),
            col("after.session_id").alias("session_id"),
            col("after.user_id").alias("session_user_id"),
            col("ts_ms").cast("timestamp").alias("cdc_timestamp")
        )
        .filter(
            col("operation").isin("c", "u", "r") &
            col("session_id").isNotNull() &
            (col("session_id") != "")
        )
        .dropDuplicates(["session_id"])
        .select("session_id", "session_user_id")
    )

    count_sessions = sessions_df.count()
    print(f"[LOG] load_sessions_cdc(): 최종 세션 레코드 수 = {count_sessions}")
    return sessions_df


# -----------------------------------
# 5) 원본 Parquet(nginx Raw) 읽기 (partition_0 안에서 Parquet만)
# -----------------------------------
def load_nginx_raw(spark):
    print("[LOG] load_nginx_raw(): 진입")

    # (디버그) partition_0 폴더 바로 아래 자식 디렉터리만 찍어보기
    try:
        print(f"[DEBUG] load_nginx_raw(): Hadoop FileSystem으로 '{NGINX_BASE_PATH}' 하위 디렉터리 조회 시도")
        jvm = spark._jvm
        conf = spark.sparkContext._jsc.hadoopConfiguration()
        fs = jvm.org.apache.hadoop.fs.FileSystem.get(jvm.java.net.URI(NGINX_BASE_PATH), conf)
        base_path = jvm.org.apache.hadoop.fs.Path(NGINX_BASE_PATH)
        statuses = fs.listStatus(base_path)
        print("[DEBUG] load_nginx_raw(): partition_0 바로 아래 즉시 자식 목록:")
        for status in statuses:
            print("  -", status.getPath().toString())
    except Exception as e:
        print("load_nginx_raw(): 파일 목록 조회 중 예외 발생 →", str(e))
        traceback.print_exc()

    # Parquet 파일만 읽도록 pathGlobFilter="*.parquet" 추가
    try:
        raw_logs = (
            spark.read
                .format("parquet")
                .option("recursiveFileLookup", "true")
                .option("pathGlobFilter", "*.parquet")
                .load(NGINX_BASE_PATH)
        )
        print("[LOG] load_nginx_raw(): Parquet 파일 로드 성공")
    except Exception as e:
        print("load_nginx_raw(): Parquet 파일 로드 실패 →", str(e))
        traceback.print_exc()
        raise

    final_logs = (
        raw_logs
        .select(
            col("session_id"),
            when(col("user_id") == "", lit(None)).otherwise(col("user_id")).alias("user_id"),
            col("endpoint"),
            col("method"),
            col("query_params"),
            col("product_id"),
            col("request_body"),
            col("timestamp").cast("timestamp").alias("event_time")
        )
        .filter(
            col("session_id").isNotNull() &
            col("endpoint").isNotNull() &
            col("event_time").isNotNull()
        )
    )

    count_logs = final_logs.count()
    print(f"[LOG] load_nginx_raw(): 최종 로그 레코드 수 = {count_logs}")
    return final_logs


# -----------------------------------
# 6) 배치 정제 로직 (전체 처리 흐름)
# -----------------------------------
def batch_enrich():
    print("[LOG] batch_enrich(): 시작")

    # 6-1) MySQL CDC 데이터(Users, Sessions) 불러오기
    print("[LOG] batch_enrich(): load_users_cdc() 호출")
    users_df = load_users_cdc(spark).alias("u")

    print("[LOG] batch_enrich(): load_sessions_cdc() 호출")
    sessions_df = load_sessions_cdc(spark).alias("s")

    # 6-2) partition_0 내부 Parquet(Nginx) 불러오기
    print("[LOG] batch_enrich(): load_nginx_raw() 호출")
    logs_df = load_nginx_raw(spark).alias("l")

    # 6-3) 조인: logs_df ← sessions_df ← users_df
    print("[LOG] batch_enrich(): 조인 시작")
    enriched = (
        logs_df
        .join(sessions_df, col("l.session_id") == col("s.session_id"), "left")
        .join(users_df,
              (col("l.user_id") == col("u.user_info_id")) |
              (col("s.session_user_id") == col("u.user_info_id")),
              "left"
        )
        .select(
            col("l.session_id").alias("session_id"),
            coalesce(col("l.user_id"), col("s.session_user_id")).alias("user_id"),
            coalesce(col("u.gender"), lit("Unknown")).alias("gender"),
            coalesce(col("u.age"), lit(0)).alias("age"),
            col("l.event_time").alias("event_time"),
            col("l.endpoint").alias("current_state"),
            col("l.method").alias("method"),
            col("l.query_params").alias("query_params"),
            col("l.product_id").alias("product_id"),
            col("l.request_body").alias("request_body")
        )
    )
    print("[LOG] batch_enrich(): 조인 완료")

    window_by_session = Window.partitionBy("session_id").orderBy("event_time")

    # 6-4) 중복 이벤트 제거
    dedup = (
        enriched
        .withColumn("prev_state", lag("current_state", 1).over(window_by_session))
        .withColumn("prev_time", lag("event_time", 1).over(window_by_session))
        .filter(
            (col("prev_time").isNull()) |
            (~((col("current_state") == col("prev_state")) & (col("event_time") == col("prev_time"))))
        )
    )

    # 6-5) 검색/장바구니 플래그 추가
    flagged = (
        dedup
        .withColumn("batch_search", when(col("current_state").like("/search%"), lit(1)).otherwise(lit(0)))
        .withColumn("batch_cart", when(col("current_state") == "/cart/add", lit(1)).otherwise(lit(0)))
    )

    # 6-6) 누적 합계 계산
    cumul = (
        flagged
        .withColumn("search_count", spark_sum("batch_search").over(
            Window.partitionBy("session_id").orderBy("event_time")
                .rowsBetween(Window.unboundedPreceding, Window.currentRow)
        ))
        .withColumn("cart_item_count", spark_sum("batch_cart").over(
            Window.partitionBy("session_id").orderBy("event_time")
                .rowsBetween(Window.unboundedPreceding, Window.currentRow)
        ))
    )

    # 6-7) 다음 상태(next_state)
    cumul2 = cumul.withColumn(
        "next_state",
        lag("current_state", -1).over(window_by_session)
    )

    # 6-8) 마지막 액션 경과 시간(last_action_elapsed)
    time_calc = (
        cumul2
        .withColumn("prev_time_for_elapsed", lag("event_time", 1).over(window_by_session))
        .withColumn("last_action_elapsed",
            when(col("prev_time_for_elapsed").isNotNull(),
                 (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_time_for_elapsed"))).cast("double")
            ).otherwise(lit(0.0))
        )
    )

    # 6-9) 페이지 깊이(page_depth)
    with_depth = (
        time_calc
        .withColumn("page_depth", row_number().over(window_by_session))
    )

    # 6-10) 날짜(dt) 컬럼 추가
    with_dt = with_depth.withColumn("dt", date_format(col("event_time"), "yyyy-MM-dd"))

    # 6-11) 최종 컬럼 추출 및 중복 제거
    final_df = (
        with_dt
        .select(
            "session_id",
            "user_id",
            "gender",
            "age",
            "current_state",
            col("search_count").cast(IntegerType()).alias("search_count"),
            col("cart_item_count").cast(IntegerType()).alias("cart_item_count"),
            col("page_depth").cast(IntegerType()).alias("page_depth"),
            round(col("last_action_elapsed"), 2).alias("last_action_elapsed"),
            "next_state",
            "dt"
        )
        .dropDuplicates(["session_id", "user_id", "current_state", "page_depth"])
    )

    print(f"[LOG] batch_enrich(): 정제 로직 완료 (컬럼 개수 = {len(final_df.columns)})")

    # 6-12) 결과 Parquet 쓰기
    try:
        print("[LOG] batch_enrich(): Parquet 쓰기 시작")
        (
            final_df
            .repartition(col("dt"))
            .write
            .mode("overwrite")
            .format("parquet")
            .partitionBy("dt")
            .option("maxRecordsPerFile", 500000)
            .save(OUTPUT_PATH)
        )
        print("[LOG] batch_enrich(): Parquet 쓰기 완료")
    except Exception as e:
        print("batch_enrich(): Parquet 쓰기 오류 →", str(e))
        traceback.print_exc()
        raise

    total = final_df.count()
    print(f"[LOG] batch_enrich(): 배치 정제 완료 (총 레코드 = {total})")


# -----------------------------------
# 7) Main: 실행 진입점
# -----------------------------------
if __name__ == "__main__":
    print("[LOG] __main__(): 스크립트 시작")
    try:
        batch_enrich()
    except Exception as e:
        print("__main__(): 배치 정제 중 오류 발생 →", str(e))
        traceback.print_exc()
    finally:
        print("[LOG] __main__(): SparkSession 중지")
        spark.stop()
        sys.exit(0)
