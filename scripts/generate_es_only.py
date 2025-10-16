#!/usr/bin/env python3
"""
Generateur Elasticsearch uniquement - 20,000 records
Version rapide et optimisee
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import random
import datetime
import uuid

ES_CONFIG = {
    'hosts': ['http://localhost:9200'],
    'verify_certs': False
}

def generate_application_logs(count=10000):
    """Genere logs applicatifs"""
    print(f"[1/3] Generation de {count} logs applicatifs...")
    
    es = Elasticsearch(**ES_CONFIG)
    
    # Supprimer ancien index
    if es.indices.exists(index='application_logs'):
        es.indices.delete(index='application_logs')
        print("   [Clean] Index application_logs supprime")
    
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service', 'notification-service']
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    level_weights = [0.25, 0.60, 0.10, 0.05]  # Distribution realiste
    
    messages = {
        'DEBUG': ['Request received', 'Query executed', 'Cache hit', 'Function called'],
        'INFO': ['User logged in', 'Order created', 'Payment processed', 'Email sent'],
        'WARNING': ['Slow query (>1s)', 'High memory', 'Rate limit approaching', 'Retry attempt'],
        'ERROR': ['Connection failed', 'Invalid input', 'Timeout', 'Database error']
    }
    
    # Generation bulk
    actions = []
    for i in range(count):
        level = random.choices(log_levels, weights=level_weights)[0]
        service = random.choice(services)
        
        timestamp = datetime.datetime.now() - datetime.timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        doc = {
            'timestamp': timestamp.isoformat(),
            'level': level,
            'service': service,
            'message': random.choice(messages[level]),
            'request_id': str(uuid.uuid4()),
            'user_id': random.randint(1, 1000) if random.random() > 0.3 else None,
            'duration_ms': random.randint(10, 5000) if level != 'ERROR' else None,
            'environment': random.choice(['production', 'staging']),
            'host': f"app-{random.randint(1, 10)}"
        }
        
        actions.append({
            '_index': 'application_logs',
            '_source': doc
        })
        
        # Bulk insert par batch de 1000
        if len(actions) >= 1000:
            bulk(es, actions)
            print(f"   [Batch] {len(actions)} logs inseres...")
            actions = []
    
    # Dernier batch
    if actions:
        bulk(es, actions)
    
    es.indices.refresh(index='application_logs')
    count_result = es.count(index='application_logs')
    print(f"[OK] {count_result['count']} logs crees")
    return count_result['count']


def generate_user_events(count=8000):
    """Genere evenements utilisateur (funnel)"""
    print(f"[2/3] Generation de {count} evenements utilisateur...")
    
    es = Elasticsearch(**ES_CONFIG)
    
    if es.indices.exists(index='user_events'):
        es.indices.delete(index='user_events')
        print("   [Clean] Index user_events supprime")
    
    event_types = ['page_view', 'click', 'conversion', 'purchase']
    pages = ['/home', '/products', '/product/123', '/cart', '/checkout', '/account']
    
    actions = []
    session_id = 1
    
    # Generer 500 sessions avec funnel realiste
    num_sessions = 500
    events_per_session = count // num_sessions
    
    for _ in range(num_sessions):
        session_start = datetime.datetime.now() - datetime.timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23)
        )
        
        user_id = random.randint(1, 1000)
        current_time = session_start
        
        # Funnel: 100% page_view -> 50% click -> 10% conversion -> 5% purchase
        num_events = random.randint(events_per_session - 5, events_per_session + 5)
        
        for i in range(num_events):
            # Progression funnel
            if i == 0:
                event_type = 'page_view'
                page = '/home'
            elif i < num_events * 0.5:
                event_type = random.choice(['page_view', 'click'])
                page = random.choice(pages)
            elif i < num_events * 0.9:
                event_type = random.choice(['click', 'conversion'])
                page = random.choice(['/products', '/product/123', '/cart'])
            else:
                event_type = random.choice(['conversion', 'purchase'])
                page = random.choice(['/cart', '/checkout'])
            
            current_time += datetime.timedelta(seconds=random.randint(5, 120))
            
            doc = {
                'timestamp': current_time.isoformat(),
                'event_type': event_type,
                'user_id': user_id,
                'session_id': f"session_{session_id}",
                'page': page,
                'referrer': random.choice(['google', 'facebook', 'direct', 'email']) if i == 0 else None,
                'device': random.choice(['desktop', 'mobile', 'tablet']),
                'browser': random.choice(['chrome', 'firefox', 'safari', 'edge']),
                'country': random.choice(['FR', 'US', 'UK', 'DE', 'ES'])
            }
            
            actions.append({
                '_index': 'user_events',
                '_source': doc
            })
            
            if len(actions) >= 1000:
                bulk(es, actions)
                print(f"   [Batch] {len(actions)} evenements inseres...")
                actions = []
        
        session_id += 1
    
    if actions:
        bulk(es, actions)
    
    es.indices.refresh(index='user_events')
    count_result = es.count(index='user_events')
    print(f"[OK] {count_result['count']} evenements crees")
    return count_result['count']


def generate_performance_metrics(count=2000):
    """Genere metriques systeme"""
    print(f"[3/3] Generation de {count} metriques performance...")
    
    es = Elasticsearch(**ES_CONFIG)
    
    if es.indices.exists(index='performance_metrics'):
        es.indices.delete(index='performance_metrics')
        print("   [Clean] Index performance_metrics supprime")
    
    metric_types = ['cpu_usage', 'memory_usage', 'response_time', 'error_rate']
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service']
    
    actions = []
    for i in range(count):
        metric_type = random.choice(metric_types)
        
        # Valeurs realistes par type
        if metric_type == 'cpu_usage':
            value = random.uniform(10, 90)
            unit = 'percent'
        elif metric_type == 'memory_usage':
            value = random.uniform(40, 85)
            unit = 'percent'
        elif metric_type == 'response_time':
            value = random.uniform(50, 2000)
            unit = 'ms'
        else:  # error_rate
            value = random.uniform(0, 5)
            unit = 'percent'
        
        timestamp = datetime.datetime.now() - datetime.timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        doc = {
            'timestamp': timestamp.isoformat(),
            'metric_type': metric_type,
            'value': round(value, 2),
            'unit': unit,
            'service': random.choice(services),
            'host': f"app-{random.randint(1, 10)}",
            'environment': random.choice(['production', 'staging'])
        }
        
        actions.append({
            '_index': 'performance_metrics',
            '_source': doc
        })
        
        if len(actions) >= 1000:
            bulk(es, actions)
            print(f"   [Batch] {len(actions)} metriques inserees...")
            actions = []
    
    if actions:
        bulk(es, actions)
    
    es.indices.refresh(index='performance_metrics')
    count_result = es.count(index='performance_metrics')
    print(f"[OK] {count_result['count']} metriques creees")
    return count_result['count']


if __name__ == '__main__':
    print("=" * 60)
    print("GENERATEUR ELASTICSEARCH - Version Rapide")
    print("=" * 60)
    print()
    
    try:
        logs = generate_application_logs(10000)
        events = generate_user_events(8000)
        metrics = generate_performance_metrics(2000)
        
        print()
        print("=" * 60)
        print("SUCCES - Elasticsearch alimente")
        print("=" * 60)
        print(f"Logs applicatifs: {logs}")
        print(f"Evenements user:  {events}")
        print(f"Metriques perf:   {metrics}")
        print(f"Total:            {logs + events + metrics} records")
        print()
        print("Verification:")
        print("  curl http://localhost:9200/_cat/indices?v")
        print()
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
