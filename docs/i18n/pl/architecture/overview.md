# Przegląd architektury

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Język**: francuski

---

## Wstęp

Platforma danych to nowoczesna architektura natywna dla chmury, zbudowana w oparciu o technologie open source. Zapewnia kompleksowe rozwiązanie do pozyskiwania, przechowywania, przekształcania i wizualizacji danych, zaprojektowane z myślą o obciążeniach analitycznych na skalę korporacyjną.

§§§KOD_0§§§

---

## Zasady projektowania

### 1. Najpierw otwarte oprogramowanie

**Filozofia**: Korzystaj z technologii open source, aby uniknąć uzależnienia od dostawców i zachować elastyczność.

**Korzyści**:
- Brak kosztów licencji
- Rozwój społeczności
- Pełna możliwość personalizacji
- Przejrzysty audyt bezpieczeństwa
- Szeroka kompatybilność ekosystemowa

### 2. Architektura warstwowa

**Filozofia**: Podziel problemy na odrębne warstwy w celu zapewnienia łatwości konserwacji i skalowalności.

**Warstwy**:
§§§KOD_1§§§

### 3. ELT zamiast ETL

**Filozofia**: Najpierw załaduj surowe dane, a następnie przekształć je w miejsce docelowe (ELT).

**Dlaczego ELT?**
- **Elastyczność**: Przekształcaj dane na wiele sposobów bez ponownego wyodrębniania
- **Wydajność**: Użyj obliczenia miejsca docelowego dla transformacji
- **Audytowalność**: Surowe dane zawsze dostępne do weryfikacji
- **Koszt**: Zmniejsz obciążenie ekstrakcji w systemach źródłowych

**Przepływ**:
§§§KOD_2§§§

### 4. Model Data Lakehouse

**Filozofia**: Połącz elastyczność jeziora danych z wydajnością hurtowni danych.

**Cechy**:
- **Transakcje ACID**: Zaufane operacje na danych
- **Aplikacja schematu**: Gwarancje jakości danych
- **Podróże w czasie**: Zapytaj o wersje historyczne
- **Formaty otwarte**: Parkiet, Góra Lodowa, Jezioro Delta
- **Bezpośredni dostęp do plików**: Brak zastrzeżonego blokowania

### 5. Projekt natywny dla chmury

**Filozofia**: Projektowanie dla środowisk kontenerowych i rozproszonych.

**Realizacja**:
- Kontenery Docker dla wszystkich usług
- Skalowalność pozioma
- Infrastruktura jako kod
- Bezpaństwowcy, jeśli to możliwe
- Konfiguracja za pomocą zmiennych środowiskowych

---

## Modele architektury

### Architektura Lambda (wsadowa + strumień)

§§§KOD_3§§§

**Warstwa wsadowa** (dane historyczne):
- Duże ilości danych
- Zabieg okresowy (co godzinę/dziennie)
- Akceptowalne duże opóźnienia
- Możliwość całkowitego przygotowania

**Warstwa prędkości** (dane w czasie rzeczywistym):
- Zmień przechwytywanie danych (CDC)
- Wymagane małe opóźnienie
- Tylko aktualizacje przyrostowe
- Zarządza najnowszymi danymi

**Warstwa usług**:
- Łączy widoki wsadowe i szybkościowe
- Interfejs pojedynczego zapytania (Dremio)
- Automatyczny wybór widoku

### Medalion Architektury (Brąz → Srebro → Złoto)

§§§KOD_4§§§

**Warstwa brązu** (Surowy):
- Dane pochodzą ze źródeł
- Żadnej transformacji
- Zachowana pełna historia
- Tutaj ładuje się Airbyte

**Warstwa srebra** (wyczyszczona):
- Stosowana jakość danych
- Standaryzowane formaty
- szablony inscenizacji dbt
- Analityka gotowa

**Warstwa złota** (Zawód):
- Zagregowane wskaźniki
- Stosowana logika biznesowa
- Modele Marts dbt
- Zoptymalizowany do spożycia

