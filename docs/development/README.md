# 💻 Development Guide

Guide de développement pour la plateforme Data Platform v3.3.1

## 📑 Table des Matières

- [Configuration de l'Environnement](#configuration-de-lenvironnement)
- [Standards de Code](#standards-de-code)
- [Tests](#tests)
- [Contribution](#contribution)
- [CI/CD](#cicd)
- [Debugging](#debugging)

---

## 🛠️ Configuration de l'Environnement

### Prérequis

- **Docker** : v20.10+ et Docker Compose v2.0+
- **Python** : v3.11+ (pour développement local)
- **Git** : v2.30+
- **Make** : (optionnel, pour les commandes simplifiées)

**Systèmes supportés** :
- Linux (Ubuntu 20.04+, Debian 11+)
- macOS (12+)
- Windows 10/11 avec WSL2

### Installation Locale

#### 1. Cloner le Repository

```bash
git clone https://github.com/your-org/data-platform.git
cd data-platform
```

#### 2. Créer l'Environnement Python

```bash
# Créer l'environnement virtuel
python3.11 -m venv venv_dremio_311

# Activer l'environnement
# Linux/macOS:
source venv_dremio_311/bin/activate
# Windows:
.\venv_dremio_311\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -e ".[dev]"
```

#### 3. Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec vos valeurs
nano .env
```

**Variables d'environnement essentielles** :

```bash
# Dremio
DREMIO_HOST=localhost
DREMIO_PORT=9047
DREMIO_USER=admin
DREMIO_PASSWORD=admin123

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Airbyte
AIRBYTE_API_URL=http://localhost:8000/api/v1

# OpenMetadata
OPENMETADATA_HOST=http://localhost:8585
OPENMETADATA_JWT_TOKEN=your-jwt-token

# Superset
SUPERSET_HOST=http://localhost:8088
SUPERSET_USERNAME=admin
SUPERSET_PASSWORD=admin
```

#### 4. Démarrer les Services Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état
docker-compose ps

# Voir les logs
docker-compose logs -f
```

#### 5. Initialisation

```bash
# Exécuter les scripts d'initialisation
python scripts/quickstart.py

# Vérifier la connectivité
python -c "from dremio_connector.clients import DremioClient; \
    client = DremioClient(); print('✓ Dremio OK')"
```

---

## 📝 Standards de Code

### Python Style Guide

Nous suivons **PEP 8** avec quelques exceptions :

```python
# ✅ GOOD
def calculate_customer_metrics(
    customer_id: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Calculate metrics for a specific customer.
    
    Args:
        customer_id: Unique customer identifier
        start_date: Start of the period
        end_date: End of the period
        
    Returns:
        Dictionary with calculated metrics
        
    Raises:
        ValueError: If dates are invalid
    """
    if end_date < start_date:
        raise ValueError("end_date must be after start_date")
    
    # Implementation
    return {
        "total_orders": 10,
        "total_revenue": 1500.00
    }

# ❌ BAD
def calc(c,s,e):
    if e<s: raise ValueError
    return {"t":10,"r":1500}
```

### Conventions de Nommage

| Type | Convention | Exemple |
|------|------------|---------|
| Variables | `snake_case` | `customer_data` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Fonctions | `snake_case` | `get_customer_info()` |
| Classes | `PascalCase` | `DremioClient` |
| Modules | `snake_case` | `dremio_client.py` |
| Packages | `lowercase` | `dremio_connector` |

### Type Hints

**Obligatoires** pour toutes les fonctions publiques :

```python
from typing import List, Dict, Optional, Union
from datetime import datetime

def fetch_orders(
    customer_id: str,
    start_date: Optional[datetime] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Fetch customer orders."""
    pass
```

### Docstrings

Format **Google Style** :

```python
def sync_data_source(source_name: str, force: bool = False) -> bool:
    """
    Synchronize a data source using Airbyte.
    
    Args:
        source_name: Name of the source to sync
        force: Force full refresh if True
        
    Returns:
        True if sync succeeded, False otherwise
        
    Raises:
        ConnectionError: If Airbyte is unreachable
        ValueError: If source_name is invalid
        
    Examples:
        >>> sync_data_source("postgres_prod")
        True
        
        >>> sync_data_source("invalid_source")
        ValueError: Source not found
    """
    pass
```

### Imports

Ordre standardisé :

```python
# 1. Standard library
import os
import sys
from datetime import datetime
from typing import Dict, List

# 2. Third-party
import pandas as pd
import requests
from sqlalchemy import create_engine

# 3. Local modules
from dremio_connector.clients import DremioClient
from dremio_connector.utils.logger import get_logger
```

### Linting

Nous utilisons plusieurs outils :

```bash
# Black (formatting)
black dremio_connector/ tests/

# isort (import sorting)
isort dremio_connector/ tests/

# flake8 (linting)
flake8 dremio_connector/ tests/

# mypy (type checking)
mypy dremio_connector/

# Tout en une commande
make lint
```

**Configuration dans `pyproject.toml`** :

```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## 🧪 Tests

### Structure des Tests

```
tests/
├── unit/                      # Tests unitaires
│   ├── test_dremio_client.py
│   ├── test_airbyte_client.py
│   └── test_utils.py
├── integration/               # Tests d'intégration
│   ├── test_dremio_integration.py
│   ├── test_airbyte_integration.py
│   └── test_openmetadata_integration.py
├── e2e/                      # Tests end-to-end
│   ├── test_full_pipeline.py
│   └── test_lineage_e2e.py
├── conftest.py               # Fixtures pytest
└── pytest.ini                # Configuration pytest
```

### Exécuter les Tests

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests avec coverage
pytest --cov=dremio_connector --cov-report=html

# Tests spécifiques
pytest tests/unit/test_dremio_client.py::test_connection

# Tests en parallèle
pytest -n auto

# Mode verbose
pytest -v

# Avec logs
pytest -s
```

### Écrire des Tests

#### Test Unitaire

```python
import pytest
from dremio_connector.clients import DremioClient

def test_client_initialization():
    """Test DremioClient initialization."""
    client = DremioClient(
        host="localhost",
        port=9047,
        username="admin",
        password="admin123"
    )
    assert client.host == "localhost"
    assert client.port == 9047

def test_invalid_connection():
    """Test connection with invalid credentials."""
    client = DremioClient(
        host="localhost",
        username="invalid",
        password="invalid"
    )
    with pytest.raises(ConnectionError):
        client.connect()
```

#### Test d'Intégration

```python
import pytest
from dremio_connector.clients import DremioClient

@pytest.fixture
def dremio_client():
    """Create a Dremio client for testing."""
    client = DremioClient(
        host="localhost",
        port=9047,
        username="admin",
        password="admin123"
    )
    yield client
    # Cleanup
    client.disconnect()

def test_execute_query(dremio_client):
    """Test query execution."""
    result = dremio_client.execute_query(
        "SELECT * FROM sys.options LIMIT 5"
    )
    assert len(result) == 5
    assert "name" in result[0]
```

#### Test avec Mocking

```python
from unittest.mock import Mock, patch
import pytest

def test_sync_with_mock():
    """Test sync with mocked Airbyte API."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "job": {"id": "123", "status": "succeeded"}
        }
        
        from dremio_connector.clients import AirbyteClient
        client = AirbyteClient()
        result = client.trigger_sync("connection-id")
        
        assert result["job"]["id"] == "123"
        mock_post.assert_called_once()
```

### Coverage

```bash
# Générer le rapport de coverage
pytest --cov=dremio_connector --cov-report=html

# Ouvrir le rapport
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Objectif** : Maintenir **> 80% de coverage**

---

## 🤝 Contribution

### Workflow Git

#### 1. Fork & Clone

```bash
# Fork sur GitHub, puis :
git clone https://github.com/YOUR_USERNAME/data-platform.git
cd data-platform
git remote add upstream https://github.com/original-org/data-platform.git
```

#### 2. Créer une Branche

```bash
# Convention : type/description
git checkout -b feature/add-snowflake-connector
git checkout -b fix/dremio-connection-timeout
git checkout -b docs/update-api-documentation
```

**Types de branches** :
- `feature/` : Nouvelles fonctionnalités
- `fix/` : Corrections de bugs
- `docs/` : Documentation
- `refactor/` : Refactoring
- `test/` : Tests
- `chore/` : Maintenance

#### 3. Développer

```bash
# Faire vos modifications
# ...

# Vérifier les standards
make lint
make test

# Committer
git add .
git commit -m "feat: Add Snowflake connector support

- Add SnowflakeClient class
- Implement connection and query methods
- Add unit tests (85% coverage)
- Update documentation

Closes #123"
```

**Convention de commits** (Conventional Commits) :

```
type(scope): subject

body

footer
```

**Types** :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

**Exemples** :

```bash
feat(dremio): Add support for Arrow Flight SQL
fix(airbyte): Handle connection timeout gracefully
docs(api): Update Dremio API examples
refactor(utils): Simplify logging configuration
test(integration): Add end-to-end pipeline test
```

#### 4. Push & Pull Request

```bash
# Push vers votre fork
git push origin feature/add-snowflake-connector

# Créer une Pull Request sur GitHub
```

**Template de PR** :

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

#### 5. Review & Merge

- Attendre l'approbation de 2+ reviewers
- CI/CD doit passer (tests, linting)
- Merge via "Squash and merge"

### Code Review Guidelines

**En tant que reviewer** :

✅ **À vérifier** :
- Logique correcte et performante
- Tests adéquats
- Documentation claire
- Pas de secrets exposés
- Style guide respecté

❌ **À éviter** :
- Commentaires vagues ("c'est mauvais")
- Changements de style non-essentiels
- Reviews sans tester localement

**En tant qu'auteur** :

✅ **Bonnes pratiques** :
- Petites PRs (< 400 lignes)
- Description claire
- Self-review avant soumission
- Répondre aux commentaires rapidement

---

## 🚀 CI/CD

### GitHub Actions Workflows

#### `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run linters
        run: |
          black --check dremio_connector/
          isort --check dremio_connector/
          flake8 dremio_connector/
          mypy dremio_connector/

  test:
    runs-on: ubuntu-latest
    services:
      dremio:
        image: dremio/dremio-oss:latest
        ports:
          - 9047:9047
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=dremio_connector --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

#### `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build package
        run: |
          pip install build
          python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### Pre-commit Hooks

**Installation** :

```bash
pip install pre-commit
pre-commit install
```

**Configuration `.pre-commit-config.yaml`** :

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

---

## 🐛 Debugging

### Logging

```python
from dremio_connector.utils.logger import get_logger

logger = get_logger(__name__)

# Niveaux de log
logger.debug("Detailed information for debugging")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.exception("Exception with traceback")
```

**Configuration** :

```python
# config/logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: default
    level: DEBUG
  file:
    class: logging.FileHandler
    filename: logs/app.log
    formatter: default
    level: INFO
root:
  level: INFO
  handlers: [console, file]
```

### Debugging with VS Code

**`.vscode/launch.json`** :

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "${file}"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Profiling

```bash
# CPU profiling
python -m cProfile -o profile.stats your_script.py
python -m pstats profile.stats

# Memory profiling
pip install memory_profiler
python -m memory_profiler your_script.py
```

---

## 📚 Ressources

- **Documentation API** : [../api/README.md](../api/README.md)
- **Architecture** : [../architecture/README.md](../architecture/README.md)
- **Guides** : [../guides/](../guides/)
- **Exemples** : [../../examples/](../../examples/)

---

**[← Retour à la documentation](../README.md)**
