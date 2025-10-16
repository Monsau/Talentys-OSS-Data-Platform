-- Test: Vérifie que overall_status correspond aux seuils définis
-- EXCELLENT: coverage_rate_pct = 100 AND email_mismatches = 0 AND country_mismatches = 0
-- GOOD: coverage_rate_pct >= 95
-- WARNING: coverage_rate_pct >= 80
-- CRITICAL: coverage_rate_pct < 80

SELECT
    coverage_rate_pct,
    email_mismatches,
    country_mismatches,
    overall_status,
    CASE
        WHEN coverage_rate_pct = 100 AND email_mismatches = 0 AND country_mismatches = 0 THEN 'EXCELLENT'
        WHEN coverage_rate_pct >= 95 THEN 'GOOD'
        WHEN coverage_rate_pct >= 80 THEN 'WARNING'
        ELSE 'CRITICAL'
    END as expected_status
FROM {{ ref('phase3_all_in_one') }}
WHERE overall_status != CASE
    WHEN coverage_rate_pct = 100 AND email_mismatches = 0 AND country_mismatches = 0 THEN 'EXCELLENT'
    WHEN coverage_rate_pct >= 95 THEN 'GOOD'
    WHEN coverage_rate_pct >= 80 THEN 'WARNING'
    ELSE 'CRITICAL'
END
