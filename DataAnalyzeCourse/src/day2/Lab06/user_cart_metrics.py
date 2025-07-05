#!/usr/bin/env python3
import argparse
import time
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import col

def main():
    parser = argparse.ArgumentParser(
        description="Build user cart metrics and load into MySQL via Spark"
    )
    parser.add_argument(
        "--mysql-endpoint", required=True,
        help="MySQL endpoint host (no port)"
    )
    parser.add_argument(
        "--mysql-port", default="3306",
        help="MySQL port"
    )
    parser.add_argument(
        "--mysql-database", default="shopdb",
        help="MySQL database name"
    )
    parser.add_argument(
        "--mysql-user", default="admin",
        help="MySQL username"
    )
    parser.add_argument(
        "--mysql-password", default="admin1234",
        help="MySQL password"
    )
    parser.add_argument(
        "--mysql-table", default="user_cart_metrics",
        help="MySQL target table name"
    )
    parser.add_argument(
        "--preview-count", type=int, default=5,
        help="Number of rows to preview with show()"
    )
    parser.add_argument(
        "--preview-sleep", type=int, default=10,
        help="Seconds to sleep after preview"
    )
    args = parser.parse_args()

    # Initialize SparkSession with Hive support
    spark = SparkSession.builder \
        .appName("UserCartMetrics") \
        .config(
            "spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive", "true"
        ) \
        .enableHiveSupport() \
        .getOrCreate()

    # Load aggregated logs from Hive metastore
    logs_df = spark.table("default.aggregated_logs")

    # Compute metrics grouped by user_id
    metrics_df = logs_df.groupBy("user_id").agg(
        F.sum(
            F.when(
                col("event_type") == "order",
                col("event_count")
            ).otherwise(0)
        ).cast("long").alias("order_count"),
        F.sum(
            F.when(
                col("event_type") == "pageview",
                col("event_count")
            ).otherwise(0)
        ).cast("long").alias("pageview_count"),
        F.round(F.sum("total_request_time"), 3).alias("total_request_time"),
        F.round(
            F.sum("total_request_time") / F.sum("event_count"),
            3
        ).alias("avg_request_time"),
        F.max("last_active_time").alias("last_active_time")
    )

    # Preview computed metrics
    metrics_df.show(5)
    time.sleep(10)

    # JDBC connection properties
    jdbc_url = (
        f"jdbc:mysql://{args.mysql_endpoint}:{args.mysql_port}/"
        f"{args.mysql_database}?useSSL=false"
    )
    connection_properties = {
        "user": args.mysql_user,
        "password": args.mysql_password,
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    # Write metrics to MySQL
    metrics_df.write \
        .mode("overwrite") \
        .jdbc(
            url=jdbc_url,
            table=args.mysql_table,
            properties=connection_properties
        )

    spark.stop()

if __name__ == "__main__":
    main()
