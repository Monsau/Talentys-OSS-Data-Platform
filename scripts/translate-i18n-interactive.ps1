# Script de Traduction Automatique i18n
# Traduit tout le contenu francais vers les 16 autres langues + anglais

param(
    [switch]$DryRun,
    [string]$TranslationService = "libre"  # Options: libre, deepl, google
)

$ErrorActionPreference = "Stop"

# Configuration
$SOURCE_LANG = "fr"
$BASE_PATH = "docs\i18n"

# Codes de langues pour les APIs de traduction
$LANG_CODES = @{
    "en" = @{code = "en"; name = "English"}
    "ar" = @{code = "ar"; name = "Arabic"}
    "cn" = @{code = "zh"; name = "Chinese"}
    "de" = @{code = "de"; name = "German"}
    "es" = @{code = "es"; name = "Spanish"}
    "hi" = @{code = "hi"; name = "Hindi"}
    "id" = @{code = "id"; name = "Indonesian"}
    "it" = @{code = "it"; name = "Italian"}
    "jp" = @{code = "ja"; name = "Japanese"}
    "ko" = @{code = "ko"; name = "Korean"}
    "nl" = @{code = "nl"; name = "Dutch"}
    "pl" = @{code = "pl"; name = "Polish"}
    "pt" = @{code = "pt"; name = "Portuguese"}
    "ru" = @{code = "ru"; name = "Russian"}
    "se" = @{code = "sv"; name = "Swedish"}
    "tr" = @{code = "tr"; name = "Turkish"}
    "vi" = @{code = "vi"; name = "Vietnamese"}
}

Write-Host "`n========================================"
Write-Host "TRADUCTION AUTOMATIQUE i18n" -ForegroundColor Yellow
Write-Host "========================================`n"

Write-Host "ATTENTION: La traduction automatique est en cours de preparation..." -ForegroundColor Yellow
Write-Host "Cette fonctionnalite necessite une API de traduction externe.`n" -ForegroundColor Yellow

Write-Host "Options disponibles:" -ForegroundColor Cyan
Write-Host "1. LibreTranslate (gratuit, auto-heberge)" -ForegroundColor White
Write-Host "2. DeepL API (payant, haute qualite)" -ForegroundColor White
Write-Host "3. Google Translate API (payant)" -ForegroundColor White
Write-Host "4. Copie du contenu francais (sans traduction)`n" -ForegroundColor White

Write-Host "Pour l'instant, je vais creer un script Python qui utilise" -ForegroundColor Cyan
Write-Host "des bibliotheques de traduction automatique gratuites.`n" -ForegroundColor Cyan

Write-Host "Voulez-vous continuer avec:" -ForegroundColor Yellow
Write-Host "  [1] Installer et utiliser googletrans (gratuit, Python)" -ForegroundColor Green
Write-Host "  [2] Copier le contenu francais sans traduction" -ForegroundColor Yellow
Write-Host "  [3] Annuler`n" -ForegroundColor Red

$choice = Read-Host "Votre choix (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host "`nCreation du script Python de traduction..." -ForegroundColor Green
        
        # Creer le script Python
        $pythonScript = @"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Traduction Automatique i18n
Utilise googletrans pour traduire le contenu francais vers toutes les langues
"""

import os
import sys
from pathlib import Path
import time

try:
    from googletrans import Translator
    print("✓ googletrans est installe")
except ImportError:
    print("✗ googletrans n'est pas installe")
    print("\nInstallation en cours...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0-rc1"])
    from googletrans import Translator
    print("✓ googletrans installe avec succes")

# Configuration
BASE_PATH = Path("docs/i18n")
SOURCE_LANG = "fr"

LANG_MAPPING = {
    "en": "en", "ar": "ar", "cn": "zh-cn", "de": "de",
    "es": "es", "hi": "hi", "id": "id", "it": "it",
    "jp": "ja", "ko": "ko", "nl": "nl", "pl": "pl",
    "pt": "pt", "ru": "ru", "se": "sv", "tr": "tr", "vi": "vi"
}

def translate_text(text, target_lang, translator):
    """Traduit un texte vers la langue cible"""
    try:
        # Ne pas traduire les blocs de code et les URLs
        if text.startswith('```') or text.startswith('http') or text.startswith('['):
            return text
        
        # Traduction
        result = translator.translate(text, src='fr', dest=target_lang)
        time.sleep(0.5)  # Rate limiting
        return result.text
    except Exception as e:
        print(f"  Erreur traduction: {e}")
        return text

def translate_file(source_file, target_file, target_lang, translator):
    """Traduit un fichier markdown complet"""
    print(f"  Traduction: {source_file.name} -> {target_lang}")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    translated_lines = []
    in_code_block = False
    
    for line in lines:
        # Gerer les blocs de code
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            translated_lines.append(line)
            continue
        
        if in_code_block:
            translated_lines.append(line)
            continue
        
        # Traduire ligne par ligne
        if line.strip():
            translated_line = translate_text(line.strip(), target_lang, translator)
            translated_lines.append(translated_line + '\n')
        else:
            translated_lines.append(line)
    
    # Ecrire le fichier traduit
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)

