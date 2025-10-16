{{ config(materialized='table') }}

WITH pg_sales AS (
    SELECT 
        CAST(order_date AS DATE) as business_day,
        'PostgreSQL' as source,
        amount as revenue,
        1 as transactions,
        amount as avg_order_value
    FROM {{ ref('fct_orders') }}
),

minio_sales AS (
    SELECT 
        sale_date as business_day,
        'MinIO' as source,
        total_amount as revenue,
        1 as transactions,
        total_amount as avg_order_value
    FROM {{ ref('stg_minio_sales') }}
),

platform_health AS (
    SELECT 
        report_day as business_day,
        service,
        error_count,
        conversions,
        purchases,
        active_users,
        avg_cpu_percent,
        avg_memory_mb,
        conversion_rate_pct,
        error_rate_pct_logs
    FROM {{ ref('fct_platform_health') }}
),

-- Agrégation des ventes par jour (tous les sources)
daily_sales AS (
    SELECT 
        business_day,
        source,
        SUM(revenue) as total_revenue,
        SUM(transactions) as total_transactions,
        AVG(avg_order_value) as avg_order_value
    FROM (
        SELECT * FROM pg_sales
        UNION ALL
        SELECT * FROM minio_sales
    ) all_sales
    GROUP BY 1, 2
),

-- Agrégation de la santé de la plateforme
daily_platform AS (
    SELECT 
        business_day,
        SUM(error_count) as total_errors,
        SUM(conversions) as total_conversions,
        SUM(purchases) as total_purchases,
        MAX(active_users) as unique_users,
        AVG(avg_cpu_percent) as platform_avg_cpu,
        AVG(avg_memory_mb) as platform_avg_memory,
        AVG(conversion_rate_pct) as avg_conversion_rate,
        AVG(error_rate_pct_logs) as avg_error_rate
    FROM platform_health
    GROUP BY 1
)

SELECT 
    COALESCE(s.business_day, p.business_day) as business_date,
    
    -- Sales metrics (from PostgreSQL + MinIO)
    MAX(CASE WHEN s.source = 'PostgreSQL' THEN s.total_revenue ELSE 0 END) as pg_revenue,
    MAX(CASE WHEN s.source = 'PostgreSQL' THEN s.total_transactions ELSE 0 END) as pg_transactions,
    MAX(CASE WHEN s.source = 'MinIO' THEN s.total_revenue ELSE 0 END) as minio_revenue,
    MAX(CASE WHEN s.source = 'MinIO' THEN s.total_transactions ELSE 0 END) as minio_transactions,
    SUM(s.total_revenue) as combined_revenue,
    SUM(s.total_transactions) as combined_transactions,
    
    -- Platform health metrics (from Elasticsearch)
    COALESCE(p.total_errors, 0) as platform_errors,
    COALESCE(p.total_conversions, 0) as web_conversions,
    COALESCE(p.total_purchases, 0) as web_purchases,
    COALESCE(p.unique_users, 0) as active_users,
    COALESCE(p.platform_avg_cpu, 0) as avg_cpu_usage,
    COALESCE(p.platform_avg_memory, 0) as avg_memory_usage,
    COALESCE(p.avg_conversion_rate, 0) as conversion_rate,
    COALESCE(p.avg_error_rate, 0) as error_rate,
    
    -- Business KPIs
    CASE 
        WHEN SUM(s.total_transactions) > 0 
        THEN SUM(s.total_revenue) / SUM(s.total_transactions)
        ELSE 0
    END as avg_transaction_value,
    
    CASE 
        WHEN p.unique_users > 0 
        THEN CAST(p.total_conversions AS FLOAT) / p.unique_users * 100
        ELSE 0
    END as user_conversion_rate_pct,
    
    CASE 
        WHEN p.total_errors > 10 THEN 'HIGH'
        WHEN p.total_errors > 5 THEN 'MEDIUM'
        ELSE 'LOW'
    END as error_severity,
    
    CASE 
        WHEN p.platform_avg_cpu > 80 THEN 'CRITICAL'
        WHEN p.platform_avg_cpu > 60 THEN 'WARNING'
        ELSE 'NORMAL'
    END as system_health_status

FROM daily_sales s
FULL OUTER JOIN daily_platform p ON s.business_day = p.business_day
GROUP BY COALESCE(s.business_day, p.business_day), p.total_errors, p.total_conversions, 
         p.total_purchases, p.unique_users, p.platform_avg_cpu, 
         p.platform_avg_memory, p.avg_conversion_rate, p.avg_error_rate
