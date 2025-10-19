# Przewodnik po jakości danych

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Ramy jakości danych](#data-quality-framework)
3. [testy dbt](#dbt-testy)
4. [Integracja wielkich oczekiwań](#integracja-wielkich-oczekiwań)
5. [Zasady Walidacji Danych](#data-validation-rules)
6. [Monitorowanie i alerty](#monitoring-and-alerts)
7. [Metryki jakości danych](#data-quality-metrics)
8. [Strategie zaradcze](#remediation-strategies)
9. [Dobre praktyki](#dobre-praktyki)
10. [Studia przypadków](#studia przypadku)

---

## Przegląd

Jakość danych jest niezbędna do wiarygodnych analiz i podejmowania decyzji. W tym przewodniku omówiono kompleksowe strategie zapewniania, monitorowania i ulepszania jakości danych na całej platformie.

### Dlaczego jakość danych ma znaczenie

§§§KOD_0§§§

### Dane dotyczące jakości wymiarów

| Wymiary | Opis | Przykładowa weryfikacja |
|---------|------------|----------------------|
| **Dokładność** | Dane poprawnie reprezentują rzeczywistość | Weryfikacja formatu wiadomości e-mail |
| **Kompletność** | Nie są wymagane żadne brakujące wartości | NOT NULL sprawdza |
| **Spójność** | Dopasowanie danych pomiędzy systemami | Kluczowe stosunki zagraniczne |
| **Wiadomości** | Dane aktualne i dostępne w razie potrzeby | Kontrole świeżości |
| **Ważność** | Dane zgodne z regułami biznesowymi | Sprawdzanie zakresu wartości |
| **Wyjątkowość** | Brak duplikatów rekordów | Unikalność klucza podstawowego |

---

## Ramy jakości danych

### Jakość drzwi architektonicznych

§§§KOD_1§§§

### Wysokiej jakości pieluchy

§§§KOD_2§§§

---

## testy dbt

### Testy zintegrowane

#### Testy ogólne

§§§KOD_3§§§

#### Testy relacji

§§§KOD_4§§§

### Spersonalizowane testy

#### Pojedyncze testy

§§§KOD_5§§§

§§§KOD_6§§§

§§§KOD_7§§§

#### Ogólne makra testowe

§§§KOD_8§§§

§§§KOD_9§§§

§§§KOD_10§§§

Używać:
§§§KOD_11§§§

### Wykonanie testu

§§§KOD_12§§§

### Konfiguracja testowa

§§§KOD_13§§§

---

## Integracja „Wielkie nadzieje”.

### Obiekt

§§§KOD_14§§§

### Organizować coś

§§§KOD_15§§§

Zainstaluj pakiety:
§§§KOD_16§§§

### Testuje oczekiwania

§§§KOD_17§§§

### Spersonalizowane oczekiwania

§§§KOD_18§§§

---

## Zasady sprawdzania poprawności danych

### Walidacja logiki biznesowej

§§§KOD_19§§§

### Tabela monitorowania jakości danych

§§§KOD_20§§§

---

## Monitorowanie i alerty

### Panel wskaźników jakości

§§§KOD_21§§§

### Automatyczne alerty

§§§KOD_22§§§

### Sprawdzanie jakości danych dotyczących przepływu powietrza

§§§KOD_23§§§

---

## Wskaźniki jakości danych

### Kluczowe wskaźniki wydajności

§§§KOD_24§§§

### Analiza trendów

§§§KOD_25§§§

---

## Strategie naprawcze

### Zasady czyszczenia danych

§§§KOD_26§§§

### Proces kwarantanny

§§§KOD_27§§§

---

## Najlepsze praktyki

### 1. Testuj wcześnie i często

§§§KOD_28§§§

### 2. Użyj poziomów istotności

§§§KOD_29§§§

### 3. Zasady jakości danych dokumentu

§§§KOD_30§§§

### 4. Monitoruj trendy, a nie tylko punkty

§§§KOD_31§§§

### 5. Automatyzuj działania naprawcze, jeśli to możliwe

§§§KOD_32§§§

---

## Studia przypadków

### Studium przypadku 1: weryfikacja adresu e-mail

**Problem**: 15% e-maili klientów było nieprawidłowych (@brak, zły format)

**Rozwiązanie**:
§§§KOD_33§§§

**Remediacja**:
§§§KOD_34§§§

**Wynik**: liczba nieprawidłowych e-maili zmniejszona z 15% do 2%

### Studium przypadku 2: Błędy w obliczaniu dochodu

**Problem**: 5% zamówień miało sumę_kwota ≠ kwotę + podatek + wysyłka

**Rozwiązanie**:
§§§KOD_35§§§

**Remediacja**:
§§§KOD_36§§§

**Wynik**: Błędy obliczeniowe zredukowane do <0,1%

---

## Streszczenie

Ten kompleksowy przewodnik po jakości danych obejmował:

- **Ramy**: Wysokiej jakości drzwi, warstwy, architektura
- **testy dbt**: testy zintegrowane, testy spersonalizowane, ogólne makrotesty
- **Wielkie oczekiwania**: Zaawansowana weryfikacja z ponad 50 typami oczekiwań
- **Zasady walidacji**: Logika biznesowa, punktacja jakości, tabele monitorowania
- **Monitorowanie**: Automatyczne alerty, integracja Airflow, pulpity nawigacyjne
- **Metryki**: KPI, analiza trendów, punktacja jakości
- **Naprawa**: Zasady czyszczenia, proces kwarantanny, automatyczne poprawki
- **Dobre praktyki**: Testuj wcześnie, stosuj poziomy ważności, monitoruj trendy
- **Studia przypadków**: Prawdziwe przykłady i rozwiązania

Kluczowe punkty do zapamiętania:
- Wprowadź kontrolę jakości na każdej warstwie (Brąz → Srebro → Złoto)
- Użyj testów dbt do walidacji strukturalnej. Wielkie oczekiwania do walidacji statystycznej
- Monitoruj trendy tymczasowe, a nie tylko wskaźniki z określonego momentu
- Automatyzuj rozwiązywanie typowych i przewidywalnych problemów
- Powiadomienie o pogorszeniu jakości przed wpływem na działalność biznesową
- Dokumentowanie zasad jakości i strategii naprawczych

**Powiązana dokumentacja:**
- [Przewodnik programisty dbt](./dbt-development.md)
- [Architektura: Przepływ danych](../architektura/data-flow.md)
- [Przewodnik konfiguracji Dremio](./dremio-setup.md)
- [Przewodnik rozwiązywania problemów](./troubleshooting.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r