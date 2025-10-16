{{ config(materialized='view') }}

SELECT 
    "timestamp" as log_timestamp,
    "level" as log_level,
    service,
    message,
    request_id,
    CAST(NULL AS INTEGER) as duration_ms,  -- Field not mapped
    COALESCE(status_code, 0) as status_code,
    CASE 
        WHEN status_code >= 500 THEN 'SERVER_ERROR'
        WHEN status_code >= 400 THEN 'CLIENT_ERROR'
        WHEN status_code >= 300 THEN 'REDIRECT'
        WHEN status_code >= 200 THEN 'SUCCESS'
        ELSE 'UNKNOWN'
    END as status_category,
    CASE 
        WHEN "level" = 'ERROR' THEN 1
        ELSE 0
    END as is_error,
    environment,
    host
FROM elasticsearch.application_logs."_doc"
