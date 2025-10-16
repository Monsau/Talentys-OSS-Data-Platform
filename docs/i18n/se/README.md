# Dremio + dbt + OpenMetadata - Dokumentation (Svenska)

**Version**: 3.2.5  
**Senast uppdaterad**: 16 oktober 2025  
**Språk**: Svenska 🇸🇪

---

## 📚 Översikt

Välkommen till den svenska dokumentationen för Dremio + dbt + OpenMetadata dataplattformen. Denna dokumentation tillhandahåller omfattande guider för installation, konfiguration och användning av plattformen.

---

## 🗺️ Dokumentationsstruktur

### 📐 Arkitektur

- **[Dremio Portar - Visuell Guide](./architecture/dremio-ports-visual.md)** ⭐ NYTT!
  - Komplett visuell guide för de 3 Dremio-portarna (9047, 31010, 32010)
  - Detaljerad PostgreSQL Proxy arkitektur
  - Prestandajämförelser och riktmärken
  - Användningsfall och beslutsträd
  - Anslutningsexempel: psql, DBeaver, Python, Java, ODBC
  - Docker Compose konfiguration
  - 456 rader | 8+ Mermaid diagram | 5 kodexempel

---

## 🌍 Tillgängliga Språk

Denna dokumentation finns tillgänglig på flera språk:

- 🇫🇷 **[Français](../fr/README.md)** - Fullständig dokumentation (22 filer)
- 🇬🇧 **[English](../../../README.md)** - Fullständig dokumentation (19 filer)
- 🇪🇸 **[Español](../es/README.md)** - Visuella guider
- 🇵🇹 **[Português](../pt/README.md)** - Visuella guider
- 🇨🇳 **[中文](../cn/README.md)** - Visuella guider
- 🇯🇵 **[日本語](../jp/README.md)** - Visuella guider
- 🇷🇺 **[Русский](../ru/README.md)** - Visuella guider
- 🇸🇦 **[العربية](../ar/README.md)** - Visuella guider
- 🇩🇪 **[Deutsch](../de/README.md)** - Visuella guider
- 🇰🇷 **[한국어](../ko/README.md)** - Visuella guider
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Visuella guider
- 🇮🇩 **[Indonesia](../id/README.md)** - Visuella guider
- 🇹🇷 **[Türkçe](../tr/README.md)** - Visuella guider
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Visuella guider
- 🇮🇹 **[Italiano](../it/README.md)** - Visuella guider
- 🇳🇱 **[Nederlands](../nl/README.md)** - Visuella guider
- 🇵🇱 **[Polski](../pl/README.md)** - Visuella guider
- 🇸🇪 **[Svenska](../se/README.md)** - Visuella guider ⭐ DU ÄR HÄR

---

## 🚀 Snabbstart

### Förutsättningar

- Docker & Docker Compose
- Python 3.11+
- Git

### Installation

```bash
# Klona repository
git clone <repository-url>
cd dremiodbt

# Starta Docker-tjänster
docker-compose up -d

# Öppna Webb-UI
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

För detaljerade installationsinstruktioner, se [engelsk dokumentation](../en/getting-started/installation.md).

---

## 📖 Viktiga Resurser

### Dremio Portar - Snabbreferens

| Port | Protokoll | Användning | Prestanda |
|------|-----------|------------|----------|
| **9047** | REST API | Webb-UI, Admin | ⭐⭐ Standard |
| **31010** | PostgreSQL Wire | BI-verktyg, Migration | ⭐⭐⭐ Bra |
| **32010** | Arrow Flight | dbt, Superset, Hög Prestanda | ⭐⭐⭐⭐⭐ Maximal |

**→ [Fullständig visuell guide](./architecture/dremio-ports-visual.md)**

---

## 🔗 Externa Länkar

- **Dremio Dokumentation**: https://docs.dremio.com/
- **dbt Dokumentation**: https://docs.getdbt.com/
- **OpenMetadata Dokumentation**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Bidra

Bidrag välkomnas! Se våra [bidragsriktlinjer](../en/CONTRIBUTING.md).

---

## 📄 Licens

Detta projekt är licensierat under [MIT-licensen](../../../LICENSE).

---

**Version**: 3.2.5  
**Status**: ✅ Produktionsklar  
**Senast uppdaterad**: 16 oktober 2025
