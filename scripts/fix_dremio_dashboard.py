"""
Script simplifié pour créer un dashboard Dremio fonctionnel
"""

import requests
import json

def main():
    # Login
    session = requests.Session()
    response = session.post("http://localhost:8088/api/v1/security/login", 
                           json={"username": "admin", "password": "admin", "provider": "db", "refresh": True})
    token = response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    
    # Get CSRF
    response = session.get("http://localhost:8088/api/v1/security/csrf_token/")
    csrf = response.json().get("result")
    session.headers.update({"X-CSRFToken": csrf, "Referer": "http://localhost:8088"})
    
    print("✅ Connecté à Superset")
    
    # Vérifier que le dataset existe
    response = session.get("http://localhost:8088/api/v1/dataset/")
    datasets = response.json().get("result", [])
    
    dataset_id = None
    for ds in datasets:
        if ds.get("table_name") == "superset_phase3_dashboard":
            dataset_id = ds.get("id")
            print(f"✅ Dataset trouvé (ID: {dataset_id})")
            break
    
    if not dataset_id:
        print("❌ Dataset superset_phase3_dashboard introuvable")
        return 1
    
    # Rafraîchir les colonnes du dataset
    print("\n🔄 Refresh des colonnes du dataset...")
    response = session.put(f"http://localhost:8088/api/v1/dataset/{dataset_id}", 
                          json={"columns": []})
    
    # Créer un chart simple avec table
    print("\n📊 Création d'un chart Table simple...")
    
    chart_config = {
        "slice_name": "[Dremio] Phase 3 Data Quality Table",
        "viz_type": "table",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps({
            "metrics": [],
            "groupby": [],
            "columns": [
                "total_customers", "coverage_rate_pct", 
                "email_quality_pct", "country_quality_pct", 
                "overall_status", "source", "synced_at"
            ],
            "row_limit": 10
        })
    }
    
    response = session.post("http://localhost:8088/api/v1/chart/", json=chart_config)
    
    if response.status_code == 201:
        chart_id = response.json().get("id")
        print(f"   ✅ Chart créé (ID: {chart_id})")
        print(f"\n🌐 Voir le chart: http://localhost:8088/explore/?form_data=%7B%22slice_id%22%3A{chart_id}%7D")
        print(f"\n💡 Source de vérité: Dremio")
        print(f"💡 Données synchronisées via: python scripts\\sync_dremio_realtime.py")
        return 0
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   Response: {response.text}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
