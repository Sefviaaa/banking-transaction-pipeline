import os
import logging
from datetime import datetime
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET_NAME = os.environ.get("GCS_RAW_BUCKET")

LOCAL_DATA_PATH = "/opt/airflow/ingestion/data/raw/LI-Medium_Trans.csv.gz"
GCS_BASE_PATH = "raw/interbank_transactions"


def upload_to_gcs():
    """Uploads a file to Google Cloud Storage with ingestion-date partitioning."""
    # Validate environment variables
    if not BUCKET_NAME:
        raise ValueError("GCS_RAW_BUCKET environment variable not set")

    if not os.path.exists(LOCAL_DATA_PATH):
        raise FileNotFoundError(f"Source file not found: {LOCAL_DATA_PATH}")
    
    ingestion_date = datetime.utcnow().strftime("%Y-%m-%d")
    destination_blob = f"{GCS_BASE_PATH}/ingestion_date={ingestion_date}/transactions.csv"
    
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob)

        logger.info(f"Uploading {LOCAL_DATA_PATH} to gs://{BUCKET_NAME}/{destination_blob}...")

        # Upload the file
        blob.upload_from_filename(LOCAL_DATA_PATH)

        logger.info(f"Successfully uploaded to gs://{BUCKET_NAME}/{destination_blob}")

    except GoogleAPIError as e:
        logger.error(f"GCS upload failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise


if __name__ == "__main__":
    upload_to_gcs()
