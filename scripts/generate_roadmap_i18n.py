#!/usr/bin/env python3
"""
Generate Roadmap in 18 languages
Copies ROADMAP.md to all i18n language folders
"""

import os
import shutil
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
I18N_DIR = BASE_DIR / "docs" / "i18n"
SOURCE_ROADMAP = I18N_DIR / "ROADMAP.md"

# All 18 languages (same as README structure)
LANGUAGES = [
    "en",  # English
    "fr",  # Français
    "es",  # Español
    "pt",  # Português
    "cn",  # 中文
    "jp",  # 日本語
    "ru",  # Русский
    "ar",  # العربية
    "de",  # Deutsch
    "ko",  # 한국어
    "hi",  # हिन्दी
    "id",  # Indonesia
    "tr",  # Türkçe
    "vi",  # Tiếng Việt
    "it",  # Italiano
    "nl",  # Nederlands
    "pl",  # Polski
    "se",  # Svenska
]

def copy_roadmap_to_all_languages():
    """Copy ROADMAP.md to all language directories"""
    
    if not SOURCE_ROADMAP.exists():
        print(f"❌ Source roadmap not found: {SOURCE_ROADMAP}")
        return False
    
    print(f"📄 Source roadmap: {SOURCE_ROADMAP}")
    print(f"🌍 Deploying to {len(LANGUAGES)} languages...\n")
    
    copied = 0
    skipped = 0
    
    for lang in LANGUAGES:
        lang_dir = I18N_DIR / lang
        target_roadmap = lang_dir / "ROADMAP.md"
        
        # Create language directory if it doesn't exist
        if not lang_dir.exists():
            print(f"⚠️  Creating directory: {lang_dir}")
            lang_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy roadmap file
            shutil.copy2(SOURCE_ROADMAP, target_roadmap)
            print(f"✅ {lang.upper()}: {target_roadmap}")
            copied += 1
        except Exception as e:
            print(f"❌ {lang.upper()}: Error - {e}")
            skipped += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Successfully copied: {copied}")
    if skipped > 0:
        print(f"❌ Skipped: {skipped}")
    print(f"{'='*50}\n")
    
    return copied > 0

def main():
    """Main execution"""
    print("="*50)
    print("🗺️  ROADMAP i18n GENERATOR")
    print("="*50)
    print()
    
    success = copy_roadmap_to_all_languages()
    
    if success:
        print("✅ Roadmap deployed to all 18 languages!")
        print()
        print("📝 Next steps:")
        print("   1. Review generated ROADMAP.md files")
        print("   2. Translate content for each language")
        print("   3. Commit changes to git")
    else:
        print("❌ Deployment failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
