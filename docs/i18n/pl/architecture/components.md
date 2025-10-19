# Komponenty platformy

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Język**: francuski

---

## Przegląd komponentów

Platforma danych składa się z 7 głównych komponentów współpracujących ze sobą w celu zapewnienia kompletnego rozwiązania.

§§§KOD_0§§§

---

## 1. Airbyte – Platforma Integracji Danych

### Przegląd

Airbyte to silnik integracji danych typu open source, który konsoliduje dane z wielu źródeł do miejsc docelowych.

**Wersja**: 0.50.33  
**Licencja**: MIT  
**Strona internetowa**: https://airbyte.com

### Kluczowe funkcje

- **Ponad 300 gotowych konektorów**: bazy danych, interfejsy API, pliki, aplikacje SaaS
- **Change Data Capture (CDC)**: Replikacja danych w czasie rzeczywistym
- **Niestandardowe złącza**: Kompiluj za pomocą języka Python lub CDK o niskim kodzie
- **Normalizacja**: Przekształć JSON w tabele relacyjne
- ** Synchronizacja przyrostowa**: Synchronizuj tylko nowe/zmodyfikowane dane
- **Monitorowanie**: Zintegrowana synchronizacja statusu śledzenia

### Architektura

§§§KOD_1§§§

### Przypadek użycia

- **Potoki ELT**: przepływy pracy wyodrębniania, ładowania i przekształcania
- **Replikacja bazy danych**: Synchronizuj bazy danych
- **Integracja API**: Wyodrębnij dane z interfejsów API REST
- **Przyjmowanie danych z jeziora danych**: Załaduj dane do S3/MinIO
- **Migracja do chmury**: Przenieś dane lokalnie do chmury

### Organizować coś

§§§KOD_2§§§

### Punkty Integracyjne

- **Wyjścia do**: MinIO S3, PostgreSQL, Dremio
- **Orkiestracja**: Może zostać wywołana przez przepływ powietrza, prefekcie
- **Monitorowanie**: Punkt końcowy metryk Prometheus

---

## 2. Dremio – Platforma Data Lakehouse

### Przegląd

Dremio zapewnia ujednolicony interfejs SQL dla wszystkich źródeł danych z przyspieszeniem zapytań.

**Wersja**: 26.0 OSS  
**Licencja**: Apache 2.0  
**Strona internetowa**: https://www.dremio.com

### Kluczowe funkcje

- **Data Lakehouse**: Połącz elastyczność jeziora z wydajnością magazynu
- **Przemyślenia**: Automatyczne przyspieszanie zapytań (nawet 100 razy szybciej)
- **Lot Arrow**: Transfer danych o wysokiej wydajności
- **Wirtualizacja danych**: Zapytanie bez przenoszenia danych
- **Warstwa semantyczna**: Przyjazne dla biznesu definicje danych
- **Podróż w czasie**: Zapytaj o wersje historyczne

### Architektura

§§§KOD_3§§§

### Przypadek użycia

- **Analiza samoobsługowa**: Pozwól użytkownikom biznesowym przeglądać dane
- **Data Mesh**: Sfederowany dostęp do danych
- **Przyspieszenie zapytań**: Przyspieszenie zapytań w panelu kontrolnym
- **Katalog danych**: odkrywaj dane i zarządzaj nimi
- **Aktywacja BI**: Power Tableau, Power BI, Superset

### Organizować coś

§§§KOD_4§§§

### Punkty Integracyjne

- **Czyta z**: MinIO S3, PostgreSQL, Elasticsearch
- **Przekształć za pomocą**: dbt
- **Używany do**: Superset, Tableau, Power BI

### Serwer proxy PostgreSQL dla Dremio

Dremio może emulować serwer PostgreSQL, umożliwiając narzędziom zgodnym z PostgreSQL łączenie się z Dremio tak, jakby była to standardowa baza danych PostgreSQL.

#### Architektura proxy PostgreSQL

§§§KOD_5§§§

#### Porównanie 3 portów Dremio

§§§KOD_6§§§

#### Konfiguracja serwera proxy

§§§KOD_7§§§

#### Przypadki użycia serwera proxy

1. **Starsze narzędzia BI**: Podłącz narzędzia, które nie obsługują Arrow Flight
2. **Łatwa migracja**: Zamień PostgreSQL na Dremio bez zmiany kodu
3. **Kompatybilność ODBC/JDBC**: Użyj standardowych sterowników PostgreSQL
4. **Programowanie**: Testuj za pomocą znanych narzędzi PostgreSQL (psql, pgAdmin)

#### Przykład połączenia

§§§KOD_8§§§

#### Ograniczenia

- **Wydajność**: Lot strzałek (port 32010) jest 20-50 razy szybszy
- **Funkcje**: Niektóre zaawansowane funkcje PostgreSQL nie są obsługiwane
- **Zalecenie**: Użyj Arrow Flight do produkcji, proxy PostgreSQL dla kompatybilności

#### Przepływ połączenia przez serwer proxy PostgreSQL

§§§KOD_9§§§

