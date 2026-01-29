import pytest
from unittest.mock import patch, MagicMock


@patch.dict('os.environ', {
    'GCS_RAW_BUCKET': 'test-bucket',
    'GCP_PROJECT_ID': 'test-project'
})
def test_upload_to_gcs_file_not_found():
    """Test that FileNotFoundError is raised when source file doesn't exist"""
    from ingestion.load_to_gcs import upload_to_gcs

    with patch('ingestion.load_to_gcs.os.path.exists', return_value=False):
        with pytest.raises(FileNotFoundError):
            upload_to_gcs()


@patch.dict('os.environ', {
    'GCS_RAW_BUCKET': 'test-bucket',
    'GCP_PROJECT_ID': 'test-project'
})
def test_upload_to_gcs_success():
    """Test successful upload to GCS"""
    from ingestion.load_to_gcs import upload_to_gcs

    with patch('ingestion.load_to_gcs.storage.Client') as mock_client:
        with patch('ingestion.load_to_gcs.os.path.exists', return_value=True):
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            mock_client.return_value.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob

            upload_to_gcs()

            mock_bucket.blob.assert_called_once()
            mock_blob.upload_from_filename.assert_called_once()
