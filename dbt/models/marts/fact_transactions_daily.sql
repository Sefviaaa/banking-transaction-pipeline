{{ config(materialized='table') }}

-- Aggregated daily summary from fact
SELECT
  transaction_date,
  from_bank AS bank_code,
  payment_currency AS currency_code,
  COUNT(*) AS total_transactions,
  SUM(amount_paid) AS total_amount_paid,
  SUM(amount_received) AS total_amount_received,
  AVG(amount_paid) AS avg_transaction_amount
FROM {{ ref('fact_transactions') }}
GROUP BY 1, 2, 3