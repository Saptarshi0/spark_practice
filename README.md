# spark_practice 

> A local PySpark practice environment using Docker, Apache Spark, MinIO (S3-compatible storage), and Jupyter Lab.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Docker Network                        │
│                                                             │
│   ┌──────────────┐    ┌────────────┐    ┌────────────┐     │
│   │ Spark Master │◄───│  Worker 1  │    │  Worker 2  │     │
│   │  :8080 :7077 │    │   :8081    │    │   :8082    │     │
│   └──────┬───────┘    └────────────┘    └────────────┘     │
│          │                                                  │
│   ┌──────▼───────┐    ┌─────────────────────────────────┐  │
│   │   Jupyter    │    │     MinIO  (S3-compatible)      │  │
│   │    :8888     │    │   API :9000  |  Console :9001   │  │
│   └──────────────┘    └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
spark_practice/
├── app/
│   └── ingest_to_minio.py        # Ingest CSVs → Parquet → MinIO
├── config/
│   └── spark-defaults.conf       # Spark + S3A/MinIO configuration
├── data/
│   ├── employees.csv             # 150 rows — employee records
│   └── sales.csv                 # 200 rows — sales transactions
├── notebooks/
│   └── practice.ipynb            # Interactive Jupyter notebook
├── scripts/
│   ├── 01_basic_transformations.py
│   ├── 02_aggregations.py
│   ├── 03_joins.py
│   ├── 04_window_functions.py
│   ├── 05_minio_integration.py
│   └── 06_udf_and_sql.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (with at least 8GB RAM allocated)
- Git

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

### 3. Check all services are running
```bash
docker compose ps
```

| Service | URL | Credentials |
|---------|-----|-------------|
| Spark Master UI | http://localhost:8080 | — |
| Spark Worker 1 | http://localhost:8081 | — |
| Spark Worker 2 | http://localhost:8082 | — |
| Jupyter Lab | http://localhost:8888 | `docker logs jupyter 2>&1 \| grep token` |
| MinIO Console | http://localhost:9001 | `minioadmin` / `minioadmin` |

---

## 📥 Step 1 — Ingest Data into MinIO

Run the ingest job to load CSV files → Parquet format → MinIO:

```bash
docker exec spark-master /opt/spark/bin/spark-submit \
    --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    /opt/spark/work/app/ingest_to_minio.py
```

This will:
- Read `employees.csv` (150 rows) and `sales.csv` (200 rows) from the `data/` folder
- Convert both to **Parquet format** (columnar, compressed with Snappy)
- Write to MinIO — `employees/` partitioned by `department`, `sales/` partitioned by `region`
- Verify the write by reading back from MinIO

After running, open http://localhost:9001 → **spark-data** bucket to see the Parquet files.

---

## ▶️ Step 2 — Run Practice Scripts

```bash
# 01 — Basic Transformations
docker exec spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work/scripts/01_basic_transformations.py

# 02 — Aggregations
docker exec spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work/scripts/02_aggregations.py

# 03 — All Join Types
docker exec spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work/scripts/03_joins.py

# 04 — Window Functions
docker exec spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work/scripts/04_window_functions.py

# 05 — MinIO Read/Write
docker exec spark-master /opt/spark/bin/spark-submit \
    --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    /opt/spark/work/scripts/05_minio_integration.py

# 06 — UDFs + Spark SQL
docker exec spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work/scripts/06_udf_and_sql.py
```

---

## 📓 Jupyter Notebook

1. Get the token: `docker logs jupyter 2>&1 | grep token`
2. Open http://localhost:8888 and paste the token
3. Navigate to `work/notebooks/practice.ipynb`
4. The notebook connects directly to the Spark cluster

---

## 📊 Datasets

### employees.csv (150 rows)
| Column | Type | Description |
|--------|------|-------------|
| employee_id | int | Unique ID |
| name | string | Full name |
| department | string | Engineering / Marketing / Finance / HR |
| salary | int | Annual salary |
| hire_date | date | Date joined |
| city | string | New York / SF / Chicago / Austin |
| age | int | Age |
| gender | string | M / F |
| experience_years | int | Years of experience |
| performance_score | float | 3.3 – 5.0 |
| manager_id | int | ID of their manager |

### sales.csv (200 rows)
| Column | Type | Description |
|--------|------|-------------|
| sale_id | int | Unique ID |
| employee_id | int | FK to employees |
| product | string | Laptop / Phone / Tablet etc. |
| amount | float | Sale value |
| sale_date | date | Date of sale |
| region | string | North / South / East / West / Central |
| units | int | Units sold |
| discount | float | Discount applied (0–0.2) |
| channel | string | Online / In-Store / Partner / Direct |

---

## 📚 Topics Covered

| Script | Topics |
|--------|--------|
| `ingest_to_minio.py` | SparkSession config, CSV → Parquet, S3A/MinIO write, partitioning |
| `01_basic_transformations.py` | `select`, `filter`, `withColumn`, `cast`, `drop`, `distinct`, `dropDuplicates` |
| `02_aggregations.py` | `groupBy`, `agg`, `pivot`, `rollup`, `cube`, `collect_list` |
| `03_joins.py` | inner / left / right / full / semi / anti / broadcast joins |
| `04_window_functions.py` | `rank`, `dense_rank`, `row_number`, `lag`, `lead`, running totals, `ntile`, `percent_rank` |
| `05_minio_integration.py` | Read/write CSV & Parquet, partitioned writes, MinIO (S3A) |
| `06_udf_and_sql.py` | Python UDFs, Pandas (vectorised) UDFs, `createOrReplaceTempView`, Spark SQL |

---

## 🛑 Stop the Cluster

```bash
# Stop but keep data
docker compose stop

# Stop and remove everything including volumes
docker compose down -v
```

---


## 🔧 Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Apache Spark | 3.5.1 | Distributed data processing |
| PySpark | 3.5.1 | Python API for Spark |
| MinIO | latest | Local S3-compatible object storage |
| Jupyter Lab | latest | Interactive notebook environment |
| Docker | — | Container orchestration |

---

*Happy Sparking! 🚀*