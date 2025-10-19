# Odniesienie do API Airbyte

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Uwierzytelnienie](#uwierzytelnienie)
3. [Obszary robocze](#obszary robocze)
4. [Źródła](#źródła)
5. [Miejsca docelowe](#miejsca docelowe)
6. [Połączenia](#połączenia)
7. [Zadania i synchronizacje](#jobs-and-synchronizations)
8. [Przykłady Pythona](#python-examples)

---

## Przegląd

Interfejs API Airbyte umożliwia programowe zarządzanie potokami danych.

**Bazowy adres URL**: `http://localhost:8001/api/v1`

### Architektura API

§§§KOD_1§§§

---

## Uwierzytelnianie

Airbyte korzysta z uwierzytelniania podstawowego podczas wdrażania Dockera.

§§§KOD_2§§§

---

## Obszary robocze

### Lista obszarów roboczych

§§§KOD_3§§§

**Odpowiedź** :
§§§KOD_4§§§

### Zdobądź przestrzeń roboczą

§§§KOD_5§§§

---

## Źródła

### Lista definicji źródeł

§§§KOD_6§§§

**Odpowiedź**: Lista ponad 300 dostępnych złączy źródłowych

### Uzyskaj definicję źródła

§§§KOD_7§§§

### Utwórz źródło

#### Źródło PostgreSQL

§§§KOD_8§§§

**Odpowiedź** :
§§§KOD_9§§§

#### Źródło API

§§§KOD_10§§§

### Sprawdź połączenie źródła

§§§KOD_11§§§

**Odpowiedź** :
§§§KOD_12§§§

### Lista źródeł

§§§KOD_13§§§

---

## Miejsca docelowe

### Utwórz miejsce docelowe (S3/MinIO)

§§§KOD_14§§§

### Utwórz miejsce docelowe (PostgreSQL)

§§§KOD_15§§§

### Przetestuj połączenie docelowe

§§§KOD_16§§§

---

## Połączenia

### Odkryj diagram

§§§KOD_17§§§

**Odpowiedź** :
§§§KOD_18§§§

### Utwórz połączenie

§§§KOD_19§§§

### Pomocniczy Python

§§§KOD_20§§§

### Zaktualizuj połączenie

§§§KOD_21§§§

---

## Zadania i synchronizacje

### Uruchom synchronizację ręczną

§§§KOD_22§§§

**Odpowiedź** :
§§§KOD_23§§§

### Uzyskaj status zadania

§§§KOD_24§§§

**Odpowiedź** :
§§§KOD_25§§§

### Monitoruj postęp zadania

§§§KOD_26§§§

### Lista zadań połączenia

§§§KOD_27§§§

### Anuluj zadanie

§§§KOD_28§§§

---

## Przykłady Pythona

### Pełna konfiguracja potoku

§§§KOD_29§§§

---

## Streszczenie

To odniesienie do interfejsu API obejmowało:

- **Obszary robocze**: Uzyskaj kontekst obszaru roboczego
- **Źródła**: Ponad 300 konektorów (PostgreSQL, API, bazy danych)
- **Miejsca docelowe**: S3/MinIO, PostgreSQL, hurtownie danych
- **Połączenia**: Konfiguracja synchronizacji z harmonogramem
- **Zadania**: Uruchamiaj, monitoruj i zarządzaj synchronizacjami
- **Klient Pythona**: Przykłady pełnej automatyzacji

**Kluczowe wnioski**:
- Użyj interfejsu API REST, aby uzyskać pełną automatyzację
- Przetestuj połączenia przed utworzeniem synchronizacji
- Monitoruj status zadań dla rurociągów produkcyjnych
- Użyj przyrostowej synchronizacji z polami kursora
- Planuj synchronizacje w oparciu o potrzeby dotyczące świeżości danych

**Powiązana dokumentacja:**
- [Przewodnik po integracji Airbyte](../guides/airbyte-integration.md)
- [Architektura: Przepływ danych](../architektura/data-flow.md)
- [Przewodnik rozwiązywania problemów](../guides/troubleshooting.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r