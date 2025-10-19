# Pierwsze kroki z platformą danych

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Język**: francuski

---

## Przegląd

Ten samouczek przeprowadzi Cię przez pierwsze interakcje z platformą danych, od łączenia się z usługami po budowanie pierwszego potoku danych za pomocą Airbyte, Dremio, dbt i Superset.

§§§KOD_0§§§

**Szacowany czas**: 60-90 minut

---

## Warunki wstępne

Zanim zaczniesz, upewnij się, że:

- ✅ Wszystkie usługi są zainstalowane i uruchomione
- ✅ Możesz uzyskać dostęp do interfejsów internetowych
- ✅ Środowisko wirtualne Python jest włączone
- ✅ Podstawowa znajomość języka SQL

**Sprawdź, czy usługi działają:**
§§§KOD_1§§§

---

## Krok 1: Uzyskaj dostęp do wszystkich usług

### Adresy URL usług

| Usługi | Adres URL | Domyślne dane uwierzytelniające |
|--------|----------|----------------------------|
| **Airbyte** | http://localhost:8000 | airbyte@example.com / hasło |
| **Dremio** | http://localhost:9047 | admin/admin123 |
| **Nadzbiór** | http://localhost:8088 | administrator / administrator |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### Pierwsze połączenie

**Przesłanie w powietrzu:**
1. Otwórz http://localhost:8000
2. Ukończ kreatora konfiguracji
3. Ustaw nazwę obszaru roboczego: „Produkcja”
4. Zastąp preferencje (możliwa późniejsza konfiguracja)

**Dremio:**
1. Otwórz http://localhost:9047
2. Utwórz użytkownika administratora przy pierwszym dostępie:
   - Nazwa użytkownika: `admin`
   - E-mail: `admin@example.com`
   - Hasło: `admin123`
3. Kliknij „Rozpocznij”

**Nadzbiór:**
1. Otwórz http://localhost:8088
2. Zaloguj się przy użyciu domyślnych danych uwierzytelniających
3. Zmień hasło: Ustawienia → Informacje o użytkowniku → Resetuj hasło

---

## Krok 2: Skonfiguruj swoje pierwsze źródło danych w Airbyte

### Utwórz źródło PostgreSQL

**Scenariusz**: Wyodrębnij dane z bazy danych PostgreSQL.

1. **Przejdź do źródeł**
   - Kliknij „Źródła” w menu po lewej stronie
   - Kliknij „+ Nowe źródło”

2. **Wybierz PostgreSQL**
   - Wyszukaj „PostgreSQL”
   - Kliknij złącze „PostgreSQL”.

3. **Skonfiguruj połączenie**
   §§§KOD_5§§§

4. **Przetestuj i zapisz**
   - Kliknij „Ustaw źródło”
   - Poczekaj na test połączenia
   - Źródło utworzone ✅

### Utwórz przykładowe dane (opcjonalnie)

Jeśli nie masz jeszcze żadnych danych, utwórz przykładowe tabele:

§§§KOD_6§§§

---

## Krok 3: Skonfiguruj miejsce docelowe MinIO S3

### Utwórz miejsce docelowe

1. **Nawiguj do miejsc docelowych**
   - Kliknij „Cele podróży” w menu po lewej stronie
   - Kliknij „+ Nowy cel podróży”

2. **Wybierz S3**
   - Wyszukaj „S3”
   - Kliknij złącze „S3”.

3. **Skonfiguruj MinIO jako S3**
   §§§KOD_7§§§

4. **Przetestuj i zapisz**
   - Kliknij „Ustaw miejsce docelowe”
   - Test połączenia powinien przejść pomyślnie ✅

---

## Krok 4: Utwórz pierwsze połączenie

### Połącz źródło z miejscem docelowym

1. **Przejdź do Połączenia**
   - Kliknij „Połączenia” w menu po lewej stronie
   - Kliknij „+ Nowe połączenie”

2. **Wybierz źródło**
   - Wybierz „Produkcja PostgreSQL”
   - Kliknij „Użyj istniejącego źródła”

