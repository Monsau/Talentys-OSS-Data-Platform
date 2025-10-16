{{ config(materialized='view') }}

-- MinIO customers bucket doesn't exist yet, using PostgreSQL data
with source as (
    select * from PostgreSQL_BusinessDB."public".customers
),

cleaned as (
    select
        id as customer_id,
        first_name || ' ' || last_name as customer_name,
        email,
        phone,
        city,
        country
    from source
)

select * from cleaned
