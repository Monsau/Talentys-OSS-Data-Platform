#Ná»n táº£ng dá»¯ liá»‡u

**Giáº£i phÃ¡p kho dá»¯ liá»‡u doanh nghiá»‡p**

**NgÃ´n ngá»¯**: Tiáº¿ng PhÃ¡p (FR)  
**PhiÃªn báº£n**: 3.3.1  
**Cáº­p nháº­t láº§n cuá»‘i**: NgÃ y 19 thÃ¡ng 10 nÄƒm 2025

---

## Tá»•ng quan

Ná»n táº£ng dá»¯ liá»‡u chuyÃªn nghiá»‡p káº¿t há»£p Dremio, dbt vÃ  Apache Superset Ä‘á»ƒ chuyá»ƒn Ä‘á»•i dá»¯ liá»‡u cáº¥p doanh nghiá»‡p, Ä‘áº£m báº£o cháº¥t lÆ°á»£ng vÃ  kinh doanh thÃ´ng minh.

Ná»n táº£ng nÃ y cung cáº¥p giáº£i phÃ¡p hoÃ n chá»‰nh cho ká»¹ thuáº­t dá»¯ liá»‡u hiá»‡n Ä‘áº¡i, bao gá»“m Ä‘Æ°á»ng dáº«n dá»¯ liá»‡u tá»± Ä‘á»™ng, kiá»ƒm tra cháº¥t lÆ°á»£ng vÃ  báº£ng Ä‘iá»u khiá»ƒn tÆ°Æ¡ng tÃ¡c.

```mermaid
graph LR
    A[Sources de donnÃ©es] --> B[Dremio]
    B --> C[dbt]
    C --> D[Superset]
    D --> E[Insights mÃ©tier]
    
    style B fill:#f5f5f5,stroke:#333,stroke-width:2px
    style C fill:#e8e8e8,stroke:#333,stroke-width:2px
    style D fill:#d8d8d8,stroke:#333,stroke-width:2px
```

---

## TÃ­nh nÄƒng chÃ­nh

- Kiáº¿n trÃºc data lakehouse vá»›i Dremio
- Chuyá»ƒn Ä‘á»•i tá»± Ä‘á»™ng vá»›i dbt
- Kinh doanh thÃ´ng minh vá»›i Apache Superset
- Kiá»ƒm tra cháº¥t lÆ°á»£ng dá»¯ liá»‡u toÃ n diá»‡n
- Äá»“ng bá»™ hÃ³a thá»i gian thá»±c thÃ´ng qua Arrow Flight

---

## HÆ°á»›ng dáº«n báº¯t Ä‘áº§u nhanh

### Äiá»u kiá»‡n tiÃªn quyáº¿t

- Docker 20.10 trá»Ÿ lÃªn
- Docker Compose 2.0 trá»Ÿ lÃªn
- Python 3.11 trá»Ÿ lÃªn
- RAM tá»‘i thiá»ƒu 8GB

### CÆ¡ sá»Ÿ

```bash
# Installer les dÃ©pendances

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>

pip install -r requirements.txt

# DÃ©marrer les services
make up

# VÃ©rifier l'installation
make status

# ExÃ©cuter les tests de qualitÃ©
make dbt-test
```

---

## NgÃ nh kiáº¿n â€‹â€‹â€‹â€‹trÃºc

###ThÃ nh pháº§n há»‡ thá»‘ng

| ThÃ nh pháº§n | Cáº£ng | MÃ´ táº£ |
|--------------|------|-------------|
| Dremio | 9047, 31010, 32010 | Ná»n táº£ng há»“ dá»¯ liá»‡u |
| dbt | - | CÃ´ng cá»¥ chuyá»ƒn Ä‘á»•i dá»¯ liá»‡u |
| SiÃªu bá»™ | 8088 | Ná»n táº£ng thÃ´ng minh kinh doanh |
| PostgreSQL | 5432 | CÆ¡ sá»Ÿ dá»¯ liá»‡u giao dá»‹ch |
| MinIO | 9000, 9001 | LÆ°u trá»¯ Ä‘á»‘i tÆ°á»£ng (tÆ°Æ¡ng thÃ­ch vá»›i S3) |
| Elaticsearch | 9200 | CÃ´ng cá»¥ tÃ¬m kiáº¿m vÃ  phÃ¢n tÃ­ch |

Xem [tÃ i liá»‡u kiáº¿n â€‹â€‹trÃºc](architecture/) Ä‘á»ƒ biáº¿t thiáº¿t káº¿ há»‡ thá»‘ng chi tiáº¿t.

---

## TÃ i liá»‡u

### Khá»Ÿi Ä‘á»™ng
- [HÆ°á»›ng dáº«n cÃ i Ä‘áº·t](báº¯t Ä‘áº§u/)
- [Cáº¥u hÃ¬nh](báº¯t Ä‘áº§u/)
- [Báº¯t Ä‘áº§u](báº¯t Ä‘áº§u/)

### HÆ°á»›ng dáº«n sá»­ dá»¥ng
- [Ká»¹ thuáº­t dá»¯ liá»‡u](guides/)
- [Táº¡o trang tá»•ng quan](guides/)
- [TÃ­ch há»£p API](guides/)

### TÃ i liá»‡u API
- [Tham kháº£o API REST](api/)
- [XÃ¡c thá»±c](api/)
- [VÃ­ dá»¥ vá» mÃ£](api/)

### TÃ i liá»‡u kiáº¿n â€‹â€‹trÃºc
- [Thiáº¿t káº¿ há»‡ thá»‘ng](architecture/)
- [Luá»“ng dá»¯ liá»‡u](architecture/)
- [HÆ°á»›ng dáº«n triá»ƒn khai](architecture/)
- [ðŸŽ¯ HÆ°á»›ng dáº«n trá»±c quan vá» cá»•ng Dremio](architecture/dremio-ports-visual.md) â­ Má»šI

---

## NgÃ´n ngá»¯ cÃ³ sáºµn

| NgÃ´n ngá»¯ | MÃ£ | TÃ i liá»‡u |
|--------|------|---------------|
| Tiáº¿ng Anh | VN | [README.md](../../../README.md) |
| Tiáº¿ng PhÃ¡p | VN | [docs/i18n/fr/](../fr/README.md) |
| TÃ¢y Ban Nha | ES | [docs/i18n/es/](../es/README.md) |
| Tiáº¿ng Bá»“ ÄÃ o Nha | PT | [docs/i18n/pt/](../pt/README.md) |
| Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© | AR | [docs/i18n/ar/](../ar/README.md) |
| ä¸­æ–‡ | CN | [docs/i18n/cn/](../cn/README.md) |
| æ—¥æœ¬èªž | JP | [docs/i18n/jp/](../jp/README.md) |
| Ð ÑƒÑÑÐºÐ¸Ð¹ | VÆ°Æ¡ng quá»‘c Anh | [docs/i18n/ru/](../ru/README.md) |

---

## á»¦ng há»™

Äá»ƒ Ä‘Æ°á»£c há»— trá»£ ká»¹ thuáº­t:
- TÃ i liá»‡u: [README main](../../../README.md)
- TrÃ¬nh theo dÃµi sá»± cá»‘: Sá»± cá»‘ GitHub
- Diá»…n Ä‘Ã n cá»™ng Ä‘á»“ng: Tháº£o luáº­n GitHub
- Email: support@example.com

---

**[Quay láº¡i tÃ i liá»‡u chÃ­nh](../../../README.md)**
