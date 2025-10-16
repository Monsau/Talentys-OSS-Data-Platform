{{ config(materialized='view') }}

with source as (
    select * from raw.customers
),

renamed as (
    select
        customer_id,
        full_name as customer_name,
        email,
        city,
        country,
        created_at,
        created_at as updated_at
    from source
)

select * from renamed
