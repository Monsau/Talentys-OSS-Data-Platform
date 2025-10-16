"""
Script de synchronisation Dremio → PostgreSQL en temps réel
Maintient PostgreSQL comme proxy vers Dremio (source de vérité)
"""

import psycopg2
from pyarrow import flight
import time
import schedule
from datetime import datetime

class DremioPostgresSync:
    """Synchronise les données de Dremio vers PostgreSQL"""
    
    def __init__(self):
        self.dremio_client = None
        self.dremio_headers = None
        self.pg_conn = None
        
    def connect_dremio(self):
        """Connexion à Dremio via Arrow Flight"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔗 Connexion à Dremio...")
        try:
            self.dremio_client = flight.FlightClient("grpc://localhost:32010")
            token_pair = self.dremio_client.authenticate_basic_token(b"admin", b"admin123")
            self.dremio_headers = [token_pair]
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ✅ Connecté à Dremio")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ❌ Erreur: {e}")
            return False
    
    def connect_postgres(self):
        """Connexion à PostgreSQL"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔗 Connexion à PostgreSQL...")
        try:
            self.pg_conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="business_db",
                user="postgres",
                password="postgres123"
            )
            self.pg_conn.autocommit = False
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ✅ Connecté à PostgreSQL")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ❌ Erreur: {e}")
            return False
    
    def fetch_from_dremio(self, sql_query):
        """Récupère les données depuis Dremio"""
        try:
            flight_desc = flight.FlightDescriptor.for_command(sql_query)
            
            # Créer les options d'appel avec les headers
            options = flight.FlightCallOptions(headers=self.dremio_headers)
            
            # Obtenir les informations de vol
            flight_info = self.dremio_client.get_flight_info(flight_desc, options)
            
            # Récupérer les données
            reader = self.dremio_client.do_get(flight_info.endpoints[0].ticket, options)
            table = reader.read_all()
            return table
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ❌ Erreur lecture Dremio: {e}")
            return None
    
    def sync_phase3_all_in_one(self):
        """Synchronise la vue phase3_all_in_one de Dremio vers PostgreSQL"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 SYNC: phase3_all_in_one")
        
        # Récupérer depuis Dremio (SOURCE DE VÉRITÉ)
        sql = 'SELECT * FROM "$scratch".phase3_all_in_one'
        table = self.fetch_from_dremio(sql)
        
        if not table:
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ❌ Impossible de récupérer les données")
            return False
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}]    📥 {table.num_rows} ligne(s) récupérée(s) depuis Dremio")
        
        # Créer/Recréer la table dans PostgreSQL
        cursor = self.pg_conn.cursor()
        
        try:
            # DROP & CREATE
            cursor.execute("DROP TABLE IF EXISTS dremio_phase3_all_in_one CASCADE")
            
            create_table_sql = """
            CREATE TABLE dremio_phase3_all_in_one (
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
                report_timestamp TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_sql)
            
            # Insérer les données
            data = table.to_pydict()
            num_rows = table.num_rows
            
            insert_sql = """
            INSERT INTO dremio_phase3_all_in_one (
                total_customers, postgres_count, minio_count,
                both_sources, postgres_only, minio_only,
                coverage_rate_pct, email_matches, email_mismatches,
                email_quality_pct, country_matches, country_mismatches,
                country_quality_pct, overall_status, report_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for i in range(num_rows):
                # Convertir le timestamp
                timestamp_val = data['report_timestamp'][i]
                if hasattr(timestamp_val, 'as_py'):
                    timestamp_val = timestamp_val.as_py()
                
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
                    timestamp_val
                )
                cursor.execute(insert_sql, values)
            
            self.pg_conn.commit()
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ✅ {num_rows} ligne(s) synchronisée(s)")
            
            # Créer une vue pour Superset
            cursor.execute("DROP VIEW IF EXISTS superset_phase3_dashboard CASCADE")
            cursor.execute("""
            CREATE VIEW superset_phase3_dashboard AS
            SELECT 
                total_customers,
                postgres_count,
                minio_count,
                both_sources,
                postgres_only,
                minio_only,
                coverage_rate_pct,
                email_matches,
                email_mismatches,
                email_quality_pct,
                country_matches,
                country_mismatches,
                country_quality_pct,
                overall_status,
                report_timestamp,
                synced_at,
                'Dremio ($scratch.phase3_all_in_one)' as source
            FROM dremio_phase3_all_in_one
            """)
            self.pg_conn.commit()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ✅ Vue superset_phase3_dashboard créée")
            
            cursor.close()
            return True
            
        except Exception as e:
            self.pg_conn.rollback()
            print(f"[{datetime.now().strftime('%H:%M:%S')}]    ❌ Erreur: {e}")
            cursor.close()
            return False
    
    def sync_all(self):
        """Synchronise toutes les vues"""
        print("\n" + "="*60)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 SYNCHRONISATION DREMIO → POSTGRESQL")
        print("="*60)
        
        if not self.dremio_client:
            if not self.connect_dremio():
                return False
        
        if not self.pg_conn or self.pg_conn.closed:
            if not self.connect_postgres():
                return False
        
        # Synchroniser phase3_all_in_one
        success = self.sync_phase3_all_in_one()
        
        if success:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ SYNCHRONISATION TERMINÉE")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Source de vérité: Dremio")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Vue accessible: public.superset_phase3_dashboard")
        else:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ ÉCHEC DE LA SYNCHRONISATION")
        
        return success
    
    def run_continuous(self, interval_minutes=5):
        """Exécute la synchronisation en continu"""
        print(f"""
╔════════════════════════════════════════════════════════════╗
║     SYNCHRONISATION CONTINUE DREMIO → POSTGRESQL           ║
║                                                            ║
║  Source de vérité: Dremio                                  ║
║  Proxy: PostgreSQL                                         ║
║  Intervalle: {interval_minutes} minutes                              ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        # Première synchronisation immédiate
        self.sync_all()
        
        # Planifier les synchronisations suivantes
        schedule.every(interval_minutes).minutes.do(self.sync_all)
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⏰ Synchronisation automatique activée (toutes les {interval_minutes} min)")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💡 Appuyez sur Ctrl+C pour arrêter")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Arrêt de la synchronisation")
            if self.pg_conn and not self.pg_conn.closed:
                self.pg_conn.close()
    
    def close(self):
        """Ferme les connexions"""
        if self.pg_conn and not self.pg_conn.closed:
            self.pg_conn.close()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 Connexions fermées")


def main():
    """Fonction principale"""
    import sys
    
    sync = DremioPostgresSync()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Mode continu
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        sync.run_continuous(interval_minutes=interval)
    else:
        # Mode one-shot
        try:
            success = sync.sync_all()
            sync.close()
            return 0 if success else 1
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
