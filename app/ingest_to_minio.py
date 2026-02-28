"""
app/ingest_to_minio.py
────────────────────────────────────────────────────────────────────────────────
Job        : Ingest CSV files → Parquet format → MinIO (S3)
Author     : Saptarshi
Description: Configures a SparkSession connected to the local Docker cluster,
             reads employees.csv and sales.csv, and writes both as Parquet
             files into MinIO buckets (s3a://spark-data/).

Run:
    docker exec spark-master /opt/spark/bin/spark-submit \
        --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
        /opt/spark/work/app/ingest_to_minio.py
────────────────────────────────────────────────────────────────────────────────
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import logging

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
MINIO_ENDPOINT   = "http://minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

INPUT_BASE  = "/opt/spark/work/data"
OUTPUT_BASE = "s3a://spark-data"

EMPLOYEES_CSV = f"{INPUT_BASE}/employees.csv"
SALES_CSV     = f"{INPUT_BASE}/sales.csv"

EMPLOYEES_PARQUET = f"{OUTPUT_BASE}/employees"
SALES_PARQUET     = f"{OUTPUT_BASE}/sales"


def build_spark_session() -> SparkSession:
    """
    Create and return a SparkSession configured to:
      - Connect to the local Docker Spark cluster
      - Talk to MinIO using the S3A connector
    """
    log.info("Building SparkSession ...")

    spark = (
        SparkSession.builder
        .appName("CSV to Parquet — MinIO Ingest")
        .master("spark://spark-master:7077")

        # ── Executor resources ────────────────────────────────────────────────
        .config("spark.executor.memory",  "1g")
        .config("spark.executor.cores",   "2")
        .config("spark.cores.max",        "4")
        .config("spark.driver.memory",    "1g")

        # ── MinIO / S3A connector settings ────────────────────────────────────
        .config("spark.hadoop.fs.s3a.endpoint",               MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key",             MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key",             MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access",      "true")
        .config("spark.hadoop.fs.s3a.impl",                   "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

        # ── Parquet settings ──────────────────────────────────────────────────
        .config("spark.sql.parquet.compression.codec",        "snappy")

        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    log.info(f"SparkSession created  |  Spark version: {spark.version}")
    return spark


def read_employees(spark: SparkSession):
    """Read employees CSV with explicit schema inference."""
    log.info(f"Reading employees CSV from  →  {EMPLOYEES_CSV}")

    df = (
        spark.read
        .option("header",      True)
        .option("inferSchema", True)
        .csv(EMPLOYEES_CSV)
    )

    log.info(f"employees  |  rows: {df.count()}  |  columns: {len(df.columns)}")
    df.printSchema()
    df.show(5, truncate=False)
    return df


def read_sales(spark: SparkSession):
    """Read sales CSV with explicit schema inference."""
    log.info(f"Reading sales CSV from  →  {SALES_CSV}")

    df = (
        spark.read
        .option("header",      True)
        .option("inferSchema", True)
        .csv(SALES_CSV)
        # Parse sale_date string → proper DateType
        .withColumn("sale_date", F.to_date(F.col("sale_date"), "yyyy-MM-dd"))
    )

    log.info(f"sales  |  rows: {df.count()}  |  columns: {len(df.columns)}")
    df.printSchema()
    df.show(5, truncate=False)
    return df


def write_parquet(df, output_path: str, partition_by: str = None):
    """
    Write a DataFrame to MinIO as Parquet.
    Optionally partition by a column for faster downstream reads.
    """
    writer = df.write.mode("overwrite").format("parquet")

    if partition_by:
        log.info(f"Writing Parquet  →  {output_path}  (partitioned by: {partition_by})")
        writer.partitionBy(partition_by).save(output_path)
    else:
        log.info(f"Writing Parquet  →  {output_path}")
        writer.save(output_path)

    log.info(f"✅  Written successfully  →  {output_path}")


def verify_parquet(spark: SparkSession, path: str, label: str):
    """Read back the written Parquet and print a summary to verify."""
    log.info(f"Verifying Parquet read-back  →  {path}")
    df = spark.read.parquet(path)
    log.info(f"[{label}]  rows: {df.count()}  |  columns: {len(df.columns)}")
    df.show(3, truncate=False)


def main():
    log.info("=" * 60)
    log.info("  JOB START — CSV to Parquet Ingest")
    log.info("=" * 60)

    # 1. Build SparkSession
    spark = build_spark_session()

    # 2. Read both CSVs
    employees_df = read_employees(spark)
    sales_df     = read_sales(spark)

    # 3. Write employees as Parquet — partitioned by department
    write_parquet(
        employees_df,
        output_path  = EMPLOYEES_PARQUET,
        partition_by = "department",
    )

    # 4. Write sales as Parquet — partitioned by region
    write_parquet(
        sales_df,
        output_path  = SALES_PARQUET,
        partition_by = "region",
    )

    # 5. Verify both writes by reading back
    verify_parquet(spark, EMPLOYEES_PARQUET, "employees")
    verify_parquet(spark, SALES_PARQUET,     "sales")

    log.info("=" * 60)
    log.info("  JOB COMPLETE — All data written to MinIO ✅")
    log.info("=" * 60)

    spark.stop()


if __name__ == "__main__":
    main()
