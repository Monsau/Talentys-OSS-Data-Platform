#!/usr/bin/env python3
"""
Script pour enrichir les sources de données avant l'initialisation complète
Alimente PostgreSQL et MinIO avec des données complètes pour Dremio
"""

import os
import sys
import time
import logging
from pathlib import Path
import subprocess
import requests
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import psycopg2
import psycopg2.extras

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataSourceEnricher:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.postgres_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'business_db',
            'user': 'dbt_user',
            'password': 'dbt_password'
        }
        self.minio_config = {
            'endpoint': 'http://localhost:9000',
            'access_key': 'minio_admin',
            'secret_key': 'minio_password'
        }
        
    def wait_for_services(self):
        """Attendre que les services soient disponibles"""
        services = [
            ('PostgreSQL', 'localhost', 5432),
            ('MinIO', 'localhost', 9000),
            ('Dremio', 'localhost', 9047)
        ]
        
        for service_name, host, port in services:
            logger.info(f"Vérification de {service_name}...")
            max_retries = 30
            for i in range(max_retries):
                try:
                    if service_name == 'PostgreSQL':
                        import socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex((host, port))
                        sock.close()
                        if result == 0:
                            break
                    else:
                        response = requests.get(f"http://{host}:{port}", timeout=5)
                        if response.status_code in [200, 401, 403]:
                            break
                except:
                    pass
                
                if i == max_retries - 1:
                    raise Exception(f"{service_name} non disponible après {max_retries} tentatives")
                    
                logger.info(f"Attente de {service_name}... ({i+1}/{max_retries})")
                time.sleep(10)
            
            logger.info(f"✓ {service_name} disponible")

    def enrich_postgresql(self):
        """Enrichir la base de données PostgreSQL avec des données complètes"""
        logger.info("=== ENRICHISSEMENT POSTGRESQL ===")
        
        try:
            # Connexion à PostgreSQL
            conn = psycopg2.connect(**self.postgres_config)
            cur = conn.cursor()
            
            # Exécuter le script d'enrichissement
            sql_file = self.base_dir.parent / "postgres" / "init" / "02-enrich-business-data.sql"
            if sql_file.exists():
                logger.info(f"Exécution du script: {sql_file}")
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Exécuter le script par blocs pour éviter les erreurs
                statements = sql_content.split(';')
                for i, statement in enumerate(statements):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            cur.execute(statement)
                            conn.commit()
                        except Exception as e:
                            logger.warning(f"Erreur statement {i}: {e}")
                            conn.rollback()
                
                logger.info("✓ Script PostgreSQL exécuté avec succès")
            else:
                logger.error(f"Script non trouvé: {sql_file}")
                
            # Vérifier les données
            cur.execute("SELECT COUNT(*) FROM customers")
            customers_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM orders")
            orders_count = cur.fetchone()[0]
            
            logger.info(f"✓ Données PostgreSQL: {customers_count} clients, {orders_count} commandes")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur enrichissement PostgreSQL: {e}")
            raise

    def setup_minio_buckets(self):
        """Configurer les buckets MinIO et uploader les données"""
        logger.info("=== CONFIGURATION MINIO ===")
        
        try:
            # Connexion à MinIO
            s3_client = boto3.client(
                's3',
                endpoint_url=self.minio_config['endpoint'],
                aws_access_key_id=self.minio_config['access_key'],
                aws_secret_access_key=self.minio_config['secret_key']
            )
            
            # Buckets à créer
            buckets = ['raw-data', 'staging-data', 'analytics-data']
            
            # Créer les buckets
            for bucket in buckets:
                try:
                    s3_client.create_bucket(Bucket=bucket)
                    logger.info(f"✓ Bucket créé: {bucket}")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                        logger.info(f"✓ Bucket existe déjà: {bucket}")
                    else:
                        logger.error(f"Erreur création bucket {bucket}: {e}")
            
            # Uploader les fichiers de données
            sample_data_dir = self.base_dir / "minio" / "sample-data"
            if sample_data_dir.exists():
                files_to_upload = [
                    ('customers_external.csv', 'raw-data', 'external/customers/'),
                    ('transactions_2025.csv', 'raw-data', 'transactions/'),
                    ('products_catalog.csv', 'staging-data', 'products/'),
                    ('inventory_detailed.csv', 'staging-data', 'inventory/'),
                    ('analytics_summary.json', 'analytics-data', 'reports/')
                ]
                
                for filename, bucket, prefix in files_to_upload:
                    file_path = sample_data_dir / filename
                    if file_path.exists():
                        s3_key = f"{prefix}{filename}"
                        s3_client.upload_file(str(file_path), bucket, s3_key)
                        logger.info(f"✓ Fichier uploadé: s3://{bucket}/{s3_key}")
                    else:
                        logger.warning(f"Fichier non trouvé: {file_path}")
            
            logger.info("✓ Configuration MinIO terminée")
            
        except Exception as e:
            logger.error(f"Erreur configuration MinIO: {e}")
            raise

    def verify_data_sources(self):
        """Vérifier que les sources de données sont bien alimentées"""
        logger.info("=== VERIFICATION DES SOURCES ===")
        
        # Vérifier PostgreSQL
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cur = conn.cursor()
            
            tables_to_check = ['customers', 'orders', 'products', 'suppliers', 'categories']
            for table in tables_to_check:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                logger.info(f"✓ PostgreSQL {table}: {count} enregistrements")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur vérification PostgreSQL: {e}")
        
        # Vérifier MinIO
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=self.minio_config['endpoint'],
                aws_access_key_id=self.minio_config['access_key'],
                aws_secret_access_key=self.minio_config['secret_key']
            )
            
            buckets = ['raw-data', 'staging-data', 'analytics-data']
            for bucket in buckets:
                response = s3_client.list_objects_v2(Bucket=bucket)
                count = response.get('KeyCount', 0)
                logger.info(f"✓ MinIO {bucket}: {count} objets")
                
        except Exception as e:
            logger.error(f"Erreur vérification MinIO: {e}")

    def run(self):
        """Exécuter l'enrichissement complet des sources de données"""
        logger.info("🚀 DEMARRAGE DE L'ENRICHISSEMENT DES SOURCES DE DONNEES")
        
        try:
            # Attendre que les services soient disponibles
            self.wait_for_services()
            
            # Enrichir PostgreSQL
            self.enrich_postgresql()
            
            # Configurer MinIO
            self.setup_minio_buckets()
            
            # Vérifier les données
            self.verify_data_sources()
            
            logger.info("✅ ENRICHISSEMENT TERMINE AVEC SUCCES!")
            logger.info("Les sources de données sont maintenant complètement alimentées.")
            logger.info("Vous pouvez maintenant exécuter les scripts d'initialisation.")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ERREUR LORS DE L'ENRICHISSEMENT: {e}")
            return False

if __name__ == "__main__":
    enricher = DataSourceEnricher()
    success = enricher.run()
    sys.exit(0 if success else 1)