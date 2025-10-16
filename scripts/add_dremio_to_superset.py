"""
Script pour ajouter une connexion Dremio native à Superset
Utilise le driver sqlalchemy-dremio déjà installé
"""

import requests
import json

def login_superset():
    """Connexion à Superset"""
    session = requests.Session()
    login_url = "http://localhost:8088/api/v1/security/login"
    payload = {
        "username": "admin",
        "password": "admin",
        "provider": "db",
        "refresh": True
    }
    
    response = session.post(login_url, json=payload)
    response.raise_for_status()
    
    token = response.json().get("access_token")
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    
    print("✅ Connecté à Superset")
    return session

def get_csrf_token(session):
    """Récupère le CSRF token"""
    response = session.get("http://localhost:8088/api/v1/security/csrf_token/")
    csrf = response.json().get("result")
    session.headers.update({
        "X-CSRFToken": csrf,
        "Referer": "http://localhost:8088"
    })
    return csrf

def add_dremio_connection(session):
    """Ajoute la connexion Dremio"""
    print("\n📊 Ajout de la connexion Dremio...")
    
    get_csrf_token(session)
    
    # Configuration Dremio avec Flight
    database_config = {
        "database_name": "Dremio Analytics (Arrow Flight)",
        "engine": "dremio",
        "configuration_method": "sqlalchemy_form",
        "sqlalchemy_uri": "dremio+flight://admin:admin123@dremio:32010/dremio?UseEncryption=false",
        "expose_in_sqllab": True,
        "allow_ctas": False,
        "allow_cvas": False,
        "allow_dml": False,
        "extra": json.dumps({
            "engine_params": {
                "connect_args": {
                    "UseSsl": False
                }
            }
        })
    }
    
    try:
        response = session.post(
            "http://localhost:8088/api/v1/database/",
            json=database_config
        )
        
        if response.status_code == 201:
            db_id = response.json().get("id")
            print(f"   ✅ Connexion Dremio créée (ID: {db_id})")
            return db_id
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Essayer sans Flight
            print("\n   🔄 Tentative sans Arrow Flight...")
            database_config["database_name"] = "Dremio Analytics"
            database_config["sqlalchemy_uri"] = "dremio://admin:admin123@dremio:31010/dremio"
            
            response = session.post(
                "http://localhost:8088/api/v1/database/",
                json=database_config
            )
            
            if response.status_code == 201:
                db_id = response.json().get("id")
                print(f"   ✅ Connexion Dremio créée (ID: {db_id})")
                return db_id
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     AJOUT CONNEXION DREMIO À SUPERSET                      ║
║                                                            ║
║  Utilise le driver sqlalchemy-dremio natif                 ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        session = login_superset()
        db_id = add_dremio_connection(session)
        
        if db_id:
            print("\n" + "="*60)
            print("✅ CONNEXION DREMIO AJOUTÉE!")
            print("="*60)
            print(f"\n📊 Database ID: {db_id}")
            print("\n✅ Vous pouvez maintenant créer des datasets depuis Dremio!")
            print("   👉 http://localhost:8088/tablemodelview/list/")
            return 0
        else:
            print("\n❌ Impossible d'ajouter la connexion Dremio")
            print("\nℹ️  La connexion PostgreSQL Business DB fonctionne déjà :")
            print("   👉 http://localhost:8088/superset/dashboard/1/")
            return 1
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
