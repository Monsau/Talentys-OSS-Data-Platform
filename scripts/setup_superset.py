#!/usr/bin/env python3
"""
Apache Superset - Automated Setup for Phase 3 Dashboard
Connects to Dremio and creates datasets, charts, and dashboards
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
SUPERSET_URL = "http://localhost:8088"
SUPERSET_USERNAME = "admin"
SUPERSET_PASSWORD = "admin"

# Dremio connection
DREMIO_CONNECTION = {
    "database_name": "Dremio Phase 3",
    "sqlalchemy_uri": "dremio://admin:admin123@dremio:9047/dremio;SSL=0",
    "expose_in_sqllab": True,
    "allow_ctas": True,
    "allow_cvas": True,
    "allow_dml": True,
}

class SupersetClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None
        
    def login(self):
        """Login to Superset and get access token"""
        print("🔐 Logging in to Superset...")
        
        # Get CSRF token
        response = self.session.get(f"{self.base_url}/login/")
        
        # Login
        login_data = {
            "username": self.username,
            "password": self.password,
            "provider": "db"
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/security/login",
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
            print("✅ Logged in successfully!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def get_csrf_token(self):
        """Get CSRF token for POST requests"""
        response = self.session.get(f"{self.base_url}/api/v1/security/csrf_token/")
        if response.status_code == 200:
            self.csrf_token = response.json().get("result")
            self.session.headers.update({"X-CSRFToken": self.csrf_token})
            return self.csrf_token
        return None
    
    def create_database(self, config: Dict[str, Any]) -> int:
        """Create database connection"""
        print(f"\n📊 Creating database connection: {config['database_name']}")
        
        self.get_csrf_token()
        
        response = self.session.post(
            f"{self.base_url}/api/v1/database/",
            json=config
        )
        
        if response.status_code in [200, 201]:
            db_id = response.json().get("id")
            print(f"✅ Database created with ID: {db_id}")
            return db_id
        else:
            print(f"⚠️ Database creation status: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to find existing database
            response = self.session.get(f"{self.base_url}/api/v1/database/")
            if response.status_code == 200:
                databases = response.json().get("result", [])
                for db in databases:
                    if db.get("database_name") == config["database_name"]:
                        print(f"✅ Database already exists with ID: {db['id']}")
                        return db["id"]
            return None
    
    def create_dataset(self, database_id: int, schema: str, table: str) -> int:
        """Create dataset (table)"""
        print(f"\n📋 Creating dataset: {schema}.{table}")
        
        self.get_csrf_token()
        
        dataset_config = {
            "database": database_id,
            "schema": schema,
            "table_name": table
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/dataset/",
            json=dataset_config
        )
        
        if response.status_code in [200, 201]:
            dataset_id = response.json().get("id")
            print(f"✅ Dataset created with ID: {dataset_id}")
            return dataset_id
        else:
            print(f"⚠️ Dataset creation status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def create_chart(self, dataset_id: int, chart_config: Dict[str, Any]) -> int:
        """Create chart"""
        print(f"\n📈 Creating chart: {chart_config['slice_name']}")
        
        self.get_csrf_token()
        
        response = self.session.post(
            f"{self.base_url}/api/v1/chart/",
            json=chart_config
        )
        
        if response.status_code in [200, 201]:
            chart_id = response.json().get("id")
            print(f"✅ Chart created with ID: {chart_id}")
            return chart_id
        else:
            print(f"⚠️ Chart creation status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def create_dashboard(self, dashboard_config: Dict[str, Any]) -> int:
        """Create dashboard"""
        print(f"\n🎨 Creating dashboard: {dashboard_config['dashboard_title']}")
        
        self.get_csrf_token()
        
        response = self.session.post(
            f"{self.base_url}/api/v1/dashboard/",
            json=dashboard_config
        )
        
        if response.status_code in [200, 201]:
            dashboard_id = response.json().get("id")
            print(f"✅ Dashboard created with ID: {dashboard_id}")
            return dashboard_id
        else:
            print(f"⚠️ Dashboard creation status: {response.status_code}")
            print(f"Response: {response.text}")
            return None

def main():
    print("="*60)
    print("🚀 Apache Superset - Automated Setup")
    print("="*60)
    
    # Initialize client
    client = SupersetClient(SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)
    
    # Login
    if not client.login():
        print("❌ Failed to login. Exiting.")
        return
    
    # Wait for Superset to be fully ready
    print("\n⏳ Waiting for Superset to be fully ready...")
    time.sleep(5)
    
    # Create database connection
    db_id = client.create_database(DREMIO_CONNECTION)
    
    if not db_id:
        print("❌ Failed to create database connection. Exiting.")
        return
    
    # Create dataset for phase3_all_in_one
    dataset_id = client.create_dataset(
        database_id=db_id,
        schema="$scratch",
        table="phase3_all_in_one"
    )
    
    if not dataset_id:
        print("❌ Failed to create dataset. Exiting.")
        return
    
    # Create charts
    chart_ids = []
    
    # Chart 1: Big Number - Total Customers
    chart1_config = {
        "slice_name": "Total Customers",
        "viz_type": "big_number_total",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps({
            "metric": "COUNT(*)",
            "adhoc_filters": []
        })
    }
    chart1_id = client.create_chart(dataset_id, chart1_config)
    if chart1_id:
        chart_ids.append(chart1_id)
    
    # Chart 2: Pie Chart - Source Distribution
    chart2_config = {
        "slice_name": "Source Distribution",
        "viz_type": "pie",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps({
            "groupby": ["source_status"],
            "metric": "COUNT(*)",
            "adhoc_filters": []
        })
    }
    chart2_id = client.create_chart(dataset_id, chart2_config)
    if chart2_id:
        chart_ids.append(chart2_id)
    
    # Create dashboard
    dashboard_config = {
        "dashboard_title": "Phase 3 - Data Quality Dashboard",
        "slug": "phase3-data-quality",
        "published": True,
        "position_json": json.dumps({
            "DASHBOARD_VERSION_KEY": "v2",
            "GRID_ID": {
                "type": "GRID",
                "id": "GRID_ID",
                "children": [f"CHART-{i}" for i in range(len(chart_ids))],
                "parents": ["ROOT_ID"]
            }
        })
    }
    
    dashboard_id = client.create_dashboard(dashboard_config)
    
    # Summary
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print(f"\n📊 Database ID: {db_id}")
    print(f"📋 Dataset ID: {dataset_id}")
    print(f"📈 Charts created: {len(chart_ids)}")
    print(f"🎨 Dashboard ID: {dashboard_id}")
    print(f"\n🌐 Access dashboard at:")
    print(f"   {SUPERSET_URL}/superset/dashboard/{dashboard_id}/")
    print("\n💡 Note: You may need to manually configure chart positions in the dashboard editor.")

if __name__ == "__main__":
    main()
