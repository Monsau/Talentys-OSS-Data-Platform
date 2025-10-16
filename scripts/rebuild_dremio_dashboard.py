"""
Script pour corriger et recréer les charts du Dashboard 2 (Dremio)
Utilise des configurations simples qui fonctionnent
"""

import requests
import json
import time

def login_superset():
    """Connexion à Superset"""
    session = requests.Session()
    response = session.post("http://localhost:8088/api/v1/security/login", 
                           json={"username": "admin", "password": "admin", "provider": "db", "refresh": True})
    token = response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    
    # Get CSRF
    response = session.get("http://localhost:8088/api/v1/security/csrf_token/")
    csrf = response.json().get("result")
    session.headers.update({"X-CSRFToken": csrf, "Referer": "http://localhost:8088"})
    
    return session

def get_dataset_id(session, table_name="superset_phase3_dashboard"):
    """Récupère l'ID du dataset"""
    response = session.get("http://localhost:8088/api/v1/dataset/")
    datasets = response.json().get("result", [])
    for ds in datasets:
        if ds.get("table_name") == table_name:
            return ds.get("id")
    return None

def delete_old_charts(session, chart_ids):
    """Supprime les anciens charts qui ont des erreurs"""
    for chart_id in chart_ids:
        try:
            response = session.delete(f"http://localhost:8088/api/v1/chart/{chart_id}")
            if response.status_code == 200:
                print(f"   ✅ Chart {chart_id} supprimé")
        except:
            pass

