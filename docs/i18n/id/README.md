# Platform data

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>


**Solusi data lakehouse perusahaan**

**Bahasa**: Prancis (FR)  
**Versi**: 3.3.1  
**Terakhir diperbarui**: 19 Oktober 2025

---

## Ringkasan

Platform data profesional yang menggabungkan Dremio, dbt, dan Apache Superset untuk transformasi data tingkat perusahaan, jaminan kualitas, dan intelijen bisnis.

Platform ini memberikan solusi lengkap untuk rekayasa data modern, termasuk jalur data otomatis, pengujian kualitas, dan dasbor interaktif.

Â§Â§Â§KODE_0Â§Â§Â§

---

## Fitur Utama

- Arsitektur rumah danau data dengan Dremio
- Transformasi otomatis dengan dbt
- Intelijen bisnis dengan Apache Superset
- Pengujian kualitas data yang komprehensif
- Sinkronisasi real-time melalui Arrow Flight

---

## Panduan Memulai Cepat

### Prasyarat

- Docker 20.10 atau lebih tinggi
- Docker Tulis 2.0 atau lebih tinggi
- Python 3.11 atau lebih tinggi
- RAM minimal 8 GB

### Fasilitas

Â§Â§Â§KODE_1Â§Â§Â§

---

## Arsitektur

### Komponen sistem

| Komponen | Pelabuhan | Deskripsi |
|---------------|------|-------------|
| Dremio | 9047, 31010, 32010 | Platform rumah danau data |
| dbt | - | Alat Transformasi Data |
| Superset | 8088 | Platform Intelijen Bisnis |
| PostgreSQL | 5432 | Basis data transaksional |
| MiniO | 9000, 9001 | Penyimpanan objek (kompatibel dengan S3) |
| Pencarian elastis | 9200 | Mesin pencari dan analisis |

Lihat [dokumentasi arsitektur](arsitektur/) untuk desain sistem terperinci.

---

## Dokumentasi

### Rintisan
- [Panduan Instalasi](memulai/)
- [Konfigurasi](memulai/)
- [Memulai](memulai/)

### Panduan pengguna
- [Rekayasa data](panduan/)
- [Pembuatan dasbor](panduan/)
- [integrasi API](panduan/)

### Dokumentasi API
- [Referensi REST API](api/)
- [Otentikasi](api/)
- [Contoh kode](api/)

### Dokumentasi arsitektur
- [Desain sistem](arsitektur/)
- [Aliran data](arsitektur/)
- [Panduan penerapan](arsitektur/)
- [ðŸŽ¯ Panduan Visual Dremio Ports](arsitektur/dremio-ports-visual.md) â­ BARU

---

## Bahasa yang tersedia

| Bahasa | Kode | Dokumentasi |
|--------|------|---------------|
| Bahasa Inggris | EN | [README.md](../../../README.md) |
| Perancis | EN | [docs/i18n/fr/](../fr/README.md) |
| Spanyol | ES | [docs/i18n/es/](../es/README.md) |
| Portugis | PT | [docs/i18n/pt/](../pt/README.md) |
| Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© | AR | [docs/i18n/ar/](../ar/README.md) |
| ä¸­æ–‡ | CN | [docs/i18n/cn/](../cn/README.md) |
| æ—¥æœ¬èªž | JP | [docs/i18n/jp/](../jp/README.md) |
| Ð ÑƒÑÑÐºÐ¸Ð¹ | Inggris | [docs/i18n/ru/](../ru/README.md) |

---

## Mendukung

Untuk bantuan teknis:
- Dokumentasi: [README utama](../../../README.md)
- Pelacak Masalah: Masalah GitHub
- Forum komunitas: Diskusi GitHub
- Email: support@example.com

---

**[Kembali ke dokumentasi utama](../../../README.md)**
