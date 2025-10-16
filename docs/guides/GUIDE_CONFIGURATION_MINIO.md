# Configuration Manuelle de la Source MinIO dans Dremio

## ✅ Prérequis
- Dremio accessible sur http://localhost:9047
- MinIO accessible avec les credentials: `minio_admin` / `minio_password`
- Buckets créés dans MinIO: `raw-data`, `staging-data`, `analytics-data`

## 📝 Étapes de Configuration

### 1. Accéder à Dremio
1. Ouvrir http://localhost:9047 dans un navigateur
2. Se connecter avec: **admin** / **admin123**

### 2. Ajouter une Source S3 (MinIO)
1. Dans Dremio, cliquer sur **"+"** (Add Source) dans la sidebar gauche
2. Sélectionner **"Amazon S3"**

### 3. Configuration de Base
- **Name**: `MinIO_Storage`
- **Authentication Method**: `AWS access key`
- **AWS Access Key**: `minio_admin`
- **AWS Secret Key**: `minio_password`

### 4. Configuration Avancée
Cliquer sur **"Advanced Options"** et ajouter ces propriétés:

| Property Name | Value |
|--------------|-------|
| `fs.s3a.endpoint` | `minio:9000` |
| `fs.s3a.path.style.access` | `true` |
| `fs.s3a.connection.ssl.enabled` | `false` |
| `dremio.s3.compat` | `true` |

### 5. Configuration des Buckets
Dans **"General"** > **"External Buckets"**, ajouter:
- `raw-data`
- `staging-data`
- `analytics-data`

### 6. Sauvegarder
1. Cliquer sur **"Save"**
2. Attendre que Dremio découvre les fichiers (peut prendre 30-60 secondes)
3. Cliquer sur le nom de la source `MinIO_Storage` pour voir les buckets

### 7. Vérifier les Données
Vous devriez voir dans `MinIO_Storage`:
```
MinIO_Storage/
├── raw-data/
│   ├── sales/
│   │   └── sales_2024.csv (400 lignes)
│   ├── inventory/
│   │   └── inventory_snapshot.json (20 objets)
│   ├── external/
│   │   └── customers/
│   │       └── customers_external.csv
│   └── web_logs/
│       └── logs.parquet
├── staging-data/
└── analytics-data/
```

## 🔄 Une fois la Source Créée

Relancer le script de création des VDS:
```bash
cd /mnt/c/projets/dremiodbt
source venv/bin/activate
python scripts/create_minio_vds_simple.py
```

Puis relancer dbt:
```bash
./run_dbt.sh
```

## 🧪 Tester la Source

Test SQL direct dans Dremio:
```sql
SELECT * FROM "MinIO_Storage"."raw-data".sales."sales_2024.csv" LIMIT 10;
```

Test via script Python:
```bash
python scripts/test_minio_vds.py
```

## ⚠️ Troubleshooting

**Si les fichiers ne s'affichent pas:**
1. Vérifier que MinIO est accessible: http://localhost:9001
2. Vérifier que les buckets existent
3. Dans Dremio, faire un clic droit sur `MinIO_Storage` > **"Refresh Metadata"**

**Si erreur "Connection refused":**
- Utiliser `minio:9000` (nom du service Docker) au lieu de `localhost:9000`
- Vérifier que Dremio et MinIO sont sur le même réseau Docker

**Si erreur "Access Denied":**
- Vérifier les credentials: `minio_admin` / `minio_password`
- Vérifier que les buckets sont accessibles depuis MinIO Console

## 📊 Résultat Attendu

Après configuration réussie, les VDS MinIO devraient contenir des données:
- `raw.minio_sales`: ~400 lignes de ventes
- `raw.minio_customers_external`: données clients externes
- `analytics.sales_by_region`: agrégations par région
- `analytics.top_products`: top 20 produits

Et dbt devrait créer avec succès:
- `stg_minio_sales` (view)
- `stg_minio_customers` (view)
- `fct_sales_minio` (table)
