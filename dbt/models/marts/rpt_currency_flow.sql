{{ config(materialized='table') }}

SELECT
  payment_currency AS source_currency,
  receiving_currency AS target_currency,
  COUNT(*) AS transaction_count,
  SUM(amount_paid) AS total_paid,
  SUM(amount_received) AS total_received,
  AVG(SAFE_DIVIDE(amount_received, amount_paid)) AS avg_exchange_rate
FROM {{ ref('fact_transactions') }}
GROUP BY 1, 2