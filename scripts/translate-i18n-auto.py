#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Traduction Automatique i18n
Traduit le contenu français vers 17 langues (dont anglais)
Utilise googletrans (gratuit)
"""

import os
import sys
from pathlib import Path
import time
import re

# Installation automatique si nécessaire
try:
    from googletrans import Translator
    print("✓ googletrans installé")
except ImportError:
    print("✗ googletrans non installé. Installation...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0-rc1"])
    from googletrans import Translator
    print("✓ googletrans installé!")

# Configuration
BASE_PATH = Path("docs/i18n")
SOURCE_LANG = "fr"

# Mapping des codes de langues
LANG_MAPPING = {
    "en": {"code": "en", "name": "English"},
    "ar": {"code": "ar", "name": "Arabic"},
    "cn": {"code": "zh-cn", "name": "Chinese"},
    "de": {"code": "de", "name": "German"},
    "es": {"code": "es", "name": "Spanish"},
    "hi": {"code": "hi", "name": "Hindi"},
    "id": {"code": "id", "name": "Indonesian"},
    "it": {"code": "it", "name": "Italian"},
    "jp": {"code": "ja", "name": "Japanese"},
    "ko": {"code": "ko", "name": "Korean"},
    "nl": {"code": "nl", "name": "Dutch"},
    "pl": {"code": "pl", "name": "Polish"},
    "pt": {"code": "pt", "name": "Portuguese"},
    "ru": {"code": "ru", "name": "Russian"},
    "se": {"code": "sv", "name": "Swedish"},
    "tr": {"code": "tr", "name": "Turkish"},
    "vi": {"code": "vi", "name": "Vietnamese"}
}

def should_translate_line(line):
    """Détermine si une ligne doit être traduite"""
    stripped = line.strip()
    
    # Ne pas traduire les lignes vides
    if not stripped:
        return False
    
    # Ne pas traduire les marqueurs de code
    if stripped.startswith('```'):
        return False
    
    # Ne pas traduire les URLs
    if stripped.startswith('http'):
        return False
    
    # Ne pas traduire les commandes shell/code
    if stripped.startswith('$') or stripped.startswith('#') or stripped.startswith('//'):
        return False
    
    return True

def translate_markdown_line(line, target_lang, translator):
    """Traduit une ligne markdown en préservant la syntaxe"""
    stripped = line.strip()
    
    if not should_translate_line(line):
        return line
    
    try:
        # Extraire et préserver les liens markdown [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.findall(link_pattern, stripped)
        
        # Remplacer temporairement les liens
        temp_line = stripped
        for i, (text, url) in enumerate(links):
            temp_line = temp_line.replace(f'[{text}]({url})', f'___LINK{i}___')
        
        # Traduire
        result = translator.translate(temp_line, src='fr', dest=target_lang)
        translated = result.text
        
        # Restaurer les liens
        for i, (text, url) in enumerate(links):
            # Traduire le texte du lien
            link_text_translated = translator.translate(text, src='fr', dest=target_lang).text
            translated = translated.replace(f'___LINK{i}___', f'[{link_text_translated}]({url})')
        
        # Préserver l'indentation
        indent = len(line) - len(line.lstrip())
        return ' ' * indent + translated + '\n'
        
    except Exception as e:
        print(f"      ⚠ Erreur traduction: {str(e)[:50]}")
        return line

def translate_file(source_file, target_file, lang_code, target_lang_code, translator):
    """Traduit un fichier markdown complet"""
    rel_path = source_file.relative_to(BASE_PATH / SOURCE_LANG)
    print(f"  📄 {rel_path} -> {lang_code}")
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"      ✗ Erreur lecture: {e}")
        return False
    
    translated_lines = []
    in_code_block = False
    line_count = len(lines)
    
    for i, line in enumerate(lines):
        # Gérer les blocs de code
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            translated_lines.append(line)
            continue
        
        if in_code_block:
            translated_lines.append(line)
            continue
        
        # Traduire la ligne
        if should_translate_line(line):
            translated_line = translate_markdown_line(line, target_lang_code, translator)
            translated_lines.append(translated_line)
            
            # Rate limiting (éviter ban API)
            if i % 10 == 0:
                time.sleep(0.5)
        else:
            translated_lines.append(line)
    
    # Écrire le fichier traduit
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)
        print(f"      ✓ Traduit ({line_count} lignes)")
        return True
    except Exception as e:
        print(f"      ✗ Erreur écriture: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("   TRADUCTION AUTOMATIQUE i18n - Data Platform v3.3.1")
    print("="*60 + "\n")
    
    print("⚙️  Initialisation du traducteur...")
    translator = Translator()
    print("✓  Traducteur prêt\n")
    
    # Obtenir tous les fichiers français
    fr_path = BASE_PATH / SOURCE_LANG
    
    if not fr_path.exists():
        print(f"✗ Erreur: Dossier source introuvable: {fr_path}")
        return
    
    fr_files = list(fr_path.rglob("*.md"))
    
    # Exclure certains fichiers
    excluded_patterns = ['DOCUMENTATION_', 'MISE_A_JOUR_', 'RESUME_FINAL']
    fr_files = [f for f in fr_files if not any(p in f.name for p in excluded_patterns)]
    
    print(f"📚 Fichiers source (FR): {len(fr_files)}")
    print(f"🌍 Langues cibles: {len(LANG_MAPPING)}\n")
    
    total_files = len(fr_files) * len(LANG_MAPPING)
    current = 0
    success_count = 0
    error_count = 0
    
    print("🚀 Démarrage de la traduction...\n")
    print("-" * 60)
    
    # Pour chaque langue cible
    for lang_code, lang_info in LANG_MAPPING.items():
        google_code = lang_info["code"]
        lang_name = lang_info["name"]
        
        print(f"\n[{lang_code.upper()}] 🌐 {lang_name} ({google_code})")
        print("-" * 60)
        
        for source_file in fr_files:
            current += 1
            progress = (current / total_files) * 100
            
            # Déterminer le chemin cible
            rel_path = source_file.relative_to(fr_path)
            target_file = BASE_PATH / lang_code / rel_path
            
            print(f"[{current}/{total_files}] {progress:.1f}%")
            
            if translate_file(source_file, target_file, lang_code, google_code, translator):
                success_count += 1
            else:
                error_count += 1
            
            # Pause pour éviter rate limiting
            time.sleep(0.3)
    
    print("\n" + "="*60)
    print("   TRADUCTION TERMINÉE")
    print("="*60)
    print(f"\n📊 Statistiques:")
    print(f"   ✓ Succès: {success_count}/{total_files}")
    print(f"   ✗ Erreurs: {error_count}/{total_files}")
    print(f"   📁 Langues: {len(LANG_MAPPING)}")
    print(f"   📄 Fichiers: {len(fr_files)} × {len(LANG_MAPPING)} = {total_files}")
    
    print(f"\n✨ Documentation disponible en {len(LANG_MAPPING) + 1} langues!")
    print("\n💡 Prochaines étapes:")
    print("   git add docs/i18n/")
    print('   git commit -m "docs: Add automatic translations for 17 languages"')
    print("   git push\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Traduction interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
