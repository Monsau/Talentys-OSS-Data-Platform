{{
  config(
    materialized='table',
    tags=['phase3', 'marts', 'quality', 'monitoring']
  )
}}

-- Rapport de qualité des données pour monitoring
WITH data_quality AS (
    SELECT * FROM {{ ref('mart_customer_360') }}
),

detailed_issues AS (
    SELECT
        customer_id,
        email,
        CASE 
            WHEN in_postgres = 0 THEN 'MISSING_IN_POSTGRES'
            WHEN in_minio = 0 THEN 'MISSING_IN_MINIO'
            WHEN email_comparison = 'MISMATCH' THEN 'EMAIL_MISMATCH'
            WHEN country_comparison = 'MISMATCH' THEN 'COUNTRY_MISMATCH'
            ELSE 'NO_ISSUE'
        END as issue_type,
        email_comparison,
        country_comparison,
        postgres_date,
        minio_date
    FROM {{ ref('int_customer_comparison') }}
    WHERE 
        in_postgres = 0 
        OR in_minio = 0 
        OR email_comparison = 'MISMATCH'
        OR country_comparison = 'MISMATCH'
)

SELECT
    -- Résumé global
    (SELECT total_customers FROM data_quality) as total_customers,
    (SELECT coverage_rate_pct FROM data_quality) as coverage_rate,
    (SELECT email_quality_pct FROM data_quality) as email_quality,
    (SELECT country_quality_pct FROM data_quality) as country_quality,
    
    -- Problèmes détaillés
    COUNT(*) as total_issues,
    SUM(CASE WHEN issue_type = 'MISSING_IN_POSTGRES' THEN 1 ELSE 0 END) as missing_postgres,
    SUM(CASE WHEN issue_type = 'MISSING_IN_MINIO' THEN 1 ELSE 0 END) as missing_minio,
    SUM(CASE WHEN issue_type = 'EMAIL_MISMATCH' THEN 1 ELSE 0 END) as email_mismatches,
    SUM(CASE WHEN issue_type = 'COUNTRY_MISMATCH' THEN 1 ELSE 0 END) as country_mismatches,
    
    -- Statut global
    CASE 
        WHEN COUNT(*) = 0 THEN 'EXCELLENT'
        WHEN (SELECT coverage_rate_pct FROM data_quality) >= 95 THEN 'GOOD'
        WHEN (SELECT coverage_rate_pct FROM data_quality) >= 80 THEN 'WARNING'
        ELSE 'CRITICAL'
    END as overall_status,
    
    CURRENT_TIMESTAMP as report_timestamp
FROM detailed_issues
