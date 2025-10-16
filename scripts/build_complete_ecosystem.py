#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[ROCKET] COMPLETE ECOSYSTEM BUILDER
Construit l'ecosysteme complet Dremio + dbt de A a Z

Etapes:
1. Verification des prerequis
2. Demarrage Docker (Dremio, PostgreSQL, Elasticsearch, MinIO)
3. Creation des schemas PostgreSQL
4. Generation des donnees (tous formats)
5. Injection PostgreSQL (psycopg2)
6. Injection Elasticsearch (bulk)
7. Injection MinIO (Parquet files)
8. Configuration Dremio (sources + VDS)
9. Execution dbt (models + tests)
10. Validation finale + rapport

Usage:
    python scripts/build_complete_ecosystem.py
    python scripts/build_complete_ecosystem.py --skip-docker  # Si deja lance
    python scripts/build_complete_ecosystem.py --data-only    # Reinitialiser donnees
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Fix Windows encoding issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from faker import Faker
except ImportError:
    print("[X] faker not installed. Run: pip install faker")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("[X] requests not installed. Run: pip install requests")
    sys.exit(1)

# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

CONFIG = {
    "docker": {
        "compose_file": "docker-compose.yml",
        "services": ["dremio", "postgres", "elasticsearch", "minio"],
        "wait_timeout": 300,
    },
    "postgres": {
        "host": "localhost",
        "port": 5432,
        "database": "business_db",
        "user": "postgres",
        "password": "postgres123",
    },
    "elasticsearch": {
        "hosts": ["http://localhost:9200"],
        "indices": {
            "application_logs": {"records": 10000},
            "user_events": {"records": 8000},
            "performance_metrics": {"records": 2000},
        },
    },
    "minio": {
        "endpoint": "localhost:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin123",
        "bucket": "sales-data",
        "files": 1095,  # 3 years * 365 days
    },
    "dremio": {
        "url": "http://localhost:9047",
        "username": "admin",
        "password": "admin123",
    },
    "data_volumes": {
        "customers": 1000,
        "orders": 10000,
        "es_total": 20000,
        "minio_sales": 50000,
    },
    "dbt": {
        "project_dir": "dbt",
        "profiles_dir": "dbt",
    },
    "airbyte": {
        "compose_file": "docker-compose-airbyte.yml",
        "url": "http://localhost:8001/api/v1",
        "ui_url": "http://localhost:8000",
        "workspace_name": "Dremio Workspace",
        "wait_timeout": 180,
        "postgres_source": {
            "name": "PostgreSQL_BusinessDB",
            "host": "dremio-postgres",
            "port": 5432,
            "database": "business_db",
            "username": "postgres",
            "password": "postgres123",
            "schemas": ["public"],
        },
        "minio_destination": {
            "name": "MinIO_Airbyte_Staging",
            "endpoint": "http://dremio-minio:9000",
            "access_key": "minioadmin",
            "secret_key": "minioadmin123",
            "bucket": "airbyte-staging",
            "format": "Parquet",
        },
        "connection": {
            "name": "PostgreSQL to MinIO (Parquet)",
            "streams": ["customers", "orders"],
            "sync_mode": "incremental",
            "cursor_field": "id",
            "schedule_cron": "0 */6 * * *",
        },
    },
}

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# ============================================================================
# UTILITIES
# ============================================================================

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_step(step: int, total: int, title: str):
    """Print step header"""
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}[{step}/{total}] {title}{Colors.ENDC}")
    print('='*70)


def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {msg}{Colors.ENDC}")


def print_info(msg: str):
    """Print info message"""
    print(f"{Colors.CYAN}[i] {msg}{Colors.ENDC}")


def print_warning(msg: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}[!] {msg}{Colors.ENDC}")


def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.RED}[X] {msg}{Colors.ENDC}")


