# 🌍 Open Data Dashboard - Phase 3

## 📊 Vue d'ensemble

Dashboard interactif open source pour visualiser les résultats de la comparaison multi-sources (PostgreSQL vs MinIO).

## 🎯 Caractéristiques

- ✅ **100% Open Source** - Aucune dépendance propriétaire
- 📈 **Visualisations interactives** - Charts.js pour graphiques dynamiques
- 📊 **Export JSON** - Données au format Open Data standard
- 🔓 **ODbL License** - Licence Open Data Commons
- 🌐 **Responsive** - Compatible mobile/desktop
- ⚡ **Zero backend** - Dashboard HTML statique

## 🚀 Quick Start

### Option 1: Dashboard HTML statique (Recommandé)

```bash
# 1. Générer les données Open Data
cd c:\projets\dremiodbt
c:\projets\dremiodbt\venv\Scripts\activate.ps1
python scripts/generate_opendata_dashboard.py

# 2. Ouvrir le dashboard dans le navigateur
start opendata/dashboard.html
```

### Option 2: Serveur HTTP local

```bash
# PowerShell
cd opendata
python -m http.server 8000

# Ouvrir http://localhost:8000/dashboard.html
```

## 📦 Fichiers générés

```
opendata/
├── dashboard.html              # Dashboard interactif
├── phase3_opendata.json        # Dataset complet (Open Data)
├── phase3_metrics.json         # Métriques uniquement
├── phase3_details.json         # Détails uniquement
└── README.md                   # Cette documentation
```

## 📄 Format Open Data

### phase3_opendata.json

```json
{
  "metadata": {
    "title": "Phase 3 - Data Quality Comparison Report",
    "description": "Multi-source data quality metrics",
    "publisher": "Dremio Analytics Team",
    "date_published": "2025-10-15T16:30:00",
    "license": "Open Data Commons Open Database License (ODbL)",
    "version": "1.0.0",
    "tags": ["data-quality", "multi-source", "comparison"],
    "sources": [
      {"name": "PostgreSQL", "type": "RDBMS"},
      {"name": "MinIO", "type": "Object Storage"}
    ]
  },
  "summary": {
    "overview": {
      "total_customers": 12,
      "coverage_rate_pct": 66.67,
      "email_quality_pct": 58.33,
      "country_quality_pct": 58.33,
      "overall_status": "WARNING"
    }
  },
  "details": [
    {
      "customer_id": 1,
      "name": "Jean Dupont",
      "source_status": "both_sources",
      "email_status": "match",
      "country_status": "match"
    }
  ]
}
```

## 🎨 Technologies utilisées

### Frontend (100% Open Source)
- **Chart.js v4.4.0** - MIT License - Graphiques interactifs
- **Tailwind CSS v3** - MIT License - Framework CSS
- **Vanilla JavaScript** - Pas de framework lourd

### Backend
- **Python 3.13** - PSF License - Génération données
- **PostgreSQL** - PostgreSQL License - Source de données
- **dbt** - Apache 2.0 - Transformation de données

## 📊 Métriques disponibles

### Métriques principales
- **Total Customers** - Nombre total de clients uniques
- **Coverage Rate** - % de clients dans les deux sources
- **Email Quality** - % d'emails identiques
- **Country Quality** - % de pays identiques

### Statuts
- 🌟 **EXCELLENT** - Coverage 100% + 0 mismatches
- ✅ **GOOD** - Coverage >= 95%
- ⚠️ **WARNING** - Coverage >= 80%
- 🚨 **CRITICAL** - Coverage < 80%

## 🔄 Mise à jour des données

```bash
# Re-générer les données après modifications
python scripts/generate_opendata_dashboard.py

# Rafraîchir le navigateur (F5)
```

## 📈 Intégration avec d'autres outils

### Apache Superset (Option avancée)

```bash
# Lancer Superset avec Docker
docker-compose -f docker-compose-superset.yml up -d

# Accéder: http://localhost:8088
# Credentials: admin / admin
```

### Metabase (Option alternative)

```bash
# Lancer Metabase
docker run -d -p 3000:3000 --name metabase metabase/metabase

# Accéder: http://localhost:3000
```

### Grafana (Pour monitoring temps réel)

```bash
# Lancer Grafana
docker run -d -p 3001:3000 --name grafana grafana/grafana

# Accéder: http://localhost:3001
```

## 🌐 Partage et collaboration

### Export CSV

```python
# Depuis Python
import pandas as pd
import json

with open('opendata/phase3_details.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df.to_csv('opendata/phase3_export.csv', index=False)
```

### API REST (optionnel)

```python
# Servir les données via API Flask
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/api/metrics')
def get_metrics():
    with open('opendata/phase3_metrics.json') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(port=5000)
```

## 🔒 Licence

### Code
- **MIT License** - Dashboard HTML/JS/CSS

### Données
- **ODbL (Open Database License)** - phase3_opendata.json
- Vous êtes libre de:
  - ✅ Partager les données
  - ✅ Créer des œuvres dérivées
  - ✅ Adapter les données
- Sous condition:
  - 📝 Attribution de la source
  - 🔓 Partager sous même licence

## 📞 Support

**Questions?** Créer un issue sur GitHub ou contacter l'équipe Dremio Analytics.

## 🎯 Roadmap

- [ ] Export PDF automatique
- [ ] Alertes email automatiques
- [ ] Intégration Slack/Teams
- [ ] Dashboard temps réel (WebSocket)
- [ ] Historique des métriques (timeseries)
- [ ] Comparaison multi-périodes
- [ ] API GraphQL

---

**Créé avec ❤️ par l'équipe Dremio Analytics**  
**Version:** 1.0.0  
**Dernière mise à jour:** 15 octobre 2025
