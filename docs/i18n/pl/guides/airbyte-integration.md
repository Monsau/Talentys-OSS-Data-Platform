# Przewodnik integracji Airbyte

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

---

## Przegląd

Airbyte to platforma integracji danych typu open source, która upraszcza przenoszenie danych z różnych źródeł do miejsc docelowych. Ten przewodnik opisuje integrację Airbyte z platformą danych, konfigurowanie złączy i ustanawianie potoków danych.

§§§KOD_0§§§

---

## Co to jest Airbyte?

### Kluczowe funkcje

- **Ponad 300 gotowych konektorów**: interfejsy API, bazy danych, pliki, aplikacje SaaS
- **Open Source**: hostowane samodzielnie z pełną kontrolą danych
- **Zmień przechwytywanie danych (CDC)**: Synchronizacja danych w czasie rzeczywistym
- **Niestandardowe łączniki**: Twórz łączniki za pomocą języka Python lub CDK o niskim kodzie
- **Normalizacja danych**: Przekształć surowy JSON w tabele strukturalne
- **Monitorowanie i alerty**: Śledź stan synchronizacji i jakość danych

### Architektura

§§§KOD_1§§§

---

## Obiekt

### Szybki start

Airbyte jest częścią platformy. Zacznij od:

§§§KOD_2§§§

### Usługi uruchomione

| Usługi | Port | Opis |
|------------|------|------------|
| **aplikacja internetowa airbyte** | 8000 | Internetowy interfejs użytkownika |
| **serwer airbyte** | 8001 | Serwer API |
| **pracownik lotniczy** | - | Silnik wykonywania zadań |
| **airbyte-temporal** | 7233 | Orkiestracja przepływu pracy |
| **airbyte-db** | 5432 | Baza metadanych (PostgreSQL) |

### Pierwszy dostęp

**Interfejs sieciowy:**
§§§KOD_3§§§

**Domyślne identyfikatory:**
- **E-mail**: `airbyte@example.com`
- **Hasło**: §§§KOD_5§§§

**Zmień hasło** przy pierwszym logowaniu dla bezpieczeństwa.

---

## Konfiguracja

### Kreator konfiguracji

Przy pierwszym dostępie wykonaj kreator konfiguracji:

1. **Preferencje e-mail**: Skonfiguruj powiadomienia
2. **Miejsce przechowywania danych**: Wybierz lokalizację przechowywania danych
3. **Anonimowe statystyki użytkowania**: Zaakceptuj/odrzuć telemetrię

### Ustawienia obszaru roboczego

Przejdź do **Ustawienia > Przestrzeń robocza**:

§§§KOD_6§§§

### Limity zasobów

**Plik**: §§§KOD_7§§§

§§§KOD_8§§§

---

## Złącza

### Złącza źródłowe

#### Źródło PostgreSQL

**Przypadek użycia**: Wyodrębnij dane z transakcyjnej bazy danych

**Konfiguracja:**

1. Przejdź do **Źródła > Nowe źródło**
2. Wybierz **PostgreSQL**
3. Skonfiguruj połączenie:

§§§KOD_9§§§

**Test połączenia** → **Skonfiguruj źródło**

#### Źródło API REST

**Przypadek użycia**: Wyodrębnij dane z interfejsów API

**Konfiguracja:**

§§§KOD_10§§§

#### Plik źródłowy (CSV)

**Przypadek użycia**: Importuj pliki CSV

**Konfiguracja:**

§§§KOD_11§§§

#### Wspólne źródła

| Źródło | Przypadki użycia | Wsparcie CDC |
|--------|--------|------------|
| **PostgreSQL** | Komiksy transakcyjne | ✅Tak |
| **MySQL** | Komiksy transakcyjne | ✅Tak |
| **MongoDB** | Dokumenty NoSQL | ✅Tak |
| **Salesforce** | Dane CRM | ❌ Nie |
| **Arkusze Google** | Arkusze kalkulacyjne | ❌ Nie |
| **Pasek** | Dane dotyczące płatności | ❌ Nie |
| **API REST** | Niestandardowe interfejsy API | ❌ Nie |
| **S3** | Przechowywanie plików | ❌ Nie |

### Złącza docelowe

#### Miejsce docelowe MinIO S3

**Przypadek użycia**: przechowuj surowe dane w jeziorze danych

**Konfiguracja:**

1. Przejdź do **Cele podróży > Nowy cel**
2. Wybierz **S3**
3. Skonfiguruj połączenie:

§§§KOD_12§§§

**Testuj połączenie** → **Skonfiguruj miejsce docelowe**

