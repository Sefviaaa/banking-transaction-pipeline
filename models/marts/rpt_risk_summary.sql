{{ config(materialized='table') }}

SELECT
  transaction_date,
  value_tier,
  payment_format,
  COUNT(*) AS transaction_count,
  SUM(amount_paid) AS total_amount,
  SUM(CASE WHEN is_laundering = 1 THEN 1 ELSE 0 END) AS flagged_count,
  ROUND(SAFE_DIVIDE(
    SUM(CASE WHEN is_laundering = 1 THEN 1 ELSE 0 END) * 100.0,
    COUNT(*)
  ), 2) AS flag_rate_pct
FROM {{ ref('fact_transactions') }}
GROUP BY 1, 2, 3