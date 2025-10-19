# Przewodnik rozwoju dbt

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Konfiguracja projektu](#project-configuration)
3. [Modelowanie danych](#data-modeling)
4. [Struktura testowa](#platforma-testowa)
5. [Dokumentacja](#dokumentacja)
6. [Makra i pakiety](#makra i pakiety)
7. [Modele przyrostowe](#modele przyrostowe)
8. [Przebieg pracy w orkiestracji](#przebieg pracy w orkiestracji)
9. [Dobre praktyki](#dobre-praktyki)
10. [Rozwiązywanie problemów](#rozwiązywanie problemów)

---

## Przegląd

dbt (narzędzie do budowania danych) umożliwia inżynierom analitykom przekształcanie danych w hurtowni przy użyciu SQL i najlepszych praktyk inżynierii oprogramowania. Ten przewodnik obejmuje wszystko, od inicjalizacji projektu po zaawansowane techniki programistyczne.

### Co to jest dbt?

dbt przekształca surowe dane w zestawy danych gotowe do analizy, korzystając z:

- **Transformacje SQL**: Napisz instrukcje SELECT, dbt zajmie się resztą
- **Kontrola wersji**: Integracja z Git w celu współpracy
- **Testowanie**: Zintegrowane ramy testowania jakości danych
- **Dokumentacja**: Dokumentacja wygenerowana samodzielnie z pochodzeniem
- **Modułowość**: Szablony i makra wielokrotnego użytku

### Kluczowe pojęcia

§§§KOD_0§§§

### dbt przepływ pracy

§§§KOD_1§§§

---

## Konfiguracja projektu

### Zainicjuj projekt dbt

§§§KOD_2§§§

### Skonfiguruj plik profiles.yml

§§§KOD_3§§§

### Skonfiguruj plik dbt_project.yml

§§§KOD_4§§§

### Zmienne środowiskowe

§§§KOD_5§§§

### Testuj połączenie

§§§KOD_6§§§

---

## Modelowanie danych

### Modele etapowe

Modele etapowe oczyszczają i standaryzują surowe dane ze źródeł.

#### Ustaw źródła

§§§KOD_7§§§

#### Przykład modelu pomostowego

§§§KOD_8§§§

§§§KOD_9§§§

### Modele pośrednie

Modele pośrednie łączą i wzbogacają dane.

§§§KOD_10§§§

### Wykonane stoły

§§§KOD_11§§§

### Tabele wymiarów

§§§KOD_12§§§

### Martowe modele

§§§KOD_13§§§

---

## Struktura testowa

### Testy zintegrowane

§§§KOD_14§§§

### Spersonalizowane testy

§§§KOD_15§§§

§§§KOD_16§§§

### Testy ogólne

§§§KOD_17§§§

Używać:
§§§KOD_18§§§

### Uruchom testy

§§§KOD_19§§§

---

## Dokumentacja

### Dokumentacja modelu

§§§KOD_20§§§

### Dodaj opisy

§§§KOD_21§§§

### Generuj dokumentację

§§§KOD_22§§§

**Dokumentacja funkcji**:
- **Wykresy liniowe**: Wizualna reprezentacja zależności modelu
- **Szczegóły kolumny**: Opisy, typy, testy
- **Świeżość źródła**: Po załadowaniu danych
- **Widok projektu**: zawartość README
- **Szukaj**: Znajdź modele, kolumny, opisy

---

## Makra i pakiety

### Niestandardowe makra

§§§KOD_23§§§

Używać:
§§§KOD_24§§§

### Fragmenty SQL wielokrotnego użytku

§§§KOD_25§§§

### Zainstaluj pakiety

§§§KOD_26§§§

Zainstaluj pakiety:
§§§KOD_27§§§

### Użyj pakietu makr

§§§KOD_28§§§

§§§KOD_29§§§

---

## Modele przyrostowe

### Podstawowy model przyrostowy

§§§KOD_30§§§

### Strategie przyrostowe

#### 1. Dołącz strategię

§§§KOD_31§§§

#### 2. Strategia połączenia

§§§KOD_32§§§

#### 3. Usuń+Wstaw strategię

§§§KOD_33§§§

### Zakończ odświeżanie

§§§KOD_34§§§

---

## Przepływ pracy w orkiestracji

### dbt Polecenia uruchamiania

§§§KOD_35§§§

### Pełny potok

§§§KOD_36§§§

### Integracja przepływu powietrza

§§§KOD_37§§§

---

## Najlepsze praktyki

### 1. Konwencje nazewnictwa

§§§KOD_38§§§

### 2. Struktura folderów

§§§KOD_39§§§

### 3. Użyj CTE

§§§KOD_40§§§

### 4. Dodaj testy wcześniej

§§§KOD_41§§§

### 5. Dokumentuj wszystko

§§§KOD_42§§§

---

## Rozwiązywanie problemów

### Typowe problemy

#### Problem 1: Błąd kompilacji

**Błąd**: `Compilation Error: Model not found`

**Rozwiązanie**:
§§§KOD_44§§§

#### Problem 2: Zależności cykliczne

**Błąd**: `Compilation Error: Circular dependency detected`

**Rozwiązanie**:
§§§KOD_46§§§

#### Problem 3: Nieudane testy

**Błąd**: `ERROR test not_null_stg_customers_email (FAIL 15)`

**Rozwiązanie**:
§§§KOD_48§§§

#### Problem 4: Model przyrostowy nie działa

**Błąd**: Model przyrostowy jest za każdym razem tworzony od zera

**Rozwiązanie**:
§§§KOD_49§§§

---

## Streszczenie

W tym kompletnym przewodniku programistycznym dbt omówiono:

- **Konfiguracja projektu**: Inicjalizacja, konfiguracja, konfiguracja środowiska
- **Modelowanie danych**: modele etapowe, pośrednie, faktograficzne, wymiarowe i marketingowe
- **Testy ramowe**: testy zintegrowane, testy niestandardowe, testy ogólne
- **Dokumentacja**: Dokumentacja modelu, automatycznie wygenerowana dokumentacja witryny
- **Makra i pakiety**: Kod wielokrotnego użytku, dbt_utils, oczekiwania
- **Modele przyrostowe**: Strategie dołączają, łączą, usuwają i wstawiają
- **Orkiestracja przepływu pracy**: polecenia dbt, skrypty potokowe, integracja Airflow
- **Dobre praktyki**: Konwencje nazewnictwa, struktura folderów, dokumentacja
- **Rozwiązywanie problemów**: Typowe problemy i rozwiązania

Kluczowe punkty do zapamiętania:
- Użyj instrukcji SQL SELECT, dbt zarządza DDL/DML
- Testuj wcześnie i często dzięki zintegrowanej platformie testowej
- Modele dokumentów na potrzeby analiz samoobsługowych
- Używaj modeli przyrostowych w przypadku dużych tabel
- Przestrzegaj spójnych konwencji nazewnictwa
- Wykorzystaj pakiety dla typowych funkcji

**Powiązana dokumentacja:**
- [Przewodnik konfiguracji Dremio](./dremio-setup.md)
- [Przewodnik po jakości danych](./data-quality.md)
- [Architektura: Przepływ danych](../architektura/data-flow.md)
- [Poradnik pierwszych kroków](../getting-started/first-steps.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r