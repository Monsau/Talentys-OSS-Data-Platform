# æ•°æ®å¹³å°

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>


**ä¼ä¸šæ•°æ®æ¹–å±‹è§£å†³æ–¹æ¡ˆ**

**è¯­è¨€**ï¼šæ³•è¯­ï¼ˆFRï¼‰  
**ç‰ˆæœ¬**ï¼š3.3.1  
**æœ€åŽæ›´æ–°**ï¼š2025 å¹´ 10 æœˆ 19 æ—¥

---

ï¼ƒï¼ƒ æ¦‚è¿°

ç»“åˆäº† Dremioã€dbt å’Œ Apache Superset çš„ä¸“ä¸šæ•°æ®å¹³å°ï¼Œç”¨äºŽä¼ä¸šçº§æ•°æ®è½¬æ¢ã€è´¨é‡ä¿è¯å’Œå•†ä¸šæ™ºèƒ½ã€‚

è¯¥å¹³å°ä¸ºçŽ°ä»£æ•°æ®å·¥ç¨‹æä¾›äº†å®Œæ•´çš„è§£å†³æ–¹æ¡ˆï¼ŒåŒ…æ‹¬è‡ªåŠ¨åŒ–æ•°æ®ç®¡é“ã€è´¨é‡æµ‹è¯•å’Œäº¤äº’å¼ä»ªè¡¨æ¿ã€‚

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

## ä¸»è¦ç‰¹ç‚¹

- ä¸Ž Dremio åˆä½œçš„æ•°æ®æ¹–å±‹æž¶æž„
- ä½¿ç”¨ dbt è‡ªåŠ¨è½¬æ¢
- ä½¿ç”¨ Apache Superset çš„å•†ä¸šæ™ºèƒ½
- å…¨é¢çš„æ•°æ®è´¨é‡æµ‹è¯•
- é€šè¿‡ Arrow Flight å®žæ—¶åŒæ­¥

---

## å¿«é€Ÿå…¥é—¨æŒ‡å—

### å…ˆå†³æ¡ä»¶

- Docker 20.10 æˆ–æ›´é«˜ç‰ˆæœ¬
- Docker Compose 2.0 æˆ–æ›´é«˜ç‰ˆæœ¬
- Python 3.11 æˆ–æ›´é«˜ç‰ˆæœ¬
- è‡³å°‘ 8 GB RAM

ï¼ƒï¼ƒï¼ƒ è®¾æ–½

```bash
# Installer les dÃ©pendances
pip install -r requirements.txt

# DÃ©marrer les services
make up

# VÃ©rifier l'installation
make status

# ExÃ©cuter les tests de qualitÃ©
make dbt-test
```

---

ï¼ƒï¼ƒ å»ºç­‘å­¦

### ç³»ç»Ÿç»„ä»¶

|ç»„ä»¶|æ¸¯å£|æè¿° |
|----------------|------|-------------|
|å¾·é›·ç±³å¥¥ | 9047, 31010, 32010 |æ•°æ®æ¹–å±‹å¹³å°|
|æ•°æ®åº“æŠ€æœ¯ | - |æ•°æ®è½¬æ¢å·¥å…·|
|è¶…çº§ç»„ | 8088 |å•†ä¸šæ™ºèƒ½å¹³å°|
| PostgreSQL | 5432 |äº¤æ˜“æ•°æ®åº“|
|è¿·ä½ IO | 9000ã€9001 |å¯¹è±¡å­˜å‚¨ï¼ˆS3 å…¼å®¹ï¼‰|
|å¼¹æ€§æœç´¢ | 9200 | 9200æœç´¢ä¸Žåˆ†æžå¼•æ“Ž|

è¯¦ç»†çš„ç³»ç»Ÿè®¾è®¡è¯·å‚è§[æž¶æž„æ–‡æ¡£](architecture/)ã€‚

---

## æ–‡æ¡£

### å¯åŠ¨
- [å®‰è£…æŒ‡å—](å…¥é—¨/)
- [é…ç½®]ï¼ˆå…¥é—¨/ï¼‰
- [å…¥é—¨](å…¥é—¨/)

### ç”¨æˆ·æŒ‡å—
- [æ•°æ®å·¥ç¨‹](æŒ‡å—/)
- [ä»ªè¡¨æ¿çš„åˆ›å»º]ï¼ˆæŒ‡å—/ï¼‰
- [APIé›†æˆ](æŒ‡å—/)

### API æ–‡æ¡£
- [REST API å‚è€ƒ](api/)
- [èº«ä»½éªŒè¯](api/)
- [ä»£ç ç¤ºä¾‹](api/)

### æž¶æž„æ–‡æ¡£
- [ç³»ç»Ÿè®¾è®¡](æž¶æž„/)
- [æ•°æ®æµ](æž¶æž„/)
- [éƒ¨ç½²æŒ‡å—](æž¶æž„/)
- [ðŸŽ¯Dremio Ports è§†è§‰æŒ‡å—](architecture/dremio-ports-visual.md) â­ æ–°

---

## å¯ç”¨è¯­è¨€

|è¯­è¨€ |ä»£ç |æ–‡æ¡£ |
|--------|------|----------------|
|è‹±è¯­ | CN | [README.md](../../../README.md) |
|æ³•è¯­ | CN | [docs/i18n/fr/](../fr/README.md) |
|è¥¿ç­ç‰™è¯­ |è‹±è¯­ | [æ–‡æ¡£/i18n/es/](../es/README.md) |
|è‘¡è„ç‰™è¯­ | PT | [æ–‡æ¡£/i18n/pt/](../pt/README.md) |
|è¿ªæ‹œ |å¢žå¼ºçŽ°å®ž | [æ–‡æ¡£/i18n/ar/](../ar/README.md) |
| ä¸­æ–‡ |ä¸­æ–‡ | [docs/i18n/cn/](../cn/README.md) |
| æ—¥æœ¬è¯­ |æ—¥æœ¬ | [docs/i18n/jp/](../jp/README.md) |
| Ð ÑƒÑÑÐºÐ¸Ð¹ | ä¿„ç½—æ–¯è‹±å›½ | [docs/i18n/ru/](../ru/README.md) |

---

ï¼ƒï¼ƒ æ”¯æŒ

å¦‚éœ€æŠ€æœ¯æ´åŠ©ï¼š
- æ–‡æ¡£ï¼š[README main](../../../README.md)
- é—®é¢˜è·Ÿè¸ªå™¨ï¼šGitHub é—®é¢˜
- ç¤¾åŒºè®ºå›ï¼šGitHub è®¨è®º
- ç”µå­é‚®ä»¶ï¼šsupport@example.com

---

**[è¿”å›žä¸»æ–‡æ¡£](../../../README.md)**
