output "bucket_name" {
  value = google_storage_bucket.raw_data.name
}

output "datasets" {
  value = [
    google_bigquery_dataset.raw.dataset_id,
    google_bigquery_dataset.staging.dataset_id,
    google_bigquery_dataset.prod.dataset_id
  ]
}
