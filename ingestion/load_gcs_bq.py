from google.cloud import bigquery
from google.api_core.exceptions import NotFound

PROJECT_ID = "noted-aloe-481504-u4"
DATASET_ID = "interbank_raw"
TABLE_ID = "transactions"

GCS_URI = "gs://banking-datalake/raw/interbank_transactions/ingestion_date=*/transactions.csv"


def ensure_dataset(client, dataset_id):
    """
    Correct and safe dataset creation
    """
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, dataset_id)

    try:
        client.get_dataset(dataset_ref)
        print(f"[OK] Dataset {dataset_id} already exists")

    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # MUST match bucket & project
        client.create_dataset(dataset)
        print(f"[CREATE] Dataset {dataset_id} created")


def load_gcs_to_bq():
    client = bigquery.Client(project=PROJECT_ID)

    # 1️⃣ ENSURE DATASET EXISTS 
    ensure_dataset(client, DATASET_ID)

    # 2️⃣ DEFINE SCHEMA 
    schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("from_bank", "STRING"),
        bigquery.SchemaField("from_account", "STRING"),
        bigquery.SchemaField("to_bank", "STRING"),
        bigquery.SchemaField("to_account", "STRING"),
        bigquery.SchemaField("amount_received", "FLOAT"),
        bigquery.SchemaField("receiving_currency", "STRING"),
        bigquery.SchemaField("amount_paid", "FLOAT"),
        bigquery.SchemaField("payment_currency", "STRING"),
        bigquery.SchemaField("payment_format", "STRING"),
        bigquery.SchemaField("is_laundering", "INTEGER"),
    ]

    # 3️⃣ LOAD CONFIG
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_quoted_newlines=True,
        ignore_unknown_values=True,
    )

    # 4️⃣ LOAD DATA
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    load_job = client.load_table_from_uri(
        GCS_URI,
        table_ref,
        job_config=job_config,
    )

    load_job.result()  

    print(f"[SUCCESS] Loaded data into {table_ref}")


if __name__ == "__main__":
    load_gcs_to_bq()
