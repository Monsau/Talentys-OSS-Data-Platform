# Dremio + dbt + OpenMetadata - Documentatie (Nederlands)

**Versie**: 3.2.5  
**Laatste update**: 16 oktober 2025  
**Taal**: Nederlands 🇳🇱

---

## 📚 Overzicht

Welkom bij de Nederlandse documentatie voor het Dremio + dbt + OpenMetadata dataplatform. Deze documentatie biedt uitgebreide handleidingen voor installatie, configuratie en gebruik van het platform.

---

## 🗺️ Documentatiestructuur

### 📐 Architectuur

- **[Dremio Poorten - Visuele Gids](./architecture/dremio-ports-visual.md)** ⭐ NIEUW!
  - Volledige visuele gids voor de 3 Dremio-poorten (9047, 31010, 32010)
  - Gedetailleerde PostgreSQL Proxy architectuur
  - Prestatievergelijkingen en benchmarks
  - Gebruikscases en beslissingsboom
  - Verbindingsvoorbeelden: psql, DBeaver, Python, Java, ODBC
  - Docker Compose configuratie
  - 456 regels | 8+ Mermaid diagrammen | 5 codevoorbeelden

---

## 🌍 Beschikbare Talen

Deze documentatie is beschikbaar in meerdere talen:

- 🇫🇷 **[Français](../fr/README.md)** - Volledige documentatie (22 bestanden)
- 🇬🇧 **[English](../../../README.md)** - Volledige documentatie (19 bestanden)
- 🇪🇸 **[Español](../es/README.md)** - Visuele gidsen
- 🇵🇹 **[Português](../pt/README.md)** - Visuele gidsen
- 🇨🇳 **[中文](../cn/README.md)** - Visuele gidsen
- 🇯🇵 **[日本語](../jp/README.md)** - Visuele gidsen
- 🇷🇺 **[Русский](../ru/README.md)** - Visuele gidsen
- 🇸🇦 **[العربية](../ar/README.md)** - Visuele gidsen
- 🇩🇪 **[Deutsch](../de/README.md)** - Visuele gidsen
- 🇰🇷 **[한국어](../ko/README.md)** - Visuele gidsen
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Visuele gidsen
- 🇮🇩 **[Indonesia](../id/README.md)** - Visuele gidsen
- 🇹🇷 **[Türkçe](../tr/README.md)** - Visuele gidsen
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Visuele gidsen
- 🇮🇹 **[Italiano](../it/README.md)** - Visuele gidsen
- 🇳🇱 **[Nederlands](../nl/README.md)** - Visuele gidsen ⭐ JE BENT HIER
- 🇵🇱 **[Polski](../pl/README.md)** - Visuele gidsen
- 🇸🇪 **[Svenska](../se/README.md)** - Visuele gidsen

---

## 🚀 Snel Starten

### Vereisten

- Docker & Docker Compose
- Python 3.11+
- Git

### Installatie

```bash
# Clone de repository
git clone <repository-url>
cd dremiodbt

# Start Docker services
docker-compose up -d

# Open Web UI
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

Voor gedetailleerde installatie-instructies, zie de [Engelse documentatie](../en/getting-started/installation.md).

---

## 📖 Belangrijke Bronnen

### Dremio Poorten - Snelle Referentie

| Poort | Protocol | Gebruik | Prestaties |
|------|-----------|------------|----------|
| **9047** | REST API | Web UI, Admin | ⭐⭐ Standaard |
| **31010** | PostgreSQL Wire | BI Tools, Migratie | ⭐⭐⭐ Goed |
| **32010** | Arrow Flight | dbt, Superset, Hoge Prestaties | ⭐⭐⭐⭐⭐ Maximaal |

**→ [Volledige visuele gids](./architecture/dremio-ports-visual.md)**

---

## 🔗 Externe Links

- **Dremio Documentatie**: https://docs.dremio.com/
- **dbt Documentatie**: https://docs.getdbt.com/
- **OpenMetadata Documentatie**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Bijdragen

Bijdragen zijn welkom! Zie onze [bijdrage richtlijnen](../en/CONTRIBUTING.md).

---

## 📄 Licentie

Dit project is gelicentieerd onder de [MIT Licentie](../../../LICENSE).

---

**Versie**: 3.2.5  
**Status**: ✅ Klaar voor Productie  
**Laatste update**: 16 oktober 2025
