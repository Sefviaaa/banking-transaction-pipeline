import os
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.models import Variable
from datetime import datetime
import json

DBT_ACCOUNT_ID = os.getenv(
    "DBT_CLOUD_ACCOUNT_ID",
    Variable.get("DBT_CLOUD_ACCOUNT_ID", default_var=None)
)

DBT_API_TOKEN = os.getenv(
    "DBT_CLOUD_API_TOKEN",
    Variable.get("DBT_CLOUD_API_TOKEN", default_var=None)
)

DBT_JOB_ID = os.getenv(
    "DBT_CLOUD_JOB_ID",
    Variable.get("DBT_CLOUD_JOB_ID", default_var=None)
)

if not DBT_ACCOUNT_ID or not DBT_API_TOKEN or not DBT_JOB_ID:
    raise ValueError("DBT Cloud credentials not set")

with DAG(
    dag_id="interbank_batch_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,  # Prevent overlapping runs
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5)
    },
    tags=["banking", "batch", "production"],
    doc_md="""
    ## Interbank Batch Pipeline
    
    End-to-end batch pipeline for processing inter-bank transactions.
    
    ### Pipeline Flow:
    1. **Ingest to GCS**: Upload raw CSV to Cloud Storage
    2. **Load to BigQuery**: Load data into raw dataset
    3. **Data Quality Check**: Validate data with Great Expectations
    4. **dbt Transformations**: Run staging, facts, and reporting models
    """,
) as dag:

    # Task 1: Ingest raw data to GCS
    ingest_to_gcs = BashOperator(
        task_id="ingest_to_gcs",
        bash_command="python /opt/airflow/ingestion/load_to_gcs.py",
    )

    # Task 2: Load from GCS to BigQuery raw layer
    load_gcs_to_bigquery = BashOperator(
        task_id="load_gcs_to_bigquery",
        bash_command="python /opt/airflow/ingestion/load_gcs_bq.py",
    )

    # Task 3: Data quality validation with Great Expectations
    validate_data_quality = BashOperator(
        task_id="validate_data_quality",
        bash_command="python /opt/airflow/great_expectations/run_validation.py",
        doc_md="Runs data quality checks on raw transaction data before transformation.",
    )

    # Task 4: Trigger dbt Cloud transformations
    trigger_dbt_cloud = SimpleHttpOperator(
        task_id="trigger_dbt_cloud_job",
        http_conn_id="dbt_cloud",
        endpoint=f"api/v2/accounts/{DBT_ACCOUNT_ID}/jobs/{DBT_JOB_ID}/run/",
        method="POST",
        headers={
            "Authorization": f"Token {DBT_API_TOKEN}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "cause": "Triggered by Airflow interbank pipeline"
        }),
        log_response=True,
    )

    # Pipeline flow: ingest -> load -> validate -> transform
    ingest_to_gcs >> load_gcs_to_bigquery >> validate_data_quality >> trigger_dbt_cloud