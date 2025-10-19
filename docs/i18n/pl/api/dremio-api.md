# Odniesienie do API Dremio

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Uwierzytelnienie](#uwierzytelnienie)
3. [API REST](#api-rest)
4. [SQL lotu strzałki](#arrow-flight-sql)
5. [ODBC/JDBC](#odbcjdbc)
6. [Klient Pythona](#client-python)
7. [Klient Java](#klient Java)
8. [Przykłady API](#dapi-przykłady)

---

## Przegląd

Dremio udostępnia kilka interfejsów API do interakcji z jeziorem danych:

| Typ API | Przypadki użycia | Port | Protokół |
|------------|------------|------|--------------|
| API REST | Zarządzanie, metadane | 9047 | HTTP/HTTPS |
| ArrowFlightSQL | Zapytania o wysokiej wydajności | 32010 | gRPC |
| ODBC | Łączność z narzędziem BI | 31010 | ODBC |
| JDBC | Aplikacje Java | 31010 | JDBC |

### Architektura API

§§§KOD_0§§§

---

## Uwierzytelnianie

### Wygeneruj token uwierzytelniający

**Punkt końcowy**: `POST /apiv2/login`

**Wniosek** :
§§§KOD_2§§§

**Odpowiedź** :
§§§KOD_3§§§

### Użyj tokena w żądaniach

§§§KOD_4§§§

### Wygaśnięcie tokena

Domyślnie tokeny wygasają po 24 godzinach. Skonfiguruj w `dremio.conf`:

§§§KOD_6§§§

---

## API REST

### Podstawowy adres URL

§§§KOD_7§§§

### Typowe nagłówki

§§§KOD_8§§§

### Zarządzanie katalogami

#### Lista pozycji katalogu

**Punkt końcowy**: `GET /catalog`

§§§KOD_10§§§

**Odpowiedź** :
§§§KOD_11§§§

#### Pobierz element katalogu według ścieżki

**Punkt końcowy**: `GET /catalog/by-path/{path}`

§§§KOD_13§§§

**Odpowiedź** :
§§§KOD_14§§§

### Wirtualne zbiory danych (VDS)

#### Utwórz wirtualny zbiór danych

**Punkt końcowy**: `POST /catalog`

§§§KOD_16§§§

**Odpowiedź** :
§§§KOD_17§§§

#### Zaktualizuj wirtualny zbiór danych

**Punkt końcowy**: `PUT /catalog/{id}`

§§§KOD_19§§§

#### Usuń zbiór danych

**Punkt końcowy**: `DELETE /catalog/{id}?tag={tag}`

§§§KOD_21§§§

### Wykonanie SQL

#### Wykonaj zapytanie SQL

**Punkt końcowy**: `POST /sql`

§§§KOD_23§§§

**Odpowiedź** :
§§§KOD_24§§§

### Zarządzanie pracą

#### Uzyskaj status zadania

**Punkt końcowy**: `GET /job/{jobId}`

§§§KOD_26§§§

**Odpowiedź** :
§§§KOD_27§§§

#### Lista ostatnich ofert pracy

**Punkt końcowy**: `GET /jobs`

§§§KOD_29§§§

#### Anuluj zadanie

**Punkt końcowy**: `POST /job/{jobId}/cancel`

§§§KOD_31§§§

###Refleksje

#### Lista refleksji

**Punkt końcowy**: `GET /reflections`

§§§KOD_33§§§

**Odpowiedź** :
§§§KOD_34§§§

#### Utwórz odbicie

**Punkt końcowy**: `POST /reflections`

§§§KOD_36§§§

### Zarządzanie źródłami

#### Dodaj źródło S3

**Punkt końcowy**: `PUT /source/{name}`

§§§KOD_38§§§

#### Odśwież metadane źródłowe

**Punkt końcowy**: `POST /source/{name}/refresh`

§§§KOD_40§§§

---

## SQL lotu strzałki

Arrow Flight SQL zapewnia wysoką wydajność wykonywania zapytań (20–50 razy szybciej niż ODBC/JDBC).

### Klient Pythona z PyArrow

#### Obiekt

§§§KOD_41§§§

#### Połączenie i zapytanie

§§§KOD_42§§§

#### Przykład: Zapytanie z parametrami

§§§KOD_43§§§

#### Przetwarzanie wsadowe

§§§KOD_44§§§

### Porównanie wydajności

§§§KOD_45§§§

---

## ODBC/JDBC

### Połączenie ODBC

#### Konfiguracja systemu Windows

1. **Pobierz sterownik ODBC**:
   §§§KOD_46§§§

2. **Skonfiguruj DSN**:
   §§§KOD_47§§§

3. **Ciąg połączenia**:
   §§§KOD_48§§§

#### Konfiguracja Linuksa

§§§KOD_49§§§

### Połączenie JDBC

#### Pobierz sterownik

§§§KOD_50§§§

#### Ciąg połączenia

§§§KOD_51§§§

#### Właściwości

§§§KOD_52§§§

---

## Klient Pythona

### Pełny przykład

§§§KOD_53§§§

---

## Klient Java

### Zależność od Mavena

§§§KOD_54§§§

### Pełny przykład

§§§KOD_55§§§

---

## Przykłady API

### Przykład 1: Automatyczne raportowanie

§§§KOD_56§§§

### Przykład 2: Eksport danych

§§§KOD_57§§§

### Przykład 3: Wykrywanie metadanych

§§§KOD_58§§§

---

## Streszczenie

To odniesienie do interfejsu API obejmowało:

- **Uwierzytelnianie**: Uwierzytelnianie oparte na tokenach za pomocą interfejsu API REST
- **REST API**: Katalog, wykonanie SQL, zadania, refleksje
- **Arrow Flight SQL**: Zapytania o wysokiej wydajności (20–50x szybsze)
- **ODBC/JDBC**: łączność z narzędziami BI
- **Klient Pythona**: Kompletna implementacja klienta
- **Klient Java**: przykłady JDBC
- **Praktyczne przykłady**: Raportowanie, eksport, odkrywanie metadanych

**Kluczowe wnioski**:
- Użyj Arrow Flight SQL, aby uzyskać dostęp do danych o wysokiej wydajności
- Użyj REST API do zarządzania i automatyzacji
- Użyj ODBC/JDBC do integracji narzędzi BI
- Zawsze używaj tokenów uwierzytelniających
- Przetwarzaj duże zapytania partiami, aby uzyskać lepszą wydajność

**Powiązana dokumentacja:**
- [Przewodnik konfiguracji Dremio](../guides/dremio-setup.md)
- [Architektura: Przepływ danych](../architektura/data-flow.md)
- [przewodnik programisty dbt](../guides/dbt-development.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r