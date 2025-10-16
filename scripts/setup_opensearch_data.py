#!/usr/bin/env python3
"""
Setup OpenSearch data - 100% compatible with Elasticsearch
Populate OpenSearch with test data for Dremio integration
"""

from opensearchpy import OpenSearch, helpers
from datetime import datetime, timedelta
import random
import json

# OpenSearch configuration (same as Elasticsearch)
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200

# Create OpenSearch client
client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False
)

def create_index_if_not_exists(index_name, mappings):
    """Create index with mappings if it doesn't exist"""
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body={'mappings': mappings})
        print(f"✅ Created index: {index_name}")
    else:
        print(f"ℹ️  Index already exists: {index_name}")

def populate_application_logs():
    """Populate application_logs index"""
    print("\n📝 Populating application_logs...")
    
    mappings = {
        'properties': {
            'log_timestamp': {'type': 'date'},
            'level': {'type': 'keyword'},
            'message': {'type': 'text'},
            'service': {'type': 'keyword'},
            'status_code': {'type': 'integer'},
            'duration_ms': {'type': 'float'},
            'user_id': {'type': 'keyword'}
        }
    }
    
    create_index_if_not_exists('application_logs', mappings)
    
    # Generate 500 log entries
    levels = ['INFO', 'WARN', 'ERROR', 'DEBUG']
    services = ['api-gateway', 'user-service', 'payment-service', 'order-service']
    messages = [
        'Request processed successfully',
        'Database query executed',
        'Cache miss - fetching from database',
        'API rate limit exceeded',
        'Authentication successful',
        'Connection timeout',
        'Invalid request parameters',
        'Payment processed'
    ]
    
    logs = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(500):
        timestamp = base_time + timedelta(minutes=i*20)
        
        log = {
            '_index': 'application_logs',
            '_source': {
                'log_timestamp': timestamp.isoformat(),
                'level': random.choice(levels),
                'message': random.choice(messages),
                'service': random.choice(services),
                'status_code': random.choice([200, 201, 400, 404, 500]),
                'duration_ms': round(random.uniform(10, 500), 2),
                'user_id': f'user_{random.randint(1000, 9999)}'
            }
        }
        logs.append(log)
    
    # Bulk insert
    helpers.bulk(client, logs)
    print(f"✅ Inserted {len(logs)} application logs")

def populate_user_events():
    """Populate user_events index"""
    print("\n📊 Populating user_events...")
    
    mappings = {
        'properties': {
            'event_timestamp': {'type': 'date'},
            'event_type': {'type': 'keyword'},
            'user_id': {'type': 'keyword'},
            'session_id': {'type': 'keyword'},
            'page_url': {'type': 'keyword'},
            'action': {'type': 'keyword'},
            'properties': {'type': 'object'}
        }
    }
    
    create_index_if_not_exists('user_events', mappings)
    
    # Generate 1000 user events
    event_types = ['page_view', 'click', 'form_submit', 'purchase', 'search']
    pages = ['/home', '/products', '/cart', '/checkout', '/profile']
    actions = ['view', 'click', 'submit', 'complete', 'cancel']
    
    events = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(1000):
        timestamp = base_time + timedelta(minutes=i*45)
        
        event = {
            '_index': 'user_events',
            '_source': {
                'event_timestamp': timestamp.isoformat(),
                'event_type': random.choice(event_types),
                'user_id': f'user_{random.randint(1000, 5000)}',
                'session_id': f'session_{random.randint(10000, 99999)}',
                'page_url': random.choice(pages),
                'action': random.choice(actions),
                'properties': {
                    'browser': random.choice(['Chrome', 'Firefox', 'Safari']),
                    'device': random.choice(['desktop', 'mobile', 'tablet']),
                    'country': random.choice(['US', 'UK', 'FR', 'DE', 'JP'])
                }
            }
        }
        events.append(event)
    
    # Bulk insert
    helpers.bulk(client, events)
    print(f"✅ Inserted {len(events)} user events")

def populate_performance_metrics():
    """Populate performance_metrics index"""
    print("\n📈 Populating performance_metrics...")
    
    mappings = {
        'properties': {
            'metric_timestamp': {'type': 'date'},
            'metric_name': {'type': 'keyword'},
            'metric_value': {'type': 'float'},
            'unit': {'type': 'keyword'},
            'host': {'type': 'keyword'},
            'tags': {'type': 'object'}
        }
    }
    
    create_index_if_not_exists('performance_metrics', mappings)
    
    # Generate 300 performance metrics
    metric_names = ['cpu_usage', 'memory_usage', 'disk_io', 'network_latency', 'error_rate']
    hosts = ['server-1', 'server-2', 'server-3', 'server-4']
    units = {'cpu_usage': 'percent', 'memory_usage': 'MB', 'disk_io': 'MB/s', 
             'network_latency': 'ms', 'error_rate': 'count'}
    
    metrics = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(300):
        timestamp = base_time + timedelta(minutes=i*5)
        metric_name = random.choice(metric_names)
        
        # Generate realistic values based on metric type
        if metric_name == 'cpu_usage':
            value = round(random.uniform(20, 90), 2)
        elif metric_name == 'memory_usage':
            value = round(random.uniform(1000, 8000), 2)
        elif metric_name == 'disk_io':
            value = round(random.uniform(10, 100), 2)
        elif metric_name == 'network_latency':
            value = round(random.uniform(5, 200), 2)
        else:  # error_rate
            value = round(random.uniform(0, 50), 2)
        
        metric = {
            '_index': 'performance_metrics',
            '_source': {
                'metric_timestamp': timestamp.isoformat(),
                'metric_name': metric_name,
                'metric_value': value,
                'unit': units[metric_name],
                'host': random.choice(hosts),
                'tags': {
                    'environment': random.choice(['prod', 'staging', 'dev']),
                    'region': random.choice(['us-east-1', 'eu-west-1', 'ap-southeast-1'])
                }
            }
        }
        metrics.append(metric)
    
    # Bulk insert
    helpers.bulk(client, metrics)
    print(f"✅ Inserted {len(metrics)} performance metrics")

def verify_data():
    """Verify all data was inserted correctly"""
    print("\n🔍 Verifying data...")
    
    indices = ['application_logs', 'user_events', 'performance_metrics']
    total_docs = 0
    
    for index in indices:
        count = client.count(index=index)['count']
        print(f"   {index}: {count} documents")
        total_docs += count
    
    print(f"\n✅ Total: {total_docs} documents indexed in OpenSearch")
    return total_docs

def main():
    print("=" * 70)
    print("🚀 OPENSEARCH DATA SETUP")
    print("=" * 70)
    
    try:
        # Check OpenSearch connection
        info = client.info()
        print(f"\n✅ Connected to OpenSearch {info['version']['number']}")
        print(f"   Cluster: {info['cluster_name']}")
        
        # Populate indices
        populate_application_logs()
        populate_user_events()
        populate_performance_metrics()
        
        # Verify
        total = verify_data()
        
        print("\n" + "=" * 70)
        print("✅ OPENSEARCH DATA SETUP COMPLETE!")
        print("=" * 70)
        print(f"\n📊 {total} documents ready for Dremio integration")
        print("\n📝 Next step: Configure OpenSearch source in Dremio")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n📝 Troubleshooting:")
        print("   1. Check OpenSearch is running: docker ps | grep opensearch")
        print("   2. Check connectivity: curl http://localhost:9200")
        print("   3. Install opensearch-py: pip install opensearch-py")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
