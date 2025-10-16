"""
Airbyte Integration Setup Script
Automatically configure Airbyte with sources and destinations
"""

import requests
import time
import json
from typing import Dict, Optional

# Configuration
AIRBYTE_API = "http://localhost:8001/api/v1"
AIRBYTE_UI = "http://localhost:8000"

# Source & Destination configs
POSTGRES_CONFIG = {
    "host": "dremio-postgres",
    "port": 5432,
    "database": "business_db",
    "username": "postgres",
    "password": "postgres123",
    "ssl": False,
    "replication_method": {
        "method": "Standard"
    }
}

MINIO_S3_CONFIG = {
    "s3_bucket_name": "airbyte-staging",
    "s3_bucket_path": "postgres-sync",
    "s3_bucket_region": "us-east-1",
    "s3_endpoint": "http://minio:9000",
    "access_key_id": "minioadmin",
    "secret_access_key": "minioadmin123",
    "format": {
        "format_type": "Parquet",
        "compression_codec": "SNAPPY"
    },
    "s3_path_format": "${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_"
}


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_info(msg: str):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.ENDC}")


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")


def wait_for_airbyte(max_attempts: int = 60) -> bool:
    """Wait for Airbyte API to be ready"""
    print_info("Waiting for Airbyte API to be ready...")
    
    for i in range(max_attempts):
        try:
            response = requests.get(f"{AIRBYTE_API}/health", timeout=2)
            if response.status_code == 200:
                print_success(f"Airbyte API is ready! (took {i*2}s)")
                return True
        except Exception as e:
            pass
        
        if i % 10 == 0 and i > 0:
            print_info(f"Still waiting... ({i*2}s elapsed)")
        
        time.sleep(2)
    
    print_error(f"Airbyte API not ready after {max_attempts*2}s")
    return False


def get_source_definitions() -> Dict:
    """Get available source connector definitions"""
    print_info("Fetching source definitions...")
    
    response = requests.post(f"{AIRBYTE_API}/source_definitions/list")
    
    if response.status_code != 200:
        print_error(f"Failed to fetch source definitions: {response.status_code}")
        return {}
    
    definitions = {}
    for source_def in response.json()["sourceDefinitions"]:
        definitions[source_def["name"]] = source_def["sourceDefinitionId"]
    
    print_success(f"Found {len(definitions)} source connectors")
    return definitions


def get_destination_definitions() -> Dict:
    """Get available destination connector definitions"""
    print_info("Fetching destination definitions...")
    
    response = requests.post(f"{AIRBYTE_API}/destination_definitions/list")
    
    if response.status_code != 200:
        print_error(f"Failed to fetch destination definitions: {response.status_code}")
        return {}
    
    definitions = {}
    for dest_def in response.json()["destinationDefinitions"]:
        definitions[dest_def["name"]] = dest_def["destinationDefinitionId"]
    
    print_success(f"Found {len(definitions)} destination connectors")
    return definitions


def create_workspace() -> Optional[str]:
    """Create or get default workspace"""
    print_info("Setting up workspace...")
    
    # List existing workspaces
    response = requests.post(f"{AIRBYTE_API}/workspaces/list")
    
    if response.status_code == 200:
        workspaces = response.json()["workspaces"]
        if workspaces:
            workspace_id = workspaces[0]["workspaceId"]
            print_success(f"Using existing workspace: {workspace_id}")
            return workspace_id
    
    # Create new workspace
    data = {
        "name": "Dremio Integration Workspace",
        "email": "admin@dremio-integration.local"
    }
    
    response = requests.post(f"{AIRBYTE_API}/workspaces/create", json=data)
    
    if response.status_code != 200:
        print_error(f"Failed to create workspace: {response.status_code}")
        return None
    
    workspace_id = response.json()["workspaceId"]
    print_success(f"Workspace created: {workspace_id}")
    return workspace_id


def create_postgres_source(workspace_id: str, source_def_id: str) -> Optional[str]:
    """Create PostgreSQL source connection"""
    print_info("Creating PostgreSQL source...")
    
    data = {
        "workspaceId": workspace_id,
        "name": "PostgreSQL BusinessDB",
        "sourceDefinitionId": source_def_id,
        "connectionConfiguration": POSTGRES_CONFIG
    }
    
    response = requests.post(f"{AIRBYTE_API}/sources/create", json=data)
    
    if response.status_code != 200:
        print_error(f"Failed to create PostgreSQL source: {response.status_code}")
        print_error(response.text)
        return None
    
    source_id = response.json()["sourceId"]
    print_success(f"PostgreSQL source created: {source_id}")
    return source_id


def create_minio_destination(workspace_id: str, dest_def_id: str) -> Optional[str]:
    """Create MinIO (S3) destination"""
    print_info("Creating MinIO destination...")
    
    data = {
        "workspaceId": workspace_id,
        "name": "MinIO Data Lake (S3)",
        "destinationDefinitionId": dest_def_id,
        "connectionConfiguration": MINIO_S3_CONFIG
    }
    
    response = requests.post(f"{AIRBYTE_API}/destinations/create", json=data)
    
    if response.status_code != 200:
        print_error(f"Failed to create MinIO destination: {response.status_code}")
        print_error(response.text)
        return None
    
    dest_id = response.json()["destinationId"]
    print_success(f"MinIO destination created: {dest_id}")
    return dest_id


def discover_schema(source_id: str) -> Optional[Dict]:
    """Discover source schema"""
    print_info("Discovering source schema...")
    
    data = {"sourceId": source_id}
    response = requests.post(f"{AIRBYTE_API}/sources/discover_schema", json=data)
    
    if response.status_code != 200:
        print_error(f"Failed to discover schema: {response.status_code}")
        return None
    
    catalog = response.json()["catalog"]
    streams = catalog.get("streams", [])
    print_success(f"Discovered {len(streams)} streams")
    
    for stream in streams:
        stream_name = stream["stream"]["name"]
        print(f"    • {stream_name}")
    
    return catalog


