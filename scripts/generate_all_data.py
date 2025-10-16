#!/usr/bin/env python3
"""
🎲 Data Generation - Consolidated Script
Generate all test data for PostgreSQL, Elasticsearch, and MinIO
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "output_dir": Path("generated_data"),
    "volumes": {
        "customers": 1000,
        "orders": 10000,
        "es_logs": 20000,
        "es_events": 20000,
        "es_metrics": 20000,
        "minio_sales": 50000,
    }
}


# ============================================================================
# GENERATORS
# ============================================================================

def generate_customers(count: int) -> List[Dict]:
    """Generate customer records"""
    print(f"📊 Generating {count:,} customers...")
    
    customers = []
    for i in range(1, count + 1):
        customers.append({
            "customer_id": i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "city": fake.city(),
            "country": fake.country(),
            "registration_date": fake.date_between(start_date='-2y', end_date='today').isoformat()
        })
    
    return customers


def generate_orders(count: int, customer_ids: List[int]) -> List[Dict]:
    """Generate order records"""
    print(f"📊 Generating {count:,} orders...")
    
    orders = []
    statuses = ['completed', 'pending', 'cancelled', 'processing']
    
    for i in range(1, count + 1):
        orders.append({
            "order_id": i,
            "customer_id": random.choice(customer_ids),
            "order_date": fake.date_between(start_date='-1y', end_date='today').isoformat(),
            "amount": round(random.uniform(10, 5000), 2),
            "status": random.choice(statuses)
        })
    
    return orders


def generate_es_logs(count: int) -> List[Dict]:
    """Generate Elasticsearch application logs"""
    print(f"📊 Generating {count:,} ES application logs...")
    
    logs = []
    levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service', 'user-service']
    environments = ['production', 'staging', 'development']
    
    for _ in range(count):
        level = random.choice(levels)
        logs.append({
            "timestamp": fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
            "level": level,
            "service": random.choice(services),
            "message": fake.sentence(),
            "request_id": fake.uuid4(),
            "status_code": 500 if level == 'ERROR' else random.choice([200, 201, 400, 404]),
            "environment": random.choice(environments),
            "host": f"server-{random.randint(1, 10)}"
        })
    
    return logs


def generate_es_events(count: int) -> List[Dict]:
    """Generate Elasticsearch user events"""
    print(f"📊 Generating {count:,} ES user events...")
    
    events = []
    event_types = ['page_view', 'click', 'purchase', 'add_to_cart', 'search']
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
    devices = ['desktop', 'mobile', 'tablet']
    actions = ['view', 'click', 'submit', 'scroll', 'hover']
    countries = ['US', 'UK', 'FR', 'DE', 'JP', 'CA']
    
    for _ in range(count):
        event_type = random.choice(event_types)
        events.append({
            "timestamp": fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
            "event_type": event_type,
            "session_id": fake.uuid4(),
            "browser": random.choice(browsers),
            "device": random.choice(devices),
            "action": random.choice(actions),
            "page": f"/{fake.word()}/{fake.word()}",
            "country": random.choice(countries),
            "referrer": fake.url() if random.random() > 0.3 else None,
            "properties": json.dumps({
                "product_id": random.randint(1, 1000) if event_type == 'purchase' else None,
                "category": fake.word() if event_type in ['page_view', 'search'] else None
            })
        })
    
    return events


def generate_es_metrics(count: int) -> List[Dict]:
    """Generate Elasticsearch performance metrics"""
    print(f"📊 Generating {count:,} ES performance metrics...")
    
    metrics = []
    metric_types = ['cpu_percent', 'memory_mb', 'disk_io', 'network_latency']
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service', 'database']
    environments = ['production', 'staging']
    units = {'cpu_percent': 'percent', 'memory_mb': 'megabytes', 'disk_io': 'mbps', 'network_latency': 'ms'}
    
    for _ in range(count):
        metric_type = random.choice(metric_types)
        service = random.choice(services)
        
        # Generate realistic values
        if metric_type == 'cpu_percent':
            value = round(random.uniform(10, 95), 2)
        elif metric_type == 'memory_mb':
            value = round(random.uniform(100, 8000), 2)
        elif metric_type == 'disk_io':
            value = round(random.uniform(1, 500), 2)
        else:  # network_latency
            value = round(random.uniform(1, 200), 2)
        
        metrics.append({
            "timestamp": fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
            "metric_type": metric_type,
            "metric_name": f"{service}_{metric_type}",  # For compatibility
            "value": value,
            "metric_value": value,  # Alias
            "service": service,
            "environment": random.choice(environments),
            "host": f"server-{random.randint(1, 20)}",
            "unit": units[metric_type]
        })
    
    return metrics


def generate_minio_sales(count: int) -> List[Dict]:
    """Generate MinIO sales records (Parquet format)"""
    print(f"📊 Generating {count:,} MinIO sales records...")
    
    sales = []
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys']
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa']
    products = {
        'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera'],
        'Clothing': ['T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes'],
        'Home & Garden': ['Furniture', 'Kitchenware', 'Bedding', 'Tools', 'Decor'],
        'Sports': ['Running Shoes', 'Yoga Mat', 'Dumbbell', 'Tennis Racket', 'Bicycle'],
        'Books': ['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography'],
        'Toys': ['Action Figure', 'Board Game', 'Puzzle', 'Doll', 'LEGO Set']
    }
    
    for i in range(1, count + 1):
        category = random.choice(categories)
        product = random.choice(products[category])
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(5, 500), 2)
        discount = round(random.uniform(0, 0.3), 2)
        total = round(quantity * unit_price * (1 - discount), 2)
        
        sales.append({
            "sale_id": f"SALE-{i:06d}",
            "sale_date": fake.date_between(start_date='-1y', end_date='today').isoformat(),
            "category": category,
            "product_name": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "region": random.choice(regions),
            "total_amount": total
        })
    
    return sales


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_to_json(data: List[Dict], filename: str):
    """Export data to JSON file"""
    output_file = CONFIG["output_dir"] / filename
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Exported to {output_file}")


def export_to_csv(data: List[Dict], filename: str):
    """Export data to CSV file"""
    import csv
    
    output_file = CONFIG["output_dir"] / filename
    if not data:
        print(f"⚠️  No data to export to {filename}")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Exported to {output_file}")


def export_summary(stats: Dict):
    """Export generation summary"""
    summary_file = CONFIG["output_dir"] / "GENERATION_SUMMARY.json"
    summary = {
        "generation_date": datetime.now().isoformat(),
        "total_records": sum(stats.values()),
        "breakdown": stats,
        "files_generated": [
            "customers.json",
            "orders.json",
            "es_logs.json",
            "es_events.json",
            "es_metrics.json",
            "minio_sales.json",
        ]
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Summary exported to {summary_file}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main data generation"""
    print("="*70)
    print("🎲 DATA GENERATION - ALL SOURCES")
    print("="*70)
    print()
    
    # Create output directory
    CONFIG["output_dir"].mkdir(exist_ok=True)
    
    stats = {}
    
    # Generate customers
    customers = generate_customers(CONFIG["volumes"]["customers"])
    export_to_json(customers, "customers.json")
    stats["customers"] = len(customers)
    
    # Generate orders
    customer_ids = [c["customer_id"] for c in customers]
    orders = generate_orders(CONFIG["volumes"]["orders"], customer_ids)
    export_to_json(orders, "orders.json")
    stats["orders"] = len(orders)
    
    # Generate Elasticsearch logs
    es_logs = generate_es_logs(CONFIG["volumes"]["es_logs"])
    export_to_json(es_logs, "es_logs.json")
    stats["es_logs"] = len(es_logs)
    
    # Generate Elasticsearch events
    es_events = generate_es_events(CONFIG["volumes"]["es_events"])
    export_to_json(es_events, "es_events.json")
    stats["es_events"] = len(es_events)
    
    # Generate Elasticsearch metrics
    es_metrics = generate_es_metrics(CONFIG["volumes"]["es_metrics"])
    export_to_json(es_metrics, "es_metrics.json")
    stats["es_metrics"] = len(es_metrics)
    
    # Generate MinIO sales
    minio_sales = generate_minio_sales(CONFIG["volumes"]["minio_sales"])
    export_to_json(minio_sales, "minio_sales.json")
    export_to_csv(minio_sales, "minio_sales.csv")
    stats["minio_sales"] = len(minio_sales)
    
    # Export summary
    export_summary(stats)
    
    print("\n" + "="*70)
    print("✅ DATA GENERATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Total records generated: {sum(stats.values()):,}")
    for source, count in stats.items():
        print(f"  • {source}: {count:,}")
    print(f"\n📁 Files saved to: {CONFIG['output_dir'].absolute()}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
