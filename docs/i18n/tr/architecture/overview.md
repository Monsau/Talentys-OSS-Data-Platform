# Mimariye Genel Bakış

**Sürüm**: 3.2.0  
**Son güncelleme**: 2025-10-16  
**Dil**: Fransızca

---

## Giriiş

Veri platformu, açık kaynak teknolojileri üzerine kurulu, modern, bulutta yerleşik bir mimaridir. Kurumsal ölçekte analitik iş yükleri için tasarlanmış, veri alımı, depolama, dönüştürme ve görselleştirmeye yönelik kapsamlı bir çözüm sunar.

```mermaid
graph TB
    subgraph "Couche d'Ingestion"
        AB[Airbyte<br/>Intégration Données]
    end
    
    subgraph "Couche de Stockage"
        S3[MinIO S3<br/>Data Lake]
        PG[PostgreSQL<br/>OLTP]
        ES[Elasticsearch<br/>Recherche]
    end
    
    subgraph "Couche de Traitement"
        DR[Dremio<br/>Lakehouse]
        DBT[dbt<br/>Transform]
    end
    
    subgraph "Couche de Présentation"
        SUP[Superset<br/>Plateforme BI]
    end
    
    AB --> S3
    AB --> PG
    S3 --> DR
    PG --> DR
    ES --> DR
    DR <--> DBT
    DR --> SUP
    
    style AB fill:#615EFF,color:#fff
    style DR fill:#FDB515
    style DBT fill:#FF694B,color:#fff
    style SUP fill:#20A7C9,color:#fff
```

---

## Tasarım İlkeleri

### 1. Önce Kaynağı Açın

**Felsefe**: Satıcıya bağımlı kalmayı önlemek ve esnekliği korumak için açık kaynak teknolojilerini kullanın.

**Faydalar**:
- Lisans maliyeti yok
- Topluluk gelişimi
- Tam kişiselleştirme yeteneği
- Şeffaf güvenlik denetimi
- Geniş ekosistem uyumluluğu

### 2. Katmanlı Mimari

**Felsefe**: Sürdürülebilirlik ve ölçeklenebilirlik için endişeleri farklı katmanlara ayırın.

**Katmanlar**:
```
┌─────────────────────────────────────┐
│     Couche de Présentation          │  Superset (BI & Tableaux de Bord)
├─────────────────────────────────────┤
│     Couche Sémantique               │  Dremio (Moteur de Requête)
├─────────────────────────────────────┤
│     Couche de Transformation        │  dbt (Transformation Données)
├─────────────────────────────────────┤
│     Couche de Stockage              │  MinIO, PostgreSQL, Elasticsearch
├─────────────────────────────────────┤
│     Couche d'Ingestion              │  Airbyte (Intégration Données)
└─────────────────────────────────────┘
```

### 3. ETL yerine ELT

**Felsefe**: Önce ham verileri yükleyin, hedefe (ELT) dönüştürün.

**Neden ELT?**
- **Esneklik**: Verileri yeniden çıkartmaya gerek kalmadan birden fazla şekilde dönüştürün
- **Performans**: Dönüşümler için hedef hesaplamayı kullanın
- **Denetlenebilirlik**: Ham veriler her zaman doğrulama için kullanılabilir
- **Maliyet**: Kaynak sistemlerdeki ekstraksiyon yükünü azaltın

**Akış**:
```
Extract → Load → Transform
(Airbyte) (MinIO/PostgreSQL) (dbt + Dremio)
```

### 4. Veri Gölevi Modeli

**Felsefe**: Veri gölünün esnekliğini veri ambarının performansıyla birleştirin.

**Özellikler**:
- **ASİT İşlemleri**: Güvenilir Veri İşlemleri
- **Şema uygulaması**: Veri kalitesi garantileri
- **Zaman yolculuğu**: Geçmiş versiyonları sorgulama
- **Açık formatlar**: Parke, Buzdağı, Delta Lake
- **Doğrudan dosya erişimi**: Tescilli kilitleme yok

### 5. Bulutta Yerel Tasarım

**Felsefe**: Konteynerli ve dağıtılmış ortamlar için tasarım.

**Uygulama**:
- Tüm hizmetler için liman işçisi konteynerleri
- Yatay ölçeklenebilirlik
- Kod olarak altyapı
- Mümkün olan her yerde vatansız
- Ortam değişkenleri aracılığıyla yapılandırma

---

