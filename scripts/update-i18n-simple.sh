#!/bin/bash
# ============================================================================
# Script de Mise a Jour Documentation Multilingue
# Version: 1.0.0
# Date: 19 Octobre 2025
# ============================================================================

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Paramètres par défaut
NEW_VERSION="3.3.1"
UPDATE_DATE="2025-10-19"
DRY_RUN=false

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            NEW_VERSION="$2"
            shift 2
            ;;
        -d|--date)
            UPDATE_DATE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Usage: $0 [-v|--version VERSION] [-d|--date DATE] [--dry-run]"
            exit 1
            ;;
    esac
done

echo -e "\n${CYAN}========================================${NC}"
echo -e "${CYAN}  MISE A JOUR DOCUMENTATION MULTILINGUE${NC}"
echo -e "${CYAN}========================================${NC}\n"

echo -e "${YELLOW}Version cible: $NEW_VERSION${NC}"
echo -e "${YELLOW}Date: $UPDATE_DATE${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "${MAGENTA}Mode: DRY RUN (aucune modification)${NC}\n"
else
    echo -e "${GREEN}Mode: PRODUCTION (modifications appliquees)${NC}\n"
fi

# Liste des répertoires de langues
LANG_DIRS=(
    "docs/i18n/ar"
    "docs/i18n/cn"
    "docs/i18n/de"
    "docs/i18n/es"
    "docs/i18n/fr"
    "docs/i18n/hi"
    "docs/i18n/id"
    "docs/i18n/it"
    "docs/i18n/jp"
    "docs/i18n/ko"
    "docs/i18n/nl"
    "docs/i18n/pl"
    "docs/i18n/pt"
    "docs/i18n/ru"
    "docs/i18n/se"
    "docs/i18n/tr"
    "docs/i18n/vi"
)

UPDATED_FILES=0
SKIPPED_FILES=0
ERROR_FILES=0

# Traiter chaque langue
for LANG_DIR in "${LANG_DIRS[@]}"; do
    README_PATH="$LANG_DIR/README.md"
    LANG_CODE=$(basename "$LANG_DIR")
    
    if [ ! -f "$README_PATH" ]; then
        echo -e "  ${YELLOW}[SKIP] $LANG_CODE - Fichier non trouve${NC}"
        ((SKIPPED_FILES++))
        continue
    fi
    
    # Créer un fichier temporaire
    TEMP_FILE=$(mktemp)
    
    # Lire et modifier le contenu
    if cat "$README_PATH" | \
        sed "s/3\.2\.5/$NEW_VERSION/g" | \
        sed "s/2025-10-15/$UPDATE_DATE/g" | \
        sed "s/2025-10-16/$UPDATE_DATE/g" | \
        sed "s/15 octobre 2025/19 octobre 2025/g" | \
        sed "s/16 octobre 2025/19 octobre 2025/g" | \
        sed "s/October 15, 2025/October 19, 2025/g" | \
        sed "s/October 16, 2025/October 19, 2025/g" | \
        sed "s/15 de octubre de 2025/19 de octubre de 2025/g" | \
        sed "s/16 de octubre de 2025/19 de octubre de 2025/g" | \
        sed "s/15\. Oktober 2025/19. Oktober 2025/g" | \
        sed "s/16\. Oktober 2025/19. Oktober 2025/g" | \
        sed "s/15 ottobre 2025/19 ottobre 2025/g" | \
        sed "s/16 ottobre 2025/19 ottobre 2025/g" | \
        sed "s/15 de outubro de 2025/19 de outubro de 2025/g" | \
        sed "s/16 de outubro de 2025/19 de outubro de 2025/g" | \
        sed "s/15 października 2025/19 października 2025/g" | \
        sed "s/16 października 2025/19 października 2025/g" | \
        sed "s/15 oktober 2025/19 oktober 2025/g" | \
        sed "s/16 oktober 2025/19 oktober 2025/g" | \
        sed "s/15 अक्टूबर 2025/19 अक्टूबर 2025/g" | \
        sed "s/16 अक्टूबर 2025/19 अक्टूबर 2025/g" | \
        sed "s/16 Ekim 2025/19 Ekim 2025/g" | \
        sed "s/15 Ekim 2025/19 Ekim 2025/g" | \
        sed "s/16 Tháng 10, 2025/19 Tháng 10, 2025/g" | \
        sed "s/15 Tháng 10, 2025/19 Tháng 10, 2025/g" | \
        sed "s/2025년 10월 15일/2025년 10월 19일/g" | \
        sed "s/2025년 10월 16일/2025년 10월 19일/g" > "$TEMP_FILE"; then
        
        # Vérifier si des changements ont été faits
        if ! diff -q "$README_PATH" "$TEMP_FILE" > /dev/null 2>&1; then
            if [ "$DRY_RUN" = true ]; then
                echo -e "  ${CYAN}[DRY] $LANG_CODE - Serait mis a jour${NC}"
            else
                cp "$TEMP_FILE" "$README_PATH"
                echo -e "  ${GREEN}[UPD] $LANG_CODE - Mis a jour${NC}"
            fi
            ((UPDATED_FILES++))
        else
            echo -e "  [OK]  $LANG_CODE - Deja a jour"
        fi
    else
        echo -e "  ${RED}[ERR] $LANG_CODE - Erreur de traitement${NC}"
        ((ERROR_FILES++))
    fi
    
    rm -f "$TEMP_FILE"
done

# Résumé
echo -e "\n${CYAN}========================================${NC}"
echo -e "${CYAN}  RESUME${NC}"
echo -e "${CYAN}========================================${NC}\n"

echo -e "${GREEN}Fichiers mis a jour: $UPDATED_FILES${NC}"
echo -e "${YELLOW}Fichiers ignores:    $SKIPPED_FILES${NC}"
echo -e "${RED}Erreurs:             $ERROR_FILES${NC}"
echo -e "${CYAN}Total langues:       ${#LANG_DIRS[@]}${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "\n${MAGENTA}Mode DRY RUN - Executez sans --dry-run pour appliquer${NC}"
else
    echo -e "\n${GREEN}Mise a jour terminee!${NC}"
    
    # Créer un changelog
    CHANGELOG_FILE="docs/i18n/UPDATE_LOG_$NEW_VERSION.md"
    cat > "$CHANGELOG_FILE" << EOF
# Documentation Multilingue - Mise a Jour v$NEW_VERSION

Date: $UPDATE_DATE
Fichiers mis a jour: $UPDATED_FILES / ${#LANG_DIRS[@]}

## Changements

Version: 3.2.5 -> $NEW_VERSION
Date: 2025-10-15 -> $UPDATE_DATE

## Langues Mises a Jour

EOF

    for LANG_DIR in "${LANG_DIRS[@]}"; do
        LANG_CODE=$(basename "$LANG_DIR")
        if [ -f "$LANG_DIR/README.md" ]; then
            echo "- $LANG_CODE" >> "$CHANGELOG_FILE"
        fi
    done

    cat >> "$CHANGELOG_FILE" << EOF

## Verification

Pour verifier:
find docs/i18n -name "README.md" -exec grep -l "$NEW_VERSION" {} \;

Script: scripts/update-i18n-simple.sh
Execute: $(date '+%Y-%m-%d %H:%M:%S')
EOF

    echo -e "Log cree: ${CYAN}$CHANGELOG_FILE${NC}\n"
fi

echo ""
exit $([ $ERROR_FILES -gt 0 ] && echo 1 || echo 0)
