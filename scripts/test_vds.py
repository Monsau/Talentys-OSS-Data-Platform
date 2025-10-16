#!/usr/bin/env python3
"""
Script de test des VDS créés
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DREMIO_URL = "http://localhost:9047"

def login():
    """Connexion à Dremio"""
    payload = {"userName": "admin", "password": "admin123"}
    response = requests.post(f"{DREMIO_URL}/apiv2/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"Échec de connexion: {response.status_code}")

def execute_query(token, sql, description):
    """Exécuter une requête SQL"""
    payload = {"sql": sql}
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    
    response = requests.post(f"{DREMIO_URL}/apiv2/sql", headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        rows = result.get('rows', [])
        logger.info(f"✓ {description}: {len(rows)} résultats")
        return True, rows
    else:
        logger.error(f"❌ {description}: {response.status_code} - {response.text[:200]}")
        return False, []

def main():
    logger.info("🧪 TEST DES VDS CREES")
    
    token = login()
    
    test_queries = [
        ("SELECT COUNT(*) as total FROM raw.customers", "Test VDS raw.customers"),
        ("SELECT COUNT(*) as total FROM raw.orders", "Test VDS raw.orders"), 
        ("SELECT category, total_revenue FROM analytics.sales_by_category LIMIT 3", "Test VDS analytics.sales_by_category"),
        ("SELECT full_name, customer_segment, total_spent FROM analytics.customer_metrics LIMIT 3", "Test VDS analytics.customer_metrics"),
        ("SELECT * FROM marts.executive_summary", "Test VDS marts.executive_summary")
    ]
    
    success_count = 0
    for sql, description in test_queries:
        success, rows = execute_query(token, sql, description)
        if success and rows:
            logger.info(f"   Échantillon: {rows[0] if rows else 'Aucune donnée'}")
            success_count += 1
    
    logger.info(f"\n✅ TESTS TERMINES: {success_count}/{len(test_queries)} VDS fonctionnels")
    
    if success_count == len(test_queries):
        logger.info("🎯 TOUS LES VDS SONT OPERATIONNELS!")
        return True
    else:
        logger.warning("⚠️ Quelques VDS ont des problèmes")
        return False

if __name__ == "__main__":
    main()