3. **Wybierz miejsce docelowe**
   - Wybierz „Jezioro danych MinIO”
   - Kliknij „Użyj istniejącego miejsca docelowego”

4. **Skonfiguruj synchronizację**
   §§§KOD_8§§§

5. **Normalizacja**
   §§§KOD_9§§§

6. **Tworzenie kopii zapasowych i synchronizacja**
   - Kliknij „Skonfiguruj połączenie”
   - Kliknij „Synchronizuj teraz”, aby przeprowadzić pierwszą synchronizację
   - Monitoruj postęp synchronizacji

### Synchronizacja monitorowania

§§§KOD_10§§§

**Sprawdź stan synchronizacji:**
- Status powinien pokazywać „Powodzenie” (zielony)
- Zsynchronizowane rekordy: ~11 (5 klientów + 6 zamówień)
- Zobacz logi, aby uzyskać szczegółowe informacje

---

## Krok 5: Podłącz Dremio do MinIO

### Dodaj źródło S3 w Dremio

1. **Przejdź do źródeł**
   - Otwórz http://localhost:9047
   - Kliknij „Dodaj źródło” (ikona +)

2. **Wybierz S3**
   - Wybierz „Amazon S3”
   - Skonfiguruj jako MinIO:

§§§KOD_11§§§

3. **Przetestuj i zapisz**
   - Kliknij „Zapisz”
   - Dremio przeanalizuje wiadra MinIO

### Przeglądaj dane

1. **Przejdź do źródła MinIOLake**
   - Opracuj „MinIOLake”
   - Opracuj wiadro „datalake”.
   - Rozwiń folder „raw-data”.
   - Zobacz folder „production_public”.

2. **Podgląd danych**
   - Kliknij folder „klienci”.
   - Kliknij plik parkietu
   - Kliknij „Podgląd”, aby zobaczyć dane
   - Dane muszą być zgodne z PostgreSQL ✅

### Utwórz wirtualny zbiór danych

1. **Zapytanie o dane**
   §§§KOD_12§§§

2. **Zapisz jako VDS**
   - Kliknij „Zapisz widok jako”
   - Imię i nazwisko: `vw_customers`
   - Spacja: `@admin` (Twoja przestrzeń)
   - Kliknij „Zapisz”

3. **Format danych** (opcjonalnie)
   - Kliknij `vw_customers`
   - Użyj interfejsu, aby zmienić nazwy kolumn i zmienić typy
   - Przykład: Zmień nazwę `customer_id` na `id`

---

## Krok 6: Utwórz szablony dbt

### Zainicjuj projekt dbt

§§§KOD_18§§§

### Utwórz definicję źródła

**Plik**: `dbt/models/sources.yml`

§§§KOD_20§§§

### Utwórz szablon przejściowy

**Plik**: `dbt/models/staging/stg_customers.sql`

§§§KOD_22§§§

**Plik**: `dbt/models/staging/stg_orders.sql`

§§§KOD_24§§§

### Utwórz szablon Mart

**Plik**: `dbt/models/marts/fct_customer_orders.sql`

§§§KOD_26§§§

### Uruchom modele dbt

§§§KOD_27§§§

### Sprawdź Dremio

§§§KOD_28§§§

---

## Krok 7: Utwórz pulpit nawigacyjny w Superset

### Dodaj bazę danych Dremio

1. **Przejdź do Baz danych**
   - Otwórz http://localhost:8088
   - Kliknij „Dane” → „Bazy danych”
   - Kliknij „+ Baza danych”

2. **Wybierz Dremio**
   §§§KOD_29§§§

3. **Kliknij „Połącz”**

### Utwórz zbiór danych

1. **Przejdź do zbiorów danych**
   - Kliknij „Dane” → „Zestawy danych”
   - Kliknij „+ Zbiór danych”

2. **Skonfiguruj zbiór danych**
   §§§KOD_30§§§

3. **Kliknij „Utwórz zbiór danych i utwórz wykres”**

### Utwórz wykresy

#### Wykres 1: Segmenty klientów (schemat kołowy)

§§§KOD_31§§§

#### Wykres 2: Dochód według kraju (wykres słupkowy)

§§§KOD_32§§§

