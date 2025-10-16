{{
  config(
    materialized='view',
    tags=['phase3', 'results']
  )
}}

-- Vue des résultats Phase 3
SELECT 
    'Phase 3 - PostgreSQL vs MinIO Comparison' as report_title,
    total_customers,
    postgres_count,
    minio_count,
    both_sources,
    postgres_only,
    minio_only,
    coverage_rate_pct as coverage_pct,
    email_matches,
    email_mismatches,
    email_quality_pct as email_quality,
    country_matches,
    country_mismatches,
    country_quality_pct as country_quality,
    overall_status,
    report_timestamp
FROM "$scratch"."phase3_all_in_one"
