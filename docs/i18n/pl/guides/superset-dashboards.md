# Przewodnik po pulpitach nawigacyjnych Apache Superset

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Konfiguracja wstępna](#initial-configuration)
3. [Połączenie ze źródłami danych](#data-sources-connection)
4. [Tworzenie grafiki](#tworzenie grafiki)
5. [Konstrukcja deski rozdzielczej](#konstrukcja deski rozdzielczej)
6. [Funkcje zaawansowane](#advanced-features)
7. [Bezpieczeństwo i uprawnienia](#bezpieczeństwo i uprawnienia)
8. [Optymalizacja wydajności](#optymalizacja-wydajności)
9. [Integracja i udostępnianie](#integracja i udostępnianie)
10. [Dobre praktyki](#dobre-praktyki)

---

## Przegląd

Apache Superset to nowoczesna, gotowa do zastosowania w przedsiębiorstwach aplikacja internetowa do analityki biznesowej, która umożliwia użytkownikom eksplorowanie i wizualizację danych za pomocą intuicyjnych pulpitów nawigacyjnych i wykresów.

### Kluczowe funkcje

| Funkcja | Opis | Zysk |
|----------------|---------|--------|
| **IDE SQL** | Interaktywny edytor SQL z funkcją automatycznego uzupełniania | Analiza doraźna |
| **Bogate wizualizacje** | Ponad 50 typów wykresów | Różne reprezentacje danych |
| **Kreator pulpitu nawigacyjnego** | Przeciągnij i upuść interfejs | Łatwe tworzenie dashboardów |
| **Buforowanie** | Zapytania o wyniki w pamięci podręcznej | Szybki czas ładowania |
| **Bezpieczeństwo** | Bezpieczeństwo na poziomie wiersza, dostęp oparty na rolach | Zarządzanie danymi |
| **Alerty** | Automatyczne powiadomienia e-mail/Slack | Proaktywne monitorowanie |

### Integracja architektury

§§§KOD_0§§§

---

## Konfiguracja wstępna

### Pierwsze połączenie

Uzyskaj dostęp do Supersetu na `http://localhost:8088`:

§§§KOD_2§§§

**Nota bezpieczeństwa**: Zmień domyślne hasło natychmiast po pierwszym logowaniu.

### Konfiguracja wstępna

§§§KOD_3§§§

### Plik konfiguracyjny

§§§KOD_4§§§

---

## Źródła danych połączenia

### Zaloguj się do Dremio

#### Krok 1: Zainstaluj sterownik bazy danych Dremio

§§§KOD_5§§§

#### Krok 2: Dodaj bazę danych Dremio

§§§KOD_6§§§

**Konfiguracja**:
§§§KOD_7§§§

#### Krok 3: Przetestuj połączenie

§§§KOD_8§§§

### Łączenie z PostgreSQL

§§§KOD_9§§§

### Łączenie z Elasticsearch

§§§KOD_10§§§

---

## Tworzenie grafiki

### Proces tworzenia grafiki

§§§KOD_11§§§

### Typ grafiki wyboru

| Typ graficzny | Najlepsze dla | Przykład zastosowania |
|----------------|--------------|--------------------------------------|
| **Wykres liniowy** | Trendy czasowe | Dzienny trend dochodów |
| **Wykres słupkowy** | Porównania | Przychody według kategorii produktów |
| **Wykres sektorów** | Udział ogółem | Udział w rynku według regionu |
| **Tabela** | Dane szczegółowe | Lista klientów z metrykami |
| **Duża liczba** | Pojedyncza metryka | Całkowity dochód od początku roku |
| **Karta grzewcza** | Wykrywanie wzorców | Sprzedaż na dzień/godzinę |
| **Chmura punktów** | Korelacje | Wartość klienta a częstotliwość |
| **Schemat Sankeya** | Analiza przepływu | Podróż użytkownika |

### Przykład: wykres liniowy (trend dochodów)

#### Krok 1: Utwórz zbiór danych

§§§KOD_12§§§

**Konfiguracja**:
- **Baza danych**: Dremio
- **Schemat**: Produkcja.Marts
- **Tabela**: mart_daily_revenue

#### Krok 2: Utwórz wykres

§§§KOD_13§§§

**Parametry**:
§§§KOD_14§§§

**Wygenerowano SQL**:
§§§KOD_15§§§

### Przykład: wykres słupkowy (najważniejsi klienci)

§§§KOD_16§§§

### Przykład: tabela przestawna

§§§KOD_17§§§

### Przykład: duża liczba z trendem

§§§KOD_18§§§

---

## Panele konstrukcyjne

### Proces tworzenia panelu kontrolnego

§§§KOD_19§§§

### Krok 1: Utwórz panel kontrolny

§§§KOD_20§§§

**Ustawienia panelu**:
§§§KOD_21§§§

### Krok 2: Dodaj grafikę

Przeciągnij i upuść grafiki z lewego panelu lub utwórz nowe:

§§§KOD_22§§§

### Krok 3: Zaprojektuj układ

**System sieciowy**:
- szerokość 12 kolumn
- Grafika przyciągana jest do siatki
- Przesuń, aby zmienić rozmiar i położenie

**Przykładowy układ**:
§§§KOD_23§§§

### Krok 4: Dodaj filtry panelu kontrolnego

§§§KOD_24§§§

**Filtr zakresu dat**:
§§§KOD_25§§§

**Filtr kategorii**:
§§§KOD_26§§§

**Filtr cyfrowy**:
§§§KOD_27§§§

### Krok 5: Filtrowanie krzyżowe

Włącz filtrowanie krzyżowe panelu kontrolnego:

§§§KOD_28§§§

**Konfiguracja**:
§§§KOD_29§§§

**Doświadczenie użytkownika**:
- Kliknij pasek → przefiltruj cały pulpit nawigacyjny
- Kliknij udział w sektorze → aktualizuje powiązane grafiki
- Wyczyść filtr → resetuje do widoku domyślnego

---

## Zaawansowane funkcje

### Laboratorium SQL

Interaktywny edytor SQL do zapytań ad hoc.

#### Wykonaj zapytanie

§§§KOD_30§§§

**Cechy**:
- Automatyczne uzupełnianie tabel i kolumn
- Zapytaj o historię
- Wiele zakładek
- Eksportuj wyniki (CSV, JSON)
- Zapisz zapytanie do ponownego użycia

#### Utwórz tabelę z zapytania (CTAS)

§§§KOD_31§§§

### Szablony Jinja

Dynamiczny SQL z szablonami Jinja2:

§§§KOD_32§§§

**Zmienne szablonu**:
- `{{ from_dttm }}` - Zakres dat rozpoczęcia
- `{{ to_dttm }}` - Koniec zakresu dat
- `{{ filter_values('column') }}` - Wybrane wartości filtrów
- `{{ current_username }}` - Użytkownik zalogowany

### Alerty i raporty

#### Utwórz alert

§§§KOD_37§§§

**Konfiguracja**:
§§§KOD_38§§§

#### Utwórz raport

§§§KOD_39§§§

### Niestandardowe wtyczki wizualizacyjne

Twórz niestandardowe typy grafiki:

§§§KOD_40§§§

Zbuduj i zainstaluj:
§§§KOD_41§§§

---

## Bezpieczeństwo i uprawnienia

### Kontrola dostępu oparta na rolach (RBAC)

§§§KOD_42§§§

### Zintegrowane role

| Rola | Uprawnienia | Przypadki użycia |
|------|------------|------------|
| **Administrator** | Wszystkie uprawnienia | Administratorzy systemu |
| **Alfa** | Twórz, edytuj, usuwaj dashboardy/wykresy | Analitycy danych |
| **Gamma** | Wyświetlaj dashboardy, uruchamiaj zapytania SQL Lab | Użytkownicy biznesowi |
| **sql_lab** | Tylko dostęp do laboratorium SQL | Naukowcy zajmujący się danymi |
| **Publiczne** | Wyświetl tylko publiczne pulpity nawigacyjne | Anonimowi użytkownicy |

### Utwórz rolę niestandardową

§§§KOD_43§§§

**Przykład: rola analityka marketingowego**
§§§KOD_44§§§

### Bezpieczeństwo na poziomie linii (RLS)

Ogranicz dane według atrybutów użytkownika:

§§§KOD_45§§§

**Przykład: RLS oparty na regionie**
§§§KOD_46§§§

**Przykład: RLS oparty na kliencie**
§§§KOD_47§§§

### Bezpieczeństwo połączenia z bazą danych

§§§KOD_48§§§

---

## Optymalizacja wydajności

### Buforowanie zapytań

§§§KOD_49§§§

**Strategia pamięci podręcznej**:
§§§KOD_50§§§

### Żądania asynchroniczne

Włącz wykonywanie zapytań asynchronicznych dla długich zapytań:

§§§KOD_51§§§

### Optymalizacja zapytań do bazy danych

§§§KOD_52§§§

### Optymalizacja ładowania panelu

§§§KOD_53§§§

### Monitorowanie wydajności

§§§KOD_54§§§

---

## Integracja i udostępnianie

### Publiczne pulpity nawigacyjne

Udostępnij pulpity nawigacyjne bez połączenia:

§§§KOD_55§§§

**Publiczny adres URL**:
§§§KOD_56§§§

### Integracja iframe

Integruj dashboardy z aplikacjami zewnętrznymi:

§§§KOD_57§§§

**Ustawienia integracji**:
- `standalone=1` - Ukryj nawigację
- `show_filters=0` - Ukryj panel filtra
- `show_title=0` - Ukryj tytuł pulpitu nawigacyjnego

### Uwierzytelnianie tokenem gościa

Programowy dostęp do zintegrowanych dashboardów:

§§§KOD_61§§§

### Eksportuj panele kontrolne

§§§KOD_62§§§

---

## Najlepsze praktyki

### Projekt deski rozdzielczej

1. **Hierarchia układu**
   §§§KOD_63§§§

2. **Stałość koloru**
   - Używaj spójnego schematu kolorów na wszystkich pulpitach nawigacyjnych
   - Zielony dla wskaźników dodatnich, czerwony dla wskaźników ujemnych
   - Kolory marki dla kategorii

3. **Wydajność**
   - Ogranicz grafikę na pulpit nawigacyjny (< 15)
   - Stosuj odpowiednie poziomy agregacji
   - Włącz pamięć podręczną dla danych statycznych
   - Ustaw rozsądne limity linii

4. **Interaktywność**
   - Dodaj znaczące filtry
   - Włącz filtrowanie krzyżowe w celu eksploracji
   - Zapewnij możliwość drążenia szczegółów

### Wybór grafiki

| Typ danych | Polecane wykresy | Unikaj |
|-------------|----------------------------|------------|
| **Szereg czasowy** | Liniowy, Obszary | Sektory, Pierścień |
| **Porównanie** | Pręty, kolumny | Liniowy (kilka punktów danych) |
| **Udział w sumie** | Sektory, Pierścień, Mapa drzewa | Bary (także kategorie) |
| **Dystrybucja** | Histogram, wykres pudełkowy | Sektory |
| **Korelacja** | Punkty chmur, bąbelki | Bary |
| **Geograficzne** | Mapa, Choropleth | Tabela |

### Optymalizacja zapytań

§§§KOD_64§§§

### Bezpieczeństwo

1. **Kontrola dostępu**
   - Użyj RBAC do zarządzania użytkownikami
   - Zaimplementuj RLS do izolacji danych
   - Ogranicz połączenia z bazą danych według roli

2. **Zarządzanie danymi**
   - Właściwość zbiorów danych dokumentów
   - Zdefiniuj harmonogramy odświeżania danych
   - Monitoruj wydajność zapytań

3. **Zgodność**
   - Ukryj PII w wizualizacjach
   - Dostęp do panelu kontrolnego
   - Wdrożyć zasady przechowywania danych

---

## Streszczenie

W tym obszernym przewodniku po Superset omówiono:

- **Konfiguracja**: Instalacja, konfiguracja, połączenia z bazą danych
- **Grafika**: Ponad 50 typów grafiki, konfiguracja, generowanie SQL
- **Panele **: Projekt układu, filtry, filtrowanie krzyżowe
- **Zaawansowane funkcje**: laboratorium SQL, szablony Jinja, alerty, niestandardowe wtyczki
- **Bezpieczeństwo**: RBAC, RLS, bezpieczeństwo połączenia z bazą danych
- **Wydajność**: Buforowanie, zapytania asynchroniczne, optymalizacja zapytań
- **Integracja**: Publiczne dashboardy, integracja iframe, tokeny gości
- **Dobre Praktyki**: Zasady projektowania, dobór grafiki, bezpieczeństwo

Kluczowe punkty do zapamiętania:
- Superset łączy się z Dremio w celu uzyskania wysokiej wydajności analiz
- Bogata biblioteka wizualizacji obsługuje różne przypadki użycia
- Wbudowane buforowanie i zapytania asynchroniczne zapewniają szybkie pulpity nawigacyjne
- RBAC i RLS umożliwiają bezpieczną analizę samoobsługową
- Możliwości integracyjne umożliwiają integrację z aplikacjami zewnętrznymi

**Powiązana dokumentacja:**
- [Przewodnik konfiguracji Dremio](./dremio-setup.md)
- [Architektura: Przepływ danych](../architektura/data-flow.md)
- [Poradnik pierwszych kroków](../getting-started/first-steps.md)
- [Przewodnik po jakości danych](./data-quality.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r