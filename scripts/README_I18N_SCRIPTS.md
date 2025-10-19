# 🛠️ Scripts de Gestion Documentation Multilingue

**Scripts Shell (bash)** pour la maintenance de la documentation i18n

---

## 📁 Scripts Disponibles

### 1. `update-i18n-simple.sh`
Script de mise à jour automatique de la documentation multilingue (17 langues)

### 2. `validate-i18n.sh`
Script de validation complète de la documentation multilingue

---

## 🚀 Installation

### Prérequis
- **Linux/macOS** : Aucun prérequis (bash natif)
- **Windows** : WSL (Windows Subsystem for Linux) ou Git Bash

### Rendre les scripts exécutables

```bash
chmod +x scripts/update-i18n-simple.sh
chmod +x scripts/validate-i18n.sh
```

---

## 📖 Guide d'Utilisation

### Script de Mise à Jour

#### Syntaxe
```bash
./scripts/update-i18n-simple.sh [OPTIONS]
```

#### Options
- `-v, --version VERSION` : Version cible (défaut: 3.3.1)
- `-d, --date DATE` : Date cible au format ISO (défaut: 2025-10-19)
- `--dry-run` : Mode test sans modification

#### Exemples

**Test sans modification** :
```bash
./scripts/update-i18n-simple.sh --dry-run
```

**Mise à jour avec paramètres par défaut** :
```bash
./scripts/update-i18n-simple.sh
```

**Mise à jour personnalisée** :
```bash
./scripts/update-i18n-simple.sh -v "3.4.0" -d "2025-11-01"
```

**Avec WSL (Windows)** :
```bash
wsl bash -c "cd /mnt/c/projets/dremiodbt && ./scripts/update-i18n-simple.sh"
```

---

### Script de Validation

#### Syntaxe
```bash
./scripts/validate-i18n.sh
```

#### Sortie
Le script effectue 6 tests :
1. ✅ Nombre de fichiers (17 attendus)
2. ✅ Versions (3.3.1 partout)
3. ✅ Dates (2025-10-19 ou formats localisés)
4. ✅ Anciennes versions (aucune 3.2.5)
5. ✅ Anciennes dates (aucune 2025-10-15)
6. ✅ Encodage UTF-8

#### Codes de Retour
- `0` : Tous les tests passent ✅
- `1` : Au moins un test échoue ❌

#### Exemple
```bash
./scripts/validate-i18n.sh
```

**Avec WSL (Windows)** :
```bash
wsl bash -c "cd /mnt/c/projets/dremiodbt && ./scripts/validate-i18n.sh"
```

---

## 🌍 Langues Supportées

Le script gère **17 langues** avec leurs formats de date spécifiques :

| Code | Langue | Format de Date | Exemple |
|------|--------|----------------|---------|
| ar | العربية (Arabe) | ISO | 2025-10-19 |
| cn | 中文 (Chinois) | ISO | 2025-10-19 |
| de | Deutsch (Allemand) | DD. Monat YYYY | 19. Oktober 2025 |
| es | Español (Espagnol) | DD de mes de YYYY | 19 de octubre de 2025 |
| fr | Français | DD mois YYYY | 19 octobre 2025 |
| hi | हिन्दी (Hindi) | DD महीना YYYY | 19 अक्टूबर 2025 |
| id | Indonesia | Month DD, YYYY | October 19, 2025 |
| it | Italiano (Italien) | DD mese YYYY | 19 ottobre 2025 |
| jp | 日本語 (Japonais) | ISO | 2025-10-19 |
| ko | 한국어 (Coréen) | YYYY년 MM월 DD일 | 2025년 10월 19일 |
| nl | Nederlands | DD maand YYYY | 19 oktober 2025 |
| pl | Polski (Polonais) | DD miesiąc YYYY | 19 października 2025 |
| pt | Português | ISO | 2025-10-19 |
| ru | Русский (Russe) | ISO | 2025-10-19 |
| se | Svenska (Suédois) | Month DD, YYYY | October 19, 2025 |
| tr | Türkçe (Turc) | DD Ay YYYY | 19 Ekim 2025 |
| vi | Tiếng Việt | DD Tháng MM, YYYY | 19 Tháng 10, 2025 |

---

## 🔧 Fonctionnement Technique

### Script de Mise à Jour

Le script utilise `sed` pour remplacer :

**Versions** :
```bash
sed "s/3\.2\.5/3.3.1/g"
```

**Dates ISO** :
```bash
sed "s/2025-10-15/2025-10-19/g"
sed "s/2025-10-16/2025-10-19/g"
```

**Dates Localisées** :
```bash
# Français
sed "s/15 octobre 2025/19 octobre 2025/g"

# Allemand
sed "s/16\. Oktober 2025/19. Oktober 2025/g"

# Coréen
sed "s/2025년 10월 16일/2025년 10월 19일/g"

# etc.
```

