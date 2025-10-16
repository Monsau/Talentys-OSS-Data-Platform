#!/usr/bin/env python3
"""
Connecteur automatique Dremio -> OpenMetadata
Découvre et synchronise automatiquement toutes les ressources Dremio
"""
import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration Dremio
DREMIO_URL = "http://localhost:9047"
DREMIO_USER = "admin"
DREMIO_PASS = "admin123"

# Configuration OpenMetadata
OPENMETADATA_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"
SERVICE_NAME = "dremio_dbt_service"

class DremioConnector:
    """Connecteur pour interagir avec l'API Dremio"""
    
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.token = None
        self.headers = {}
    
    def authenticate(self) -> bool:
        """Authentification auprès de Dremio"""
        try:
            response = requests.post(
                f"{self.url}/apiv2/login",
                json={"userName": self.username, "password": self.password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json()["token"]
                self.headers = {"Authorization": f"_dremio{self.token}"}
                logger.info("Authentification Dremio réussie")
                return True
            else:
                logger.error(f"Échec authentification Dremio: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification Dremio: {e}")
            return False
    
    def get_catalog_item(self, path: str = None) -> Optional[Dict]:
        """Récupérer un élément du catalogue"""
        try:
            if path:
                url = f"{self.url}/api/v3/catalog/by-path/{path}"
            else:
                url = f"{self.url}/api/v3/catalog"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Erreur récupération catalogue {path}: {e}")
            return None
    
    def get_dataset_schema(self, dataset_id: str) -> Optional[Dict]:
        """Récupérer le schéma d'un dataset"""
        try:
            url = f"{self.url}/api/v3/catalog/{dataset_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Erreur récupération schéma {dataset_id}: {e}")
            return None
    
    def discover_all_resources(self) -> List[Dict]:
        """Découvrir toutes les ressources Dremio récursivement"""
        logger.info("Découverte des ressources Dremio...")
        resources = []
        visited = set()  # Pour éviter les boucles infinies
        
        # Récupérer le catalogue racine
        catalog = self.get_catalog_item()
        if not catalog:
            logger.error("Impossible de récupérer le catalogue racine")
            return resources
        
        # Explorer récursivement
        items = catalog.get("data", [])
        for item in items:
            self._explore_item_deep(item, resources, visited)
        
        logger.info(f"Découverte terminée: {len(resources)} ressources trouvées")
        return resources
    
    def _explore_item_deep(self, item: Dict, resources: List[Dict], visited: set):
        """Explorer récursivement un élément avec requêtes API pour chaque conteneur"""
        path = item.get("path", [])
        path_str = ".".join(path) if path else ""
        
        # Éviter les cycles
        if path_str in visited:
            return
        visited.add(path_str)
        
        # L'API utilise 'type' et 'containerType' dans certaines réponses,
        # et 'entityType' dans d'autres
        item_type = item.get("type", item.get("entityType", "UNKNOWN"))
        container_type = item.get("containerType", "")
        item_id = item.get("id", "")
        
        # Normaliser le type
        if item_type == "CONTAINER":
            if container_type == "SPACE":
                entity_type = "space"
            elif container_type == "HOME":
                entity_type = "home"
            elif container_type == "SOURCE":
                entity_type = "source"
            elif container_type == "FOLDER":
                entity_type = "folder"
            else:
                entity_type = "folder"
        elif item_type == "DATASET":
            entity_type = "dataset"
        else:
            entity_type = item_type.lower() if item_type else "unknown"
        
        resource = {
            "id": item_id,
            "path": path,
            "full_path": path_str,
            "type": entity_type
        }
        
        # Pour les datasets, récupérer le schéma détaillé
        if entity_type == "dataset" and item_id:
            logger.debug(f"  Récupération schéma pour dataset: {path_str}")
            schema = self.get_dataset_schema(item_id)
            if schema:
                resource["schema"] = schema
                resource["columns"] = self._extract_columns(schema)
        
        resources.append(resource)
        logger.info(f"Découvert: [{entity_type}] {path_str}")
        
        # Si c'est un conteneur, explorer ses enfants via une requête API dédiée
        if entity_type in ["space", "source", "folder", "home"] and path:
            container_path = "/".join(path)
            logger.info(f"  Exploration du conteneur: {container_path}")
            
            container_data = self.get_catalog_item(container_path)
            if container_data:
                # Récupérer les children directs
                children = container_data.get("children", [])
                logger.info(f"    Trouvé {len(children)} enfants")
                
                for child in children:
                    self._explore_item_deep(child, resources, visited)
    
    
    def _extract_columns(self, schema: Dict) -> List[Dict]:
        """Extraire les colonnes d'un schéma Dremio"""
        columns = []
        fields = schema.get("fields", [])
        
        for field in fields:
            column = {
                "name": field.get("name", ""),
                "dataType": self._map_dremio_type(field.get("type", {})),
                "dataLength": 1,
                "ordinalPosition": len(columns) + 1
            }
            columns.append(column)
        
        return columns
    
    def _map_dremio_type(self, dremio_type: Dict) -> str:
        """Mapper les types Dremio vers les types OpenMetadata"""
        type_name = dremio_type.get("name", "VARCHAR")
        
        type_mapping = {
            "INTEGER": "INT",
            "BIGINT": "BIGINT",
            "FLOAT": "FLOAT",
            "DOUBLE": "DOUBLE",
            "VARCHAR": "VARCHAR",
            "BOOLEAN": "BOOLEAN",
            "DATE": "DATE",
            "TIME": "TIME",
            "TIMESTAMP": "TIMESTAMP",
            "DECIMAL": "DECIMAL"
        }
        
        return type_mapping.get(type_name.upper(), "VARCHAR")


class OpenMetadataConnector:
    """Connecteur pour interagir avec l'API OpenMetadata"""
    
    def __init__(self, url: str, jwt_token: str, service_name: str):
        self.url = url
        self.service_name = service_name
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        self.stats = {
            "databases_created": 0,
            "schemas_created": 0,
            "tables_created": 0,
            "errors": 0
        }
    
    def create_or_update_database(self, name: str, description: str = "") -> Optional[str]:
        """Créer ou mettre à jour une database"""
        payload = {
            "name": name,
            "displayName": name,
            "description": description,
            "service": self.service_name
        }
        
        try:
            response = requests.put(
                f"{self.url}/v1/databases",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                fqn = response.json().get("fullyQualifiedName")
                logger.info(f"Database créée/mise à jour: {fqn}")
                self.stats["databases_created"] += 1
                return fqn
            else:
                logger.warning(f"Échec création database {name}: {response.status_code}")
                self.stats["errors"] += 1
                return None
        except Exception as e:
            logger.error(f"Erreur création database {name}: {e}")
            self.stats["errors"] += 1
            return None
    
    def create_or_update_schema(self, database_fqn: str, name: str, description: str = "") -> Optional[str]:
        """Créer ou mettre à jour un schéma"""
        payload = {
            "name": name,
            "displayName": name,
            "description": description,
            "database": database_fqn
        }
        
        try:
            response = requests.put(
                f"{self.url}/v1/databaseSchemas",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                fqn = response.json().get("fullyQualifiedName")
                logger.info(f"  Schema créé/mis à jour: {fqn}")
                self.stats["schemas_created"] += 1
                return fqn
            else:
                logger.warning(f"  Échec création schema {name}: {response.status_code}")
                self.stats["errors"] += 1
                return None
        except Exception as e:
            logger.error(f"Erreur création schema {name}: {e}")
            self.stats["errors"] += 1
            return None
    
    def create_or_update_table(self, schema_fqn: str, name: str, columns: List[Dict], description: str = "") -> Optional[str]:
        """Créer ou mettre à jour une table"""
        payload = {
            "name": name,
            "displayName": name,
            "description": description,
            "tableType": "Regular",
            "columns": columns,
            "databaseSchema": schema_fqn
        }
        
        try:
            response = requests.put(
                f"{self.url}/v1/tables",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                fqn = response.json().get("fullyQualifiedName")
                logger.info(f"    Table créée/mise à jour: {fqn} ({len(columns)} colonnes)")
                self.stats["tables_created"] += 1
                return fqn
            else:
                logger.warning(f"    Échec création table {name}: {response.status_code}")
                self.stats["errors"] += 1
                return None
        except Exception as e:
            logger.error(f"Erreur création table {name}: {e}")
            self.stats["errors"] += 1
            return None
    
    def get_stats(self) -> Dict:
        """Retourner les statistiques de synchronisation"""
        return self.stats


class DremioOpenMetadataSync:
    """Orchestrateur de synchronisation Dremio -> OpenMetadata"""
    
    def __init__(self, dremio: DremioConnector, openmetadata: OpenMetadataConnector):
        self.dremio = dremio
        self.openmetadata = openmetadata
    
    def sync(self, incremental: bool = False):
        """Synchroniser toutes les ressources Dremio vers OpenMetadata"""
        logger.info("=" * 80)
        logger.info("Démarrage de la synchronisation Dremio -> OpenMetadata")
        logger.info("=" * 80)
        
        # Authentification Dremio
        if not self.dremio.authenticate():
            logger.error("Impossible de s'authentifier auprès de Dremio")
            return
        
        # Découvrir les ressources
        resources = self.dremio.discover_all_resources()
        
        if not resources:
            logger.warning("Aucune ressource découverte")
            return
        
        # Organiser les ressources par hiérarchie
        hierarchy = self._organize_hierarchy(resources)
        
        # Synchroniser vers OpenMetadata
        self._sync_to_openmetadata(hierarchy)
        
        # Afficher les statistiques
        self._display_stats()
    
    def _organize_hierarchy(self, resources: List[Dict]) -> Dict:
        """Organiser les ressources en hiérarchie database -> schema -> table"""
        hierarchy = {}
        
        for resource in resources:
            path = resource.get("path", [])
            if not path:
                continue
            
            resource_type = resource.get("type", "")
            
            # Déterminer le niveau hiérarchique selon le type et la longueur du path
            if resource_type in ["space", "source"] or len(path) == 1:
                # Niveau database
                db_name = path[0]
                if db_name not in hierarchy:
                    hierarchy[db_name] = {
                        "type": "database",
                        "resource": resource,
                        "schemas": {}
                    }
            
            elif len(path) == 2:
                # Niveau schema
                db_name, schema_name = path[0], path[1]
                if db_name not in hierarchy:
                    hierarchy[db_name] = {"type": "database", "schemas": {}}
                
                if schema_name not in hierarchy[db_name]["schemas"]:
                    hierarchy[db_name]["schemas"][schema_name] = {
                        "type": "schema",
                        "resource": resource,
                        "tables": []
                    }
            
            elif len(path) >= 3 and resource_type == "dataset":
                # Niveau table
                db_name, schema_name = path[0], path[1]
                table_name = path[-1]
                
                if db_name not in hierarchy:
                    hierarchy[db_name] = {"type": "database", "schemas": {}}
                if schema_name not in hierarchy[db_name]["schemas"]:
                    hierarchy[db_name]["schemas"][schema_name] = {"type": "schema", "tables": []}
                
                hierarchy[db_name]["schemas"][schema_name]["tables"].append(resource)
        
        return hierarchy
    
    def _sync_to_openmetadata(self, hierarchy: Dict):
        """Synchroniser la hiérarchie vers OpenMetadata"""
        logger.info(f"\nSynchronisation de {len(hierarchy)} databases...")
        
        for db_name, db_data in hierarchy.items():
            # Créer la database
            db_fqn = self.openmetadata.create_or_update_database(
                db_name,
                f"Database Dremio: {db_name}"
            )
            
            if not db_fqn:
                continue
            
            # Créer les schémas
            schemas = db_data.get("schemas", {})
            for schema_name, schema_data in schemas.items():
                schema_fqn = self.openmetadata.create_or_update_schema(
                    db_fqn,
                    schema_name,
                    f"Schema Dremio: {db_name}.{schema_name}"
                )
                
                if not schema_fqn:
                    continue
                
                # Créer les tables
                tables = schema_data.get("tables", [])
                for table_resource in tables:
                    table_name = table_resource.get("path", [])[-1]
                    columns = table_resource.get("columns", [])
                    
                    # Si pas de colonnes, créer une colonne par défaut
                    if not columns:
                        columns = [{
                            "name": "column_1",
                            "dataType": "VARCHAR",
                            "dataLength": 1,
                            "ordinalPosition": 1
                        }]
                    
                    self.openmetadata.create_or_update_table(
                        schema_fqn,
                        table_name,
                        columns,
                        f"Table Dremio: {'.'.join(table_resource.get('path', []))}"
                    )
    
    def _display_stats(self):
        """Afficher les statistiques de synchronisation"""
        stats = self.openmetadata.get_stats()
        
        logger.info("\n" + "=" * 80)
        logger.info("STATISTIQUES DE SYNCHRONISATION")
        logger.info("=" * 80)
        logger.info(f"Databases créées/mises à jour: {stats['databases_created']}")
        logger.info(f"Schemas créés/mis à jour: {stats['schemas_created']}")
        logger.info(f"Tables créées/mises à jour: {stats['tables_created']}")
        logger.info(f"Erreurs: {stats['errors']}")
        logger.info("=" * 80)


def main():
    """Point d'entrée principal"""
    # Initialiser les connecteurs
    dremio = DremioConnector(DREMIO_URL, DREMIO_USER, DREMIO_PASS)
    openmetadata = OpenMetadataConnector(OPENMETADATA_URL, JWT_TOKEN, SERVICE_NAME)
    
    # Créer le synchroniseur
    sync = DremioOpenMetadataSync(dremio, openmetadata)
    
    # Lancer la synchronisation
    sync.sync()


if __name__ == "__main__":
    main()
