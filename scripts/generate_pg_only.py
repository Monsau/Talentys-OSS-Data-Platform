#!/usr/bin/env python3
"""
Generateur rapide PostgreSQL uniquement - 11,000 records
"""

import psycopg2
import random
import datetime
import uuid
from faker import Faker

fake = Faker()

POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'business_db',
    'user': 'dbt_user',
    'password': 'dbt_password'
}

def generate_customers(count=1000):
    """Genere clients PostgreSQL"""
    print(f"[1/2] Generation de {count} clients...")
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE customers CASCADE")
    
    customers = []
    for i in range(1, count + 1):
        full_name = fake.name()
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else 'Unknown'
        
        # Email unique avec UUID pour eviter doublons
        email = f"{first_name.lower()}.{last_name.lower()}.{uuid.uuid4().hex[:8]}@example.com"
        
        customer = (
            i,
            first_name,
            last_name,
            email,
            fake.phone_number(),
            fake.street_address(),
            fake.city(),
            random.choice(['FR', 'US', 'UK', 'DE', 'ES']),
            fake.date_time_between(start_date='-3y', end_date='now')
        )
        customers.append(customer)
    
    cursor.executemany(
        """INSERT INTO customers (id, first_name, last_name, email, phone, address, city, country, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        customers
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"[OK] {count} clients crees")
    return count


def generate_orders(customer_count=1000, orders_per_customer=(5, 15)):
    """Genere commandes PostgreSQL avec saisonnalite"""
    print(f"[2/2] Generation de commandes (5-15 par client)...")
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE orders CASCADE")
    
    orders = []
    order_id = 1
    
    for customer_id in range(1, customer_count + 1):
        num_orders = random.randint(*orders_per_customer)
        
        for _ in range(num_orders):
            # Dates avec saisonnalite Q4
            year = random.choice([2022, 2023, 2024])
            if random.random() < 0.4:  # 40% en Q4
                month = random.choice([10, 11, 12])
            else:
                month = random.randint(1, 9)
            day = random.randint(1, 28)
            
            order_date = datetime.datetime(year, month, day, random.randint(0, 23), random.randint(0, 59))
            
            total = round(random.uniform(10, 500), 2)
            discount = round(total * random.uniform(0, 0.15), 2)
            tax = round((total - discount) * 0.20, 2)
            shipping = round(random.uniform(0, 15), 2)
            
            order = (
                order_id,
                customer_id,
                order_date,
                random.choice(['pending', 'completed', 'shipped', 'cancelled']),
                total,
                None,  # promotion_id (pas de table promotions)
                discount,
                tax,
                shipping
            )
            orders.append(order)
            order_id += 1
        
        # Commit par batch de 1000
        if len(orders) >= 1000:
            cursor.executemany(
                """INSERT INTO orders (id, customer_id, order_date, status, total_amount, promotion_id, discount_amount, tax_amount, shipping_cost)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                orders
            )
            conn.commit()
            print(f"   [Batch] {len(orders)} commandes inserees...")
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
    
    print(f"[OK] {total} commandes creees")
    return total


if __name__ == '__main__':
    print("=" * 60)
    print("GENERATEUR POSTGRESQL - Version Rapide")
    print("=" * 60)
    
    try:
        customers = generate_customers(1000)
        orders = generate_orders(1000, (5, 15))
        
        print()
        print("=" * 60)
        print("SUCCES - PostgreSQL alimente")
        print("=" * 60)
        print(f"Clients: {customers}")
        print(f"Commandes: {orders}")
        print(f"Total: {customers + orders} records")
        print()
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
