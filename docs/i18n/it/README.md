# Dremio + dbt + OpenMetadata - Documentazione (Italiano)

**Versione**: 3.2.5  
**Ultimo aggiornamento**: 16 ottobre 2025  
**Lingua**: Italiano 🇮🇹

---

## 📚 Panoramica

Benvenuti nella documentazione italiana per la piattaforma dati Dremio + dbt + OpenMetadata. Questa documentazione fornisce guide complete per l'installazione, la configurazione e l'utilizzo della piattaforma.

---

## 🗺️ Struttura della Documentazione

### 📐 Architettura

- **[Dremio Ports - Guida Visiva](./architecture/dremio-ports-visual.md)** ⭐ NUOVO!
  - Guida visiva completa per le 3 porte Dremio (9047, 31010, 32010)
  - Architettura dettagliata PostgreSQL Proxy
  - Confronti prestazioni e benchmark
  - Casi d'uso e albero decisionale
  - Esempi di connessione: psql, DBeaver, Python, Java, ODBC
  - Configurazione Docker Compose
  - 456 righe | 8+ diagrammi Mermaid | 5 esempi di codice

---

## 🌍 Lingue Disponibili

Questa documentazione è disponibile in più lingue:

- 🇫🇷 **[Français](../fr/README.md)** - Documentazione completa (22 file)
- 🇬🇧 **[English](../../../README.md)** - Documentazione completa (19 file)
- 🇪🇸 **[Español](../es/README.md)** - Guide visive
- 🇵🇹 **[Português](../pt/README.md)** - Guide visive
- 🇨🇳 **[中文](../cn/README.md)** - Guide visive
- 🇯🇵 **[日本語](../jp/README.md)** - Guide visive
- 🇷🇺 **[Русский](../ru/README.md)** - Guide visive
- 🇸🇦 **[العربية](../ar/README.md)** - Guide visive
- 🇩🇪 **[Deutsch](../de/README.md)** - Guide visive
- 🇰🇷 **[한국어](../ko/README.md)** - Guide visive
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Guide visive
- 🇮🇩 **[Indonesia](../id/README.md)** - Guide visive
- 🇹🇷 **[Türkçe](../tr/README.md)** - Guide visive
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Guide visive
- 🇮🇹 **[Italiano](../it/README.md)** - Guide visive ⭐ SEI QUI
- 🇳🇱 **[Nederlands](../nl/README.md)** - Guide visive
- 🇵🇱 **[Polski](../pl/README.md)** - Guide visive
- 🇸🇪 **[Svenska](../se/README.md)** - Guide visive

---

## 🚀 Avvio Rapido

### Prerequisiti

- Docker & Docker Compose
- Python 3.11+
- Git

### Installazione

```bash
# Clona il repository
git clone <repository-url>
cd dremiodbt

# Avvia i servizi Docker
docker-compose up -d

# Apri Web UI
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

Per istruzioni dettagliate sull'installazione, consulta la [documentazione inglese](../en/getting-started/installation.md).

---

## 📖 Risorse Principali

### Dremio Ports - Riferimento Rapido

| Porta | Protocollo | Uso | Prestazioni |
|------|-----------|------------|----------|
| **9047** | REST API | Web UI, Admin | ⭐⭐ Standard |
| **31010** | PostgreSQL Wire | Strumenti BI, Migrazione | ⭐⭐⭐ Buone |
| **32010** | Arrow Flight | dbt, Superset, Alte Prestazioni | ⭐⭐⭐⭐⭐ Massime |

**→ [Guida visiva completa](./architecture/dremio-ports-visual.md)**

---

## 🔗 Link Esterni

- **Documentazione Dremio**: https://docs.dremio.com/
- **Documentazione dbt**: https://docs.getdbt.com/
- **Documentazione OpenMetadata**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Contribuire

I contributi sono benvenuti! Si prega di consultare le nostre [linee guida per contribuire](../en/CONTRIBUTING.md).

---

## 📄 Licenza

Questo progetto è concesso in licenza con [Licenza MIT](../../../LICENSE).

---

**Versione**: 3.2.5  
**Stato**: ✅ Pronto per la Produzione  
**Ultimo aggiornamento**: 16 ottobre 2025
