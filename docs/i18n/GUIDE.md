# 📚 Guide Complet - Documentation Multilingue

**Version** : 3.3.1  
**Date** : 19 octobre 2025  
**Langues supportées** : 17

---

## 🌍 Vue d'Ensemble

La plateforme supporte **17 langues** avec documentation complète :

| Région | Langues |
|--------|---------|
| 🌏 **Asie** | Chinois (cn), Japonais (jp), Coréen (ko), Hindi (hi), Indonésien (id), Vietnamien (vi) |
| 🌍 **Europe** | Français (fr), Allemand (de), Espagnol (es), Italien (it), Portugais (pt), Polonais (pl), Néerlandais (nl), Suédois (se), Russe (ru) |
| 🌎 **Moyen-Orient** | Arabe (ar), Turc (tr) |

**Structure** : `docs/i18n/{code_langue}/README.md`

---

## 🛠️ Scripts de Gestion

### Scripts Shell (Recommandés)

#### Mise à Jour
```bash
# Test sans modification
./scripts/update-i18n-simple.sh --dry-run

# Application
./scripts/update-i18n-simple.sh

# Personnalisé
./scripts/update-i18n-simple.sh -v "3.4.0" -d "2025-11-01"
```

#### Validation
```bash
./scripts/validate-i18n.sh
```

### Windows (WSL)
```bash
wsl bash -c "cd /mnt/c/projets/dremiodbt && ./scripts/update-i18n-simple.sh"
```

### Scripts PowerShell (Legacy)
```powershell
.\scripts\update-i18n-simple.ps1 -DryRun
.\scripts\validate-i18n.ps1
```

**Documentation détaillée** : `scripts/README_I18N_SCRIPTS.md`

---

## 📋 Formats de Date par Langue

| Langue | Code | Format | Exemple |
|--------|------|--------|---------|
| Arabe | ar | ISO | 2025-10-19 |
| Chinois | cn | ISO | 2025-10-19 |
| Allemand | de | DD. Monat YYYY | 19. Oktober 2025 |
| Espagnol | es | DD de mes YYYY | 19 de octubre de 2025 |
| Français | fr | DD mois YYYY | 19 octobre 2025 |
| Hindi | hi | DD महीना YYYY | 19 अक्टूबर 2025 |
| Indonésien | id | Month DD, YYYY | October 19, 2025 |
| Italien | it | DD mese YYYY | 19 ottobre 2025 |
| Japonais | jp | ISO | 2025-10-19 |
| Coréen | ko | YYYY년 MM월 DD일 | 2025년 10월 19일 |
| Néerlandais | nl | DD maand YYYY | 19 oktober 2025 |
| Polonais | pl | DD miesiąc YYYY | 19 października 2025 |
| Portugais | pt | ISO | 2025-10-19 |
| Russe | ru | ISO | 2025-10-19 |
| Suédois | se | Month DD, YYYY | October 19, 2025 |
| Turc | tr | DD Ay YYYY | 19 Ekim 2025 |
| Vietnamien | vi | DD Tháng MM, YYYY | 19 Tháng 10, 2025 |

---

## ✅ Validation

### Tests Effectués

1. **Nombre de fichiers** : 17/17 ✅
2. **Versions** : 3.3.1 partout ✅
3. **Dates** : 19 octobre 2025 ✅
4. **Encodage** : UTF-8 valide ✅
5. **Anciennes versions** : Aucune ✅

### Commandes de Vérification

```bash
# Shell
find docs/i18n -name "README.md" -exec grep -l "3.3.1" {} \;

# PowerShell
Get-ChildItem -Path docs/i18n/*/README.md | Select-String -Pattern "3.3.1"
```

---

## 📝 Maintenance

### Workflow Recommandé

1. **Test** : `./scripts/update-i18n-simple.sh --dry-run`
2. **Application** : `./scripts/update-i18n-simple.sh`
3. **Validation** : `./scripts/validate-i18n.sh`

### Mise à Jour de Version

Pour passer de 3.3.1 à 3.4.0 :

```bash
./scripts/update-i18n-simple.sh -v "3.4.0" -d "2025-11-01" --dry-run
./scripts/update-i18n-simple.sh -v "3.4.0" -d "2025-11-01"
./scripts/validate-i18n.sh
```

### Ajout d'une Nouvelle Langue

1. Créer `docs/i18n/{code}/README.md`
2. Ajouter le code dans `update-i18n-simple.sh` (tableau `LANG_DIRS`)
3. Ajouter le format de date si nécessaire
4. Tester avec `--dry-run`

---

## 🔧 Caractéristiques Techniques

### Scripts Shell
- **Taille** : ~6 KB chacun
- **Dépendances** : bash, sed, grep, file
- **Encodage** : UTF-8 natif
- **Plateformes** : Linux, macOS, Windows (WSL/Git Bash)
- **Performance** : < 5 secondes

### Support Unicode
- ✅ Scripts arabes (RTL)
- ✅ Caractères chinois/japonais/coréens (CJK)
- ✅ Devanagari (Hindi)
- ✅ Cyrillique (Russe)
- ✅ Accents européens

---

## 📦 CI/CD

### GitHub Actions
```yaml
name: Validate i18n
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate
        run: |
          chmod +x scripts/validate-i18n.sh
          ./scripts/validate-i18n.sh
```

---

## 📞 Ressources

**Documentation** :
- `README.md` - Vue d'ensemble
- `RESUME_FINAL_FR.md` - Résumé complet
- `UPDATE_LOG_3.3.1.md` - Historique
- `GUIDE.md` - Ce guide
- `scripts/README_I18N_SCRIPTS.md` - Documentation scripts

**Scripts** :
- `scripts/update-i18n-simple.sh` - Mise à jour
- `scripts/validate-i18n.sh` - Validation

---

## 🎯 Statut Actuel

- ✅ **17 langues** opérationnelles
- ✅ **Version 3.3.1** synchronisée
- ✅ **Dates** au 19 octobre 2025
- ✅ **Scripts Shell** recommandés
- ✅ **UTF-8** validé
- ✅ **100%** de réussite

---

*Guide mis à jour le 19 octobre 2025*
