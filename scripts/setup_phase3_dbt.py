#!/usr/bin/env python3
"""
Setup Phase 3 - dbt Advanced Models for Airbyte Data
Automatically creates all dbt models, tests, and configurations for Airbyte integration

Requirements:
- Airbyte configured and running
- MinIO_Airbyte_Staging source in Dremio
- At least 1 Airbyte sync completed

Usage:
    python scripts/setup_phase3_dbt.py
"""

import os
import sys
from pathlib import Path


def print_header():
    """Print script header"""
    print("\n" + "="*70)
    print(" 🚀 PHASE 3 - dbt ADVANCED MODELS SETUP")
    print("="*70 + "\n")


def print_step(step, total, message):
    """Print step information"""
    print(f"[{step}/{total}] {message}...")


def print_success(message):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message):
    """Print error message"""
    print(f"✗ ERROR: {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ {message}")


def ensure_directory(path):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_dbt_path():
    """Get dbt project path"""
    # Try multiple possible locations
    possible_paths = [
        "dremio_connector/dbt",
        "c:/projets/dremio/dremio_connector/dbt",
        "c:/projets/dremiodbt/dremio_connector/dbt"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Default to first option
    return "dremio_connector/dbt"


# File contents
SOURCES_YML_ADDITION = """
  # Airbyte source
  - name: airbyte_staging
    description: "Data ingested by Airbyte from PostgreSQL"
    database: MinIO_Airbyte_Staging
    schema: "airbyte-staging"
    
    tables:
      - name: data_customers
        description: "Customers data synced via Airbyte"
        identifier: data/customers
        columns:
          - name: id
            description: "Customer ID"
            tests:
              - not_null
              - unique
          
          - name: first_name
            description: "Customer first name"
          
          - name: last_name
            description: "Customer last name"
          
          - name: email
            description: "Customer email"
            tests:
              - not_null
          
          - name: created_at
            description: "Customer creation timestamp"
          
          - name: _airbyte_ab_id
            description: "Airbyte internal ID"
            tests:
              - not_null
          
          - name: _airbyte_emitted_at
            description: "Timestamp when Airbyte emitted the record"
            tests:
              - not_null
      
      - name: data_orders
        description: "Orders data synced via Airbyte"
        identifier: data/orders
        columns:
          - name: id
            description: "Order ID"
            tests:
              - not_null
              - unique
          
          - name: customer_id
            description: "Foreign key to customers"
            tests:
              - not_null
          
          - name: order_date
            description: "Order date"
          
          - name: total_amount
            description: "Order total amount"
          
          - name: status
            description: "Order status"
          
          - name: _airbyte_ab_id
            description: "Airbyte internal ID"
            tests:
              - not_null
          
          - name: _airbyte_emitted_at
            description: "Timestamp when Airbyte emitted the record"
            tests:
              - not_null
"""

STG_AIRBYTE_CUSTOMERS = """{{
  config(
    materialized='view',
    tags=['staging', 'airbyte', 'customers']
  )
}}

WITH source AS (
    SELECT * FROM {{ source('airbyte_staging', 'data_customers') }}
),

renamed AS (
    SELECT
        id AS customer_id,
        first_name,
        last_name,
        email,
        created_at,
        
        -- Airbyte metadata
        _airbyte_ab_id AS airbyte_record_id,
        _airbyte_emitted_at AS airbyte_synced_at,
        
        -- Data quality flags
        CASE 
            WHEN first_name IS NULL OR last_name IS NULL THEN 'incomplete'
            WHEN email IS NULL THEN 'missing_email'
            ELSE 'complete'
        END AS data_quality_flag,
        
        -- Sync metadata
        'airbyte' AS source_system,
        CURRENT_TIMESTAMP AS dbt_loaded_at

    FROM source
)

SELECT * FROM renamed
"""

STG_AIRBYTE_ORDERS = """{{
  config(
    materialized='view',
    tags=['staging', 'airbyte', 'orders']
  )
}}

WITH source AS (
    SELECT * FROM {{ source('airbyte_staging', 'data_orders') }}
),

renamed AS (
    SELECT
        id AS order_id,
        customer_id,
        order_date,
        total_amount,
        status,
        
        -- Airbyte metadata
        _airbyte_ab_id AS airbyte_record_id,
        _airbyte_emitted_at AS airbyte_synced_at,
        
        -- Data quality flags
        CASE 
            WHEN total_amount < 0 THEN 'invalid_amount'
            WHEN status NOT IN ('pending', 'completed', 'cancelled') THEN 'invalid_status'
            ELSE 'valid'
        END AS data_quality_flag,
        
        -- Sync metadata
        'airbyte' AS source_system,
        CURRENT_TIMESTAMP AS dbt_loaded_at

    FROM source
)

SELECT * FROM renamed
"""

INT_CUSTOMER_COMPARISON = """{{
  config(
    materialized='table',
    tags=['intermediate', 'comparison', 'airbyte']
  )
}}

WITH postgres_customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

airbyte_customers AS (
    SELECT * FROM {{ ref('stg_airbyte_customers') }}
),

comparison AS (
    SELECT
        COALESCE(p.customer_id, a.customer_id) AS customer_id,
        
        -- Source presence flags
        CASE WHEN p.customer_id IS NOT NULL THEN TRUE ELSE FALSE END AS in_postgres,
        CASE WHEN a.customer_id IS NOT NULL THEN TRUE ELSE FALSE END AS in_airbyte,
        
        -- Data comparison
        CASE 
            WHEN p.customer_id IS NULL THEN 'only_in_airbyte'
            WHEN a.customer_id IS NULL THEN 'only_in_postgres'
            WHEN p.email != a.email THEN 'data_mismatch'
            ELSE 'match'
        END AS sync_status,
        
        -- PostgreSQL data
        p.first_name AS postgres_first_name,
        p.last_name AS postgres_last_name,
        p.email AS postgres_email,
        
        -- Airbyte data
        a.first_name AS airbyte_first_name,
        a.last_name AS airbyte_last_name,
        a.email AS airbyte_email,
        a.airbyte_synced_at,
        
        CURRENT_TIMESTAMP AS comparison_timestamp
    
    FROM postgres_customers p
    FULL OUTER JOIN airbyte_customers a
        ON p.customer_id = a.customer_id
)

SELECT * FROM comparison
"""

INT_AIRBYTE_METADATA = """{{
  config(
    materialized='table',
    tags=['intermediate', 'metadata', 'airbyte']
  )
}}

WITH airbyte_customers AS (
    SELECT
        'customers' AS table_name,
        COUNT(*) AS record_count,
        MIN(airbyte_synced_at) AS earliest_sync,
        MAX(airbyte_synced_at) AS latest_sync,
        COUNT(CASE WHEN data_quality_flag != 'complete' THEN 1 END) AS quality_issues_count
    FROM {{ ref('stg_airbyte_customers') }}
),

airbyte_orders AS (
    SELECT
        'orders' AS table_name,
        COUNT(*) AS record_count,
        MIN(airbyte_synced_at) AS earliest_sync,
        MAX(airbyte_synced_at) AS latest_sync,
        COUNT(CASE WHEN data_quality_flag != 'valid' THEN 1 END) AS quality_issues_count
    FROM {{ ref('stg_airbyte_orders') }}
),

combined AS (
    SELECT * FROM airbyte_customers
    UNION ALL
    SELECT * FROM airbyte_orders
)

SELECT
    table_name,
    record_count,
    earliest_sync,
    latest_sync,
    quality_issues_count,
    ROUND(
        (record_count - quality_issues_count) * 100.0 / NULLIF(record_count, 0),
        2
    ) AS data_quality_percentage,
    CURRENT_TIMESTAMP AS calculated_at
FROM combined
"""

MART_CUSTOMER_360 = """{{
  config(
    materialized='table',
    tags=['mart', 'business', 'customer-360']
  )
}}

WITH postgres_customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

airbyte_customers AS (
    SELECT * FROM {{ ref('stg_airbyte_customers') }}
),

customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        SUM(total_amount) AS total_spent,
        MAX(order_date) AS last_order_date
    FROM {{ ref('stg_orders') }}
    GROUP BY customer_id
),

unified AS (
    SELECT
        COALESCE(p.customer_id, a.customer_id) AS customer_id,
        
        -- Use PostgreSQL as primary, Airbyte as fallback
        COALESCE(p.first_name, a.first_name) AS first_name,
        COALESCE(p.last_name, a.last_name) AS last_name,
        COALESCE(p.email, a.email) AS email,
        
        -- Data source tracking
        CASE 
            WHEN p.customer_id IS NOT NULL AND a.customer_id IS NOT NULL THEN 'both'
            WHEN p.customer_id IS NOT NULL THEN 'postgres_only'
            ELSE 'airbyte_only'
        END AS data_source,
        
        -- Airbyte sync info
        a.airbyte_synced_at,
        
        -- Order aggregations
        COALESCE(o.total_orders, 0) AS total_orders,
        COALESCE(o.total_spent, 0) AS total_spent,
        o.last_order_date,
        
        -- Customer segments
        CASE
            WHEN COALESCE(o.total_orders, 0) = 0 THEN 'no_orders'
            WHEN o.total_orders = 1 THEN 'one_time'
            WHEN o.total_orders BETWEEN 2 AND 5 THEN 'occasional'
            WHEN o.total_orders > 5 THEN 'frequent'
        END AS customer_segment,
        
        CASE
            WHEN COALESCE(o.total_spent, 0) = 0 THEN 'no_spend'
            WHEN o.total_spent < 100 THEN 'low_value'
            WHEN o.total_spent BETWEEN 100 AND 500 THEN 'medium_value'
            WHEN o.total_spent > 500 THEN 'high_value'
        END AS value_segment,
        
        CURRENT_TIMESTAMP AS loaded_at
    
    FROM postgres_customers p
    FULL OUTER JOIN airbyte_customers a
        ON p.customer_id = a.customer_id
    LEFT JOIN customer_orders o
        ON COALESCE(p.customer_id, a.customer_id) = o.customer_id
)

SELECT * FROM unified
"""

MART_AIRBYTE_QUALITY = """{{
  config(
    materialized='table',
    tags=['mart', 'operational', 'quality', 'airbyte']
  )
}}

WITH metadata AS (
    SELECT * FROM {{ ref('int_airbyte_metadata') }}
),

comparison AS (
    SELECT
        COUNT(*) AS total_records,
        COUNT(CASE WHEN sync_status = 'match' THEN 1 END) AS matched_records,
        COUNT(CASE WHEN sync_status = 'data_mismatch' THEN 1 END) AS mismatched_records,
        COUNT(CASE WHEN sync_status = 'only_in_postgres' THEN 1 END) AS missing_in_airbyte,
        COUNT(CASE WHEN sync_status = 'only_in_airbyte' THEN 1 END) AS extra_in_airbyte
    FROM {{ ref('int_customer_comparison') }}
),

quality_report AS (
    SELECT
        'Airbyte Data Quality Report' AS report_name,
        
        -- Metadata metrics
        (SELECT SUM(record_count) FROM metadata) AS total_airbyte_records,
        (SELECT AVG(data_quality_percentage) FROM metadata) AS avg_quality_percentage,
        (SELECT MAX(latest_sync) FROM metadata) AS last_sync_timestamp,
        
        -- Comparison metrics
        c.total_records AS comparison_total,
        c.matched_records,
        c.mismatched_records,
        c.missing_in_airbyte,
        c.extra_in_airbyte,
        
        -- Calculated metrics
        ROUND(c.matched_records * 100.0 / NULLIF(c.total_records, 0), 2) AS match_percentage,
        
        -- Quality score (0-100)
        ROUND(
            (
                (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) * 0.6 +
                ((SELECT AVG(data_quality_percentage) FROM metadata) * 0.4)
            ),
            2
        ) AS overall_quality_score,
        
        -- Status
        CASE
            WHEN (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) > 95 THEN 'excellent'
            WHEN (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) > 90 THEN 'good'
            WHEN (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) > 80 THEN 'acceptable'
            ELSE 'needs_attention'
        END AS quality_status,
        
        CURRENT_TIMESTAMP AS report_generated_at
    
    FROM comparison c
)

SELECT * FROM quality_report
"""

MART_DATA_FRESHNESS = """{{
  config(
    materialized='table',
    tags=['mart', 'operational', 'freshness', 'airbyte']
  )
}}

WITH airbyte_tables AS (
    SELECT * FROM {{ ref('int_airbyte_metadata') }}
),

freshness_report AS (
    SELECT
        table_name,
        record_count,
        latest_sync,
        
        -- Freshness status
        CASE
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '1' HOUR THEN 'very_fresh'
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '6' HOUR THEN 'fresh'
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '12' HOUR THEN 'acceptable'
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '24' HOUR THEN 'stale'
            ELSE 'very_stale'
        END AS freshness_status,
        
        -- Expected next sync (assuming 6-hour schedule)
        latest_sync + INTERVAL '6' HOUR AS expected_next_sync,
        
        CURRENT_TIMESTAMP AS report_generated_at
    
    FROM airbyte_tables
)

SELECT * FROM freshness_report
"""

TEST_AIRBYTE_DATA_QUALITY = """-- Test: Airbyte metadata columns must be present and not null

WITH airbyte_customers AS (
    SELECT
        airbyte_record_id,
        airbyte_synced_at
    FROM {{ ref('stg_airbyte_customers') }}
    WHERE airbyte_record_id IS NULL
       OR airbyte_synced_at IS NULL
),

airbyte_orders AS (
    SELECT
        airbyte_record_id,
        airbyte_synced_at
    FROM {{ ref('stg_airbyte_orders') }}
    WHERE airbyte_record_id IS NULL
       OR airbyte_synced_at IS NULL
)

SELECT * FROM airbyte_customers
UNION ALL
SELECT * FROM airbyte_orders
"""

TEST_AIRBYTE_VS_SOURCE = """-- Test: Ensure Airbyte has synced at least 90% of source records

WITH comparison AS (
    SELECT
        COUNT(CASE WHEN sync_status IN ('match', 'data_mismatch') THEN 1 END) AS synced_records,
        COUNT(CASE WHEN sync_status = 'only_in_postgres' THEN 1 END) AS missing_records,
        COUNT(*) AS total_records
    FROM {{ ref('int_customer_comparison') }}
),

sync_percentage AS (
    SELECT
        synced_records,
        missing_records,
        total_records,
        ROUND(synced_records * 100.0 / NULLIF(total_records, 0), 2) AS sync_percentage
    FROM comparison
)

SELECT *
FROM sync_percentage
WHERE sync_percentage < 90
"""


def create_staging_models(dbt_path):
    """Create staging models for Airbyte data"""
    staging_path = os.path.join(dbt_path, "models", "staging")
    ensure_directory(staging_path)
    
    # stg_airbyte_customers.sql
    with open(os.path.join(staging_path, "stg_airbyte_customers.sql"), "w") as f:
        f.write(STG_AIRBYTE_CUSTOMERS)
    
    # stg_airbyte_orders.sql
    with open(os.path.join(staging_path, "stg_airbyte_orders.sql"), "w") as f:
        f.write(STG_AIRBYTE_ORDERS)
    
    print_success("Staging models created (2 files)")


def create_intermediate_models(dbt_path):
    """Create intermediate models"""
    intermediate_path = os.path.join(dbt_path, "models", "intermediate")
    ensure_directory(intermediate_path)
    
    # int_customer_comparison.sql
    with open(os.path.join(intermediate_path, "int_customer_comparison.sql"), "w") as f:
        f.write(INT_CUSTOMER_COMPARISON)
    
    # int_airbyte_metadata.sql
    with open(os.path.join(intermediate_path, "int_airbyte_metadata.sql"), "w") as f:
        f.write(INT_AIRBYTE_METADATA)
    
    print_success("Intermediate models created (2 files)")


def create_mart_models(dbt_path):
    """Create mart models"""
    # Business marts
    business_path = os.path.join(dbt_path, "models", "marts", "business")
    ensure_directory(business_path)
    
    with open(os.path.join(business_path, "mart_customer_360.sql"), "w") as f:
        f.write(MART_CUSTOMER_360)
    
    # Operational marts
    operational_path = os.path.join(dbt_path, "models", "marts", "operational")
    ensure_directory(operational_path)
    
    with open(os.path.join(operational_path, "mart_airbyte_quality.sql"), "w") as f:
        f.write(MART_AIRBYTE_QUALITY)
    
    with open(os.path.join(operational_path, "mart_data_freshness.sql"), "w") as f:
        f.write(MART_DATA_FRESHNESS)
    
    print_success("Mart models created (3 files)")


def create_tests(dbt_path):
    """Create custom tests"""
    tests_path = os.path.join(dbt_path, "tests")
    ensure_directory(tests_path)
    
    # airbyte_data_quality.sql
    with open(os.path.join(tests_path, "airbyte_data_quality.sql"), "w") as f:
        f.write(TEST_AIRBYTE_DATA_QUALITY)
    
    # airbyte_vs_source_comparison.sql
    with open(os.path.join(tests_path, "airbyte_vs_source_comparison.sql"), "w") as f:
        f.write(TEST_AIRBYTE_VS_SOURCE)
    
    print_success("Custom tests created (2 files)")


def update_sources_yml(dbt_path):
    """Update sources.yml with Airbyte source"""
    sources_file = os.path.join(dbt_path, "models", "sources.yml")
    
    if os.path.exists(sources_file):
        with open(sources_file, "r") as f:
            content = f.read()
        
        # Check if airbyte_staging already exists
        if "airbyte_staging" not in content:
            with open(sources_file, "a") as f:
                f.write(SOURCES_YML_ADDITION)
            print_success("sources.yml updated with Airbyte source")
        else:
            print_info("sources.yml already contains Airbyte source")
    else:
        print_info("sources.yml not found, creating new one")
        sources_path = os.path.join(dbt_path, "models")
        ensure_directory(sources_path)
        
        with open(sources_file, "w") as f:
            f.write("version: 2\n\nsources:\n")
            f.write(SOURCES_YML_ADDITION)
        
        print_success("sources.yml created with Airbyte source")


def print_summary():
    """Print setup summary"""
    print("\n" + "="*70)
    print(" ✓ PHASE 3 SETUP COMPLETE!")
    print("="*70 + "\n")
    
    print("📁 Files Created:\n")
    print("Staging models (2):")
    print("  - stg_airbyte_customers.sql")
    print("  - stg_airbyte_orders.sql\n")
    
    print("Intermediate models (2):")
    print("  - int_customer_comparison.sql")
    print("  - int_airbyte_metadata.sql\n")
    
    print("Marts (3):")
    print("  - mart_customer_360.sql (business)")
    print("  - mart_airbyte_quality.sql (operational)")
    print("  - mart_data_freshness.sql (operational)\n")
    
    print("Tests (2):")
    print("  - airbyte_data_quality.sql")
    print("  - airbyte_vs_source_comparison.sql\n")
    
    print("Configuration (1):")
    print("  - sources.yml (updated)\n")
    
    print("="*70)
    print("🚀 Next Steps:\n")
    print("1. Build staging models:")
    print("   cd dremio_connector/dbt")
    print("   dbt run --models staging.stg_airbyte_*\n")
    
    print("2. Build intermediate models:")
    print("   dbt run --models intermediate.*\n")
    
    print("3. Build marts:")
    print("   dbt run --models marts.*\n")
    
    print("4. Run tests:")
    print("   dbt test\n")
    
    print("5. Generate documentation:")
    print("   dbt docs generate")
    print("   dbt docs serve\n")
    
    print("📚 Documentation:")
    print("   - PHASE3_DBT_ADVANCED.md (complete guide)")
    print("   - Check dbt logs for any errors\n")


def main():
    """Main execution"""
    print_header()
    
    total_steps = 5
    
    # Step 1: Get dbt path
    print_step(1, total_steps, "Locating dbt project")
    dbt_path = get_dbt_path()
    
    if not os.path.exists(dbt_path):
        print_info(f"Creating dbt directory: {dbt_path}")
        ensure_directory(dbt_path)
    
    print_success(f"dbt project path: {dbt_path}")
    print()
    
    # Step 2: Create staging models
    print_step(2, total_steps, "Creating staging models")
    create_staging_models(dbt_path)
    print()
    
    # Step 3: Create intermediate models
    print_step(3, total_steps, "Creating intermediate models")
    create_intermediate_models(dbt_path)
    print()
    
    # Step 4: Create mart models
    print_step(4, total_steps, "Creating mart models")
    create_mart_models(dbt_path)
    print()
    
    # Step 5: Create tests and update sources
    print_step(5, total_steps, "Creating tests and updating configuration")
    create_tests(dbt_path)
    update_sources_yml(dbt_path)
    print()
    
    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
