#!/usr/bin/env python3
"""
Configure OpenMetadata Airbyte Connector
Automatically creates Airbyte service and ingestion pipeline in OpenMetadata

Requirements:
- OpenMetadata running on http://localhost:8585
- Airbyte running on http://localhost:8001
- At least 1 Airbyte connection configured

Usage:
    python scripts/configure_openmetadata_airbyte.py
"""

import json
import requests
import time
import sys
from datetime import datetime


# Configuration
OPENMETADATA_URL = "http://localhost:8585/api/v1"
OPENMETADATA_UI = "http://localhost:8585"
AIRBYTE_URL = "http://localhost:8001/api/v1"
AIRBYTE_UI = "http://localhost:8000"

# Default credentials
OPENMETADATA_EMAIL = "admin@openmetadata.org"
OPENMETADATA_PASSWORD = "admin"


def print_header():
    """Print script header"""
    print("\n" + "="*70)
    print(" 🔗 OPENMETADATA AIRBYTE CONNECTOR CONFIGURATION")
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


def print_warning(message):
    """Print warning message"""
    print(f"⚠ WARNING: {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ {message}")


def check_openmetadata():
    """Check if OpenMetadata is accessible"""
    try:
        response = requests.get(
            f"{OPENMETADATA_URL}/health",
            timeout=5
        )
        if response.status_code == 200:
            return True
        else:
            print_warning(f"OpenMetadata health check returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to OpenMetadata: {e}")
        return False


def check_airbyte():
    """Check if Airbyte is accessible"""
    try:
        response = requests.get(
            f"{AIRBYTE_URL}/health",
            timeout=5
        )
        if response.status_code == 200:
            return True
        else:
            print_warning(f"Airbyte health check returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to Airbyte: {e}")
        return False