## Mimari Modeller

### Lambda mimarisi (Toplu + Akış)

```mermaid
graph LR
    subgraph "Sources de Données"
        SRC[Sources]
    end
    
    subgraph "Couche Batch"
        B1[Airbyte Batch] --> B2[MinIO S3]
        B2 --> B3[Vues Dremio]
    end
    
    subgraph "Couche Vitesse"
        S1[Airbyte CDC] --> S2[PostgreSQL]
        S2 --> S3[Dremio Live]
    end
    
    subgraph "Couche Service"
        B3 --> MERGE[Vue Unifiée]
        S3 --> MERGE
        MERGE --> SUP[Superset]
    end
    
    SRC --> B1
    SRC --> S1
```

**Toplu Katman** (Geçmiş Verileri):
- Büyük miktarda veri
- Periyodik tedavi (saatlik/günlük)
- Kabul edilebilir yüksek gecikme süresi
- Tamamen yeniden işleme mümkündür

**Hız Katmanı** (Gerçek Zamanlı Veriler):
- Veri Yakalamayı Değiştir (CDC)
- Düşük gecikme gerekli
- Yalnızca artımlı güncellemeler
- Son verileri yönetir

**Hizmet Katmanı**:
- Toplu ve hızlı görünümleri birleştirir
- Tek sorgu arayüzü (Dremio)
- Otomatik görünüm seçimi

### Mimari Madalyon (Bronz → Gümüş → Altın)

```mermaid
graph LR
    A[Sources] -->|Brut| B[Couche Bronze<br/>MinIO S3]
    B -->|Nettoyé| C[Couche Silver<br/>dbt Staging]
    C -->|Agrégé| D[Couche Gold<br/>dbt Marts]
    D --> E[Utilisateurs Métier<br/>Superset]
    
    style B fill:#CD7F32,color:#fff
    style C fill:#C0C0C0
    style D fill:#FFD700
```

**Bronz katman** (Ham):
- Kaynaklardan alınan veriler
- Dönüşüm yok
- Tam geçmiş korunmuş
- Airbyte buraya yüklenir

**Gümüş katman** (Temizlenmiş):
- Uygulamalı veri kalitesi
- Standartlaştırılmış formatlar
- dbt hazırlama şablonları
- Analitik hazır

**Altın Katman** (Meslek):
- Toplu metrikler
- Uygulamalı iş mantığı
- Marts dbt modelleri
- Tüketim için optimize edildi

---

## Bileşenler Arası Etkileşimler

### Veri Alma Akışı

```mermaid
sequenceDiagram
    participant Src as Source Données
    participant Ab as Airbyte
    participant S3 as MinIO S3
    participant Dr as Dremio
    participant Pg as PostgreSQL
    
    Src->>Ab: 1. Extraire données
    Ab->>Ab: 2. Transformer en Parquet
    Ab->>S3: 3. Écrire couche bronze
    Ab->>Pg: 4. Écrire métadonnées
    
    Note over S3,Dr: Dremio analyse S3
    Dr->>S3: 5. Lire fichiers Parquet
    Dr->>Dr: 6. Construire métadonnées
    Dr->>Pg: 7. Requêter métadonnées
    
    Note over Dr: Données prêtes pour requêtes
```

### Dönüşüm Boru Hattı

```mermaid
sequenceDiagram
    participant Dr as Dremio
    participant Dbt as dbt
    participant S3 as MinIO S3
    
    Dbt->>Dr: 1. Lire données bronze (SELECT)
    Dr->>S3: 2. Analyser fichiers Parquet
    S3->>Dr: 3. Retourner données
    Dr->>Dbt: 4. Résultats requête
    
    Dbt->>Dbt: 5. Appliquer transformations
    Dbt->>Dbt: 6. Exécuter tests
    
    Dbt->>Dr: 7. Écrire silver/gold (CREATE TABLE)
    Dr->>S3: 8. Écrire Parquet
    S3->>Dr: 9. Confirmer écriture
    Dr->>Dbt: 10. Succès
    
    Note over Dbt,Dr: Données transformées disponibles
```

### Sorguları Yürütme

