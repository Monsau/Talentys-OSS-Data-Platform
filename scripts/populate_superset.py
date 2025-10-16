"""
Script pour peupler automatiquement Apache Superset avec les données Phase 3
Crée: Database, Dataset, Charts, et Dashboard
"""

import requests
import json
import time
import sys
from typing import Optional, Dict, Any

class SupersetPopulator:
    """Client pour peupler Superset automatiquement via API"""
    
    def __init__(self, base_url: str = "http://localhost:8088"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.csrf_token: Optional[str] = None
        self.database_id: Optional[int] = None
        self.dataset_id: Optional[int] = None
        self.chart_ids: Dict[str, int] = {}
        self.dashboard_id: Optional[int] = None
    
    def login(self, username: str = "admin", password: str = "admin") -> bool:
        """Connexion à Superset"""
        print(f"🔐 Connexion à Superset ({username})...")
        
        login_url = f"{self.base_url}/api/v1/security/login"
        payload = {
            "username": username,
            "password": password,
            "provider": "db",
            "refresh": True
        }
        
        try:
            response = self.session.post(login_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data.get("access_token")
            
            if self.access_token:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })
                print("   ✅ Connexion réussie!")
                return True
            else:
                print("   ❌ Token d'accès non reçu")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erreur de connexion: {e}")
            return False
    
    def get_csrf_token(self) -> Optional[str]:
        """Récupère le token CSRF"""
        if self.csrf_token:
            return self.csrf_token
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/csrf_token/")
            response.raise_for_status()
            data = response.json()
            self.csrf_token = data.get("result")
            
            if self.csrf_token:
                self.session.headers.update({
                    "X-CSRFToken": self.csrf_token,
                    "Referer": self.base_url
                })
            
            return self.csrf_token
        except Exception as e:
            print(f"   ⚠️ Erreur CSRF token: {e}")
            return None
    
    def create_database(self) -> bool:
        """Crée la connexion Dremio"""
        print("\n📊 Création de la database Dremio...")
        
        # Vérifier si la database existe déjà
        try:
            response = self.session.get(f"{self.base_url}/api/v1/database/")
            if response.status_code == 200:
                databases = response.json().get("result", [])
                for db in databases:
                    if db.get("database_name") == "Dremio Analytics":
                        self.database_id = db.get("id")
                        print(f"   ✅ Database existe déjà (ID: {self.database_id})")
                        return True
        except Exception as e:
            print(f"   ⚠️ Vérification database: {e}")
        
    def create_database(self) -> bool:
        """Crée la connexion PostgreSQL Business DB"""
        print("\n📊 Création de la database PostgreSQL Business DB...")
        
        # Vérifier si la database existe déjà
        try:
            response = self.session.get(f"{self.base_url}/api/v1/database/")
            if response.status_code == 200:
                databases = response.json().get("result", [])
                for db in databases:
                    if db.get("database_name") == "PostgreSQL Business DB":
                        self.database_id = db.get("id")
                        print(f"   ✅ Database existe déjà (ID: {self.database_id})")
                        return True
        except Exception as e:
            print(f"   ⚠️ Vérification database: {e}")
        
        # Créer la database
        self.get_csrf_token()
        
        database_config = {
            "database_name": "PostgreSQL Business DB",
            "engine": "postgresql",
            "configuration_method": "sqlalchemy_form",
            "sqlalchemy_uri": "postgresql://postgres:postgres123@dremio-postgres:5432/business_db",
            "expose_in_sqllab": True,
            "allow_ctas": True,
            "allow_cvas": True,
            "allow_dml": False,
            "extra": json.dumps({
                "metadata_params": {},
                "engine_params": {},
                "metadata_cache_timeout": {},
                "schemas_allowed_for_csv_upload": []
            })
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/database/",
                json=database_config
            )
            
            if response.status_code == 201:
                data = response.json()
                self.database_id = data.get("id")
                print(f"   ✅ Database créée (ID: {self.database_id})")
                return True
            else:
                print(f"   ❌ Erreur création database: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    def test_database_connection(self) -> bool:
        """Test la connexion à la database"""
        print("\n🔍 Test de la connexion Dremio...")
        
        if not self.database_id:
            print("   ❌ Database ID manquant")
            return False
        
        self.get_csrf_token()
        
    def test_database_connection(self) -> bool:
        """Test la connexion à la database"""
        print("\n🔍 Test de la connexion PostgreSQL...")
        
        if not self.database_id:
            print("   ❌ Database ID manquant")
            return False
        
        self.get_csrf_token()
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/database/test_connection/",
                json={
                    "database_name": "PostgreSQL Business DB",
                    "engine": "postgresql",
                    "sqlalchemy_uri": "postgresql://postgres:postgres123@dremio-postgres:5432/business_db"
                }
            )
            
            if response.status_code == 200:
                print("   ✅ Connexion Dremio validée!")
                return True
            else:
                print(f"   ⚠️ Test connexion: {response.status_code}")
                return True  # Continue quand même
                
        except Exception as e:
            print(f"   ⚠️ Exception test: {e}")
            return True  # Continue quand même
    
    def create_dataset(self) -> bool:
        """Crée le dataset depuis les tables customers"""
        print("\n📋 Création du dataset customers...")
        
        if not self.database_id:
            print("   ❌ Database ID manquant")
            return False
        
        # Vérifier si le dataset existe déjà
        try:
            response = self.session.get(f"{self.base_url}/api/v1/dataset/")
            if response.status_code == 200:
                datasets = response.json().get("result", [])
                for ds in datasets:
                    if ds.get("table_name") == "customers":
                        self.dataset_id = ds.get("id")
                        print(f"   ✅ Dataset existe déjà (ID: {self.dataset_id})")
                        return True
        except Exception as e:
            print(f"   ⚠️ Vérification dataset: {e}")
        
        self.get_csrf_token()
        
        dataset_config = {
            "database": self.database_id,
            "schema": "public",
            "table_name": "customers"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/dataset/",
                json=dataset_config
            )
            
            if response.status_code == 201:
                data = response.json()
                self.dataset_id = data.get("id")
                print(f"   ✅ Dataset créé (ID: {self.dataset_id})")
                return True
            else:
                print(f"   ❌ Erreur création dataset: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    def create_chart(self, chart_config: Dict[str, Any]) -> Optional[int]:
        """Crée un chart"""
        chart_name = chart_config.get("slice_name", "Unknown Chart")
        print(f"\n📈 Création du chart: {chart_name}...")
        
        if not self.dataset_id:
            print("   ❌ Dataset ID manquant")
            return None
        
        self.get_csrf_token()
        
        # Ajouter dataset_id au config
        chart_config["datasource_id"] = self.dataset_id
        chart_config["datasource_type"] = "table"
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chart/",
                json=chart_config
            )
            
            if response.status_code == 201:
                data = response.json()
                chart_id = data.get("id")
                print(f"   ✅ Chart créé (ID: {chart_id})")
                return chart_id
            else:
                print(f"   ❌ Erreur création chart: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return None
    
    def create_all_charts(self) -> bool:
        """Crée tous les charts pour le dashboard"""
        print("\n" + "="*60)
        print("📊 CRÉATION DES CHARTS")
        print("="*60)
        
        # Chart 1: Total Customers (Big Number)
        chart1_config = {
            "slice_name": "Total Customers",
            "viz_type": "big_number_total",
            "params": json.dumps({
                "metric": "count",
                "adhoc_filters": [],
                "header_font_size": 0.3,
                "subheader_font_size": 0.15,
                "y_axis_format": ",d"
            })
        }
        chart_id = self.create_chart(chart1_config)
        if chart_id:
            self.chart_ids["total_customers"] = chart_id
        
        time.sleep(1)
        
        # Chart 2: Coverage Rate (Gauge)
        chart2_config = {
            "slice_name": "Coverage Rate",
            "viz_type": "gauge_chart",
            "params": json.dumps({
                "metric": {
                    "expressionType": "SIMPLE",
                    "column": {"column_name": "coverage_rate_pct"},
                    "aggregate": "AVG",
                    "label": "Coverage Rate"
                },
                "min_val": 0,
                "max_val": 100,
                "value_formatter": ".2f"
            })
        }
        chart_id = self.create_chart(chart2_config)
        if chart_id:
            self.chart_ids["coverage_rate"] = chart_id
        
        time.sleep(1)
        
        # Chart 3: Email Quality (Gauge)
        chart3_config = {
            "slice_name": "Email Quality",
            "viz_type": "gauge_chart",
            "params": json.dumps({
                "metric": {
                    "expressionType": "SIMPLE",
                    "column": {"column_name": "email_quality_pct"},
                    "aggregate": "AVG",
                    "label": "Email Quality"
                },
                "min_val": 0,
                "max_val": 100,
                "value_formatter": ".2f"
            })
        }
        chart_id = self.create_chart(chart3_config)
        if chart_id:
            self.chart_ids["email_quality"] = chart_id
        
        time.sleep(1)
        
        # Chart 4: Country Quality (Gauge)
        chart4_config = {
            "slice_name": "Country Quality",
            "viz_type": "gauge_chart",
            "params": json.dumps({
                "metric": {
                    "expressionType": "SIMPLE",
                    "column": {"column_name": "country_quality_pct"},
                    "aggregate": "AVG",
                    "label": "Country Quality"
                },
                "min_val": 0,
                "max_val": 100,
                "value_formatter": ".2f"
            })
        }
        chart_id = self.create_chart(chart4_config)
        if chart_id:
            self.chart_ids["country_quality"] = chart_id
        
        time.sleep(1)
        
        # Chart 5: Quality Metrics Comparison (Bar Chart)
        chart5_config = {
            "slice_name": "Quality Metrics Comparison",
            "viz_type": "dist_bar",
            "query_context": json.dumps({
                "datasource": {
                    "id": self.dataset_id,
                    "type": "table"
                },
                "queries": [{
                    "metrics": [
                        {
                            "expressionType": "SIMPLE",
                            "column": {"column_name": "coverage_rate_pct"},
                            "aggregate": "AVG",
                            "label": "Coverage Rate"
                        },
                        {
                            "expressionType": "SIMPLE",
                            "column": {"column_name": "email_quality_pct"},
                            "aggregate": "AVG",
                            "label": "Email Quality"
                        },
                        {
                            "expressionType": "SIMPLE",
                            "column": {"column_name": "country_quality_pct"},
                            "aggregate": "AVG",
                            "label": "Country Quality"
                        }
                    ],
                    "filters": []
                }]
            }),
            "params": json.dumps({
                "viz_type": "dist_bar",
                "show_legend": True,
                "show_bar_value": True,
                "y_axis_format": ".2f"
            })
        }
        chart_id = self.create_chart(chart5_config)
        if chart_id:
            self.chart_ids["metrics_comparison"] = chart_id
        
        success = len(self.chart_ids) >= 4
        if success:
            print(f"\n   ✅ {len(self.chart_ids)} charts créés avec succès!")
        else:
            print(f"\n   ⚠️ Seulement {len(self.chart_ids)} charts créés")
        
        return success
    
    def create_dashboard(self) -> bool:
        """Crée le dashboard et y ajoute les charts"""
        print("\n" + "="*60)
        print("🎨 CRÉATION DU DASHBOARD")
        print("="*60)
        
        if not self.chart_ids:
            print("   ❌ Aucun chart à ajouter")
            return False
        
        self.get_csrf_token()
        
        # Position layout pour les charts
        position_json = {
            "DASHBOARD_VERSION_KEY": "v2",
            "GRID_ID": {
                "type": "GRID",
                "id": "GRID_ID",
                "children": [],
                "parents": ["ROOT_ID"]
            },
            "ROOT_ID": {
                "type": "ROOT",
                "id": "ROOT_ID",
                "children": ["GRID_ID"]
            }
        }
        
        # Ajouter les charts au layout
        row = 0
        col = 0
        chart_keys = list(self.chart_ids.keys())
        
        for idx, (chart_name, chart_id) in enumerate(self.chart_ids.items()):
            chart_key = f"CHART-{chart_id}"
            
            # 4 charts en haut (1 ligne, 4 colonnes)
            if idx < 4:
                position_json[chart_key] = {
                    "type": "CHART",
                    "id": chart_id,
                    "children": [],
                    "parents": ["ROOT_ID", "GRID_ID"],
                    "meta": {
                        "width": 3,
                        "height": 4,
                        "chartId": chart_id
                    }
                }
            # Chart 5 en bas (pleine largeur)
            else:
                position_json[chart_key] = {
                    "type": "CHART",
                    "id": chart_id,
                    "children": [],
                    "parents": ["ROOT_ID", "GRID_ID"],
                    "meta": {
                        "width": 12,
                        "height": 6,
                        "chartId": chart_id
                    }
                }
            
            position_json["GRID_ID"]["children"].append(chart_key)
        
        dashboard_config = {
            "dashboard_title": "Phase 3 - Data Quality Dashboard",
            "slug": "phase3-data-quality",
            "position_json": json.dumps(position_json),
            "published": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/dashboard/",
                json=dashboard_config
            )
            
            if response.status_code == 201:
                data = response.json()
                self.dashboard_id = data.get("id")
                print(f"\n   ✅ Dashboard créé (ID: {self.dashboard_id})")
                print(f"\n   🌐 URL: {self.base_url}/superset/dashboard/{self.dashboard_id}/")
                return True
            else:
                print(f"   ❌ Erreur création dashboard: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    def populate(self) -> bool:
        """Peuple complètement Superset"""
        print("\n" + "="*60)
        print("🚀 POPULATION DE SUPERSET")
        print("="*60)
        
        # Étape 1: Login
        if not self.login():
            print("\n❌ Échec de connexion")
            return False
        
        # Étape 2: Create Database
        if not self.create_database():
            print("\n❌ Échec création database")
            return False
        
        # Étape 3: Test Connection
        self.test_database_connection()
        
        # Étape 4: Create Dataset
        if not self.create_dataset():
            print("\n❌ Échec création dataset")
            return False
        
        # Étape 5: Create Charts
        if not self.create_all_charts():
            print("\n⚠️ Tous les charts n'ont pas pu être créés")
        
        # Étape 6: Create Dashboard
        if not self.create_dashboard():
            print("\n❌ Échec création dashboard")
            return False
        
        return True
    
    def print_summary(self):
        """Affiche le résumé"""
        print("\n" + "="*60)
        print("✅ SUPERSET PEUPLÉ AVEC SUCCÈS!")
        print("="*60)
        print(f"\n📊 Database ID: {self.database_id}")
        print(f"📋 Dataset ID: {self.dataset_id}")
        print(f"📈 Charts créés: {len(self.chart_ids)}")
        for name, chart_id in self.chart_ids.items():
            print(f"   - {name}: {chart_id}")
        print(f"🎨 Dashboard ID: {self.dashboard_id}")
        print(f"\n🌐 URL Dashboard: {self.base_url}/superset/dashboard/{self.dashboard_id}/")
        print(f"🔐 Login: admin / admin")
        print("\n" + "="*60)


def main():
    """Fonction principale"""
    print("""
╔════════════════════════════════════════════════════════════╗
║     SUPERSET POPULATION AUTOMATIQUE - PHASE 3              ║
║                                                            ║
║  Ce script va créer automatiquement:                       ║
║    - Connexion PostgreSQL Business DB                      ║
║    - Dataset customers                                     ║
║    - 5 Charts (Big Number, Gauges, Bar Chart)             ║
║    - 1 Dashboard professionnel                             ║
║                                                            ║
║  Durée estimée: 30-60 secondes                             ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    populator = SupersetPopulator(base_url="http://localhost:8088")
    
    try:
        success = populator.populate()
        
        if success:
            populator.print_summary()
            print("\n✅ TERMINÉ! Vous pouvez maintenant accéder à votre dashboard:")
            print(f"   👉 http://localhost:8088/superset/dashboard/{populator.dashboard_id}/")
            return 0
        else:
            print("\n❌ La population a échoué. Consultez les logs ci-dessus.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