#### Miejsce docelowe PostgreSQL

**Przypadek użycia**: Załaduj przekształcone dane do celów analitycznych

**Konfiguracja:**

§§§KOD_13§§§

#### Miejsce docelowe Dremio

**Przypadek użycia**: Bezpośrednie ładowanie do Data Lakehouse

**Konfiguracja:**

§§§KOD_14§§§

---

## Połączenia

### Utwórz połączenie

Połączenie łączy źródło z miejscem docelowym.

§§§KOD_15§§§

#### Krok po kroku

1. **Przejdź do Połączenia > Nowe połączenie**

2. **Wybierz źródło**: Wybierz skonfigurowane źródło (np. PostgreSQL)

3. **Wybierz miejsce docelowe**: Wybierz miejsce docelowe (np. MinIO S3)

4. **Skonfiguruj synchronizację**:

§§§KOD_16§§§

5. **Skonfiguruj normalizację** (opcjonalnie):

§§§KOD_17§§§

6. **Test połączenia** → **Skonfiguruj połączenie**

### Tryby synchronizacji

| Moda | Opis | Przypadki użycia |
|------|------------|------------|
| **Pełne odświeżanie\| Nadpisz** | Zamień wszystkie dane | Tabele wymiarów |
| **Pełne odświeżanie\| Dołącz** | Dodaj wszystkie rekordy | Śledzenie historyczne |
| **Przyrostowy\| Dołącz** | Dodaj nowe/zaktualizowane rekordy | Tabele faktów |
| **Przyrostowy\| Oszukany** | Aktualizuj istniejące rekordy | SCD Typ 1 |

### Planowanie

**Opcje częstotliwości:**
- **Ręczny**: Wyzwalanie ręczne
- **Co godzinę**: Co godzinę
- **Codziennie**: Co 24 godziny (określ godzinę)
- **Tygodniowo**: Określone dni tygodnia
- **Cron**: harmonogram niestandardowy (np.: `0 2 * * *`)

**Przykładowe harmonogramy:**
§§§KOD_19§§§

---

## Transformacja danych

### Podstawowa normalizacja

Airbyte zawiera **Podstawową normalizację** przy użyciu dbt:

**Co ona robi:**
- Konwertuje zagnieżdżony JSON na płaskie tabele
- Utwórz tabele `_airbyte_raw_*` (surowy JSON)
- Tworzy ustandaryzowane (ustrukturyzowane) tabele
- Dodaj kolumny metadanych (§§CODE_21§§§, `_airbyte_normalized_at`)

**Przykład:**

**Surowy JSON** (`_airbyte_raw_customers`):
§§§KOD_24§§§

**Standardowe tabele:**

§§§KOD_25§§§:
§§§KOD_26§§§

§§§KOD_27§§§:
§§§KOD_28§§§

### Niestandardowe transformacje (dbt)

W przypadku zaawansowanych transformacji użyj dbt:

1. **Wyłącz normalizację Airbyte**
2. **Utwórz modele dbt** tabele referencyjne `_airbyte_raw_*`
3. **Uruchom dbt** po synchronizacji Airbyte

**Przykład modelu dbt:**
§§§KOD_30§§§

---

## Monitorowanie

### Stan synchronizacji

**Interfejs sieciowy pulpitu nawigacyjnego:**
- **Połączenia**: Zobacz wszystkie połączenia
- **Historia synchronizacji**: poprzednie zadania synchronizacji
- **Synchronizacja dzienników**: szczegółowe dzienniki dla każdego zadania

**Wskaźniki stanu:**
- 🟢 **Udało się**: Synchronizacja zakończyła się pomyślnie
- 🔴 **Niepowodzenie**: Synchronizacja nie powiodła się (sprawdź dzienniki)
- 🟡 **Bieganie**: Synchronizacja w toku
- ⚪ **Anulowano**: Synchronizacja anulowana przez użytkownika

### Dzienniki

**Zobacz dzienniki synchronizacji:**
§§§KOD_31§§§

### Metryki

**Kluczowe wskaźniki do monitorowania:**
- **Nagrania zsynchronizowane**: Liczba nagrań na synchronizację
- **Synchronizowane bajty**: Ilość przesłanych danych
- **Czas trwania synchronizacji**: Czas potrzebny na synchronizację
- **Współczynnik błędów**: Procent nieudanych synchronizacji

**Eksportuj wskaźniki:**
§§§KOD_32§§§

### Alerty

**Skonfiguruj alerty** w **Ustawienia > Powiadomienia**:

§§§KOD_33§§§

---

