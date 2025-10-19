# Panduan Visual Pelabuhan Dremio

**Versi**: 3.2.3  
**Terakhir diperbarui**: 16 Oktober 2025  
**Bahasa**: Prancis

---

## Ikhtisar 3 Port Dremio

§§§KODE_0§§§

---

## Arsitektur Terperinci dari Proxy PostgreSQL

### Alur Koneksi Pelanggan → Dremio

§§§KODE_1§§§

---

## Perbandingan Kinerja

### Tolok Ukur: Pemindaian data sebesar 100 GB

§§§KODE_2§§§

### Kecepatan Data

§§§KODE_3§§§

### Latensi Kueri Sederhana

| Protokol | Pelabuhan | Latensi Rata-Rata | Overhead Jaringan |
|---------------|------|-----------------|-----------------|
| **API REST** | 9047 | 50-100 md | JSON (bertele-tele) |
| **Proksi PostgreSQL** | 31010 | 20-50 md | Protokol Kawat (kompak) |
| **Penerbangan Panah** | 32010 | 5-10 md | Apache Arrow (kolom biner) |

---

## Kasus Penggunaan berdasarkan Port

### Pelabuhan 9047 - API REST

§§§KODE_4§§§

### Pelabuhan 31010 - Proksi PostgreSQL

§§§KODE_5§§§

### Port 32010 - Penerbangan Panah

§§§KODE_6§§§

---

## Pohon Keputusan: Port Mana yang Digunakan?

§§§KODE_7§§§

---

## Contoh Koneksi Proxy PostgreSQL

### 1. psql CLI

§§§KODE_8§§§

### 2. Konfigurasi DBeaver

§§§KODE_9§§§

### 3. Python dengan psycopg2

§§§KODE_10§§§

### 4. Java JDBC

§§§KODE_11§§§

### 5. Tali ODBC (DSN)

§§§KODE_12§§§

---

## Konfigurasi Docker Tulis

### Pemetaan Pelabuhan Dremio

§§§KODE_13§§§

### Pemeriksaan Pelabuhan

§§§KODE_14§§§

---

## Ringkasan Visual Cepat

### Sekilas tentang 3 Port

| Pelabuhan | Protokol | Kegunaan Utama | Kinerja | Kompatibilitas |
|------|----------|---------||-------------|---------------|
| **9047** | API REST | 🌐 Antarmuka Web, Admin | ⭐⭐Standar | ⭐⭐⭐ Universal |
| **31010** | Kawat PostgreSQL | 💼 Alat BI, Migrasi | ⭐⭐⭐ Bagus | ⭐⭐⭐ Luar Biasa |
| **32010** | Penerbangan Panah | ⚡ Produksi, dbt, Superset | ⭐⭐⭐⭐⭐ Maksimal | ⭐⭐ Terbatas |

### Matriks Seleksi

§§§KODE_15§§§

---

## Sumber Daya Tambahan

### Dokumentasi Terkait

- [Arsitektur - Komponen](./components.md) - Bagian "Proxy PostgreSQL untuk Dremio"
- [Panduan - Pengaturan Dremio](../guides/dremio-setup.md) - Bagian "Koneksi melalui Proxy PostgreSQL"
- [Konfigurasi - Dremio](../getting-started/configuration.md) - Parameter `dremio.conf`

### Tautan Resmi

- **Dokumentasi Dremio**: https://docs.dremio.com/
- **Protokol Kawat PostgreSQL**: https://www.postgresql.org/docs/current/protocol.html
- **Penerbangan Apache Arrow**: https://arrow.apache.org/docs/format/Flight.html

---

**Versi**: 3.2.3  
**Terakhir diperbarui**: 16 Oktober 2025  
**Status**: ✅ Selesai