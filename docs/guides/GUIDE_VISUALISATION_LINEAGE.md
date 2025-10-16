# 📊 Guide de Visualisation du Lineage dbt

## 🎯 Objectif
Visualiser le flux de données (lineage) entre les sources, modèles staging, et marts dans dbt.

---

## 🌐 Option 1: Documentation dbt Interactive (RECOMMANDÉ)

### 1. Générer et Servir la Documentation

**Via WSL (recommandé)**:
```bash
cd /mnt/c/projets/dremiodbt
source venv/bin/activate
cd dbt
dbt docs generate
dbt docs serve --port 8083
```

**Via PowerShell**:
```powershell
cd C:\projets\dremiodbt
.\venv\Scripts\Activate.ps1
cd dbt
dbt docs generate
dbt docs serve --port 8083
```

### 2. Accéder à la Documentation

**Ouvrir dans le navigateur**: http://localhost:8083

### 3. Visualiser le Lineage

Dans l'interface dbt docs:

1. **Vue d'ensemble** : 
   - Page d'accueil liste tous les modèles
   - Clic sur un modèle pour voir les détails

2. **Lineage Graph (Graphe de lignage)** :
   - Clic sur l'icône "Lineage" (en bas à droite) **OU**
   - Clic sur le bouton bleu "View Lineage Graph" dans la page d'un modèle
   
3. **Navigation interactive** :
   - **Zoom** : Molette de la souris
   - **Déplacement** : Clic + glisser
   - **Focus** : Clic sur un nœud pour centrer
   - **Détails** : Double-clic sur un nœud pour ouvrir la page du modèle

### 4. Ce que tu verras

```
┌─────────────────────────────────────────────────────────┐
│                     LINEAGE GRAPH                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [raw.customers] ──┐                                    │
│                     ├──> [stg_customers] ──┐            │
│  [raw.orders] ──────┼──> [stg_orders] ─────┼──>        │
│                     │                       │            │
│  [raw.minio_sales] ─┴──> [stg_minio_sales] ┴──>        │
│                                              │           │
│                          [dim_customers] <───┤           │
│                          [fct_orders]    <───┤           │
│                          [fct_sales_minio] <─┘           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Codes couleur** :
- 🟢 **Vert** : Sources
- 🔵 **Bleu** : Modèles staging (views)
- 🟣 **Violet** : Modèles marts (tables)
- 🔴 **Rouge** : Modèles avec erreurs

---

## 📈 Option 2: Lineage via dbt CLI

### Commande de base
```bash
cd /mnt/c/projets/dremiodbt/dbt
source ../venv/bin/activate
dbt ls --select +fct_orders+
```

### Exemples de sélection

**1. Voir tous les modèles upstream d'un modèle** (ses parents):
```bash
dbt ls --select +fct_orders
```
Résultat: `raw.customers`, `raw.orders`, `stg_customers`, `stg_orders`, `fct_orders`

**2. Voir tous les modèles downstream d'un modèle** (ses enfants):
```bash
dbt ls --select stg_customers+
```
Résultat: `stg_customers`, `dim_customers`, `fct_orders`

**3. Voir le lineage complet d'un modèle** (parents + lui + enfants):
```bash
dbt ls --select +fct_orders+
```

**4. Générer un graphe visuel en texte**:
```bash
dbt run-operation generate_model_yaml --args '{model_name: fct_orders}'
```

---

## 🎨 Option 3: Générer un Diagramme PNG/SVG (Avancé)

### Installer les dépendances:
```bash
pip install dbt-osmosis sqllineage graphviz
```

### Générer le diagramme:
```bash
dbt-osmosis yaml refactor
dbt docs generate
# Puis utiliser un outil externe comme dbt-lineage-graph
```

---

## 🔍 Option 4: Lineage dans Dremio (Limité)

Dremio ne montre pas le lineage dbt directement, mais tu peux voir:

1. **Dans Dremio UI** (http://localhost:9047):
   - Ouvrir un VDS
   - Voir sa définition SQL
   - Identifier manuellement les dépendances

2. **Requête SQL pour voir les dépendances**:
```sql
-- Voir tous les VDS dans un espace
SELECT * FROM sys.views WHERE table_schema = 'analytics'

-- Voir la définition d'un VDS
SHOW CREATE VIEW analytics.sales_by_region
```

**Limitation** : Dremio ne trace pas automatiquement les transformations dbt, il voit seulement les VDS finaux.

---

## 📊 Option 5: Intégration OpenMetadata (Le Plus Complet)

Si OpenMetadata est configuré, il peut capturer le lineage complet:

### 1. Configuration
Assure-toi que l'ingestion dbt est configurée dans OpenMetadata.

### 2. Accès
- **URL**: http://localhost:8585
- **Login**: admin / admin

### 3. Navigation
1. Aller dans "Explore" → "Tables"
2. Chercher un modèle (ex: `fct_orders`)
3. Cliquer sur l'onglet **"Lineage"**

### 4. Avantages OpenMetadata
- ✅ Lineage multi-sources (PostgreSQL → Dremio → dbt)
- ✅ Lineage au niveau des colonnes
- ✅ Historique des transformations
- ✅ Impact analysis
- ✅ Ownership et tags

---

## 🎯 Recommandation

**Pour le développement quotidien** :
→ **dbt docs** (Option 1) - Simple, rapide, toujours à jour

**Pour la documentation d'équipe** :
→ **OpenMetadata** (Option 5) - Vue d'ensemble, gouvernance

**Pour le debugging** :
→ **dbt CLI** (Option 2) - Sélection précise des modèles

---

## 🚀 Accès Rapide

### Démarrer le serveur dbt docs:
```bash
cd /mnt/c/projets/dremiodbt
./generate_dbt_docs.sh
```

### Ouvrir dans le navigateur:
```
http://localhost:8083
```

### Arrêter le serveur:
```bash
Ctrl + C dans le terminal
```

---

## 📝 Exemple de Lineage de notre Projet

```
SOURCES
├── PostgreSQL
│   ├── customers ──────┐
│   ├── orders ─────────┤
│   └── products ───────┤
│                        │
└── MinIO               │
    ├── sales_2024.csv ─┤
    └── customers.csv ──┤
                         │
                         ▼
STAGING (dbt views)     
├── stg_customers ──────┐
├── stg_orders ─────────┤
├── stg_minio_sales ────┤
└── stg_minio_customers─┤
                         │
                         ▼
MARTS (dbt tables)      
├── dim_customers ◄─────┤
├── fct_orders ◄────────┤
└── fct_sales_minio ◄───┘
```

---

## ✅ Checklist de Vérification

- [ ] dbt docs généré: `dbt docs generate`
- [ ] Serveur lancé: `dbt docs serve --port 8083`
- [ ] Navigateur ouvert: http://localhost:8083
- [ ] Lineage Graph cliquable
- [ ] Tous les modèles visibles (7 modèles + sources)

---

**Date**: 2025-10-14  
**Port par défaut**: 8083  
**Documentation officielle dbt**: https://docs.getdbt.com/docs/collaborate/documentation
