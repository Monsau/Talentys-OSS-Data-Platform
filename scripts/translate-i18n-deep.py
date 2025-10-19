#!/usr/bin/env python3
"""
Script de traduction automatique i18n avec deep-translator
Compatible Python 3.13+
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

def extract_code_blocks(content):
    """Extrait les blocs de code pour ne pas les traduire"""
    code_blocks = []
    pattern = r'```[\s\S]*?```|`[^`]+`'
    
    def replacer(match):
        code_blocks.append(match.group(0))
        return f"§§§CODE_BLOCK_{len(code_blocks)-1}§§§"
    
    cleaned = re.sub(pattern, replacer, content)
    return cleaned, code_blocks

def restore_code_blocks(content, code_blocks):
    """Restaure les blocs de code"""
    for i, block in enumerate(code_blocks):
        content = content.replace(f"§§§CODE_BLOCK_{i}§§§", block)
    return content

def extract_links(content):
    """Extrait les liens markdown pour traduction ciblée"""
    links = []
    # Pattern pour [texte](url)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    
    def replacer(match):
        text, url = match.groups()
        links.append((text, url))
        return f"§§§LINK_{len(links)-1}§§§"
    
    cleaned = re.sub(pattern, replacer, content)
    return cleaned, links

def restore_links(content, links, translated_texts):
    """Restaure les liens avec texte traduit"""
    for i, (original_text, url) in enumerate(links):
        translated_text = translated_texts.get(i, original_text)
        content = content.replace(f"§§§LINK_{i}§§§", f"[{translated_text}]({url})")
    return content

def translate_text(text, target_lang, translator):
    """Traduit un texte avec gestion d'erreur"""
    if not text or not text.strip():
        return text
    
    try:
        # Découper en chunks si trop long (limite Google: 5000 chars)
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
        print(f"      ⚠️ Erreur traduction: {e}")
        return text

def translate_file(source_file, target_file, target_lang, translator):
    """Traduit un fichier markdown"""
    try:
        # Lire le contenu source
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire les blocs de code
        content, code_blocks = extract_code_blocks(content)
        
        # Extraire les liens
        content, links = extract_links(content)
        
        # Traduire le contenu principal
        translated_content = translate_text(content, target_lang, translator)
        
        # Traduire les textes de liens
        translated_link_texts = {}
        for i, (link_text, _) in enumerate(links):
            translated_link_texts[i] = translate_text(link_text, target_lang, translator)
            time.sleep(0.1)  # Rate limiting
        
        # Restaurer les liens avec textes traduits
        translated_content = restore_links(translated_content, links, translated_link_texts)
        
        # Restaurer les blocs de code
        translated_content = restore_code_blocks(translated_content, code_blocks)
        
        # Créer le répertoire cible si nécessaire
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le fichier traduit
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        return True
    
    except Exception as e:
        print(f"      ❌ Erreur: {e}")
        return False

def main():
    print("=" * 60)
    print("TRADUCTION AUTOMATIQUE i18n (deep-translator)")
    print("=" * 60)
    print()
    
    # Vérifier que le dossier source existe
    source_dir = DOCS_I18N_PATH / SOURCE_LANG
    if not source_dir.exists():
        print(f"❌ Dossier source non trouvé: {source_dir}")
        return
    
    # Collecter tous les fichiers .md du dossier source
    source_files = list(source_dir.rglob("*.md"))
    print(f"📁 Fichiers source trouvés: {len(source_files)}")
    print()
    
    # Statistiques
    total_files = len(source_files) * len(LANG_MAPPING)
    processed = 0
    success = 0
    failed = 0
    
    # Traduire pour chaque langue
    for lang_code, google_code in LANG_MAPPING.items():
        print(f"🌐 [{lang_code.upper()}] Traduction vers {google_code}...")
        
        try:
            # Créer le traducteur pour cette langue
            translator = GoogleTranslator(source='fr', target=google_code)
            
            for source_file in source_files:
                # Calculer le chemin relatif
                rel_path = source_file.relative_to(source_dir)
                target_file = DOCS_I18N_PATH / lang_code / rel_path
                
                print(f"  📄 {rel_path}...", end=" ", flush=True)
                
                if translate_file(source_file, target_file, google_code, translator):
                    print("✅")
                    success += 1
                else:
                    print("❌")
                    failed += 1
                
                processed += 1
                
                # Progress
                percent = (processed / total_files) * 100
                print(f"      Progression: {processed}/{total_files} ({percent:.1f}%)")
                
                # Rate limiting
                time.sleep(0.3)
            
            print(f"  ✅ {lang_code.upper()}: {len(source_files)} fichiers traduits")
            print()
            
        except Exception as e:
            print(f"  ❌ Erreur langue {lang_code}: {e}")
            failed += len(source_files)
            processed += len(source_files)
    
    print()
    print("=" * 60)
    print("TRADUCTION TERMINÉE")
    print("=" * 60)
    print(f"Total: {processed} fichiers")
    print(f"✅ Succès: {success}")
    print(f"❌ Échecs: {failed}")
    print()
    print("Prochaines étapes:")
    print("  1. Vérifier les fichiers traduits")
    print("  2. git add docs/i18n/")
    print("  3. git commit -m 'docs: Add automatic translations'")

if __name__ == "__main__":
    main()
