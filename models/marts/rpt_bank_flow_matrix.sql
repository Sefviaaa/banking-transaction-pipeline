{{ config(materialized='table') }}

SELECT
  from_bank,
  to_bank,
  COUNT(*) AS transaction_count,
  SUM(amount_paid) AS total_amount,
  AVG(amount_paid) AS avg_amount
FROM {{ ref('fact_transactions') }}
GROUP BY 1, 2