#!/bin/bash
# Script de verification rapide de l'etat de la sandbox
# Usage: ./scripts/quick_check.sh

echo "=========================================="
echo "VERIFICATION RAPIDE - SANDBOX DREMIO"
echo "=========================================="
echo ""

# Services Docker
echo "[1] Services Docker"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(dremio|postgres|elasticsearch|minio)" | while read line; do
    echo "  $line"
done
echo ""

# PostgreSQL
echo "[2] PostgreSQL"
psql -h localhost -p 5432 -U dbt_user -d business_db -c "SELECT 'Clients: ' || COUNT(*) FROM customers UNION ALL SELECT 'Commandes: ' || COUNT(*) FROM orders;" 2>/dev/null || echo "  [ERREUR] Connexion impossible"
echo ""

# Elasticsearch
echo "[3] Elasticsearch"
curl -s http://localhost:9200/_cat/indices?v | grep -E "(application_logs|user_events|performance_metrics)" || echo "  [ERREUR] Indices non trouves"
echo ""

# MinIO
echo "[4] MinIO"
echo "  Console: http://localhost:9001"
echo "  Status: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:9001)"
echo ""

# Dremio
echo "[5] Dremio"
echo "  UI: http://localhost:9047"
echo "  Status: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:9047)"
echo ""

# Documentation
echo "[6] Documentation"
if [ -f "/mnt/c/projets/dremiodbt/README.md" ]; then
    lines=$(wc -l < /mnt/c/projets/dremiodbt/README.md)
    echo "  README.md: $lines lignes"
fi
if [ -f "/mnt/c/projets/dremiodbt/docs/QUICKSTART.md" ]; then
    echo "  QUICKSTART.md: OK"
fi
if [ -f "/mnt/c/projets/dremiodbt/docs/DEMO_GUIDE.md" ]; then
    echo "  DEMO_GUIDE.md: OK"
fi
echo ""

# dbt
echo "[7] Pipeline dbt"
cd /mnt/c/projets/dremiodbt/dbt 2>/dev/null
if [ -d "target" ]; then
    echo "  Documentation: Generee"
    model_count=$(find models -name "*.sql" | wc -l)
    echo "  Modeles: $model_count fichiers SQL"
else
    echo "  [INFO] Pas encore execute"
fi
echo ""

echo "=========================================="
echo "Verification terminee"
echo "=========================================="
