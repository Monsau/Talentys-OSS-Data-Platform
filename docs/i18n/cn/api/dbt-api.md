# dbt API 参考

**版本**：3.2.0  
**最后更新**：2025 年 10 月 16 日  
**语言**：法语

＃＃ 目录

1. [概述](#overview)
2. [CLI 命令](#cli-commands)
3. [Python API](#api-python)
4. [元数据文件](#metadata-files)
5. [dbt云API](#api-dbt-cloud)
6. [自定义宏](#custom-macros)

---

＃＃ 概述

dbt提供了三个主要接口：

|接口 |使用案例 |访问 |
|----------------|-------------|--------|
|命令行 |开发、CI/CD |命令行 |
| Python API |程序化执行 | Python 代码 |
| dbt云API |托管服务|休息 API |
|元数据|内省| JSON 文件 |

---

## CLI 命令

### 主要命令

#### dbt 运行

运行模型来转换数据。

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

**选项**：
```bash
--select (-s)      # Sélectionner les modèles à exécuter
--exclude (-x)     # Exclure des modèles
--full-refresh     # Reconstruire les modèles incrémentaux
--vars             # Passer des variables
--threads          # Nombre de threads (défaut : 1)
--target           # Profil cible
```

#### 数据库测试

运行数据质量测试。

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

#### dbt 构建

一起运行模型、测试、种子和快照。

```bash
# Tout construire
dbt build

# Construire avec sélection
dbt build --select +customers

# Construire les modèles et tests modifiés
dbt build --select state:modified+
```

#### DBT 文档

生成并提供文档。

```bash
# Générer la documentation
dbt docs generate

# Servir la documentation localement
dbt docs serve --port 8080

# Générer avec une cible
dbt docs generate --target prod
```

### 开发者命令

#### dbt 编译

将模型编译为 SQL 而不运行它们。

```bash
# Compiler tous les modèles
dbt compile

# Compiler un modèle spécifique
dbt compile --select customers

# Voir le SQL compilé
cat target/compiled/project_name/models/staging/stg_customers.sql
```

#### dbt 调试

测试数据库连接和配置。

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

#### dbt ls（列表）

列出项目资源。

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

### 数据命令

#### dbt 种子

将 CSV 文件加载到数据库中。

```bash
# Charger tous les seeds
dbt seed

# Charger un seed spécifique
dbt seed --select country_codes

# Rafraîchissement complet des seeds
dbt seed --full-refresh
```

#### dbt 快照

创建类型 2 缓慢变化的维度表。

```bash
# Exécuter tous les snapshots
dbt snapshot

# Exécuter un snapshot spécifique
dbt snapshot --select orders_snapshot
```

### 实用命令

#### dbt 清洁

删除编译的文件和工件。

```bash
dbt clean
# Supprime : target/, dbt_packages/, logs/
```

#### dbt 依赖项

从packages.yml 安装包。

```bash
dbt deps

# Forcer la réinstallation
dbt deps --force
```

####dbt 初始化

初始化一个新的 dbt 项目。

```bash
dbt init my_project
```

---

## Python API

### 基本执行

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

### 完整的 Python 包装器

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

### 气流集成

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

## 元数据文件

### 清单.json

包含完整的项目元数据。

**位置**：`target/manifest.json`

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

包含上次执行的执行结果。

**位置**：`target/run_results.json`

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

### 目录.json

包含数据库架构信息。

**位置**：`target/catalog.json`

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

## dbt 云 API

如果您使用的是dbt Cloud（不适用于本地安装），则可以使用该API。

**基本网址**：`https://cloud.getdbt.com/api/v2`

＃＃＃ 验证

```python
import requests

DBT_CLOUD_TOKEN = "your-api-token"
ACCOUNT_ID = "your-account-id"

headers = {
    "Authorization": f"Token {DBT_CLOUD_TOKEN}",
    "Content-Type": "application/json"
}
```

### 触发作业

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

## 自定义宏

### 创建自定义宏

**文件**：`macros/custom_tests.sql`

```sql
{% macro test_valid_email(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} NOT LIKE '%@%.%'

{% endmacro %}
```

### 在测试中使用

**文件**：`models/staging/schema.yml`

```yaml
models:
  - name: stg_customers
    columns:
      - name: email
        tests:
          - valid_email
```

### 带参数的高级宏

```sql
{% macro grant_select(schema, role) %}

{% set sql %}
  GRANT SELECT ON ALL TABLES IN SCHEMA {{ schema }} TO {{ role }}
{% endset %}

{% do run_query(sql) %}
{% do log("Granted SELECT on " ~ schema ~ " to " ~ role, info=True) %}

{% endmacro %}
```

### 调用宏

```bash
dbt run-operation grant_select --args '{schema: Production, role: analyst}'
```

---

＃＃ 概括

此 API 参考涵盖：

- **CLI 命令**：所有 dbt 命令的完整参考
- **Python API**：使用 Python 包装器进行编程执行
- **元数据文件**：manifest.json、run_results.json、catalog.json
- **dbt Cloud API**：触发作业（如果使用 dbt Cloud）
- **自定义宏**：创建和使用自定义功能

**要点**：
- 使用 CLI 进行开发和交互工作
- 使用Python API进行自动化和编排
- 分析元数据文件以进行自省
- 为可重用逻辑创建自定义宏
- 与 Airflow 集成以制定生产计划

**相关文档**：
- [dbt开发指南](../guides/dbt-development.md)
- [数据质量指南](../guides/data-quality.md)
- [架构：数据流](../architecture/data-flow.md)

---

**版本**：3.2.0  
**最后更新**：2025 年 10 月 16 日