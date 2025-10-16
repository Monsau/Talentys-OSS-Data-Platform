#!/bin/bash
# Script pour activer le venv Python et exécuter dbt run + dbt test sous WSL/Linux

set -e

PROJECT_ROOT="$(dirname "$(realpath "$0")")"
cd "$PROJECT_ROOT"
source venv/bin/activate
cd dbt
echo "=== dbt run ==="
dbt run
echo "=== dbt test ==="
dbt test
echo "=== Terminé ==="