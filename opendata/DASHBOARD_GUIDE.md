# 📸 Dashboard Open Data - Guide visuel

## 🌐 Accéder au dashboard

### Méthode 1: Double-clic (Simple)
1. Ouvrir l'explorateur Windows
2. Naviguer vers `c:\projets\dremiodbt\opendata\`
3. Double-cliquer sur `dashboard.html`
4. Le dashboard s'ouvre dans votre navigateur par défaut

### Méthode 2: Ligne de commande
```powershell
start c:\projets\dremiodbt\opendata\dashboard.html
```

### Méthode 3: Serveur HTTP local (Recommandé pour développement)
```powershell
cd c:\projets\dremiodbt\opendata
python -m http.server 8000
```
Puis ouvrir: http://localhost:8000/dashboard.html

---

## 📊 Sections du dashboard

### 1. Header (En-tête)
```
═══════════════════════════════════════════════════════
📊 Phase 3 - Data Quality Dashboard
Multi-source comparison: PostgreSQL vs MinIO

🌍 Open Data | 🔓 ODbL License | ⏱️ Updated: 15/10/2025
═══════════════════════════════════════════════════════
```

**Badges:**
- 🌍 Open Data - Indique que les données sont en format ouvert
- 🔓 ODbL License - Open Database License
- ⏱️ Updated - Timestamp de dernière génération

---

### 2. Overall Status Banner (Bannière de statut)

**Couleurs selon statut:**

```
🌟 EXCELLENT (Vert)
Perfect data quality across all sources!
└─ Coverage 100% + 0 email/country mismatches
```

```
✅ GOOD (Bleu)
Great data quality with minor issues.
└─ Coverage >= 95%
```

```
⚠️ WARNING (Orange) ← ÉTAT ACTUEL
Some data quality issues detected. Review recommended.
└─ Coverage >= 80%
```

```
🚨 CRITICAL (Rouge)
Critical data quality issues! Immediate action required.
└─ Coverage < 80%
```

**Données actuelles:**
```
Overall Status: ⚠️ WARNING
Some data quality issues detected. Review recommended.
```

---

### 3. Key Metrics Cards (Cartes métriques)

**4 cartes principales:**

```
┌─────────────────────┐
│ 👥 Total Customers  │
│      12             │
│ Unique records      │
└─────────────────────┘

┌─────────────────────┐
│ 🎯 Coverage Rate    │
│    66.67%           │
│ Records in both     │
└─────────────────────┘

┌─────────────────────┐
│ 📧 Email Quality    │
│    58.33%           │
│ Matching emails     │
└─────────────────────┘

┌─────────────────────┐
│ 🌍 Country Quality  │
│    58.33%           │
│ Matching countries  │
└─────────────────────┘
```

**Interactivité:**
- Hover (survol) : Cartes se soulèvent légèrement
- Responsive : S'adapte à la taille de l'écran

---

### 4. Charts (Graphiques)

#### Chart 1: Source Distribution (Doughnut)
```
     ┌────────────────────────┐
     │  📊 Source Distribution│
     │                        │
     │        ╱╲              │
     │       ╱  ╲             │
     │      │    │            │
     │       ╲  ╱             │
     │        ╲╱              │
     │                        │
     │ 🟢 Both Sources: 8     │
     │ 🔵 PostgreSQL Only: 2  │
     │ 🟠 MinIO Only: 2       │
     └────────────────────────┘
```

**Interprétation:**
- 66.67% des clients sont dans les deux sources
- 16.67% uniquement dans PostgreSQL (IDs 9-10)
- 16.67% uniquement dans MinIO (IDs 11-12)

#### Chart 2: Quality Metrics (Bar)
```
     ┌────────────────────────┐
     │  📈 Quality Metrics    │
     │                        │
     │  100%┤                 │
     │   80%┤                 │
     │   60%┤ ▓▓  ▓▓  ▓▓     │
     │   40%┤ ▓▓  ▓▓  ▓▓     │
     │   20%┤ ▓▓  ▓▓  ▓▓     │
     │    0%┴─────────────    │
     │      Coverage Email    │
     │              Country   │
     └────────────────────────┘