#### Porównanie protokołów

| Protokół | Port | Wydajność | Opóźnienie | Przypadki użycia |
|--------------|------|------------|-------------|--------|
| **API REST** | 9047 | Standardowe | ~50-100ms | Interfejs sieciowy, administracja |
| **ODBC/JDBC (serwer proxy PostgreSQL)** | 31010 | Dobrze | ~20-50ms | Starsze narzędzia BI, kompatybilność |
| **Lot strzały** | 32010 | Znakomity (20-50x) | ~5-10ms | Produkcja, Superset, dbt |

#### Wydajność porównawcza

§§§KOD_10§§§

---

## 3. dbt - Narzędzie do transformacji danych

### Przegląd

dbt (narzędzie do budowania danych) umożliwia inżynierom analitycznym przekształcanie danych za pomocą języka SQL.

**Wersja**: 1.10+  
**Licencja**: Apache 2.0  
**Strona internetowa**: https://www.getdbt.com

### Kluczowe funkcje

- **Oparta na SQL**: Zapis transformacji w SQL
- **Kontrola wersji**: Integracja z Git w celu współpracy
- **Testy**: Zintegrowane testy jakości danych
- **Dokumentacja**: Automatyczne generowanie słowników danych
- **Modułowość**: Makra i pakiety wielokrotnego użytku
- **Modele przyrostowe**: przetwarzaj tylko nowe dane

### Architektura

§§§KOD_11§§§

### Przypadek użycia

- **Modelowanie danych**: Twórz diagramy gwiazd/płatków
- **Jakość danych**: Sprawdź integralność danych
- **Powoli zmiana wymiarów**: Śledź zmiany historyczne
- **Agregacja danych**: Twórz tabele podsumowujące
- **Dokumentacja danych**: Generowanie katalogów danych

### Organizować coś

§§§KOD_12§§§

### Punkty Integracyjne

- **Czytanie z**: Zestawy danych Dremio
- **Napisane do**: Dremio (przez Arrow Flight)
- **Organizacja:**: Airflow, cron, postsynchronizacja Airbyte

---

## 4. Apache Superset – platforma Business Intelligence

### Przegląd

Superset to nowoczesna platforma do eksploracji i wizualizacji danych.

**Wersja**: 3.0  
**Licencja**: Apache 2.0  
**Strona internetowa**: https://superset.apache.org

### Kluczowe funkcje

- **SQL IDE**: Zaawansowany edytor SQL z autouzupełnianiem
- **Bogate wizualizacje**: ponad 50 typów wykresów
- **Interaktywne pulpity nawigacyjne**: drążenie, filtry, filtrowanie krzyżowe
- **Laboratorium SQL**: Interfejs zapytań ad-hoc
- **Alerty**: Zaplanowane raporty i alerty
- **Buforowanie**: Buforowanie wyników zapytań w celu sprawdzenia wydajności

### Architektura

§§§KOD_13§§§

### Przypadek użycia

- **Panele wykonawcze**: Monitorowanie KPI
- **Analiza operacyjna**: Monitorowanie w czasie rzeczywistym
- **BI Self-Service**: wzmocnienie pozycji analityków
- **Embedded Analytics**: integracja elementów iframe z aplikacjami
- **Eksploracja danych**: Analiza doraźna

### Organizować coś

§§§KOD_14§§§

### Punkty Integracyjne

- **Prośby**: Dremio (przez Arrow Flight)
- **Uwierzytelnianie**: LDAP, OAuth2, baza danych
- **Alerty**: e-mail, Slack

---

## 5. PostgreSQL - Relacyjna Baza Danych

### Przegląd

PostgreSQL to zaawansowany system zarządzania relacyjnymi bazami danych typu open source.

**Wersja**: 16  
**Licencja**: Licencja PostgreSQL  
**Strona internetowa**: https://www.postgresql.org

### Kluczowe funkcje

- **Zgodność z ACID**: Wiarygodne transakcje
- **Obsługa JSON**: Natywne typy JSON/JSONB
- **Wyszukiwanie pełnotekstowe**: Zintegrowane możliwości wyszukiwania
- **Rozszerzenia**: PostGIS, pg_stat_statements, TimescaleDB
- **Replikacja**: replikacja strumieniowa, replikacja logiczna
- **Partycjonowanie**: Natywne partycjonowanie tabeli

### Architektura

§§§KOD_15§§§

### Przypadek użycia

- **Przechowywanie metadanych**: Przechowywanie metadanych systemowych
- **Ładunki transakcyjne**: Aplikacje OLTP
- **Tabele pomostowe**: Tymczasowe przetwarzanie danych
- **Konfiguracja pamięci**: Ustawienia aplikacji
- **Dzienniki audytu**: Śledź zmiany w systemie

### Organizować coś

§§§KOD_16§§§

### Punkty Integracyjne

- **Przeczytane przez**: Dremio, Superset, Airbyte
- **Napisane przez**: Airbyte, dbt, aplikacje
- **Zarządzane przez**: Automatyczne kopie zapasowe, replikacja

---

