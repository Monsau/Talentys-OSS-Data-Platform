# Przewodnik instalacji

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Język**: francuski

---

## Przegląd

Ten przewodnik zawiera instrukcje krok po kroku dotyczące instalacji i konfiguracji kompletnej platformy danych, w tym Airbyte, Dremio, dbt, Apache Superset i infrastruktury pomocniczej.

§§§KOD_0§§§

---

## Warunki wstępne

### Wymagania systemowe

**Minimalne wymagania:**
- **Procesor**: 4 rdzenie (zalecane 8+)
- **RAM**: 8 GB (zalecane 16+ GB)
- **Miejsce na dysku**: dostępne 20 GB (zalecane 50+ GB)
- **Sieć**: Stabilne połączenie internetowe dla obrazów Dockera

**Systemy operacyjne:**
- Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- macOS (11.0+)
- Windows 10/11 z WSL2

### Wymagane oprogramowanie

#### 1. Okno dokowane

**Wersja**: 20.10 lub wyższa

**Obiekt:**

**Linuks:**
§§§KOD_1§§§

**macOS:**
§§§KOD_2§§§

**Okna:**
§§§KOD_3§§§

#### 2. Tworzenie Dockera

**Wersja**: 2.0 lub wyższa

**Obiekt:**

§§§KOD_4§§§

**Uwaga**: Docker Desktop dla systemów macOS i Windows zawiera Docker Compose.

#### 3. Python

**Wersja**: 3.11 lub wyższa

**Obiekt:**

**Linux (Ubuntu/Debian):**
§§§KOD_5§§§

**macOS:**
§§§KOD_6§§§

**Okna:**
§§§KOD_7§§§

**Weryfikacja:**
§§§KOD_8§§§

#### 4. Git

**Obiekt:**

§§§KOD_9§§§

**Weryfikacja:**
§§§KOD_10§§§

---

## Kroki instalacji

### Krok 1: Sklonuj repozytorium

§§§KOD_11§§§

**Oczekiwana struktura:**
§§§KOD_12§§§

### Krok 2: Skonfiguruj środowisko

#### Utwórz plik środowiska

§§§KOD_13§§§

#### Zmienne środowiskowe

**Podstawowa konfiguracja:**
§§§KOD_14§§§

### Krok 3: Zainstaluj zależności Pythona

#### Utwórz środowisko wirtualne

§§§KOD_15§§§

#### Wymagania dotyczące instalacji

§§§KOD_16§§§

**Kluczowe zainstalowane pakiety:**
- `pyarrow>=21.0.0` - Klient lotu Arrow
- `pandas>=2.3.0` - Manipulacja danymi
- `dbt-core>=1.10.0` - Transformacja danych
- `sqlalchemy>=2.0.0` - Łączność z bazą danych
- `pyyaml>=6.0.0` - Zarządzanie konfiguracją

### Krok 4: Uruchom usługi Docker

#### Uruchom główne usługi

§§§KOD_22§§§

**Rozpoczęte usługi:**
- PostgreSQL (port 5432)
- Dremio (porty 9047, 32010)
- Superset Apache (port 8088)
- MinIO (porty 9000, 9001)
- Elasticsearch (port 9200)

#### Rozpocznij Airbyte (utwórz osobno)

§§§KOD_23§§§

**Uruchomiono usługi Airbyte:**
- Serwer Airbyte (port 8001)
- Interfejs sieciowy Airbyte (port 8000)
- Pracownik Airbyte'a
- Czasowy Airbyte
- Baza danych Airbyte'a

#### Sprawdź stan usług

§§§KOD_24§§§

---

## Weryfikacja

### Krok 5: Sprawdź usługi

#### 1. PostgreSQL

§§§KOD_25§§§

**Oczekiwana wydajność:**
§§§KOD_26§§§

#### 2. Dremio

**Interfejs sieciowy:**
§§§KOD_27§§§

**Pierwsze połączenie:**
- Nazwa użytkownika: `admin`
- Hasło: `admin123`
- Przy pierwszym dostępie zostaniesz poproszony o utworzenie konta administratora

**Przetestuj połączenie:**
§§§KOD_30§§§

#### 3. Airbyte

**Interfejs sieciowy:**
§§§KOD_31§§§

