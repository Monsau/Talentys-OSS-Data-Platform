#!/usr/bin/env python3
"""
Script pour configurer automatiquement Dremio via l'API REST
"""
import requests
import json
import time
import sys

DREMIO_URL = "http://localhost:9047"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
NEW_USER_USERNAME = "dremio_user"
NEW_USER_PASSWORD = "dremio_pass123"  # Au moins 8 caractères avec 1 chiffre

def wait_for_dremio():
    """Attendre que Dremio soit prêt"""
    print("⏳ Attente que Dremio soit prêt...")
    for i in range(30):
        try:
            response = requests.get(f"{DREMIO_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Dremio est prêt")
                return True
        except:
            pass
        time.sleep(2)
        print(f"   Tentative {i+1}/30...")
    print("❌ Dremio ne répond pas")
    return False

def check_first_time_setup():
    """Vérifier si c'est la première configuration"""
    try:
        response = requests.get(f"{DREMIO_URL}/apiv2/bootstrap/firstuser", timeout=5)
        # Si 200, première configuration nécessaire
        # Si 401/403, déjà configuré
        return response.status_code == 200
    except:
        return False

def create_first_user():
    """Créer le premier utilisateur admin"""
    print("🔧 Création du premier utilisateur admin...")
    
    payload = {
        "userName": ADMIN_USERNAME,
        "firstName": "Admin",
        "lastName": "User",
        "email": "admin@example.com",
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.put(
            f"{DREMIO_URL}/apiv2/bootstrap/firstuser",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Utilisateur admin créé: {ADMIN_USERNAME}")
            return True
        else:
            print(f"⚠️ Réponse: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        return False

def login(username, password):
    """Se connecter à Dremio et obtenir un token"""
    print(f"🔐 Connexion en tant que {username}...")
    
    payload = {
        "userName": username,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{DREMIO_URL}/apiv2/login",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"✅ Connexion réussie")
            return token
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def create_user(token, username, password):
    """Créer un nouvel utilisateur"""
    print(f"👤 Création de l'utilisateur {username}...")
    
    # Dremio 26.0 API v3 - payload simplifié
    payload = {
        "name": username,
        "firstName": "dbt",
        "lastName": "User",
        "email": f"{username}@example.com",
        "password": password
    }
    
    try:
        # Essayer avec l'API v3
        response = requests.post(
            f"{DREMIO_URL}/api/v3/user",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"_dremio{token}"
            }
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Utilisateur {username} créé avec succès")
            return True
        elif response.status_code == 409:
            print(f"ℹ️ L'utilisateur {username} existe déjà")
            return True
        else:
            print(f"⚠️ Réponse API v3: {response.status_code}")
            print(f"   Message: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        return False

def create_space(token, space_name):
    """Créer un espace (space) dans Dremio"""
    print(f"📁 Création de l'espace {space_name}...")
    
    # Dremio 26.0 API v3
    payload = {
        "entityType": "space",
        "name": space_name,
        "path": [space_name]
    }
    
    try:
        # API v3 pour créer un space
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"_dremio{token}"
            }
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Espace {space_name} créé")
            return True
        elif response.status_code == 409:
            print(f"ℹ️ L'espace {space_name} existe déjà")
            return True
        else:
            print(f"⚠️ Échec création espace: {response.status_code}")
            print(f"   Message: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Configuration automatique de Dremio")
    print("=" * 60)
    
    # 1. Attendre que Dremio soit prêt
    if not wait_for_dremio():
        sys.exit(1)
    
    # 2. Vérifier si première configuration
    first_time = check_first_time_setup()
    
    if first_time:
        print("\n📝 Première configuration détectée")
        if not create_first_user():
            print("❌ Échec de la création de l'admin")
            sys.exit(1)
        time.sleep(2)
    else:
        print("\nℹ️ Dremio déjà configuré")
    
    # 3. Se connecter
    token = login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if not token:
        print("\n⚠️ Impossible de se connecter avec admin/admin123")
        print("   Tentative avec credentials existants...")
        # Essayer d'autres credentials communs
        token = login("$dremio", "dremio123")
        if not token:
            print("❌ Échec de connexion")
            print("\n📝 Configuration manuelle requise:")
            print(f"   1. Aller sur {DREMIO_URL}")
            print("   2. Se connecter ou créer un compte admin")
            print(f"   3. Créer l'utilisateur '{NEW_USER_USERNAME}' avec mot de passe '{NEW_USER_PASSWORD}'")
            sys.exit(1)
    
    # 4. Créer l'utilisateur dbt
    if not create_user(token, NEW_USER_USERNAME, NEW_USER_PASSWORD):
        print("⚠️ Échec de création de l'utilisateur")
    
    # 5. Créer les espaces nécessaires
    for space in ["raw", "staging", "marts"]:
        create_space(token, space)
    
    print("\n" + "=" * 60)
    print("✅ Configuration terminée !")
    print("=" * 60)
    print(f"\n📋 Informations de connexion:")
    print(f"   URL: {DREMIO_URL}")
    print(f"   Utilisateur dbt: {NEW_USER_USERNAME}")
    print(f"   Mot de passe: {NEW_USER_PASSWORD}")
    print(f"\n📁 Espaces créés: raw, staging, marts")
    print(f"\n🔗 Accéder à l'interface: {DREMIO_URL}")

if __name__ == "__main__":
    main()
