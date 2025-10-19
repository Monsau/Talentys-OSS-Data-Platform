#!/usr/bin/env python3
"""
Script de traduction i18n intelligent - saute les fichiers déjà traduits
"""

import os
import re
import time
from pathlib import Path
from deep_translator import GoogleTranslator

# Configuration
DOCS_I18N_PATH = Path("docs/i18n")
SOURCE_LANG = "fr"

# Mapping code langue -> code Google Translate
LANG_MAPPING = {
    "en": "en",    # English
    "ar": "ar",    # Arabic
    "cn": "zh-CN", # Chinese Simplified
    "de": "de",    # German
    "es": "es",    # Spanish
    "hi": "hi",    # Hindi
    "id": "id",    # Indonesian
    "it": "it",    # Italian
    "jp": "ja",    # Japanese
    "ko": "ko",    # Korean
    "nl": "nl",    # Dutch
    "pl": "pl",    # Polish
    "pt": "pt",    # Portuguese
    "ru": "ru",    # Russian
    "se": "sv",    # Swedish
    "tr": "tr",    # Turkish
    "vi": "vi",    # Vietnamese
}

def is_already_translated(file_path):
    """Vérifie si un fichier a déjà été traduit (pas juste un warning)"""
    if not file_path.exists():
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = f.read(500)
            # Si contient le warning de traduction, pas encore traduit
            if "Translation Required" in first_lines or "Documentation In Progress" in first_lines:
                return False
            # Si commence directement par du contenu sans warning
            return True
    except:
        return False

def extract_code_blocks(content):
    """Extrait les blocs de code"""
    code_blocks = []
    pattern = r'```[\s\S]*?```|`[^`]+`'
    
    def replacer(match):
        code_blocks.append(match.group(0))
        return f"§§§CODE_{len(code_blocks)-1}§§§"
    
    cleaned = re.sub(pattern, replacer, content)
    return cleaned, code_blocks

def restore_code_blocks(content, code_blocks):
    """Restaure les blocs de code"""
    for i, block in enumerate(code_blocks):
        content = content.replace(f"§§§CODE_{i}§§§", block)
    return content

def translate_text(text, translator):
    """Traduit un texte"""
    if not text or not text.strip():
        return text
    
    try:
        max_length = 4500
        if len(text) <= max_length:
            return translator.translate(text)
        
        # Découper par paragraphes
        paragraphs = text.split('\n\n')
        translated_parts = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    translated_parts.append(translator.translate(current_chunk.strip()))
                current_chunk = para + "\n\n"
        
        if current_chunk:
            translated_parts.append(translator.translate(current_chunk.strip()))
        
        return "\n\n".join(translated_parts)
    
    except Exception as e:
        print(f" ⚠️ {str(e)[:50]}")
        return text

def translate_file(source_file, target_file, translator):
    """Traduit un fichier"""
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire et protéger les blocs de code
        content, code_blocks = extract_code_blocks(content)
        
        # Traduire
        translated_content = translate_text(content, translator)
        
        # Restaurer les blocs de code
        translated_content = restore_code_blocks(translated_content, code_blocks)
        
        # Écrire
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        return True
    
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")
        return False

def main():
    print("\n" + "="*70)
    print("  TRADUCTION AUTOMATIQUE INTELLIGENTE")
    print("  Saute les fichiers déjà traduits")
    print("="*70 + "\n")
    
    source_dir = DOCS_I18N_PATH / SOURCE_LANG
    if not source_dir.exists():
        print(f"❌ Dossier source introuvable: {source_dir}")
        return
    
    source_files = sorted(source_dir.rglob("*.md"))
    print(f"📁 Fichiers source: {len(source_files)}\n")
    
    # Statistiques globales
    total_to_check = len(source_files) * len(LANG_MAPPING)
    total_processed = 0
    total_skipped = 0
    total_translated = 0
    total_failed = 0
    
    start_time = time.time()
    
    for lang_code, google_code in LANG_MAPPING.items():
        print(f"\n🌐 {lang_code.upper():>3} | {google_code:>5} ".ljust(70, "─"))
        
        try:
            translator = GoogleTranslator(source='fr', target=google_code)
            lang_translated = 0
            lang_skipped = 0
            lang_failed = 0
            
            for idx, source_file in enumerate(source_files, 1):
                rel_path = source_file.relative_to(source_dir)
                target_file = DOCS_I18N_PATH / lang_code / rel_path
                
                total_processed += 1
                percent = (total_processed / total_to_check) * 100
                
                # Vérifier si déjà traduit
                if is_already_translated(target_file):
                    print(f"  {idx:2}/{len(source_files)} ⏭️  {str(rel_path)[:45]:45} [SKIP] {percent:5.1f}%")
                    lang_skipped += 1
                    total_skipped += 1
                    continue
                
                print(f"  {idx:2}/{len(source_files)} 🔄 {str(rel_path)[:45]:45} ", end="", flush=True)
                
                if translate_file(source_file, target_file, translator):
                    print(f"✅ {percent:5.1f}%")
                    lang_translated += 1
                    total_translated += 1
                else:
                    print(f"❌ {percent:5.1f}%")
                    lang_failed += 1
                    total_failed += 1
                
                time.sleep(0.3)  # Rate limiting
            
            print(f"  └─ ✅ {lang_translated} | ⏭️ {lang_skipped} | ❌ {lang_failed}")
            
        except Exception as e:
            print(f"  ❌ Erreur langue: {e}")
            total_failed += len(source_files)
            total_processed += len(source_files)
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    print("\n" + "="*70)
    print("  RÉSUMÉ")
    print("="*70)
    print(f"  Total vérifié     : {total_processed}")
    print(f"  ✅ Traduits       : {total_translated}")
    print(f"  ⏭️  Déjà traduits  : {total_skipped}")
    print(f"  ❌ Échecs         : {total_failed}")
    print(f"  ⏱️  Temps          : {minutes}m {seconds}s")
    print("="*70 + "\n")
    
    if total_translated > 0:
        print("✅ Traduction terminée avec succès!")
        print("\nProchaines étapes:")
        print("  git add docs/i18n/")
        print("  git status")
        print("  git commit -m 'docs: Add real translations to all languages'")

if __name__ == "__main__":
    main()
