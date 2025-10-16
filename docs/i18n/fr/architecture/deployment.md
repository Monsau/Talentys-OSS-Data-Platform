# Architecture de Déploiement

**Version**: 3.2.0  
**Dernière Mise à Jour**: 16 octobre 2025  
**Langue**: Français

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Topologies de Déploiement](#topologies-de-déploiement)
3. [Déploiement Docker Compose](#déploiement-docker-compose)
4. [Déploiement Kubernetes](#déploiement-kubernetes)
5. [Déploiements Cloud](#déploiements-cloud)
6. [Configuration Haute Disponibilité](#configuration-haute-disponibilité)
7. [Stratégies de Mise à l'Échelle](#stratégies-de-mise-à-léchelle)
8. [Configuration Sécurité](#configuration-sécurité)
9. [Surveillance et Journalisation](#surveillance-et-journalisation)
10. [Reprise après Sinistre](#reprise-après-sinistre)
11. [Bonnes Pratiques](#bonnes-pratiques)

---

## Vue d'ensemble

Ce document fournit des conseils complets sur le déploiement de la plateforme de données à travers différents environnements, du développement à la production. Nous couvrons diverses topologies de déploiement, stratégies d'orchestration et bonnes pratiques opérationnelles.

### Objectifs de Déploiement

- **Fiabilité**: 99,9% de disponibilité pour les charges de travail de production
- **Scalabilité**: Gérer une croissance 10x sans changements d'architecture
- **Sécurité**: Défense en profondeur avec plusieurs couches de sécurité
- **Maintenabilité**: Mises à jour et gestion de configuration faciles
- **Rentabilité**: Optimiser l'utilisation des ressources

### Types d'Environnement

| Environnement | Objectif | Échelle | Disponibilité |
|---------------|----------|---------|---------------|
| **Développement** | Développement fonctionnalités, tests | Nœud unique | <95% |
| **Staging** | Validation pré-production | Multi-nœud | 95-99% |
| **Production** | Charges de travail données live | Clusterisé | >99,9% |
| **DR** | Site reprise après sinistre | Miroir prod | Standby |

---

## Topologies de Déploiement

### Topologie 1: Développement Mono-Hôte

```mermaid
graph TB
    subgraph "Hôte Docker Unique"
        subgraph "Réseau: data-platform"
            A[Airbyte<br/>:8000,:8001]
            B[Dremio<br/>:9047,:31010,:32010]
            C[dbt<br/>CLI Seulement]
            D[Superset<br/>:8088]
            E[PostgreSQL<br/>:5432]
            F[MinIO<br/>:9000,:9001]
            G[Elasticsearch<br/>:9200]
        end
        
        H[Volume Partagé<br/>./docker-volume]
    end
    
    A & B & D & E & F & G -.-> H
    
    style A fill:#615EFF,color:#fff
    style B fill:#FDB515
    style C fill:#FF694B,color:#fff
    style D fill:#20A7C9,color:#fff
    style E fill:#336791,color:#fff
    style F fill:#C72E49,color:#fff
    style G fill:#005571,color:#fff
```

**Cas d'Usage**: Développement local, tests, démonstrations

**Spécifications**:
- CPU: 4-8 cœurs
- RAM: 16-32 Go
- Disque: 100-500 Go SSD
- Réseau: Localhost uniquement

**Avantages**:
- Configuration simple (docker-compose up)
- Faible coût
- Itération rapide

**Inconvénients**:
- Pas de redondance
- Performance limitée
- Non adapté pour la production

### Topologie 2: Docker Swarm Multi-Hôte

```mermaid
graph TB
    LB[Équilibreur de Charge<br/>nginx/HAProxy]
    
    subgraph "Manager Swarm"
        M1[Manager 1]
        M2[Manager 2]
        M3[Manager 3]
    end
    
    subgraph "Nœud Worker 1"
        W1A[Airbyte]
        W1D[Coordinateur Dremio]
    end
    
    subgraph "Nœud Worker 2"
        W2D[Exécuteur Dremio]
        W2S[Superset]
    end
    
    subgraph "Nœud Worker 3"
        W3D[Exécuteur Dremio]
        W3E[Elasticsearch]
    end
    
    subgraph "Nœud Base de Données"
        DB1[PostgreSQL Primaire]
        DB2[PostgreSQL Secondaire]
    end
    
    subgraph "Nœud Stockage"
        ST1[Nœud MinIO 1]
        ST2[Nœud MinIO 2]
        ST3[Nœud MinIO 3]
        ST4[Nœud MinIO 4]
    end
    
    LB --> W1A & W1D & W2S
    
    M1 & M2 & M3 -.-> W1A & W1D & W2D & W2S & W3D & W3E
    
    W1A & W1D & W2D & W2S & W3D & W3E --> DB1
    DB1 -.->|Réplication| DB2
    
    W1D & W2D & W3D --> ST1 & ST2 & ST3 & ST4
    
    style LB fill:#4CAF50,color:#fff
    style M1 fill:#9C27B0,color:#fff
    style M2 fill:#9C27B0,color:#fff
    style M3 fill:#9C27B0,color:#fff
```

**Cas d'Usage**: Déploiements staging et petite production

**Spécifications**:
- Nœuds manager: 3x (2 CPU, 4 Go RAM)
- Nœuds worker: 3+ (8-16 CPU, 32-64 Go RAM)
- Nœud base de données: 1-2 (4 CPU, 16 Go RAM, SSD)
- Nœuds stockage: 4+ (2 CPU, 8 Go RAM, HDD/SSD)

**Avantages**:
- Haute disponibilité
- Mise à l'échelle facile
- Équilibrage de charge intégré
- Surveillance de santé

**Inconvénients**:
- Plus complexe que mono-hôte
- Nécessite stockage partagé ou volumes
- Complexité configuration réseau

### Topologie 3: Cluster Kubernetes

```mermaid
graph TB
    subgraph "Couche Ingress"
        ING[Contrôleur Ingress<br/>nginx/traefik]
    end
    
    subgraph "Namespace Application"
        subgraph "Airbyte"
            A1[airbyte-webapp]
            A2[airbyte-server]
            A3[airbyte-worker<br/>HPA: 2-10]
        end
        
        subgraph "Dremio"
            D1[dremio-coordinator]
            D2[dremio-executor<br/>StatefulSet: 3+]
        end
        
        subgraph "Superset"
            S1[superset-web<br/>Deployment: 2+]
        end
    end
    
    subgraph "Namespace Données"
        subgraph "PostgreSQL"
            P1[postgres-primary]
            P2[postgres-replica<br/>StatefulSet: 2]
        end
        
        subgraph "MinIO"
            M1[minio-pool<br/>StatefulSet: 4+]
        end
        
        subgraph "Elasticsearch"
            E1[es-master<br/>StatefulSet: 3]
            E2[es-data<br/>StatefulSet: 3+]
        end
    end
    
    subgraph "Stockage"
        PVC1[PersistentVolumeClaims]
        SC1[StorageClass<br/>fast-ssd]
        SC2[StorageClass<br/>standard]
    end
    
    ING --> A1 & D1 & S1
    
    A1 & A2 & A3 --> P1
    D1 & D2 --> P1
    D1 & D2 --> M1
    S1 --> P1
    
    P1 -.->|Réplication| P2
    
    P1 & P2 & M1 & E1 & E2 -.-> PVC1
    PVC1 -.-> SC1 & SC2
    
    style ING fill:#4CAF50,color:#fff
    style A1 fill:#615EFF,color:#fff
    style D1 fill:#FDB515
    style S1 fill:#20A7C9,color:#fff
    style P1 fill:#336791,color:#fff
    style M1 fill:#C72E49,color:#fff
    style E1 fill:#005571,color:#fff
```

**Cas d'Usage**: Déploiements production à grande échelle

**Spécifications**:
- Plan de contrôle: 3+ nœuds (géré ou auto-hébergé)
- Nœuds worker: 10+ nœuds (16-32 CPU, 64-128 Go RAM)
- Stockage: Pilote CSI (EBS, GCP PD, Azure Disk)
- Réseau: Plugin CNI (Calico, Cilium)

**Avantages**:
- Orchestration niveau entreprise
- Mise à l'échelle et réparation automatisées
- Réseau avancé (service mesh)
- Compatible GitOps
- Support multi-tenant

**Inconvénients**:
- Configuration et gestion complexes
- Courbe d'apprentissage plus raide
- Surcharge opérationnelle plus élevée

---

## Déploiement Docker Compose

### Environnement de Développement

Notre `docker-compose.yml` standard pour développement local:

```yaml
version: '3.8'

services:
  # Airbyte Platform
  airbyte-server:
    image: airbyte/server:0.50.33
    container_name: airbyte-server
    ports:
      - "8001:8001"
    environment:
      - DATABASE_USER=airbyte
      - DATABASE_PASSWORD=airbyte
      - DATABASE_DB=airbyte
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - WORKSPACE_ROOT=/tmp/workspace
      - CONFIG_ROOT=/data
      - TRACKING_STRATEGY=logging
    volumes:
      - airbyte-data:/data
      - airbyte-workspace:/tmp/workspace
    depends_on:
      - postgres
    networks:
      - data-platform

  airbyte-webapp:
    image: airbyte/webapp:0.50.33
    container_name: airbyte-webapp
    ports:
      - "8000:80"
    environment:
      - AIRBYTE_SERVER_HOST=airbyte-server
      - AIRBYTE_SERVER_PORT=8001
    depends_on:
      - airbyte-server
    networks:
      - data-platform

  airbyte-worker:
    image: airbyte/worker:0.50.33
    container_name: airbyte-worker
    environment:
      - DATABASE_USER=airbyte
      - DATABASE_PASSWORD=airbyte
      - DATABASE_DB=airbyte
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - WORKSPACE_ROOT=/tmp/workspace
      - LOCAL_ROOT=/tmp/airbyte_local
    volumes:
      - airbyte-workspace:/tmp/workspace
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - postgres
      - airbyte-server
    networks:
      - data-platform

  # Dremio Lakehouse
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      - "9047:9047"   # Web UI
      - "31010:31010" # ODBC/JDBC
      - "32010:32010" # Arrow Flight
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms2g -Xmx4g
    volumes:
      - dremio-data:/opt/dremio/data
      - ./config/dremio.conf:/opt/dremio/conf/dremio.conf
    networks:
      - data-platform

  # Apache Superset
  superset:
    image: apache/superset:3.0.0
    container_name: superset
    ports:
      - "8088:8088"
    environment:
      - SUPERSET_SECRET_KEY=your-secret-key-here
      - SUPERSET_LOAD_EXAMPLES=yes
    volumes:
      - superset-data:/app/superset_home
    command: >
      sh -c "superset db upgrade &&
             superset fab create-admin 
               --username admin 
               --firstname Admin 
               --lastname User 
               --email admin@example.com 
               --password admin &&
             superset init &&
             superset run -h 0.0.0.0 -p 8088"
    depends_on:
      - postgres
    networks:
      - data-platform

  # PostgreSQL Database
  postgres:
    image: postgres:16
    container_name: postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=postgres
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-databases.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - data-platform
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MinIO Object Storage
  minio:
    image: minio/minio:latest
    container_name: minio
    ports:
      - "9000:9000"  # API
      - "9001:9001"  # Console
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"
    networks:
      - data-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    container_name: elasticsearch
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - es-data:/usr/share/elasticsearch/data
    networks:
      - data-platform
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  airbyte-data:
  airbyte-workspace:
  dremio-data:
  superset-data:
  postgres-data:
  minio-data:
  es-data:

networks:
  data-platform:
    driver: bridge
```

### Surcharges Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Surcharge avec paramètres production
  dremio:
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms8g -Xmx16g
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
        reservations:
          cpus: '4'
          memory: 8G

  postgres:
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}  # Depuis .env
    volumes:
      - /mnt/data/postgres:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  minio:
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    volumes:
      - /mnt/data/minio:/data
    deploy:
      replicas: 4  # MinIO distribué
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

**Déployer en production**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Déploiement Kubernetes

### Configuration Namespace

```yaml
# namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: data-platform
  labels:
    name: data-platform
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: data-storage
  labels:
    name: data-storage
    environment: production
```

### Déploiement Airbyte

```yaml
# airbyte-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airbyte-server
  namespace: data-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: airbyte-server
  template:
    metadata:
      labels:
        app: airbyte-server
    spec:
      containers:
      - name: server
        image: airbyte/server:0.50.33
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: airbyte-secrets
              key: db-user
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: airbyte-secrets
              key: db-password
        - name: DATABASE_HOST
          value: postgres-service.data-storage.svc.cluster.local
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: airbyte-server
  namespace: data-platform
spec:
  selector:
    app: airbyte-server
  ports:
  - protocol: TCP
    port: 8001
    targetPort: 8001
  type: ClusterIP
```

### StatefulSet Dremio

```yaml
# dremio-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: dremio-executor
  namespace: data-platform
spec:
  serviceName: dremio-executor
  replicas: 3
  selector:
    matchLabels:
      app: dremio
      role: executor
  template:
    metadata:
      labels:
        app: dremio
        role: executor
    spec:
      containers:
      - name: dremio
        image: dremio/dremio-oss:26.0
        ports:
        - containerPort: 9047
        - containerPort: 31010
        - containerPort: 32010
        env:
        - name: DREMIO_JAVA_SERVER_EXTRA_OPTS
          value: "-Xms8g -Xmx16g"
        - name: DREMIO_COORDINATOR
          value: "false"
        - name: DREMIO_MASTER_HOST
          value: dremio-coordinator.data-platform.svc.cluster.local
        resources:
          requests:
            memory: "16Gi"
            cpu: "4000m"
          limits:
            memory: "32Gi"
            cpu: "8000m"
        volumeMounts:
        - name: dremio-data
          mountPath: /opt/dremio/data
  volumeClaimTemplates:
  - metadata:
      name: dremio-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

### Autoscaler Horizontal de Pods

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airbyte-worker-hpa
  namespace: data-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airbyte-worker
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
```

### Configuration Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: data-platform-ingress
  namespace: data-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "500m"
spec:
  tls:
  - hosts:
    - airbyte.example.com
    - dremio.example.com
    - superset.example.com
    secretName: data-platform-tls
  rules:
  - host: airbyte.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: airbyte-webapp
            port:
              number: 80
  - host: dremio.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dremio-coordinator
            port:
              number: 9047
  - host: superset.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: superset-web
            port:
              number: 8088
```

### Stockage Persistant

```yaml
# storage-class.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  fsType: ext4
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

---

## Déploiements Cloud

### Architecture AWS

```mermaid
graph TB
    subgraph "VPC: 10.0.0.0/16"
        subgraph "Sous-réseau Public: 10.0.1.0/24"
            ALB[Application Load Balancer]
            NAT[Passerelle NAT]
        end
        
        subgraph "Sous-réseau Privé 1: 10.0.10.0/24"
            EKS1[Nœud Worker EKS 1]
            EKS2[Nœud Worker EKS 2]
        end
        
        subgraph "Sous-réseau Privé 2: 10.0.20.0/24"
            RDS1[RDS PostgreSQL<br/>Multi-AZ]
        end
        
        subgraph "Sous-réseau Privé 3: 10.0.30.0/24"
            S3GW[Point de Terminaison Passerelle S3]
        end
    end
    
    subgraph "Services AWS"
        S3[Buckets S3<br/>bronze/silver/gold]
        ECR[Registre Conteneurs ECR]
        CW[CloudWatch Logs]
        SM[Secrets Manager]
    end
    
    Internet[Internet] --> ALB
    ALB --> EKS1 & EKS2
    EKS1 & EKS2 --> RDS1
    EKS1 & EKS2 --> S3GW
    S3GW --> S3
    EKS1 & EKS2 --> ECR
    EKS1 & EKS2 --> CW
    EKS1 & EKS2 --> SM
    EKS1 & EKS2 --> NAT --> Internet
    
    style ALB fill:#FF9900
    style EKS1 fill:#FF9900
    style RDS1 fill:#527FFF
    style S3 fill:#569A31
    style CW fill:#FF4F8B
```

**Services AWS Utilisés**:
- **EKS**: Cluster Kubernetes géré
- **RDS**: PostgreSQL Multi-AZ pour métadonnées
- **S3**: Stockage objet pour data lake
- **ALB**: Application load balancer
- **CloudWatch**: Surveillance et journalisation
- **Secrets Manager**: Gestion identifiants
- **ECR**: Registre conteneurs
- **VPC**: Isolation réseau

**Exemple Terraform**:
```hcl
# main.tf
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "data-platform-prod"
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    general = {
      min_size     = 3
      max_size     = 10
      desired_size = 5

      instance_types = ["m5.2xlarge"]
      capacity_type  = "ON_DEMAND"
    }
  }
}

module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "data-platform-db"

  engine               = "postgres"
  engine_version       = "16.1"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 100
  max_allocated_storage = 1000

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]

  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "data-platform-datalake-prod"

  versioning = {
    enabled = true
  }

  lifecycle_rule = [
    {
      id      = "bronze-to-glacier"
      enabled = true

      transition = [
        {
          days          = 90
          storage_class = "GLACIER"
        }
      ]
    }
  ]
}
```

### Architecture Azure

**Services Azure**:
- **AKS**: Azure Kubernetes Service
- **Azure Database for PostgreSQL**: Serveur flexible
- **Azure Blob Storage**: Data Lake Gen2
- **Application Gateway**: Équilibreur de charge
- **Azure Monitor**: Surveillance et journalisation
- **Key Vault**: Gestion secrets
- **ACR**: Azure Container Registry

### Architecture GCP

**Services GCP**:
- **GKE**: Google Kubernetes Engine
- **Cloud SQL**: PostgreSQL avec HA
- **Cloud Storage**: Stockage objet
- **Cloud Load Balancing**: Équilibreur de charge global
- **Cloud Logging**: Journalisation centralisée
- **Secret Manager**: Gestion identifiants
- **Artifact Registry**: Registre conteneurs

---

## Configuration Haute Disponibilité

### Haute Disponibilité Base de Données

```mermaid
graph LR
    subgraph "Centre de Données Primaire"
        APP1[Pods Application] --> PG1[PostgreSQL Primaire]
        PG1 -.->|Réplication Streaming| PG2[PostgreSQL Secondaire]
    end
    
    subgraph "Centre de Données Secondaire"
        PG3[PostgreSQL Secondaire]
    end
    
    PG1 -.->|Réplication Async| PG3
    PG2 -.->|Candidat Failover| PG1
    
    style PG1 fill:#336791,color:#fff
    style PG2 fill:#336791,color:#fff
    style PG3 fill:#336791,color:#fff
```

**Configuration HA PostgreSQL**:
```yaml
# postgresql.conf pour primaire
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB
synchronous_commit = on
synchronous_standby_names = 'standby1'

# pg_hba.conf
host replication replicator standby1-ip/32 md5
host replication replicator standby2-ip/32 md5
```

### Configuration MinIO Distribuée

```bash
# MinIO distribué 4 nœuds
docker run -d \
  -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=password" \
  minio/minio server \
  http://minio-{1...4}.example.com/data{1...4} \
  --console-address ":9001"
```

**Erasure Coding**: MinIO protège automatiquement les données avec erasure coding (EC:4 pour 4+ nœuds).

### Configuration Cluster Dremio

```conf
# dremio.conf pour coordinateur
coordinator.enabled: true
coordinator.master.enabled: true

# dremio.conf pour exécuteur
coordinator.enabled: false
executor.enabled: true

# Connexion au coordinateur
zookeeper: "coordinator1:2181,coordinator2:2181,coordinator3:2181"
```

---

## Stratégies de Mise à l'Échelle

### Mise à l'Échelle Verticale

**Quand utiliser**: Composants uniques atteignant limites ressources

| Composant | Initial | Mis à l'échelle | Amélioration |
|-----------|---------|-----------------|--------------|
| Exécuteur Dremio | 8 CPU, 16 Go | 16 CPU, 32 Go | 2x performance requête |
| PostgreSQL | 4 CPU, 8 Go | 8 CPU, 16 Go | 2x débit transactions |
| Worker Airbyte | 2 CPU, 4 Go | 4 CPU, 8 Go | 2x parallélisme sync |

```yaml
# Mise à jour ressources Kubernetes
kubectl set resources deployment airbyte-worker \
  --limits=cpu=4,memory=8Gi \
  --requests=cpu=2,memory=4Gi
```

### Mise à l'Échelle Horizontale

**Quand utiliser**: Besoin gérer plus de charges de travail concurrentes

```yaml
# Mettre à l'échelle exécuteurs Dremio
kubectl scale statefulset dremio-executor --replicas=6

# Mettre à l'échelle workers Airbyte
kubectl scale deployment airbyte-worker --replicas=5

# Mettre à l'échelle serveurs web Superset
kubectl scale deployment superset-web --replicas=4
```

**Politique Autoscaling**:
```yaml
# Cibler 70% utilisation CPU
kubectl autoscale deployment airbyte-worker \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

### Mise à l'Échelle Stockage

**MinIO**: Ajouter nœuds au cluster distribué
```bash
# Étendre de 4 à 8 nœuds
minio server \
  http://minio-{1...8}.example.com/data{1...4}
```

**PostgreSQL**: Utiliser pooling connexions (PgBouncer)
```ini
# pgbouncer.ini
[databases]
* = host=postgres port=5432

[pgbouncer]
listen_addr = *
listen_port = 6432
max_client_conn = 1000
default_pool_size = 25
```

---

## Configuration Sécurité

### Sécurité Réseau

```yaml
# NetworkPolicy: Restreindre trafic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: data-platform-network-policy
  namespace: data-platform
spec:
  podSelector:
    matchLabels:
      app: dremio
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: superset
    - podSelector:
        matchLabels:
          app: airbyte
    ports:
    - protocol: TCP
      port: 9047
    - protocol: TCP
      port: 32010
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: minio
    ports:
    - protocol: TCP
      port: 9000
```

### Gestion des Secrets

```yaml
# Secret Kubernetes
apiVersion: v1
kind: Secret
metadata:
  name: data-platform-secrets
  namespace: data-platform
type: Opaque
stringData:
  postgres-password: "change-me-in-production"
  minio-root-password: "change-me-in-production"
  superset-secret-key: "change-me-in-production"
---
# Utiliser dans déploiement
env:
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: data-platform-secrets
      key: postgres-password
```

**External Secrets Operator** (recommandé pour production):
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: data-platform-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: data-platform-secrets
  data:
  - secretKey: postgres-password
    remoteRef:
      key: prod/data-platform/postgres
      property: password
```

### Configuration TLS/SSL

```yaml
# Certificat cert-manager
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: data-platform-tls
  namespace: data-platform
spec:
  secretName: data-platform-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - airbyte.example.com
  - dremio.example.com
  - superset.example.com
```

---

## Surveillance et Journalisation

### Métriques Prometheus

```yaml
# ServiceMonitor pour Dremio
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dremio-metrics
  namespace: data-platform
spec:
  selector:
    matchLabels:
      app: dremio
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Tableaux de Bord Grafana

**Métriques Clés**:
- Airbyte: Taux succès sync, enregistrements synchronisés, durée sync
- Dremio: Nombre requêtes, durée requêtes, fraîcheur réflexions
- PostgreSQL: Nombre connexions, taux transactions, taux succès cache
- MinIO: Taux requêtes, bande passante, taux erreurs

### Journalisation Centralisée

```yaml
# DaemonSet Fluentd
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.data-storage.svc.cluster.local"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

---

## Reprise après Sinistre

### Stratégie de Sauvegarde

```mermaid
gantt
    title Planification Sauvegarde
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Base de Données
    Sauvegarde Complète           :00:00, 2h
    Sauvegarde Incrémentielle     :06:00, 30m
    Sauvegarde Incrémentielle     :12:00, 30m
    Sauvegarde Incrémentielle     :18:00, 30m
    
    section Stockage Objet
    Snapshot Quotidien            :01:00, 1h
    
    section Métadonnées
    Sauvegarde Configuration      :02:00, 30m
```

**Sauvegarde PostgreSQL**:
```bash
# Sauvegarde complète avec pg_basebackup
pg_basebackup -h postgres -U postgres -D /backup/full -Ft -z -P

# Archivage continu (WAL)
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

**Sauvegarde MinIO**:
```bash
# Réplication bucket vers site DR
mc admin bucket remote add minio/datalake \
  https://dr-minio.example.com/datalake \
  --service replication

mc replicate add minio/datalake \
  --remote-bucket datalake \
  --replicate delete,delete-marker
```

### Procédures de Récupération

**Objectifs RTO/RPO**:
| Environnement | RTO (Objectif Temps Récupération) | RPO (Objectif Point Récupération) |
|---------------|-----------------------------------|-----------------------------------|
| Développement | 24 heures | 24 heures |
| Staging | 4 heures | 4 heures |
| Production | 1 heure | 15 minutes |

**Étapes de Récupération**:
1. Évaluer portée de la défaillance
2. Restaurer base de données depuis dernière sauvegarde
3. Appliquer logs WAL jusqu'au point de défaillance
4. Restaurer stockage objet depuis snapshot
5. Redémarrer services dans ordre dépendances
6. Vérifier intégrité données
7. Reprendre opérations

---

## Bonnes Pratiques

### Liste de Contrôle Déploiement

- [ ] Utiliser infrastructure as code (Terraform/Helm)
- [ ] Implémenter workflow GitOps (ArgoCD/Flux)
- [ ] Configurer contrôles santé pour tous services
- [ ] Définir limites et requêtes ressources
- [ ] Activer autoscaling où approprié
- [ ] Implémenter politiques réseau
- [ ] Utiliser gestion secrets externe
- [ ] Configurer TLS pour tous points de terminaison externes
- [ ] Mettre en place surveillance et alertes
- [ ] Implémenter agrégation logs
- [ ] Configurer sauvegardes automatisées
- [ ] Tester procédures reprise après sinistre
- [ ] Documenter runbooks pour problèmes courants
- [ ] Mettre en place pipelines CI/CD
- [ ] Implémenter déploiements blue-green ou canary

### Ajustement Performance

**Dremio**:
```conf
# Augmenter mémoire pour grandes requêtes
services.coordinator.master.heap_memory_mb: 16384
services.executor.heap_memory_mb: 32768

# Ajuster rafraîchissement réflexion
reflection.refresh.threads: 8
reflection.refresh.schedule.interval: 3600000  # 1 heure
```

**PostgreSQL**:
```conf
# Optimiser pour charge de travail lecture intensive
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 1GB

# Pooling connexions
max_connections = 200
```

**MinIO**:
```bash
# Définir classe stockage optimale pour objets
mc mb --with-lock minio/datalake
mc retention set --default GOVERNANCE 30d minio/datalake
```

### Optimisation Coûts

1. **Dimensionner ressources correctement**: Surveiller utilisation réelle et ajuster limites
2. **Utiliser instances spot/préemptibles**: Pour charges de travail non critiques
3. **Implémenter politiques cycle de vie données**: Déplacer données froides vers niveaux stockage moins chers
4. **Planifier mise à l'échelle ressources**: Réduire pendant heures creuses
5. **Utiliser instances réservées**: Pour capacité de base (économies 40-60%)

---

## Résumé

Ce guide architecture déploiement couvre :

- **Topologies**: Développement mono-hôte, Docker Swarm multi-hôte, cluster Kubernetes
- **Orchestration**: Docker Compose pour dev, Kubernetes pour production
- **Déploiements Cloud**: Architectures de référence AWS, Azure et GCP
- **Haute Disponibilité**: Réplication base de données, stockage distribué, services clusterisés
- **Mise à l'Échelle**: Stratégies mise à l'échelle verticale et horizontale avec autoscaling
- **Sécurité**: Politiques réseau, gestion secrets, configuration TLS/SSL
- **Surveillance**: Métriques Prometheus, tableaux de bord Grafana, journalisation centralisée
- **Reprise après Sinistre**: Stratégies sauvegarde, objectifs RTO/RPO, procédures récupération

Points clés à retenir :
- Commencer simple (mono-hôte) et mettre à l'échelle selon besoins
- Kubernetes offre plus de flexibilité pour production
- Implémenter surveillance complète dès premier jour
- Tout automatiser avec infrastructure as code
- Tester procédures reprise après sinistre régulièrement

**Documentation Associée:**
- [Vue d'Ensemble Architecture](./overview.md)
- [Composants](./components.md)
- [Flux de Données](./data-flow.md)
- [Guide Installation](../getting-started/installation.md)

---

**Version**: 3.2.0  
**Dernière Mise à Jour**: 16 octobre 2025