### Script de Validation

Utilise `grep` pour vérifier la présence de :
- Version cible dans chaque fichier
- Date cible (ISO ou contenant "19")
- Absence d'anciennes versions/dates

---

## 📊 Exemple de Sortie

### Mise à Jour
```
========================================
  MISE A JOUR DOCUMENTATION MULTILINGUE
========================================

Version cible: 3.3.1
Date: 2025-10-19
Mode: PRODUCTION (modifications appliquees)

  [OK]  ar - Deja a jour
  [UPD] fr - Mis a jour
  [UPD] es - Mis a jour
  ...

========================================
  RESUME
========================================

Fichiers mis a jour: 3
Fichiers ignores:    0
Erreurs:             0
Total langues:       17

Mise a jour terminee!
Log cree: docs/i18n/UPDATE_LOG_3.3.1.md
```

### Validation
```
========================================
  VALIDATION DOCUMENTATION MULTILINGUE
========================================

Verification version: 3.3.1
Verification date: 2025-10-19
Langues attendues: 17

TEST 1: Nombre de fichiers
  [OK] 17 fichiers trouves

TEST 2: Versions
  [OK] 17/17 fichiers avec version 3.3.1

TEST 3: Dates
  [OK] 17/17 fichiers avec date 2025-10-19

...

========================================
  RESUME FINAL
========================================

STATUT: TOUS LES TESTS PASSES

La documentation multilingue est a jour et valide!
```

---

## 🎨 Codes Couleur

Les scripts utilisent des couleurs ANSI pour une meilleure lisibilité :

- 🟢 **Vert** : Succès / OK
- 🔴 **Rouge** : Erreur / FAIL
- 🟡 **Jaune** : Avertissement / WARN
- 🔵 **Cyan** : Informations / Titres
- 🟣 **Magenta** : Mode DryRun

---

## 📝 Fichiers Générés

### Log de Mise à Jour
```
docs/i18n/UPDATE_LOG_3.3.1.md
```

Contient :
- Date et heure d'exécution
- Liste des langues mises à jour
- Changements appliqués (version, dates)
- Commande de vérification

---

## 🔍 Dépannage

### Problème : Script non exécutable
```bash
# Solution
chmod +x scripts/update-i18n-simple.sh
chmod +x scripts/validate-i18n.sh
```

### Problème : Encodage UTF-8
```bash
# Vérifier l'encodage d'un fichier
file -b --mime-encoding docs/i18n/fr/README.md

# Devrait retourner: utf-8
```

### Problème : Dates non détectées
Le script de validation accepte :
- Dates ISO : `2025-10-19`
- Dates avec "19" : `19 octobre 2025`, `October 19, 2025`, etc.
- Formats localisés : `2025년 10월 19일`, `19 Ekim 2025`, etc.

---

## 🚦 Workflow Recommandé

### 1. Test en Mode DryRun
```bash
./scripts/update-i18n-simple.sh --dry-run
```

### 2. Application des Changements
```bash
./scripts/update-i18n-simple.sh
```

### 3. Validation
```bash
./scripts/validate-i18n.sh
```

### 4. Vérification Manuelle (optionnel)
```bash
# Lister les versions
grep -r "Version.*3.3.1" docs/i18n/*/README.md

# Lister les dates
grep -r "2025-10-19\|19.*2025" docs/i18n/*/README.md
```

---

## 📦 Intégration CI/CD

### GitHub Actions
```yaml
name: Validate i18n Documentation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate i18n
        run: |
          chmod +x scripts/validate-i18n.sh
          ./scripts/validate-i18n.sh
```

---

## 📞 Support

**Documentation** : `docs/i18n/`
- `README.md` - Vue d'ensemble
- `RESUME_FINAL_FR.md` - Résumé complet
- `VALIDATION_REPORT.md` - Rapport de validation
- `MULTILINGUAL_UPDATE_COMPLETE.md` - Documentation technique

**Scripts** : `scripts/`
- `update-i18n-simple.sh` - Mise à jour
- `validate-i18n.sh` - Validation

---

## ✅ Avantages des Scripts Shell

1. **Multiplateforme** : Linux, macOS, Windows (WSL/Git Bash)
2. **Pas de dépendances** : Utilisent seulement bash, sed, grep
3. **Légers** : Exécution rapide (< 5 secondes)
4. **Encodage UTF-8** : Support natif complet
5. **CI/CD Ready** : Faciles à intégrer dans pipelines
6. **Couleurs** : Sortie lisible et professionnelle
7. **Codes de retour** : Intégration facile dans scripts

---

**Version** : 1.0.0  
**Date** : 19 octobre 2025  
**Statut** : ✅ Opérationnel et Validé
