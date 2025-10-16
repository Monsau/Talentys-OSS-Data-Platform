{{
  config(
    materialized='table',
    tags=['phase3', 'intermediate', 'quality']
  )
}}

-- Comparaison des données entre PostgreSQL et MinIO
WITH postgres_data AS (
    SELECT
        customer_id,
        email,
        country,
        created_at as source_date,
        _loaded_at,
        _source_system
    FROM {{ ref('phase3_stg_postgres_customers') }}
),

minio_data AS (
    SELECT
        customer_id,
        email,
        country,
        signup_date as source_date,
        _loaded_at,
        _source_system
    FROM {{ ref('phase3_stg_minio_customers') }}
),

comparison AS (
    SELECT
        COALESCE(p.customer_id, m.customer_id) as customer_id,
        COALESCE(p.email, m.email) as email,
        
        -- Indicateurs de présence
        CASE WHEN p.customer_id IS NOT NULL THEN 1 ELSE 0 END as in_postgres,
        CASE WHEN m.customer_id IS NOT NULL THEN 1 ELSE 0 END as in_minio,
        
        -- Comparaison des champs
        CASE 
            WHEN p.email = m.email THEN 'MATCH'
            WHEN p.email IS NULL OR m.email IS NULL THEN 'MISSING'
            ELSE 'MISMATCH'
        END as email_comparison,
        
        CASE 
            WHEN p.country = m.country THEN 'MATCH'
            WHEN p.country IS NULL OR m.country IS NULL THEN 'MISSING'
            ELSE 'MISMATCH'
        END as country_comparison,
        
        -- Métadonnées
        p.source_date as postgres_date,
        m.source_date as minio_date,
        p._loaded_at as postgres_loaded_at,
        m._loaded_at as minio_loaded_at,
        
        CURRENT_TIMESTAMP as comparison_timestamp
    FROM postgres_data p
    FULL OUTER JOIN minio_data m
        ON p.customer_id = m.customer_id
)

SELECT * FROM comparison
