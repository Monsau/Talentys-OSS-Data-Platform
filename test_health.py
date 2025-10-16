#!/usr/bin/env python3
"""
Script de test des connexions pour l'environnement Dremio complet.

Teste toutes les connexions et affiche un rapport de santé.
"""

import requests
import psycopg2
import json
import time
from datetime import datetime

def test_service(name, url, expected_status=200, timeout=5):
    """Test générique d'un service HTTP"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == expected_status:
            return True, f"✅ {name}: OK"
        else:
            return False, f"❌ {name}: Status {response.status_code}"
    except Exception as e:
        return False, f"❌ {name}: {str(e)}"

def test_postgres():
    """Test connexion PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="business_data",
            user="business_user", 
            password="business_password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        count = cursor.fetchone()[0]
        conn.close()
        return True, f"✅ PostgreSQL: OK ({count} customers)"
    except Exception as e:
        return False, f"❌ PostgreSQL: {str(e)}"

def test_dremio_api():
    """Test API Dremio"""
    try:
        # Test de base
        response = requests.get("http://localhost:9047/apiv2/information", timeout=10)
        if response.status_code == 200:
            info = response.json()
            version = info.get("version", "unknown")
            return True, f"✅ Dremio API: OK (v{version})"
        else:
            return False, f"❌ Dremio API: Status {response.status_code}"
    except Exception as e:
        return False, f"❌ Dremio API: {str(e)}"

def main():
    """Tests de santé complets"""
    print("=" * 60)
    print("🔍 TESTS DE SANTÉ - ENVIRONNEMENT DREMIO")
    print("=" * 60)
    print(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tests des services
    tests = [
        # Format: (function, args) ou (test_service, args)
        (test_service, "Dremio UI", "http://localhost:9047"),
        (test_service, "MinIO API", "http://localhost:9000/minio/health/live"),
        (test_service, "MinIO Console", "http://localhost:9001"),
        (test_service, "OpenMetadata", "http://localhost:8585/health"),
        (test_service, "Elasticsearch", "http://localhost:9200"),
        (test_service, "Airflow", "http://localhost:8080/health", 200, 10),
        (test_service, "Polaris", "http://localhost:8181/api/catalog/v1/config"),
        (test_postgres, ),
        (test_dremio_api, )
    ]
    
    results = []
    success_count = 0
    
    for test in tests:
        if len(test) == 2:  # Function without args
            func, args = test
            success, message = func()
        else:  # test_service with args
            func = test[0]
            args = test[1:]
            success, message = func(*args)
        
        results.append((success, message))
        if success:
            success_count += 1
        print(message)
    
    print()
    print("=" * 60)
    print(f"📊 RÉSUMÉ: {success_count}/{len(results)} services OK")
    
    if success_count == len(results):
        print("🎉 Tous les services sont opérationnels !")
        print()
        print("🚀 Prochaines étapes :")
        print("1. Accéder à Dremio: http://localhost:9047 (admin/admin123)")
        print("2. Configurer sources dans Dremio")
        print("3. Tester sync: python scripts/auto-sync-dremio-openmetadata.py")
    else:
        print("⚠️  Certains services ont des problèmes")
        print("Vérifiez les logs avec: docker-compose logs [service]")
    
    print("=" * 60)
    
    # Sauvegarder rapport
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "successful_tests": success_count,
        "success_rate": (success_count / len(results)) * 100,
        "results": [{"success": r[0], "message": r[1]} for r in results]
    }
    
    with open(f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return success_count == len(results)

if __name__ == '__main__':
    main()