```

**Interprétation:**
- Coverage: 66.67% (barre bleue)
- Email Quality: 58.33% (barre verte)
- Country Quality: 58.33% (barre violette)

---

### 5. Detailed Issues Table (Tableau détaillé)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Detailed Issues                                                          │
├──────────┬─────────────┬──────────────┬──────────────┬──────────────┬───────┤
│ Customer │ Name        │ Source       │ Email        │ Country      │Details│
│ ID       │             │ Status       │ Status       │ Status       │       │
├──────────┼─────────────┼──────────────┼──────────────┼──────────────┼───────┤
│ 7        │Thomas       │both_sources  │🔴 mismatch  │✅ match      │Email: │
│          │Richard      │              │              │              │gmail  │
├──────────┼─────────────┼──────────────┼──────────────┼──────────────┼───────┤
│ 8        │Emma         │both_sources  │✅ match      │🔴 mismatch  │Countr:│
│          │Moreau       │              │              │              │BE≠FR  │
├──────────┼─────────────┼──────────────┼──────────────┼──────────────┼───────┤
│ 9        │Lucas        │🟣 postgres   │🟡 missing   │🟡 missing   │Missin │
│          │Simon        │only          │              │              │MinIO  │
├──────────┼─────────────┼──────────────┼──────────────┼──────────────┼───────┤
│ 10       │Camille      │🟣 postgres   │🟡 missing   │🟡 missing   │Missin │
│          │Laurent      │only          │              │              │MinIO  │
├──────────┼─────────────┼──────────────┼──────────────┼──────────────┼───────┤
│ 11       │Antoine      │🟠 minio      │🟡 missing   │🟡 missing   │Missin │
│          │Dubois       │only          │              │              │in PG  │
├──────────┼─────────────┼──────────────┼──────────────┼──────────────┼───────┤
│ 12       │Claire       │🟠 minio      │🟡 missing   │🟡 missing   │Missin │
│          │Leroy        │only          │              │              │in PG  │
└──────────┴─────────────┴──────────────┴──────────────┴──────────────┴───────┘
```

**Badges de statut:**
- ✅ `match` (vert) - Données identiques
- 🔴 `mismatch` (rouge) - Données différentes
- 🟡 `missing` (jaune) - Données absentes
- 🔵 `both_sources` (bleu) - Présent partout
- 🟣 `postgres_only` (violet) - Uniquement PostgreSQL
- 🟠 `minio_only` (orange) - Uniquement MinIO

---

### 6. Open Data Info Section

```
┌────────────────────────────────────────────────────────┐
│ 🌍 Open Data Information                               │
├────────────────────────────────────────────────────────┤
│ 📄 License                                             │
│ Open Data Commons Open Database License (ODbL)         │
│ You are free to share, create, and adapt this data     │
│                                                        │
│ 📦 Data Sources                                        │
│ • PostgreSQL: postgresql://localhost:5432/business_db  │
│ • MinIO: http://localhost:9000                         │
│                                                        │
│ [⬇️ Download Full Dataset]  [⬇️ Download Metrics]     │
│ [⬇️ Download Details]                                  │
└────────────────────────────────────────────────────────┘
```

**Boutons de téléchargement:**
1. **Download Full Dataset (JSON)** - `phase3_opendata.json` (complet)
2. **Download Metrics Only** - `phase3_metrics.json` (métriques)
3. **Download Details Only** - `phase3_details.json` (détails)

---

## 🎨 Palette de couleurs

```
Statuts:
├─ EXCELLENT : #10b981 → #059669 (vert gradient)
├─ GOOD      : #3b82f6 → #2563eb (bleu gradient)
├─ WARNING   : #f59e0b → #d97706 (orange gradient) ← ACTUEL
└─ CRITICAL  : #ef4444 → #dc2626 (rouge gradient)

Charts:
├─ Both Sources    : #10b981 (vert)
├─ PostgreSQL Only : #3b82f6 (bleu)
├─ MinIO Only      : #f59e0b (orange)
├─ Coverage        : #3b82f6 (bleu)
├─ Email Quality   : #10b981 (vert)
└─ Country Quality : #8b5cf6 (violet)

Badges:
├─ match          : #10b981 (vert)
├─ mismatch       : #ef4444 (rouge)
├─ missing        : #f59e0b (jaune)
├─ both_sources   : #3b82f6 (bleu)
├─ postgres_only  : #8b5cf6 (violet)
└─ minio_only     : #f59e0b (orange)
```

---

## 📱 Responsive Design

### Desktop (> 1024px)
- 4 cartes métriques en ligne
- 2 graphiques côte à côte
- Tableau pleine largeur

### Tablet (768px - 1024px)
- 2 cartes métriques par ligne
- 2 graphiques côte à côte
- Tableau scrollable horizontalement

