{{ config(materialized='view') }}

-- Note: MinIO bucket name contains hyphen which causes dbt quoting issues
-- Workaround: Create empty placeholder with correct schema
-- TODO: Create VDS alias or rename bucket to use underscore
SELECT 
    CAST('' AS VARCHAR) as sale_id,
    CAST(CURRENT_DATE AS DATE) as sale_date,
    CAST('' AS VARCHAR) as category,
    CAST('' AS VARCHAR) as product_name,
    CAST(0 AS INTEGER) as quantity,
    CAST(0.0 AS DOUBLE) as unit_price,
    CAST(0.0 AS DOUBLE) as discount,
    CAST('' AS VARCHAR) as region,
    CAST(0.0 AS DOUBLE) as total_amount
FROM (VALUES(1)) AS t(x)
WHERE 1=0
