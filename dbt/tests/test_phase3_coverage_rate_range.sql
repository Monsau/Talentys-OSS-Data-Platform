-- Test: Vérifie que le coverage_rate_pct est dans la plage [0, 100]

SELECT
    coverage_rate_pct
FROM {{ ref('phase3_all_in_one') }}
WHERE coverage_rate_pct < 0 
   OR coverage_rate_pct > 100
   OR coverage_rate_pct IS NULL
