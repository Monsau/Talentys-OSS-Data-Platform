import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='business_db',
    user='dbt_user',
    password='dbt_password'
)

cur = conn.cursor()
cur.execute('TRUNCATE TABLE customers CASCADE')
conn.commit()
print('Tables customers et orders videes')
conn.close()
