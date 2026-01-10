import os
import logging
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "noted-aloe-481504-u4")
BUCKET_NAME = os.environ.get("GCS_RAW_BUCKET", "banking-datalake")

LOCAL_DATA_PATH = "/opt/airflow/ingestion/data/raw/LI-Medium_Trans.csv"
GCS_BASE_PATH = "interbank_transactions"

## SOURCE_PATH = "../data/raw/LI-Medium_Trans.csv"

def upload_to_gcs():
    """Uploads a file to Google Cloud Storage."""
    try:
        # Validate environment variables
        if not BUCKET_NAME:
            raise ValueError("GCS_RAW_BUCKET environment variable not set")
        
        if not os.path.exists(LOCAL_DATA_PATH):
            raise FileNotFoundError(f"Source file not found: {LOCAL_DATA_PATH}")
        
        # Create a client
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        
        ingestion_date = datetime.utcnow().strftime("%Y-%m-%d")
        destination_blob = f"raw/interbank_transactions/ingestion_date={ingestion_date}/transactions.csv"
        
        # Create a blob object
        blob = bucket.blob(destination_blob)

        logger.info(f"Uploading {LOCAL_DATA_PATH} to gs://{BUCKET_NAME}/{destination_blob}...")

        # Upload the file
        blob.upload_from_filename(LOCAL_DATA_PATH)
        
        logger.info(f"Successfully uploaded to gs://{BUCKET_NAME}/{destination_blob}")
    
    except FileNotFoundError:
        logger.error(f"Source file not found: {LOCAL_DATA_PATH}")
        raise
    except GoogleAPIError as e:
        logger.error(f"GCS upload failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise

if __name__ == "__main__":
    upload_to_gcs()