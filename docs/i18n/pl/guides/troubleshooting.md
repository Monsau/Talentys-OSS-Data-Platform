# Przewodnik rozwiązywania problemów

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Ogólne podejście do rozwiązywania problemów](#general-troubleshooting-approach)
3. [Problemy z Airbyte](#airbyte-problems)
4. [Problemy z Dremio](#dremio-problemy)
5. [problemy z dbt](#dbt-problemy)
6. [Problemy z superzbiorem](#problemy z superzbiorem)
7. [Problemy z PostgreSQL](#postgresql-problems)
8. [Problemy MinIO](#minio-problemy)
9. [Problemy z Elasticsearch](#elasticsearch-issues)
10. [Sieć i łączność](#sieć i łączność)
11. [Problemy z wydajnością](#problemy z wydajnością)
12. [Problemy z jakością danych](#data-quality-issues)

---

## Przegląd

Ten kompleksowy przewodnik rozwiązywania problemów pomaga diagnozować i rozwiązywać typowe problemy we wszystkich komponentach platformy. Problemy są uporządkowane według komponentów i zawierają jasne objawy, diagnostykę i rozwiązania.

### Metodologia rozwiązywania problemów

§§§KOD_0§§§

---

## Ogólne podejście do rozwiązywania problemów

### Krok 1: Sprawdź stan usług

§§§KOD_1§§§

### Krok 2: Sprawdź logi

§§§KOD_2§§§

### Krok 3: Sprawdź łączność sieciową

§§§KOD_3§§§

### Krok 4: Sprawdź wykorzystanie zasobów

§§§KOD_4§§§

### Typowe szybkie poprawki

§§§KOD_5§§§

---

## Problemy z Airbyte

### Problem 1: Nie ładuje się interfejs Airbyte

**Objawy**:
- Przeglądarka wyświetla komunikat „Nie można połączyć” lub przekroczono limit czasu
- URL: `http://localhost:8000` nie odpowiada

**Diagnoza**:
§§§KOD_7§§§

**Rozwiązania**:

1. **Sprawdź, czy port nie jest używany**:
   §§§KOD_8§§§

2. **Uruchom ponownie kontenery Airbyte**:
   §§§KOD_9§§§

3. **Sprawdź, czy serwer jest zdrowy**:
   §§§KOD_10§§§

### Problem 2: Synchronizacja nie powiodła się z powodu „Przekroczenia limitu czasu połączenia”

**Objawy**:
- Zadanie synchronizacji natychmiast kończy się niepowodzeniem lub zawiesza się
- Błąd: „Upłynął limit czasu połączenia” lub „Nie można połączyć się ze źródłem”

**Diagnoza**:
§§§KOD_11§§§

**Rozwiązania**:

1. **Sprawdź identyfikatory źródła**:
   §§§KOD_12§§§

2. **Wydłuż limit czasu**:
   §§§KOD_13§§§

3. **Sprawdź sieć**:
   §§§KOD_14§§§

### Problem 3: Brak pamięci podczas synchronizacji

**Objawy**:
— Proces roboczy kontenera ulega awarii podczas dużych synchronizacji
- Błąd: „OutOfMemoryError” lub „Przestrzeń sterty Java”

**Diagnoza**:
§§§KOD_15§§§

**Rozwiązania**:

1. **Zwiększ pamięć pracowników**:
   §§§KOD_16§§§

2. **Zmniejsz wielkość partii**:
   §§§KOD_17§§§

3. **Użyj synchronizacji przyrostowej**:
   §§§KOD_18§§§

### Problem 4: Dane nie pojawiają się w miejscu docelowym

**Objawy**:
- Synchronizacja zakończyła się pomyślnie
- Żadnych błędów w logach
- Dane nie znajdują się w MinIO/miejscu docelowym

**Diagnoza**:
§§§KOD_19§§§

**Rozwiązania**:

1. **Sprawdź konfigurację docelową**:
   §§§KOD_20§§§

2. **Sprawdź normalizację**:
   §§§KOD_21§§§

3. **Weryfikacja ręczna**:
   §§§KOD_22§§§

---

## Problemy z Dremio

### Problem 1: Nie można połączyć się z interfejsem Dremio

**Objawy**:
- Przeglądarka pokazuje błąd połączenia w `http://localhost:9047`

**Diagnoza**:
§§§KOD_24§§§

**Rozwiązania**:

1. **Poczekaj na całkowite uruchomienie** (może to zająć 2-3 minuty):
   §§§KOD_25§§§

2. **Zwiększ pamięć**:
   §§§KOD_26§§§

3. **Wyczyść dane Dremio** (⚠️ resetuje konfigurację):
   §§§KOD_27§§§

### Problem 2: „Źródło offline” dla MinIO

**Objawy**:
- Źródło MinIO wyświetla czerwony wskaźnik „Offline”.
- Błąd: „Nie można połączyć się ze źródłem”

**Diagnoza**:
§§§KOD_28§§§

**Rozwiązania**:

1. **Sprawdź punkt końcowy MinIO**:
   §§§KOD_29§§§

2. **Sprawdź dane uwierzytelniające**:
   §§§KOD_30§§§

3. **Odśwież metadane**:
   §§§KOD_31§§§

### Problem 3: Niska wydajność zapytań

**Objawy**:
- Zapytania zajmują ponad 10 sekund
- Panele ładują się powoli

**Diagnoza**:
§§§KOD_32§§§

**Rozwiązania**:

1. **Twórz odbicia**:
   §§§KOD_33§§§

2. **Dodaj filtry partycji**:
   §§§KOD_34§§§

3. **Zwiększ pamięć modułu wykonawczego**:
   §§§KOD_35§§§

### Problem 4: Refleksja nie buduje

**Objawy**:
- Odbicie pozostaje w stanie „ODŚWIEŻAJĄCYM”.
- Nigdy się nie kończy

**Diagnoza**:
§§§KOD_36§§§

**Rozwiązania**:

1. **Wyłącz i włącz ponownie**:
   §§§KOD_37§§§

2. **Sprawdź dane źródłowe**:
   §§§KOD_38§§§

3. **Wydłuż limit czasu**:
   §§§KOD_39§§§

---

## problemy z dbt

### Problem 1: „Błąd połączenia” podczas uruchamiania dbt

**Objawy**:
- `dbt debug` nie powiodło się
- Błąd: „Nie można połączyć się z Dremio”

**Diagnoza**:
§§§KOD_41§§§

**Rozwiązania**:

1. **Sprawdź plik profiles.yml**:
   §§§KOD_42§§§

2. **Przetestuj łączność Dremio**:
   §§§KOD_43§§§

3. **Zainstaluj adapter Dremio**:
   §§§KOD_44§§§

### Problem 2: Nie udało się zbudować modelu

**Objawy**:
- `dbt run` nie działa w przypadku konkretnego modelu
- Błąd kompilacji lub wykonania SQL

**Diagnoza**:
§§§KOD_46§§§

**Rozwiązania**:

1. **Sprawdź składnię modelu**:
   §§§KOD_47§§§

2. **Najpierw przetestuj w środowisku SQL IDE**:
   §§§KOD_48§§§

3. **Sprawdź zależności**:
   §§§KOD_49§§§

### Problem 3: Testy kończą się niepowodzeniem

**Objawy**:
- `dbt test` zgłasza awarie
— Wykryto problemy z jakością danych

**Diagnoza**:
§§§KOD_51§§§

**Rozwiązania**:

1. **Popraw dane źródłowe**:
   §§§KOD_52§§§

2. **Ustaw próg testowy**:
   §§§KOD_53§§§

3. **Zbadaj pierwotną przyczynę**:
   §§§KOD_54§§§

### Problem 4: Model przyrostowy nie działa

**Objawy**:
- Model przyrostowy jest całkowicie przebudowywany przy każdym uruchomieniu
- Brak zachowań przyrostowych

**Diagnoza**:
§§§KOD_55§§§

**Rozwiązania**:

1. **Dodaj wymagania systemowe**:
   §§§KOD_56§§§

2. **Dodaj logikę przyrostową**:
   §§§KOD_57§§§

3. **Wymuś jednorazowe pełne odświeżenie**:
   §§§KOD_58§§§

---

## Problemy z superzbiorami

### Problem 1: Nie można połączyć się z Superset

**Objawy**:
- Strona logowania wyświetla komunikat „Nieprawidłowe dane uwierzytelniające”
- Domyślna para administrator/administrator nie działa

**Diagnoza**:
§§§KOD_59§§§

**Rozwiązania**:

1. **Zresetuj hasło administratora**:
   §§§KOD_60§§§

2. **Utwórz konto administratora**:
   §§§KOD_61§§§

3. **Zresetuj nadzbiór**:
   §§§KOD_62§§§

### Problem 2: Błąd połączenia z bazą danych

**Objawy**:
- Przycisk „Testuj połączenie” nie działa
- Błąd: „Nie można połączyć się z bazą danych”

**Diagnoza**:
§§§KOD_63§§§

**Rozwiązania**:

1. **Użyj prawidłowego identyfikatora URI SQLAlchemy**:
   §§§KOD_64§§§

2. **Zainstaluj wymagane sterowniki**:
   §§§KOD_65§§§

3. **Sprawdź sieć**:
   §§§KOD_66§§§

### Problem 3: Nie ładują się wykresy

**Objawy**:
- Pulpit nawigacyjny wyświetla pokrętło ładowania w nieskończoność
- Wykresy wyświetlają „Błąd ładowania danych”

**Diagnoza**:
§§§KOD_67§§§

**Rozwiązania**:

1. **Sprawdź limit czasu zapytania**:
   §§§KOD_68§§§

2. **Włącz żądania asynchroniczne**:
   §§§KOD_69§§§

3. **Wyczyść pamięć podręczną**:
   §§§KOD_70§§§

### Problem 4: Błędy uprawnień

**Objawy**:
- Użytkownik nie może zobaczyć pulpitów nawigacyjnych
- Błąd: „Nie masz dostępu do tego pulpitu nawigacyjnego”

**Diagnoza**:
§§§KOD_71§§§

**Rozwiązania**:

1. **Dodaj użytkownika do roli**:
   §§§KOD_72§§§

2. **Przyznaj dostęp do dashboardu**:
   §§§KOD_73§§§

3. **Sprawdź zasady RLS**:
   §§§KOD_74§§§

---

## Problemy z PostgreSQL

### Problem 1: Odmowa połączenia

**Objawy**:
- Aplikacje nie mogą połączyć się z PostgreSQL
- Błąd: „Odmowa połączenia” lub „Nie można się połączyć”

**Diagnoza**:
§§§KOD_75§§§

**Rozwiązania**:

1. **Uruchom ponownie PostgreSQL**:
   §§§KOD_76§§§

2. **Sprawdź mapowanie portów**:
   §§§KOD_77§§§

3. **Sprawdź dane uwierzytelniające**:
   §§§KOD_78§§§

### Problem 2: Brak połączeń

**Objawy**:
- Błąd: „FATAL: pozostałe gniazda połączeń są zarezerwowane”
- Aplikacje sporadycznie nie łączą się

**Diagnoza**:
§§§KOD_79§§§

**Rozwiązania**:

1. **Zwiększ max_połączenia**:
   §§§KOD_80§§§

2. **Użyj łączenia połączeń**:
   §§§KOD_81§§§

3. **Zabij bezczynne połączenia**:
   §§§KOD_82§§§

### Problem 3: Powolne zapytania

**Objawy**:
- Zapytania do bazy danych trwają kilka sekund
- Aplikacje wygasają

**Diagnoza**:
§§§KOD_83§§§

**Rozwiązania**:

1. **Utwórz indeksy**:
   §§§KOD_84§§§

2. **Przeprowadź ANALIZĘ**:
   §§§KOD_85§§§

3. **Zwiększ wspólne bufory**:
   §§§KOD_86§§§

---

##Problemy z MinIO

### Problem 1: Nie można uzyskać dostępu do konsoli MinIO

**Objawy**:
- Przeglądarka wyświetla błąd w `http://localhost:9001`

**Diagnoza**:
§§§KOD_88§§§

**Rozwiązania**:

1. **Sprawdź porty**:
   §§§KOD_89§§§

2. **Uzyskaj dostęp do prawidłowego adresu URL**:
   §§§KOD_90§§§

3. **Uruchom ponownie MinIO**:
   §§§KOD_91§§§

### Problem 2: Błędy odmowy dostępu

**Objawy**:
- Aplikacje nie mogą czytać/zapisywać na S3
- Błąd: „Odmowa dostępu” lub „403 zabroniony”

**Diagnoza**:
§§§KOD_92§§§

**Rozwiązania**:

1. **Sprawdź dane uwierzytelniające**:
   §§§KOD_93§§§

2. **Sprawdź zasady dotyczące wiadra**:
   §§§KOD_94§§§

3. **Utwórz klucz dostępu do aplikacji**:
   §§§KOD_95§§§

### Problem 3: Nie znaleziono zasobnika

**Objawy**:
- Błąd: „Określony zasobnik nie istnieje”

**Diagnoza**:
§§§KOD_96§§§

**Rozwiązania**:

1. **Utwórz wiadro**:
   §§§KOD_97§§§

2. **Sprawdź nazwę segmentu w konfiguracji**:
   §§§KOD_98§§§

---

## Sieć i łączność

### Problem: Usługi nie mogą się komunikować

**Objawy**:
- „Odmowa połączenia” pomiędzy kontenerami
- Błędy „Nie znaleziono hosta”.

**Diagnoza**:
§§§KOD_99§§§

**Rozwiązania**:

1. **Upewnij się, że wszystkie usługi znajdują się w tej samej sieci**:
   §§§KOD_100§§§

2. **Użyj nazw kontenerów, a nie hosta lokalnego**:
   §§§KOD_101§§§

3. **Utwórz ponownie sieć**:
   §§§KOD_102§§§

---

## Problemy z wydajnością

### Problem: Wysokie użycie procesora

**Diagnoza**:
§§§KOD_103§§§

**Rozwiązania**:

1. **Ogranicz konkurencyjne żądania**:
   §§§KOD_104§§§

2. **Optymalizuj zapytania** (zobacz [Problemy z Dremio](#dremio-issues))

3. **Zwiększ alokację procesora**:
   §§§KOD_105§§§

### Problem: Wysokie zużycie pamięci

**Diagnoza**:
§§§KOD_106§§§

**Rozwiązania**:

1. **Zwiększ rozmiar sterty**:
   §§§KOD_107§§§

2. **Włącz rozlewanie dysku**:
   §§§KOD_108§§§

---

## Problemy z jakością danych

Zobacz rozwiązania szczegółowo opisane w [Przewodniku po jakości danych](./data-quality.md).

### Szybkie kontrole

§§§KOD_109§§§

---

## Streszczenie

Ten przewodnik rozwiązywania problemów dotyczył:

- **Podejście ogólne**: Systematyczna metodologia diagnozowania problemów
- **Problemy według komponentów**: Rozwiązania dla 7 usług platformy
- **Problemy z siecią**: Problemy z łącznością kontenera
- **Problemy z wydajnością**: Optymalizacja procesora, pamięci i zapytań
- **Problemy z jakością danych**: Typowe problemy i kontrole danych

**Kluczowe wnioski**:
- Zawsze najpierw sprawdź logi: `docker-compose logs [service]`
- Do komunikacji między usługami używaj nazw kontenerów, a nie hosta lokalnego
- Testuj łączność: `docker exec [container] ping [target]`
- Monitoruj zasoby: `docker stats`
- Zacznij od prostego: uruchom ponownie usługę przed złożonym debugowaniem

**Powiązana dokumentacja:**
- [Przewodnik instalacji](../getting-started/installation.md)
- [Przewodnik po konfiguracji](../getting-started/configuration.md)
- [Przewodnik po jakości danych](./data-quality.md)
- [Architektura: Wdrożenie](../architektura/deployment.md)

**Potrzebujesz dodatkowej pomocy?**
- Sprawdź logi komponentów: `docker-compose logs -f [service]`
- Zapoznaj się z dokumentacją serwisową
- Wyszukaj problemy z GitHubem
- Skontaktuj się z zespołem wsparcia

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r