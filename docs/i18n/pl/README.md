# Dremio + dbt + OpenMetadata - Dokumentacja (Polski)

**Wersja**: 3.2.5  
**Ostatnia aktualizacja**: 16 października 2025  
**Język**: Polski 🇵🇱

---

## 📚 Przegląd

Witamy w polskiej dokumentacji platformy danych Dremio + dbt + OpenMetadata. Ta dokumentacja zapewnia kompleksowe przewodniki dotyczące instalacji, konfiguracji i użytkowania platformy.

---

## 🗺️ Struktura Dokumentacji

### 📐 Architektura

- **[Dremio Porty - Wizualny Przewodnik](./architecture/dremio-ports-visual.md)** ⭐ NOWOŚĆ!
  - Pełny wizualny przewodnik po 3 portach Dremio (9047, 31010, 32010)
  - Szczegółowa architektura PostgreSQL Proxy
  - Porównania wydajności i testy porównawcze
  - Przypadki użycia i drzewo decyzyjne
  - Przykłady połączeń: psql, DBeaver, Python, Java, ODBC
  - Konfiguracja Docker Compose
  - 456 linii | 8+ diagramów Mermaid | 5 przykładów kodu

---

## 🌍 Dostępne Języki

Ta dokumentacja jest dostępna w wielu językach:

- 🇫🇷 **[Français](../fr/README.md)** - Pełna dokumentacja (22 pliki)
- 🇬🇧 **[English](../../../README.md)** - Pełna dokumentacja (19 plików)
- 🇪🇸 **[Español](../es/README.md)** - Przewodniki wizualne
- 🇵🇹 **[Português](../pt/README.md)** - Przewodniki wizualne
- 🇨🇳 **[中文](../cn/README.md)** - Przewodniki wizualne
- 🇯🇵 **[日本語](../jp/README.md)** - Przewodniki wizualne
- 🇷🇺 **[Русский](../ru/README.md)** - Przewodniki wizualne
- 🇸🇦 **[العربية](../ar/README.md)** - Przewodniki wizualne
- 🇩🇪 **[Deutsch](../de/README.md)** - Przewodniki wizualne
- 🇰🇷 **[한국어](../ko/README.md)** - Przewodniki wizualne
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Przewodniki wizualne
- 🇮🇩 **[Indonesia](../id/README.md)** - Przewodniki wizualne
- 🇹🇷 **[Türkçe](../tr/README.md)** - Przewodniki wizualne
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Przewodniki wizualne
- 🇮🇹 **[Italiano](../it/README.md)** - Przewodniki wizualne
- 🇳🇱 **[Nederlands](../nl/README.md)** - Przewodniki wizualne
- 🇵🇱 **[Polski](../pl/README.md)** - Przewodniki wizualne ⭐ JESTEŚ TUTAJ
- 🇸🇪 **[Svenska](../se/README.md)** - Przewodniki wizualne

---

## 🚀 Szybki Start

### Wymagania

- Docker & Docker Compose
- Python 3.11+
- Git

### Instalacja

```bash
# Sklonuj repozytorium
git clone <repository-url>
cd dremiodbt

# Uruchom usługi Docker
docker-compose up -d

# Otwórz Web UI
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

Szczegółowe instrukcje instalacji można znaleźć w [dokumentacji angielskiej](../en/getting-started/installation.md).

---

## 📖 Główne Zasoby

### Dremio Porty - Szybkie Odniesienie

| Port | Protokół | Użycie | Wydajność |
|------|-----------|------------|----------|
| **9047** | REST API | Web UI, Admin | ⭐⭐ Standardowa |
| **31010** | PostgreSQL Wire | Narzędzia BI, Migracja | ⭐⭐⭐ Dobra |
| **32010** | Arrow Flight | dbt, Superset, Wysoka Wydajność | ⭐⭐⭐⭐⭐ Maksymalna |

**→ [Pełny przewodnik wizualny](./architecture/dremio-ports-visual.md)**

---

## 🔗 Linki Zewnętrzne

- **Dokumentacja Dremio**: https://docs.dremio.com/
- **Dokumentacja dbt**: https://docs.getdbt.com/
- **Dokumentacja OpenMetadata**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Współpraca

Wkład jest mile widziany! Proszę zapoznać się z naszymi [wytycznymi dotyczącymi współpracy](../en/CONTRIBUTING.md).

---

## 📄 Licencja

Ten projekt jest licencjonowany na podstawie [Licencji MIT](../../../LICENSE).

---

**Wersja**: 3.2.5  
**Status**: ✅ Gotowe do Produkcji  
**Ostatnia aktualizacja**: 16 października 2025
