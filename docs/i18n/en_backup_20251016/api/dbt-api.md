# dbt API Reference

**Version**: 3.2.0  
**Last Updated**: October 16, 2025  
**Language**: English

## Table of Contents

1. [Overview](#overview)
2. [CLI Commands](#cli-commands)
3. [Python API](#python-api)
4. [Metadata Files](#metadata-files)
5. [dbt Cloud API](#dbt-cloud-api)
6. [Custom Macros](#custom-macros)

---

## Overview

dbt provides three primary interfaces:

| Interface | Use Case | Access |
|-----------|----------|--------|
| CLI | Development, CI/CD | Command line |
| Python API | Programmatic execution | Python code |
| dbt Cloud API | Managed service | REST API |
| Metadata | Introspection | JSON files |

---

## CLI Commands

### Core Commands

#### dbt run

Execute models to transform data.

```bash
# Run all models
dbt run

# Run specific model
dbt run --select customers

# Run model and upstream dependencies
dbt run --select +customers

# Run model and downstream dependencies
dbt run --select customers+

# Run models in specific folder
dbt run --select staging.*

# Run modified models only
dbt run --select state:modified

# Full refresh (ignore incremental logic)
dbt run --full-refresh

# Run with specific target
dbt run --target prod
```

**Options**:
```bash
--select (-s)      # Select models to run
--exclude (-x)     # Exclude models
--full-refresh     # Rebuild incremental models
--vars             # Pass variables
--threads          # Number of threads (default: 1)
--target           # Target profile
```

#### dbt test

Run data quality tests.

```bash
# Run all tests
dbt test

# Test specific model
dbt test --select customers

# Run only schema tests
dbt test --select test_type:schema

# Run only data tests
dbt test --select test_type:data

# Store test failures
dbt test --store-failures

# Fail on warn severity
dbt test --warn-error
```

#### dbt build

Run models, tests, seeds, and snapshots together.

```bash
# Build everything
dbt build

# Build with selection
dbt build --select +customers

# Build modified models and tests
dbt build --select state:modified+
```

#### dbt docs

Generate and serve documentation.

```bash
# Generate documentation
dbt docs generate

# Serve documentation locally
dbt docs serve --port 8080

# Generate with target
dbt docs generate --target prod
```

### Development Commands

#### dbt compile

Compile models to SQL without running.

```bash
# Compile all models
dbt compile

# Compile specific model
dbt compile --select customers

# View compiled SQL
cat target/compiled/project_name/models/staging/stg_customers.sql
```

#### dbt debug

Test database connection and configuration.

```bash
dbt debug

# Expected output:
# Configuration:
#   profiles.yml file [OK found and valid]
#   dbt_project.yml file [OK found and valid]
# 
# Connection:
#   host: localhost
#   port: 9047
#   user: admin
#   Connection test: [OK connection ok]
```

#### dbt ls (list)

List resources in project.

```bash
# List all models
dbt ls --resource-type model

# List all tests
dbt ls --resource-type test

# List all sources
dbt ls --resource-type source

# List with selection
dbt ls --select staging.*
```

### Data Commands

#### dbt seed

Load CSV files into database.

```bash
# Load all seeds
dbt seed

# Load specific seed
dbt seed --select country_codes

# Full refresh seeds
dbt seed --full-refresh
```

#### dbt snapshot

Create type-2 slowly changing dimension tables.

```bash
# Run all snapshots
dbt snapshot

# Run specific snapshot
dbt snapshot --select orders_snapshot
```

### Utility Commands

#### dbt clean

Remove compiled files and artifacts.

```bash
dbt clean
# Removes: target/, dbt_packages/, logs/
```

#### dbt deps

Install packages from packages.yml.

```bash
dbt deps

# Force reinstall
dbt deps --force
```

#### dbt init

Initialize new dbt project.

```bash
dbt init my_project
```

---

## Python API

### Basic Execution

```python
import dbt.main

# Run dbt commands programmatically
result = dbt.main.handle_and_check([
    "run",
    "--select", "customers"
])

# result is exit code (0 = success, 1+ = error)
if result == 0:
    print("dbt run succeeded")
else:
    print("dbt run failed")
```

### Complete Python Wrapper

```python
import dbt.main
import json
from pathlib import Path

class DbtProject:
    """Wrapper for dbt CLI operations"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
    
    def _run_command(self, command: list) -> int:
        """Execute dbt command"""
        return dbt.main.handle_and_check(command)
    
    def run(self, select: str = None, exclude: str = None, 
            full_refresh: bool = False, target: str = None) -> bool:
        """Run dbt models"""
        cmd = ["run", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        if exclude:
            cmd.extend(["--exclude", exclude])
        if full_refresh:
            cmd.append("--full-refresh")
        if target:
            cmd.extend(["--target", target])
        
        return self._run_command(cmd) == 0
    
    def test(self, select: str = None, store_failures: bool = False) -> bool:
        """Run dbt tests"""
        cmd = ["test", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        if store_failures:
            cmd.append("--store-failures")
        
        return self._run_command(cmd) == 0
    
    def build(self, select: str = None) -> bool:
        """Build models and run tests"""
        cmd = ["build", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        
        return self._run_command(cmd) == 0
    
    def compile(self, select: str = None) -> bool:
        """Compile dbt models"""
        cmd = ["compile", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        
        return self._run_command(cmd) == 0
    
    def docs_generate(self) -> bool:
        """Generate documentation"""
        cmd = ["docs", "generate", "--project-dir", str(self.project_dir)]
        return self._run_command(cmd) == 0
    
    def get_manifest(self) -> dict:
        """Load manifest.json"""
        manifest_path = self.project_dir / "target" / "manifest.json"
        
        if not manifest_path.exists():
            raise FileNotFoundError("manifest.json not found. Run dbt compile first.")
        
        with open(manifest_path) as f:
            return json.load(f)
    
    def get_run_results(self) -> dict:
        """Load run_results.json"""
        results_path = self.project_dir / "target" / "run_results.json"
        
        if not results_path.exists():
            raise FileNotFoundError("run_results.json not found. Run dbt first.")
        
        with open(results_path) as f:
            return json.load(f)

# Usage example
if __name__ == "__main__":
    dbt = DbtProject("/path/to/dbt/project")
    
    # Compile models
    if dbt.compile():
        print("Compilation successful")
    
    # Run staging models
    if dbt.run(select="staging.*"):
        print("Staging models ran successfully")
    
    # Run tests on marts
    if dbt.test(select="marts.*"):
        print("All tests passed")
    
    # Get manifest
    manifest = dbt.get_manifest()
    print(f"Found {len(manifest['nodes'])} nodes")
```

### Airflow Integration

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def run_dbt_models(**context):
    """Run dbt models"""
    import dbt.main
    
    result = dbt.main.handle_and_check([
        "run",
        "--project-dir", "/opt/airflow/dbt/dremio_project",
        "--profiles-dir", "/opt/airflow/dbt",
        "--select", "staging.*"
    ])
    
    if result != 0:
        raise Exception("dbt run failed")

def run_dbt_tests(**context):
    """Run dbt tests"""
    import dbt.main
    
    result = dbt.main.handle_and_check([
        "test",
        "--project-dir", "/opt/airflow/dbt/dremio_project",
        "--profiles-dir", "/opt/airflow/dbt"
    ])
    
    if result != 0:
        raise Exception("dbt tests failed")

# Define DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'dbt_daily_run',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # 2 AM daily
    catchup=False
)

# Tasks
run_staging = PythonOperator(
    task_id='run_staging',
    python_callable=run_dbt_models,
    dag=dag
)

run_intermediate = PythonOperator(
    task_id='run_intermediate',
    python_callable=lambda: dbt.main.handle_and_check([
        "run", "--select", "intermediate.*"
    ]),
    dag=dag
)

run_marts = PythonOperator(
    task_id='run_marts',
    python_callable=lambda: dbt.main.handle_and_check([
        "run", "--select", "marts.*"
    ]),
    dag=dag
)

run_tests = PythonOperator(
    task_id='run_tests',
    python_callable=run_dbt_tests,
    dag=dag
)

# Dependencies
run_staging >> run_intermediate >> run_marts >> run_tests
```

---

## Metadata Files

### manifest.json

Contains complete project metadata.

**Location**: `target/manifest.json`

```python
import json

def analyze_manifest():
    """Analyze dbt manifest"""
    with open("target/manifest.json") as f:
        manifest = json.load(f)
    
    # List all models
    models = {
        k: v for k, v in manifest["nodes"].items()
        if v["resource_type"] == "model"
    }
    
    print(f"Total models: {len(models)}")
    
    # List models by materialization
    materializations = {}
    for node_id, node in models.items():
        mat = node["config"]["materialized"]
        materializations[mat] = materializations.get(mat, 0) + 1
    
    print("\nBy materialization:")
    for mat, count in materializations.items():
        print(f"  {mat}: {count}")
    
    # List model dependencies
    print("\nModel dependencies:")
    for node_id, node in models.items():
        if node["depends_on"]["nodes"]:
            model_name = node["name"]
            deps = [manifest["nodes"][dep]["name"] 
                   for dep in node["depends_on"]["nodes"]
                   if dep in manifest["nodes"]]
            print(f"  {model_name} → {deps}")

analyze_manifest()
```

### run_results.json

Contains execution results from last run.

**Location**: `target/run_results.json`

```python
def analyze_run_results():
    """Analyze dbt run results"""
    with open("target/run_results.json") as f:
        results = json.load(f)
    
    # Overall statistics
    total = len(results["results"])
    success = sum(1 for r in results["results"] if r["status"] == "success")
    error = sum(1 for r in results["results"] if r["status"] == "error")
    skipped = sum(1 for r in results["results"] if r["status"] == "skipped")
    
    print(f"Total models run: {total}")
    print(f"Success: {success}")
    print(f"Error: {error}")
    print(f"Skipped: {skipped}")
    
    # Slowest models
    print("\nSlowest models:")
    sorted_results = sorted(
        results["results"],
        key=lambda x: x["execution_time"],
        reverse=True
    )[:10]
    
    for result in sorted_results:
        name = result["unique_id"].split(".")[-1]
        time = result["execution_time"]
        print(f"  {name}: {time:.2f}s")
    
    # Failed models
    failed = [r for r in results["results"] if r["status"] == "error"]
    if failed:
        print("\nFailed models:")
        for result in failed:
            name = result["unique_id"].split(".")[-1]
            message = result["message"]
            print(f"  {name}: {message}")

analyze_run_results()
```

### catalog.json

Contains database schema information.

**Location**: `target/catalog.json`

```python
def analyze_catalog():
    """Analyze dbt catalog"""
    with open("target/catalog.json") as f:
        catalog = json.load(f)
    
    # List all sources
    sources = catalog["sources"]
    print(f"Total sources: {len(sources)}")
    
    for source_id, source in sources.items():
        print(f"\n{source['metadata']['name']}:")
        print(f"  Rows: {source['stats']['row_count']['value']:,}")
        print(f"  Bytes: {source['stats']['bytes']['value']:,}")
        print(f"  Columns: {len(source['columns'])}")

analyze_catalog()
```

---

## dbt Cloud API

If using dbt Cloud (not applicable to local setup), API is available.

**Base URL**: `https://cloud.getdbt.com/api/v2`

### Authentication

```python
import requests

DBT_CLOUD_TOKEN = "your-api-token"
ACCOUNT_ID = "your-account-id"

headers = {
    "Authorization": f"Token {DBT_CLOUD_TOKEN}",
    "Content-Type": "application/json"
}
```

### Trigger Job

```python
def trigger_dbt_cloud_job(job_id: int):
    """Trigger dbt Cloud job"""
    url = f"https://cloud.getdbt.com/api/v2/accounts/{ACCOUNT_ID}/jobs/{job_id}/run/"
    
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code == 200:
        run = response.json()["data"]
        return run["id"]
    else:
        raise Exception(f"Failed to trigger job: {response.text}")

# Usage
run_id = trigger_dbt_cloud_job(job_id=12345)
print(f"Job run started: {run_id}")
```

---

## Custom Macros

### Create Custom Macro

**File**: `macros/custom_tests.sql`

```sql
{% macro test_valid_email(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} NOT LIKE '%@%.%'

{% endmacro %}
```

### Use in Tests

**File**: `models/staging/schema.yml`

```yaml
models:
  - name: stg_customers
    columns:
      - name: email
        tests:
          - valid_email
```

### Advanced Macro with Arguments

```sql
{% macro grant_select(schema, role) %}

{% set sql %}
  GRANT SELECT ON ALL TABLES IN SCHEMA {{ schema }} TO {{ role }}
{% endset %}

{% do run_query(sql) %}
{% do log("Granted SELECT on " ~ schema ~ " to " ~ role, info=True) %}

{% endmacro %}
```

### Call Macro

```bash
dbt run-operation grant_select --args '{schema: Production, role: analyst}'
```

---

## Summary

This API reference covered:

- **CLI Commands**: Complete reference for all dbt commands
- **Python API**: Programmatic execution with Python wrapper
- **Metadata Files**: manifest.json, run_results.json, catalog.json
- **dbt Cloud API**: Trigger jobs (if using dbt Cloud)
- **Custom Macros**: Creating and using custom functionality

**Key Takeaways**:
- Use CLI for development and interactive work
- Use Python API for automation and orchestration
- Parse metadata files for introspection
- Create custom macros for reusable logic
- Integrate with Airflow for production scheduling

**Related Documentation:**
- [dbt Development Guide](../guides/dbt-development.md)
- [Data Quality Guide](../guides/data-quality.md)
- [Architecture: Data Flow](../architecture/data-flow.md)

---

**Version**: 3.2.0  
**Last Updated**: October 16, 2025
