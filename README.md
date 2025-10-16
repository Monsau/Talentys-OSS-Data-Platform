# 🚀 Data Platform - ISO Opensource

**Enterprise Data Lakehouse Solution**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-18%20languages-success.svg)](docs/i18n/)

**Created by:** [Mustapha Fonsau](https://www.linkedin.com/in/mustapha-fonsau/) | [GitHub](https://github.com/Monsau)

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="https://talentys.eu/logo.png" alt="Supported by Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> - Data Engineering & Analytics Excellence</em>
</p>

> 📖 **Main documentation in English.** Translations available in 17 additional languages below.

---

## 🌍 Available Languages

🇬🇧 **English** (You are here) | [🇫🇷 Français](docs/i18n/fr/README.md) | [🇪🇸 Español](docs/i18n/es/README.md) | [🇵🇹 Português](docs/i18n/pt/README.md) | [🇨🇳 中文](docs/i18n/cn/README.md) | [🇯🇵 日本語](docs/i18n/jp/README.md) | [🇷🇺 Русский](docs/i18n/ru/README.md) | [🇸🇦 العربية](docs/i18n/ar/README.md) | [🇩🇪 Deutsch](docs/i18n/de/README.md) | [🇰🇷 한국어](docs/i18n/ko/README.md) | [🇮🇳 हिन्दी](docs/i18n/hi/README.md) | [🇮🇩 Indonesia](docs/i18n/id/README.md) | [🇹🇷 Türkçe](docs/i18n/tr/README.md) | [🇻🇳 Tiếng Việt](docs/i18n/vi/README.md) | [🇮🇹 Italiano](docs/i18n/it/README.md) | [🇳🇱 Nederlands](docs/i18n/nl/README.md) | [🇵🇱 Polski](docs/i18n/pl/README.md) | [🇸🇪 Svenska](docs/i18n/se/README.md)

---

## Overview

Professional data platform combining **Airbyte**, **Dremio**, **dbt**, and **Apache Superset** for enterprise-grade data integration, transformation, quality assurance, and business intelligence. Built with multilingual support for global teams.

```mermaid
graph LR
    A[Data Sources] --> B[Airbyte ETL]
    B --> C[Dremio Lakehouse]
    C --> D[dbt Transformations]
    D --> E[Apache Superset]
    E --> F[Business Insights]
    
    style B fill:#615EFF,color:#fff,stroke:#333,stroke-width:2px
    style C fill:#f5f5f5,stroke:#333,stroke-width:2px
    style D fill:#e8e8e8,stroke:#333,stroke-width:2px
    style E fill:#d8d8d8,stroke:#333,stroke-width:2px
```

### Key Features

- Data integration with Airbyte 1.8.0 (300+ connectors)
- Data lakehouse architecture with Dremio 26.0
- Automated transformations with dbt 1.10+
- Business intelligence with Apache Superset 3.0
- Comprehensive data quality testing (21 automated tests)
- Real-time synchronization via Arrow Flight
- Multilingual documentation (18 languages)

---

## Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Python 3.11 or higher
- Minimum 8 GB RAM
- 20 GB available disk space

### Installation

```bash
# Clone repository
git clone https://github.com/Monsau/data-platform-iso-opensource.git
cd data-platform-iso-opensource

# Install dependencies
pip install -r requirements.txt

# Start infrastructure
make up

# Verify installation
make status

# Run quality tests
make dbt-test
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airbyte | http://localhost:8000 | - |
| Dremio | http://localhost:9047 | admin / admin123 |
| Superset | http://localhost:8088 | admin / admin |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin123 |
| PostgreSQL | localhost:5432 | postgres / postgres123 |

---

## Architecture

### System Components

| Component | Version | Port | Description |
|-----------|---------|------|-------------|
| **Airbyte** | 1.8.0 | 8000, 8001 | Data integration platform (300+ connectors) |
| **Dremio** | 26.0 | 9047, 32010 | Data lakehouse platform |
| **dbt** | 1.10+ | - | Data transformation tool |
| **Superset** | 3.0.0 | 8088 | Business intelligence platform |
| **PostgreSQL** | 15 | 5432 | Transactional database |
| **MinIO** | Latest | 9000, 9001 | S3-compatible object storage |
| **Elasticsearch** | 7.17.0 | 9200 | Search and analytics engine |
| **MySQL** | 8.0 | 3307 | OpenMetadata database |

### Architecture Diagrams

- [System Architecture with Airbyte](docs/diagrams/architecture-with-airbyte.mmd)
- [Data Flow](docs/diagrams/data-flow.mmd)
- [Airbyte Workflow](docs/diagrams/airbyte-workflow.mmd)
- [Deployment](docs/diagrams/deployment.mmd)
- [User Journey](docs/diagrams/user-journey.mmd)

---

## Multilingual Support

This project provides complete documentation in **18 languages**, covering **5.2B+ people** (70% of global population):

| Language | Documentation | Data Generation | Native Speakers |
|----------|---------------|-----------------|-----------------|
| 🇬🇧 English | [README.md](README.md) | `--language en` | 1.5B |
| 🇫🇷 Français | [docs/i18n/fr/](docs/i18n/fr/README.md) | `--language fr` | 280M |
| 🇪🇸 Español | [docs/i18n/es/](docs/i18n/es/README.md) | `--language es` | 559M |
| 🇵🇹 Português | [docs/i18n/pt/](docs/i18n/pt/README.md) | `--language pt` | 264M |
| 🇸🇦 العربية | [docs/i18n/ar/](docs/i18n/ar/README.md) | `--language ar` | 422M |
| 🇨🇳 中文 | [docs/i18n/cn/](docs/i18n/cn/README.md) | `--language cn` | 1.3B |
| 🇯🇵 日本語 | [docs/i18n/jp/](docs/i18n/jp/README.md) | `--language jp` | 125M |
| 🇷🇺 Русский | [docs/i18n/ru/](docs/i18n/ru/README.md) | `--language ru` | 258M |
| 🇩🇪 Deutsch | [docs/i18n/de/](docs/i18n/de/README.md) | `--language de` | 134M |
| 🇰🇷 한국어 | [docs/i18n/ko/](docs/i18n/ko/README.md) | `--language ko` | 81M |
| 🇮🇳 हिन्दी | [docs/i18n/hi/](docs/i18n/hi/README.md) | `--language hi` | 602M |
| 🇮🇩 Indonesia | [docs/i18n/id/](docs/i18n/id/README.md) | `--language id` | 199M |
| 🇹🇷 Türkçe | [docs/i18n/tr/](docs/i18n/tr/README.md) | `--language tr` | 88M |
| 🇻🇳 Tiếng Việt | [docs/i18n/vi/](docs/i18n/vi/README.md) | `--language vi` | 85M |
| 🇮🇹 Italiano | [docs/i18n/it/](docs/i18n/it/README.md) | `--language it` | 85M |
| 🇳🇱 Nederlands | [docs/i18n/nl/](docs/i18n/nl/README.md) | `--language nl` | 25M |
| 🇵🇱 Polski | [docs/i18n/pl/](docs/i18n/pl/README.md) | `--language pl` | 45M |
| 🇸🇪 Svenska | [docs/i18n/se/](docs/i18n/se/README.md) | `--language se` | 13M |

### Generate Multilingual Test Data

```bash
# Generate French customer data (CSV format)
python config/i18n/data_generator.py --language fr --records 1000 --format csv

# Generate Spanish product data (JSON format)
python config/i18n/data_generator.py --language es --records 500 --format json

# Generate Chinese user data (Parquet format)
python config/i18n/data_generator.py --language cn --records 2000 --format parquet
```

Configuration: [config/i18n/config.json](config/i18n/config.json)

---

## Documentation

### For Different Roles

**Data Engineers**
- [Getting Started](docs/i18n/en/getting-started/)
- [dbt Models](dbt/README.md)
- [Data Quality Tests](reports/phase3/PHASE3_SUCCESS_REPORT.md)

**Data Analysts**
- [Superset Dashboards](reports/superset/SUPERSET_DREMIO_FINAL.md)
- [Query Examples](docs/i18n/en/guides/)
- [Open Data Dashboard](opendata/README.md)

**Developers**
- [API Documentation](docs/i18n/en/api/)
- [Contributing Guide](CONTRIBUTING.md)
- [Architecture](docs/i18n/en/architecture/)

**DevOps**
- [Deployment Guide](docs/i18n/en/architecture/)
- [Docker Configuration](docker-compose.yml)
- [Monitoring Setup](docs/i18n/en/guides/)

---

## Common Commands

```bash
# Infrastructure Management
make up              # Start all services
make down            # Stop all services
make restart         # Restart services
make status          # Check service status
make logs            # View service logs

# Data Transformation (dbt)
make dbt-run         # Run transformations
make dbt-test        # Run quality tests
make dbt-docs        # Generate documentation
make dbt-clean       # Clean artifacts

# Data Synchronization
make sync            # Manual sync Dremio to PostgreSQL
make sync-auto       # Auto sync every 5 minutes

# Testing & Quality
make test            # Run all tests
make lint            # Code quality checks
make format          # Format code

# Deployment
make deploy          # Complete deployment
make deploy-quick    # Quick deployment
```

---

## Project Status

```
Services: 9/9 operational (includes Airbyte)
dbt Tests: 21/21 passing
Dashboards: 3 active
Languages: 18 supported (5.2B+ people coverage)
Documentation: Complete in 18 languages
Status: Production Ready - v1.0
```

---

## Project Structure

```
data-platform-iso-opensource/
├── README.md                       # This file
├── AUTHORS.md                      # Project creators and contributors
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── CODE_OF_CONDUCT.md              # Community guidelines
├── SECURITY.md                     # Security policies
├── LICENSE                         # MIT License
│
├── docs/                           # Documentation
│   ├── i18n/                       # Multilingual docs (18 languages)
│   │   ├── fr/, es/, pt/, cn/, jp/, ru/, ar/
│   │   ├── de/, ko/, hi/, id/, tr/, vi/
│   │   └── it/, nl/, pl/, se/
│   └── diagrams/                   # Mermaid diagrams (248+)
│
├── config/                         # Configuration
│   └── i18n/                       # Internationalization
│       ├── config.json
│       └── data_generator.py
│
├── dbt/                            # Data transformations
│   ├── models/                     # SQL models
│   ├── tests/                      # Quality tests
│   └── dbt_project.yml
│
├── reports/                        # Documentation reports
│   ├── phase1/                     # Integration reports
│   ├── phase2/                     # Data cleaning reports
│   ├── phase3/                     # Quality testing reports
│   ├── superset/                   # Dashboard guides
│   └── integration/                # Integration guides
│
├── scripts/                        # Automation scripts
│   ├── orchestrate_platform.py
│   ├── sync_dremio_realtime.py
│   └── populate_superset.py
│
└── docker-compose.yml              # Infrastructure definition
```

---

## Contributing

We welcome contributions from the community. Please see:
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CONTRIBUTING.md#code-of-conduct)
- [Development Setup](docs/i18n/en/getting-started/)

### Adding a New Language

1. Add language configuration to `config/i18n/config.json`
2. Create documentation directory: `docs/i18n/[language-code]/`
3. Translate README and guides
4. Update main README language table
5. Submit pull request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

**Supported by [Talentys](https://talentys.eu)** - Data Engineering and Analytics Excellence

Built with enterprise-grade open-source technologies:
- [Airbyte](https://airbyte.com/) - Data integration platform (300+ connectors)
- [Dremio](https://www.dremio.com/) - Data lakehouse platform
- [dbt](https://www.getdbt.com/) - Data transformation tool
- [Apache Superset](https://superset.apache.org/) - Business intelligence platform
- [Apache Arrow](https://arrow.apache.org/) - Columnar data format
- [PostgreSQL](https://www.postgresql.org/) - Relational database
- [MinIO](https://min.io/) - Object storage
- [Elasticsearch](https://www.elastic.co/) - Search and analytics

---

## 📧 Contact

**Author:** Mustapha Fonsau
- 🏢 **Organization:** [Talentys](https://talentys.eu)
- 💼 **LinkedIn:** [linkedin.com/in/mustapha-fonsau](https://www.linkedin.com/in/mustapha-fonsau/)
- 🐙 **GitHub:** [github.com/Monsau](https://github.com/Monsau)
- 📧 **Email:** mfonsau@talentys.eu

## Support

For technical assistance:
- 📚 **Documentation:** [docs/i18n/](docs/i18n/)
- 🐛 **Issue Tracker:** [GitHub Issues](https://github.com/Monsau/data-platform-iso-opensource/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/Monsau/data-platform-iso-opensource/discussions)

---

**Version 1.0.0** | **2025-10-16** | **Production Ready**

Made with ❤️ by [Mustapha Fonsau](https://www.linkedin.com/in/mustapha-fonsau/) | Supported by [Talentys](https://talentys.eu)
