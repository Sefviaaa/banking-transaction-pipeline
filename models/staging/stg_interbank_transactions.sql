SELECT
  timestamp AS transaction_ts,
  from_bank,
  from_account,
  to_bank,
  to_account,
  SAFE_CAST(amount_received AS FLOAT64) AS amount_received,
  receiving_currency,
  SAFE_CAST(amount_paid AS FLOAT64) AS amount_paid,
  payment_currency,
  TRIM(UPPER(payment_format)) AS payment_format,
  SAFE_CAST(is_laundering AS INT64) AS is_laundering
FROM {{ source('interbank_raw', 'transactions') }}
WHERE timestamp IS NOT NULL
