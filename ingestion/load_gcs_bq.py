import os
import logging
from google.cloud import bigquery
from google.api_core.exceptions import NotFound, GoogleAPIError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration from environment variables
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
DATASET_ID = os.environ.get("BQ_DATASET_ID")
TABLE_ID = os.environ.get("BQ_TABLE_ID")
BUCKET_NAME = os.environ.get("GCS_RAW_BUCKET")
GCS_BASE_PATH = "raw/interbank_transactions"

# Validate required environment variables
if not PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable not set")
if not BUCKET_NAME:
    raise ValueError("GCS_RAW_BUCKET environment variable not set")

GCS_URI = f"gs://{BUCKET_NAME}/{GCS_BASE_PATH}/ingestion_date=*/transactions.csv"

SCHEMA = [
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


def ensure_dataset(client: bigquery.Client, dataset_id: str) -> None:
    """
    Dataset creation
    """
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, dataset_id)

    try:
        client.get_dataset(dataset_ref)
        logger.info(f"Dataset {dataset_id} already exists")

    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # MUST match bucket & project
        client.create_dataset(dataset)
        logger.info(f"Dataset {dataset_id} created successfully")
    except GoogleAPIError as e:
        logger.error(f"Failed to ensure dataset {dataset_id}: {e}")
        raise


def load_gcs_to_bq():
    try:
        logger.info("Starting BigQuery load operation")
        client = bigquery.Client(project=PROJECT_ID)

        ensure_dataset(client, DATASET_ID)

        # 3️⃣ LOAD CONFIG
        job_config = bigquery.LoadJobConfig(
            schema=SCHEMA,
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            allow_quoted_newlines=True,
            ignore_unknown_values=True,
        )

        # 4️⃣ LOAD DATA
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        logger.info(f"Loading data from {GCS_URI} to {table_ref}")

        load_job = client.load_table_from_uri(
            GCS_URI,
            table_ref,
            job_config=job_config,
        )

        load_job.result()

        logger.info(f"Successfully loaded data into {table_ref}")

    except GoogleAPIError as e:
        logger.error(f"BigQuery operation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during BigQuery load: {e}")
        raise


if __name__ == "__main__":
    load_gcs_to_bq()
