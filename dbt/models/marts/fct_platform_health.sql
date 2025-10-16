{{ config(materialized='table') }}

WITH error_summary AS (
    SELECT 
        CAST(log_timestamp AS DATE) as log_day,
        service,
        COUNT(*) as total_logs,
        SUM(is_error) as error_count,
        AVG(duration_ms) as avg_duration_ms,
        MAX(duration_ms) as max_duration_ms
    FROM {{ ref('stg_es_logs') }}
    GROUP BY 1, 2
),

conversion_summary AS (
    SELECT 
        CAST(event_timestamp AS DATE) as event_day,
        COUNT(*) as total_events,
        SUM(is_conversion) as conversion_count,
        SUM(is_purchase) as purchase_count,
        SUM(is_engagement) as engagement_count,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT session_id) as unique_sessions
    FROM {{ ref('stg_es_events') }}
    GROUP BY 1
),

metrics_summary AS (
    SELECT 
        CAST(metric_timestamp AS DATE) as metric_day,
        service,
        AVG(CASE WHEN metric_name = 'cpu_usage' THEN metric_value END) as avg_cpu_pct,
        AVG(CASE WHEN metric_name = 'memory_usage' THEN metric_value END) as avg_memory_mb,
        AVG(CASE WHEN metric_name = 'request_latency' THEN metric_value END) as avg_latency_ms,
        AVG(CASE WHEN metric_name = 'error_rate' THEN metric_value END) as avg_error_rate,
        MAX(CASE WHEN metric_name = 'cpu_usage' THEN metric_value END) as max_cpu_pct,
        SUM(is_critical) as critical_metrics_count
    FROM {{ ref('stg_es_metrics') }}
    GROUP BY 1, 2
)

SELECT 
    COALESCE(e.log_day, c.event_day, m.metric_day) as report_day,
    COALESCE(e.service, m.service, 'ALL') as service,
    
    -- Error metrics
    COALESCE(e.total_logs, 0) as total_logs,
    COALESCE(e.error_count, 0) as error_count,
    COALESCE(e.avg_duration_ms, 0) as avg_request_duration_ms,
    COALESCE(e.max_duration_ms, 0) as max_request_duration_ms,
    
    -- User activity metrics
    COALESCE(c.total_events, 0) as total_user_events,
    COALESCE(c.conversion_count, 0) as conversions,
    COALESCE(c.purchase_count, 0) as purchases,
    COALESCE(c.engagement_count, 0) as engagement_events,
    COALESCE(c.unique_users, 0) as active_users,
    COALESCE(c.unique_sessions, 0) as sessions,
    
    -- Performance metrics
    COALESCE(m.avg_cpu_pct, 0) as avg_cpu_percent,
    COALESCE(m.avg_memory_mb, 0) as avg_memory_mb,
    COALESCE(m.avg_latency_ms, 0) as avg_latency_ms,
    COALESCE(m.avg_error_rate, 0) as avg_error_rate_pct,
    COALESCE(m.max_cpu_pct, 0) as max_cpu_percent,
    COALESCE(m.critical_metrics_count, 0) as critical_alerts,
    
    -- Calculated KPIs
    CASE 
        WHEN c.total_events > 0 
        THEN CAST(c.conversion_count AS FLOAT) / c.total_events * 100
        ELSE 0
    END as conversion_rate_pct,
    
    CASE 
        WHEN e.total_logs > 0 
        THEN CAST(e.error_count AS FLOAT) / e.total_logs * 100
        ELSE 0
    END as error_rate_pct_logs

FROM error_summary e
FULL OUTER JOIN conversion_summary c 
    ON e.log_day = c.event_day
FULL OUTER JOIN metrics_summary m 
    ON COALESCE(e.log_day, c.event_day) = m.metric_day 
    AND COALESCE(e.service, 'ALL') = m.service
