# Informacje o interfejsie API Superset

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Uwierzytelnienie](#uwierzytelnienie)
3. [Panele informacyjne](#panele informacyjne)
4. [Grafika](#grafika)
5. [Zbiory danych](#zestawy danych)
6. [Laboratorium SQL](#sql-lab)
7. [Bezpieczeństwo](#bezpieczeństwo)
8. [Przykłady Pythona](#python-examples)

---

## Przegląd

Apache Superset zapewnia interfejs API REST umożliwiający dostęp programowy.

**Bazowy adres URL**: `http://localhost:8088/api/v1`

### Architektura API

§§§KOD_1§§§

---

## Uwierzytelnianie

### Zaloguj się

**Punkt końcowy**: `POST /api/v1/security/login`

§§§KOD_3§§§

**Odpowiedź** :
§§§KOD_4§§§

### Odśwież token

**Punkt końcowy**: `POST /api/v1/security/refresh`

§§§KOD_6§§§

### Pomocnik uwierzytelniania Pythona

§§§KOD_7§§§

---

## Pulpity nawigacyjne

### Lista paneli kontrolnych

**Punkt końcowy**: `GET /api/v1/dashboard/`

§§§KOD_9§§§

**Odpowiedź** :
§§§KOD_10§§§

### Uzyskaj pulpit nawigacyjny

**Punkt końcowy**: `GET /api/v1/dashboard/{id}`

§§§KOD_12§§§

**Odpowiedź** :
§§§KOD_13§§§

### Utwórz pulpit nawigacyjny

**Punkt końcowy**: `POST /api/v1/dashboard/`

§§§KOD_15§§§

### Przykład Pythona

§§§KOD_16§§§

### Zaktualizuj panel

**Punkt końcowy**: `PUT /api/v1/dashboard/{id}`

§§§KOD_18§§§

### Usuń panel

**Punkt końcowy**: `DELETE /api/v1/dashboard/{id}`

§§§KOD_20§§§

### Eksportuj pulpit nawigacyjny

**Punkt końcowy**: `GET /api/v1/dashboard/export/`

§§§KOD_22§§§

### Zaimportuj panel

**Punkt końcowy**: `POST /api/v1/dashboard/import/`

§§§KOD_24§§§

---

## Grafika

### Lista grafik

**Punkt końcowy**: `GET /api/v1/chart/`

§§§KOD_26§§§

### Pobierz wykres

**Punkt końcowy**: `GET /api/v1/chart/{id}`

§§§KOD_28§§§

**Odpowiedź** :
§§§KOD_29§§§

### Utwórz wykres

**Punkt końcowy**: `POST /api/v1/chart/`

§§§KOD_31§§§

### Pobierz dane z wykresu

**Punkt końcowy**: `POST /api/v1/chart/data`

§§§KOD_33§§§

**Odpowiedź** :
§§§KOD_34§§§

---

## Zbiory danych

### Lista zestawów danych

**Punkt końcowy**: `GET /api/v1/dataset/`

§§§KOD_36§§§

### Pobierz zbiór danych

**Punkt końcowy**: `GET /api/v1/dataset/{id}`

§§§KOD_38§§§

**Odpowiedź** :
§§§KOD_39§§§

### Utwórz zbiór danych

**Punkt końcowy**: `POST /api/v1/dataset/`

§§§KOD_41§§§

### Dodaj obliczoną metrykę

**Punkt końcowy**: `POST /api/v1/dataset/{id}/metric`

§§§KOD_43§§§

---

## Laboratorium SQL

### Wykonaj zapytanie SQL

**Punkt końcowy**: `POST /api/v1/sqllab/execute/`

§§§KOD_45§§§

**Odpowiedź** :
§§§KOD_46§§§

### Wykonanie SQL w Pythonie

§§§KOD_47§§§

### Uzyskaj wyniki zapytania

**Punkt końcowy**: `GET /api/v1/sqllab/results/{query_id}`

§§§KOD_49§§§

---

## Bezpieczeństwo

### Token gościa

**Punkt końcowy**: `POST /api/v1/security/guest_token/`

§§§KOD_51§§§

### Lista ról

**Punkt końcowy**: `GET /api/v1/security/roles/`

§§§KOD_53§§§

### Utwórz użytkownika

**Punkt końcowy**: `POST /api/v1/security/users/`

§§§KOD_55§§§

---

## Przykłady Pythona

### Pełna automatyzacja pulpitu nawigacyjnego

§§§KOD_56§§§

### Eksport wsadowy dashboardów

§§§KOD_57§§§

---

## Streszczenie

To odniesienie do interfejsu API obejmowało:

- **Uwierzytelnianie**: Uwierzytelnianie w oparciu o tokeny JWT
- **Panele **: operacje CRUD, eksport/import
- **Wykresy**: Twórz, aktualizuj i wysyłaj zapytania do danych
- **Zestawy danych**: Zarządzanie tabelami/widokami, metrykami
- **Laboratorium SQL**: Programowe uruchamianie zapytań
- **Bezpieczeństwo**: Tokeny gości, użytkownicy, role
- **Przykłady Pythona**: Kompletne skrypty automatyzacji

**Kluczowe punkty**:
- Użyj interfejsu API do automatyzacji pulpitu nawigacyjnego
- Tokeny gościa umożliwiają bezpieczną integrację
- API SQL Lab dla zapytań ad-hoc
- Eksport/import w celu kontroli wersji
- Twórz zbiory danych z obliczonymi metrykami

**Powiązana dokumentacja**:
- [Przewodnik po pulpitach nawigacyjnych Superset](../guides/superset-dashboards.md)
- [Architektura: Przepływ danych](../architektura/data-flow.md)
- [Przewodnik rozwiązywania problemów](../guides/troubleshooting.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r