---

## Interakcje pomiędzy komponentami

### Przepływ pozyskiwania danych

§§§KOD_5§§§

### Rurociąg transformacji

§§§KOD_6§§§

### Wykonywanie zapytań

§§§KOD_7§§§

---

## Modele skalowalności

### Skalowanie poziome

**Usługi bezpaństwowe** (mogą się swobodnie rozwijać):
- Pracownicy Airbyte: Ewoluuj w celu równoległych synchronizacji
- Dremio Executors: Skalowanie wydajności zapytań
- Web Superset: Ewoluuj dla konkurencyjnych użytkowników

**Usługi stanowe** (wymagają koordynacji):
- PostgreSQL: replikacja repliki podstawowej
- MinIO: Tryb rozproszony (wiele węzłów)
- Elasticsearch: Klaster z fragmentowaniem

### Skalowanie pionowe

**Intensywna pamięć**:
- Dremio: Zwiększ stertę JVM dla dużych zapytań
- PostgreSQL: Więcej pamięci RAM dla bufora pamięci podręcznej
- Elasticsearch: Więcej sterty do indeksowania

**Intensywnie obciążający procesor**:
- dbt: Więcej rdzeni dla modeli konstrukcji równoległych
- Airbyte: Szybsze transformacje danych

### Partycjonowanie danych

§§§KOD_8§§§

---

## Wysoka dostępność

### Redundancja usług

§§§KOD_9§§§

### Scenariusze niepowodzeń

| Składnik | Podział | Odzyskiwanie |
|--------------|-------|--------|
| **Pracownik Airbyte** | Katastrofa kontenera | Automatyczny restart, wznów synchronizację |
| **Egzekutor Dremio** | Awaria węzła | Żądanie przekierowane do innych wykonawców |
| **PostgreSQL** | Podstawowy nieczynny | Promuj replikę w podstawowej |
| **Węzeł MinIO** | Awaria dysku | Kodowanie kasujące rekonstruuje dane |
| **Nadzbiór** | Usługa nieczynna | Balancer przekierowuje ruch |

### Strategia tworzenia kopii zapasowych

§§§KOD_10§§§

---

## Architektura bezpieczeństwa

### Bezpieczeństwo sieci

§§§KOD_11§§§

### Uwierzytelnianie i autoryzacja

**Uwierzytelnianie usługi**:
- **Dremio**: integracja z LDAP/AD, OAuth2, SAML
- **Nadzbiór**: uwierzytelnianie bazy danych, LDAP, OAuth2
- **Airbyte**: uwierzytelnianie podstawowe, OAuth2 (korporacja)
- **MinIO**: zasady IAM, tokeny STS

**Poziomy autoryzacji**:
§§§KOD_12§§§

### Szyfrowanie danych

**Spokojnie**:
- MinIO: szyfrowanie po stronie serwera (AES-256)
- PostgreSQL: przezroczyste szyfrowanie danych (TDE)
- Elasticsearch: Zaszyfrowane indeksy

**W transporcie**:
- TLS 1.3 dla całej komunikacji między usługami
- Lot strzałą z TLS dla Dremio ↔ Superset
- HTTPS dla interfejsów internetowych

---

## Monitorowanie i obserwowalność

### Zbiór metryk

§§§KOD_13§§§

**Kluczowe wskaźniki**:
- **Airbyte**: Wskaźnik powodzenia synchronizacji, synchronizacja nagrań, przesłane bajty
- **Dremio**: Opóźnienie żądania, współczynnik trafień w pamięci podręcznej, wykorzystanie zasobów
- **dbt**: Czas budowy modelu, błędy testów
- **Superset**: Czas ładowania panelu, aktywni użytkownicy
- **Infrastruktura**: procesor, pamięć, dysk, sieć

### Rejestrowanie

**Scentralizowane logowanie**:
§§§KOD_14§§§

