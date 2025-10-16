# Dremio + dbt + OpenMetadata - Dokümantasyon (Türkçe)

**Sürüm**: 3.2.5  
**Son Güncelleme**: 16 Ekim 2025  
**Dil**: Türkçe 🇹🇷

---

## 📚 Genel Bakış

Dremio + dbt + OpenMetadata veri platformu Türkçe dokümantasyonuna hoş geldiniz. Bu dokümantasyon, platformun kurulumu, yapılandırması ve kullanımı için kapsamlı kılavuzlar sağlar.

---

## 🗺️ Dokümantasyon Yapısı

### 📐 Mimari

- **[Dremio Portları - Görsel Kılavuz](./architecture/dremio-ports-visual.md)** ⭐ YENİ!
  - 3 Dremio portu (9047, 31010, 32010) için tam görsel kılavuz
  - PostgreSQL Proxy detaylı mimarisi
  - Performans karşılaştırmaları ve kıyaslamalar
  - Kullanım senaryoları ve karar ağacı
  - Bağlantı örnekleri: psql, DBeaver, Python, Java, ODBC
  - Docker Compose yapılandırması
  - 456 satır | 8+ Mermaid diyagramı | 5 kod örneği

---

## 🌍 Mevcut Diller

Bu dokümantasyon birçok dilde mevcuttur:

- 🇫🇷 **[Français](../fr/README.md)** - Tam dokümantasyon (22 dosya)
- 🇬🇧 **[English](../../../README.md)** - Tam dokümantasyon (19 dosya)
- 🇪🇸 **[Español](../es/README.md)** - Görsel kılavuzlar
- 🇵🇹 **[Português](../pt/README.md)** - Görsel kılavuzlar
- 🇨🇳 **[中文](../cn/README.md)** - Görsel kılavuzlar
- 🇯🇵 **[日本語](../jp/README.md)** - Görsel kılavuzlar
- 🇷🇺 **[Русский](../ru/README.md)** - Görsel kılavuzlar
- 🇸🇦 **[العربية](../ar/README.md)** - Görsel kılavuzlar
- 🇩🇪 **[Deutsch](../de/README.md)** - Görsel kılavuzlar
- 🇰🇷 **[한국어](../ko/README.md)** - Görsel kılavuzlar
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Görsel kılavuzlar
- 🇮🇩 **[Indonesia](../id/README.md)** - Görsel kılavuzlar
- 🇹🇷 **[Türkçe](../tr/README.md)** - Görsel kılavuzlar ⭐ BURADASıNıZ
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Görsel kılavuzlar
- 🇮🇹 **[Italiano](../it/README.md)** - Görsel kılavuzlar
- 🇳🇱 **[Nederlands](../nl/README.md)** - Görsel kılavuzlar
- 🇵🇱 **[Polski](../pl/README.md)** - Görsel kılavuzlar
- 🇸🇪 **[Svenska](../se/README.md)** - Görsel kılavuzlar

---

## 🚀 Hızlı Başlangıç

### Önkoşullar

- Docker & Docker Compose
- Python 3.11+
- Git

### Kurulum

```bash
# Repository'yi klonlayın
git clone <repository-url>
cd dremiodbt

# Docker servislerini başlatın
docker-compose up -d

# Web UI'yi açın
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

Ayrıntılı kurulum talimatları için [İngilizce dokümantasyona](../en/getting-started/installation.md) bakın.

---

## 📖 Ana Kaynaklar

### Dremio Portları - Hızlı Referans

| Port | Protokol | Kullanım | Performans |
|------|-----------|------------|----------|
| **9047** | REST API | Web UI, Yönetim | ⭐⭐ Standart |
| **31010** | PostgreSQL Wire | BI Araçları, Göç | ⭐⭐⭐ İyi |
| **32010** | Arrow Flight | dbt, Superset, Yüksek Performans | ⭐⭐⭐⭐⭐ Maksimum |

**→ [Tam görsel kılavuz](./architecture/dremio-ports-visual.md)**

---

## 🔗 Harici Bağlantılar

- **Dremio Dokümantasyonu**: https://docs.dremio.com/
- **dbt Dokümantasyonu**: https://docs.getdbt.com/
- **OpenMetadata Dokümantasyonu**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Katkıda Bulunma

Katkılar memnuniyetle karşılanır! Lütfen [katkı kılavuzumuza](../en/CONTRIBUTING.md) bakın.

---

## 📄 Lisans

Bu proje [MIT Lisansı](../../../LICENSE) altında lisanslanmıştır.

---

**Sürüm**: 3.2.5  
**Durum**: ✅ Üretime Hazır  
**Son Güncelleme**: 16 Ekim 2025
