"""Quick Elasticsearch data injection"""
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import random

print("=" * 60)
print("ELASTICSEARCH - INJECTION DE DONNEES")
print("=" * 60)

try:
    es = Elasticsearch(['http://localhost:9200'])
    
    # Vérifier la connexion
    if not es.ping():
        print("❌ Cannot connect to Elasticsearch")
        exit(1)
    
    print("✅ Connected to Elasticsearch\n")
    
    # Index 1: application_logs
    print("1. Creating index: application_logs...")
    index_name = "application_logs"
    
    # Create index if not exists
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
    
    # Insert logs
    log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    services = ["api", "web", "worker", "scheduler"]
    
    for i in range(500):
        doc = {
            "timestamp": datetime.now() - timedelta(hours=random.randint(0, 720)),
            "level": random.choice(log_levels),
            "service": random.choice(services),
            "message": f"Log message {i}",
            "host": f"server-{random.randint(1, 10)}"
        }
        es.index(index=index_name, document=doc)
        
        if (i + 1) % 100 == 0:
            print(f"   Inserted {i + 1} logs...")
    
    print(f"   ✅ {index_name}: 500 documents\n")
    
    # Index 2: user_events
    print("2. Creating index: user_events...")
    index_name = "user_events"
    
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
    
    event_types = ["click", "view", "purchase", "search"]
    
    for i in range(300):
        doc = {
            "timestamp": datetime.now() - timedelta(hours=random.randint(0, 720)),
            "event_type": random.choice(event_types),
            "user_id": random.randint(1, 100),
            "page": f"/page/{random.randint(1, 20)}",
            "duration": random.randint(1, 300)
        }
        es.index(index=index_name, document=doc)
        
        if (i + 1) % 100 == 0:
            print(f"   Inserted {i + 1} events...")
    
    print(f"   ✅ {index_name}: 300 documents\n")
    
    # Index 3: system_metrics
    print("3. Creating index: system_metrics...")
    index_name = "system_metrics"
    
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
    
    for i in range(200):
        doc = {
            "timestamp": datetime.now() - timedelta(minutes=random.randint(0, 1440)),
            "cpu_usage": round(random.uniform(0, 100), 2),
            "memory_usage": round(random.uniform(0, 100), 2),
            "disk_usage": round(random.uniform(0, 100), 2),
            "host": f"server-{random.randint(1, 10)}"
        }
        es.index(index=index_name, document=doc)
        
        if (i + 1) % 100 == 0:
            print(f"   Inserted {i + 1} metrics...")
    
    print(f"   ✅ {index_name}: 200 documents\n")
    
    # Refresh indices
    es.indices.refresh(index="_all")
    
    # Summary
    print("=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print("✅ application_logs: 500 documents")
    print("✅ user_events: 300 documents")
    print("✅ system_metrics: 200 documents")
    print("\n💡 Total: 1000 documents indexés dans Elasticsearch")
    
except Exception as e:
    print(f"❌ Error: {e}")
