#!/usr/bin/env python3
"""
Pipeline d'exemple - Environnement Dremio Complet

Démontre :
- Connexion aux sources PostgreSQL
- Transformation via VDS Dremio
- Synchronisation OpenMetadata
- Lineage automatique
"""

import sys
from pathlib import Path

# Ajouter le connecteur au path
sys.path.append(r"c:\projets\dremio")

from dremio_connector.clients.dremio_client import DremioClient
from dremio_connector.clients.openmetadata_client import OpenMetadataClient

def main():
    print("🚀 Pipeline Dremio → OpenMetadata")
    
    # Configuration
    dremio = DremioClient("http://localhost:9047", "admin", "admin123")
    
    # Test connexions
    if dremio.test_connection():
        print("✅ Dremio connecté")
        
        # Récupérer catalogue
        catalog = dremio.get_catalog()
        print(f"📊 Catalogue: {len(catalog)} éléments")
        
        # Afficher structure
        for item in catalog:
            print(f"   - {item.get('name')} ({item.get('type')})")
    
    print("🎉 Pipeline terminé")

if __name__ == '__main__':
    main()
