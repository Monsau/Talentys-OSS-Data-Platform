-- Test: Vérifie que le total des customers est cohérent
-- total_customers doit être égal à postgres_only + minio_only + both_sources

SELECT
    total_customers,
    postgres_only,
    minio_only,
    both_sources,
    (postgres_only + minio_only + both_sources) as calculated_total
FROM {{ ref('phase3_all_in_one') }}
WHERE total_customers != (postgres_only + minio_only + both_sources)
