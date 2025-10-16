#!/bin/bash
# Script pour générer et servir la documentation dbt avec lineage

set -e

PROJECT_ROOT="$(dirname "$(realpath "$0")")"
cd "$PROJECT_ROOT"
source venv/bin/activate
cd dbt

echo "=== Génération de la documentation dbt ==="
dbt docs generate

echo ""
echo "=== Lancement du serveur de documentation ==="
echo "📊 La documentation sera disponible sur: http://localhost:8080"
echo "🔗 Le lineage interactif sera visible dans l'onglet 'Lineage Graph'"
echo ""
echo "💡 Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

dbt docs serve --port 8080
