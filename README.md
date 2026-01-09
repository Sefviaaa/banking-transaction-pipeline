# Banking Transaction Data Pipeline

This project implements an **end-to-end batch data engineering pipeline** for processing inter-bank payment transactions.
It demonstrates how banking transaction data can be ingested, stored, transformed, and aggregated into analytics-ready tables using **industry-standard tooling and best practices**.

The pipeline emphasizes:

* Batch correctness over real-time complexity
* Clear separation of raw, staging, and reporting layers
* Reproducibility using Infrastructure as Code and containerized orchestration

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
  [https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)
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

* **Google Cloud Platform**

  * Cloud Storage (raw data lake)
  * BigQuery (analytical warehouse)
* **Terraform**

  * Infrastructure as Code
* **Apache Airflow**

  * Batch workflow orchestration
* **dbt Cloud**

  * SQL-based transformations and testing
* **Python**

  * Data ingestion and loading logic
* **Docker**

  * Local reproducible runtime
* **Looker Studio**

  * Reporting and visualization

---

## Execution Order (Important)

This project **must be executed in the following order**.
Skipping steps will cause the pipeline to fail.

1. **Provision infrastructure with Terraform**
2. **Configure credentials and environment variables**
3. **Run The Pipeline**
	1. **Start Airflow locally using Docker**
	2. **Trigger the Airflow DAG**
	3. **dbt Cloud performs transformations**

---
##  1) Infrastructure (Terraform)

Terraform is used **only to provision infrastructure**, not to run pipelines.

### Managed Resources

* Google Cloud Storage bucket (raw data lake)
* BigQuery datasets:

  * `interbank_raw` – raw ingestion layer
  * `interbank_dbt_dev` – dbt development dataset
  * `interbank_prod` – production reporting dataset

### Apply Infrastructure

```bash
cd infra/terraform
terraform init
terraform apply
```

Terraform ensures required cloud resources exist **before** the pipeline runs.

---

## 2) Credentials & Environment Variables

### Google Cloud Credentials

Create a GCP service account with:

* BigQuery permissions
* Cloud Storage permissions

Download the JSON key and place it here:

```
orchestration/credentials/credentials.json
```

This file is mounted into Airflow containers.

---

### Required Environment Variables

These variables **must be available to Airflow containers**:

```bash
# GCP
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/google/credentials.json
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET=banking-datalake

# dbt Cloud
DBT_CLOUD_ACCOUNT_ID=your_account_id
DBT_CLOUD_API_TOKEN=your_api_token
DBT_CLOUD_JOB_ID=your_job_id
```

They are consumed by:

* Python ingestion scripts
* Airflow DAG
* dbt Cloud API trigger

---

## 3)  Running the Pipeline Locally

### 1. Start Airflow

```bash
cd orchestration
docker compose up
```

This starts:

* PostgreSQL (Airflow metadata DB)
* Airflow Webserver
* Airflow Scheduler

Access the Airflow UI:

```
http://localhost:8080
```

---

### 2. Trigger the Pipeline

In the Airflow UI:

1. Enable the DAG: `interbank_batch_pipeline`
2. Trigger it manually or wait for the schedule

Pipeline steps:

1. Upload CSV to GCS
2. Load data into BigQuery (`interbank_raw.transactions`)
3. Trigger dbt Cloud job

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

* **Staging**

  * Type casting
  * Timestamp normalization
  * Column standardization
* **Dimensions**

  * `dim_bank`
  * `dim_currency`
* **Fact**

  * `fact_transactions_daily`
* **Reporting**

  * `rpt_bank_daily_volume`

---

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
├── ingestion/
│   ├── load_to_gcs.py
│   └── load_gcs_bq.py
│
├── orchestration/
│   ├── dags/
│   │   └── interbank_batch_dag.py
│   ├── docker-compose.yml
│   └── credentials/
│       └── credentials.json   # not committed
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── dbt_project.yml
│
├── infra/
│   └── terraform/
│
└── README.md
```


