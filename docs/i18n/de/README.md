# Datenplattform

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>


**Enterprise Data Lakehouse-LÃ¶sung**

**Sprache**: FranzÃ¶sisch (FR)  
**Version**: 3.3.1  
**Letzte Aktualisierung**: 19. Oktober 2025

---

## Ãœbersicht

Professionelle Datenplattform, die Dremio, dbt und Apache Superset fÃ¼r Datentransformation, QualitÃ¤tssicherung und Business Intelligence auf Unternehmensniveau kombiniert.

Diese Plattform bietet eine KomplettlÃ¶sung fÃ¼r modernes Data Engineering, einschlieÃŸlich automatisierter Datenpipelines, QualitÃ¤tstests und interaktiver Dashboards.

```mermaid
graph LR
    A[Sources de donnÃ©es] --> B[Dremio]
    B --> C[dbt]
    C --> D[Superset]
    D --> E[Insights mÃ©tier]
    
    style B fill:#f5f5f5,stroke:#333,stroke-width:2px
    style C fill:#e8e8e8,stroke:#333,stroke-width:2px
    style D fill:#d8d8d8,stroke:#333,stroke-width:2px
```

---

## Hauptmerkmale

- Daten-Lakehouse-Architektur mit Dremio
- Automatisierte Transformationen mit dbt
- Business Intelligence mit Apache Superset
- Umfassende PrÃ¼fung der DatenqualitÃ¤t
- Echtzeitsynchronisierung Ã¼ber Arrow Flight

---

## Kurzanleitung

### Voraussetzungen

- Docker 20.10 oder hÃ¶her
- Docker Compose 2.0 oder hÃ¶her
- Python 3.11 oder hÃ¶her
- Mindestens 8 GB RAM

### Einrichtung

```bash
# Installer les dÃ©pendances
pip install -r requirements.txt

# DÃ©marrer les services
make up

# VÃ©rifier l'installation
make status

# ExÃ©cuter les tests de qualitÃ©
make dbt-test
```

---

## Architektur

### Systemkomponenten

| Komponente | Hafen | Beschreibung |
|---------------|------|-------------|
| Dremio | 9047, 31010, 32010 | Data Lakehouse-Plattform |
| dbt | - | Datentransformationstool |
| Obermenge | 8088 | Business-Intelligence-Plattform |
| PostgreSQL | 5432 | Transaktionsdatenbank |
| MinIO | 9000, 9001 | Objektspeicher (S3-kompatibel) |
| Elasticsearch | 9200 | Such- und Analysemaschine |

AusfÃ¼hrliche Informationen zum Systemdesign finden Sie in der [Architekturdokumentation](architecture/).

---

## Dokumentation

### Start-up
- [Installationsanleitung](erste Schritte/)
- [Konfiguration](erste Schritte/)
- [Erste Schritte](getting-started/)

### BenutzerhandbÃ¼cher
- [Datentechnik](Anleitungen/)
- [Erstellung von Dashboards](guides/)
- [API-Integration](guides/)

### API-Dokumentation
- [REST-API-Referenz](api/)
- [Authentifizierung](api/)
- [Codebeispiele](api/)

### Architekturdokumentation
- [Systemdesign](Architektur/)
- [Datenfluss](architecture/)
- [Bereitstellungsleitfaden](architecture/)
- [ðŸŽ¯ Dremio Ports Visual Guide](architecture/dremio-ports-visual.md) â­ NEU

---

## VerfÃ¼gbare Sprachen

| Sprache | Code | Dokumentation |
|--------|------|---------------|
| Englisch | DE | [README.md](../../../README.md) |
| FranzÃ¶sisch | DE | [docs/i18n/fr/](../fr/README.md) |
| Spanisch | ES | [docs/i18n/es/](../es/README.md) |
| Portugiesisch | PT | [docs/i18n/pt/](../pt/README.md) |
| Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© | AR | [docs/i18n/ar/](../ar/README.md) |
| ä¸­æ–‡ | CN | [docs/i18n/cn/](../cn/README.md) |
| æ—¥æœ¬èªž | JP | [docs/i18n/jp/](../jp/README.md) |
| Russisch | GroÃŸbritannien | [docs/i18n/ru/](../ru/README.md) |

---

## UnterstÃ¼tzung

FÃ¼r technische UnterstÃ¼tzung:
- Dokumentation: [README main](../../../README.md)
- Issue Tracker: GitHub-Probleme
- Community-Forum: GitHub-Diskussionen
- E-Mail: support@example.com

---

**[ZurÃ¼ck zur Hauptdokumentation](../../../README.md)**
