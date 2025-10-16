with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

final as (
    select
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.email,
        o.order_date,
        o.amount,
        o.status,
        o.created_at
    from orders o
    left join customers c on o.customer_id = c.customer_id
)

select * from final
