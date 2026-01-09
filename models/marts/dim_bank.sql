SELECT
  DISTINCT (from_bank) AS bank_code
FROM {{ ref('stg_interbank_transactions') }}
