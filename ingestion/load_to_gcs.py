import os
from google.cloud import storage
from datetime import datetime


PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "noted-aloe-481504-u4")
BUCKET_NAME = os.environ.get("GCS_RAW_BUCKET", "banking-datalake")

LOCAL_DATA_PATH = "/opt/airflow/ingestion/data/raw/LI-Medium_Trans.csv"
GCS_BASE_PATH = "interbank_transactions"

## SOURCE_PATH = "../data/raw/LI-Medium_Trans.csv"

def upload_to_gcs():
    """Uploads a file to Google Cloud Storage."""

    # Create a client
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    
    ingestion_date = datetime.utcnow().strftime("%Y-%m-%d")
    destination_blob = f"raw/interbank_transactions/ingestion_date={ingestion_date}/transactions.csv"
    
    # Create a blob object
    blob = bucket.blob(destination_blob)

    print(f"Uploading {LOCAL_DATA_PATH} to gs://{BUCKET_NAME}/{destination_blob}...")

    # Upload the file
    blob.upload_from_filename(LOCAL_DATA_PATH)
    
    print(f"File {LOCAL_DATA_PATH} uploaded to {destination_blob} in bucket {BUCKET_NAME}.")

if __name__ == "__main__":
    upload_to_gcs()