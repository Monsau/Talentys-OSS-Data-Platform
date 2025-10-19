# Przewodnik konfiguracji Dremio

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Konfiguracja wstępna](#initial-configuration)
3. [Konfiguracja źródła danych](#data-source-configuration)
4. [Wirtualne zbiory danych](#virtual-datasets)
5. [Myśli (zapytania o przyspieszenie)](#zapytania o przyspieszenie myśli)
6. [Bezpieczeństwo i kontrola dostępu](#bezpieczeństwo-i-kontrola dostępu)
7. [Optymalizacja wydajności](#optymalizacja-wydajności)
8. [Integracja z dbt](#integracja-z-dbt)
9. [Monitorowanie i konserwacja](#monitoring-i-konserwacja)
10. [Rozwiązywanie problemów](#rozwiązywanie problemów)

---

## Przegląd

Dremio to platforma Data Lakehouse, która zapewnia ujednolicony interfejs do wysyłania zapytań o dane do wielu źródeł. W tym przewodniku opisano wszystko, od konfiguracji początkowej po zaawansowane techniki optymalizacji.

### Co to jest Dremio?

Dremio łączy elastyczność jeziora danych z wydajnością hurtowni danych:

- **Wirtualizacja danych**: wysyłaj zapytania do danych bez ich przenoszenia i kopiowania
- **Przyspieszenie zapytań**: Automatyczne buforowanie z odbiciami
- **Analiza samoobsługowa**: Użytkownicy biznesowi mogą bezpośrednio eksplorować dane
- **Standard SQL**: Brak zastrzeżonego języka zapytań
- **Apache Arrow**: Format kolumnowy o wysokiej wydajności

### Kluczowe funkcje

| Funkcja | Opis | Zysk |
|----------------|---------|--------|
| **Myśli** | Inteligentne przyspieszenie zapytań | 10-100x szybsze zapytania |
| **Wirtualizacja danych** | Ujednolicony pogląd na źródła | Brak powielania danych |
| **Lot strzały** | Szybki transfer danych | 20-50x szybciej niż ODBC/JDBC |
| **Warstwa semantyczna** | Nazwy pól zorientowane na biznes | Analityka samoobsługowa |
| **Git dla danych** | Kontrola wersji zbioru danych | Współpraca i wycofywanie |

---

## Konfiguracja wstępna

### Warunki wstępne

Zanim zaczniesz, upewnij się, że masz:
- Uruchomiony kontener Dremio (patrz [Poradnik instalacji](../getting-started/installation.md))
- Dostęp do źródeł danych (MinIO, PostgreSQL itp.)
- Poświadczenia administratora

### Pierwsze połączenie

§§§KOD_0§§§

#### Krok 1: Uzyskaj dostęp do interfejsu Dremio

Otwórz przeglądarkę i przejdź do:
§§§KOD_1§§§

#### Krok 2: Utwórz konto administratora

Przy pierwszym uruchomieniu zostaniesz poproszony o utworzenie konta administratora:

§§§KOD_2§§§

**Nota bezpieczeństwa**: Użyj silnego hasła składającego się z co najmniej 12 znaków, w tym wielkich i małych liter, cyfr i znaków specjalnych.

#### Krok 3: Konfiguracja wstępna

§§§KOD_3§§§

### Pliki konfiguracyjne

Konfiguracją Dremio zarządza się poprzez `dremio.conf`:

§§§KOD_5§§§

### Zmienne środowiskowe

§§§KOD_6§§§

### Połączenie przez serwer proxy PostgreSQL

Dremio udostępnia interfejs zgodny z PostgreSQL na porcie 31010, umożliwiając narzędziom zgodnym z PostgreSQL łączenie się bez modyfikacji.

#### Architektura połączeń Dremio

§§§KOD_7§§§

#### Przepływ zapytań przez serwer proxy PostgreSQL

§§§KOD_8§§§

#### Konfiguracja serwera proxy

Serwer proxy PostgreSQL jest automatycznie włączany w `dremio.conf`:

§§§KOD_10§§§

#### Połączenie z psql

§§§KOD_11§§§

#### Połączenie z DBeaverem / pgAdmin

Konfiguracja połączenia:

§§§KOD_12§§§

#### Kanały połączeń

**JDBC:**
§§§KOD_13§§§

**ODBC (DSN):**
§§§KOD_14§§§

**Python (psycopg2):**
§§§KOD_15§§§

#### Kiedy używać serwera proxy PostgreSQL

§§§KOD_16§§§

| Scenariusz | Użyj serwera proxy PostgreSQL | Użyj lotu strzałą |
|------------|----------------------------|----------------------|
| **Starsze narzędzia BI** (nie obsługują lotu Arrow) | ✅Tak | ❌ Nie |
| **Migracja z PostgreSQL** (istniejący kod JDBC/ODBC) | ✅Tak | ❌ Nie |
| **Wysoka wydajność produkcji** | ❌ Nie | ✅ Tak (20-50x szybciej) |
| **Superset, dbt, nowoczesne narzędzia** | ❌ Nie | ✅Tak |
| **Szybki rozwój/testowanie** | ✅Tak (znajomy) | ⚠️Oba OK |

#### Porównanie wydajności 3 portów

§§§KOD_17§§§

**Zalecenie**: Użyj serwera proxy PostgreSQL (port 31010) dla **kompatybilności** i Arrow Flight (port 32010) dla **wydajności produkcyjnej**.

---

## Konfigurowanie źródeł danych

### Dodaj źródło MinIO S3

MinIO to podstawowa pamięć masowa typu Data Lake.

#### Krok 1: Przejdź do źródeł

§§§KOD_18§§§

#### Krok 2: Skonfiguruj połączenie S3

§§§KOD_19§§§

#### Krok 3: Przetestuj połączenie

§§§KOD_20§§§

**Oczekiwany wynik**:
§§§KOD_21§§§

### Dodaj źródło PostgreSQL

#### Organizować coś

§§§KOD_22§§§

§§§KOD_23§§§

### Dodaj źródło Elasticsearch

§§§KOD_24§§§

### Organizacja źródeł

§§§KOD_25§§§

---

## Wirtualne zbiory danych

Wirtualne zbiory danych umożliwiają tworzenie przekształconych widoków danych, które można ponownie wykorzystać.

### Utwórz wirtualne zbiory danych

#### Z edytora SQL

§§§KOD_26§§§

**Zapisz lokalizację**:
§§§KOD_27§§§

#### Z interfejsu

§§§KOD_28§§§

**Kroki**:
1. Przejdź do źródła MinIO
2. Przejdź do `datalake/bronze/customers/`
3. Kliknij przycisk „Formatuj pliki”.
4. Sprawdź wykryty wzór
5. Kliknij „Zapisz”, aby awansować do zbioru danych

### Organizacja zbiorów danych

Utwórz logiczną strukturę za pomocą spacji i folderów:

§§§KOD_30§§§

### Warstwa semantyczna

Dodaj nazwy i opisy zorientowane biznesowo:

§§§KOD_31§§§

**Dodaj opisy**:
§§§KOD_32§§§

---

## Refleksje (zapytania dotyczące przyspieszenia)

Reflections to inteligentny mechanizm buforowania Dremio, który znacznie poprawia wydajność zapytań.

### Rodzaje odbić

#### 1. Surowe refleksje

Przechowuj podzbiór kolumn w celu szybkiego pobrania:

§§§KOD_33§§§

**Przypadek użycia**:
- Pulpity nawigacyjne z zapytaniami do określonych kolumn
- Raporty z podzbiorami kolumn
- Zapytania eksploracyjne

#### 2. Refleksje na temat agregacji

Wstępnie oblicz agregacje, aby uzyskać natychmiastowe wyniki:

§§§KOD_34§§§

**Przypadek użycia**:
- Pulpity menedżerskie
- Raporty zbiorcze
- Analiza trendów

### Odbicie konfiguracji

§§§KOD_35§§§

#### Polityka dotycząca wyżywienia

§§§KOD_36§§§

**Opcje**:
- **Nigdy nie odświeżaj**: dane statyczne (np. archiwa historyczne)
- **Odśwież co [1 godzinę]**: Aktualizacje okresowe
- **Odśwież, gdy zmieni się zbiór danych**: Synchronizacja w czasie rzeczywistym

§§§KOD_37§§§

#### Polityka wygaśnięcia

§§§KOD_38§§§

### Dobre praktyki dotyczące refleksji

#### 1. Zacznij od zapytań o dużej wartości

Zidentyfikuj powolne zapytania z historii:

§§§KOD_39§§§

#### 2. Twórz ukierunkowane refleksje

§§§KOD_40§§§

#### 3. Monitoruj odbicie zasięgu

§§§KOD_41§§§

### Przemyślenia dotyczące wydajności

| Rozmiar zbioru danych | Wpisz zapytanie | Bez Refleksji | Z Refleksją | Przyspieszenie |
|----------------|------------|----------------|----------------|------------|
| 1M linii | WYBIERZ Prosty | 500ms | 50ms | 10x |
| 10M linii | Agregacja | 15s | 200ms | 75x |
| 100M linii | Złożone DOŁĄCZ | 2 minuty | 1s | 120x |
| Linie 1B | GRUPUJ WG | 10 minut | 5s | 120x |

---

## Bezpieczeństwo i kontrola dostępu

### Zarządzanie użytkownikami

#### Utwórz użytkowników

§§§KOD_42§§§

§§§KOD_43§§§

#### Role użytkowników

| Rola | Uprawnienia | Przypadki użycia |
|------|------------|------------|
| **Administrator** | Pełny dostęp | Administracja systemem |
| **Użytkownik** | Zapytania, tworzenie osobistych zbiorów danych | Analitycy, badacze danych |
| **Ograniczona liczba użytkowników** | Tylko zapytanie, a nie tworzenie zbioru danych | Użytkownicy biznesowi, widzowie |

### Uprawnienia do przestrzeni

§§§KOD_44§§§

**Typy uprawnień**:
- **Widok**: umożliwia przeglądanie zbiorów danych i wysyłanie do nich zapytań
- **Modyfikuj**: Może edytować definicje zestawu danych
- **Zarządzaj dotacjami**: może zarządzać uprawnieniami
- **Właściciel**: Pełna kontrola

**Przykład**:
§§§KOD_45§§§

### Bezpieczeństwo na poziomie linii

Zaimplementuj filtrowanie na poziomie wiersza:

§§§KOD_46§§§

### Kolumna Poziom zabezpieczeń

Ukryj wrażliwe kolumny:

§§§KOD_47§§§

### Integracja OAuth

§§§KOD_48§§§

---

## Optymalizacja wydajności

### Techniki optymalizacji zapytań

#### 1. Czyszczenie partycji

§§§KOD_49§§§

#### 2. Przycinanie kolumn

§§§KOD_50§§§

#### 3. Przesunięcie predykatu

§§§KOD_51§§§

#### 4. Dołącz do Optymalizacji

§§§KOD_52§§§

### Konfiguracja pamięci

§§§KOD_53§§§

### Rozmiar klastra

| Typ obciążenia | Koordynator | Wykonawcy | Razem klaster |
|------------|---------|------------|--------------|
| **Mały** | 4 procesor, 16 GB | 2x (8 procesorów, 32 GB) | 20 procesorów, 80 GB |
| **Średni** | 8 procesorów, 32 GB | 4x (16 procesorów, 64 GB) | 72 procesor, 288 GB |
| **Duży** | 16 procesorów, 64 GB | 8x (32 procesory, 128 GB) | 272 procesor, 1088 GB |

### Monitorowanie wydajności

§§§KOD_54§§§

---

## Integracja z dbt

### Dremio jako cel dbt

Skonfiguruj `profiles.yml`:

§§§KOD_56§§§

### modele dbt na Dremio

§§§KOD_57§§§

### Wykorzystaj refleksje w dbt

§§§KOD_58§§§

---

## Monitorowanie i konserwacja

### Kluczowe wskaźniki do monitorowania

§§§KOD_59§§§

### Zadania konserwacyjne

#### 1. Odśwież myśli

§§§KOD_60§§§

#### 2. Wyczyść stare dane

§§§KOD_61§§§

#### 3. Aktualizuj statystyki

§§§KOD_62§§§

---

## Rozwiązywanie problemów

### Typowe problemy

#### Problem 1: Niska wydajność zapytań

**Symptomy**: Zapytania trwające minuty zamiast sekund

**Diagnoza**:
§§§KOD_63§§§

**Rozwiązania**:
1. Stwórz odpowiednie myśli
2. Dodaj filtry czyszczenia partycji
3. Zwiększ pamięć executora
4. Włącz kolejkowanie

#### Problem 2: Refleksja nie buduje

**Objawy**: Odbicie utknęło w stanie „ODŚWIEŻAJĄCYM”.

**Diagnoza**:
§§§KOD_64§§§

**Rozwiązania**:
1. Sprawdź dane źródłowe pod kątem zmian w schemacie
2. Sprawdź wystarczającą ilość miejsca na dysku
3. Zwiększ odbicie konstrukcji limitu czasu
4. Wyłącz i włącz ponownie odbicie

#### Problem 3: Przekroczono limit czasu połączenia

**Objawy**: Błędy „Przekroczono limit czasu połączenia” podczas sprawdzania źródeł

**Rozwiązania**:
§§§KOD_65§§§

#### Problem 4: Brak pamięci

**Symptomy**: „OutOfMemoryError” w logach

**Rozwiązania**:
§§§KOD_66§§§

### Zapytania diagnostyczne

§§§KOD_67§§§

---

## Streszczenie

Ten obszerny przewodnik obejmuje:

- **Konfiguracja wstępna**: Pierwsza konfiguracja, utworzenie konta administratora, pliki konfiguracyjne
- **Źródła danych**: połączenie MinIO, PostgreSQL i Elasticsearch
- **Wirtualne zbiory danych**: Tworzenie przekształconych widoków wielokrotnego użytku z warstwą semantyczną
- **Refleksje**: Surowe odbicia i agregacja w celu przyspieszenia zapytań 10–100x
- **Bezpieczeństwo**: zarządzanie użytkownikami, uprawnienia do przestrzeni, bezpieczeństwo na poziomie wierszy/kolumn
- **Wydajność**: Optymalizacja zapytań, konfiguracja pamięci, rozmiar klastra
- **Integracja z dbt**: Używaj Dremio jako celu dbt z zarządzaniem odbiciami
- **Monitorowanie**: Kluczowe wskaźniki, zadania konserwacyjne, żądania diagnostyczne
- **Rozwiązywanie problemów**: Typowe problemy i rozwiązania

Kluczowe punkty do zapamiętania:
- Dremio zapewnia ujednolicony interfejs SQL dla wszystkich źródeł danych
- Niezbędne przemyślenia dotyczące wydajności produkcyjnej
- Właściwa konfiguracja zabezpieczeń umożliwia samoobsługową analizę
- Regularne monitorowanie zapewnia optymalną wydajność

**Powiązana dokumentacja:**
- [Komponenty architektury](../architecture/components.md)
- [Przepływ danych](../architecture/data-flow.md)
- [Przewodnik programisty dbt](./dbt-development.md)
- [Integracja Airbyte](./airbyte-integration.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r