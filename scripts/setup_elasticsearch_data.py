#!/usr/bin/env python3
"""
Script pour peupler Elasticsearch avec des données d'exemple
- Logs d'applications
- Événements utilisateurs
- Métriques de performance
"""

from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import random
import json

ES_HOST = "localhost:9200"

def create_es_client():
    """Créer le client Elasticsearch avec configuration pour ES 8.x"""
    try:
        print("🔗 Tentative de connexion à Elasticsearch...")
        es = Elasticsearch(
            hosts=['http://localhost:9200'],
            verify_certs=False,
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        
        # Test de connexion
        info = es.info()
        print(f"✅ Connecté à Elasticsearch {info['version']['number']}")
        print(f"   Cluster: {info['cluster_name']}")
        
        return es
    except Exception as e:
        print(f"❌ Erreur de connexion à Elasticsearch")
        print(f"   Type d'erreur: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def create_indices(es):
    """Créer les indices Elasticsearch"""
    print("📊 Création des indices Elasticsearch...")
    
    indices = {
        "application_logs": {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text"},
                    "user_id": {"type": "keyword"},
                    "request_id": {"type": "keyword"},
                    "duration_ms": {"type": "integer"},
                    "status_code": {"type": "integer"}
                }
            }
        },
        "user_events": {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "event_type": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "session_id": {"type": "keyword"},
                    "page": {"type": "keyword"},
                    "action": {"type": "keyword"},
                    "properties": {"type": "object"},
                    "device": {"type": "keyword"},
                    "browser": {"type": "keyword"}
                }
            }
        },
        "performance_metrics": {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "metric_name": {"type": "keyword"},
                    "metric_value": {"type": "float"},
                    "service": {"type": "keyword"},
                    "environment": {"type": "keyword"},
                    "host": {"type": "keyword"},
                    "tags": {"type": "keyword"}
                }
            }
        }
    }
    
    for index_name, index_config in indices.items():
        try:
            if es.indices.exists(index=index_name):
                print(f"ℹ️ Index '{index_name}' existe déjà")
            else:
                es.indices.create(index=index_name, body=index_config)
                print(f"✅ Index '{index_name}' créé")
        except Exception as e:
            print(f"❌ Erreur création index '{index_name}': {e}")

def generate_app_logs(count=500):
    """Générer des logs d'application"""
    services = ["api-gateway", "auth-service", "order-service", "payment-service", "notification-service"]
    levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    messages = [
        "Request processed successfully",
        "Database query executed",
        "Cache miss, fetching from database",
        "Rate limit exceeded",
        "Authentication failed",
        "Payment processed",
        "Order created",
        "Email sent"
    ]
    
    logs = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(count):
        timestamp = base_time + timedelta(minutes=random.randint(0, 10080))  # 7 jours
        
        log = {
            "timestamp": timestamp.isoformat(),
            "level": random.choice(levels),
            "service": random.choice(services),
            "message": random.choice(messages),
            "user_id": f"user_{random.randint(1, 100)}",
            "request_id": f"req_{random.randint(10000, 99999)}",
            "duration_ms": random.randint(10, 5000),
            "status_code": random.choice([200, 201, 400, 401, 403, 404, 500, 503])
        }
        logs.append(log)
    
    return logs

def generate_user_events(count=1000):
    """Générer des événements utilisateurs"""
    event_types = ["page_view", "click", "form_submit", "purchase", "logout"]
    pages = ["/home", "/products", "/cart", "/checkout", "/profile", "/help"]
    actions = ["view", "add_to_cart", "remove_from_cart", "checkout", "search", "filter"]
    devices = ["desktop", "mobile", "tablet"]
    browsers = ["Chrome", "Firefox", "Safari", "Edge"]
    
    events = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(count):
        timestamp = base_time + timedelta(minutes=random.randint(0, 10080))
        
        event = {
            "timestamp": timestamp.isoformat(),
            "event_type": random.choice(event_types),
            "user_id": f"user_{random.randint(1, 100)}",
            "session_id": f"session_{random.randint(1000, 9999)}",
            "page": random.choice(pages),
            "action": random.choice(actions),
            "properties": {
                "product_id": f"prod_{random.randint(1, 50)}" if random.random() > 0.5 else None,
                "value": round(random.uniform(10, 500), 2) if random.random() > 0.7 else None
            },
            "device": random.choice(devices),
            "browser": random.choice(browsers)
        }
        events.append(event)
    
    return events