def main():
    print("\n" + "="*50)
    print("TRADUCTION AUTOMATIQUE i18n")
    print("="*50 + "\n")
    
    translator = Translator()
    
    # Obtenir tous les fichiers francais
    fr_path = BASE_PATH / SOURCE_LANG
    fr_files = list(fr_path.rglob("*.md"))
    
    # Exclure certains fichiers
    fr_files = [f for f in fr_files if not any(x in f.name for x in ['DOCUMENTATION_', 'MISE_A_JOUR_'])]
    
    print(f"Fichiers a traduire: {len(fr_files)}")
    print(f"Langues cibles: {len(LANG_MAPPING)}\n")
    
    total_files = len(fr_files) * len(LANG_MAPPING)
    current = 0
    
    # Pour chaque langue cible
    for lang_code, google_code in LANG_MAPPING.items():
        print(f"\n[{lang_code.upper()}] Traduction vers {google_code}...")
        
        for source_file in fr_files:
            current += 1
            progress = (current / total_files) * 100
            
            # Determiner le chemin cible
            rel_path = source_file.relative_to(fr_path)
            target_file = BASE_PATH / lang_code / rel_path
            
            print(f"  [{progress:.1f}%] {rel_path}")
            
            try:
                translate_file(source_file, target_file, google_code, translator)
                print(f"    ✓ Traduit")
            except Exception as e:
                print(f"    ✗ Erreur: {e}")
    
    print("\n" + "="*50)
    print("TRADUCTION TERMINEE")
    print("="*50)
    print(f"\nTotal: {total_files} fichiers traduits")

if __name__ == "__main__":
    main()
"@
        
        Set-Content -Path "scripts\translate-i18n-auto.py" -Value $pythonScript -Encoding UTF8
        Write-Host "✓ Script Python cree: scripts\translate-i18n-auto.py" -ForegroundColor Green
        
        Write-Host "`nExecution du script Python..." -ForegroundColor Cyan
        Write-Host "Cela peut prendre 10-20 minutes...`n" -ForegroundColor Yellow
        
        python scripts\translate-i18n-auto.py
    }
    
    "2" {
        Write-Host "`nCopie du contenu francais (sans traduction)..." -ForegroundColor Yellow
        Write-Host "Cette option copie le contenu FR dans toutes les langues." -ForegroundColor Yellow
        Write-Host "Utile pour avoir du contenu immediatement.`n" -ForegroundColor Yellow
        
        # Creer un script simple qui copie
        $copyScript = @"
# Copie simple du contenu francais vers toutes les langues
`$SOURCE = "docs\i18n\fr"
`$LANGS = @("ar", "cn", "de", "es", "hi", "id", "it", "jp", "ko", "nl", "pl", "pt", "ru", "se", "tr", "vi", "en")

foreach (`$lang in `$LANGS) {
    Write-Host "Copie vers `$lang..." -ForegroundColor Cyan
    
    `$files = Get-ChildItem -Path `$SOURCE -Recurse -File -Name | Where-Object { `$_ -notmatch "DOCUMENTATION_|MISE_A_JOUR_" }
    
    foreach (`$file in `$files) {
        `$source_file = Join-Path `$SOURCE `$file
        `$target_file = Join-Path "docs\i18n\`$lang" `$file
        `$target_dir = Split-Path `$target_file -Parent
        
        if (-not (Test-Path `$target_dir)) {
            New-Item -ItemType Directory -Path `$target_dir -Force | Out-Null
        }
        
        Copy-Item -Path `$source_file -Destination `$target_file -Force
        Write-Host "  ✓ `$file" -ForegroundColor Green
    }
}

Write-Host "`nCopie terminee!" -ForegroundColor Green
"@
        
        Set-Content -Path "scripts\copy-fr-content.ps1" -Value $copyScript -Encoding UTF8
        Write-Host "✓ Script de copie cree: scripts\copy-fr-content.ps1" -ForegroundColor Green
        
        $confirm = Read-Host "`nVoulez-vous executer la copie maintenant? (o/n)"
        if ($confirm -eq "o") {
            & "scripts\copy-fr-content.ps1"
        }
    }
    
    "3" {
        Write-Host "`nAnnule." -ForegroundColor Red
        exit
    }
    
    default {
        Write-Host "`nChoix invalide. Annule." -ForegroundColor Red
        exit
    }
}
