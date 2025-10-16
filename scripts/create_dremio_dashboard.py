"""
Script pour ajouter le dataset Dremio (via proxy PostgreSQL) à Superset
"""

import requests
import json
import time

def login_superset():
    """Connexion à Superset"""
    session = requests.Session()
    login_url = "http://localhost:8088/api/v1/security/login"
    payload = {"username": "admin", "password": "admin", "provider": "db", "refresh": True}
    
    response = session.post(login_url, json=payload)
    response.raise_for_status()
    
    token = response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    
    print("✅ Connecté à Superset")
    return session

def get_csrf_token(session):
    """Récupère le CSRF token"""
    response = session.get("http://localhost:8088/api/v1/security/csrf_token/")
    csrf = response.json().get("result")
    session.headers.update({"X-CSRFToken": csrf, "Referer": "http://localhost:8088"})
    return csrf

def get_database_id(session, db_name="PostgreSQL Business DB"):
    """Récupère l'ID de la database"""
    response = session.get("http://localhost:8088/api/v1/database/")
    databases = response.json().get("result", [])
    for db in databases:
        if db.get("database_name") == db_name:
            return db.get("id")
    return None

def create_dremio_dataset(session, database_id):
    """Crée le dataset pointant vers la vue Dremio"""
    print("\n📊 Création du dataset Dremio (via proxy PostgreSQL)...")
    
    get_csrf_token(session)
    
    dataset_config = {
        "database": database_id,
        "schema": "public",
        "table_name": "superset_phase3_dashboard"
    }
    
    try:
        response = session.post("http://localhost:8088/api/v1/dataset/", json=dataset_config)
        
        if response.status_code == 201:
            dataset_id = response.json().get("id")
            print(f"   ✅ Dataset créé (ID: {dataset_id})")
            return dataset_id
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def create_dremio_chart(session, dataset_id, chart_config):
    """Crée un chart depuis le dataset Dremio"""
    chart_name = chart_config.get("slice_name")
    print(f"\n📈 Création du chart: {chart_name}...")
    
    get_csrf_token(session)
    
    chart_config["datasource_id"] = dataset_id
    chart_config["datasource_type"] = "table"
    
    try:
        response = session.post("http://localhost:8088/api/v1/chart/", json=chart_config)
        
        if response.status_code == 201:
            chart_id = response.json().get("id")
            print(f"   ✅ Chart créé (ID: {chart_id})")
            return chart_id
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def create_dremio_dashboard(session, chart_ids):
    """Crée le dashboard Dremio"""
    print("\n🎨 Création du dashboard Dremio...")
    
    get_csrf_token(session)
    
    # Position layout
    position_json = {
        "DASHBOARD_VERSION_KEY": "v2",
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [], "parents": ["ROOT_ID"]},
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]}
    }
    
    # Ajouter les charts
    for idx, chart_id in enumerate(chart_ids):
        chart_key = f"CHART-{chart_id}"
        if idx < 4:  # 4 premiers charts en haut
            position_json[chart_key] = {
                "type": "CHART", "id": chart_id, "children": [], "parents": ["ROOT_ID", "GRID_ID"],
                "meta": {"width": 3, "height": 4, "chartId": chart_id}
            }
        else:  # Chart 5 en bas
            position_json[chart_key] = {
                "type": "CHART", "id": chart_id, "children": [], "parents": ["ROOT_ID", "GRID_ID"],
                "meta": {"width": 12, "height": 6, "chartId": chart_id}
            }
        position_json["GRID_ID"]["children"].append(chart_key)
    
    dashboard_config = {
        "dashboard_title": "Phase 3 - Dremio Source (Real-time)",
        "slug": "phase3-dremio-realtime",
        "position_json": json.dumps(position_json),
        "published": True
    }
    
    try:
        response = session.post("http://localhost:8088/api/v1/dashboard/", json=dashboard_config)
        
        if response.status_code == 201:
            dashboard_id = response.json().get("id")
            print(f"   ✅ Dashboard créé (ID: {dashboard_id})")
            return dashboard_id
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     SUPERSET - DASHBOARD DREMIO (SOURCE DE VÉRITÉ)         ║
║                                                            ║
║  Crée un dashboard utilisant Dremio comme source via       ║
║  PostgreSQL proxy (vue superset_phase3_dashboard)          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        session = login_superset()
        
        # Récupérer database ID
        db_id = get_database_id(session)
        if not db_id:
            print("❌ Database PostgreSQL Business DB introuvable")
            return 1
        print(f"✅ Database ID: {db_id}")
        
        # Créer dataset
        dataset_id = create_dremio_dataset(session, db_id)
        if not dataset_id:
            return 1
        
        # Créer charts
        chart_ids = []
        
        # Chart 1: Total Customers
        chart_id = create_dremio_chart(session, dataset_id, {
            "slice_name": "[Dremio] Total Customers",
            "viz_type": "big_number_total",
            "params": json.dumps({"metric": "count", "header_font_size": 0.3})
        })
        if chart_id:
            chart_ids.append(chart_id)
            time.sleep(1)
        
        # Chart 2: Coverage Rate
        chart_id = create_dremio_chart(session, dataset_id, {
            "slice_name": "[Dremio] Coverage Rate",
            "viz_type": "gauge_chart",
            "params": json.dumps({
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "coverage_rate_pct"}, 
                          "aggregate": "AVG", "label": "Coverage"},
                "min_val": 0, "max_val": 100
            })
        })
        if chart_id:
            chart_ids.append(chart_id)
            time.sleep(1)
        
        # Chart 3: Email Quality
        chart_id = create_dremio_chart(session, dataset_id, {
            "slice_name": "[Dremio] Email Quality",
            "viz_type": "gauge_chart",
            "params": json.dumps({
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "email_quality_pct"}, 
                          "aggregate": "AVG", "label": "Email Quality"},
                "min_val": 0, "max_val": 100
            })
        })
        if chart_id:
            chart_ids.append(chart_id)
            time.sleep(1)
        
        # Chart 4: Country Quality
        chart_id = create_dremio_chart(session, dataset_id, {
            "slice_name": "[Dremio] Country Quality",
            "viz_type": "gauge_chart",
            "params": json.dumps({
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "country_quality_pct"}, 
                          "aggregate": "AVG", "label": "Country Quality"},
                "min_val": 0, "max_val": 100
            })
        })
        if chart_id:
            chart_ids.append(chart_id)
            time.sleep(1)
        
        # Chart 5: Source indicator
        chart_id = create_dremio_chart(session, dataset_id, {
            "slice_name": "[Dremio] Data Source",
            "viz_type": "big_number_total",
            "params": json.dumps({"metric": "count"})
        })
        if chart_id:
            chart_ids.append(chart_id)
        
        # Créer dashboard
        dashboard_id = create_dremio_dashboard(session, chart_ids)
        
        if dashboard_id:
            print("\n" + "="*60)
            print("✅ DASHBOARD DREMIO CRÉÉ!")
            print("="*60)
            print(f"\n📊 Source de vérité: Dremio ($scratch.phase3_all_in_one)")
            print(f"🔄 Proxy: PostgreSQL (vue superset_phase3_dashboard)")
            print(f"📈 Charts créés: {len(chart_ids)}")
            print(f"🎨 Dashboard ID: {dashboard_id}")
            print(f"\n🌐 URL: http://localhost:8088/superset/dashboard/{dashboard_id}/")
            print(f"\n💡 Pour synchroniser: python scripts\\sync_dremio_realtime.py")
            print(f"💡 Mode continu: python scripts\\sync_dremio_realtime.py --continuous 5")
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
