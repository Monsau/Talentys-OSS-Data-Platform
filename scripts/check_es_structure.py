#!/usr/bin/env python3
"""Check Elasticsearch document structure"""

import elasticsearch

es = elasticsearch.Elasticsearch(["http://localhost:9200"])

# Get sample from each index
indices = ["application_logs", "user_events", "performance_metrics"]

for index in indices:
    result = es.search(index=index, size=1)
    if result["hits"]["hits"]:
        doc = result["hits"]["hits"][0]["_source"]
        print(f"\n=== {index} ===")
        print(f"Fields: {list(doc.keys())}")
        print(f"Sample: {doc}")