### Mobile (< 768px)
- 1 carte métrique par ligne (stack vertical)
- 1 graphique par ligne (stack vertical)
- Tableau scrollable horizontalement

---

## 🔄 Rafraîchir les données

### Étape 1: Re-générer le modèle dbt
```powershell
cd c:\projets\dremiodbt\dbt
c:\projets\dremiodbt\venv\Scripts\activate.ps1
dbt run --select phase3_all_in_one --full-refresh
```

### Étape 2: Re-générer les données JSON
```powershell
cd c:\projets\dremiodbt
python scripts/generate_opendata_dashboard.py
```

### Étape 3: Rafraîchir le navigateur
- Appuyer sur `F5` dans le navigateur
- Ou `Ctrl+R` (Windows)
- Ou `Cmd+R` (Mac)

---

## 🐛 Troubleshooting

### Dashboard ne charge pas les données
**Symptôme:** Dashboard affiche "Loading data..."

**Solutions:**
1. Vérifier que les fichiers JSON existent:
   ```powershell
   dir c:\projets\dremiodbt\opendata\*.json
   ```
   
2. Vérifier le contenu JSON:
   ```powershell
   Get-Content c:\projets\dremiodbt\opendata\phase3_opendata.json | ConvertFrom-Json
   ```

3. Re-générer les données:
   ```powershell
   python scripts/generate_opendata_dashboard.py
   ```

4. Vérifier la console navigateur (F12):
   - Chercher les erreurs JavaScript
   - Vérifier les requêtes réseau (Network tab)

### Graphiques ne s'affichent pas
**Symptôme:** Cartes visibles mais graphiques vides

**Solutions:**
1. Vérifier connexion internet (Chart.js CDN):
   - https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
   
2. Utiliser serveur HTTP local (évite CORS):
   ```powershell
   cd opendata
   python -m http.server 8000
   ```

3. Vérifier console navigateur pour erreurs

### Erreur CORS
**Symptôme:** "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution:** Utiliser serveur HTTP local:
```powershell
cd c:\projets\dremiodbt\opendata
python -m http.server 8000
# Ouvrir http://localhost:8000/dashboard.html
```

---

## 📊 Exemples de données

### phase3_metrics.json
```json
{
  "total_customers": 12,
  "postgres_count": 10,
  "minio_count": 10,
  "both_sources": 8,
  "postgres_only": 2,
  "minio_only": 2,
  "coverage_rate_pct": 66.67,
  "email_matches": 7,
  "email_mismatches": 1,
  "email_quality_pct": 58.33,
  "country_matches": 7,
  "country_mismatches": 1,
  "country_quality_pct": 58.33,
  "overall_status": "WARNING",
  "report_timestamp": "2025-10-15T16:30:00.123456"
}
```

### phase3_details.json (extrait)
```json
[
  {
    "customer_id": 7,
    "name": "Thomas Richard",
    "postgres_email": "thomas.richard@email.fr",
    "minio_email": "thomas.richard@gmail.com",
    "postgres_country": "France",
    "minio_country": "France",
    "source_status": "both_sources",
    "email_status": "mismatch",
    "country_status": "match"
  }
]
```

---

## 🎯 Utilisation avancée

### Intégrer dans Jupyter Notebook
```python
import json
import pandas as pd
import matplotlib.pyplot as plt

# Charger les données
with open('opendata/phase3_metrics.json') as f:
    metrics = json.load(f)

# Créer un graphique
labels = ['Coverage', 'Email Quality', 'Country Quality']
values = [
    metrics['coverage_rate_pct'],
    metrics['email_quality_pct'],
    metrics['country_quality_pct']
]

plt.bar(labels, values)
plt.ylabel('Percentage (%)')
plt.title('Phase 3 Quality Metrics')
plt.show()
```

### Exporter en CSV
```python
import json
import csv

with open('opendata/phase3_details.json') as f:
    data = json.load(f)

with open('opendata/export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
```

### Créer une API Flask
```python
from flask import Flask, jsonify, send_file
import json

app = Flask(__name__)

@app.route('/api/metrics')
def get_metrics():
    with open('opendata/phase3_metrics.json') as f:
        return jsonify(json.load(f))

@app.route('/api/details')
def get_details():
    with open('opendata/phase3_details.json') as f:
        return jsonify(json.load(f))

@app.route('/')
def dashboard():
    return send_file('opendata/dashboard.html')

if __name__ == '__main__':
    app.run(port=5000)
```

---

**Bon dashboard! 📊✨**
