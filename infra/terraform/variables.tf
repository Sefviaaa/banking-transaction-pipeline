variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "US"
}

variable "bucket_name" {
  description = "GCS bucket for raw data"
  type        = string
}
