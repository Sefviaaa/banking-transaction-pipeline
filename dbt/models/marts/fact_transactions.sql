{{ config(
    materialized='incremental',
    unique_key='transaction_id',
    partition_by={
      "field": "transaction_date",
      "data_type": "date"
    },
    cluster_by=["from_bank", "to_bank", "payment_currency"],
    incremental_strategy='merge'
) }}

-- Granular fact table (one row per transaction)
-- Incremental: only processes new records on subsequent runs
SELECT
  -- Surrogate key for deduplication
  {{ dbt_utils.generate_surrogate_key(['transaction_ts', 'from_account', 'to_account', 'amount_paid']) }} as transaction_id,
  
  -- Original timestamp for incremental filtering
  transaction_ts,
  
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

{% if is_incremental() %}
-- Only process new records since last run
WHERE transaction_ts > (SELECT MAX(transaction_ts) FROM {{ this }})
{% endif %}