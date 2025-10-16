#!/bin/bash
# Script pour tester la connexion PostgreSQL à Dremio

echo "=========================================="
echo "Test de connexion PostgreSQL à Dremio"
echo "=========================================="

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Attendre que Dremio soit prêt
echo -e "${YELLOW}Attente du démarrage de Dremio...${NC}"
sleep 30

# Test 1: Vérifier que le port 31010 est ouvert
echo -e "\n${YELLOW}Test 1: Vérification du port 31010...${NC}"
if nc -zv localhost 31010 2>&1 | grep -q "succeeded"; then
    echo -e "${GREEN}✓ Port 31010 est accessible${NC}"
else
    echo -e "${RED}✗ Port 31010 n'est pas accessible${NC}"
    exit 1
fi

# Test 2: Tester la connexion avec psql (si disponible)
echo -e "\n${YELLOW}Test 2: Connexion avec psql...${NC}"
if command -v psql &> /dev/null; then
    PGPASSWORD=dremio_password psql -h localhost -p 31010 -U dremio_user -d dremio -c "SELECT 1;" 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Connexion PostgreSQL réussie${NC}"
    else
        echo -e "${YELLOW}! psql a échoué, mais cela peut être normal avant la première configuration${NC}"
    fi
else
    echo -e "${YELLOW}! psql n'est pas installé, test ignoré${NC}"
fi

# Test 3: Tester avec Python psycopg2
echo -e "\n${YELLOW}Test 3: Connexion avec Python psycopg2...${NC}"
python3 << 'PYTHON'
try:
    import psycopg2
    conn = psycopg2.connect(
        host='localhost',
        port=31010,
        user='dremio_user',
        password='dremio_password',
        database='dremio'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\033[0;32m✓ Connexion Python réussie\033[0m")
    print(f"Version: {version}")
    cursor.close()
    conn.close()
except ImportError:
    print("\033[1;33m! psycopg2 n'est pas installé. Installer avec: pip install psycopg2-binary\033[0m")
except Exception as e:
    print(f"\033[0;31m✗ Erreur de connexion: {e}\033[0m")
    print("\033[1;33mNote: Il faut d'abord créer un utilisateur dans Dremio UI\033[0m")
PYTHON

# Test 4: Vérifier l'UI Dremio
echo -e "\n${YELLOW}Test 4: Vérification de l'UI Dremio...${NC}"
if curl -s http://localhost:9047 > /dev/null; then
    echo -e "${GREEN}✓ UI Dremio accessible sur http://localhost:9047${NC}"
else
    echo -e "${RED}✗ UI Dremio non accessible${NC}"
fi

echo -e "\n${GREEN}=========================================="
echo "Tests terminés!"
echo "==========================================${NC}"
echo ""
echo "Prochaines étapes:"
echo "1. Accéder à http://localhost:9047"
echo "2. Créer un utilisateur admin"
echo "3. Créer un utilisateur 'dremio_user' avec mot de passe 'dremio_password'"
echo "4. Exécuter le script setup.sql pour créer les données d'exemple"
