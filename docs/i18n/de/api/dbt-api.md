# dbt-API-Referenz

**Version**: 3.2.0  
**Letzte Aktualisierung**: 16. Oktober 2025  
**Sprache**: Französisch

## Inhaltsverzeichnis

1. [Übersicht](#Übersicht)
2. [CLI-Befehle](#cli-commands)
3. [Python-API](#api-python)
4. [Metadatendateien](#metadata-files)
5. [dbt Cloud API](#api-dbt-cloud)
6. [Benutzerdefinierte Makros](#custom-macros)

---

## Übersicht

dbt bietet drei Hauptschnittstellen:

| Schnittstelle | Anwendungsfälle | Zugriff |
|---------------|-------------|-------|
| CLI | Entwicklung, CI/CD | Befehlszeile |
| Python-API | Programmatische Ausführung | Python-Code |
| dbt Cloud-API | Managed Service | REST-API |
| Metadaten | Selbstbeobachtung | JSON-Dateien |

---

## CLI-Befehle

### Hauptbefehle

#### dbt-Lauf

Führen Sie die Modelle aus, um die Daten zu transformieren.

```bash
# Exécuter tous les modèles
dbt run

# Exécuter un modèle spécifique
dbt run --select customers

# Exécuter un modèle et ses dépendances amont
dbt run --select +customers

# Exécuter un modèle et ses dépendances aval
dbt run --select customers+

# Exécuter les modèles d'un dossier spécifique
dbt run --select staging.*

# Exécuter uniquement les modèles modifiés
dbt run --select state:modified

# Rafraîchissement complet (ignorer la logique incrémentale)
dbt run --full-refresh

# Exécuter avec une cible spécifique
dbt run --target prod
```

**Optionen**:
```bash
--select (-s)      # Sélectionner les modèles à exécuter
--exclude (-x)     # Exclure des modèles
--full-refresh     # Reconstruire les modèles incrémentaux
--vars             # Passer des variables
--threads          # Nombre de threads (défaut : 1)
--target           # Profil cible
```

#### DBT-Test

Führen Sie Datenqualitätstests durch.

```bash
# Exécuter tous les tests
dbt test

# Tester un modèle spécifique
dbt test --select customers

# Exécuter uniquement les tests de schéma
dbt test --select test_type:schema

# Exécuter uniquement les tests de données
dbt test --select test_type:data

# Stocker les échecs de tests
dbt test --store-failures

# Échec sur sévérité warn
dbt test --warn-error
```

#### DBT-Build

Führen Sie Modelle, Tests, Seeds und Snapshots gemeinsam aus.

```bash
# Tout construire
dbt build

# Construire avec sélection
dbt build --select +customers

# Construire les modèles et tests modifiés
dbt build --select state:modified+
```

#### dbt-Dokumente

Dokumentation erstellen und bereitstellen.

```bash
# Générer la documentation
dbt docs generate

# Servir la documentation localement
dbt docs serve --port 8080

# Générer avec une cible
dbt docs generate --target prod
```

### Entwicklerbefehle

#### dbt kompiliert

Kompilieren Sie Modelle in SQL, ohne sie auszuführen.

```bash
# Compiler tous les modèles
dbt compile

# Compiler un modèle spécifique
dbt compile --select customers

# Voir le SQL compilé
cat target/compiled/project_name/models/staging/stg_customers.sql
```

#### DBT-Debug

Testen Sie die Datenbankverbindung und -konfiguration.

```bash
dbt debug

# Sortie attendue :
# Configuration:
#   profiles.yml file [OK found and valid]
#   dbt_project.yml file [OK found and valid]
# 
# Connection:
#   host: localhost
#   port: 9047
#   user: admin
#   Connection test: [OK connection ok]
```

#### dbt ls (Liste)

Projektressourcen auflisten.

```bash
# Lister tous les modèles
dbt ls --resource-type model

# Lister tous les tests
dbt ls --resource-type test

# Lister toutes les sources
dbt ls --resource-type source

# Lister avec sélection
dbt ls --select staging.*
```

### Datenbefehle

#### dbt-Seed

Laden Sie CSV-Dateien in die Datenbank.

```bash
# Charger tous les seeds
dbt seed

# Charger un seed spécifique
dbt seed --select country_codes

# Rafraîchissement complet des seeds
dbt seed --full-refresh
```

#### dbt-Snapshot

Erstellen Sie sich langsam ändernde Dimensionstabellen vom Typ 2.

```bash
# Exécuter tous les snapshots
dbt snapshot

# Exécuter un snapshot spécifique
dbt snapshot --select orders_snapshot
```

### Dienstprogrammbefehle

#### dbt sauber

Kompilierte Dateien und Artefakte löschen.

```bash
dbt clean
# Supprime : target/, dbt_packages/, logs/
```

#### dbt abt

Installieren Sie Pakete von packets.yml.

```bash
dbt deps

# Forcer la réinstallation
dbt deps --force
```

#### dbt init

Initialisieren Sie ein neues DBT-Projekt.

```bash
dbt init my_project
```

---

## Python-API

### Grundlegende Ausführung

```python
import dbt.main

# Exécuter des commandes dbt de manière programmatique
result = dbt.main.handle_and_check([
    "run",
    "--select", "customers"
])

# result est le code de sortie (0 = succès, 1+ = erreur)
if result == 0:
    print("dbt run succeeded")
else:
    print("dbt run failed")
```

### Vollständiger Python-Wrapper

```python
import dbt.main
import json
from pathlib import Path

class DbtProject:
    """Wrapper pour les opérations CLI dbt"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
    
    def _run_command(self, command: list) -> int:
        """Exécuter une commande dbt"""
        return dbt.main.handle_and_check(command)
    
    def run(self, select: str = None, exclude: str = None, 
            full_refresh: bool = False, target: str = None) -> bool:
        """Exécuter les modèles dbt"""
        cmd = ["run", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        if exclude:
            cmd.extend(["--exclude", exclude])
        if full_refresh:
            cmd.append("--full-refresh")
        if target:
            cmd.extend(["--target", target])
        
        return self._run_command(cmd) == 0
    
    def test(self, select: str = None, store_failures: bool = False) -> bool:
        """Exécuter les tests dbt"""
        cmd = ["test", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        if store_failures:
            cmd.append("--store-failures")
        
        return self._run_command(cmd) == 0
    
    def build(self, select: str = None) -> bool:
        """Construire les modèles et exécuter les tests"""
        cmd = ["build", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        
        return self._run_command(cmd) == 0
    
    def compile(self, select: str = None) -> bool:
        """Compiler les modèles dbt"""
        cmd = ["compile", "--project-dir", str(self.project_dir)]
        
        if select:
            cmd.extend(["--select", select])
        
        return self._run_command(cmd) == 0
    
    def docs_generate(self) -> bool:
        """Générer la documentation"""
        cmd = ["docs", "generate", "--project-dir", str(self.project_dir)]
        return self._run_command(cmd) == 0
    
    def get_manifest(self) -> dict:
        """Charger manifest.json"""
        manifest_path = self.project_dir / "target" / "manifest.json"
        
        if not manifest_path.exists():
            raise FileNotFoundError("manifest.json not found. Run dbt compile first.")
        
        with open(manifest_path) as f:
            return json.load(f)
    
    def get_run_results(self) -> dict:
        """Charger run_results.json"""
        results_path = self.project_dir / "target" / "run_results.json"
        
        if not results_path.exists():
            raise FileNotFoundError("run_results.json not found. Run dbt first.")
        
        with open(results_path) as f:
            return json.load(f)

# Exemple d'utilisation
if __name__ == "__main__":
    dbt = DbtProject("/path/to/dbt/project")
    
    # Compiler les modèles
    if dbt.compile():
        print("Compilation successful")
    
    # Exécuter les modèles staging
    if dbt.run(select="staging.*"):
        print("Staging models ran successfully")
    
    # Exécuter les tests sur marts
    if dbt.test(select="marts.*"):
        print("All tests passed")
    
    # Obtenir le manifest
    manifest = dbt.get_manifest()
    print(f"Found {len(manifest['nodes'])} nodes")
```

### Airflow-Integration

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def run_dbt_models(**context):
    """Exécuter les modèles dbt"""
    import dbt.main
    
    result = dbt.main.handle_and_check([
        "run",
        "--project-dir", "/opt/airflow/dbt/dremio_project",
        "--profiles-dir", "/opt/airflow/dbt",
        "--select", "staging.*"
    ])
    
    if result != 0:
        raise Exception("dbt run failed")

def run_dbt_tests(**context):
    """Exécuter les tests dbt"""
    import dbt.main
    
    result = dbt.main.handle_and_check([
        "test",
        "--project-dir", "/opt/airflow/dbt/dremio_project",
        "--profiles-dir", "/opt/airflow/dbt"
    ])
    
    if result != 0:
        raise Exception("dbt tests failed")

# Définir le DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'dbt_daily_run',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # 2h du matin quotidiennement
    catchup=False
)

# Tâches
run_staging = PythonOperator(
    task_id='run_staging',
    python_callable=run_dbt_models,
    dag=dag
)

run_intermediate = PythonOperator(
    task_id='run_intermediate',
    python_callable=lambda: dbt.main.handle_and_check([
        "run", "--select", "intermediate.*"
    ]),
    dag=dag
)

run_marts = PythonOperator(
    task_id='run_marts',
    python_callable=lambda: dbt.main.handle_and_check([
        "run", "--select", "marts.*"
    ]),
    dag=dag
)

run_tests = PythonOperator(
    task_id='run_tests',
    python_callable=run_dbt_tests,
    dag=dag
)

# Dépendances
run_staging >> run_intermediate >> run_marts >> run_tests
```

---

## Metadatendateien

### manifest.json

Enthält die vollständigen Projektmetadaten.

**Standort**: `target/manifest.json`

```python
import json

def analyze_manifest():
    """Analyser le manifest dbt"""
    with open("target/manifest.json") as f:
        manifest = json.load(f)
    
    # Lister tous les modèles
    models = {
        k: v for k, v in manifest["nodes"].items()
        if v["resource_type"] == "model"
    }
    
    print(f"Total models: {len(models)}")
    
    # Lister les modèles par matérialisation
    materializations = {}
    for node_id, node in models.items():
        mat = node["config"]["materialized"]
        materializations[mat] = materializations.get(mat, 0) + 1
    
    print("\nBy materialization:")
    for mat, count in materializations.items():
        print(f"  {mat}: {count}")
    
    # Lister les dépendances des modèles
    print("\nModel dependencies:")
    for node_id, node in models.items():
        if node["depends_on"]["nodes"]:
            model_name = node["name"]
            deps = [manifest["nodes"][dep]["name"] 
                   for dep in node["depends_on"]["nodes"]
                   if dep in manifest["nodes"]]
            print(f"  {model_name} → {deps}")

analyze_manifest()
```

### run_results.json

Enthält die Ausführungsergebnisse der letzten Ausführung.

**Standort**: `target/run_results.json`

```python
def analyze_run_results():
    """Analyser les résultats d'exécution dbt"""
    with open("target/run_results.json") as f:
        results = json.load(f)
    
    # Statistiques globales
    total = len(results["results"])
    success = sum(1 for r in results["results"] if r["status"] == "success")
    error = sum(1 for r in results["results"] if r["status"] == "error")
    skipped = sum(1 for r in results["results"] if r["status"] == "skipped")
    
    print(f"Total models run: {total}")
    print(f"Success: {success}")
    print(f"Error: {error}")
    print(f"Skipped: {skipped}")
    
    # Modèles les plus lents
    print("\nSlowest models:")
    sorted_results = sorted(
        results["results"],
        key=lambda x: x["execution_time"],
        reverse=True
    )[:10]
    
    for result in sorted_results:
        name = result["unique_id"].split(".")[-1]
        time = result["execution_time"]
        print(f"  {name}: {time:.2f}s")
    
    # Modèles en échec
    failed = [r for r in results["results"] if r["status"] == "error"]
    if failed:
        print("\nFailed models:")
        for result in failed:
            name = result["unique_id"].split(".")[-1]
            message = result["message"]
            print(f"  {name}: {message}")

analyze_run_results()
```

### Katalog.json

Enthält Informationen zum Datenbankschema.

**Standort**: `target/catalog.json`

```python
def analyze_catalog():
    """Analyser le catalogue dbt"""
    with open("target/catalog.json") as f:
        catalog = json.load(f)
    
    # Lister toutes les sources
    sources = catalog["sources"]
    print(f"Total sources: {len(sources)}")
    
    for source_id, source in sources.items():
        print(f"\n{source['metadata']['name']}:")
        print(f"  Rows: {source['stats']['row_count']['value']:,}")
        print(f"  Bytes: {source['stats']['bytes']['value']:,}")
        print(f"  Columns: {len(source['columns'])}")

analyze_catalog()
```

---

## dbt Cloud-API

Wenn Sie dbt Cloud verwenden (gilt nicht für die lokale Installation), ist die API verfügbar.

**Basis-URL**: `https://cloud.getdbt.com/api/v2`

### Authentifizierung

```python
import requests

DBT_CLOUD_TOKEN = "your-api-token"
ACCOUNT_ID = "your-account-id"

headers = {
    "Authorization": f"Token {DBT_CLOUD_TOKEN}",
    "Content-Type": "application/json"
}
```

### Einen Job auslösen

```python
def trigger_dbt_cloud_job(job_id: int):
    """Déclencher un job dbt Cloud"""
    url = f"https://cloud.getdbt.com/api/v2/accounts/{ACCOUNT_ID}/jobs/{job_id}/run/"
    
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code == 200:
        run = response.json()["data"]
        return run["id"]
    else:
        raise Exception(f"Failed to trigger job: {response.text}")

# Utilisation
run_id = trigger_dbt_cloud_job(job_id=12345)
print(f"Job run started: {run_id}")
```

---

## Benutzerdefinierte Makros

### Erstellen Sie ein benutzerdefiniertes Makro

**Datei**: `macros/custom_tests.sql`

```sql
{% macro test_valid_email(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} NOT LIKE '%@%.%'

{% endmacro %}
```

### Verwendung in Tests

**Datei**: `models/staging/schema.yml`

```yaml
models:
  - name: stg_customers
    columns:
      - name: email
        tests:
          - valid_email
```

### Erweitertes Makro mit Argumenten

```sql
{% macro grant_select(schema, role) %}

{% set sql %}
  GRANT SELECT ON ALL TABLES IN SCHEMA {{ schema }} TO {{ role }}
{% endset %}

{% do run_query(sql) %}
{% do log("Granted SELECT on " ~ schema ~ " to " ~ role, info=True) %}

{% endmacro %}
```

### Rufen Sie ein Makro auf

```bash
dbt run-operation grant_select --args '{schema: Production, role: analyst}'
```

---

## Zusammenfassung

Diese API-Referenz behandelte Folgendes:

- **CLI-Befehle**: Vollständige Referenz für alle DBT-Befehle
- **Python-API**: Programmatische Ausführung mit Python-Wrapper
- **Metadatendateien**: manifest.json, run_results.json, Catalog.json
- **dbt Cloud API**: Jobs auslösen (bei Verwendung von dbt Cloud)
- **Benutzerdefinierte Makros**: Erstellen und verwenden Sie benutzerdefinierte Funktionen

**Wichtige Punkte**:
- Nutzen Sie die CLI für Entwicklung und interaktives Arbeiten
- Verwenden Sie die Python-API zur Automatisierung und Orchestrierung
- Analysieren Sie Metadatendateien zur Selbstbeobachtung
- Erstellen Sie benutzerdefinierte Makros für wiederverwendbare Logik
- Integration mit Airflow für die Produktionsplanung

**Zugehörige Dokumentation**:
- [dbt-Entwicklungsleitfaden](../guides/dbt-development.md)
- [Datenqualitätsleitfaden](../guides/data-quality.md)
- [Architektur: Datenfluss](../architecture/data-flow.md)

---

**Version**: 3.2.0  
**Letzte Aktualisierung**: 16. Oktober 2025