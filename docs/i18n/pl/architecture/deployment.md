# Architektura wdrożenia

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r  
**Język**: francuski

## Spis treści

1. [Przegląd](#przegląd)
2. [Topologie wdrożeń](#topologie wdrożeń)
3. [Wdrożenie Docker Compose](wdrożenie #docker-compose)
4. [Wdrożenie Kubernetes](#kubernetes-deployment)
5. [Wdrożenia w chmurze](#cloud-deployments)
6. [Konfiguracja wysokiej dostępności](#konfiguracja-wysokiej dostępności)
7. [Strategie skalowania](#scaling-strategies)
8. [Konfiguracja zabezpieczeń](#konfiguracja-bezpieczeństwa)
9. [Monitorowanie i rejestrowanie](#monitoring-and-logowanie)
10. [Odzyskiwanie po awarii](#odzyskiwanie po awarii)
11. [Dobre praktyki](#dobre-praktyki)

---

## Przegląd

Ten dokument zawiera kompleksowe wskazówki dotyczące wdrażania platformy danych w różnych środowiskach, od programowania po produkcję. Omawiamy różne topologie wdrożeń, strategie orkiestracji i najlepsze praktyki operacyjne.

### Cele wdrożenia

- **Niezawodność**: czas sprawności wynoszący 99,9% w przypadku obciążeń produkcyjnych
- **Skalowalność**: Zarządzaj 10-krotnym wzrostem bez zmian architektonicznych
- **Bezpieczeństwo**: Dogłębna ochrona z wieloma warstwami zabezpieczeń
- **Łatwość konserwacji**: Łatwe aktualizacje i zarządzanie konfiguracją
- **Rentowność**: Optymalizacja wykorzystania zasobów

### Typy środowiska

| Środowisko | Cel | Skala | Dostępność |
|--------------|---------|-------------|--------------|
| **Rozwój** | Rozwój funkcji, testowanie | Pojedynczy węzeł | <95% |
| **Inscenizacja** | Walidacja przedprodukcyjna | Wielowęzłowy | 95-99% |
| **Produkcja** | Obciążenia danymi na żywo | Zgrupowane | >99,9% |
| **DR** | Miejsce odzyskiwania po awarii | Lustro produkcyjne | Gotowość |

---

## Topologie wdrożeń

### Topologia 1: Rozwój na jednym hoście

§§§KOD_0§§§

**Przypadek użycia**: rozwój lokalny, testy, demonstracje

**Specyfikacje**:
- Procesor: 4-8 rdzeni
- RAM: 16-32 GB
- Dysk: SSD 100-500 GB
- Sieć: tylko Localhost

**Korzyści**:
- Prosta konfiguracja (tworzenie dokera)
- Niski koszt
- Szybka iteracja

**Wady**:
- Żadnej redundancji
- Ograniczona wydajność
- Nie nadaje się do produkcji

### Topologia 2: Wiele hostów Docker Swarm

§§§KOD_1§§§

**Przypadek użycia**: Wdrożenia etapowe i małe wdrożenia produkcyjne

**Specyfikacje**:
- Węzły menedżerskie: 3x (2 procesory, 4 GB RAM)
- Węzły robocze: 3+ (8-16 procesorów, 32-64 GB RAM)
- Węzeł bazy danych: 1-2 (4 CPU, 16 GB RAM, SSD)
- Węzły magazynujące: 4+ (2 procesory, 8 GB RAM, HDD/SSD)

**Korzyści**:
- Wysoka dostępność
- Łatwe skalowanie
- Zintegrowane równoważenie obciążenia
- Monitorowanie stanu zdrowia

**Wady**:
- Bardziej złożone niż pojedynczy host
- Wymaga współdzielonej pamięci lub woluminów
- Złożoność konfiguracji sieci

### Topologia 3: Klaster Kubernetes

§§§KOD_2§§§

**Przypadek użycia**: wdrożenia produkcyjne na dużą skalę

**Specyfikacje**:
- Płaszczyzna sterowania: ponad 3 węzły (zarządzane lub hostowane samodzielnie)
- Węzły robocze: ponad 10 węzłów (16-32 procesorów, 64-128 GB RAM)
- Pamięć masowa: sterownik CSI (EBS, GCP PD, Azure Disk)
- Sieć: wtyczka CNI (Calico, Cilium)

**Korzyści**:
- Orkiestracja na poziomie przedsiębiorstwa
- Automatyczne skalowanie i naprawa
- Zaawansowana sieć (siatka usługowa)
- Kompatybilny z GitOps
- Wsparcie dla wielu najemców

**Wady**:
- Kompleksowa konfiguracja i zarządzanie
- Bardziej stroma krzywa uczenia się
- Wyższe koszty operacyjne

---

## Wdrożenie Docker Compose

### Środowisko programistyczne

Nasz `docker-compose.yml` standard rozwoju lokalnego:

§§§KOD_4§§§

### Koszty ogólne produkcji Docker Compose

§§§KOD_5§§§

**Wdróż w środowisku produkcyjnym**:
§§§KOD_6§§§

---

## Wdrożenie Kubernetes

### Konfiguracja przestrzeni nazw

§§§KOD_7§§§

### Wdrożenie Airbyte

§§§KOD_8§§§

### Stanowy zestaw Dremio

§§§KOD_9§§§

### Automatyczne skalowanie podów poziomych

§§§KOD_10§§§

### Konfiguracja wejścia

§§§KOD_11§§§

### Pamięć trwała

§§§KOD_12§§§

---

## Wdrożenia w chmurze

### Architektura AWS

§§§KOD_13§§§

**Wykorzystane usługi AWS**:
- **EKS**: Zarządzany klaster Kubernetes
- **RDS**: PostgreSQL Multi-AZ dla metadanych
- **S3**: Magazyn obiektów dla jeziora danych
- **ALB**: Aplikacja do równoważenia obciążenia
- **CloudWatch**: Monitorowanie i rejestrowanie
- **Secrets Manager**: Zarządzanie identyfikatorami
- **ECR**: Rejestr kontenerów
- **VPC**: Izolacja sieci

**Przykład Terraformy**:
§§§KOD_14§§§

### Architektura platformy Azure

**Usługi platformy Azure**:
- **AKS**: Usługa Azure Kubernetes
- **Azure Database for PostgreSQL**: Elastyczny serwer
— **Azure Blob Storage**: Data Lake Gen2
- **Brama aplikacji**: Moduł równoważenia obciążenia
- **Azure Monitor**: Monitorowanie i rejestrowanie
- **Key Vault**: Zarządzanie sekretami
- **ACR**: Rejestr kontenerów platformy Azure

### Architektura GCP

**Usługi GCP**:
- **GKE**: Silnik Google Kubernetes
- **Cloud SQL**: PostgreSQL z HA
- **Przechowywanie w chmurze**: Przechowywanie obiektów
- ** Równoważenie obciążenia w chmurze**: Globalny moduł równoważenia obciążenia
- **Logowanie w chmurze**: Scentralizowane rejestrowanie
- **Secret Manager**: Zarządzanie identyfikatorami
- **Rejestr artefaktów**: Rejestr kontenerów

---

## Konfiguracja wysokiej dostępności

### Baza danych o wysokiej dostępności

§§§KOD_15§§§

**Konfiguracja PostgreSQL HA**:
§§§KOD_16§§§

### Rozproszona konfiguracja MinIO

§§§KOD_17§§§

**Kodowanie usuwania**: MinIO automatycznie chroni dane za pomocą kodowania usuwania (EC:4 dla ponad 4 węzłów).

### Konfiguracja klastra Dremio

§§§KOD_18§§§

---

## Strategie skalowania

### Skalowanie pionowe

**Kiedy używać**: Unikalne komponenty osiągają limity zasobów

| Składnik | Początkowe | Skalowane | Poprawa |
|---------|---------|--------------------------------|--------|
| Wykonawca Dremio | 8 procesorów, 16 GB | 16 procesorów, 32 GB | 2x wydajność zapytań |
| PostgreSQL | 4 procesory, 8 GB | 8 procesorów, 16 GB | 2x debet transakcyjny |
| Pracownik Airbyte | 2 procesory, 4 GB | 4 procesory, 8 GB | 2x synchronizacja równoległości |

§§§KOD_19§§§

### Skalowanie poziome

**Kiedy używać**: Należy obsłużyć więcej jednoczesnych obciążeń

§§§KOD_20§§§

**Zasady autoskalowania**:
§§§KOD_21§§§

### Skalowanie pamięci

**MinIO**: Dodaj węzły do ​​rozproszonego klastra
§§§KOD_22§§§

**PostgreSQL**: Użyj połączeń pulowych (PgBouncer)
§§§KOD_23§§§

---

## Konfiguracja zabezpieczeń

### Bezpieczeństwo sieci

§§§KOD_24§§§

### Zarządzanie tajemnicami

§§§KOD_25§§§

**Operator tajemnic zewnętrznych** (zalecany do produkcji):
§§§KOD_26§§§

### Konfiguracja TLS/SSL

§§§KOD_27§§§

---

## Monitorowanie i rejestrowanie

### Metryki Prometeusza

§§§KOD_28§§§

### Panele Grafana

**Kluczowe wskaźniki**:
- Airbyte: wskaźnik powodzenia synchronizacji, zsynchronizowane nagrania, czas trwania synchronizacji
- Dremio: Liczba próśb, czas trwania próśb, świeżość refleksji
- PostgreSQL: Liczba połączeń, współczynnik transakcji, współczynnik trafień w pamięci podręcznej
- MinIO: częstotliwość żądań, przepustowość, stopa błędów

### Scentralizowane logowanie

§§§KOD_29§§§

---

## Odzyskiwanie po awarii

### Strategia tworzenia kopii zapasowych

§§§KOD_30§§§

**Kopia zapasowa PostgreSQL**:
§§§KOD_31§§§

**Kopia zapasowa MinIO**:
§§§KOD_32§§§

### Procedury odzyskiwania

**Cele RTO/RPO**:
| Środowisko | RTO (cel czasu odzyskiwania) | RPO (cel punktu odzyskiwania) |
|--------------|------------------------------------------------------|---------------------------------|
| Rozwój | 24 godziny | 24 godziny |
| Inscenizacja | 4 godziny | 4 godziny |
| Produkcja | 1 godzina | 15 minut |

**Kroki odzyskiwania**:
1. Oceń zakres awarii
2. Przywróć bazę danych z ostatniej kopii zapasowej
3. Zastosuj dzienniki WAL aż do momentu awarii
4. Przywróć pamięć obiektów z migawki
5. Uruchom ponownie usługi w kolejności zależności
6. Sprawdź integralność danych
7. Wznów działanie

---

## Najlepsze praktyki

### Lista kontrolna wdrożenia

- [ ] Użyj infrastruktury jako kodu (Terraform/Helm)
- [ ] Implementacja przepływu pracy GitOps (ArgoCD/Flux)
- [ ] Skonfiguruj kontrolę stanu wszystkich usług
- [ ] Zdefiniuj limity zasobów i żądania
- [ ] Włącz automatyczne skalowanie, jeśli to konieczne
- [ ] Wdrażaj zasady sieciowe
- [ ] Użyj zewnętrznego zarządzania sekretami
- [ ] Skonfiguruj TLS dla wszystkich zewnętrznych punktów końcowych
- [ ] Skonfiguruj monitorowanie i alerty
- [ ] Zaimplementuj agregację logów
- [ ] Skonfiguruj automatyczne kopie zapasowe
- [ ] Przetestuj procedury odzyskiwania po awarii
- [ ] Dokumentuj elementy Runbook dotyczące typowych problemów
- [ ] Skonfiguruj potoki CI/CD
- [ ] Wdrażaj wdrożenia niebiesko-zielone lub kanarkowe

### Regulacja wydajności

**Dremio**:
§§§KOD_33§§§

**PostgreSQL**:
§§§KOD_34§§§

**MinIO**:
§§§KOD_35§§§

### Optymalizacja kosztów

1. **Prawidłowo dopasuj zasoby**: Monitoruj rzeczywiste wykorzystanie i dostosowuj limity
2. **Użyj instancji typu spot/wywłaszczania**: w przypadku obciążeń niekrytycznych
3. **Wdrażaj zasady cyklu życia danych**: Przenieś zimne dane na tańsze poziomy przechowywania
4. **Zaplanuj skalowanie zasobów**: Zmniejsz w godzinach pozaszczytowych
5. **Użyj instancji zarezerwowanych**: w przypadku podstawowej pojemności (oszczędność 40–60%)

---

## Streszczenie

Ten przewodnik po architekturze wdrażania obejmuje:

- **Topologie**: rozwój z jednym hostem, rój Docker Swarm z wieloma hostami, klaster Kubernetes
- **Orkiestracja**: Docker Compose dla programistów, Kubernetes dla produkcji
- **Wdrożenia w chmurze**: architektury referencyjne AWS, Azure i GCP
- **Wysoka dostępność**: replikacja baz danych, rozproszona pamięć masowa, usługi klastrowe
- **Skalowanie**: strategie skalowania w pionie i poziomie z autoskalowaniem
- **Bezpieczeństwo**: zasady sieciowe, zarządzanie sekretami, konfiguracja TLS/SSL
- **Monitorowanie**: metryki Prometheus, dashboardy Grafana, scentralizowane logowanie
- **Odzyskiwanie po awarii**: strategie tworzenia kopii zapasowych, cele RTO/RPO, procedury odzyskiwania

Kluczowe punkty do zapamiętania:
- Zacznij od prostego (pojedynczy host) i skaluj w razie potrzeby
- Kubernetes oferuje większą elastyczność produkcji
- Wdróż pełny monitoring od pierwszego dnia
- Zautomatyzuj wszystko za pomocą infrastruktury jako kodu
- Regularnie testuj procedury odzyskiwania po awarii

**Powiązana dokumentacja:**
- [Przegląd architektury](./overview.md)
- [Komponenty](./components.md)
- [Przepływ danych](./data-flow.md)
- [Przewodnik instalacji](../getting-started/installation.md)

---

**Wersja**: 3.2.0  
**Ostatnia aktualizacja**: 16 października 2025 r