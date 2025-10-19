# dbt Models

This directory contains dbt (data build tool) models for transforming data in Dremio.

## 📁 Structure

```
dbt/
├── models/           # SQL transformation models
│   ├── staging/     # Raw data cleaning and standardization
│   ├── intermediate/# Business logic transformations
│   └── marts/       # Final analytics-ready tables
├── tests/           # Data quality tests
├── macros/          # Reusable SQL functions
├── seeds/           # Static CSV data
└── dbt_project.yml  # Project configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- dbt-core installed
- dbt-dremio adapter
- Access to Dremio instance

### Installation

```bash
# Install dbt with Dremio adapter
pip install dbt-core dbt-dremio

# Navigate to dbt directory
cd dbt

# Configure profiles.yml
cp profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml with your Dremio connection details
```

### Configuration

Edit `~/.dbt/profiles.yml`:

```yaml
default:
  outputs:
    dev:
      type: dremio
      host: localhost
      port: 9047
      user: your_username
      password: your_password
      database: dremio
      schema: dev
      threads: 4
  target: dev
```

## 📊 Running dbt

### Test Connection

```bash
# Test Dremio connection
dbt debug
```

### Run Models

```bash
# Run all models
dbt run

# Run specific model
dbt run --select model_name

# Run models in specific directory
dbt run --select staging.*
```

### Test Data Quality

```bash
# Run all tests
dbt test

# Test specific model
dbt test --select model_name
```

### Generate Documentation

```bash
# Generate and serve documentation
dbt docs generate
dbt docs serve
```

## 📝 Model Organization

### Staging Models (`models/staging/`)

Clean and standardize raw data from source systems.

- **Purpose**: Rename columns, cast data types, basic cleaning
- **Naming**: `stg_<source>__<entity>.sql`
- **Example**: `stg_minio__transactions.sql`

### Intermediate Models (`models/intermediate/`)

Apply business logic and combine multiple sources.

- **Purpose**: Complex transformations, business rules
- **Naming**: `int_<entity>__<description>.sql`
- **Example**: `int_sales__enriched.sql`

### Mart Models (`models/marts/`)

Final analytics-ready tables for reporting and dashboards.

- **Purpose**: Wide tables optimized for queries
- **Naming**: `<domain>__<entity>.sql`
- **Example**: `finance__revenue_summary.sql`

## 🧪 Testing

### Schema Tests

Define tests in `schema.yml`:

```yaml
models:
  - name: stg_transactions
    columns:
      - name: transaction_id
        tests:
          - unique
          - not_null
      - name: amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
```

### Custom Tests

Create custom data quality tests in `tests/`:

```sql
-- tests/assert_positive_revenue.sql
SELECT *
FROM {{ ref('finance__revenue_summary') }}
WHERE total_revenue < 0
```

## 🔄 Development Workflow

1. **Create Branch**
   ```bash
   git checkout -b feature/new-model
   ```

2. **Develop Model**
   - Write SQL transformation
   - Add tests in schema.yml
   - Document columns

3. **Test Locally**
   ```bash
   dbt run --select +my_model
   dbt test --select my_model
   ```

4. **Generate Docs**
   ```bash
   dbt docs generate
   ```

5. **Commit & Push**
   ```bash
   git add .
   git commit -m "Add new model"
   git push origin feature/new-model
   ```

## 📚 Best Practices

### Naming Conventions

- **Models**: `snake_case`
- **Columns**: `snake_case`
- **CTEs**: `snake_case`
- **Macros**: `snake_case`

### Documentation

Document all models with descriptions:

```yaml
models:
  - name: finance__revenue_summary
    description: |
      Daily revenue summary aggregated by product and region.
      Updated daily at 2 AM UTC.
    columns:
      - name: revenue_date
        description: Date of the revenue transaction
      - name: total_revenue
        description: Sum of all revenues for the day
```

### Performance

- Use incremental models for large tables
- Materialize intermediate results
- Partition by date where applicable
- Use Dremio reflections for frequently queried tables

### Version Control

- Commit model changes with clear messages
- Use branches for new features
- Review SQL before merging
- Tag releases with version numbers

## 🔗 Integration with Dremio

### Reflections

Create Dremio reflections for dbt models:

```sql
-- In Dremio SQL Runner
ALTER TABLE finance__revenue_summary
CREATE AGGREGATE REFLECTION revenue_summary_agg
USING DIMENSIONS (revenue_date, product_id)
MEASURES (total_revenue (SUM))
PARTITION BY (revenue_date);
```

### Spaces

Organize dbt output in Dremio spaces:

- `DEV` - Development models
- `STAGING` - Staging models
- `PROD` - Production marts

## 📖 Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt-dremio Adapter](https://github.com/dremio/dbt-dremio)
- [Dremio Documentation](https://docs.dremio.com/)
- [dbt Discourse](https://discourse.getdbt.com/)

## 🆘 Troubleshooting

### Connection Issues

```bash
# Test connection
dbt debug

# Check profiles.yml location
dbt --version
```

### Model Compilation Errors

```bash
# Compile without running
dbt compile

# Parse project
dbt parse
```

### Performance Issues

```bash
# Run with specific threads
dbt run --threads 8

# Run specific models
dbt run --select tag:critical
```

## 📧 Support

For questions or issues:

- GitHub Issues: [data-platform-iso-opensource](https://github.com/Monsau/data-platform-iso-opensource)
- Email: support@talentys.eu
- Documentation: See main [README.md](../README.md)

---

**Last Updated**: 2025-10-19  
**Version**: 1.0.0  
**Maintainer**: Mustapha Fonsau
