# Dataplattform

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>


**Enterprise data lakehouse-lÃ¶sning**

**SprÃ¥k**: Franska (FR)  
**Version**: 3.3.1  
**Senast uppdaterad**: 19 oktober 2025

---

## Ã–versikt

Professionell dataplattform som kombinerar Dremio, dbt och Apache Superset fÃ¶r datatransformation av fÃ¶retagsklass, kvalitetssÃ¤kring och business intelligence.

Denna plattform tillhandahÃ¥ller en komplett lÃ¶sning fÃ¶r modern datateknik, inklusive automatiserade datapipelines, kvalitetstester och interaktiva instrumentpaneler.

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

## Nyckelfunktioner

- Data lakehouse-arkitektur med Dremio
- Automatiserade transformationer med dbt
- Business Intelligence med Apache Superset
- Omfattande datakvalitetstestning
- Synkronisering i realtid via Arrow Flight

---

## Snabbstartguide

### FÃ¶rutsÃ¤ttningar

- Docker 20.10 eller senare
- Docker Compose 2.0 eller hÃ¶gre
- Python 3.11 eller hÃ¶gre
- Minst 8 GB RAM

### AnlÃ¤ggning

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

## Arkitektur

### Systemkomponenter

| Komponent | Hamn | Beskrivning |
|---------------|------|-------------|
| Dremio | 9047, 31010, 32010 | Data Lakehouse-plattform |
| dbt | - | Datatransformationsverktyg |
| Superset | 8088 | Business Intelligence-plattform |
| PostgreSQL | 5432 | Transaktionsdatabas |
| MinIO | 9000, 9001 | Objektlagring (S3-kompatibel) |
| Elasticsearch | 9200 | SÃ¶k- och analysmotor |

Se [arkitekturdokumentationen](arkitektur/) fÃ¶r detaljerad systemdesign.

---

## Dokumentation

### Start
- [Installationsguide](komma igÃ¥ng/)
- [Konfiguration](komma igÃ¥ng/)
- [Komma igÃ¥ng](komma igÃ¥ng/)

### AnvÃ¤ndarguider
- [Datateknik](guider/)
- [Skapa instrumentpaneler](guider/)
- [API-integration](guider/)

### API-dokumentation
- [REST API-referens](api/)
- [Autentisering](api/)
- [Kodexempel](api/)

### Arkitekturdokumentation
- [Systemdesign](arkitektur/)
- [DataflÃ¶de](arkitektur/)
- [Deployment guide](arkitektur/)
- [ðŸŽ¯ Dremio Ports Visual Guide](architecture/dremio-ports-visual.md) â­ NYTT

---

## TillgÃ¤ngliga sprÃ¥k

| SprÃ¥k | Kod | Dokumentation |
|--------|------|---------------|
| engelska | SV | [README.md](../../../README.md) |
| franska | SV | [docs/i18n/fr/](../fr/README.md) |
| Spanska | ES | [docs/i18n/es/](../es/README.md) |
| portugisiska | PT | [docs/i18n/pt/](../pt/README.md) |
| Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© | AR | [docs/i18n/ar/](../ar/README.md) |
| ä¸­æ–‡ | CN | [docs/i18n/cn/](../cn/README.md) |
| æ—¥æœ¬èªž | JP | [docs/i18n/jp/](../jp/README.md) |
| Ð ÑƒÑÑÐºÐ¸Ð¹ | Storbritannien | [docs/i18n/ru/](../ru/README.md) |

---

## Support

FÃ¶r teknisk hjÃ¤lp:
- Dokumentation: [README main](../../../README.md)
- Issue Tracker: GitHub-problem
- Gemenskapsforum: GitHub-diskussioner
- E-post: support@talentys.eu

---

**[Ã…tergÃ¥ till huvuddokumentationen](../../../README.md)**
