{{ config(materialized='table') }}

SELECT
  transaction_date,
  MIN(transaction_hour) AS earliest_hour,
  MAX(transaction_hour) AS latest_hour,
  COUNT(*) AS record_count,
  COUNT(DISTINCT from_bank) AS unique_source_banks,
  COUNT(DISTINCT to_bank) AS unique_dest_banks,
  COUNT(DISTINCT payment_currency) AS unique_currencies,
  CURRENT_TIMESTAMP() AS report_generated_at
FROM {{ ref('fact_transactions') }}
GROUP BY 1