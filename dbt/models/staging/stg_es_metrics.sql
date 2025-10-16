{{ config(materialized='view') }}

SELECT 
    "timestamp" as metric_timestamp,
    metric_type as metric_name,
    service,
    "value" as metric_value,
    host,
    environment,
    CASE 
        WHEN metric_type = 'cpu_usage' AND "value" > 80 THEN 1
        WHEN metric_type = 'memory_usage' AND "value" > 85 THEN 1
        WHEN metric_type = 'error_rate' AND "value" > 5 THEN 1
        ELSE 0
    END as is_critical
FROM elasticsearch.performance_metrics."_doc"
