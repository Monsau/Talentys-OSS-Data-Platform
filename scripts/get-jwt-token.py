#!/usr/bin/env python3
"""
Script pour récupérer un nouveau token JWT d'OpenMetadata
"""

import requests
import json

# Récupérer le token du bot ingestion
response = requests.get("http://localhost:8585/api/v1/users/name/ingestion-bot?fields=*")

if response.status_code == 200:
    data = response.json()
    token = data.get("authenticationMechanism", {}).get("config", {}).get("JWTToken")
    if token:
        print("=" * 70)
        print("🔑 JWT Token récupéré:")
        print("=" * 70)
        print(token)
        print("=" * 70)
        print("\n✅ Copiez ce token et mettez-le à jour dans le script")
    else:
        print("❌ Token non trouvé dans la réponse")
else:
    print(f"❌ Erreur {response.status_code}: {response.text}")
