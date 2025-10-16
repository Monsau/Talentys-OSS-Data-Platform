-- Résultats de la comparaison Phase 3: PostgreSQL vs MinIO
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
FROM "$scratch"."phase3_all_in_one";
