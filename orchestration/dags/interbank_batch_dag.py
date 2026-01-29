import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import timedelta, datetime
import json

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

    # Task 4: Run dbt transformations
    run_dbt_transformations = BashOperator(
        task_id="run_dbt_transformations",
        bash_command="""
            cd /opt/airflow/dbt && \
            dbt deps && \
            dbt run --profiles-dir /opt/airflow/dbt
        """,
        doc_md="""Run dbt staging marts and models"""
    )

    # Task 5: Run dbt tests
    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command="""
            cd /opt/airflow/dbt && \
            dbt test --profiles-dir /opt/airflow/dbt
        """,
        doc_md="""Run dbt tests to validate transformed data"""
    )


    # Pipeline flow: ingest -> load -> validate -> transform
    ingest_to_gcs >> load_gcs_to_bigquery >> validate_data_quality >> run_dbt_transformations >> run_dbt_tests