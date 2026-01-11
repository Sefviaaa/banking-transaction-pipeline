{{ config(
    materialized='table',
    partition_by={
      "field": "transaction_date",
      "data_type": "date"
    },
    cluster_by=["from_bank", "to_bank", "payment_currency"]
) }}

-- Granular fact table (one row per transaction)
SELECT
  -- Time dimensions
  DATE(transaction_ts) AS transaction_date,
  EXTRACT(HOUR FROM transaction_ts) AS transaction_hour,
  EXTRACT(DAYOFWEEK FROM transaction_ts) AS day_of_week,
  
  -- Bank dimensions
  from_bank,
  to_bank,
  from_account,
  to_account,
  
  -- Currency dimensions
  payment_currency,
  receiving_currency,
  
  -- Amount measures
  amount_paid,
  amount_received,
  
  -- Transaction attributes
  payment_format,
  is_laundering,
  
  -- Derived measures
  CASE 
    WHEN amount_paid > 100000 THEN 'High'
    WHEN amount_paid > 10000 THEN 'Medium'
    ELSE 'Standard'
  END AS value_tier

FROM {{ ref('stg_interbank_transactions') }}