```mermaid
sequenceDiagram
    participant User as Utilisateur Final
    participant Sup as Superset
    participant Dr as Dremio
    participant S3 as MinIO S3
    participant Pg as PostgreSQL
    
    User->>Sup: 1. Demander tableau de bord
    Sup->>Dr: 2. Exécuter SQL (Arrow Flight)
    
    Dr->>Dr: 3. Parser requête
    Dr->>Dr: 4. Vérifier réflexions (cache)
    
    alt Réflexion disponible
        Dr->>S3: 5a. Lire données en cache
    else Pas de réflexion
        Dr->>S3: 5b. Analyser fichiers source
        Dr->>Pg: 5c. Requêter métadonnées
    end
    
    Dr->>Dr: 6. Exécuter requête
    Dr->>Sup: 7. Retourner résultats (Arrow)
    Sup->>Sup: 8. Rendre graphiques
    Sup->>User: 9. Afficher tableau de bord
```

---

## Ölçeklenebilirlik Modelleri

### Yatay Ölçeklendirme

**Durum Bilgisi Olmayan Hizmetler** (serbestçe gelişebilir):
- Airbyte Workers: Paralel senkronizasyonlar için gelişin
- Dremio Executors: Sorgu performansına göre ölçeklendirme
- Web Superset: Rakip kullanıcılar için gelişin

**Devlet Bilgili Hizmetler** (koordinasyon gerektirir):
- PostgreSQL: Birincil çoğaltma çoğaltması
- MinIO: Dağıtılmış mod (birden fazla düğüm)
- Elasticsearch: Parçalamalı küme

### Dikey Ölçeklendirme

**Yoğun Bellek**:
- Dremio: Büyük sorgular için JVM yığınını artırın
- PostgreSQL: Önbellek arabelleği için daha fazla RAM
- Elasticsearch: İndeksleme için daha fazla yığın

**CPU yoğun**:
- dbt: Paralel yapı modelleri için daha fazla çekirdek
- Airbyte: Daha hızlı veri dönüşümleri

### Veri Bölümleme

```sql
-- Exemple: Partitionner par date
CREATE TABLE orders_partitioned (
    order_id INT,
    customer_id INT,
    amount DECIMAL,
    order_date DATE
)
PARTITION BY (DATE_TRUNC('month', order_date))
STORED AS PARQUET;

-- La requête analyse uniquement les partitions pertinentes
SELECT SUM(amount)
FROM orders_partitioned
WHERE order_date >= '2025-01-01'
  AND order_date < '2025-02-01';
-- Analyse uniquement la partition de janvier
```

---

## Yüksek Kullanılabilirlik

### Hizmetlerin Fazlalığı

```mermaid
graph TB
    subgraph "Équilibreur de Charge"
        LB[HAProxy/Nginx]
    end
    
    subgraph "Niveau Application"
        SUP1[Superset 1]
        SUP2[Superset 2]
        SUP3[Superset 3]
    end
    
    subgraph "Niveau Données"
        DR1[Dremio Primaire]
        DR2[Dremio Exécuteur 1]
        DR3[Dremio Exécuteur 2]
    end
    
    subgraph "Niveau Stockage"
        PG1[(PostgreSQL Primaire)]
        PG2[(PostgreSQL Réplique)]
        S3C[Cluster MinIO]
    end
    
    LB --> SUP1
    LB --> SUP2
    LB --> SUP3
    
    SUP1 --> DR1
    SUP2 --> DR1
    SUP3 --> DR1
    
    DR1 --> DR2
    DR1 --> DR3
    
    DR1 --> S3C
    DR2 --> S3C
    DR3 --> S3C
    
    DR1 --> PG1
    PG1 -.->|Réplication| PG2
```

### Arıza Senaryoları

| Bileşen | Arıza | Kurtarma |
|---------------|----------|-----------|
| **Airbyte Çalışanı** | Konteyner kazası | Otomatik yeniden başlatma, senkronizasyona devam etme |
| **Dremio Yürütücüsü** | Düğüm hatası | İstek diğer uygulayıcılara yönlendirildi |
| **PostgreSQL** | Birincil hizmet dışı | Birincilde kopyayı tanıtın |
| **MinIO Düğümü** | Disk hatası | Silme kodlaması verileri yeniden yapılandırır |
| **Süper set** | Servis hizmet dışı | Dengeleyici trafiği yönlendirir |

### Yedekleme Stratejisi

