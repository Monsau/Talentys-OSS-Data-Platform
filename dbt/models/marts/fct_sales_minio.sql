{{ config(materialized='table') }}

with minio_sales as (
    select * from {{ ref('stg_minio_sales') }}
),

sales_summary as (
    select
        category,
        region,
        count(*) as total_sales_count,
        sum(quantity) as total_quantity_sold,
        sum(total_amount) as total_revenue,
        avg(unit_price) as avg_unit_price,
        avg(discount) as avg_discount
    from minio_sales
    group by category, region
)

select * from sales_summary
order by total_revenue desc
