#!/usr/bin/env python3
import argparse
import time
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import col

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql-endpoint", required=True)
    parser.add_argument("--mysql-port", default="3306")
    parser.add_argument("--mysql-database", default="shopdb")
    parser.add_argument("--mysql-user", default="admin")
    parser.add_argument("--mysql-password", default="admin1234")
    parser.add_argument("--mysql-table", default="user_cart_metrics")
    args = parser.parse_args()

    spark = SparkSession.builder \
        .appName("UserCartMetrics") \
        .config("spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive", "true") \
        .enableHiveSupport() \
        .getOrCreate()

    df = spark.table("default.aggregated_logs")
    metrics = df.groupBy("user_id").agg(
        F.sum(F.when(col("event_type")=="order", col("event_count")).otherwise(0)).cast("long").alias("order_count"),
        F.sum(F.when(col("event_type")=="pageview", col("event_count")).otherwise(0)).cast("long").alias("pageview_count"),
        F.round(F.sum("total_request_time"),3).alias("total_request_time"),
        F.round(F.sum("total_request_time")/F.sum("event_count"),3).alias("avg_request_time"),
        F.max("last_active_time").alias("last_active_time")
    )

    metrics.show(5)
    time.sleep(10)

    url = f"jdbc:mysql://{args.mysql_endpoint}:{args.mysql_port}/{args.mysql_database}?useSSL=false"
    props = {"user": args.mysql_user, "password": args.mysql_password, "driver": "com.mysql.cj.jdbc.Driver"}
    metrics.write.mode("overwrite").jdbc(url, args.mysql_table, properties=props)

    spark.stop()

if __name__ == "__main__":
    main()
