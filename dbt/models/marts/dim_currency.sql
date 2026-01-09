SELECT
  DISTINCT (payment_currency) AS currency_code
FROM {{ ref('stg_interbank_transactions') }}
