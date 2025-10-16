from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'], verify_certs=False)

print("Indices Elasticsearch:")
print("-" * 40)

try:
    # Lister les indices
    indices = es.cat.indices(format='json')
    
    for idx in indices:
        print(f"{idx['index']:25s} {idx['docs.count']:>10s} docs")
    
    if not indices:
        print("Aucun index trouve")
        
except Exception as e:
    print(f"Erreur: {e}")
