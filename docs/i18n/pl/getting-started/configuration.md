# Przewodnik konfiguracji

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Język**: francuski

---

## Przegląd

Ten przewodnik opisuje konfigurację wszystkich komponentów platformy, w tym Airbyte, Dremio, dbt, Apache Superset, PostgreSQL, MinIO i Elasticsearch. Właściwa konfiguracja zapewnia optymalną wydajność, bezpieczeństwo i integrację pomiędzy usługami.

§§§KOD_0§§§

---

## Pliki konfiguracyjne

### Główne pliki konfiguracyjne

§§§KOD_1§§§

---

## Zmienne środowiskowe

### Ustawienia podstawowe

Utwórz lub edytuj plik `.env` w katalogu głównym projektu:

§§§KOD_3§§§

### Dobre praktyki bezpieczeństwa

**Generuj bezpieczne hasła:**
§§§KOD_4§§§

**Nigdy nie udostępniaj wrażliwych danych:**
§§§KOD_5§§§

---

## Konfiguracja usług

### 1. Konfiguracja PostgreSQL

#### Ustawienia połączenia

**Plik**: §§§KOD_6§§§

§§§KOD_7§§§

#### Utwórz bazy danych

§§§KOD_8§§§

### 2. Konfiguracja Dremio

#### Ustawienia pamięci

**Plik**: §§§KOD_9§§§

§§§KOD_10§§§

#### Konfigurowanie źródeł danych

§§§KOD_11§§§

### 3. Konfiguracja Airbyte

#### Ustawienia obszaru roboczego

**Plik**: §§§KOD_12§§§

§§§KOD_13§§§

#### Konfiguracja źródeł prądu

**Źródło PostgreSQL:**
§§§KOD_14§§§

**Miejsce docelowe S3 (MinIO):**
§§§KOD_15§§§

### 4. konfiguracja dbt

#### Konfiguracja projektu

**Plik**: §§§KOD_16§§§

§§§KOD_17§§§

#### Konfiguracja profilu

**Plik**: `dbt/profiles.yml`

§§§KOD_19§§§

### 5. Konfiguracja supersetu Apache

#### Ustawienia aplikacji

**Plik**: `config/superset_config.py`

§§§KOD_21§§§

### 6. Konfiguracja MinIO

#### Konfiguracja łyżki

§§§KOD_22§§§

#### Polityka dostępu

§§§KOD_23§§§

### 7. Konfiguracja Elasticsearch

**Plik**: `config/elasticsearch.yml`

§§§KOD_25§§§

---

## Konfiguracja sieci

### Sieć Dockera

**Plik**: `docker-compose.yml` (sekcja sieciowa)

§§§KOD_27§§§

### Komunikacja pomiędzy usługami

§§§KOD_28§§§

---

## Zarządzanie głośnością

### Trwałe woluminy

**Plik**: `docker-compose.yml` (sekcja tomów)

§§§KOD_30§§§

### Strategia tworzenia kopii zapasowych

§§§KOD_31§§§

---

## Automatyczna konfiguracja

### Skrypt konfiguracyjny

**Plik**: `scripts/configure_platform.py`

§§§KOD_33§§§

**Uruchom konfigurację:**
§§§KOD_34§§§

---

## Następne kroki

Po konfiguracji:

1. **Sprawdź ustawienia** – Uruchom kontrolę stanu
2. **Pierwsze kroki** — zobacz [Przewodnik po pierwszych krokach](first-steps.md)
3. **Skonfiguruj Airbyte** – zobacz [Integracja Airbyte](../guides/airbyte-integration.md)
4. **Skonfiguruj Dremio** - Zobacz [Konfiguracja Dremio](../guides/dremio-setup.md)

---

**Wersja podręcznika konfiguracji**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Obsługiwane przez**: Zespół ds. platformy danych