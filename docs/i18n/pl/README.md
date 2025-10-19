# Platforma danych

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>


**RozwiÄ…zanie typu Lakehouse dla przedsiÄ™biorstw**

**JÄ™zyk**: francuski (FR)  
**Wersja**: 3.3.1  
**Ostatnia aktualizacja**: 19 paÅºdziernika 2025 r

---

## PrzeglÄ…d

Profesjonalna platforma danych Å‚Ä…czÄ…ca Dremio, dbt i Apache Superset do transformacji danych klasy korporacyjnej, zapewniania jakoÅ›ci i analityki biznesowej.

Platforma ta zapewnia kompletne rozwiÄ…zanie dla nowoczesnej inÅ¼ynierii danych, obejmujÄ…ce zautomatyzowane potoki danych, testy jakoÅ›ci i interaktywne dashboardy.

Â§Â§Â§KOD_0Â§Â§Â§

---

## Kluczowe funkcje

- Architektura Data Lakehouse z Dremio
- Automatyczne transformacje za pomocÄ… dbt
- Inteligencja biznesowa z Apache Superset
- Kompleksowe testowanie jakoÅ›ci danych
- Synchronizacja w czasie rzeczywistym za poÅ›rednictwem Arrow Flight

---

## SkrÃ³cona instrukcja obsÅ‚ugi

### Warunki wstÄ™pne

- Docker 20.10 lub nowszy
- Docker Compose 2.0 lub nowszy
- Python 3.11 lub nowszy
- Minimum 8 GB pamiÄ™ci RAM

### Obiekt

Â§Â§Â§KOD_1Â§Â§Â§

---

## Architektura

### Komponenty systemu

| SkÅ‚adnik | Port | Opis |
|--------------|------|------------|
| Dremio | 9047, 31010, 32010 | Platforma danych nad jeziorem |
| db | - | NarzÄ™dzie do transformacji danych |
| NadzbiÃ³r | 8088 | Platforma analityki biznesowej |
| PostgreSQL | 5432 | Baza transakcyjna |
| MinIO | 9000, 9001 | PamiÄ™Ä‡ obiektÃ³w (kompatybilna z S3) |
| Elastyczne wyszukiwanie | 9200 | Silnik wyszukiwania i analiz |

Zobacz [dokumentacjÄ™ architektury](architektura/), aby zapoznaÄ‡ siÄ™ ze szczegÃ³Å‚owym projektem systemu.

---

## Dokumentacja

### Uruchamianie
- [Instrukcja instalacji] (wprowadzenie/)
- [Konfiguracja] (wprowadzenie/)
- [Pierwsze kroki] (pierwsze kroki/)

### PodrÄ™czniki uÅ¼ytkownika
- [InÅ¼ynieria danych](przewodniki/)
- [Tworzenie dashboardÃ³w](przewodniki/)
- [Integracja API](przewodniki/)

### Dokumentacja API
- [Odniesienie do API REST](api/)
- [Uwierzytelnianie](api/)
- [PrzykÅ‚ady kodu](api/)

### Dokumentacja architektury
- [Projekt systemu](architektura/)
- [PrzepÅ‚yw danych](architektura/)
- [Przewodnik po wdraÅ¼aniu](architektura/)
- [ðŸŽ¯ Wizualny przewodnik po portach Dremio](architektura/dremio-ports-visual.md) â­ NOWOÅšÄ†

---

## DostÄ™pne jÄ™zyki

| JÄ™zyk | Kod | Dokumentacja |
|------------|------|--------------|
| Angielski | PL | [README.md](../../../README.md) |
| Francuski | PL | [docs/i18n/fr/](../fr/README.md) |
| hiszpaÅ„ski | ES | [docs/i18n/es/](../es/README.md) |
| portugalski | PT | [docs/i18n/pt/](../pt/README.md) |
| Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© | AR | [docs/i18n/ar/](../ar/README.md) |
| ä¸­æ–‡ | CN | [docs/i18n/cn/](../cn/README.md) |
| æ—¥æœ¬èªž | JP | [docs/i18n/jp/](../jp/README.md) |
| Rosyjski | Wielka Brytania | [docs/i18n/ru/](../ru/README.md) |

---

## Wsparcie

Pomoc techniczna:
- Dokumentacja: [README gÅ‚Ã³wny](../../../README.md)
- Åšledzenie problemÃ³w: problemy z GitHubem
- Forum spoÅ‚ecznoÅ›ci: dyskusje na GitHubie
- E-mail: support@example.com

---

**[PowrÃ³t do gÅ‚Ã³wnej dokumentacji](../../../README.md)**
