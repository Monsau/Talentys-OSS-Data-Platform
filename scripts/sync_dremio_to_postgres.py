"""
Script pour synchroniser les données Phase 3 de Dremio vers PostgreSQL
Permet à Superset de lire les données via PostgreSQL
"""

import psycopg2
from pyarrow import flight
import json

def connect_dremio_flight():
    """Connexion à Dremio via Arrow Flight"""
    print("🔗 Connexion à Dremio Arrow Flight...")
    try:
        client = flight.FlightClient("grpc://localhost:32010")
        
        # Authentification
        token_pair = client.authenticate_basic_token(b"admin", b"admin123")
        headers = [token_pair]
        
        print("   ✅ Connecté à Dremio")
        return client, headers
    except Exception as e:
        print(f"   ❌ Erreur connexion Dremio: {e}")
        return None, None

def connect_postgres():
    """Connexion à PostgreSQL"""
    print("\n🔗 Connexion à PostgreSQL...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="business_db",
            user="postgres",
            password="postgres123"
        )
        print("   ✅ Connecté à PostgreSQL")
        return conn
    except Exception as e:
        print(f"   ❌ Erreur connexion PostgreSQL: {e}")
        return None

def fetch_from_dremio(client, headers):
    """Récupère les données depuis Dremio"""
    print("\n📥 Récupération des données depuis Dremio...")
    
    sql = 'SELECT * FROM "$scratch".phase3_all_in_one'
    
    try:
        flight_desc = flight.FlightDescriptor.for_command(sql)
        flight_info = client.get_flight_info(flight_desc, headers)
        
        # Récupérer les données
        reader = client.do_get(flight_info.endpoints[0].ticket, headers)
        table = reader.read_all()
        
        print(f"   ✅ {table.num_rows} ligne(s) récupérée(s)")
        return table
    except Exception as e:
        print(f"   ❌ Erreur lecture Dremio: {e}")
        return None

def create_postgres_table(conn):
    """Crée la table dans PostgreSQL"""
    print("\n📋 Création de la table PostgreSQL...")
    
    cursor = conn.cursor()
    
    # Supprimer la table si elle existe
    cursor.execute("DROP TABLE IF EXISTS phase3_dashboard")
    
    # Créer la nouvelle table
    create_table_sql = """
    CREATE TABLE phase3_dashboard (
        id SERIAL PRIMARY KEY,
        total_customers INTEGER,
        postgres_count INTEGER,
        minio_count INTEGER,
        both_sources INTEGER,
        postgres_only INTEGER,
        minio_only INTEGER,
        coverage_rate_pct NUMERIC(5,2),
        email_matches INTEGER,
        email_mismatches INTEGER,
        email_quality_pct NUMERIC(5,2),
        country_matches INTEGER,
        country_mismatches INTEGER,
        country_quality_pct NUMERIC(5,2),
        overall_status VARCHAR(20),
        report_timestamp TIMESTAMP
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("   ✅ Table créée")
    
    cursor.close()

def insert_data(conn, table):
    """Insère les données dans PostgreSQL"""
    print("\n📤 Insertion des données...")
    
    cursor = conn.cursor()
    
    # Convertir Arrow Table en dictionnaire
    data = table.to_pydict()
    num_rows = table.num_rows
    
    insert_sql = """
    INSERT INTO phase3_dashboard (
        total_customers, postgres_count, minio_count,
        both_sources, postgres_only, minio_only,
        coverage_rate_pct, email_matches, email_mismatches,
        email_quality_pct, country_matches, country_mismatches,
        country_quality_pct, overall_status, report_timestamp
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for i in range(num_rows):
        values = (
            int(data['total_customers'][i]),
            int(data['postgres_count'][i]),
            int(data['minio_count'][i]),
            int(data['both_sources'][i]),
            int(data['postgres_only'][i]),
            int(data['minio_only'][i]),
            float(data['coverage_rate_pct'][i]),
            int(data['email_matches'][i]),
            int(data['email_mismatches'][i]),
            float(data['email_quality_pct'][i]),
            int(data['country_matches'][i]),
            int(data['country_mismatches'][i]),
            float(data['country_quality_pct'][i]),
            str(data['overall_status'][i]),
            data['report_timestamp'][i].as_py()
        )
        cursor.execute(insert_sql, values)
    
    conn.commit()
    print(f"   ✅ {num_rows} ligne(s) insérée(s)")
    
    cursor.close()

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     SYNCHRONISATION DREMIO → POSTGRESQL                    ║
║                                                            ║
║  Copie les données Phase 3 de Dremio vers PostgreSQL      ║
║  pour permettre à Superset de les lire facilement          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Connexion Dremio
    client, headers = connect_dremio_flight()
    if not client:
        print("\n❌ Impossible de se connecter à Dremio")
        return 1
    
    # Connexion PostgreSQL
    pg_conn = connect_postgres()
    if not pg_conn:
        print("\n❌ Impossible de se connecter à PostgreSQL")
        return 1
    
    try:
        # Récupérer les données
        table = fetch_from_dremio(client, headers)
        if not table:
            return 1
        
        # Créer la table
        create_postgres_table(pg_conn)
        
        # Insérer les données
        insert_data(pg_conn, table)
        
        print("\n" + "="*60)
        print("✅ SYNCHRONISATION TERMINÉE!")
        print("="*60)
        print("\n📊 Table PostgreSQL créée: phase3_dashboard")
        print("📍 Schema: public")
        print("📍 Database: business_db")
        print("\n✅ Superset peut maintenant lire ces données!")
        
        return 0
        
    finally:
        if pg_conn:
            pg_conn.close()
            print("\n🔌 Connexion PostgreSQL fermée")

if __name__ == "__main__":
    import sys
    sys.exit(main())