def create_chart(session, dataset_id, chart_config):
    """Crée un chart"""
    chart_name = chart_config.get("slice_name")
    print(f"\n📈 Création: {chart_name}...")
    
    chart_config["datasource_id"] = dataset_id
    chart_config["datasource_type"] = "table"
    
    try:
        response = session.post("http://localhost:8088/api/v1/chart/", json=chart_config)
        
        if response.status_code == 201:
            chart_id = response.json().get("id")
            print(f"   ✅ Chart créé (ID: {chart_id})")
            return chart_id
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     CORRECTION DASHBOARD 2 - DREMIO SOURCE                 ║
║                                                            ║
║  Crée des charts simples qui fonctionnent                  ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    session = login_superset()
    print("✅ Connecté à Superset")
    
    dataset_id = get_dataset_id(session)
    if not dataset_id:
        print("❌ Dataset superset_phase3_dashboard introuvable")
        return 1
    print(f"✅ Dataset ID: {dataset_id}")
    
    # Supprimer les anciens charts problématiques (6-10)
    print("\n🗑️  Suppression des anciens charts...")
    delete_old_charts(session, [6, 7, 8, 9, 10])
    
    chart_ids = []
    
    # Chart 1: Total Customers (Big Number avec COUNT)
    chart_id = create_chart(session, dataset_id, {
        "slice_name": "[Dremio] Total Customers",
        "viz_type": "big_number_total",
        "params": json.dumps({
            "metric": {
                "expressionType": "SIMPLE",
                "column": {"column_name": "total_customers"},
                "aggregate": "MAX",
                "label": "Total"
            },
            "header_font_size": 0.4
        })
    })
    if chart_id:
        chart_ids.append(chart_id)
    time.sleep(1)
    
    # Chart 2: Coverage Rate (Big Number)
    chart_id = create_chart(session, dataset_id, {
        "slice_name": "[Dremio] Coverage Rate",
        "viz_type": "big_number_total",
        "params": json.dumps({
            "metric": {
                "expressionType": "SIMPLE",
                "column": {"column_name": "coverage_rate_pct"},
                "aggregate": "MAX",
                "label": "Coverage %"
            },
            "header_font_size": 0.4,
            "subheader_font_size": 0.2,
            "y_axis_format": ".2f"
        })
    })
    if chart_id:
        chart_ids.append(chart_id)
    time.sleep(1)
    
    # Chart 3: Email Quality (Big Number)
    chart_id = create_chart(session, dataset_id, {
        "slice_name": "[Dremio] Email Quality",
        "viz_type": "big_number_total",
        "params": json.dumps({
            "metric": {
                "expressionType": "SIMPLE",
                "column": {"column_name": "email_quality_pct"},
                "aggregate": "MAX",
                "label": "Email Quality %"
            },
            "header_font_size": 0.4,
            "y_axis_format": ".2f"
        })
    })
    if chart_id:
        chart_ids.append(chart_id)
    time.sleep(1)
    
    # Chart 4: Country Quality (Big Number)
    chart_id = create_chart(session, dataset_id, {
        "slice_name": "[Dremio] Country Quality",
        "viz_type": "big_number_total",
        "params": json.dumps({
            "metric": {
                "expressionType": "SIMPLE",
                "column": {"column_name": "country_quality_pct"},
                "aggregate": "MAX",
                "label": "Country Quality %"
            },
            "header_font_size": 0.4,
            "y_axis_format": ".2f"
        })
    })
    if chart_id:
        chart_ids.append(chart_id)
    time.sleep(1)
    
    # Chart 5: Status (Big Number avec texte)
    chart_id = create_chart(session, dataset_id, {
        "slice_name": "[Dremio] Overall Status",
        "viz_type": "big_number_total",
        "params": json.dumps({
            "metric": "count",
            "header_font_size": 0.3
        })
    })
    if chart_id:
        chart_ids.append(chart_id)
    time.sleep(1)
    
    # Chart 6: Table détaillée
    chart_id = create_chart(session, dataset_id, {
        "slice_name": "[Dremio] Detailed Metrics",
        "viz_type": "table",
        "params": json.dumps({
            "metrics": [],
            "groupby": [],
            "columns": [
                "total_customers", 
                "both_sources",
                "postgres_only",
                "minio_only",
                "coverage_rate_pct", 
                "email_quality_pct", 
                "country_quality_pct", 
                "overall_status"
            ],
            "row_limit": 10,
            "include_time": True
        })
    })
    if chart_id:
        chart_ids.append(chart_id)
    
    # Recréer le dashboard
    print("\n🎨 Recréation du dashboard...")
    
    # Supprimer l'ancien dashboard 2
    try:
        session.delete("http://localhost:8088/api/v1/dashboard/2")
        print("   ✅ Ancien dashboard supprimé")
    except:
        pass
    
    # Position layout
    position_json = {
        "DASHBOARD_VERSION_KEY": "v2",
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [], "parents": ["ROOT_ID"]},
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]}
    }
    
    # Ajouter les charts
    for idx, chart_id in enumerate(chart_ids):
        chart_key = f"CHART-{chart_id}"
        if idx < 5:  # 5 premiers charts en haut (Big Numbers)
            position_json[chart_key] = {
                "type": "CHART", 
                "id": chart_id, 
                "children": [], 
                "parents": ["ROOT_ID", "GRID_ID"],
                "meta": {
                    "width": int(12 / 5),  # 5 colonnes
                    "height": 3, 
                    "chartId": chart_id
                }
            }
        else:  # Table en bas
            position_json[chart_key] = {
                "type": "CHART", 
                "id": chart_id, 
                "children": [], 
                "parents": ["ROOT_ID", "GRID_ID"],
                "meta": {
                    "width": 12, 
                    "height": 8, 
                    "chartId": chart_id
                }
            }
        position_json["GRID_ID"]["children"].append(chart_key)
    
    dashboard_config = {
        "dashboard_title": "Phase 3 - Dremio Source of Truth",
        "slug": "phase3-dremio-source",
        "position_json": json.dumps(position_json),
        "published": True
    }
    
    response = session.post("http://localhost:8088/api/v1/dashboard/", json=dashboard_config)
    
    if response.status_code == 201:
        dashboard_id = response.json().get("id")
        print(f"   ✅ Dashboard créé (ID: {dashboard_id})")
        
        print("\n" + "="*60)
        print("✅ DASHBOARD DREMIO CORRIGÉ!")
        print("="*60)
        print(f"\n📊 Source de vérité: Dremio")
        print(f"📈 Charts créés: {len(chart_ids)}")
        print(f"🎨 Dashboard ID: {dashboard_id}")
        print(f"\n🌐 URL: http://localhost:8088/superset/dashboard/{dashboard_id}/")
        print(f"🔐 Login: admin / admin")
        print(f"\n💡 Synchronisation: python scripts\\sync_dremio_realtime.py")
        return 0
    else:
        print(f"   ❌ Erreur dashboard: {response.status_code}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
