# dbt API-referens

**Version**: 3.2.0  
**Senast uppdaterad**: 16 oktober 2025  
**Språk**: Franska

## Innehållsförteckning

1. [Översikt](#översikt)
2. [CLI-kommandon](#cli-kommandon)
3. [Python API](#api-python)
4. [Metadatafiler](#metadata-filer)
5. [dbt Cloud API](#api-dbt-moln)
6. [Anpassade makron](#custom-macros)

---

## Översikt

dbt tillhandahåller tre huvudgränssnitt:

| Gränssnitt | Användningsfall | Tillgång |
|--------------|-------------|-------|
| CLI | Utveckling, CI/CD | Kommandorad |
| Python API | Programmatisk exekvering | Python-kod |
| dbt Cloud API | Hanterad tjänst | REST API |
| Metadata | Introspektion | JSON-filer |

---

## CLI-kommandon

### Huvudkommandon

#### dbt run

Kör modellerna för att transformera data.

```bash
# Exécuter tous les modèles
dbt run

# Exécuter un modèle spécifique
dbt run --select customers

# Exécuter un modèle et ses dépendances amont
dbt run --select +customers

# Exécuter un modèle et ses dépendances aval
dbt run --select customers+

# Exécuter les modèles d'un dossier spécifique
dbt run --select staging.*

# Exécuter uniquement les modèles modifiés
dbt run --select state:modified

# Rafraîchissement complet (ignorer la logique incrémentale)
dbt run --full-refresh

# Exécuter avec une cible spécifique
dbt run --target prod
```

**Alternativ**:
```bash
--select (-s)      # Sélectionner les modèles à exécuter
--exclude (-x)     # Exclure des modèles
--full-refresh     # Reconstruire les modèles incrémentaux
--vars             # Passer des variables
--threads          # Nombre de threads (défaut : 1)
--target           # Profil cible
```

#### dbt-test

Kör datakvalitetstester.

```bash
# Exécuter tous les tests
dbt test

# Tester un modèle spécifique
dbt test --select customers

# Exécuter uniquement les tests de schéma
dbt test --select test_type:schema

# Exécuter uniquement les tests de données
dbt test --select test_type:data

# Stocker les échecs de tests
dbt test --store-failures

# Échec sur sévérité warn
dbt test --warn-error
```

#### dbt build

Kör modeller, tester, frön och ögonblicksbilder tillsammans.

§§§KOD_3§§§

#### dbt docs

Generera och servera dokumentation.

§§§KOD_4§§§

### Utvecklarkommandon

#### dbt kompilerar

Kompilera modeller till SQL utan att köra dem.

§§§KOD_5§§§

#### dbt-felsökning

Testa databasanslutning och konfiguration.

§§§KOD_6§§§

#### dbt ls (lista)

Lista projektresurser.

§§§KOD_7§§§

### Datakommandon

#### dbt-frö

Ladda CSV-filer i databasen.

§§§KOD_8§§§

#### dbt ögonblicksbild

Skapa typ 2 långsamt föränderliga dimensionstabeller.

§§§KOD_9§§§

### Verktygskommandon

#### dbt clean

Ta bort kompilerade filer och artefakter.

§§§KOD_10§§§

#### dbt deps

Installera paket från packages.yml.

§§§KOD_11§§§

#### dbt init

Initiera ett nytt dbt-projekt.

§§§KOD_12§§§

---

## Python API

### Grundläggande utförande

§§§KOD_13§§§

### Komplett Python-omslag

§§§KOD_14§§§

### Luftflödesintegration

§§§KOD_15§§§

---

## Metadatafiler

### manifest.json

Innehåller hela projektets metadata.

**Plats**: `target/manifest.json`

§§§KOD_17§§§

### run_results.json

Innehåller exekveringsresultaten från den senaste exekveringen.

**Plats**: `target/run_results.json`

§§§KOD_19§§§

### catalog.json

Innehåller databasschemainformation.

**Plats**: `target/catalog.json`

§§§KOD_21§§§

---

## dbt Cloud API

Om du använder dbt Cloud (ej tillämpligt för lokal installation) är API:et tillgängligt.

**Baswebbadress**: `https://cloud.getdbt.com/api/v2`

### Autentisering

§§§KOD_23§§§

### Utlösa ett jobb

§§§KOD_24§§§

---

## Anpassade makron

### Skapa ett anpassat makro

**Arkiv**: `macros/custom_tests.sql`

§§§KOD_26§§§

### Använd i tester

**Arkiv**: `models/staging/schema.yml`

§§§KOD_28§§§

### Avancerat makro med argument

§§§KOD_29§§§

### Ring ett makro

§§§KOD_30§§§

---

## Sammanfattning

Denna API-referens täckte:

- **CLI-kommandon**: Fullständig referens för alla dbt-kommandon
- **Python API**: Programmatisk körning med Python-omslag
- **Metadatafiler**: manifest.json, run_results.json, catalog.json
- **dbt Cloud API**: Utlösa jobb (om du använder dbt Cloud)
- **Anpassade makron**: Skapa och använd anpassade funktioner

**Nyckelpunkter**:
- Använd CLI för utveckling och interaktivt arbete
- Använd Python API för automatisering och orkestrering
- Analysera metadatafiler för introspektion
- Skapa anpassade makron för återanvändbar logik
- Integrera med Airflow för produktionsplanering

**Relaterad dokumentation**:
- [dbt utvecklingsguide](../guides/dbt-development.md)
- [Datakvalitetsguide](../guides/data-quality.md)
- [Arkitektur: Dataflöde](../architecture/data-flow.md)

---

**Version**: 3.2.0  
**Senast uppdaterad**: 16 oktober 2025