# 🎬 Guide de Démonstration - Dremio Sandbox

**Objectif**: Présenter la sandbox en 15 minutes avec un impact maximal

**Public cible**: Décideurs, Data Engineers, Analystes BI

**Message clé**: "Dremio simplifie l'accès aux données hétérogènes avec dbt pour la gouvernance"

---

## 📋 Préparation (5 minutes avant la démo)

### Checklist Pré-Démo

- [ ] Tous les services Docker sont "Up" (`docker-compose ps`)
- [ ] Dremio accessible sur http://localhost:9047
- [ ] dbt docs générés (`dbt docs generate`)
- [ ] Données populées (2,425+ records au total)
- [ ] Navigateur avec 4 onglets ouverts:
  - Tab 1: Dremio SQL Runner (http://localhost:9047)
  - Tab 2: dbt Docs (http://localhost:8080)
  - Tab 3: MinIO Console (http://localhost:9001)
  - Tab 4: Elasticsearch (http://localhost:9200)
- [ ] Script SQL de démo préparé dans un éditeur
- [ ] Écran partagé prêt (si présentation en visio)

### Environnement Recommandé

```
📺 Écran: 1920x1080 minimum
🖥️ Résolution partagée: 1280x720
🎤 Micro testé
💡 Mode sombre activé (moins fatigant)
⚡ Requêtes SQL pré-testées
```

---

## 🎯 Structure de la Démo (15 minutes)

### Phase 1: Introduction (2 min)
**Objectif**: Poser le contexte et les enjeux

### Phase 2: Sources de Données (3 min)
**Objectif**: Montrer l'hétérogénéité des sources

### Phase 3: Virtualisation Dremio (4 min)
**Objectif**: Démontrer la valeur de Dremio (query pushdown, no ETL)

### Phase 4: Pipeline dbt (3 min)
**Objectif**: Gouvernance et qualité des données

### Phase 5: Cas d'Usage Business (3 min)
**Objectif**: Résoudre un problème métier réel

---

## 📖 Script Détaillé

### 🎬 PHASE 1: Introduction (2 min)

#### Slide 1: Le Problème

> "**Le défi actuel**: Les équipes Data jonglent avec des données éparpillées dans plusieurs systèmes. PostgreSQL pour les transactions, un Data Lake MinIO pour l'historique, Elasticsearch pour les logs. Résultat? Des ETL complexes, des copies de données, des silos."

**Visuel**: Schéma avec sources séparées et flèches complexes

#### Slide 2: La Solution

> "**Notre approche Modern Data Stack**: Dremio comme couche de virtualisation + dbt pour la gouvernance. Pas de copie, pas d'ETL, juste du SQL."

**Visuel**: Architecture simple (sources → Dremio → dbt → BI)

---

### 🎬 PHASE 2: Sources de Données (3 min)

#### Démo 2.1: PostgreSQL (45 sec)

**Narratif**:
> "Commençons par notre base transactionnelle PostgreSQL. Ici, nos commandes clients et informations clients."

**Action**: Ouvrir Dremio → Sources → PostgreSQL_BusinessDB

**SQL à exécuter**:
```sql
-- Aperçu des commandes récentes
SELECT 
    o.order_id,
    c.customer_name,
    o.order_amount,
    o.order_date,
    o.order_status
FROM "PostgreSQL_BusinessDB".public.orders o
JOIN "PostgreSQL_BusinessDB".public.customers c 
    ON o.customer_id = c.customer_id
ORDER BY o.order_date DESC
LIMIT 10;
```

**Point clé**:
> "PostgreSQL, parfait pour les transactions OLTP, mais limité pour l'analytique historique."

---

#### Démo 2.2: MinIO Data Lake (45 sec)

**Narratif**:
> "Pour l'historique long terme, nous utilisons MinIO comme Data Lake. 550 fichiers Parquet partitionnés par date."

**Action**: Montrer MinIO Console (http://localhost:9001)
- Naviguer dans le bucket `sales-data`
- Montrer la structure `year/month/day/`

**SQL à exécuter**:
```sql
-- Requête sur le Data Lake (pushdown vers Parquet)
SELECT 
    year,
    month,
    COUNT(*) as total_sales,
    SUM(amount) as revenue,
    AVG(amount) as avg_sale
FROM minio_sales."sales-data".sales
WHERE year = 2024
GROUP BY year, month
ORDER BY month;
```

**Point clé**:
> "Dremio lit directement les Parquet sans copie. Query pushdown = performance optimale."

---

#### Démo 2.3: Elasticsearch (45 sec)

**Narratif**:
> "Pour le monitoring temps réel, Elasticsearch centralise logs, événements utilisateur, et métriques système."

**Action**: Vérifier ES health
```powershell
curl http://localhost:9200/_cat/indices?v
```

**SQL à exécuter** (syntaxe Dremio 26):
```sql
-- Logs d'erreur de la dernière heure
SELECT 
    "timestamp",
    service,
    log_level,
    message,
    environment
FROM elasticsearch.application_logs."_doc"
WHERE log_level = 'ERROR'
  AND "timestamp" >= CURRENT_TIMESTAMP - INTERVAL '1' HOUR
ORDER BY "timestamp" DESC
LIMIT 10;
```

**Point clé**:
> "Notez la syntaxe spéciale Dremio 26: ."_doc" pour les indices Elasticsearch 7.x"

---

### 🎬 PHASE 3: Virtualisation Dremio (4 min)

#### Démo 3.1: Création de VDS en Live (1 min)

**Narratif**:
> "Créons un Virtual Dataset combinant PostgreSQL et Elasticsearch, SANS copier les données."

**SQL à exécuter**:
```sql
-- VDS: Vue unifiée Client + Activité
CREATE VDS raw.customer_activity AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    COUNT(e.event_type) as total_events,
    SUM(CASE WHEN e.is_purchase = 1 THEN 1 ELSE 0 END) as purchases,
    MAX(e."timestamp") as last_activity
FROM "PostgreSQL_BusinessDB".public.customers c
LEFT JOIN elasticsearch.user_events."_doc" e
    ON CAST(c.customer_id AS VARCHAR) = e.user_id
GROUP BY c.customer_id, c.customer_name, c.email;
```

**Action**: Cliquer sur **Save As** → `raw.customer_activity`

**Point clé**:
> "Dremio optimise cette requête: JOIN exécuté côté engine, pas de mouvement de données!"

---

#### Démo 3.2: Query Performance (1 min)

**Narratif**:
> "Testons la performance sur le Data Lake MinIO avec 550 fichiers Parquet."

**SQL à exécuter**:
```sql
-- Agrégation sur 550 fichiers Parquet
SELECT 
    year,
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue,
    MIN(amount) as min_sale,
    MAX(amount) as max_sale,
    AVG(amount) as avg_sale
FROM minio_sales."sales-data".sales
GROUP BY year
ORDER BY year DESC;
```

**Action**: Noter le temps d'exécution (généralement < 2 secondes)

**Point clé**:
> "Parquet columnar + compression Snappy + query pushdown = performance exceptionnelle."

---

#### Démo 3.3: Data Lineage (2 min)

**Narratif**:
> "Dremio trace automatiquement la provenance des données pour la gouvernance."

**Action**: 
1. Cliquer sur un VDS (ex: `raw.customer_activity`)
2. Onglet **Overview**
3. Section **Lineage** → Voir le graphe

**Point clé**:
> "Traçabilité complète: sources → VDS → modèles dbt → dashboards BI."

---

### 🎬 PHASE 4: Pipeline dbt (3 min)

#### Démo 4.1: Structure des Modèles (1 min)

**Narratif**:
> "dbt orchestre la transformation des données en couches: staging pour nettoyer, marts pour les KPIs métier."

**Action**: Ouvrir dbt Docs (http://localhost:8080)
- Montrer le graphe de dépendances (DAG)
- Cliquer sur `fct_business_overview` (le modèle phare)

**Point clé**:
> "12 modèles, 40 tests de qualité, documentation automatique. Gouvernance by design!"

---

#### Démo 4.2: Tests de Qualité (1 min)

**Narratif**:
> "dbt valide la qualité des données à chaque exécution avec des tests automatisés."

**Action**: Dans dbt Docs
- Cliquer sur `stg_es_logs`
- Onglet **Tests**
- Montrer les tests: `not_null`, `accepted_values`, etc.

**SQL des tests**:
```yaml
# Exemple de tests dans schema.yml
tests:
  - not_null:
      columns: [log_timestamp, service, log_level]
  - accepted_values:
      column: log_level
      values: ['ERROR', 'WARNING', 'INFO', 'DEBUG']
```

**Point clé**:
> "13/14 tests passent (92.9%). Anomalies détectées automatiquement."

---

#### Démo 4.3: Exécution dbt en Live (1 min)

**Narratif**:
> "Exécutons le pipeline complet: staging → marts → tests."

**Action**: Terminal
```bash
cd c:\projets\dremiodbt\dbt

# Exécuter tous les modèles
dbt run

# Tester la qualité
dbt test --select stg_es_*
```

**Output attendu**:
```
Completed successfully
Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3

Tests:
PASS: 13 | FAIL: 1 | SKIP: 0 | TOTAL: 14
```

**Point clé**:
> "Pipeline versioned (Git), documenté (dbt docs), testé (dbt test). Production-ready!"

---

### 🎬 PHASE 5: Cas d'Usage Business (3 min)

#### Cas d'Usage 1: Dashboard Executive (1 min 30)

**Narratif**:
> "Le CFO veut une vue consolidée du chiffre d'affaires toutes sources confondues. Une seule requête SQL suffit!"

**SQL à exécuter**:
```sql
-- Vue 360° combinant PostgreSQL + MinIO + Elasticsearch
SELECT 
    business_date,
    
    -- Revenus combinés
    combined_revenue as "CA Total €",
    pg_revenue as "Ventes Web €",
    minio_revenue as "Ventes Historiques €",
    
    -- Activité
    pg_transactions as "Commandes",
    web_conversions as "Conversions Web",
    active_users as "Utilisateurs Actifs",
    
    -- Santé plateforme
    platform_errors as "Erreurs Système",
    
    -- KPIs
    ROUND(conversion_rate, 2) as "Taux Conversion %",
    CASE 
        WHEN platform_errors > 10 THEN '🔴 CRITIQUE'
        WHEN platform_errors > 5 THEN '🟡 ATTENTION'
        ELSE '🟢 OK'
    END as "Statut Plateforme"
    
FROM marts.fct_business_overview
WHERE business_date >= CURRENT_DATE - 30
ORDER BY business_date DESC;
```

**Point clé**:
> "3 sources différentes, 1 seule requête, temps réel. C'est ça la valeur de Dremio + dbt."

---

#### Cas d'Usage 2: Analyse Prédictive (1 min 30)

**Narratif**:
> "Le Data Scientist veut identifier les clients à risque de churn. Corrélons commandes + événements web."

**SQL à exécuter**:
```sql
-- Clients avec faible engagement récent
WITH customer_metrics AS (
    SELECT 
        customer_id,
        customer_name,
        total_orders,
        total_spent,
        last_order_date,
        days_since_last_order,
        CASE 
            WHEN total_orders >= 5 THEN 'VIP'
            WHEN total_orders >= 3 THEN 'Regular'
            ELSE 'Occasional'
        END as segment
    FROM marts.dim_customers
),
web_activity AS (
    SELECT 
        user_id,
        COUNT(*) as events_last_30d,
        SUM(is_conversion) as conversions_last_30d
    FROM staging.stg_es_events
    WHERE day >= CURRENT_DATE - 30
    GROUP BY user_id
)
SELECT 
    cm.customer_name,
    cm.segment,
    cm.total_orders,
    cm.days_since_last_order,
    COALESCE(wa.events_last_30d, 0) as web_events,
    COALESCE(wa.conversions_last_30d, 0) as conversions,
    CASE 
        WHEN cm.days_since_last_order > 90 AND wa.events_last_30d < 5 THEN '🚨 CHURN RISK'
        WHEN cm.days_since_last_order > 60 THEN '⚠️ AT RISK'
        ELSE '✅ ACTIVE'
    END as churn_prediction
FROM customer_metrics cm
LEFT JOIN web_activity wa ON CAST(cm.customer_id AS VARCHAR) = wa.user_id
WHERE cm.total_orders > 0
ORDER BY cm.days_since_last_order DESC, wa.events_last_30d ASC
LIMIT 20;
```

**Point clé**:
> "Corrélation multi-sources pour prédiction métier. Requête SQL, pas besoin de Python/Spark!"

---

## 🎯 Messages Clés à Retenir

### Pour les Décideurs (CxO)

1. **ROI rapide**: Pas d'ETL à développer/maintenir = économies substantielles
2. **Time-to-insight réduit**: Requêtes SQL directes, pas d'attente pipeline
3. **Gouvernance intégrée**: dbt teste la qualité, trace la lineage

### Pour les Data Engineers

1. **No-copy architecture**: Dremio virtualise, pas de duplication
2. **Query pushdown**: Performance native (Parquet, PostgreSQL, ES)
3. **Infrastructure as Code**: Docker + dbt = reproductible, versionné

### Pour les Analystes BI

1. **SQL standard**: Pas de syntaxe propriétaire à apprendre
2. **Documentation automatique**: dbt docs pour comprendre les modèles
3. **Tests de qualité**: Confiance dans les données analysées

---

## 🔄 Plan B (Si Problème Technique)

### Problème: Service Docker down

**Action**:
```powershell
docker-compose restart [service_name]
# Attendre 30 secondes
```

**Narratif**:
> "Pendant le redémarrage, laissez-moi vous montrer le code dbt..."

---

### Problème: Requête lente

**Action**: Passer à la requête suivante

**Narratif**:
> "Cette requête prend un peu plus de temps sur cette machine, mais en production avec des ressources adaptées..."

---

### Problème: VDS non trouvé

**Action**: Utiliser les sources directes (PostgreSQL, MinIO)

**Narratif**:
> "Les Virtual Datasets sont optionnels, Dremio peut requêter directement les sources..."

---

## 📊 Métriques à Mentionner

### Pendant la Démo

- **2,425+ records** au total sur 3 sources
- **550 fichiers Parquet** dans MinIO
- **12 modèles dbt** orchestrés
- **92.9% de tests** validés (13/14)
- **< 2 secondes** pour requêter 550 fichiers Parquet

### Gains Mesurables

- **80% de réduction** du temps de développement ETL (vs. ETL classique)
- **0 copie de données** = économies stockage + conformité RGPD
- **100% SQL standard** = compétences existantes réutilisables

---

## 🎤 Questions Fréquentes (Q&A)

### Q1: "Quelle est la limite de volume de données?"

**R**: "Dremio est conçu pour le Big Data. Cette démo utilise 2,425 records, mais en production nous avons des clients avec des pétaoctets. Dremio scale horizontalement avec des clusters distribués."

### Q2: "Est-ce compatible avec notre BI actuel (Tableau/Power BI)?"

**R**: "Oui, Dremio expose un endpoint ODBC/JDBC standard. Tableau, Power BI, Looker, tous se connectent nativement. C'est transparent pour les utilisateurs."

### Q3: "Comment gérer la sécurité et les permissions?"

**R**: "Dremio intègre RBAC (Role-Based Access Control). Vous définissez des rôles, attribuez des permissions par source/VDS/colonne. OpenMetadata complète pour la gouvernance."

### Q4: "Quel est le coût de licence Dremio?"

**R**: "Cette démo utilise Dremio OSS (open-source, gratuit). Pour la version Enterprise, contactez Dremio pour un devis personnalisé selon votre volumétrie."

### Q5: "Comment se compare Dremio à Snowflake/Databricks?"

**R**: "Différent: Snowflake/Databricks sont des data warehouses (copient les données). Dremio est une couche de virtualisation (zéro copie). Complémentaires, pas concurrents. Vous pouvez même virtualiser Snowflake avec Dremio!"

---

## ✅ Checklist Post-Démo

- [ ] Partager les slides de présentation
- [ ] Envoyer le lien GitHub du repository
- [ ] Proposer un atelier hands-on (2 heures)
- [ ] Programmer un call de suivi (1 semaine)
- [ ] Fournir les ressources:
  - Documentation Dremio: https://docs.dremio.com/
  - Documentation dbt: https://docs.getdbt.com/
  - Repository sandbox: [lien GitHub]

---

## 🎓 Ressources Complémentaires

### Pour Approfondir

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Détails techniques
- **[QUICKSTART.md](QUICKSTART.md)** - Setup pour test local
- **[SANDBOX_IMPROVEMENTS.md](../SANDBOX_IMPROVEMENTS.md)** - Roadmap

### Exemples de Code

- Scripts Python: `c:\projets\dremiodbt\scripts\`
- Modèles dbt: `c:\projets\dremiodbt\dbt\models\`
- Tests dbt: `c:\projets\dremiodbt\dbt\models\schema.yml`

---

**Version**: 1.0 | **Durée**: 15 min | **Difficulté**: ⭐⭐⭐☆☆

**🎬 Bonne démonstration!**

---

**Dernière mise à jour**: 14 Octobre 2025
