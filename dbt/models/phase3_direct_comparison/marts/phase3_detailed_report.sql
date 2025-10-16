{{
  config(
    materialized='view',
    tags=['phase3', 'detailed_results']
  )
}}

-- Rapport détaillé Phase 3 - Résultats complets
SELECT 
    total_customers,
    postgres_count,
    minio_count,
    both_sources,
    postgres_only,
    minio_only,
    coverage_rate_pct,
    email_matches,
    email_mismatches,
    email_quality_pct,
    country_matches,
    country_mismatches,
    country_quality_pct,
    overall_status,
    report_timestamp
FROM "$scratch"."phase3_all_in_one"
