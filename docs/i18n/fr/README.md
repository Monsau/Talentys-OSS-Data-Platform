# Plateforme de donnÃ©es

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>


**Solution d'entreprise pour lakehouse de donnÃ©es**

**Langue** : FranÃ§ais (FR)  
**Version**: 3.3.1  
**DerniÃ¨re mise Ã  jour** : 19 octobre 2025

---

## Vue d'ensemble

Plateforme de donnÃ©es professionnelle combinant Dremio, dbt et Apache Superset pour la transformation de donnÃ©es, l'assurance qualitÃ© et l'intelligence d'affaires de niveau entreprise.

Cette plateforme fournit une solution complÃ¨te pour l'ingÃ©nierie de donnÃ©es moderne, comprenant des pipelines de donnÃ©es automatisÃ©s, des tests de qualitÃ© et des tableaux de bord interactifs.

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

## FonctionnalitÃ©s clÃ©s

- Architecture de lakehouse de donnÃ©es avec Dremio
- Transformations automatisÃ©es avec dbt
- Intelligence d'affaires avec Apache Superset
- Tests complets de qualitÃ© des donnÃ©es
- Synchronisation en temps rÃ©el via Arrow Flight

---

## Guide de dÃ©marrage rapide

### PrÃ©requis

- Docker 20.10 ou supÃ©rieur
- Docker Compose 2.0 ou supÃ©rieur
- Python 3.11 ou supÃ©rieur
- Minimum 8 Go de RAM

### Installation

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

## Architecture

### Composants du systÃ¨me

| Composant | Port | Description |
|-----------|------|-------------|
| Dremio | 9047, 31010, 32010 | Plateforme de lakehouse de donnÃ©es |
| dbt | - | Outil de transformation de donnÃ©es |
| Superset | 8088 | Plateforme d'intelligence d'affaires |
| PostgreSQL | 5432 | Base de donnÃ©es transactionnelle |
| MinIO | 9000, 9001 | Stockage objet (compatible S3) |
| Elasticsearch | 9200 | Moteur de recherche et d'analyse |

Consultez la [documentation d'architecture](architecture/) pour la conception dÃ©taillÃ©e du systÃ¨me.

---

## Documentation

### DÃ©marrage
- [Guide d'installation](getting-started/)
- [Configuration](getting-started/)
- [Premiers pas](getting-started/)

### Guides utilisateur
- [IngÃ©nierie des donnÃ©es](guides/)
- [CrÃ©ation de dashboards](guides/)
- [IntÃ©gration API](guides/)

### Documentation API
- [RÃ©fÃ©rence API REST](api/)
- [Authentification](api/)
- [Exemples de code](api/)

### Documentation d'architecture
- [Conception du systÃ¨me](architecture/)
- [Flux de donnÃ©es](architecture/)
- [Guide de dÃ©ploiement](architecture/)
- [ðŸŽ¯ Guide visuel des ports Dremio](architecture/dremio-ports-visual.md) â­ NOUVEAU

---

## Langues disponibles

| Langue | Code | Documentation |
|--------|------|---------------|
| English | EN | [README.md](../../../README.md) |
| FranÃ§ais | FR | [docs/i18n/fr/](../fr/README.md) |
| EspaÃ±ol | ES | [docs/i18n/es/](../es/README.md) |
| PortuguÃªs | PT | [docs/i18n/pt/](../pt/README.md) |
| Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© | AR | [docs/i18n/ar/](../ar/README.md) |
| ä¸­æ–‡ | CN | [docs/i18n/cn/](../cn/README.md) |
| æ—¥æœ¬èªž | JP | [docs/i18n/jp/](../jp/README.md) |
| Ð ÑƒÑÑÐºÐ¸Ð¹ | RU | [docs/i18n/ru/](../ru/README.md) |

---

## Support

Pour l'assistance technique :
- Documentation : [README principal](../../../README.md)
- Suivi des problÃ¨mes : GitHub Issues
- Forum communautaire : GitHub Discussions
- Email : support@example.com

---

**[Retour Ã  la documentation principale](../../../README.md)**

