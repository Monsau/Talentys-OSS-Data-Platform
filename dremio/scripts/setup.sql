-- Create sample raw data tables in Dremio

-- Create raw schema
CREATE SCHEMA IF NOT EXISTS raw;

-- Create sample customers table
CREATE TABLE raw.customers AS
SELECT
  1 as customer_id,
  'John Doe' as customer_name,
  'john@example.com' as email,
  CURRENT_TIMESTAMP as created_at,
  CURRENT_TIMESTAMP as updated_at
UNION ALL
SELECT
  2 as customer_id,
  'Jane Smith' as customer_name,
  'jane@example.com' as email,
  CURRENT_TIMESTAMP as created_at,
  CURRENT_TIMESTAMP as updated_at;

-- Create sample orders table
CREATE TABLE raw.orders AS
SELECT
  1 as order_id,
  1 as customer_id,
  CURRENT_DATE as order_date,
  100.50 as amount,
  'completed' as status,
  CURRENT_TIMESTAMP as created_at
UNION ALL
SELECT
  2 as order_id,
  2 as customer_id,
  CURRENT_DATE as order_date,
  250.75 as amount,
  'completed' as status,
  CURRENT_TIMESTAMP as created_at;