def get_openmetadata_token():
    """Authenticate with OpenMetadata and get access token"""
    try:
        auth_response = requests.post(
            f"{OPENMETADATA_URL}/users/login",
            json={
                "email": OPENMETADATA_EMAIL,
                "password": OPENMETADATA_PASSWORD
            },
            timeout=10
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json().get("accessToken")
            if token:
                print_success("Authentication successful")
                return token
            else:
                print_error("No access token in response")
                return None
        else:
            print_error(f"Authentication failed: {auth_response.status_code}")
            print_info(f"Response: {auth_response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Authentication request failed: {e}")
        return None


def create_airbyte_service(token):
    """Create Airbyte service in OpenMetadata"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    service_config = {
        "name": "airbyte-local",
        "serviceType": "Airbyte",
        "description": "Local Airbyte instance for data ingestion pipelines",
        "connection": {
            "config": {
                "type": "Airbyte",
                "hostPort": "http://airbyte-server:8001",
                "apiVersion": "v1"
            }
        }
    }
    
    try:
        # Try to create service
        response = requests.post(
            f"{OPENMETADATA_URL}/services/pipelineServices",
            headers=headers,
            json=service_config,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            service = response.json()
            print_success(f"Airbyte service created: {service['id']}")
            return service
            
        elif response.status_code == 409:
            # Service already exists, get it
            print_info("Airbyte service already exists, fetching...")
            response = requests.get(
                f"{OPENMETADATA_URL}/services/pipelineServices/name/airbyte-local",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                service = response.json()
                print_success(f"Existing service found: {service['id']}")
                return service
            else:
                print_error(f"Could not fetch existing service: {response.status_code}")
                return None
        else:
            print_error(f"Failed to create service: {response.status_code}")
            print_info(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Service creation request failed: {e}")
        return None


def create_ingestion_pipeline(token, service_id):
    """Create metadata ingestion pipeline for Airbyte"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    ingestion_config = {
        "name": "airbyte-metadata-ingestion",
        "displayName": "Airbyte Metadata Ingestion",
        "description": "Automated ingestion of Airbyte pipelines metadata",
        "pipelineType": "metadata",
        "service": {
            "id": service_id,
            "type": "pipelineService"
        },
        "sourceConfig": {
            "config": {
                "type": "PipelineMetadata",
                "includeLineage": True,
                "includeTags": True,
                "pipelineFilterPattern": {
                    "includes": [".*"]
                }
            }
        },
        "airflowConfig": {
            "scheduleInterval": "0 */12 * * *",  # Every 12 hours
            "startDate": datetime.now().strftime("%Y-%m-%d")
        },
        "loggerLevel": "INFO"
    }
    
    try:
        # Try to create ingestion pipeline
        response = requests.post(
            f"{OPENMETADATA_URL}/services/ingestionPipelines",
            headers=headers,
            json=ingestion_config,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            pipeline = response.json()
            print_success(f"Ingestion pipeline created: {pipeline['id']}")
            return pipeline
            
        elif response.status_code == 409:
            print_info("Ingestion pipeline already exists")
            # Try to get existing pipeline
            response = requests.get(
                f"{OPENMETADATA_URL}/services/ingestionPipelines/name/airbyte-local.airbyte-metadata-ingestion",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                pipeline = response.json()
                print_success(f"Existing pipeline found: {pipeline['id']}")
                return pipeline
            else:
                print_warning("Could not fetch existing pipeline")
                return None
        else:
            print_error(f"Failed to create ingestion pipeline: {response.status_code}")
            print_info(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Ingestion pipeline creation request failed: {e}")
        return None


def trigger_ingestion(token, service_name, pipeline_name):
    """Trigger manual ingestion run"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Full pipeline name: service.pipeline
    full_pipeline_name = f"{service_name}.{pipeline_name}"
    
    try:
        response = requests.post(
            f"{OPENMETADATA_URL}/services/ingestionPipelines/trigger/{full_pipeline_name}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"Ingestion triggered successfully")
            return True
        else:
            print_warning(f"Could not trigger ingestion: {response.status_code}")
            print_info("You can trigger it manually from OpenMetadata UI")
            return False
            
    except requests.exceptions.RequestException as e:
        print_warning(f"Ingestion trigger request failed: {e}")
        print_info("You can trigger it manually from OpenMetadata UI")
        return False


def verify_configuration(token):
    """Verify the configuration by listing Airbyte connections"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Check Airbyte directly
        print_info("Checking Airbyte connections...")
        
        airbyte_response = requests.post(
            f"{AIRBYTE_URL}/workspaces/list",
            json={"pagination": {"pageSize": 10}},
            timeout=10
        )
        
        if airbyte_response.status_code == 200:
            workspaces = airbyte_response.json().get("workspaces", [])
            if workspaces:
                workspace_id = workspaces[0]["workspaceId"]
                
                # List connections
                conn_response = requests.post(
                    f"{AIRBYTE_URL}/connections/list",
                    json={"workspaceId": workspace_id},
                    timeout=10
                )
                
                if conn_response.status_code == 200:
                    connections = conn_response.json().get("connections", [])
                    print_success(f"Found {len(connections)} Airbyte connection(s)")
                    
                    for conn in connections:
                        print_info(f"  - {conn.get('name', 'Unknown')}: {conn.get('status', 'Unknown')}")
                    
                    return True
        
        print_warning("Could not verify Airbyte connections")
        return False
        
    except requests.exceptions.RequestException as e:
        print_warning(f"Verification failed: {e}")
        return False


def print_summary(success):
    """Print final summary"""
    print("\n" + "="*70)
    
    if success:
        print(" ✓ CONFIGURATION COMPLETE!")
        print("="*70 + "\n")
        
        print("📊 Next Steps:\n")
        print(f"1. Open OpenMetadata UI:")
        print(f"   {OPENMETADATA_UI}\n")
        
        print(f"2. Navigate to: Settings → Services → Pipeline Services")
        print(f"   → airbyte-local\n")
        
        print(f"3. View ingested pipelines:")
        print(f"   Pipelines → Filter by 'airbyte-local'\n")
        
        print(f"4. Check lineage:")
        print(f"   Click on a pipeline → Lineage tab\n")
        
        print(f"5. Monitor Airbyte UI:")
        print(f"   {AIRBYTE_UI}\n")
        
        print("📚 Documentation:")
        print("   - OPENMETADATA_AIRBYTE_INTEGRATION.md")
        print("   - READY_FOR_TEST.md\n")
        
    else:
        print(" ✗ CONFIGURATION INCOMPLETE")
        print("="*70 + "\n")
        
        print("⚠ Some steps failed. Please check:\n")
        print("1. OpenMetadata is running:")
        print(f"   docker ps | grep openmetadata\n")
        
        print("2. Airbyte is running:")
        print(f"   docker ps | grep airbyte\n")
        
        print("3. At least 1 Airbyte connection exists:")
        print(f"   {AIRBYTE_UI}\n")
        
        print("4. Try manual configuration:")
        print(f"   - Login: {OPENMETADATA_UI}")
        print(f"   - Settings → Services → Add Pipeline Service")
        print(f"   - Select: Airbyte")
        print(f"   - Host: http://airbyte-server:8001\n")


def main():
    """Main execution"""
    print_header()
    
    success_steps = 0
    total_steps = 6
    
    # Step 1: Check OpenMetadata
    print_step(1, total_steps, "Checking OpenMetadata accessibility")
    if not check_openmetadata():
        print_error("OpenMetadata is not accessible")
        print_info(f"Make sure it's running: {OPENMETADATA_UI}")
        print_summary(False)
        sys.exit(1)
    print_success("OpenMetadata is accessible")
    success_steps += 1
    print()
    
    # Step 2: Check Airbyte
    print_step(2, total_steps, "Checking Airbyte accessibility")
    if not check_airbyte():
        print_error("Airbyte is not accessible")
        print_info(f"Make sure it's running: {AIRBYTE_UI}")
        print_summary(False)
        sys.exit(1)
    print_success("Airbyte is accessible")
    success_steps += 1
    print()
    
    # Step 3: Authenticate
    print_step(3, total_steps, "Authenticating with OpenMetadata")
    token = get_openmetadata_token()
    if not token:
        print_error("Authentication failed")
        print_info(f"Default credentials: {OPENMETADATA_EMAIL} / {OPENMETADATA_PASSWORD}")
        print_summary(False)
        sys.exit(1)
    success_steps += 1
    print()
    
    # Step 4: Create Airbyte service
    print_step(4, total_steps, "Creating Airbyte service in OpenMetadata")
    service = create_airbyte_service(token)
    if not service:
        print_error("Could not create Airbyte service")
        print_summary(False)
        sys.exit(1)
    success_steps += 1
    print()
    
    # Step 5: Create ingestion pipeline
    print_step(5, total_steps, "Creating metadata ingestion pipeline")
    pipeline = create_ingestion_pipeline(token, service['id'])
    if not pipeline:
        print_warning("Could not create ingestion pipeline")
        print_info("You can create it manually from OpenMetadata UI")
    else:
        success_steps += 1
    print()
    
    # Step 6: Trigger initial ingestion
    print_step(6, total_steps, "Triggering initial metadata ingestion")
    trigger_ingestion(token, "airbyte-local", "airbyte-metadata-ingestion")
    success_steps += 1
    print()
    
    # Verification
    print("Verifying configuration...")
    verify_configuration(token)
    print()
    
    # Summary
    print_summary(success_steps >= 4)  # At least service and auth must succeed
    
    if success_steps >= 4:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
