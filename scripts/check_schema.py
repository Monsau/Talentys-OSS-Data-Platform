import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='business_db',
    user='dbt_user',
    password='dbt_password'
)

cur = conn.cursor()
cur.execute("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name IN ('customers', 'orders') 
    ORDER BY table_name, ordinal_position
""")

current_table = None
for row in cur.fetchall():
    if row[0] != current_table:
        print(f"\n{row[0]}:")
        current_table = row[0]
    print(f"  {row[1]}: {row[2]}")

cur.close()
conn.close()
