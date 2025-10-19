# Odniesienie do API dbt

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Polecenia CLI](#polecenia-cli)
3. [API Pythona](#api-python)
4. [Pliki metadanych](#metadata-files)
5. [dbt Cloud API](#api-dbt-cloud)
6. [Makra niestandardowe](#custom-macros)

---

## Przegląd

dbt udostępnia trzy główne interfejsy:

| Interfejs | Przypadki użycia | Dostęp |
|--------------|------------|-------|
| Interfejs wiersza polecenia | Rozwój, CI/CD | Linia poleceń |
| API Pythona | Wykonanie programowe | Kod Pythona |
| dbt Cloud API | Usługa zarządzana | API REST |
| Metadane | Introspekcja | Pliki JSON |

---

## Polecenia CLI

### Główne polecenia

#### Uruchom dbt

Uruchom modele, aby przekształcić dane.

§§§KOD_0§§§

**Opcje**:
§§§KOD_1§§§

#### test dbt

Przeprowadź testy jakości danych.

§§§KOD_2§§§

#### kompilacja dbt

Wspólnie uruchamiaj modele, testy, nasiona i migawki.

§§§KOD_3§§§

#### Dokumentacja dbt

Generowanie i obsługa dokumentacji.

§§§KOD_4§§§

### Polecenia programistyczne

#### dbt się kompiluje

Kompiluj modele do SQL bez ich uruchamiania.

§§§KOD_5§§§

#### debugowanie dbt

Przetestuj połączenie i konfigurację bazy danych.

§§§KOD_6§§§

#### dbt ls (lista)

Lista zasobów projektu.

§§§KOD_7§§§

### Polecenia dotyczące danych

#### materiał siewny dbt

Załaduj pliki CSV do bazy danych.

§§§KOD_8§§§

#### migawka dbt

Utwórz wolno zmieniające się tabele wymiarów typu 2.

§§§KOD_9§§§

### Polecenia narzędziowe

#### dbt czyste

Usuń skompilowane pliki i artefakty.

§§§KOD_10§§§

#### dbt deps

Zainstaluj pakiety z pliku package.yml.

§§§KOD_11§§§

#### dbt inicj

Zainicjuj nowy projekt dbt.

§§§KOD_12§§§

---

## API Pythona

### Wykonanie podstawowe

§§§KOD_13§§§

### Kompletne opakowanie Pythona

§§§KOD_14§§§

### Integracja przepływu powietrza

§§§KOD_15§§§

---

## Pliki metadanych

### manifest.json

Zawiera pełne metadane projektu.

**Lokalizacja**: `target/manifest.json`

§§§KOD_17§§§

### run_results.json

Zawiera wyniki ostatniego wykonania.

**Lokalizacja**: `target/run_results.json`

§§§KOD_19§§§

### katalog.json

Zawiera informacje o schemacie bazy danych.

**Lokalizacja**: `target/catalog.json`

§§§KOD_21§§§

---

## dbt Cloud API

Jeśli korzystasz z dbt Cloud (nie dotyczy instalacji lokalnej), interfejs API jest dostępny.

**Bazowy adres URL**: `https://cloud.getdbt.com/api/v2`

### Uwierzytelnianie

§§§KOD_23§§§

### Uruchom zadanie

§§§KOD_24§§§

---

## Niestandardowe makra

### Utwórz niestandardowe makro

**Plik**: `macros/custom_tests.sql`

§§§KOD_26§§§

### Użyj w testach

**Plik**: `models/staging/schema.yml`

§§§KOD_28§§§

### Zaawansowane makro z argumentami

§§§KOD_29§§§

### Wywołaj makro

§§§KOD_30§§§

---

## Streszczenie

To odniesienie do interfejsu API obejmowało:

- **Polecenia CLI**: Pełna dokumentacja dla wszystkich poleceń dbt
- **Python API**: Programowe wykonanie z opakowaniem Pythona
- **Pliki metadanych**: manifest.json, run_results.json, katalog.json
- **dbt Cloud API**: Uruchamianie zadań (w przypadku korzystania z dbt Cloud)
- **Niestandardowe makra**: Twórz i korzystaj z niestandardowych funkcji

**Kluczowe punkty**:
- Używaj interfejsu CLI do programowania i pracy interaktywnej
- Użyj interfejsu API języka Python do automatyzacji i orkiestracji
- Analizuj pliki metadanych pod kątem introspekcji
- Twórz niestandardowe makra dla logiki wielokrotnego użytku
- Integracja z Airflow w celu planowania produkcji

**Powiązana dokumentacja**:
- [przewodnik programisty dbt](../guides/dbt-development.md)
- [Przewodnik po jakości danych](../guides/data-quality.md)
- [Architektura: Przepływ danych](../architektura/data-flow.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r