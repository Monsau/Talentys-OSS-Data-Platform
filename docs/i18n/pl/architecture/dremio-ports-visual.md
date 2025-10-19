# Wizualny przewodnik po portach Dremio

**Wersja**: 3.2.3  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

---

## Przegląd 3 portów Dremio

§§§KOD_0§§§

---

## Szczegółowa architektura serwera proxy PostgreSQL

### Przebieg połączenia klienta → Dremio

§§§KOD_1§§§

---

## Porównanie wydajności

### Benchmark: Skan 100 GB danych

§§§KOD_2§§§

### Szybkość transmisji danych

§§§KOD_3§§§

### Proste opóźnienie zapytania

| Protokół | Port | Średnie opóźnienie | Narzut sieciowy |
|--------------|------|----------------|----------------|
| **API REST** | 9047 | 50-100ms | JSON (pełny) |
| **Proxy PostgreSQL** | 31010 | 20-50ms | Protokół przewodowy (kompaktowy) |
| **Lot strzały** | 32010 | 5-10ms | Strzałka Apache (kolumna binarna) |

---

## Przypadek użycia według portu

### Port 9047 — API REST

§§§KOD_4§§§

### Port 31010 — serwer proxy PostgreSQL

§§§KOD_5§§§

### Port 32010 – Lot strzały

§§§KOD_6§§§

---

## Drzewo decyzyjne: jakiego portu użyć?

§§§KOD_7§§§

---

## Przykłady połączeń proxy PostgreSQL

### 1. Interfejs wiersza polecenia psql

§§§KOD_8§§§

### 2. Konfiguracja DBeavera

§§§KOD_9§§§

### 3. Python z psycopg2

§§§KOD_10§§§

### 4. JDBC Java

§§§KOD_11§§§

### 5. Ciąg ODBC (DSN)

§§§KOD_12§§§

---

## Konfiguracja Docker Compose

### Mapowanie portów Dremio

§§§KOD_13§§§

### Kontrola portu

§§§KOD_14§§§

---

## Szybkie podsumowanie wizualne

### Rzut oka na 3 porty

| Port | Protokół | Główne zastosowanie | Wydajność | Kompatybilność |
|------|----------|----------------------------|------------|--------------|
| **9047** | API REST | 🌐 Interfejs sieciowy, administrator | ⭐⭐Standardowy | ⭐⭐⭐ Uniwersalny |
| **31010** | Przewód PostgreSQL | 💼 Narzędzia BI, Migracja | ⭐⭐⭐ Dobrze | ⭐⭐⭐ Doskonale |
| **32010** | Lot strzałą | ⚡ Produkcja, dbt, Superset | ⭐⭐⭐⭐⭐ Maksymalnie | ⭐⭐ Ograniczona |

### Macierz wyboru

§§§KOD_15§§§

---

## Dodatkowe zasoby

### Powiązana dokumentacja

- [Architektura - Komponenty](./components.md) - Sekcja "PostgreSQL Proxy dla Dremio"
- [Poradnik - Instalacja Dremio](../guides/dremio-setup.md) - Sekcja "Połączenie przez PostgreSQL Proxy"
- [Konfiguracja - Dremio](../getting-started/configuration.md) - Parametry `dremio.conf`

### Oficjalne linki

- **Dokumentacja Dremio**: https://docs.dremio.com/
- **Protokół PostgreSQL Wire**: https://www.postgresql.org/docs/current/protocol.html
- **Lot Apache Arrow**: https://arrow.apache.org/docs/format/Flight.html

---

**Wersja**: 3.2.3  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Stan**: ✅ Ukończony