### Śledzenie

**Śledzenie rozproszone**:
- Integracja z Jaegerem lub Zipkinem
- Śledzenie żądań między usługami
- Identyfikacja wąskich gardeł
- Problemy z wydajnością debugowania

---

## Topologie wdrożeń

### Środowisko programistyczne

§§§KOD_15§§§

### Środowisko testowe

§§§KOD_16§§§

### Środowisko produkcyjne

§§§KOD_17§§§

---

## Uzasadnienie wyborów technologicznych

### Dlaczego Airbyte?

- **Ponad 300 złączy**: Gotowe integracje
- **Open source**: Brak uzależnienia od dostawcy
- **Aktywna społeczność**: ponad 12 tys. gwiazdek na GitHubie
- **Wsparcie CDC**: Przechwytywanie danych w czasie rzeczywistym
- **Standardyzacja**: Wbudowana integracja dbt

### Dlaczego Dremio?

- **Przyspieszenie zapytań**: Zapytania 10–100 razy szybsze
- **Lot Arrow**: Transfer danych o wysokiej wydajności
- **Zgodność z jeziorem danych**: brak przenoszenia danych
- **Samoobsługa**: Użytkownicy biznesowi eksplorują dane
- **Opłacalne**: Zmniejsz koszty magazynowania

### Dlaczego dbt?

- **Na bazie SQL**: Znany analitykom
- **Kontrola wersji**: Integracja z Git
- **Testy**: Zintegrowane testy jakości danych
- **Dokumentacja**: Dokumenty generowane automatycznie
- **Społeczność**: dostępnych ponad 5 tys. pakietów

### Dlaczego superseria?

- **Nowoczesny interfejs użytkownika**: Intuicyjny interfejs
- **SQL IDE**: Zaawansowane możliwości zapytań
- **Bogate wizualizacje**: ponad 50 typów graficznych
- **Rozszerzalne**: Niestandardowe wtyczki
- **Open source**: Obsługiwana platforma Apache

### Dlaczego PostgreSQL?

- **Niezawodność**: zgodność z ACID
- **Wydajność**: Sprawdzona na dużą skalę
- **Funkcje**: JSON, wyszukiwanie pełnotekstowe, rozszerzenia
- **Społeczność**: Dojrzały ekosystem
- **Koszt**: Darmowe i otwarte oprogramowanie

### Dlaczego MinIO?

- **Kompatybilność z S3**: standardowy interfejs API w branży
- **Wydajność**: Wysokie natężenie przepływu
- **Kodowanie usuwania**: Trwałość danych
- **Wiele chmur**: wdrażaj wszędzie
- **Opłacalne**: Alternatywa na własnym serwerze

---

## Przyszła ewolucja architektury

### Planowane ulepszenia

1. **Katalog danych** (integracja OpenMetadata)
   - Zarządzanie metadanymi
   - Śledzenie pochodzenia
   - Odkrywanie danych

2. **Jakość danych** (wielkie oczekiwania)
   - Automatyczna walidacja
   - Wykrywanie anomalii
   - Panele jakości

3. **Operacje ML** (MLflow)
   - Modelowanie potoków szkoleniowych
   - Rejestr modeli
   - Automatyzacja wdrażania

4. **Przetwarzanie strumienia** (Apache Flink)
   - Transformacje w czasie rzeczywistym
   - Kompleksowe przetwarzanie zdarzeń
   - Analityka transmisji strumieniowej

5. **Zarządzanie danymi** (Apache Atlas)
   - Aplikacja polityczna
   - Audyt dostępu
   - Raporty zgodności

---

## Referencje

- [Szczegóły komponentu](components.md)
- [Przepływ danych](przepływ danych.md)
- [Przewodnik po wdrażaniu] (deployment.md)
- [Integracja Airbyte](../guides/airbyte-integration.md)

---

**Wersja przeglądu architektury**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Obsługiwane przez**: Zespół ds. platformy danych