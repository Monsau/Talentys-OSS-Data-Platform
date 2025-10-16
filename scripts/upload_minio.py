#!/usr/bin/env python3
"""
Script rapide pour uploader les fichiers dans MinIO
"""

import boto3
from pathlib import Path

# Configuration MinIO
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minio_admin',
    aws_secret_access_key='minio_password'
)

# Chemins et mapping
base_dir = Path(r"c:\projets\dremiodbt\minio\sample-data")
files_to_upload = [
    ('customers_external.csv', 'raw-data', 'external/customers/'),
    ('transactions_2025.csv', 'raw-data', 'transactions/'),
    ('products_catalog.csv', 'staging-data', 'products/'),
    ('inventory_detailed.csv', 'staging-data', 'inventory/'),
    ('analytics_summary.json', 'analytics-data', 'reports/')
]

for filename, bucket, prefix in files_to_upload:
    file_path = base_dir / filename
    if file_path.exists():
        s3_key = f"{prefix}{filename}"
        s3_client.upload_file(str(file_path), bucket, s3_key)
        print(f"✓ Fichier uploadé: s3://{bucket}/{s3_key}")
    else:
        print(f"✗ Fichier non trouvé: {file_path}")

print("Upload MinIO terminé !")