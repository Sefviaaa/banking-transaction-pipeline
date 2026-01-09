SELECT
  DATE(transaction_ts) AS transaction_date,
  from_bank AS bank_code,
  payment_currency AS currency_code,
  COUNT(*) AS total_transactions,
  SUM(amount_paid) AS total_amount_paid
FROM {{ ref('stg_interbank_transactions') }}
GROUP BY 1,2,3