def generate_performance_metrics(count=300):
    """Générer des métriques de performance"""
    metric_names = [
        "cpu_usage",
        "memory_usage",
        "disk_io",
        "network_throughput",
        "request_count",
        "error_rate",
        "response_time",
        "db_query_time"
    ]
    services = ["api-gateway", "auth-service", "order-service", "payment-service"]
    environments = ["production", "staging", "development"]
    hosts = ["host-01", "host-02", "host-03", "host-04"]
    
    metrics = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(count):
        timestamp = base_time + timedelta(minutes=random.randint(0, 10080))
        
        metric = {
            "timestamp": timestamp.isoformat(),
            "metric_name": random.choice(metric_names),
            "metric_value": round(random.uniform(0, 100), 2),
            "service": random.choice(services),
            "environment": random.choice(environments),
            "host": random.choice(hosts),
            "tags": [random.choice(["monitoring", "alerting", "performance", "capacity"])]
        }
        metrics.append(metric)
    
    return metrics

def bulk_index(es, index_name, documents):
    """Indexer des documents en masse"""
    print(f"\n📝 Indexation dans '{index_name}'...")
    
    from elasticsearch.helpers import bulk
    
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in documents
    ]
    
    try:
        success, failed = bulk(es, actions, raise_on_error=False)
        print(f"✅ {success} documents indexés")
        if failed:
            print(f"⚠️ {len(failed)} documents échoués")
        return success
    except Exception as e:
        print(f"❌ Erreur d'indexation: {e}")
        return 0

def main():
    print("=" * 70)
    print("🔍 SETUP ELASTICSEARCH - DONNÉES D'EXEMPLE")
    print("=" * 70)
    
    try:
        # Créer le client
        es = create_es_client()
        
        # Vérifier la connexion
        if not es.ping():
            print("❌ Impossible de se connecter à Elasticsearch")
            print(f"   Vérifiez que Elasticsearch tourne sur {ES_HOST}")
            return False
        
        print(f"✅ Connexion Elasticsearch établie")
        print(f"   Cluster: {es.info()['cluster_name']}")
        print(f"   Version: {es.info()['version']['number']}")
        
        # Créer les indices
        create_indices(es)
        
        # Générer et indexer les logs d'application
        print("\n📊 Génération des logs d'application...")
        app_logs = generate_app_logs(500)
        bulk_index(es, "application_logs", app_logs)
        
        # Générer et indexer les événements utilisateurs
        print("\n👥 Génération des événements utilisateurs...")
        user_events = generate_user_events(1000)
        bulk_index(es, "user_events", user_events)
        
        # Générer et indexer les métriques de performance
        print("\n📈 Génération des métriques de performance...")
        perf_metrics = generate_performance_metrics(300)
        bulk_index(es, "performance_metrics", perf_metrics)
        
        # Résumé
        print("\n" + "=" * 70)
        print("📋 RÉSUMÉ DES DONNÉES ELASTICSEARCH")
        print("=" * 70)
        
        for index in ["application_logs", "user_events", "performance_metrics"]:
            count = es.count(index=index)['count']
            print(f"✅ {index}: {count} documents")
        
        print(f"\n🌐 Accès Elasticsearch: http://localhost:9200")
        print(f"📊 Kibana (si installé): http://localhost:5601")
        print("\n✅ Setup Elasticsearch terminé avec succès!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    main()
