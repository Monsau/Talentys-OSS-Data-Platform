#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=31010,
        user='dremio_user',
        password='dremio_pass123',
        database='dremio'
    )
    print("✅ Connexion PostgreSQL réussie")
    
    # Test requête
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as test")
    result = cursor.fetchone()
    print(f"✅ Test requête: {result}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Erreur: {e}")
