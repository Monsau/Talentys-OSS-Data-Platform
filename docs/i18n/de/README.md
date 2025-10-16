# Dremio + dbt + OpenMetadata - Dokumentation (Deutsch)

**Version**: 3.2.5  
**Letzte Aktualisierung**: 16. Oktober 2025  
**Sprache**: Deutsch 🇩🇪

---

## 📚 Übersicht

Willkommen zur deutschen Dokumentation für die Dremio + dbt + OpenMetadata Datenplattform. Diese Dokumentation bietet umfassende Anleitungen zur Einrichtung, Konfiguration und Nutzung der Plattform.

---

## 🗺️ Dokumentationsstruktur

### 📐 Architektur

- **[Dremio Ports - Visuelle Anleitung](./architecture/dremio-ports-visual.md)** ⭐ NEU!
  - Vollständiger visueller Leitfaden zu den 3 Dremio-Ports (9047, 31010, 32010)
  - PostgreSQL Proxy detaillierte Architektur
  - Leistungsvergleiche und Benchmarks
  - Anwendungsfälle und Entscheidungsbaum
  - Verbindungsbeispiele: psql, DBeaver, Python, Java, ODBC
  - Docker Compose Konfiguration
  - 456 Zeilen | 8+ Mermaid-Diagramme | 5 Code-Beispiele

---

## 🌍 Verfügbare Sprachen

Diese Dokumentation ist in mehreren Sprachen verfügbar:

- 🇫🇷 **[Français](../fr/README.md)** - Vollständige Dokumentation (22 Dateien)
- 🇬🇧 **[English](../../../README.md)** - Vollständige Dokumentation (19 Dateien)
- 🇪🇸 **[Español](../es/README.md)** - Visuelle Anleitungen
- 🇵🇹 **[Português](../pt/README.md)** - Visuelle Anleitungen
- 🇨🇳 **[中文](../cn/README.md)** - Visuelle Anleitungen
- 🇯🇵 **[日本語](../jp/README.md)** - Visuelle Anleitungen
- 🇷🇺 **[Русский](../ru/README.md)** - Visuelle Anleitungen
- 🇸🇦 **[العربية](../ar/README.md)** - Visuelle Anleitungen
- 🇩🇪 **[Deutsch](../de/README.md)** - Visuelle Anleitungen ⭐ SIE SIND HIER
- 🇰🇷 **[한국어](../ko/README.md)** - Visuelle Anleitungen
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Visuelle Anleitungen
- 🇮🇩 **[Indonesia](../id/README.md)** - Visuelle Anleitungen
- 🇹🇷 **[Türkçe](../tr/README.md)** - Visuelle Anleitungen
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Visuelle Anleitungen
- 🇮🇹 **[Italiano](../it/README.md)** - Visuelle Anleitungen
- 🇳🇱 **[Nederlands](../nl/README.md)** - Visuelle Anleitungen
- 🇵🇱 **[Polski](../pl/README.md)** - Visuelle Anleitungen
- 🇸🇪 **[Svenska](../se/README.md)** - Visuelle Anleitungen

---

## 🚀 Schnellstart

### Voraussetzungen

- Docker & Docker Compose
- Python 3.11+
- Git

### Installation

```bash
# Repository klonen
git clone <repository-url>
cd dremiodbt

# Docker-Services starten
docker-compose up -d

# Web-UI öffnen
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

Ausführliche Installationsanweisungen finden Sie in der [englischen Dokumentation](../en/getting-started/installation.md).

---

## 📖 Wichtige Ressourcen

### Dremio Ports - Schnellreferenz

| Port | Protokoll | Verwendung | Leistung |
|------|-----------|------------|----------|
| **9047** | REST API | Web UI, Administration | ⭐⭐ Standard |
| **31010** | PostgreSQL Wire | BI-Tools, Migration | ⭐⭐⭐ Gut |
| **32010** | Arrow Flight | dbt, Superset, Hochleistung | ⭐⭐⭐⭐⭐ Maximal |

**→ [Vollständige visuelle Anleitung](./architecture/dremio-ports-visual.md)**

---

## 🔗 Externe Links

- **Dremio Dokumentation**: https://docs.dremio.com/
- **dbt Dokumentation**: https://docs.getdbt.com/
- **OpenMetadata Dokumentation**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Beitragen

Beiträge sind willkommen! Bitte beachten Sie unsere [Beitragsrichtlinien](../en/CONTRIBUTING.md).

---

## 📄 Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](../../../LICENSE).

---

**Version**: 3.2.5  
**Status**: ✅ Produktionsbereit  
**Letzte Aktualisierung**: 16. Oktober 2025
