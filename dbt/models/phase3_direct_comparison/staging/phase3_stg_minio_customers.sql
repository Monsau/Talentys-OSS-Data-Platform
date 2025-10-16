{{
  config(
    materialized='view',
    tags=['phase3', 'staging', 'minio']
  )
}}

-- Staging layer pour les clients MinIO (using simulation table with intentional data quality issues)
SELECT
    customer_id,
    name,
    email,
    country,
    signup_date,
    CURRENT_TIMESTAMP as _loaded_at,
    'minio' as _source_system
FROM PostgreSQL_BusinessDB."public".minio_customers_simulation
