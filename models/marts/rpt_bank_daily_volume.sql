SELECT
  transaction_date,
  bank_code,
  SUM(total_amount_paid) AS daily_volume
FROM {{ ref('fact_transactions_daily') }}
GROUP BY 1,2