def create_connection(
    source_id: str,
    destination_id: str,
    catalog: Dict,
    workspace_id: str
) -> Optional[str]:
    """Create sync connection"""
    print_info("Creating sync connection...")
    
    # Configure streams (customers and orders with incremental sync)
    configured_streams = []
    
    for stream in catalog["streams"]:
        stream_name = stream["stream"]["name"]
        
        if stream_name in ["customers", "orders"]:
            configured_stream = {
                "stream": stream["stream"],
                "config": {
                    "syncMode": "incremental",
                    "destinationSyncMode": "append",
                    "cursorField": ["id"],  # Assuming 'id' or 'customer_id'
                    "selected": True
                }
            }
            configured_streams.append(configured_stream)
            print(f"    ✓ Configured: {stream_name} (incremental)")
    
    if not configured_streams:
        print_warning("No streams configured (customers/orders not found)")
        return None
    
    data = {
        "name": "PostgreSQL → MinIO (Incremental)",
        "sourceId": source_id,
        "destinationId": destination_id,
        "syncCatalog": {
            "streams": configured_streams
        },
        "scheduleType": "cron",
        "scheduleData": {
            "cron": {
                "cronExpression": "0 */6 * * *",  # Every 6 hours
                "cronTimeZone": "UTC"
            }
        },
        "namespaceDefinition": "source",
        "namespaceFormat": "${SOURCE_NAMESPACE}",
        "prefix": "",
        "status": "active"
    }
    
    response = requests.post(f"{AIRBYTE_API}/connections/create", json=data)
    
    if response.status_code != 200:
        print_error(f"Failed to create connection: {response.status_code}")
        print_error(response.text)
        return None
    
    connection_id = response.json()["connectionId"]
    print_success(f"Connection created: {connection_id}")
    print_info(f"Schedule: Every 6 hours (cron: 0 */6 * * *)")
    return connection_id


def trigger_manual_sync(connection_id: str) -> bool:
    """Trigger a manual sync"""
    print_info("Triggering manual sync...")
    
    data = {"connectionId": connection_id}
    response = requests.post(f"{AIRBYTE_API}/connections/sync", json=data)
    
    if response.status_code != 200:
        print_error(f"Failed to trigger sync: {response.status_code}")
        return False
    
    job = response.json()["job"]
    job_id = job["id"]
    print_success(f"Sync triggered! Job ID: {job_id}")
    print_info(f"Monitor in UI: {AIRBYTE_UI}/workspaces/<workspace>/connections/{connection_id}")
    return True


def main():
    print("\n" + "="*70)
    print(f"{Colors.BOLD}🚀 AIRBYTE INTEGRATION SETUP{Colors.ENDC}")
    print("="*70 + "\n")
    
    # Step 1: Wait for Airbyte
    if not wait_for_airbyte():
        print_error("Airbyte not ready. Make sure Airbyte is running:")
        print("  docker-compose -f docker-compose-airbyte.yml up -d")
        return
    
    # Step 2: Get connector definitions
    source_defs = get_source_definitions()
    dest_defs = get_destination_definitions()
    
    postgres_def_id = source_defs.get("Postgres")
    s3_def_id = dest_defs.get("S3")
    
    if not postgres_def_id:
        print_error("PostgreSQL connector not found")
        return
    
    if not s3_def_id:
        print_error("S3 connector not found")
        return
    
    print_success(f"PostgreSQL connector: {postgres_def_id[:8]}...")
    print_success(f"S3 connector: {s3_def_id[:8]}...")
    
    # Step 3: Create workspace
    workspace_id = create_workspace()
    if not workspace_id:
        return
    
    # Step 4: Create source
    source_id = create_postgres_source(workspace_id, postgres_def_id)
    if not source_id:
        return
    
    # Step 5: Create destination
    dest_id = create_minio_destination(workspace_id, s3_def_id)
    if not dest_id:
        return
    
    # Step 6: Discover schema
    catalog = discover_schema(source_id)
    if not catalog:
        return
    
    # Step 7: Create connection
    connection_id = create_connection(source_id, dest_id, catalog, workspace_id)
    if not connection_id:
        return
    
    # Step 8: Trigger initial sync (optional)
    print("\n" + "-"*70)
    response = input("Trigger manual sync now? (y/n): ")
    if response.lower() == 'y':
        trigger_manual_sync(connection_id)
    
    # Final summary
    print("\n" + "="*70)
    print(f"{Colors.BOLD}✅ AIRBYTE SETUP COMPLETE!{Colors.ENDC}")
    print("="*70)
    print(f"\n📊 Configuration:")
    print(f"  • Workspace ID: {workspace_id}")
    print(f"  • Source ID:    {source_id}")
    print(f"  • Destination:  {dest_id}")
    print(f"  • Connection:   {connection_id}")
    print(f"\n🌐 Access UI:")
    print(f"  • Airbyte UI:   {AIRBYTE_UI}")
    print(f"  • API:          {AIRBYTE_API}")
    print(f"\n📅 Schedule:")
    print(f"  • Frequency:    Every 6 hours")
    print(f"  • Cron:         0 */6 * * *")
    print(f"\n📁 Data Location:")
    print(f"  • Bucket:       airbyte-staging")
    print(f"  • Path:         postgres-sync/")
    print(f"  • Format:       Parquet (Snappy)")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Setup interrupted by user{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n\n{Colors.RED}❌ Error: {e}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
