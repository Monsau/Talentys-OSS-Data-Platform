"""
Générateur de données volumineuses pour Dremio Sandbox

Ce script augmente significativement le volume de données pour rendre
la démo plus réaliste et crédible.

Volumes cibles:
- PostgreSQL: 75 → 10,000 commandes (x133)
- Elasticsearch: 1,800 → 20,000 événements (x11)
- MinIO: 550 → 2,000 fichiers Parquet (x4)

Temps d'exécution: ~5-10 minutes

Usage:
    python scripts/generate_volumetric_data.py --scale=10
"""

import random
import datetime
import psycopg2
from elasticsearch import Elasticsearch
from minio import Minio
import pyarrow as pa
import pyarrow.parquet as pq
import io
from faker import Faker
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'business_db',
    'user': 'dbt_user',
    'password': 'dbt_password'
}

ES_CONFIG = {
    'hosts': ['http://localhost:9200']
}

MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False
}

# Initialisation Faker pour données réalistes
fake = Faker()


def generate_customers_pg(count=1000):
    """Génère des clients PostgreSQL avec données réalistes"""
    logger.info(f"[PostgreSQL] Génération de {count} clients...")
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    
    # Supprimer anciennes données
    cursor.execute("TRUNCATE TABLE customers CASCADE")
    
    customers = []
    for i in range(1, count + 1):
        full_name = fake.name()
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else 'Unknown'
        
        customer = (
            i,
            first_name,
            last_name,
            fake.email(),
            fake.phone_number(),
            fake.street_address(),
            fake.city(),
            fake.random_element(['FR', 'US', 'UK', 'DE', 'ES']),
            fake.date_time_between(start_date='-3y', end_date='now')
        )
        customers.append(customer)
    
    # Insertion en batch (plus rapide)
    cursor.executemany(
        """INSERT INTO customers (id, first_name, last_name, email, phone, address, city, country, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        customers
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"[PostgreSQL] {count} clients créés avec succès")
    return count


def generate_orders_pg(customer_count=1000, orders_per_customer=(5, 20)):
    """Génère des commandes PostgreSQL avec saisonnalité"""
    logger.info(f"[PostgreSQL] Génération de commandes (5-20 par client)...")
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    
    # Supprimer anciennes commandes (CASCADE pour foreign keys)
    cursor.execute("TRUNCATE TABLE orders CASCADE")
    
    orders = []
    order_id = 1
    
    # Dates avec saisonnalité (pics Q4: Black Friday, Noël)
    def random_date_with_seasonality():
        year = random.choice([2022, 2023, 2024])
        
        # 40% des commandes en Q4 (Oct-Dec)
        if random.random() < 0.4:
            month = random.choice([10, 11, 12])
        else:
            month = random.randint(1, 9)
        
        # Pics spéciaux: Black Friday (24-30 Nov), Noël (15-25 Dec)
        if month == 11 and random.random() < 0.3:
            day = random.randint(24, 30)  # Black Friday week
        elif month == 12 and random.random() < 0.3:
            day = random.randint(15, 25)  # Christmas shopping
        else:
            day = random.randint(1, 28)
        
        return datetime.date(year, month, day)
    
    for customer_id in range(1, customer_count + 1):
        num_orders = random.randint(*orders_per_customer)
        
        for _ in range(num_orders):
            total = round(random.uniform(10, 500), 2)
            discount = round(total * random.uniform(0, 0.15), 2)
            tax = round((total - discount) * 0.20, 2)
            shipping = round(random.uniform(0, 15), 2)
            
            order = (
                order_id,
                customer_id,
                fake.date_time_between_dates(
                    datetime_start=random_date_with_seasonality(),
                    datetime_end=random_date_with_seasonality() + datetime.timedelta(days=1)
                ),
                fake.random_element(['pending', 'completed', 'shipped', 'cancelled']),
                total,
                random.randint(1, 10) if random.random() < 0.3 else None,
                discount,
                tax,
                shipping
            )
            orders.append(order)
            order_id += 1
        
        # Commit par batch de 1000 pour performance
        if len(orders) >= 1000:
            cursor.executemany(
                """INSERT INTO orders (id, customer_id, order_date, status, total_amount, promotion_id, discount_amount, tax_amount, shipping_cost)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                orders
            )
            conn.commit()
            logger.info(f"   [Batch] {len(orders)} commandes insérées...")
            orders = []
    
    # Dernier batch
    if orders:
        cursor.executemany(
            """INSERT INTO orders (id, customer_id, order_date, status, total_amount, promotion_id, discount_amount, tax_amount, shipping_cost)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            orders
        )
        conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    logger.info(f"[PostgreSQL] {total} commandes créées avec succès")
    return total


def generate_elasticsearch_logs(count=10000):
    """Génère des logs applicatifs avec patterns réalistes"""
    logger.info(f"[Elasticsearch] Génération de {count} logs...")
    
    es = Elasticsearch(**ES_CONFIG)
    
    # Supprimer ancien index
    if es.indices.exists(index='application_logs'):
        es.indices.delete(index='application_logs')
    
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service', 'notification-service']
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    environments = ['production', 'staging', 'development']
    
    # Patterns de messages par niveau
    messages = {
        'DEBUG': [
            'Request received',
            'Database query executed',
            'Cache hit',
            'Function called'
        ],
        'INFO': [
            'User logged in successfully',
            'Order created',
            'Payment processed',
            'Email sent'
        ],
        'WARNING': [
            'Slow database query (>1s)',
            'High memory usage detected',
            'Rate limit approaching',
            'Retry attempt'
        ],
        'ERROR': [
            'Database connection failed',
            'Payment gateway timeout',
            'Authentication failed',
            'Invalid input data'
        ]
    }
    
    logs = []
    for i in range(count):
        # Distribution réaliste: 60% INFO, 25% DEBUG, 10% WARNING, 5% ERROR
        level = random.choices(
            log_levels,
            weights=[25, 60, 10, 5]
        )[0]
        
        log = {
            'timestamp': datetime.datetime.now() - datetime.timedelta(
                hours=random.randint(0, 720)  # 30 jours
            ),
            'service': random.choice(services),
            'log_level': level,
            'message': random.choice(messages[level]),
            'environment': random.choice(environments),
            'host': f'host-{random.randint(1, 10)}'
        }
        logs.append(log)
        
        # Bulk insert par 500
        if len(logs) >= 500:
            for log in logs:
                es.index(index='application_logs', document=log)
            logger.info(f"   [Batch] {i} logs insérés...")
            logs = []
    
    # Dernier batch
    for log in logs:
        es.index(index='application_logs', document=log)
    
    es.indices.refresh(index='application_logs')
    
    count_result = es.count(index='application_logs')
    logger.info(f"[Elasticsearch] {count_result['count']} logs créés avec succès")
    return count_result['count']


def generate_elasticsearch_events(count=8000):
    """Génère des événements utilisateur avec funnel réaliste"""
    logger.info(f"[Elasticsearch] Génération de {count} événements...")
    
    es = Elasticsearch(**ES_CONFIG)
    
    # Supprimer ancien index
    if es.indices.exists(index='user_events'):
        es.indices.delete(index='user_events')
    
    event_types = ['page_view', 'click', 'conversion', 'purchase']
    pages = ['/home', '/products', '/cart', '/checkout', '/account']
    
    events = []
    user_sessions = {}  # Simuler des sessions réalistes
    
    # Créer 500 sessions utilisateur avec funnel
    for session_id in range(500):
        user_id = f"user_{random.randint(1, 1000)}"
        session_start = datetime.datetime.now() - datetime.timedelta(
            hours=random.randint(0, 720)
        )
        
        # Funnel: 100% page_view → 50% click → 10% conversion → 5% purchase
        session_events = []
        
        # Page view (100%)
        for _ in range(random.randint(3, 10)):
            session_events.append({
                'timestamp': session_start + datetime.timedelta(seconds=len(session_events) * 30),
                'user_id': user_id,
                'session_id': f'session_{session_id}',
                'event_type': 'page_view',
                'page_url': random.choice(pages)
            })
        
        # Click (50%)
        if random.random() < 0.5:
            for _ in range(random.randint(1, 5)):
                session_events.append({
                    'timestamp': session_start + datetime.timedelta(seconds=len(session_events) * 30),
                    'user_id': user_id,
                    'session_id': f'session_{session_id}',
                    'event_type': 'click',
                    'page_url': '/products'
                })
        
        # Conversion (10%)
        if random.random() < 0.1:
            session_events.append({
                'timestamp': session_start + datetime.timedelta(seconds=len(session_events) * 30),
                'user_id': user_id,
                'session_id': f'session_{session_id}',
                'event_type': 'conversion',
                'page_url': '/cart'
            })
            
            # Purchase (5% du total, donc 50% des conversions)
            if random.random() < 0.5:
                session_events.append({
                    'timestamp': session_start + datetime.timedelta(seconds=len(session_events) * 30),
                    'user_id': user_id,
                    'session_id': f'session_{session_id}',
                    'event_type': 'purchase',
                    'page_url': '/checkout'
                })
        
        events.extend(session_events)
        
        # Bulk insert
        if len(events) >= 500:
            for event in events:
                es.index(index='user_events', document=event)
            logger.info(f"   [Batch] {len(events)} événements insérés...")
            events = []
    
    # Dernier batch
    for event in events:
        es.index(index='user_events', document=event)
    
    es.indices.refresh(index='user_events')
    
    count_result = es.count(index='user_events')
    logger.info(f"[Elasticsearch] {count_result['count']} événements créés avec succès")
    return count_result['count']


def generate_elasticsearch_metrics(count=2000):
    """Génère des métriques système avec patterns réalistes"""
    logger.info(f"[Elasticsearch] Génération de {count} métriques...")
    
    es = Elasticsearch(**ES_CONFIG)
    
    # Supprimer ancien index
    if es.indices.exists(index='performance_metrics'):
        es.indices.delete(index='performance_metrics')
    
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service']
    metrics_names = ['cpu_usage', 'memory_usage', 'response_time', 'error_rate']
    
    metrics = []
    for i in range(count):
        metric_name = random.choice(metrics_names)
        
        # Valeurs réalistes par type de métrique
        if metric_name == 'cpu_usage':
            value = random.uniform(20, 85)  # %
        elif metric_name == 'memory_usage':
            value = random.uniform(1024, 8192)  # MB
        elif metric_name == 'response_time':
            value = random.uniform(50, 2000)  # ms
        else:  # error_rate
            value = random.uniform(0, 5)  # %
        
        metric = {
            'timestamp': datetime.datetime.now() - datetime.timedelta(
                minutes=random.randint(0, 43200)  # 30 jours
            ),
            'metric_name': metric_name,
            'service': random.choice(services),
            'metric_value': round(value, 2),
            'environment': 'production',
            'host': f'host-{random.randint(1, 10)}'
        }
        metrics.append(metric)
        
        # Bulk insert
        if len(metrics) >= 500:
            for metric in metrics:
                es.index(index='performance_metrics', document=metric)
            logger.info(f"   [Batch] {i} métriques insérées...")
            metrics = []
    
    # Dernier batch
    for metric in metrics:
        es.index(index='performance_metrics', document=metric)
    
    es.indices.refresh(index='performance_metrics')
    
    count_result = es.count(index='performance_metrics')
    logger.info(f"[Elasticsearch] {count_result['count']} métriques créées avec succès")
    return count_result['count']


def generate_minio_sales(file_count=2000):
    """Génère des fichiers Parquet de ventes dans MinIO"""
    logger.info(f"[MinIO] Génération de {file_count} fichiers Parquet...")
    
    client = Minio(**MINIO_CONFIG)
    
    bucket_name = 'sales-data'
    
    # Supprimer anciens fichiers
    objects = client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        client.remove_object(bucket_name, obj.object_name)
    
    total_generated = 0
    
    # Générer fichiers par jour (2022-2024)
    start_date = datetime.date(2022, 1, 1)
    end_date = datetime.date(2024, 12, 31)
    current_date = start_date
    
    while current_date <= end_date and total_generated < file_count:
        year = current_date.year
        month = current_date.month
        day = current_date.day
        
        # Nombre de ventes par jour (saisonnalité)
        if month in [11, 12]:  # Q4: Black Friday, Noël
            num_sales = random.randint(50, 150)
        elif month in [1, 2]:  # Q1: Soldes
            num_sales = random.randint(30, 80)
        else:
            num_sales = random.randint(20, 50)
        
        # Créer données Parquet
        sales_data = {
            'sale_id': [f'sale_{total_generated}_{i}' for i in range(num_sales)],
            'customer_id': [random.randint(1, 1000) for _ in range(num_sales)],
            'product_id': [random.randint(1, 500) for _ in range(num_sales)],
            'amount': [round(random.uniform(10, 500), 2) for _ in range(num_sales)],
            'quantity': [random.randint(1, 5) for _ in range(num_sales)],
            'sale_date': [current_date for _ in range(num_sales)],
            'year': [year for _ in range(num_sales)],
            'month': [month for _ in range(num_sales)],
            'day': [day for _ in range(num_sales)]
        }
        
        # Convertir en Parquet
        table = pa.table(sales_data)
        parquet_buffer = io.BytesIO()
        pq.write_table(table, parquet_buffer, compression='snappy')
        parquet_buffer.seek(0)
        
        # Upload vers MinIO
        object_name = f'year={year}/month={month:02d}/day={day:02d}/sales_{current_date.strftime("%Y%m%d")}.parquet'
        client.put_object(
            bucket_name,
            object_name,
            data=parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        
        total_generated += 1
        current_date += datetime.timedelta(days=1)
        
        if total_generated % 100 == 0:
            logger.info(f"   [Batch] {total_generated} fichiers générés...")
    
    logger.info(f"[MinIO] {total_generated} fichiers Parquet créés avec succès")
    return total_generated


def main():
    """Fonction principale"""
    logger.info("="*60)
    logger.info("GENERATEUR DE DONNEES VOLUMINEUSES")
    logger.info("="*60)
    
    start_time = datetime.datetime.now()
    
    try:
        # PostgreSQL
        logger.info("\n[PostgreSQL] Starting data generation")
        customers_count = generate_customers_pg(count=1000)
        orders_count = generate_orders_pg(customer_count=1000, orders_per_customer=(5, 20))
        
        # Elasticsearch
        logger.info("\n[Elasticsearch] Starting data generation")
        logs_count = generate_elasticsearch_logs(count=10000)
        events_count = generate_elasticsearch_events(count=8000)
        metrics_count = generate_elasticsearch_metrics(count=2000)
        
        # MinIO
        logger.info("\n[MinIO] Starting data generation")
        files_count = generate_minio_sales(file_count=1095)  # 3 ans de données
        
        # Résumé
        logger.info("\n" + "="*60)
        logger.info("GENERATION TERMINEE AVEC SUCCES")
        logger.info("="*60)
        logger.info(f"PostgreSQL:")
        logger.info(f"  - Clients: {customers_count}")
        logger.info(f"  - Commandes: {orders_count}")
        logger.info(f"Elasticsearch:")
        logger.info(f"  - Logs: {logs_count}")
        logger.info(f"  - Evenements: {events_count}")
        logger.info(f"  - Metriques: {metrics_count}")
        logger.info(f"MinIO:")
        logger.info(f"  - Fichiers Parquet: {files_count}")
        logger.info(f"\nTOTAL: {customers_count + orders_count + logs_count + events_count + metrics_count + files_count} records")
        
        elapsed = datetime.datetime.now() - start_time
        logger.info(f"Temps d'execution: {elapsed}")
        
    except Exception as e:
        logger.error(f"ERREUR: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
