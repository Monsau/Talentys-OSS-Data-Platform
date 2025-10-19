#!/bin/bash
# ============================================================================
# Script de Validation Documentation Multilingue
# Version: 1.0.0
# Date: 19 Octobre 2025
# ============================================================================

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

TARGET_VERSION="3.3.1"
TARGET_DATE="2025-10-19"
EXPECTED_LANGUAGES=17

echo -e "\n${CYAN}========================================${NC}"
echo -e "${CYAN}  VALIDATION DOCUMENTATION MULTILINGUE${NC}"
echo -e "${CYAN}========================================${NC}\n"

echo -e "${YELLOW}Verification version: $TARGET_VERSION${NC}"
echo -e "${YELLOW}Verification date: $TARGET_DATE${NC}"
echo -e "${YELLOW}Langues attendues: $EXPECTED_LANGUAGES${NC}\n"

# Liste des fichiers README
README_FILES=(docs/i18n/*/README.md)
FILE_COUNT=${#README_FILES[@]}

# TEST 1: Nombre de fichiers
echo -e "${CYAN}TEST 1: Nombre de fichiers${NC}"
if [ "$FILE_COUNT" -eq "$EXPECTED_LANGUAGES" ]; then
    echo -e "  ${GREEN}[OK] $FILE_COUNT fichiers trouves${NC}"
    TEST1_PASS=true
else
    echo -e "  ${RED}[FAIL] $FILE_COUNT fichiers trouves (attendu: $EXPECTED_LANGUAGES)${NC}"
    TEST1_PASS=false
fi

# TEST 2: Versions
echo -e "\n${CYAN}TEST 2: Versions${NC}"
VERSION_COUNT=0
for file in "${README_FILES[@]}"; do
    if grep -q "$TARGET_VERSION" "$file" 2>/dev/null; then
        ((VERSION_COUNT++))
    fi
done

if [ "$VERSION_COUNT" -eq "$EXPECTED_LANGUAGES" ]; then
    echo -e "  ${GREEN}[OK] $VERSION_COUNT/$EXPECTED_LANGUAGES fichiers avec version $TARGET_VERSION${NC}"
    TEST2_PASS=true
else
    echo -e "  ${RED}[FAIL] $VERSION_COUNT/$EXPECTED_LANGUAGES fichiers avec version $TARGET_VERSION${NC}"
    TEST2_PASS=false
fi

# TEST 3: Dates
echo -e "\n${CYAN}TEST 3: Dates${NC}"
DATE_COUNT=0
for file in "${README_FILES[@]}"; do
    # Accepter soit la date ISO, soit "19" dans la date (formats localisés)
    if grep -q "$TARGET_DATE\|19.*2025\|2025.*19" "$file" 2>/dev/null; then
        ((DATE_COUNT++))
    fi
done

if [ "$DATE_COUNT" -eq "$EXPECTED_LANGUAGES" ]; then
    echo -e "  ${GREEN}[OK] $DATE_COUNT/$EXPECTED_LANGUAGES fichiers avec date $TARGET_DATE${NC}"
    TEST3_PASS=true
else
    echo -e "  ${RED}[FAIL] $DATE_COUNT/$EXPECTED_LANGUAGES fichiers avec date $TARGET_DATE${NC}"
    TEST3_PASS=false
fi

# TEST 4: Anciennes versions
echo -e "\n${CYAN}TEST 4: Anciennes versions${NC}"
OLD_VERSION_COUNT=0
for file in "${README_FILES[@]}"; do
    if grep -q "3\.2\.5" "$file" 2>/dev/null; then
        ((OLD_VERSION_COUNT++))
    fi
done

if [ "$OLD_VERSION_COUNT" -eq 0 ]; then
    echo -e "  ${GREEN}[OK] Aucune version 3.2.5 trouvee${NC}"
    TEST4_PASS=true
else
    echo -e "  ${YELLOW}[WARN] $OLD_VERSION_COUNT fichiers contiennent encore 3.2.5${NC}"
    TEST4_PASS=false
fi

# TEST 5: Anciennes dates
echo -e "\n${CYAN}TEST 5: Anciennes dates${NC}"
OLD_DATE_COUNT=0
for file in "${README_FILES[@]}"; do
    if grep -q "2025-10-15" "$file" 2>/dev/null; then
        ((OLD_DATE_COUNT++))
    fi
done

if [ "$OLD_DATE_COUNT" -eq 0 ]; then
    echo -e "  ${GREEN}[OK] Aucune date 2025-10-15 trouvee${NC}"
    TEST5_PASS=true
else
    echo -e "  ${YELLOW}[WARN] $OLD_DATE_COUNT fichiers contiennent encore 2025-10-15${NC}"
    TEST5_PASS=false
fi

# TEST 6: Encodage UTF-8
echo -e "\n${CYAN}TEST 6: Encodage UTF-8${NC}"
ENCODING_ISSUES=0
for file in "${README_FILES[@]}"; do
    if ! file -b --mime-encoding "$file" | grep -q "utf-8\|us-ascii" 2>/dev/null; then
        LANG_CODE=$(basename "$(dirname "$file")")
        echo -e "  ${RED}[ERR] $LANG_CODE - Erreur encodage${NC}"
        ((ENCODING_ISSUES++))
    fi
done

if [ "$ENCODING_ISSUES" -eq 0 ]; then
    echo -e "  ${GREEN}[OK] Encodage UTF-8 valide pour toutes les langues${NC}"
    TEST6_PASS=true
else
    echo -e "  ${YELLOW}[WARN] $ENCODING_ISSUES problemes d'encodage detectes${NC}"
    TEST6_PASS=false
fi

# Détails par langue
echo -e "\n${CYAN}========================================${NC}"
echo -e "${CYAN}  DETAILS PAR LANGUE${NC}"
echo -e "${CYAN}========================================${NC}\n"

# Noms des langues
declare -A LANG_NAMES=(
    ["ar"]="Arabe"
    ["cn"]="Chinois"
    ["de"]="Allemand"
    ["es"]="Espagnol"
    ["fr"]="Francais"
    ["hi"]="Hindi"
    ["id"]="Indonesien"
    ["it"]="Italien"
    ["jp"]="Japonais"
    ["ko"]="Coreen"
    ["nl"]="Neerlandais"
    ["pl"]="Polonais"
    ["pt"]="Portugais"
    ["ru"]="Russe"
    ["se"]="Suedois"
    ["tr"]="Turc"
    ["vi"]="Vietnamien"
)

for file in "${README_FILES[@]}"; do
    LANG_CODE=$(basename "$(dirname "$file")")
    LANG_NAME=${LANG_NAMES[$LANG_CODE]:-$LANG_CODE}
    
    HAS_VERSION=false
    HAS_DATE=false
    
    if grep -q "$TARGET_VERSION" "$file" 2>/dev/null; then
        HAS_VERSION=true
    fi
    
    if grep -q "$TARGET_DATE\|19.*2025" "$file" 2>/dev/null; then
        HAS_DATE=true
    fi
    
    if [ "$HAS_VERSION" = true ] && [ "$HAS_DATE" = true ]; then
        echo -e "  ${GREEN}[OK] $LANG_CODE ($LANG_NAME)${NC}"
    else
        LINE="  ${RED}[!!] $LANG_CODE ($LANG_NAME)${NC}"
        [ "$HAS_VERSION" = false ] && LINE="${LINE} - VERSION MANQUANTE"
        [ "$HAS_DATE" = false ] && LINE="${LINE} - DATE MANQUANTE"
        echo -e "$LINE"
    fi
done

# Résumé final
echo -e "\n${CYAN}========================================${NC}"
echo -e "${CYAN}  RESUME FINAL${NC}"
echo -e "${CYAN}========================================${NC}\n"

ALL_TESTS_PASSED=true
[ "$TEST1_PASS" = false ] && ALL_TESTS_PASSED=false
[ "$TEST2_PASS" = false ] && ALL_TESTS_PASSED=false
[ "$TEST3_PASS" = false ] && ALL_TESTS_PASSED=false
[ "$TEST4_PASS" = false ] && ALL_TESTS_PASSED=false
[ "$TEST5_PASS" = false ] && ALL_TESTS_PASSED=false
[ "$TEST6_PASS" = false ] && ALL_TESTS_PASSED=false

if [ "$ALL_TESTS_PASSED" = true ]; then
    echo -e "${GREEN}STATUT: TOUS LES TESTS PASSES${NC}"
    echo -e "\n${GREEN}La documentation multilingue est a jour et valide!${NC}\n"
    exit 0
else
    echo -e "${RED}STATUT: CERTAINS TESTS ONT ECHOUE${NC}"
    echo -e "\n${YELLOW}Verifiez les problemes ci-dessus.${NC}\n"
    exit 1
fi
