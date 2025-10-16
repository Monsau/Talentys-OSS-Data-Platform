{{
  config(
    materialized='table',
    tags=['phase3', 'marts', 'all-in-one']
  )
}}

-- Tout-en-un: comparaison complète des données clients PostgreSQL vs MinIO
WITH postgres_customers AS (
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
),

minio_customers AS (
    SELECT
        customer_id,
        name,
        email,
        country,
        signup_date,
        CURRENT_TIMESTAMP as _loaded_at,
        'minio' as _source_system
    FROM PostgreSQL_BusinessDB."public".minio_customers_simulation
),

customer_comparison AS (
    SELECT
        COALESCE(p.customer_id, m.customer_id) as customer_id,
        COALESCE(p.email, m.email) as email,
        COALESCE(p.country, m.country) as country,
        
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
        p.created_at as postgres_date,
        m.signup_date as minio_date,
        p._loaded_at as postgres_loaded_at,
        m._loaded_at as minio_loaded_at,
        
        CURRENT_TIMESTAMP as comparison_timestamp
    FROM postgres_customers p
    FULL OUTER JOIN minio_customers m
        ON p.customer_id = m.customer_id
),

quality_summary AS (
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
        SUM(CASE WHEN country_comparison = 'MISMATCH' THEN 1 ELSE 0 END) as country_mismatches
    FROM customer_comparison
)

SELECT
    *,
    -- Taux de couverture
    ROUND(CAST(both_sources AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) as coverage_rate_pct,
    
    -- Taux de qualité  
    ROUND(CAST(email_matches AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) as email_quality_pct,
    ROUND(CAST(country_matches AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) as country_quality_pct,
    
    -- Statut global
    CASE 
        WHEN ROUND(CAST(both_sources AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) = 100 
            AND email_mismatches = 0 AND country_mismatches = 0 
        THEN 'EXCELLENT'
        WHEN ROUND(CAST(both_sources AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) >= 95 THEN 'GOOD'
        WHEN ROUND(CAST(both_sources AS DOUBLE) / NULLIF(total_customers, 0) * 100, 2) >= 80 THEN 'WARNING'
        ELSE 'CRITICAL'
    END as overall_status,
    
    CURRENT_TIMESTAMP as report_timestamp
FROM quality_summary