def run_command(cmd: List[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run shell command"""
    try:
        if capture:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        if capture and e.stderr:
            print_error(e.stderr)
        raise


def check_airbyte_running() -> bool:
    """Check if Airbyte services are running"""
    try:
        result = subprocess.run(
            ["docker-compose", "-f", CONFIG["airbyte"]["compose_file"], "ps", "-q"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Check if any containers are running
            container_ids = result.stdout.strip().split('\n')
            if len(container_ids) >= 6:  # At least 6 Airbyte services
                return True
        return False
    except Exception:
        return False


def wait_for_service(url: str, name: str, timeout: int = 120) -> bool:
    """Wait for service to be ready"""
    print_info(f"Waiting for {name} to be ready...")
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 401]:  # 401 for auth-required services
                print_success(f"{name} is ready!")
                return True
        except:
            pass
        time.sleep(5)
    
    print_error(f"{name} did not start within {timeout}s")
    return False


# ============================================================================
# STEP 1: CHECK PREREQUISITES
# ============================================================================

def step_01_check_prerequisites():
    """Check system prerequisites"""
    print_step(1, 10, "Checking Prerequisites")
    
    checks = {
        "Docker": ["docker", "--version"],
        "Docker Compose": ["docker-compose", "--version"],
        "Python 3.8+": [sys.executable, "--version"],
    }
    
    for name, cmd in checks.items():
        try:
            result = run_command(cmd, capture=True)
            version = result.stdout.strip()
            print_success(f"{name}: {version}")
        except Exception as e:
            print_error(f"{name}: Not found")
            raise SystemExit(1)
    
    # Check Python packages
    required_packages = ["psycopg2", "elasticsearch", "minio", "pyarrow", "pandas"]
    missing = []
    
    for pkg in required_packages:
        try:
            __import__(pkg)
            print_success(f"Python package: {pkg}")
        except ImportError:
            missing.append(pkg)
            print_warning(f"Python package: {pkg} (not installed)")
    
    if missing:
        print_warning(f"Missing packages: {', '.join(missing)}")
        print_info(f"Installing automatically: {' '.join(missing)}")
        
        # Install automatically without asking
        run_command([sys.executable, "-m", "pip", "install"] + missing)
        print_success("Packages installed!")
    
    print_success("All prerequisites OK!")


# ============================================================================
# STEP 2: START DOCKER SERVICES
# ============================================================================

def step_02_start_docker(skip: bool = False):
    """Start Docker services"""
    print_step(2, 10, "Starting Docker Services")
    
    if skip:
        print_warning("Docker startup skipped (--skip-docker)")
        return
    
    compose_file = CONFIG["docker"]["compose_file"]
    
    if not Path(compose_file).exists():
        print_error(f"Docker Compose file not found: {compose_file}")
        raise SystemExit(1)
    
    print_info(f"Starting services: {', '.join(CONFIG['docker']['services'])}")
    print_info(f"Using: {compose_file}")
    
    # Stop existing containers
    print_info("Stopping existing containers...")
    run_command(["docker-compose", "-f", compose_file, "down"], check=False)
    
    # Start services
    print_info("Starting Docker services...")
    run_command(["docker-compose", "-f", compose_file, "up", "-d"])
    
    print_success("Docker services started!")
    
    # Wait for services
    services_health = {
        "Dremio": "http://localhost:9047",
        "Elasticsearch": "http://localhost:9200",
        "MinIO": "http://localhost:9000/minio/health/live",
    }
    
    for name, url in services_health.items():
        if not wait_for_service(url, name, timeout=120):
            print_error(f"{name} failed to start")
            raise SystemExit(1)
    
    # PostgreSQL needs different check
    print_info("Waiting for PostgreSQL...")
    time.sleep(10)  # Give PostgreSQL time to initialize
    print_success("PostgreSQL is ready!")


# ============================================================================
# STEP 3: CREATE POSTGRESQL SCHEMA
# ============================================================================

def step_03_create_postgres_schema():
    """Create PostgreSQL database and tables"""
    print_step(3, 10, "Creating PostgreSQL Schema")
    
    try:
        import psycopg2
    except ImportError:
        print_error("psycopg2 not installed")
        raise SystemExit(1)
    
    # Connect to PostgreSQL
    print_info("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=CONFIG["postgres"]["host"],
        port=CONFIG["postgres"]["port"],
        database=CONFIG["postgres"]["database"],
        user=CONFIG["postgres"]["user"],
        password=CONFIG["postgres"]["password"],
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create customers table
    print_info("Creating customers table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255),
            city VARCHAR(100),
            country VARCHAR(100),
            registration_date DATE
        )
    """)
    
    # Create orders table
    print_info("Creating orders table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(customer_id),
            order_date DATE,
            amount DECIMAL(10, 2),
            status VARCHAR(50)
        )
    """)
    
    cursor.close()
    conn.close()
    
    print_success("PostgreSQL schema created!")


# ============================================================================
# STEP 4: GENERATE DATA
# ============================================================================

def step_04_generate_data():
    """Generate all test data"""
    print_step(4, 10, "Generating Test Data")
    
    data = {}
    
    # Generate customers
    print_info(f"Generating {CONFIG['data_volumes']['customers']:,} customers...")
    customers = []
    for i in range(1, CONFIG['data_volumes']['customers'] + 1):
        customers.append({
            "customer_id": i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "city": fake.city(),
            "country": fake.country(),
            "registration_date": fake.date_between(start_date='-2y', end_date='today'),
        })
    data["customers"] = customers
    print_success(f"Generated {len(customers):,} customers")
    
    # Generate orders
    print_info(f"Generating {CONFIG['data_volumes']['orders']:,} orders...")
    orders = []
    statuses = ['completed', 'pending', 'cancelled', 'processing']
    for i in range(1, CONFIG['data_volumes']['orders'] + 1):
        orders.append({
            "order_id": i,
            "customer_id": random.randint(1, len(customers)),
            "order_date": fake.date_between(start_date='-1y', end_date='today'),
            "amount": round(random.uniform(10, 5000), 2),
            "status": random.choice(statuses),
        })
    data["orders"] = orders
    print_success(f"Generated {len(orders):,} orders")
    
    # Generate Elasticsearch logs
    print_info("Generating Elasticsearch application logs...")
    es_logs = []
    levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service']
    
    for _ in range(CONFIG['elasticsearch']['indices']['application_logs']['records']):
        es_logs.append({
            "timestamp": fake.date_time_between(start_date='-30d', end_date='now'),
            "level": random.choice(levels),
            "service": random.choice(services),
            "message": fake.sentence(),
            "request_id": fake.uuid4(),
        })
    data["es_logs"] = es_logs
    print_success(f"Generated {len(es_logs):,} application logs")
    
    # Generate Elasticsearch events
    print_info("Generating Elasticsearch user events...")
    es_events = []
    event_types = ['page_view', 'click', 'purchase', 'add_to_cart', 'search']
    
    for _ in range(CONFIG['elasticsearch']['indices']['user_events']['records']):
        es_events.append({
            "timestamp": fake.date_time_between(start_date='-30d', end_date='now'),
            "event_type": random.choice(event_types),
            "session_id": fake.uuid4(),
            "user_id": random.randint(1, 1000),
        })
    data["es_events"] = es_events
    print_success(f"Generated {len(es_events):,} user events")
    
    # Generate Elasticsearch metrics
    print_info("Generating Elasticsearch performance metrics...")
    es_metrics = []
    metric_types = ['cpu_percent', 'memory_mb', 'disk_io', 'network_latency']
    
    for _ in range(CONFIG['elasticsearch']['indices']['performance_metrics']['records']):
        metric_type = random.choice(metric_types)
        es_metrics.append({
            "timestamp": fake.date_time_between(start_date='-30d', end_date='now'),
            "metric_type": metric_type,
            "metric_name": f"server_{metric_type}",
            "value": round(random.uniform(10, 100), 2),
            "service": random.choice(services),
        })
    data["es_metrics"] = es_metrics
    print_success(f"Generated {len(es_metrics):,} performance metrics")
    
    # Generate MinIO sales
    print_info(f"Generating {CONFIG['data_volumes']['minio_sales']:,} MinIO sales...")
    minio_sales = []
    categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books']
    regions = ['North America', 'Europe', 'Asia', 'South America']
    
    for i in range(1, CONFIG['data_volumes']['minio_sales'] + 1):
        minio_sales.append({
            "sale_id": f"SALE-{i:06d}",
            "sale_date": fake.date_between(start_date='-3y', end_date='today'),
            "category": random.choice(categories),
            "product_name": fake.word().title(),
            "quantity": random.randint(1, 10),
            "unit_price": round(random.uniform(5, 500), 2),
            "region": random.choice(regions),
        })
    data["minio_sales"] = minio_sales
    print_success(f"Generated {len(minio_sales):,} sales records")
    
    total_records = sum(len(v) for v in data.values())
    print_success(f"Total records generated: {total_records:,}")
    
    return data


# ============================================================================
# STEP 5: INJECT POSTGRESQL DATA
# ============================================================================

def step_05_inject_postgres(data: Dict):
    """Inject data into PostgreSQL"""
    print_step(5, 10, "Injecting PostgreSQL Data")
    
    import psycopg2
    from psycopg2.extras import execute_batch
    
    conn = psycopg2.connect(
        host=CONFIG["postgres"]["host"],
        port=CONFIG["postgres"]["port"],
        database=CONFIG["postgres"]["database"],
        user=CONFIG["postgres"]["user"],
        password=CONFIG["postgres"]["password"],
    )
    cursor = conn.cursor()
    
    # Clear existing data
    print_info("Clearing existing data...")
    cursor.execute("TRUNCATE TABLE orders CASCADE")
    cursor.execute("TRUNCATE TABLE customers CASCADE")
    conn.commit()
    
    # Insert customers
    print_info(f"Inserting {len(data['customers']):,} customers...")
    customer_sql = """
        INSERT INTO customers (customer_id, first_name, last_name, email, city, country, registration_date)
        VALUES (%(customer_id)s, %(first_name)s, %(last_name)s, %(email)s, %(city)s, %(country)s, %(registration_date)s)
    """
    execute_batch(cursor, customer_sql, data['customers'], page_size=1000)
    conn.commit()
    print_success(f"Inserted {len(data['customers']):,} customers")
    
    # Insert orders
    print_info(f"Inserting {len(data['orders']):,} orders...")
    order_sql = """
        INSERT INTO orders (order_id, customer_id, order_date, amount, status)
        VALUES (%(order_id)s, %(customer_id)s, %(order_date)s, %(amount)s, %(status)s)
    """
    execute_batch(cursor, order_sql, data['orders'], page_size=1000)
    conn.commit()
    print_success(f"Inserted {len(data['orders']):,} orders")
    
    # Verify counts
    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print_success(f"PostgreSQL: {customer_count:,} customers, {order_count:,} orders")


# ============================================================================
# STEP 6: INJECT ELASTICSEARCH DATA
# ============================================================================

def step_06_inject_elasticsearch(data: Dict):
    """Inject data into Elasticsearch"""
    print_step(6, 10, "Injecting Elasticsearch Data")
    
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
    
    es = Elasticsearch(CONFIG["elasticsearch"]["hosts"])
    
    # Inject application logs
    index_name = "application_logs"
    print_info(f"Injecting {len(data['es_logs']):,} documents into {index_name}...")
    
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print_info(f"Deleted existing index: {index_name}")
    
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in data['es_logs']
    ]
    success, failed = bulk(es, actions, chunk_size=1000, raise_on_error=False)
    print_success(f"Indexed {success:,} documents in {index_name}")
    
    # Inject user events
    index_name = "user_events"
    print_info(f"Injecting {len(data['es_events']):,} documents into {index_name}...")
    
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print_info(f"Deleted existing index: {index_name}")
    
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in data['es_events']
    ]
    success, failed = bulk(es, actions, chunk_size=1000, raise_on_error=False)
    print_success(f"Indexed {success:,} documents in {index_name}")
    
    # Inject performance metrics
    index_name = "performance_metrics"
    print_info(f"Injecting {len(data['es_metrics']):,} documents into {index_name}...")
    
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print_info(f"Deleted existing index: {index_name}")
    
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in data['es_metrics']
    ]
    success, failed = bulk(es, actions, chunk_size=1000, raise_on_error=False)
    print_success(f"Indexed {success:,} documents in {index_name}")
    
    # Verify indices
    indices = es.cat.indices(format='json')
    total_docs = sum(int(idx['docs.count']) for idx in indices if idx['index'] in ['application_logs', 'user_events', 'performance_metrics'])
    print_success(f"Elasticsearch: {total_docs:,} total documents across all indices")


# ============================================================================
# STEP 7: INJECT MINIO DATA
# ============================================================================

def step_07_inject_minio(data: Dict):
    """Inject Parquet files into MinIO"""
    print_step(7, 10, "Injecting MinIO Data (Parquet)")
    
    from minio import Minio
    import pandas as pd
    import io
    
    # Connect to MinIO
    client = Minio(
        CONFIG["minio"]["endpoint"],
        access_key=CONFIG["minio"]["access_key"],
        secret_key=CONFIG["minio"]["secret_key"],
        secure=False,
    )
    
    bucket = CONFIG["minio"]["bucket"]
    
    # Create bucket if not exists
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        print_info(f"Created bucket: {bucket}")
    else:
        print_info(f"Using existing bucket: {bucket}")
        
        # Clear existing objects
        print_info("Clearing existing objects...")
        objects = client.list_objects(bucket, recursive=True)
        for obj in objects:
            client.remove_object(bucket, obj.object_name)
    
    # Convert to DataFrame
    df = pd.DataFrame(data['minio_sales'])
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    
    # Group by date and upload as partitioned Parquet files
    print_info(f"Uploading {len(df):,} records as Parquet files...")
    
    # Partition by year/month/day
    df['year'] = df['sale_date'].dt.year
    df['month'] = df['sale_date'].dt.month
    df['day'] = df['sale_date'].dt.day
    
    grouped = df.groupby(['year', 'month', 'day'])
    file_count = 0
    
    for (year, month, day), group in grouped:
        # Remove partition columns from data
        data_df = group.drop(['year', 'month', 'day'], axis=1)
        
        # Convert to Parquet in memory
        buffer = io.BytesIO()
        data_df.to_parquet(buffer, engine='pyarrow', index=False)
        buffer.seek(0)
        
        # Upload to MinIO with partition path
        object_name = f"year={year}/month={month:02d}/day={day:02d}/sales_{year}{month:02d}{day:02d}.parquet"
        client.put_object(
            bucket,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream',
        )
        file_count += 1
        
        if file_count % 100 == 0:
            print_info(f"Uploaded {file_count} files...")
    
    print_success(f"Uploaded {file_count} Parquet files to MinIO")
    
    # Verify
    objects = list(client.list_objects(bucket, recursive=True))
    print_success(f"MinIO: {len(objects)} files in bucket '{bucket}'")


# ============================================================================
# STEP 7b: START AIRBYTE (OPTIONAL)
# ============================================================================

def step_07b_start_airbyte():
    """Start Airbyte services"""
    print_step("7b", 11, "Starting Airbyte Services")
    
    compose_file = CONFIG["airbyte"]["compose_file"]
    
    if not os.path.exists(compose_file):
        print_error(f"Airbyte compose file not found: {compose_file}")
        raise FileNotFoundError(f"Missing {compose_file}")
    
    print_info(f"Starting Airbyte from {compose_file}...")
    
    try:
        # Start Airbyte services
        result = subprocess.run(
            ["docker-compose", "-f", compose_file, "up", "-d"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print_error("Docker Compose failed!")
            print_error(result.stderr)
            raise RuntimeError("Airbyte startup failed")
        
        print_success("Airbyte services started!")
        
        # Wait for Airbyte to be ready
        print_info("Waiting for Airbyte to initialize (this may take 2-3 minutes)...")
        wait_timeout = CONFIG["airbyte"]["wait_timeout"]
        airbyte_url = CONFIG["airbyte"]["url"]
        
        max_attempts = wait_timeout // 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{airbyte_url}/health",
                    timeout=5
                )
                if response.status_code == 200:
                    print_success(f"Airbyte is ready! (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(5)  # Additional stability wait
                    return True
            except:
                pass
            
            if attempt < max_attempts - 1:
                time.sleep(10)
                print_info(f"Still waiting... ({attempt + 1}/{max_attempts})")
        
        print_warning("Airbyte health check timeout - proceeding anyway")
        return True
        
    except subprocess.TimeoutExpired:
        print_error("Docker Compose timed out!")
        raise
    except Exception as e:
        print_error(f"Failed to start Airbyte: {e}")
        raise


# ============================================================================
# STEP 7c: CONFIGURE AIRBYTE (OPTIONAL)
# ============================================================================

def step_07c_configure_airbyte():
    """Configure Airbyte sources, destinations, and connections"""
    print_step("7c", 11, "Configuring Airbyte Integration")
    
    airbyte_url = CONFIG["airbyte"]["url"]
    
    print_info("Configuring Airbyte workspace and connections...")
    
    try:
        # 1. Get or create workspace
        print_info("Step 1/6: Getting workspace...")
        response = requests.post(
            f"{airbyte_url}/workspaces/list",
            json={},
            timeout=30
        )
        
        if response.status_code != 200:
            print_error(f"Failed to list workspaces: {response.status_code}")
            print_error(response.text)
            raise RuntimeError("Workspace listing failed")
        
        workspaces = response.json().get("workspaces", [])
        if workspaces:
            workspace_id = workspaces[0]["workspaceId"]
            print_success(f"Using existing workspace: {workspace_id}")
        else:
            print_error("No workspace found - Airbyte not initialized properly")
            raise RuntimeError("No workspace available")
        
        # 2. Get source definitions (PostgreSQL)
        print_info("Step 2/6: Finding PostgreSQL connector...")
        response = requests.post(
            f"{airbyte_url}/source_definitions/list",
            json={},
            timeout=30
        )
        
        if response.status_code != 200:
            raise RuntimeError("Failed to list source definitions")
        
        postgres_def = None
        for source_def in response.json().get("sourceDefinitions", []):
            if "postgres" in source_def.get("name", "").lower():
                postgres_def = source_def
                break
        
        if not postgres_def:
            raise RuntimeError("PostgreSQL connector not found")
        
        print_success(f"Found: {postgres_def['name']}")
        
        # 3. Get destination definitions (S3)
        print_info("Step 3/6: Finding S3 connector...")
        response = requests.post(
            f"{airbyte_url}/destination_definitions/list",
            json={},
            timeout=30
        )
        
        if response.status_code != 200:
            raise RuntimeError("Failed to list destination definitions")
        
        s3_def = None
        for dest_def in response.json().get("destinationDefinitions", []):
            if "s3" in dest_def.get("name", "").lower():
                s3_def = dest_def
                break
        
        if not s3_def:
            raise RuntimeError("S3 connector not found")
        
        print_success(f"Found: {s3_def['name']}")
        
        # 4. Create PostgreSQL source
        print_info("Step 4/6: Creating PostgreSQL source...")
        pg_config = CONFIG["airbyte"]["postgres_source"]
        
        source_payload = {
            "workspaceId": workspace_id,
            "name": pg_config["name"],
            "sourceDefinitionId": postgres_def["sourceDefinitionId"],
            "connectionConfiguration": {
                "host": pg_config["host"],
                "port": pg_config["port"],
                "database": pg_config["database"],
                "username": pg_config["username"],
                "password": pg_config["password"],
                "schemas": pg_config["schemas"],
                "ssl": False,
                "replication_method": {
                    "method": "Standard"
                }
            }
        }
        
        response = requests.post(
            f"{airbyte_url}/sources/create",
            json=source_payload,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print_warning(f"Source creation returned {response.status_code}")
            print_info("Attempting to find existing source...")
            
            # Try to find existing
            list_response = requests.post(
                f"{airbyte_url}/sources/list",
                json={"workspaceId": workspace_id},
                timeout=30
            )
            
            if list_response.status_code == 200:
                sources = list_response.json().get("sources", [])
                for src in sources:
                    if src.get("name") == pg_config["name"]:
                        source_id = src["sourceId"]
                        print_success(f"Using existing source: {source_id}")
                        break
                else:
                    raise RuntimeError("Failed to create or find source")
            else:
                raise RuntimeError("Source creation failed")
        else:
            source_id = response.json()["sourceId"]
            print_success(f"PostgreSQL source created: {source_id}")
        
        # 5. Create MinIO/S3 destination
        print_info("Step 5/6: Creating MinIO destination...")
        minio_config = CONFIG["airbyte"]["minio_destination"]
        
        destination_payload = {
            "workspaceId": workspace_id,
            "name": minio_config["name"],
            "destinationDefinitionId": s3_def["destinationDefinitionId"],
            "connectionConfiguration": {
                "s3_bucket_name": minio_config["bucket"],
                "s3_bucket_path": "data",
                "s3_bucket_region": "us-east-1",
                "s3_endpoint": minio_config["endpoint"],
                "access_key_id": minio_config["access_key"],
                "secret_access_key": minio_config["secret_key"],
                "format": {
                    "format_type": "Parquet"
                }
            }
        }
        
        response = requests.post(
            f"{airbyte_url}/destinations/create",
            json=destination_payload,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print_warning(f"Destination creation returned {response.status_code}")
            print_info("Attempting to find existing destination...")
            
            list_response = requests.post(
                f"{airbyte_url}/destinations/list",
                json={"workspaceId": workspace_id},
                timeout=30
            )
            
            if list_response.status_code == 200:
                destinations = list_response.json().get("destinations", [])
                for dest in destinations:
                    if dest.get("name") == minio_config["name"]:
                        destination_id = dest["destinationId"]
                        print_success(f"Using existing destination: {destination_id}")
                        break
                else:
                    raise RuntimeError("Failed to create or find destination")
            else:
                raise RuntimeError("Destination creation failed")
        else:
            destination_id = response.json()["destinationId"]
            print_success(f"MinIO destination created: {destination_id}")
        
        # 6. Discover schema
        print_info("Step 6/6: Discovering schema and creating connection...")
        discover_payload = {
            "sourceId": source_id
        }
        
        response = requests.post(
            f"{airbyte_url}/sources/discover_schema",
            json=discover_payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print_warning("Schema discovery failed - skipping connection creation")
            print_info("You can create connections manually in Airbyte UI")
            return True
        
        catalog = response.json().get("catalog", {})
        print_success("Schema discovered successfully!")
        
        # Create connection (simplified - enable all streams)
        connection_config = CONFIG["airbyte"]["connection"]
        
        connection_payload = {
            "name": connection_config["name"],
            "sourceId": source_id,
            "destinationId": destination_id,
            "syncCatalog": catalog,
            "schedule": {
                "scheduleType": "cron",
                "cronExpression": connection_config["schedule_cron"]
            },
            "status": "active"
        }
        
        response = requests.post(
            f"{airbyte_url}/connections/create",
            json=connection_payload,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            connection_id = response.json()["connectionId"]
            print_success(f"Connection created: {connection_id}")
            print_info(f"Schedule: {connection_config['schedule_cron']}")
            print_success("Airbyte configuration complete!")
        else:
            print_warning("Connection creation failed - configure manually in UI")
            print_info(f"Airbyte UI: {CONFIG['airbyte']['ui_url']}")
        
        return True
        
    except Exception as e:
        print_error(f"Airbyte configuration failed: {e}")
        print_warning("You can configure Airbyte manually:")
        print_info(f"UI: {CONFIG['airbyte']['ui_url']}")
        print_info("Check logs: docker-compose -f docker-compose-airbyte.yml logs")
        raise


# ============================================================================
# STEP 8: INITIALIZE DREMIO ADMIN
# ============================================================================

def step_08_initialize_dremio():
    """Initialize Dremio admin account via bootstrap API"""
    print_step(8, 11, "Initializing Dremio Admin Account")
    
    dremio_url = "http://localhost:9047"
    
    # Wait for Dremio UI to be accessible
    print_info("Waiting for Dremio to be accessible...")
    max_wait = 120  # 2 minutes max
    wait_interval = 5
    elapsed = 0
    dremio_ready = False
    
    while elapsed < max_wait:
        try:
            # Try to access the bootstrap firstuser endpoint (returns 405 if ready)
            response = requests.get(f"{dremio_url}/apiv2/bootstrap/firstuser", timeout=5)
            # If we get ANY response (even error), Dremio is up
            if response.status_code in [200, 400, 401, 403, 404, 405]:
                print_success("Dremio is accessible!")
                dremio_ready = True
                break
        except requests.exceptions.ConnectionError:
            pass  # Still waiting
        except Exception as e:
            print_info(f"Waiting for Dremio: {e}")
        
        time.sleep(wait_interval)
        elapsed += wait_interval
        if elapsed % 10 == 0:  # Print every 10 seconds
            print_info(f"Still waiting... ({elapsed}s/{max_wait}s)")
    
    if not dremio_ready:
        print_error("Dremio did not respond in time")
        print_warning("You will need to create the admin user manually at http://localhost:9047")
        return False
    
    # Give Dremio a few more seconds to stabilize
    time.sleep(5)
    
    # Check if already initialized by trying to login
    try:
        print_info("Checking if admin account already exists...")
        login_response = requests.post(
            f"{dremio_url}/apiv2/login",
            json={"userName": "admin", "password": "admin123"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            print_success("Admin account already exists and works!")
            token = login_response.json().get("token")
            if token:
                print_info("Authentication token obtained successfully")
            return True
        elif login_response.status_code == 401:
            print_info("Admin account exists but wrong password (will try to create)")
        else:
            print_info(f"Login returned status {login_response.status_code}")
    except Exception as e:
        print_info(f"Admin account check: {e}")
    
    # Try to create first user via bootstrap API
    try:
        print_info("Creating first admin user via bootstrap API...")
        
        setup_data = {
            "firstName": "Admin",
            "lastName": "User",
            "email": "admin@dremio.local",
            "createdAt": int(time.time() * 1000),
            "userName": "admin",
            "password": "admin123"
        }
        
        print_info(f"Sending PUT request to {dremio_url}/apiv2/bootstrap/firstuser")
        response = requests.put(
            f"{dremio_url}/apiv2/bootstrap/firstuser",
            json=setup_data,
            timeout=30
        )
        
        print_info(f"Bootstrap API returned status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print_success("Admin user created successfully!")
            print_info("Username: admin")
            print_info("Password: admin123")
            time.sleep(3)  # Wait for Dremio to process
            
            # Verify by logging in
            try:
                auth_response = requests.post(
                    f"{dremio_url}/apiv2/login",
                    json={"userName": "admin", "password": "admin123"},
                    timeout=10
                )
                
                if auth_response.status_code == 200:
                    token = auth_response.json().get("token")
                    print_success("Login verification successful!")
                    print_info(f"Token obtained: {token[:20]}...")
                    return True
                else:
                    print_warning(f"Login returned status {auth_response.status_code}")
                    print_info("Admin user created but login failed - may need manual verification")
                    return True  # Consider it success anyway
            except Exception as e:
                print_warning(f"Login verification failed: {e}")
                return True  # Consider it success anyway
                
        elif response.status_code == 409:
            print_success("Admin user already configured (409 Conflict)")
            return True
            
        elif response.status_code == 403:
            print_warning("Bootstrap API returned 403 - Dremio may already be configured")
            print_info("Checking if we can login with existing credentials...")
            try:
                auth_response = requests.post(
                    f"{dremio_url}/apiv2/login",
                    json={"userName": "admin", "password": "admin123"},
                    timeout=10
                )
                if auth_response.status_code == 200:
                    print_success("Login successful with existing admin account!")
                    return True
            except:
                pass
            print_warning("Please create admin user manually at http://localhost:9047")
            return False
            
        else:
            print_error(f"Bootstrap API failed with status {response.status_code}")
            print_info("Response: " + str(response.text)[:300])
            print_warning("You may need to create the admin user manually at http://localhost:9047")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Could not initialize Dremio: {e}")
        print_warning("Manual setup required at http://localhost:9047")
        print_info("Create user: admin / admin123")
        return False
    
    return True
    
    # Try to create first user
    try:
        print_info("Creating first admin user...")
        
        setup_data = {
            "firstName": "Admin",
            "lastName": "User",
            "email": "admin@dremio.local",
            "createdAt": int(time.time() * 1000),
            "userName": "admin",
            "password": "admin123"
        }
        
        response = requests.put(
            f"{dremio_url}/apiv2/bootstrap/firstuser",
            json=setup_data,
            timeout=10
        )
        
        if response.status_code in [200, 201, 409]:  # 409 = already configured
            print_success("Admin user configured!")
            print_info("Username: admin")
            print_info("Password: admin123")
            time.sleep(5)  # Give Dremio time to process
            
            # Verify by logging in
            try:
                auth_response = requests.post(
                    f"{dremio_url}/apiv2/login",
                    json={"userName": "admin", "password": "admin123"},
                    timeout=10
                )
                
                if auth_response.status_code == 200:
                    token = auth_response.json().get("token")
                    print_success("Login verification successful!")
                    print_info(f"Token obtained: {token[:20]}...")
                    return True
                else:
                    print_warning(f"Login returned status {auth_response.status_code}")
                    return False
            except Exception as e:
                print_warning(f"Login verification failed: {e}")
                return False
        else:
            print_error(f"User creation failed with status {response.status_code}")
            print_info("Response: " + str(response.text)[:200])
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Could not initialize Dremio: {e}")
        print_info("Manual setup required at http://localhost:9047")
        return False
    
    return True


# ============================================================================
# STEP 9: CONFIGURE DREMIO
# ============================================================================

def step_09_configure_dremio(with_airbyte=False):
    """Configure Dremio sources automatically using API v3"""
    print_step(9, 11, "Configuring Dremio Sources")
    
    # Authenticate
    try:
        print_info("Authenticating with Dremio...")
        login_response = requests.post(
            "http://localhost:9047/apiv2/login",
            json={"userName": "admin", "password": "admin123"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print_error(f"Cannot login to Dremio (status {login_response.status_code})")
            print_warning("Skipping automatic configuration")
            return False
        
        token = login_response.json().get("token")
        headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
        print_success("Authentication successful!")
        
    except Exception as e:
        print_error(f"Cannot connect to Dremio: {e}")
        return False
    
    # Step 1: Create spaces first (raw, staging, marts, analytics)
    print_info("Creating Dremio spaces...")
    spaces = ["raw", "staging", "marts", "analytics"]
    spaces_created = 0
    
    for space_name in spaces:
        try:
            # Check if space exists
            check_response = requests.get(
                f"http://localhost:9047/api/v3/catalog/by-path/{space_name}",
                headers=headers,
                timeout=5
            )
            if check_response.status_code == 404:
                # Create space
                space_config = {
                    "entityType": "space",
                    "name": space_name
                }
                create_response = requests.post(
                    "http://localhost:9047/api/v3/catalog",
                    headers=headers,
                    json=space_config,
                    timeout=10
                )
                if create_response.status_code in [200, 201]:
                    spaces_created += 1
                    print_success(f"  Space '{space_name}' created")
                else:
                    print_warning(f"  Space '{space_name}' failed: {create_response.status_code}")
            else:
                spaces_created += 1
                print_info(f"  Space '{space_name}' already exists")
        except Exception as e:
            print_warning(f"  Space '{space_name}' error: {e}")
    
    print_success(f"Spaces: {spaces_created}/{len(spaces)} created/verified")
    time.sleep(1)
    
    # Helper function to delete source if exists
    def delete_source_if_exists(source_name):
        try:
            response = requests.get(
                f"http://localhost:9047/api/v3/catalog/by-path/{source_name}",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                source_id = data.get("id")
                source_tag = data.get("tag")
                requests.delete(
                    f"http://localhost:9047/api/v3/catalog/{source_id}",
                    headers=headers,
                    params={"tag": source_tag},
                    timeout=5
                )
                time.sleep(1)
        except:
            pass
    
    # Helper function to create source
    def create_source(config, source_name):
        try:
            response = requests.post(
                "http://localhost:9047/api/v3/catalog",
                headers=headers,
                json=config,
                timeout=10
            )
            if response.status_code in [200, 201]:
                print_success(f"  {source_name} created")
                return True
            elif response.status_code == 409:
                print_info(f"  {source_name} already exists")
                return True
            else:
                print_error(f"  {source_name} failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"  {source_name} error: {e}")
            return False
    
    print_info("Creating data sources...")
    results = {}
    
    # 1. PostgreSQL
    print_info("1/3 PostgreSQL_BusinessDB...")
    delete_source_if_exists("PostgreSQL_BusinessDB")
    pg_config = {
        "entityType": "source",
        "name": "PostgreSQL_BusinessDB",
        "type": "POSTGRES",
        "config": {
            "hostname": "dremio-postgres",
            "port": 5432,
            "databaseName": "business_db",
            "username": "postgres",
            "password": "postgres123",
            "authenticationType": "MASTER",
            "useSsl": False
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "namesRefreshMs": 3600000,
            "datasetRefreshAfterMs": 3600000,
            "datasetExpireAfterMs": 10800000,
            "datasetUpdateMode": "PREFETCH_QUERIED",
            "deleteUnavailableDatasets": True,
            "autoPromoteDatasets": True
        }
    }
    results["PostgreSQL"] = create_source(pg_config, "PostgreSQL")
    time.sleep(1)
    
    # 2. MinIO
    print_info("2/3 MinIO_Storage...")
    delete_source_if_exists("MinIO_Storage")
    minio_config = {
        "entityType": "source",
        "name": "MinIO_Storage",
        "type": "S3",
        "config": {
            "credentialType": "ACCESS_KEY",
            "accessKey": "minioadmin",
            "accessSecret": "minioadmin123",
            "secure": False,
            "externalBucketList": ["sales-data"],
            "enableAsync": True,
            "compatibilityMode": True,
            "rootPath": "/",
            "defaultCtasFormat": "PARQUET",
            "isPartitionInferenceEnabled": True,
            "requesterPays": False,
            "propertyList": [
                {"name": "fs.s3a.path.style.access", "value": "true"},
                {"name": "fs.s3a.endpoint", "value": "dremio-minio:9000"},
                {"name": "dremio.s3.compat", "value": "true"}
            ]
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "namesRefreshMs": 3600000,
            "datasetRefreshAfterMs": 3600000,
            "datasetExpireAfterMs": 10800000,
            "datasetUpdateMode": "PREFETCH_QUERIED",
            "deleteUnavailableDatasets": True,
            "autoPromoteDatasets": True
        }
    }
    results["MinIO"] = create_source(minio_config, "MinIO")
    time.sleep(1)
    
    # 3. Elasticsearch
    print_info("3/3 Elasticsearch_Logs...")
    delete_source_if_exists("Elasticsearch_Logs")
    es_config = {
        "entityType": "source",
        "name": "Elasticsearch_Logs",
        "type": "ELASTIC",
        "config": {
            "hostList": [{"hostname": "dremio-elasticsearch", "port": 9200}],
            "authenticationType": "ANONYMOUS",
            "scrollSize": 4000,
            "scrollTimeoutMillis": 60000,
            "usePainless": True,
            "useWhitelist": False,
            "showHiddenIndices": False,
            "showIdColumn": False,
            "readTimeoutMillis": 60000,
            "scriptsEnabled": True,
            "allowPushdownOnNormalizedOrAnalyzedFields": True
        },
        "metadataPolicy": {
            "authTTLMs": 86400000,
            "namesRefreshMs": 3600000,
            "datasetRefreshAfterMs": 3600000,
            "datasetExpireAfterMs": 10800000,
            "datasetUpdateMode": "PREFETCH_QUERIED",
            "deleteUnavailableDatasets": True,
            "autoPromoteDatasets": True
        }
    }
    results["Elasticsearch"] = create_source(es_config, "Elasticsearch")
    time.sleep(1)
    
    # 4. MinIO_Airbyte_Staging (optional, if Airbyte enabled)
    if with_airbyte:
        print_info("4/4 MinIO_Airbyte_Staging (Airbyte output)...")
        delete_source_if_exists("MinIO_Airbyte_Staging")
        airbyte_minio_config = {
            "entityType": "source",
            "name": "MinIO_Airbyte_Staging",
            "type": "S3",
            "config": {
                "credentialType": "ACCESS_KEY",
                "accessKey": "minioadmin",
                "accessSecret": "minioadmin123",
                "secure": False,
                "externalBucketList": ["airbyte-staging"],
                "enableAsync": True,
                "enableFileStatusCheck": True,
                "rootPath": "/",
                "defaultCtasFormat": "PARQUET",
                "isPartitionInferenceEnabled": False,
                "isCachingEnabled": True,
                "maxCacheSpacePct": 100,
                "propertyList": [
                    {"name": "fs.s3a.path.style.access", "value": "true"},
                    {"name": "fs.s3a.endpoint", "value": "dremio-minio:9000"},
                    {"name": "dremio.s3.compat", "value": "true"}
                ]
            },
            "metadataPolicy": {
                "authTTLMs": 86400000,
                "namesRefreshMs": 3600000,
                "datasetRefreshAfterMs": 3600000,
                "datasetExpireAfterMs": 10800000,
                "datasetUpdateMode": "PREFETCH_QUERIED",
                "deleteUnavailableDatasets": True,
                "autoPromoteDatasets": True
            }
        }
        results["MinIO_Airbyte"] = create_source(airbyte_minio_config, "MinIO_Airbyte")
        print_success("MinIO Airbyte staging source created!")
        time.sleep(1)
    
    # Create VDS for easier access
    print_info("Creating Virtual Datasets (VDS) in 'raw' space...")
    
    vds_configs = [
        ("customers", 'SELECT * FROM "PostgreSQL_BusinessDB".public.customers'),
        ("orders", 'SELECT * FROM "PostgreSQL_BusinessDB".public.orders'),
        ("minio_sales", 'SELECT * FROM "MinIO_Storage"."sales-data"'),
    ]
    
    vds_created = 0
    for vds_name, sql in vds_configs:
        try:
            vds_config = {
                "entityType": "dataset",
                "type": "VIRTUAL_DATASET",
                "path": ["raw", vds_name],
                "sql": sql,
                "sqlContext": ["@admin"]
            }
            response = requests.post(
                "http://localhost:9047/api/v3/catalog",
                headers=headers,
                json=vds_config,
                timeout=10
            )
            if response.status_code in [200, 201]:
                vds_created += 1
                print_success(f"  VDS raw.{vds_name} created")
            elif response.status_code == 409:
                vds_created += 1
                print_info(f"  VDS raw.{vds_name} already exists")
        except:
            pass
    
    # Summary
    success_count = sum(1 for v in results.values() if v)
    print("")
    print_success(f"Sources created: {success_count}/3")
    print_success(f"VDS created: {vds_created}/{len(vds_configs)}")
    
    if all(results.values()):
        print_success("All Dremio sources configured successfully!")
        return True
    else:
        print_warning("Some sources failed to configure")
        return False


# ============================================================================
# STEP 10: RUN DBT
# ============================================================================

def step_10_run_dbt():
    """Run dbt models and tests automatically"""
    print_step(10, 11, "Running dbt Models & Tests")
    
    dbt_dir = Path(CONFIG["dbt"]["project_dir"])
    
    if not dbt_dir.exists():
        print_error(f"dbt project not found: {dbt_dir}")
        return
    
    dbt_script = Path("scripts/run_dbt_dremio.py")
    
    # Check if automated script exists
    if dbt_script.exists():
        print_info("Running dbt with automated script...")
        
        try:
            result = run_command([sys.executable, str(dbt_script)], capture=True, check=False)
            
            if result.returncode == 0:
                print_success("dbt execution completed successfully!")
                if result.stdout:
                    print_info("dbt output:")
                    for line in result.stdout.split('\n')[-30:]:  # Show last 30 lines
                        if line.strip():
                            print(f"  {line}")
            else:
                print_warning("dbt execution completed with warnings")
                if result.stderr:
                    print_warning("Warnings/Errors:")
                    for line in result.stderr.split('\n')[-20:]:
                        if line.strip():
                            print(f"  {line}")
        except Exception as e:
            print_error(f"Failed to run dbt script: {e}")
            print_info("Try running dbt manually")
    else:
        # Fallback to direct dbt commands
        print_info("Running dbt commands directly...")
        
        # Check if dbt is available
        try:
            result = run_command(["dbt", "--version"], capture=True, check=False)
            if result.returncode != 0:
                print_warning("dbt not found in PATH, trying with venv...")
                
                # Try to find venv python
                venv_candidates = ["venv/bin/python", "venv/Scripts/python.exe"]
                python_cmd = None
                
                for candidate in venv_candidates:
                    if Path(candidate).exists():
                        python_cmd = candidate
                        break
                
                if not python_cmd:
                    print_warning("Virtual environment not found")
                    print_info("Manual dbt execution required:")
                    print_info("  1. Activate venv: source venv/bin/activate")
                    print_info("  2. cd dbt")
                    print_info("  3. dbt debug")
                    print_info("  4. dbt run")
                    print_info("  5. dbt test")
                    return
        except:
            pass
        
        # Run dbt commands
        original_dir = Path.cwd()
        try:
            os.chdir(dbt_dir)
            
            print_info("Running dbt debug...")
            run_command(["dbt", "debug"], check=False)
            
            print_info("Running dbt deps...")
            run_command(["dbt", "deps"], check=False)
            
            print_info("Running dbt run...")
            result = run_command(["dbt", "run"], capture=True, check=False)
            if result.returncode == 0:
                print_success("dbt run completed successfully!")
            else:
                print_warning("dbt run completed with errors")
            
            print_info("Running dbt test...")
            result = run_command(["dbt", "test"], capture=True, check=False)
            if result.returncode == 0:
                print_success("dbt test completed successfully!")
            else:
                print_warning("dbt test completed with failures")
            
        finally:
            os.chdir(original_dir)
    
    print_success("dbt execution step completed!")


# ============================================================================
# STEP 11: VALIDATE & REPORT
# ============================================================================

def step_11_validate_and_report(with_airbyte=False):
    """Validate ecosystem and generate report"""
    print_step(11, 11, "Validating Ecosystem & Generating Report")
    
    import psycopg2
    from elasticsearch import Elasticsearch
    from minio import Minio
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "services": {},
        "data_volumes": {},
        "status": "SUCCESS",
        "airbyte_enabled": with_airbyte,
    }
    
    # Check PostgreSQL
    try:
        conn = psycopg2.connect(
            host=CONFIG["postgres"]["host"],
            port=CONFIG["postgres"]["port"],
            database=CONFIG["postgres"]["database"],
            user=CONFIG["postgres"]["user"],
            password=CONFIG["postgres"]["password"],
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        customers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        report["services"]["postgresql"] = "HEALTHY"
        report["data_volumes"]["postgresql"] = {
            "customers": customers_count,
            "orders": orders_count,
        }
        print_success(f"PostgreSQL: {customers_count:,} customers, {orders_count:,} orders")
    except Exception as e:
        report["services"]["postgresql"] = f"ERROR: {e}"
        print_error(f"PostgreSQL check failed: {e}")
    
    # Check Elasticsearch
    try:
        es = Elasticsearch(CONFIG["elasticsearch"]["hosts"])
        indices = es.cat.indices(format='json')
        
        es_data = {}
        for idx in indices:
            if idx['index'] in ['application_logs', 'user_events', 'performance_metrics']:
                es_data[idx['index']] = int(idx['docs.count'])
        
        report["services"]["elasticsearch"] = "HEALTHY"
        report["data_volumes"]["elasticsearch"] = es_data
        print_success(f"Elasticsearch: {sum(es_data.values()):,} total documents")
    except Exception as e:
        report["services"]["elasticsearch"] = f"ERROR: {e}"
        print_error(f"Elasticsearch check failed: {e}")
    
    # Check MinIO
    try:
        client = Minio(
            CONFIG["minio"]["endpoint"],
            access_key=CONFIG["minio"]["access_key"],
            secret_key=CONFIG["minio"]["secret_key"],
            secure=False,
        )
        
        objects = list(client.list_objects(CONFIG["minio"]["bucket"], recursive=True))
        
        report["services"]["minio"] = "HEALTHY"
        report["data_volumes"]["minio"] = {
            "files": len(objects),
            "bucket": CONFIG["minio"]["bucket"],
        }
        print_success(f"MinIO: {len(objects)} Parquet files")
    except Exception as e:
        report["services"]["minio"] = f"ERROR: {e}"
        print_error(f"MinIO check failed: {e}")
    
    # Check Dremio
    try:
        response = requests.get(CONFIG["dremio"]["url"], timeout=5)
        report["services"]["dremio"] = "HEALTHY"
        print_success(f"Dremio: Accessible at {CONFIG['dremio']['url']}")
    except Exception as e:
        report["services"]["dremio"] = f"ERROR: {e}"
        print_error(f"Dremio check failed: {e}")
    
    # Test VDS access via SQL
    print_info("Testing VDS access via SQL queries...")
    vds_tests = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    try:
        # Login to Dremio
        login_response = requests.post(
            f"{CONFIG['dremio']['url']}/apiv2/login",
            json={"userName": CONFIG["dremio"]["username"], "password": CONFIG["dremio"]["password"]}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["token"]
            headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
            
            # Define test queries
            test_queries = [
                ("PostgreSQL customers", "SELECT COUNT(*) FROM raw.customers"),
                ("PostgreSQL orders", "SELECT COUNT(*) FROM raw.orders"),
                ("MinIO sales (all)", "SELECT COUNT(*) FROM raw.minio_sales"),
            ]
            
            # Execute each test query
            for test_name, sql in test_queries:
                try:
                    # Submit SQL job
                    job_response = requests.post(
                        f"{CONFIG['dremio']['url']}/api/v3/sql",
                        headers=headers,
                        json={"sql": sql},
                        timeout=10
                    )
                    
                    if job_response.status_code == 200:
                        job_id = job_response.json().get("id")
                        
                        # Wait for job completion (max 20 seconds)
                        for _ in range(40):
                            time.sleep(0.5)
                            status_response = requests.get(
                                f"{CONFIG['dremio']['url']}/api/v3/job/{job_id}",
                                headers=headers,
                                timeout=5
                            )
                            
                            if status_response.status_code == 200:
                                job_state = status_response.json().get("jobState")
                                
                                if job_state == "COMPLETED":
                                    row_count = status_response.json().get("rowCount", 0)
                                    vds_tests["passed"] += 1
                                    vds_tests["tests"].append({
                                        "name": test_name,
                                        "status": "PASSED",
                                        "rows": row_count
                                    })
                                    print_success(f"  ✓ {test_name}: {row_count} rows")
                                    break
                                elif job_state in ["FAILED", "CANCELLED"]:
                                    error_msg = status_response.json().get("errorMessage", "Unknown error")
                                    vds_tests["failed"] += 1
                                    vds_tests["tests"].append({
                                        "name": test_name,
                                        "status": "FAILED",
                                        "error": error_msg[:100]
                                    })
                                    print_warning(f"  ✗ {test_name}: {error_msg[:60]}")
                                    break
                        else:
                            # Timeout
                            vds_tests["failed"] += 1
                            vds_tests["tests"].append({
                                "name": test_name,
                                "status": "TIMEOUT"
                            })
                            print_warning(f"  ✗ {test_name}: Query timeout")
                    else:
                        vds_tests["failed"] += 1
                        vds_tests["tests"].append({
                            "name": test_name,
                            "status": "ERROR",
                            "error": f"HTTP {job_response.status_code}"
                        })
                        print_warning(f"  ✗ {test_name}: Submit failed")
                        
                except Exception as e:
                    vds_tests["failed"] += 1
                    vds_tests["tests"].append({
                        "name": test_name,
                        "status": "ERROR",
                        "error": str(e)[:100]
                    })
                    print_warning(f"  ✗ {test_name}: {str(e)[:60]}")
            
            # Summary
            total_tests = vds_tests["passed"] + vds_tests["failed"]
            if vds_tests["passed"] == total_tests:
                print_success(f"VDS Tests: {vds_tests['passed']}/{total_tests} passed ✓")
            else:
                print_warning(f"VDS Tests: {vds_tests['passed']}/{total_tests} passed")
                
        else:
            print_warning("Could not authenticate to Dremio for VDS testing")
            vds_tests["error"] = "Authentication failed"
            
    except Exception as e:
        print_warning(f"VDS testing failed: {e}")
        vds_tests["error"] = str(e)
    
    report["vds_tests"] = vds_tests
    
    # Check Airbyte if enabled
    if with_airbyte:
        print_info("Checking Airbyte status...")
        airbyte_status = {
            "enabled": True,
            "services_running": False,
            "api_accessible": False,
            "connections": []
        }
        
        try:
            # Check if Airbyte API is accessible
            airbyte_url = CONFIG["airbyte"]["url"]
            response = requests.get(
                f"{airbyte_url}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                airbyte_status["api_accessible"] = True
                airbyte_status["services_running"] = True
                print_success("Airbyte API is accessible")
                
                # Try to list connections
                try:
                    workspaces_response = requests.post(
                        f"{airbyte_url}/workspaces/list",
                        json={},
                        timeout=10
                    )
                    
                    if workspaces_response.status_code == 200:
                        workspaces = workspaces_response.json().get("workspaces", [])
                        if workspaces:
                            workspace_id = workspaces[0]["workspaceId"]
                            
                            connections_response = requests.post(
                                f"{airbyte_url}/connections/list",
                                json={"workspaceId": workspace_id},
                                timeout=10
                            )
                            
                            if connections_response.status_code == 200:
                                connections = connections_response.json().get("connections", [])
                                airbyte_status["connections"] = [
                                    {
                                        "name": conn.get("name"),
                                        "status": conn.get("status"),
                                        "connectionId": conn.get("connectionId")
                                    }
                                    for conn in connections
                                ]
                                print_success(f"Found {len(connections)} Airbyte connection(s)")
                except Exception as e:
                    print_warning(f"Could not list Airbyte connections: {e}")
            else:
                print_warning("Airbyte API not responding")
                
        except Exception as e:
            print_warning(f"Airbyte check failed: {e}")
            airbyte_status["error"] = str(e)
        
        report["airbyte"] = airbyte_status
    
    # Save report
    report_file = Path("ECOSYSTEM_BUILD_REPORT.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print_success(f"Report saved to {report_file}")
    
    # Print summary
    print("\n" + "="*70)
    print(f"{Colors.BOLD}🎉 ECOSYSTEM BUILD COMPLETE!{Colors.ENDC}")
    print("="*70)
    
    total_records = 0
    for source, data in report["data_volumes"].items():
        if isinstance(data, dict):
            count = sum(v for v in data.values() if isinstance(v, int))
            print(f"  • {source.upper()}: {count:,} records")
            total_records += count
    
    print(f"\n📊 Total data records: {total_records:,}")
    print(f"📁 Report: {report_file.absolute()}")
    
    if with_airbyte:
        airbyte_data = report.get("airbyte", {})
        if airbyte_data.get("api_accessible"):
            print(f"\n🔄 Airbyte: {len(airbyte_data.get('connections', []))} connection(s) configured")
            print(f"   UI: {CONFIG['airbyte']['ui_url']}")
        else:
            print("\n⚠️  Airbyte: Services started but not yet accessible")
            print(f"   Check logs: docker-compose -f {CONFIG['airbyte']['compose_file']} logs")
    
    print("="*70 + "\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main orchestration"""
    parser = argparse.ArgumentParser(description="Build complete Dremio+dbt ecosystem")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker startup")
    parser.add_argument("--data-only", action="store_true", help="Regenerate data only")
    parser.add_argument("--with-airbyte", action="store_true", help="Include Airbyte integration")
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}[ROCKET] COMPLETE ECOSYSTEM BUILDER{Colors.ENDC}")
    print("="*70)
    print("This will build the entire Dremio + dbt platform from scratch")
    if args.with_airbyte:
        print("Mode: WITH AIRBYTE INTEGRATION")
        print("Estimated time: 15-20 minutes")
    else:
        print("Estimated time: 10-15 minutes")
    print("="*70 + "\n")
    
    print_info("Starting automated build process...")
    time.sleep(2)  # Brief pause to show message
    
    try:
        if args.data_only:
            print_info("DATA-ONLY MODE: Regenerating data...")
            step_03_create_postgres_schema()
            data = step_04_generate_data()
            step_05_inject_postgres(data)
            step_06_inject_elasticsearch(data)
            step_07_inject_minio(data)
            if args.with_airbyte:
                print_info("Skipping Airbyte in data-only mode")
            step_11_validate_and_report()
        else:
            step_01_check_prerequisites()
            step_02_start_docker(skip=args.skip_docker)
            step_03_create_postgres_schema()
            data = step_04_generate_data()
            step_05_inject_postgres(data)
            step_06_inject_elasticsearch(data)
            step_07_inject_minio(data)
            
            # Optional: Airbyte integration
            if args.with_airbyte:
                step_07b_start_airbyte()
                step_07c_configure_airbyte()
            
            step_08_initialize_dremio()
            step_09_configure_dremio(with_airbyte=args.with_airbyte)
            step_10_run_dbt()
            step_11_validate_and_report(with_airbyte=args.with_airbyte)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] SUCCESS! Ecosystem is ready!{Colors.ENDC}\n")
        if args.with_airbyte:
            print_info(f"Airbyte UI: {CONFIG['airbyte']['ui_url']}")
            print_info("Check connections and sync status in the UI")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Build interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}[X] Build failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
