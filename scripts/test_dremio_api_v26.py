#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'API Dremio 26 pour créer des sources
"""
import requests
import json

DREMIO_URL = "http://localhost:9047"
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    """Login et obtenir le token"""
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json={"userName": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["token"]
        print(f"[OK] Login réussi, token: {token[:20]}...")
        return token
    else:
        print(f"[X] Erreur login: {response.status_code}")
        return None

def test_create_source_v3(token):
    """Tester création source avec /api/v3/catalog"""
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    
    # Essai 1: POST avec entityType=source
    source_config = {
        "entityType": "source",
        "name": "Test_PostgreSQL",
        "type": "POSTGRES",
        "config": {
            "hostname": "dremio-postgres",
            "port": 5432,
            "databaseName": "business_db",
            "username": "postgres",
            "password": "postgres123",
            "authenticationType": "MASTER"
        }
    }
    
    print("\n=== Test 1: POST /api/v3/catalog ===")
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        headers=headers,
        json=source_config
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    # Essai 2: POST avec path
    if response.status_code != 200:
        print("\n=== Test 2: POST /api/v3/catalog avec path ===")
        source_config["path"] = ["Test_PostgreSQL"]
        response = requests.post(
            f"{DREMIO_URL}/api/v3/catalog",
            headers=headers,
            json=source_config
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    
    # Essai 3: PUT /api/v3/catalog/Test_PostgreSQL
    if response.status_code != 200:
        print("\n=== Test 3: PUT /api/v3/catalog/Test_PostgreSQL ===")
        response = requests.put(
            f"{DREMIO_URL}/api/v3/catalog/Test_PostgreSQL",
            headers=headers,
            json=source_config
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    
    # Essai 4: POST /apiv2/source (ancienne API)
    if response.status_code != 200:
        print("\n=== Test 4: POST /apiv2/source ===")
        response = requests.post(
            f"{DREMIO_URL}/apiv2/source",
            headers=headers,
            json=source_config
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")

def main():
    print("=== TEST API DREMIO 26 ===\n")
    token = login()
    if token:
        test_create_source_v3(token)

if __name__ == "__main__":
    main()
