# Dremio + dbt + OpenMetadata - Dokumentasi (Indonesia)

**Versi**: 3.2.5  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Bahasa**: Indonesia 🇮🇩

---

## 📚 Ikhtisar

Selamat datang di dokumentasi Indonesia untuk platform data Dremio + dbt + OpenMetadata. Dokumentasi ini menyediakan panduan komprehensif untuk pengaturan, konfigurasi, dan penggunaan platform.

---

## 🗺️ Struktur Dokumentasi

### 📐 Arsitektur

- **[Dremio Ports - Panduan Visual](./architecture/dremio-ports-visual.md)** ⭐ BARU!
  - Panduan visual lengkap untuk 3 port Dremio (9047, 31010, 32010)
  - Arsitektur detail PostgreSQL Proxy
  - Perbandingan performa dan benchmark
  - Kasus penggunaan dan pohon keputusan
  - Contoh koneksi: psql, DBeaver, Python, Java, ODBC
  - Konfigurasi Docker Compose
  - 456 baris | 8+ diagram Mermaid | 5 contoh kode

---

## 🌍 Bahasa yang Tersedia

Dokumentasi ini tersedia dalam beberapa bahasa:

- 🇫🇷 **[Français](../fr/README.md)** - Dokumentasi lengkap (22 file)
- 🇬🇧 **[English](../../../README.md)** - Dokumentasi lengkap (19 file)
- 🇪🇸 **[Español](../es/README.md)** - Panduan visual
- 🇵🇹 **[Português](../pt/README.md)** - Panduan visual
- 🇨🇳 **[中文](../cn/README.md)** - Panduan visual
- 🇯🇵 **[日本語](../jp/README.md)** - Panduan visual
- 🇷🇺 **[Русский](../ru/README.md)** - Panduan visual
- 🇸🇦 **[العربية](../ar/README.md)** - Panduan visual
- 🇩🇪 **[Deutsch](../de/README.md)** - Panduan visual
- 🇰🇷 **[한국어](../ko/README.md)** - Panduan visual
- 🇮🇳 **[हिन्दी](../hi/README.md)** - Panduan visual
- 🇮🇩 **[Indonesia](../id/README.md)** - Panduan visual ⭐ ANDA DI SINI
- 🇹🇷 **[Türkçe](../tr/README.md)** - Panduan visual
- 🇻🇳 **[Tiếng Việt](../vi/README.md)** - Panduan visual
- 🇮🇹 **[Italiano](../it/README.md)** - Panduan visual
- 🇳🇱 **[Nederlands](../nl/README.md)** - Panduan visual
- 🇵🇱 **[Polski](../pl/README.md)** - Panduan visual
- 🇸🇪 **[Svenska](../se/README.md)** - Panduan visual

---

## 🚀 Memulai Cepat

### Prasyarat

- Docker & Docker Compose
- Python 3.11+
- Git

### Instalasi

```bash
# Clone repository
git clone <repository-url>
cd dremiodbt

# Mulai layanan Docker
docker-compose up -d

# Buka Web UI
# Dremio: http://localhost:9047
# OpenMetadata: http://localhost:8585
```

Untuk instruksi instalasi detail, lihat [dokumentasi bahasa Inggris](../en/getting-started/installation.md).

---

## 📖 Sumber Daya Utama

### Dremio Ports - Referensi Cepat

| Port | Protokol | Penggunaan | Performa |
|------|-----------|------------|----------|
| **9047** | REST API | Web UI, Admin | ⭐⭐ Standar |
| **31010** | PostgreSQL Wire | Tools BI, Migrasi | ⭐⭐⭐ Baik |
| **32010** | Arrow Flight | dbt, Superset, Performa Tinggi | ⭐⭐⭐⭐⭐ Maksimal |

**→ [Panduan visual lengkap](./architecture/dremio-ports-visual.md)**

---

## 🔗 Tautan Eksternal

- **Dokumentasi Dremio**: https://docs.dremio.com/
- **Dokumentasi dbt**: https://docs.getdbt.com/
- **Dokumentasi OpenMetadata**: https://docs.open-metadata.org/
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

## 🤝 Berkontribusi

Kontribusi sangat diterima! Silakan lihat [panduan kontribusi](../en/CONTRIBUTING.md) kami.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](../../../LICENSE).

---

**Versi**: 3.2.5  
**Status**: ✅ Siap Produksi  
**Pembaruan Terakhir**: 16 Oktober 2025
