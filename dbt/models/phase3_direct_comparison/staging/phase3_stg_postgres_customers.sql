{{
  config(
    materialized='view',
    tags=['phase3', 'staging', 'postgres']
  )
}}

-- Staging layer pour les clients PostgreSQL
SELECT
    id as customer_id,
    first_name,
    last_name,
    email,
    phone,
    address,
    city,
    country,
    created_at,
    CURRENT_TIMESTAMP as _loaded_at,
    'postgres' as _source_system
FROM PostgreSQL_BusinessDB."public".customers