#### Wykres 3: Dane klientów (duża liczba)

§§§KOD_33§§§

### Utwórz panel kontrolny

1. **Przejdź do Paneli**
   - Kliknij „Panele informacyjne”
   - Kliknij „+ Panel”

2. **Skonfiguruj pulpit nawigacyjny**
   §§§KOD_34§§§

3. **Dodaj grafikę**
   - Przeciągnij i upuść utworzoną grafikę
   - Organizuj w siatce:
     §§§KOD_35§§§

4. **Dodaj filtry** (opcjonalnie)
   - Kliknij „Dodaj filtr”
   - Filtruj według: kod_kraju
   - Zastosuj do wszystkich wykresów

5. **Zapisz panel**

---

## Krok 8: Sprawdź cały rurociąg

### Kompleksowe testowanie

§§§KOD_36§§§

### Dodaj nowe dane

1. **Wstaw nowe rekordy w PostgreSQL**
   §§§KOD_37§§§

2. **Wyzwól synchronizację Airbyte**
   - Otwórz interfejs Airbyte
   - Przejdź do połączenia „PostgreSQL → MinIO”
   - Kliknij „Synchronizuj teraz”
   - Poczekaj na koniec ✅

3. **Uruchom dbt**
   §§§KOD_38§§§

4. **Odśwież panel Superset**
   - Otwórz pulpit nawigacyjny
   - Kliknij przycisk „Odśwież”.
   - Powinny pojawić się nowe dane ✅

### Sprawdź przepływ danych

§§§KOD_39§§§

---

## Krok 9: Zautomatyzuj rurociąg

### Zaplanuj synchronizację Airbyte

Już skonfigurowany do uruchamiania co 24 godziny o 02:00.

Aby edytować:
1. Otwórz połączenie w Airbyte
2. Przejdź do zakładki „Ustawienia”.
3. Zaktualizuj „Częstotliwość replikacji”
4. Zapisz

### Zaplanuj wykonanie dbt

**Opcja 1: Zadanie Cron (Linux)**
§§§KOD_40§§§

**Opcja 2: Skrypt w Pythonie**

**Plik**: `scripts/run_pipeline.py`
§§§KOD_42§§§

### Harmonogram w Docker Compose

**Plik**: `docker-compose.scheduler.yml`
§§§KOD_44§§§

---

## Następne kroki

Gratulacje! Zbudowałeś kompletny, kompleksowy potok danych. 🎉

### Dowiedz się więcej

1. **Airbyte Advanced** - [Przewodnik integracji Airbyte](../guides/airbyte-integration.md)
2. **Optymalizacja Dremio** - [Przewodnik instalacji Dremio](../guides/dremio-setup.md)
3. **Złożone modele dbt** - [Przewodnik programisty dbt](../guides/dbt-development.md)
4. **Zaawansowane pulpity nawigacyjne** - [Przewodnik po pulpitach nawigacyjnych Superset](../guides/superset-dashboards.md)
5. **Jakość danych** – [Przewodnik po jakości danych](../guides/data-quality.md)

### Rozwiązywanie problemów

Jeśli masz problemy, zobacz:
- [Przewodnik rozwiązywania problemów](../guides/troubleshooting.md)
- [Przewodnik instalacji](installation.md#troubleshooting)
- [Przewodnik po konfiguracji](configuration.md)

---

## Streszczenie

Udało Ci się:

- ✅ Uzyskaj dostęp do 7 usług platformy
- ✅ Skonfiguruj źródło Airbyte (PostgreSQL)
- ✅ Skonfiguruj miejsce docelowe Airbyte (MinIO S3)
- ✅ Utwórz swoje pierwsze połączenie Airbyte
- ✅ Połącz Dremio z MinIO
- ✅ Twórz szablony dbt (staging + marty)
- ✅ Zbuduj pulpit nawigacyjny Superset
- ✅ Sprawdź kompleksowy przepływ danych
- ✅ Zautomatyzuj wykonywanie rurociągów

**Twoja platforma danych już działa!** 🚀

---

**Wersja Przewodnika po pierwszych krokach**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Obsługiwane przez**: Zespół ds. platformy danych