```bash
# Sauvegardes automatisées quotidiennes
0 2 * * * /scripts/backup_all.sh

# backup_all.sh
#!/bin/bash

# Sauvegarder PostgreSQL
pg_dumpall -U postgres > /backups/postgres_$(date +%Y%m%d).sql

# Sauvegarder métadonnées Dremio
tar czf /backups/dremio_$(date +%Y%m%d).tar.gz /opt/dremio/data

# Synchroniser MinIO vers S3 distant
mc mirror MinIOLake/datalake s3-offsite/datalake-backup

# Conserver 30 jours
find /backups -mtime +30 -delete
```

---

## Güvenlik Mimarisi

### Ağ Güvenliği

```mermaid
graph TB
    subgraph "Externe"
        U[Utilisateurs]
    end
    
    subgraph "DMZ"
        FW[Pare-feu]
        RP[Proxy Inverse]
    end
    
    subgraph "Réseau Application"
        SUP[Superset :8088]
        DR[Dremio :9047/:31010/:32010]
        AB[Airbyte :8000]
    end
    
    subgraph "Réseau Données"
        PG[PostgreSQL :5432]
        S3[MinIO :9000]
        ES[Elasticsearch :9200]
    end
    
    U -->|HTTPS| FW
    FW --> RP
    RP --> SUP
    RP --> DR
    RP --> AB
    
    SUP --> PG
    SUP --> DR
    DR --> PG
    DR --> S3
    DR --> ES
    AB --> PG
    AB --> S3
```

### Kimlik Doğrulama ve Yetkilendirme

**Hizmet Kimlik Doğrulaması**:
- **Dremio**: LDAP/AD, OAuth2, SAML entegrasyonu
- **Süperset**: Veritabanı Kimlik Doğrulaması, LDAP, OAuth2
- **Airbyte**: Temel Kimlik Doğrulaması, OAuth2 (kurumsal)
- **MinIO**: IAM politikaları, STS belirteçleri

**Yetki Düzeyleri**:
```yaml
Rôles:
  - Admin:
      - Accès complet à tous les services
      - Gestion utilisateurs
      - Modifications configuration
  
  - Data Engineer:
      - Créer/modifier sources données
      - Exécuter syncs Airbyte
      - Exécuter modèles dbt
      - Créer datasets Dremio
  
  - Analyst:
      - Accès lecture seule données
      - Créer tableaux de bord Superset
      - Requêter datasets Dremio
  
  - Viewer:
      - Voir tableaux de bord uniquement
      - Pas d'accès données
```

### Veri Şifreleme

**Dinlenme Halinde**:
- MinIO: Sunucu tarafı şifreleme (AES-256)
- PostgreSQL: Şeffaf Veri Şifreleme (TDE)
- Elasticsearch: Şifreli dizinler

**Transit olarak**:
- Tüm servisler arası iletişim için TLS 1.3
- Dremio için TLS ile Ok Uçuşu ↔ Superset
- Web arayüzleri için HTTPS

---

## İzleme ve Gözlemlenebilirlik

### Metrik Koleksiyonu

```mermaid
graph LR
    A[Airbyte] -->|Métriques| P[Prometheus]
    D[Dremio] -->|Métriques| P
    S[Superset] -->|Métriques| P
    PG[PostgreSQL] -->|Métriques| P
    M[MinIO] -->|Métriques| P
    
    P --> G[Grafana]
    P --> AL[Alertmanager]
    
    AL -->|Email| E[Email]
    AL -->|Slack| SL[Slack]
```

**Temel Metrikler**:
- **Airbyte**: Senkronizasyon başarı oranı, senkronize edilen kayıtlar, aktarılan bayt sayısı
- **Dremio**: İstek gecikmesi, önbellek isabet oranı, kaynak kullanımı
- **dbt**: Model oluşturma süresi, test hataları
- **Süperset**: Kontrol paneli yükleme süresi, aktif kullanıcılar
- **Altyapı**: CPU, bellek, disk, ağ

### Günlük kaydı

**Merkezi Günlük Kaydı**:
```yaml
Stack ELK:
  - Elasticsearch: Stocker logs
  - Logstash: Traiter logs
  - Kibana: Visualiser logs

Sources de Logs:
  - Logs application (format JSON)
  - Logs d'accès
  - Logs d'audit
  - Logs d'erreur
```

### İzleme

**Dağıtılmış İzleme**:
- Jaeger veya Zipkin entegrasyonu
- Hizmetler arasındaki istekleri izleme
- Darboğazları tanımlayın
- Performans sorunlarında hata ayıklama

---

## Dağıtım Topolojileri

### Geliştirme Ortamı

