import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='business_db',
    user='dbt_user',
    password='dbt_password'
)

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM customers")
print(f"Customers: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM orders")
print(f"Orders: {cur.fetchone()[0]}")

conn.close()