**Domyślne identyfikatory:**
- E-mail: `airbyte@example.com`
- Hasło: `password`

**Przetestuj interfejs API:**
§§§KOD_34§§§

**Oczekiwana odpowiedź:**
§§§KOD_35§§§

#### 4. Nadzbiór Apache

**Interfejs sieciowy:**
§§§KOD_36§§§

**Domyślne identyfikatory:**
- Nazwa użytkownika: `admin`
- Hasło: `admin`

**Przetestuj połączenie:**
§§§KOD_39§§§

#### 5. MinIO

** Interfejs konsoli:**
§§§KOD_40§§§

**Referencje:**
- Nazwa użytkownika: `minioadmin`
- Hasło: `minioadmin123`

**Przetestuj API S3:**
§§§KOD_43§§§

#### 6. Elastyczne wyszukiwanie

**Przetestuj połączenie:**
§§§KOD_44§§§

**Oczekiwana odpowiedź:**
§§§KOD_45§§§

### Krok 6: Uruchom kontrolę stanu

§§§KOD_46§§§

**Oczekiwana wydajność:**
§§§KOD_47§§§

---

## Konfiguracja poinstalacyjna

### 1. Zainicjuj Dremio

§§§KOD_48§§§

**Tworzy:**
- Użytkownik administracyjny
- Domyślne źródła (PostgreSQL, MinIO)
- Przykładowe zbiory danych

### 2. Zainicjuj nadzbiór

§§§KOD_49§§§

### 3. Skonfiguruj dbt

§§§KOD_50§§§

### 4. Skonfiguruj Airbyte

**Za pośrednictwem interfejsu internetowego (http://localhost:8000):**

1. Ukończ kreatora konfiguracji
2. Skonfiguruj pierwsze źródło (np.: PostgreSQL)
3. Skonfiguruj miejsce docelowe (np. MinIO S3)
4. Utwórz połączenie
5. Uruchom pierwszą synchronizację

**Przez API:**
§§§KOD_51§§§

---

## Struktura katalogów po instalacji

§§§KOD_52§§§

---

## Rozwiązywanie problemów

### Typowe problemy

#### 1. Port jest już używany

**Błąd:**
§§§KOD_53§§§

**Rozwiązanie:**
§§§KOD_54§§§

#### 2. Za mało pamięci

**Błąd:**
§§§KOD_55§§§

**Rozwiązanie:**
§§§KOD_56§§§

#### 3. Usługi nie uruchamiają się

**Sprawdź logi:**
§§§KOD_57§§§

#### 4. Problemy z siecią

**Zresetuj sieć Dockera:**
§§§KOD_58§§§

#### 5. Problemy z uprawnieniami (Linux)

**Rozwiązanie:**
§§§KOD_59§§§

---

## Dezinstalacja

### Zatrzymaj usługi

§§§KOD_60§§§

### Usuń dane (opcjonalnie)

§§§KOD_61§§§

### Usuń obrazy Dockera

§§§KOD_62§§§

---

## Następne kroki

Po pomyślnej instalacji:

1. **Skonfiguruj źródła danych** — zobacz [Przewodnik konfiguracji](configuration.md)
2. **Poradnik pierwszych kroków** — zobacz [Pierwsze kroki](first-steps.md)
3. **Konfiguracja Airbyte** — zobacz [Przewodnik integracji Airbyte](../guides/airbyte-integration.md)
4. **Konfiguracja Dremio** — zobacz [Przewodnik konfiguracji Dremio](../guides/dremio-setup.md)
5. **Utwórz modele dbt** - Zobacz [Przewodnik programisty dbt](../guides/dbt-development.md)
6. **Tworzenie pulpitów nawigacyjnych** — zobacz [Przewodnik po pulpitach nawigacyjnych Superset](../guides/superset-dashboards.md)

---

## Wsparcie

W przypadku problemów z instalacją:

- **Dokumentacja**: [Przewodnik rozwiązywania problemów](../guides/troubleshooting.md)
- **Problemy z GitHub**: https://github.com/your-org/dremiodbt/issues
- **Społeczność**: https://github.com/your-org/dremiodbt/discussions

---

**Wersja instrukcji instalacji**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Obsługiwane przez**: Zespół ds. platformy danych