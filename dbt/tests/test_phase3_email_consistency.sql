-- Test: Vérifie que email_mismatches = both_sources - email_matches

SELECT
    both_sources,
    email_matches,
    email_mismatches,
    (both_sources - email_matches) as calculated_mismatches
FROM {{ ref('phase3_all_in_one') }}
WHERE email_mismatches != (both_sources - email_matches)
