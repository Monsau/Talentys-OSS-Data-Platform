{{
  config(
    materialized='table',
    tags=['phase3', 'marts', 'quality']
  )
}}

-- Vue 360° des clients avec données de toutes les sources
WITH customer_comparison AS (
    SELECT * FROM {{ ref('int_customer_comparison') }}
),

quality_metrics AS (
    SELECT
        COUNT(*) as total_customers,
        SUM(in_postgres) as postgres_count,
        SUM(in_minio) as minio_count,
        SUM(CASE WHEN in_postgres = 1 AND in_minio = 1 THEN 1 ELSE 0 END) as both_sources,
        SUM(CASE WHEN in_postgres = 1 AND in_minio = 0 THEN 1 ELSE 0 END) as postgres_only,
        SUM(CASE WHEN in_postgres = 0 AND in_minio = 1 THEN 1 ELSE 0 END) as minio_only,
        
        -- Qualité des données
        SUM(CASE WHEN email_comparison = 'MATCH' THEN 1 ELSE 0 END) as email_matches,
        SUM(CASE WHEN email_comparison = 'MISMATCH' THEN 1 ELSE 0 END) as email_mismatches,
        SUM(CASE WHEN country_comparison = 'MATCH' THEN 1 ELSE 0 END) as country_matches,
        SUM(CASE WHEN country_comparison = 'MISMATCH' THEN 1 ELSE 0 END) as country_mismatches,
        
        CURRENT_TIMESTAMP as calculated_at
    FROM customer_comparison
)

SELECT
    *,
    -- Taux de couverture
    ROUND(CAST(both_sources AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) as coverage_rate_pct,
    
    -- Taux de qualité
    ROUND(CAST(email_matches AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) as email_quality_pct,
    ROUND(CAST(country_matches AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) as country_quality_pct
FROM quality_metrics
