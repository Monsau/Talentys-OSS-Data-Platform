import requests

# Auth
r = requests.post('http://localhost:9047/apiv2/login', json={'userName':'admin','password':'admin123'})
headers = {'Authorization': '_dremio' + r.json()['token']}

# Lister sources
r = requests.get('http://localhost:9047/api/v3/catalog', headers=headers)
print("Sources existantes:")
for s in r.json().get('data', []):
    name = s.get('path', [None])[0] if s.get('path') else 'Unknown'
    print(f"  - {name} (type: {s.get('containerType', s.get('type'))})")
