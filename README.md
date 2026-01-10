# Banking Transaction Data Pipeline

This project implements an **end-to-end batch data engineering pipeline** for processing inter-bank payment transactions.
It demonstrates how banking transaction data can be ingested, stored, transformed, and aggregated into analytics-ready tables using **industry-standard tooling and best practices**.

The pipeline emphasizes:

* Batch correctness over real-time complexity
* Clear separation of raw, staging, and reporting layers
* Reproducibility using Infrastructure as Code and containerized orchestration

---
## Table of Contents

- [Problem Statement](#problem-statement)
- [Dataset](#dataset)
- [High-Level Architecture](#high-level-architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [Detailed Setup Instructions](#detailed-setup-instructions)
- [dbt Transformations](#dbt-transformations)
- [Data Quality & Testing](#data-quality--testing)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Problem Statement

Banks process large volumes of inter-bank payment transactions every day. These transactions support settlement, reconciliation, regulatory reporting, and operational monitoring. Because of their financial and regulatory importance, transaction data must be processed **accurately, consistently, and repeatably**.

In real-world banking systems, transaction data:

* Arrives incrementally throughout the day
* Originates from multiple systems
* Must be aggregated reliably at end-of-day or end-of-period boundaries

Without a structured batch pipeline, banks risk:

* Inconsistent settlement figures
* Delayed reporting
* Poor auditability of transaction flows

This project simulates how such inter-bank payment data can be handled using a **reliable batch-oriented data pipeline**, closely reflecting real-world banking data engineering patterns.

---

## Dataset

* **Source:** IBM Synthetic AML Transaction Dataset
  (https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)[(Kaggle)]
* **File used:** `LI-Medium_Trans.csv`

**Characteristics:**

* Inter-bank transfers
* Transaction timestamps
* Bank and account identifiers
* Payment amounts and currencies
* Payment formats (ACH, wire transfer, cheque)

The dataset is **fully synthetic** and safe for demonstration purposes.

---

## High-Level Architecture

```
Local CSV
  ↓
Google Cloud Storage (Raw Data Lake)
  ↓
BigQuery (interbank_raw)
  ↓
dbt Transformations
  ↓
Analytics-Ready Tables
```

---

## Orchestration Flow

```
Airflow DAG: interbank_batch_pipeline
└── ingest_to_gcs
    └── load_gcs_to_bigquery
        └── trigger_dbt_cloud_job
```

---

## Tech Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| Cloud Platform | Google Cloud Platform | Infrastructure hosting |
| Data Lake | Cloud Storage | Raw data storage |
| Data Warehouse | BigQuery | Analytical queries |
| Infrastructure | Terraform | Infrastructure as Code |
| Orchestration | Apache Airflow | Workflow scheduling |
| Transformation | dbt Cloud | SQL-based transformations |
| Ingestion | Python | Data loading scripts |
| Containerization | Docker | Local reproducible runtime |
| Visualization | Looker Studio | Reporting dashboards |

## Prerequisites

Before you begin, ensure you have the following installed:

- [ ] [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [ ] [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- [ ] [Terraform](https://developer.hashicorp.com/terraform/downloads) (v1.3+)
- [ ] [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (gcloud CLI)
- [ ] [Python](https://www.python.org/downloads/) (v3.9+)
- [ ] A [GCP Account](https://cloud.google.com/) with billing enabled
- [ ] A [dbt Cloud Account](https://www.getdbt.com/product/dbt-cloud) (free tier available)

---

## Quick Start Guide

```bash
# 1. Clone the repository
git clone https://github.com/Sefviaaa/banking-transaction-pipeline.git
cd banking-transaction-pipeline

# 2. Download the dataset
# Download LI-Medium_Trans.csv from Kaggle and place it in: 
# ingestion/data/raw/LI-Medium_Trans.csv

# 3. Set up GCP infrastructure
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars  # Edit with your project ID
terraform init
terraform apply

# 4. Configure environment
cd ../../orchestration
cp .env. example .env  # Edit with your credentials

# 5. Set up GCP credentials
mkdir -p credentials
# Place your service account JSON key as credentials/credentials.json

# 6. Set up dbt profile
mkdir -p ~/. dbt
cp ../dbt/profiles.yml. example ~/.dbt/profiles.yml  # Edit with your project ID

# 7. Start the pipeline
docker compose up -d

# 8. Access Airflow UI
open http://localhost:8080  # Login:  admin / admin
```

---

## Detailed Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sefviaaa/banking-transaction-pipeline.git
cd banking-transaction-pipeline
```

### Step 2: Download the Dataset

1. Go to [Kaggle - IBM Transactions for AML](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)
2. Download `LI-Medium_Trans.csv`
3. Create the data directory and move the file:

```bash
mkdir -p ingestion/data/raw
mv ~/Downloads/LI-Medium_Trans.csv ingestion/data/raw/
```

### Step 3: Set Up Google Cloud Platform

#### 3.1 Create a GCP Project

```bash
# Create a new project (or use existing)
gcloud projects create your-project-id --name="Banking Pipeline"
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

#### 3.2 Create a Service Account

```bash
# Create service account
gcloud iam service-accounts create banking-pipeline \
    --display-name="Banking Pipeline Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:banking-pipeline@your-project-id.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount: banking-pipeline@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Download credentials
gcloud iam service-accounts keys create orchestration/credentials/credentials.json \
    --iam-account=banking-pipeline@your-project-id.iam.gserviceaccount.com
```

### Step 4: Provision Infrastructure with Terraform

```bash
cd infra/terraform

# Create your variables file
cat > terraform.tfvars << EOF
project_id  = "your-project-id"
region      = "US"
bucket_name = "your-unique-bucket-name"
EOF

# Initialize and apply
terraform init
terraform apply
```

This creates:
- GCS bucket for raw data
- BigQuery datasets:  `interbank_raw`, `interbank_dbt_dev`, `interbank_prod`

### Step 5: Configure Environment Variables

```bash
cd ../../orchestration

# Copy the example file
cp .env.example .env

# Edit . env with your values
nano .env  # or use your preferred editor
```

Your `.env` file should contain:

```bash
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCS_RAW_BUCKET=your-unique-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/google/credentials. json

# dbt Cloud Configuration
DBT_CLOUD_ACCOUNT_ID=your_dbt_account_id
DBT_CLOUD_API_TOKEN=your_dbt_api_token
DBT_CLOUD_JOB_ID=your_dbt_job_id

# Airflow Security
AIRFLOW_SECRET_KEY=your-secure-random-string-here
```

### Step 6: Set Up dbt Cloud

1. **Create a dbt Cloud account** at [getdbt.com](https://www.getdbt.com/)

2. **Connect your repository** to dbt Cloud

3. **Configure BigQuery connection** in dbt Cloud:
   - Upload your service account JSON key
   - Set the project and dataset

4. **Create a dbt Cloud job** and note the Job ID

5. **Generate an API token** from dbt Cloud settings

6. **Update your `.env`** with the dbt Cloud credentials

### Step 7: Set Up dbt Profile (for local development)

If you want to run dbt locally (optional):

```bash
mkdir -p ~/.dbt

cat > ~/.dbt/profiles.yml << EOF
banking_transaction_pipeline:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: your-project-id
      dataset: interbank_dbt_dev
      location: US
      threads: 4
      keyfile: /path/to/your/credentials.json
    
    prod:
      type: bigquery
      method: service-account
      project: your-project-id
      dataset: interbank_prod
      location: US
      threads: 4
      keyfile: /path/to/your/credentials.json
EOF
```

### Step 8: Start the Pipeline

```bash
cd orchestration

# Build and start containers
docker compose up -d

# Check logs
docker compose logs -f
```

### Step 9: Access Airflow and Trigger the Pipeline

1. Open **http://localhost:8080** in your browser
2. Login with:
   - Username: `admin`
   - Password: `admin`
3. Find the DAG:  `interbank_batch_pipeline`
4. Toggle the DAG **ON**
5. Click **Trigger DAG** to run manually

### Step 10: Verify the Results

```bash
# Check BigQuery for data
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM `your-project-id.interbank_raw.transactions`'

# Check dbt Cloud for transformation results
# View in dbt Cloud UI or query the marts: 
bq query --use_legacy_sql=false \
  'SELECT * FROM `your-project-id.interbank_prod.fact_transactions_daily` LIMIT 10'
```

---

## dbt Transformations

The Airflow DAG triggers a **dbt Cloud job** via API.

### What the dbt job does

* Runs staging models
* Builds dimension tables
* Aggregates daily transaction facts
* Produces reporting tables
* Executes dbt tests

### Target Datasets

* **Development:** `interbank_dbt_dev`
* **Production:** `interbank_prod`

### Key Models

| Layer | Model | Description |
|-------|-------|-------------|
| Staging | `stg_interbank_transactions` | Type casting, timestamp normalization, column standardization |
| Dimension | `dim_bank` | Bank reference data |
| Dimension | `dim_currency` | Currency reference data |
| Fact | `fact_transactions_daily` | Daily aggregated transactions |
| Reporting | `rpt_bank_daily_volume` | Bank daily volume report |

## Data Quality & Testing

Implemented using dbt tests:

* `not_null` checks
* Referential integrity (`relationships`)
* Metric sanity checks

These ensure analytical outputs remain **consistent, auditable, and trustworthy**.


---

## Project Structure

```
banking-transaction-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
│
├── ingestion/
│   ├── data/
│   │   └── raw/
│   │       └── LI-Medium_Trans.csv  # not committed
│   ├── load_to_gcs.py          # Upload to GCS
│   └── load_gcs_bq.py          # Load to BigQuery
│
├── orchestration/
│   ├── dags/
│   │   └── interbank_batch_dag.py
│   ├── credentials/
│   │   └── credentials.json    # not committed
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env                    # not committed
│   └── .env.example
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_interbank_transactions. sql
│   │   │   └── schema.yml
│   │   ├── marts/
│   │   │   ├── dim_bank.sql
│   │   │   ├── dim_currency.sql
│   │   │   ├── fact_transactions_daily. sql
│   │   │   ├── rpt_bank_daily_volume.sql
│   │   │   └── schema.yml
│   │   └── sources.yml
│   ├── dbt_project.yml
│   ├── packages.yml
│   └── profiles.yml.example
│
├── infra/
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── terraform.tfvars    # not committed
│
├── .gitignore
└── README.md
```


## Troubleshooting

### Common Issues

#### 1. Docker Compose fails to start

```bash
# Check if ports are in use
lsof -i : 8080

# Reset Docker volumes
docker compose down -v
docker compose up -d
```

#### 2. GCS upload fails with permission denied

```bash
# Verify service account permissions
gcloud projects get-iam-policy your-project-id \
  --filter="bindings.members:banking-pipeline@*"

# Re-authenticate
gcloud auth activate-service-account \
  --key-file=orchestration/credentials/credentials.json
```

#### 3. dbt Cloud job fails

- Check that your BigQuery connection is configured correctly in dbt Cloud
- Verify the `interbank_raw. transactions` table exists
- Check dbt Cloud logs for specific errors

#### 4. Airflow can't find environment variables

```bash
# Verify .env file exists and is properly formatted
cat orchestration/.env

# Restart containers to pick up changes
docker compose restart
```

#### 5. Terraform fails with quota errors

```bash
# Check GCP quotas
gcloud compute regions describe US --format="value(quotas)"

# Use a different region in terraform.tfvars
```

---

