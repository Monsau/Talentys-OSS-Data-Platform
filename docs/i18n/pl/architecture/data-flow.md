# Architektura przepływu danych

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Przepływ danych od końca do końca](#przepływ danych od końca do końca)
3. [Warstwa przetwarzania](#warstwa przetwarzania)
4. [Warstwa przechowywania](#warstwa przechowywania)
5. [Warstwa przetwarzania](#warstwa przetwarzania)
6. [Warstwa prezentacji](#warstwa-prezentacji)
7. [Modele przepływu danych](#dataflow-models)
8. [Względy dotyczące wydajności](#względy wydajności)
9. [Monitorowanie przepływu danych](#dataflow-monitoring)
10. [Dobre praktyki](#dobre-praktyki)

---

## Przegląd

W tym dokumencie szczegółowo opisano pełną architekturę przepływu danych platformy, od początkowego przyjęcia danych do końcowego wykorzystania. Zrozumienie tych przepływów ma kluczowe znaczenie dla optymalizacji wydajności, rozwiązywania problemów i projektowania efektywnych potoków danych.

### Zasady przepływu danych

Nasza architektura kieruje się następującymi podstawowymi zasadami:

1. **Przepływ jednokierunkowy**: dane przemieszczają się w jasnym i przewidywalnym kierunku
2. **Przetwarzanie warstwowe**: Każda warstwa ma określoną odpowiedzialność
3. **Oddzielone komponenty**: Usługi komunikują się poprzez dobrze zdefiniowane interfejsy
4. **Idempotencja**: Operacje można bezpiecznie powtarzać
5. **Obserwowalność**: Każdy krok jest rejestrowany i monitorowany

### Warstwy architektury

§§§KOD_0§§§

---

## Kompleksowy przepływ danych

### Kompletna sekwencja potoku

§§§KOD_1§§§

### Kroki przepływu danych

| Krok | Składnik | Wejście | Wyjdź | Opóźnienie |
|-------|---------|--------|--------|---------|
| **Wyciąg** | Airbyte | Zewnętrzne interfejsy API/BD | Surowy JSON/CSV | 1-60 minut |
| **Ładowanie** | Warstwa pamięci | Surowe pliki | Wyselekcjonowane wiadra | <1 minuta |
| **Katalogowanie** | Dremio | Ścieżki przechowywania | Wirtualne zbiory danych | <1 minuta |
| **Transformacja** | db | Brązowe Stoły | Stoły srebrne/złote | 5-30 minut |
| **Optymalizacja** | Myśli Dremio | Surowe zapytania | Ukryte wyniki | Czas rzeczywisty |
| **Wizualizacja** | Nadzbiór | Zapytania SQL | Wykresy/Dashboardy | <5 sek |

---

## Warstwa przyjmowania

### Ekstrakcja danych Airbyte

Airbyte zarządza wszystkimi danymi pobieranymi ze źródeł zewnętrznych.

#### Przepływ połączenia źródłowego

§§§KOD_2§§§

#### Metody ekstrakcji danych

**1. Pełne odświeżenie**
§§§KOD_3§§§

**2. Synchronizacja przyrostowa**
§§§KOD_4§§§

**3. Zmień przechwytywanie danych (CDC)**
§§§KOD_5§§§

### Integracja z API Airbyte

§§§KOD_6§§§

### Wydajność ekstrakcji

| Typ źródła | Przepływ | Zalecana częstotliwość |
|----------------|------------|----------------------|
| PostgreSQL | 50-100 tys. linii/s | Co 15-60 minut |
| API REST | 1-10 tys. żądań/s | Co 5-30 minut |
| Pliki CSV | 100-500 MB/s | Codziennie |
| MongoDB | 10–50 tys. dokumentów/s | Co 15-60 minut |
| CDC MySQL | Czas rzeczywisty | Ciągłe |

---

## Warstwa przechowywania

### Pamięć MinIO S3

MinIO przechowuje surowe i przetworzone dane w strukturze hierarchicznej.

#### Organizacja wiader

§§§KOD_7§§§

#### Struktura ścieżki danych

§§§KOD_8§§§

### Strategia formatu pamięci

| Warstwa | Formatuj | Kompresja | Partycjonowanie | Powód |
|------------|-------|------------|----------------|-------|
| **Brąz** | Parkiet | Zgryźliwy | Według daty | Szybkie pisanie, dobra kompresja |
| **Srebro** | Parkiet | Zgryźliwy | Według klucza biznesowego | Efektywne zapytania |
| **Złoto** | Parkiet | ZSTD | Według okresu | Maksymalna kompresja |
| **Dzienniki** | JSON | Gzip | Według usługi/daty | Czytelne dla ludzi |

### Przechowywanie metadanych PostgreSQL

Sklepy PostgreSQL:
- Konfiguracja i status Airbyte
- Historia wykonania metadanych i dbt
- Pulpity nawigacyjne i użytkownicy Superset
- Dzienniki aplikacji i metryki

§§§KOD_9§§§

### Przechowywanie dokumentów Elasticsearch

Elasticsearch indeksuje logi i umożliwia wyszukiwanie pełnotekstowe.

§§§KOD_10§§§

---

## Warstwa przetwarzania

### Wirtualizacja danych Dremio

Dremio tworzy ujednolicony widok na wszystkie źródła przechowywania.

#### Tworzenie wirtualnego zbioru danych

§§§KOD_11§§§

#### Przyspieszenie przez odbicia

Dremio odzwierciedla wstępne obliczenia wyników zapytań w celu uzyskania natychmiastowej wydajności.

§§§KOD_12§§§

**Wpływ odbić na wydajność:**

| Typ zapytania | Bez Refleksji | Z Refleksją | Przyspieszenie |
|----------------|----------------|----------------|--------|
| WYBIERZ Prosty | 500ms | 50ms | 10x |
| Agregacje | 5s | 100ms | 50x |
| Złożone ŁĄCZENIA | lata 30. | 500ms | 60x |
| Duże skany | 120s | 2s | 60x |

### transformacje dbt

dbt przekształca surowe dane w gotowe modele biznesowe.

#### Przebieg transformacji

§§§KOD_13§§§

#### Przykład rurociągu transformacji

§§§KOD_14§§§

§§§KOD_15§§§

§§§KOD_16§§§

#### dbt Przebieg wykonania

§§§KOD_17§§§

### Możliwość śledzenia pochodzenia danych

§§§KOD_18§§§

---

## Warstwa prezentacji

### Przebieg wykonywania zapytania

§§§KOD_19§§§

### Modele dostępu do API

#### 1. Pulpity nawigacyjne Superset (BI Interactive)

§§§KOD_20§§§

#### 2. API Arrow Flight (wysoka wydajność)

§§§KOD_21§§§

#### 3. REST API (integracje zewnętrzne)

§§§KOD_22§§§

---

## Modele przepływu danych

### Model 1: Rurociąg wsadowy ETL

§§§KOD_23§§§

### Model 2: Przesyłanie strumieniowe w czasie rzeczywistym

§§§KOD_24§§§

### Wzorzec 3: Aktualizacje przyrostowe

§§§KOD_25§§§

### Model 4: Architektura Lambda (wsad + strumień)

§§§KOD_26§§§

---

## Względy wydajności

### Optymalizacja spożycia

§§§KOD_27§§§

### Optymalizacja pamięci

§§§KOD_28§§§

### Optymalizacja zapytań

§§§KOD_29§§§

### Optymalizacja przekształceń

§§§KOD_30§§§

### Testy wydajności

| Operacja | Mały zbiór danych<br/>(1 mln linii) | Średni zbiór danych<br/>(100 mln wierszy) | Duży zbiór danych<br/>(1B linii) |
|----------------------------|----------------------------|--------------------------------------|----------------------------|
| **Synchronizuj Airbyte** | 2 minuty | 30 minut | 5 godzin |
| **wykonanie dbt** | 30 sekund | 10 minut | 2 godziny |
| **Odbicie konstrukcji** | 10 sekund | 5 minut | 30 minut |
| **Zapytanie w panelu** | <100 ms | <500 ms | <2s |

---

## Monitorowanie przepływu danych

### Kluczowe wskaźniki do śledzenia

§§§KOD_31§§§

### Panel monitorowania

§§§KOD_32§§§

### Agregacja logów

§§§KOD_33§§§

---

## Najlepsze praktyki

### Projekt przepływu danych

1. **Projekt dla idempotencji**
   - Gwarancja, że ​​operacje można bezpiecznie powtórzyć
   - Używaj unikalnych kluczy do deduplikacji
   - Zaimplementuj odpowiednią obsługę błędów

2. **Wdrożenie kontroli jakości danych**
   §§§KOD_34§§§

3. **Podziel duże zbiory danych na partycje**
   §§§KOD_35§§§

4. **Użyj odpowiednich trybów synchronizacji**
   - Pełne odświeżanie: tabele małych wymiarów
   - Przyrostowe: duże tabele faktów
   - CDC: Wymagania w czasie rzeczywistym

### Regulacja wydajności

1. **Optymalizuj harmonogram synchronizacji Airbyte**
   §§§KOD_36§§§

2. **Twórz myśli strategiczne**
   §§§KOD_37§§§

3. **Optymalizuj modele dbt**
   §§§KOD_38§§§

### Wspólne rozwiązywanie problemów

| Problem | Objaw | Rozwiązanie |
|--------|---------|---------|
| **Powolna synchronizacja Airbyte** | Czasy synchronizacji | Zwiększ rozmiar partii, użyj trybu przyrostowego |
| **Brak pamięci** | Nieudane modele dbt | Materializuj stopniowo, dodaj partycjonowanie |
| **Powolne zapytania** | Pulpit limitu czasu | Utwórz odbicia, dodaj indeks |
| **Pamięć pełna** | Pisanie niepowodzeń | Wdrażaj przechowywanie danych, kompresuj stare dane |
| **Dane nieaktualne** | Stare wskaźniki | Zwiększ częstotliwość synchronizacji, sprawdź harmonogramy |

### Dobre praktyki bezpieczeństwa

1. **Szyfruj dane podczas przesyłania**
   §§§KOD_39§§§

2. **Wdrożenie kontroli dostępu**
   §§§KOD_40§§§

3. **Dostęp do danych audytowych**
   §§§KOD_41§§§

---

## Streszczenie

W tym dokumencie szczegółowo opisano pełną architekturę przepływu danych:

- **Warstwa przetwarzania**: Airbyte wyodrębnia dane z różnych źródeł poprzez pełne odświeżanie, przyrostowe lub CDC
- **Warstwa przechowywania**: MinIO, PostgreSQL i Elasticsearch przechowują surowe i przetworzone dane w zorganizowanych warstwach
- **Warstwa przetwarzania**: Dremio wirtualizuje dane, a dbt przekształca je poprzez modele staging, pośrednie i mart
- **Warstwa prezentacji**: Pulpity nawigacyjne i interfejsy API Superset zapewniają dostęp do danych gotowych do użytku biznesowego

Kluczowe punkty do zapamiętania:
- Dane przepływają jednokierunkowo przez jasno określone warstwy
- Każdy komponent ma określone obowiązki i interfejsy
- Wydajność jest optymalizowana poprzez odbicia, partycjonowanie i buforowanie
- Monitorowanie i obserwowalność są zintegrowane w każdej warstwie
- Dobre praktyki gwarantują niezawodność, wydajność i bezpieczeństwo

**Powiązana dokumentacja:**
- [Przegląd architektury](./overview.md)
- [Komponenty](./components.md)
- [Wdrożenie](./deployment.md)
- [Przewodnik po integracji Airbyte](../guides/airbyte-integration.md)
- [Przewodnik programisty dbt](../guides/dbt-development.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r