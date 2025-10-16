{{ config(materialized='view') }}

SELECT 
    "timestamp" as event_timestamp,
    event_type,
    CAST(NULL AS INTEGER) as user_id,  -- Field not mapped in Dremio
    session_id,
    page,
    action,
    device,
    browser,
    country,
    referrer,
    CASE 
        WHEN event_type IN ('purchase', 'signup', 'conversion') THEN 1
        ELSE 0
    END as is_conversion,
    CASE 
        WHEN event_type = 'purchase' THEN 1
        ELSE 0
    END as is_purchase,
    CASE 
        WHEN event_type IN ('click', 'page_view') THEN 1
        ELSE 0
    END as is_engagement
FROM elasticsearch.user_events."_doc"
