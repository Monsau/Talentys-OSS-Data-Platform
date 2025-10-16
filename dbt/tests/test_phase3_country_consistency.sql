-- Test: Vérifie que country_mismatches = both_sources - country_matches

SELECT
    both_sources,
    country_matches,
    country_mismatches,
    (both_sources - country_matches) as calculated_mismatches
FROM {{ ref('phase3_all_in_one') }}
WHERE country_mismatches != (both_sources - country_matches)
