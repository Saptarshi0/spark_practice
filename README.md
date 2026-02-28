# spark_practice

> PySpark practice project using a local Docker Spark cluster + MinIO (S3-compatible storage).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Docker Network                   │
│                                                     │
│  ┌──────────────┐    ┌──────────┐  ┌──────────┐    │
│  │ Spark Master │◄───│ Worker 1 │  │ Worker 2 │    │
│  │  :8080 :7077 │    │  :8081   │  │  :8082   │    │
│  └──────┬───────┘    └──────────┘  └──────────┘    │
│         │                                           │
│  ┌──────▼───────┐    ┌──────────────────────────┐  │
│  │   Jupyter    │    │  MinIO (S3-compatible)   │  │
│  │    :8888     │    │  API :9000 | UI :9001    │  │
│  └──────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Saptarshi0/spark_practice.git
cd spark_practice
```

### 2. Start the cluster
```bash
docker compose up -d
```
Wait ~30 seconds for all services to be healthy.

### 3. Verify everything is running
| Service | URL |
|---------|-----|
| Spark Master UI | http://localhost:8080 |
| Spark Worker 1 | http://localhost:8081 |
| Spark Worker 2 | http://localhost:8082 |
| Jupyter Lab | http://localhost:8888 (token: check logs) |
| MinIO Console | http://localhost:9001 (user: `minioadmin` / pw: `minioadmin`) |

Get the Jupyter token:
```bash
docker logs jupyter 2>&1 | grep token
```

---

## 📂 Project Structure

```
spark_practice/
├── docker-compose.yml          # Full cluster definition
├── requirements.txt            # Local Python packages
├── .gitignore
├── config/
│   └── spark-defaults.conf    # Spark + S3A/MinIO settings
├── data/
│   ├── employees.csv          # Sample employee data (20 rows)
│   └── sales.csv              # Sample sales data (20 rows)
├── scripts/                   # Run via spark-submit inside Docker
│   ├── 01_basic_transformations.py   # select, filter, withColumn, cast
│   ├── 02_aggregations.py            # groupBy, agg, pivot, rollup, cube
│   ├── 03_joins.py                   # inner/left/right/full/semi/anti/broadcast
│   ├── 04_window_functions.py        # rank, lag/lead, running totals, ntile
│   ├── 05_minio_integration.py       # read/write Parquet & CSV to MinIO
│   └── 06_udf_and_sql.py             # Python UDFs, Pandas UDFs, Spark SQL
└── notebooks/
    └── practice.ipynb         # Interactive Jupyter notebook
```

---

## ▶️ Running Scripts

All scripts run inside the `spark-master` container:

```bash
# Basic transformations
docker exec spark-master spark-submit \
    /opt/bitnami/spark/work/scripts/01_basic_transformations.py

# Aggregations
docker exec spark-master spark-submit \
    /opt/bitnami/spark/work/scripts/02_aggregations.py

# Joins
docker exec spark-master spark-submit \
    /opt/bitnami/spark/work/scripts/03_joins.py

# Window functions
docker exec spark-master spark-submit \
    /opt/bitnami/spark/work/scripts/04_window_functions.py

# MinIO read/write (needs hadoop-aws packages)
docker exec spark-master spark-submit \
    --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    /opt/bitnami/spark/work/scripts/05_minio_integration.py

# UDFs + Spark SQL
docker exec spark-master spark-submit \
    /opt/bitnami/spark/work/scripts/06_udf_and_sql.py
```

---

## 📓 Jupyter Notebook

1. Open http://localhost:8888
2. Navigate to `work/notebooks/practice.ipynb`
3. Run all cells — the notebook connects directly to the Spark cluster

---

## 🛑 Stop the Cluster

```bash
# Stop (keep data)
docker compose stop

# Stop + remove containers + volumes
docker compose down -v
```

---

## 📚 Topics Covered

| Script | Topics |
|--------|--------|
| 01 | `select`, `filter`, `withColumn`, `cast`, `drop`, `distinct`, `dropDuplicates` |
| 02 | `groupBy`, `agg`, `pivot`, `rollup`, `cube`, `collect_list` |
| 03 | inner / left / right / full / semi / anti / broadcast joins |
| 04 | `rank`, `dense_rank`, `row_number`, `lag`, `lead`, running totals, `ntile`, `percent_rank` |
| 05 | Read/write CSV & Parquet, partitioned writes, MinIO (S3A) integration |
| 06 | Python UDFs, Pandas (vectorised) UDFs, `createOrReplaceTempView`, Spark SQL |

---

## ⚙️ Requirements

- Docker Desktop ≥ 4.x
- 6 GB RAM available for Docker (4 containers)
- No local Spark / Java installation needed

---

*Happy Sparking! 🚀*