## 6. MinIO – pamięć obiektowa kompatybilna z S3

### Przegląd

MinIO to wysokowydajny system obiektowej pamięci masowej zgodny z S3.

**Wersja**: najnowsza  
**Licencja**: AGPLv3  
**Strona internetowa**: https://min.io

### Kluczowe funkcje

- **S3 API**: w 100% kompatybilny z Amazon S3
- **Wysoka wydajność**: przepustowość wielu GB/s
- **Kod kasowany**: Dane dotyczące zrównoważonego rozwoju i dostępności
- **Wersjonowanie**: Kontrola wersji obiektu
- **Szyfrowanie**: po stronie serwera i po stronie klienta
- **Multi-Cloud**: wdrażaj wszędzie

### Architektura

§§§KOD_17§§§

### Przypadek użycia

- **Data Lake**: przechowuj surowe i przetworzone dane
- **Przechowywanie obiektów**: pliki, obrazy, filmy
- **Kopia zapasowa magazynu**: Kopie zapasowe bazy danych i systemu
- **Archiwum**: Długoterminowe przechowywanie danych
- **Przechowywanie danych**: Tymczasowe przechowywanie danych

### Organizować coś

§§§KOD_18§§§

### Punkty Integracyjne

- **Napisane przez**: Airbyte, dbt, aplikacje
- **Przeczytane przez**: Dremio, badacze danych
- **Zarządzane przez**: mc (Klient MinIO), s3cmd

---

## 7. Elasticsearch - Silnik wyszukiwania i analityki

### Przegląd

Elasticsearch to rozproszony silnik wyszukiwania i analiz zbudowany na platformie Apache Lucene.

**Wersja**: 8.15  
**Licencja**: Licencja elastyczna 2.0  
**Strona internetowa**: https://www.elastic.co

### Kluczowe funkcje

- **Wyszukiwanie pełnotekstowe**: Zaawansowane możliwości wyszukiwania
- **Indeksowanie w czasie rzeczywistym**: Dostępność danych w czasie zbliżonym do rzeczywistego
- **Rozproszone**: Skalowalność pozioma
- **Agregacje**: Złożona analityka
- **RESTful API**: Proste API HTTP
- **Uczenie maszynowe**: Wykrywanie anomalii

### Architektura

§§§KOD_19§§§

### Przypadek użycia

- **Dzienniki analityczne**: Scentralizowane rejestrowanie (stos ELK)
- **Wyszukiwanie aplikacji**: katalogi produktów, wyszukiwanie w witrynie
- **Analiza bezpieczeństwa**: przypadki użycia SIEM
- **Obserwowalność**: Metryki i ślady
- **Analiza tekstu**: NLP i analiza nastrojów

### Organizować coś

§§§KOD_20§§§

### Punkty Integracyjne

- **Indeksowane przez**: Logstash, Filebeat
- **Na prośbę**: Dremio, Kibana
- **Monitorowane przez**: Elasticsearch Monitoring

---

## Porównanie komponentów

| Składnik | Wpisz | Główne zastosowanie | Skalowalność | stan |
|--------------|------|----------------|------------|------|
| **Airbyte** | Integracja | Pozyskiwanie danych | Poziome (pracownicy) | Bezpaństwowiec |
| **Dremio** | Silnik zapytań | Dostęp do danych | Poziome (wykonawcy) | Bezpaństwowiec |
| **db** | Transformacja | Modelowanie danych | Pionowe (serca) | Bezpaństwowiec |
| **Nadzbiór** | Platforma BI | Wizualizacja | Poziomy (wstęga) | Bezpaństwowiec |
| **PostgreSQL** | Baza danych | Przechowywanie metadanych | Pionowe (+ replikacja) | Stanowy |
| **MinIO** | Przechowywanie obiektów | Jezioro danych | Poziome (rozproszone) | Stanowy |
| **Elastyczne wyszukiwanie** | Wyszukiwarka | Wyszukiwanie pełnotekstowe | Poziome (klaster) | Stanowy |

---

## Wymagania dotyczące zasobów

### Minimalna konfiguracja (programowanie)

§§§KOD_21§§§

### Zalecana konfiguracja (produkcja)

§§§KOD_22§§§

---

## Tabela zgodności wersji

| Składnik | Zwolnij | Kompatybilny z |
|---------|---------|----------------------|
| Airbyte | 0,50+ | Wszystkie kierunki |
| Dremio | 26,0 | dbt 1.8+, klienci Arrow Flight |
| db | 1.10+ | Dremio 23.0+ |
| Nadzbiór | 3.0+ | Dremio 22.0+, PostgreSQL 12+ |
| PostgreSQL | 16 | Wszystkie komponenty |
| MinIO | Najnowsze | Klienci kompatybilni z S3 |
| Elastyczne wyszukiwanie | 8.15 | Dremio 26.0+, Logstash 8.x |

---

**Wersja przewodnika po komponentach**: 3.2.0  
**Ostatnia aktualizacja**: 16.10.2025  
**Obsługiwane przez**: Zespół ds. platformy danych