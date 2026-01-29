terraform {
  required_version = ">= 1.3.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "raw_data" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "raw" {
  dataset_id = "interbank_raw"
  location   = var.region
}

resource "google_bigquery_dataset" "staging" {
  dataset_id = "interbank_dev"
  location   = var.region
}

resource "google_bigquery_dataset" "prod" {
  dataset_id = "interbank_prod"
  location   = var.region
}
