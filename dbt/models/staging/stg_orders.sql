{{ config(materialized='view') }}

with source as (
    select * from raw.orders
),

renamed as (
    select
        order_id,
        customer_id,
        order_date,
        total_amount as amount,
        status,
        order_date as created_at
    from source
)

select * from renamed