## Użycie API

### Uwierzytelnianie

§§§KOD_34§§§

### Typowe wywołania API

#### Lista źródeł

§§§KOD_35§§§

#### Utwórz połączenie

§§§KOD_36§§§

#### Synchronizacja wyzwalacza

§§§KOD_37§§§

#### Uzyskaj status zadania

§§§KOD_38§§§

---

## Integracja z Dremio

### Przebieg pracy

§§§KOD_39§§§

### Kroki konfiguracji

1. **Skonfiguruj Airbyte do ładowania do MinIO S3** (patrz wyżej)

2. **Dodaj źródło S3 w Dremio:**

§§§KOD_40§§§

3. **Zapytaj o dane Airbyte w Dremio:**

§§§KOD_41§§§

4. **Utwórz wirtualny zbiór danych Dremio:**

§§§KOD_42§§§

5. **Stosuj w modelach dbt:**

§§§KOD_43§§§

---

## Najlepsze praktyki

### Wydajność

1. **Jeśli to możliwe, korzystaj z synchronizacji przyrostowej**
2. ** Harmonogram synchronizuje się poza godzinami szczytu**
3. **Użyj formatu Parquet** dla lepszej kompresji
4. **Podziel duże tabele** według daty
5. **Monitoruj wykorzystanie zasobów** i dostosowuj limity

### Jakość danych

1. **Włącz sprawdzanie poprawności danych** w złączach źródłowych
2. **Użyj kluczy podstawowych**, aby wykryć duplikaty
3. **Skonfiguruj alerty** w przypadku błędów synchronizacji
4. **Monitoruj aktualność danych**
5. **Wdrażaj testy dbt** na surowych danych

### Bezpieczeństwo

1. **Użyj identyfikatorów tylko do odczytu** dla źródeł
2. **Przechowuj sekrety** w zmiennych środowiskowych
3. **Włącz SSL/TLS** dla połączeń
4. **Regularnie odnawiaj swoje identyfikatory**
5. **Okresowo sprawdzaj logi dostępu**

### Optymalizacja kosztów

1. **Użyj kompresji** (GZIP, SNAPPY)
2. **Deduplikuj dane** u źródła
3. **Archiwizuj stare dane** w chłodni
4. **Monitoruj częstotliwość synchronizacji** w porównaniu z wymaganiami
5. **Wyczyść dane nieudanej synchronizacji**

---

## Rozwiązywanie problemów

### Typowe problemy

#### Błąd synchronizacji: Przekroczono limit czasu połączenia

**Objaw:**
§§§KOD_44§§§

**Rozwiązanie:**
§§§KOD_45§§§

#### Błąd braku pamięci

**Objaw:**
§§§KOD_46§§§

**Rozwiązanie:**
§§§KOD_47§§§

#### Normalizacja nie powiodła się

**Objaw:**
§§§KOD_48§§§

**Rozwiązanie:**
§§§KOD_49§§§

#### Wolna synchronizacja

**Diagnoza:**
§§§KOD_50§§§

**Rozwiązania:**
- Zwiększ przyrostową częstotliwość synchronizacji
- Dodaj indeks do pól kursora
- Użyj CDC dla źródeł czasu rzeczywistego
- Skaluj zasoby pracowników

---

## Tematy zaawansowane

### Złącza niestandardowe

Twórz niestandardowe złącza za pomocą Airbyte CDK:

§§§KOD_51§§§

### Orkiestracja API

Zautomatyzuj Airbyte za pomocą Pythona:

§§§KOD_52§§§

---

## Zasoby

### Dokumentacja

- **Dokumentacja Airbyte**: https://docs.airbyte.com
- **Katalog złączy**: https://docs.airbyte.com/integrations
- **Odniesienie do interfejsu API**: https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html

### Wspólnota

- **Slack**: https://slack.airbyte.io
- **GitHub**: https://github.com/airbytehq/airbyte
- **Forum**: https://discuss.airbyte.io

---

## Następne kroki

Po skonfigurowaniu Airbyte:

1. **Skonfiguruj Dremio** - [Przewodnik konfiguracji Dremio](dremio-setup.md)
2. **Utwórz modele dbt** - [Przewodnik programisty dbt](dbt-development.md)
3. **Tworzenie pulpitów nawigacyjnych** — [Przewodnik po pulpitach nawigacyjnych Superset](superset-dashboards.md)
4. **Monitoruj jakość** – [Przewodnik po jakości danych](data-quality.md)

---

**Wersja przewodnika integracji Airbyte**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Obsługiwane przez**: Zespół ds. platformy danych