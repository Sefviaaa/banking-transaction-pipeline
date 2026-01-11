import os
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
) as dag:

    ingest_to_gcs = BashOperator(
        task_id="ingest_to_gcs",
        bash_command="python /opt/airflow/ingestion/load_to_gcs.py",
    )

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

    load_gcs_to_bigquery = BashOperator(
    task_id="load_gcs_to_bigquery",
    bash_command="python /opt/airflow/ingestion/load_gcs_bq.py",
    )

    ingest_to_gcs >> load_gcs_to_bigquery >> trigger_dbt_cloud