```yaml
Hôte Unique:
  Ressources: 8 Go RAM, 4 CPUs
  Services: Tous sur une machine
  Stockage: Volumes locaux
  Réseau: Réseau bridge
  Cas d'usage: Développement, tests
```

### Hazırlama Ortamı

```yaml
Multi-Hôtes:
  Ressources: 16 Go RAM, 8 CPUs par hôte
  Services: Répartis sur 2-3 hôtes
  Stockage: NFS partagé ou MinIO distribué
  Réseau: Réseau overlay
  Cas d'usage: Tests pré-production, UAT
```

### Üretim Ortamı

```yaml
Cluster Kubernetes:
  Ressources: Auto-scaling selon charge
  Services: Conteneurisés, répliqués
  Stockage: Volumes persistants (SSD)
  Réseau: Service mesh (Istio)
  Haute Disponibilité: Déploiement multi-zones
  Cas d'usage: Charges production
```

---

## Teknolojik Seçimlerin Gerekçelendirilmesi

### Neden Airbyte?

- **300'den fazla konektör**: Önceden oluşturulmuş entegrasyonlar
- **Açık kaynak**: Tedarikçi bağımlılığı yok
- **Aktif topluluk**: 12.000'den fazla GitHub yıldızı
- **CDC desteği**: Gerçek zamanlı veri yakalama
- **Standartlaştırma**: Yerleşik dbt entegrasyonu

### Neden Dremio?

- **Sorgu hızlandırma**: 10-100 kat daha hızlı sorgular
- **Arrow Flight**: Yüksek performanslı veri aktarımı
- **Veri gölü uyumluluğu**: Veri hareketi yok
- **Self-servis**: İş kullanıcıları verileri keşfediyor
- **Karlı**: Depo maliyetlerini azaltın

### Neden dbt?

- **SQL Tabanlı**: Analistler için tanıdık
- **Sürüm kontrolü**: Git entegrasyonu
- **Testler**: Entegre veri kalitesi testleri
- **Belgeler**: Otomatik oluşturulan Dokümanlar
- **Topluluk**: 5 binden fazla paket mevcut

### Neden Süperset?

- **Modern kullanıcı arayüzü**: Sezgisel arayüz
- **SQL IDE**: Gelişmiş sorgu yetenekleri
- **Zengin görselleştirmeler**: 50'den fazla grafik türü
- **Genişletilebilir**: Özel eklentiler
- **Açık kaynak**: Desteklenen Apache Vakfı

### Neden PostgreSQL?

- **Güvenilirlik**: ASİT uyumluluğu
- **Performans**: Geniş ölçekte kanıtlanmış
- **Özellikler**: JSON, tam metin araması, uzantılar
- **Topluluk**: Olgun ekosistem
- **Maliyet**: Ücretsiz ve açık kaynak

### Neden MinIO?

- **S3 uyumluluğu**: endüstri standardı API
- **Performans**: Yüksek akış hızı
- **Silme kodlaması**: Veri dayanıklılığı
- **Çoklu bulut**: Her yere dağıtın
- **Uygun maliyetli**: Kendi kendine barındırılan alternatif

---

## Mimarinin Gelecekteki Evrimi

### Planlanan İyileştirmeler

1. **Veri Kataloğu** (OpenMetadata Entegrasyonu)
   - Meta veri yönetimi
   - Soy takibi
   - Veri keşfi

2. **Veri Kalitesi** (Büyük Beklentiler)
   - Otomatik doğrulama
   - Anormallik tespiti
   - Kalite kontrol panelleri

3. **ML İşlemleri** (MLflow)
   - Model eğitim hatları
   - Model kaydı
   - Dağıtım otomasyonu

4. **Akış işleme** (Apache Flink)
   - Gerçek zamanlı dönüşümler
   - Karmaşık olay işleme
   - Akış analitiği

5. **Veri Yönetişimi** (Apache Atlas)
   - Politika uygulaması
   - Erişim denetimi
   - Uyumluluk raporları

---

## Referanslar

- [Bileşen Ayrıntıları](components.md)
- [Veri Akışı](data-flow.md)
- [Dağıtım Kılavuzu](deployment.md)
- [Airbyte Entegrasyonu](../guides/airbyte-integration.md)

---

**Mimariye Genel Bakış Sürümü**: 3.2.0  
**Son Güncelleme**: 2025-10-16  
**Bakımını Yapan**: Veri Platformu Ekibi