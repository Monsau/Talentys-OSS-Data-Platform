#!/usr/bin/env python3
"""
Génère un diagramme de lineage dbt simple en format texte et Mermaid
"""

import json
import os

def load_manifest():
    """Charge le manifest.json généré par dbt"""
    manifest_path = "dbt/target/manifest.json"
    
    if not os.path.exists(manifest_path):
        print("❌ Fichier manifest.json introuvable.")
        print("   Exécutez d'abord: cd dbt && dbt docs generate")
        return None
    
    with open(manifest_path, 'r') as f:
        return json.load(f)

def extract_lineage(manifest):
    """Extrait le lineage depuis le manifest"""
    nodes = manifest.get('nodes', {})
    sources = manifest.get('sources', {})
    
    lineage = {}
    
    # Parcourir tous les modèles
    for node_id, node in nodes.items():
        if node.get('resource_type') == 'model':
            name = node.get('name')
            depends_on = node.get('depends_on', {}).get('nodes', [])
            
            # Extraire les noms des dépendances
            deps = []
            for dep in depends_on:
                if dep.startswith('source'):
                    source_key = dep.replace('source.', '').replace('.', '_')
                    deps.append(f"source_{source_key}")
                elif dep.startswith('model'):
                    model_name = dep.split('.')[-1]
                    deps.append(model_name)
            
            lineage[name] = deps
    
    return lineage, sources

def print_text_lineage(lineage):
    """Affiche le lineage en format texte"""
    print("\n" + "=" * 70)
    print("📊 LINEAGE DBT - FORMAT TEXTE")
    print("=" * 70 + "\n")
    
    # Trier par niveau de dépendances (sources d'abord)
    def get_depth(model, visited=None):
        if visited is None:
            visited = set()
        if model in visited:
            return 0
        visited.add(model)
        deps = lineage.get(model, [])
        if not deps:
            return 0
        return 1 + max(get_depth(dep, visited.copy()) for dep in deps if dep in lineage)
    
    sorted_models = sorted(lineage.keys(), key=get_depth)
    
    for model in sorted_models:
        deps = lineage[model]
        indent = "  " * get_depth(model)
        
        if deps:
            print(f"{indent}📦 {model}")
            for dep in deps:
                print(f"{indent}  ← {dep}")
        else:
            print(f"{indent}🌱 {model} (source)")
    
    print("\n" + "=" * 70)

def generate_mermaid_diagram(lineage):
    """Génère un diagramme Mermaid"""
    print("\n" + "=" * 70)
    print("📊 LINEAGE DBT - FORMAT MERMAID")
    print("=" * 70 + "\n")
    print("Copiez ce code dans un éditeur Mermaid (ex: https://mermaid.live/)\n")
    print("```mermaid")
    print("graph TD")
    
    # Définir les styles
    print("    classDef sourceClass fill:#90EE90,stroke:#333,stroke-width:2px")
    print("    classDef stagingClass fill:#87CEEB,stroke:#333,stroke-width:2px")
    print("    classDef martClass fill:#DDA0DD,stroke:#333,stroke-width:2px")
    print()
    
    # Générer les nœuds et relations
    node_ids = {}
    counter = 1
    
    for model, deps in lineage.items():
        # Créer un ID propre pour le nœud
        if model not in node_ids:
            node_ids[model] = f"node{counter}"
            counter += 1
        
        model_id = node_ids[model]
        
        # Déterminer le type de nœud
        if model.startswith('stg_'):
            style = "stagingClass"
            shape = f"{model_id}[{model}]"
        elif model.startswith('dim_') or model.startswith('fct_'):
            style = "martClass"
            shape = f"{model_id}[{model}]"
        else:
            style = "sourceClass"
            shape = f"{model_id}({{{model}}})"
        
        print(f"    {shape}:::{style}")
        
        # Ajouter les relations
        for dep in deps:
            if dep not in node_ids:
                node_ids[dep] = f"node{counter}"
                counter += 1
            
            dep_id = node_ids[dep]
            print(f"    {dep_id} --> {model_id}")
    
    print("```")
    print("\n" + "=" * 70)

def generate_summary(lineage):
    """Génère un résumé statistique"""
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DU LINEAGE")
    print("=" * 70 + "\n")
    
    total = len(lineage)
    staging = len([m for m in lineage if m.startswith('stg_')])
    marts = len([m for m in lineage if m.startswith('dim_') or m.startswith('fct_')])
    sources = len([m for m, deps in lineage.items() if not deps])
    
    print(f"📦 Total de modèles: {total}")
    print(f"🌱 Sources: {sources}")
    print(f"🔵 Staging (views): {staging}")
    print(f"🟣 Marts (tables): {marts}")
    print()
    
    # Modèles les plus dépendants
    deps_count = {m: len(deps) for m, deps in lineage.items()}
    top_deps = sorted(deps_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print("🔗 Modèles avec le plus de dépendances:")
    for model, count in top_deps:
        if count > 0:
            print(f"   • {model}: {count} dépendance(s)")
    
    print("\n" + "=" * 70)

def main():
    print("=" * 70)
    print("🔍 ANALYSE DU LINEAGE DBT")
    print("=" * 70)
    
    # Charger le manifest
    manifest = load_manifest()
    if not manifest:
        return
    
    print("✅ Manifest chargé avec succès\n")
    
    # Extraire le lineage
    lineage, sources = extract_lineage(manifest)
    
    # Afficher le résumé
    generate_summary(lineage)
    
    # Afficher le lineage texte
    print_text_lineage(lineage)
    
    # Générer le diagramme Mermaid
    generate_mermaid_diagram(lineage)
    
    print("\n💡 Pour visualiser de façon interactive:")
    print("   1. Lancez: dbt docs serve --port 8083")
    print("   2. Ouvrez: http://localhost:8083")
    print("   3. Cliquez sur 'Lineage Graph'\n")

if __name__ == "__main__":
    main()
