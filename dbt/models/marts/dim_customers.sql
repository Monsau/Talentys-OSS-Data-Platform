{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_orders as (
    select
        customer_id,
        count(*) as total_orders,
        sum(amount) as total_amount,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from orders
    where status = 'completed'
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.customer_name,
        c.email,
        c.city,
        c.country,
        c.created_at,
        c.updated_at,
        coalesce(co.total_orders, 0) as total_orders,
        coalesce(co.total_amount, 0) as total_amount,
        co.first_order_date,
        co.last_order_date,
        case 
            when co.total_amount > 1000 then 'VIP'
            when co.total_amount > 500 then 'Premium'
            else 'Standard'
        end as customer_segment
    from customers c
    left join customer_orders co on c.customer_id = co.customer_id
)

select * from final
