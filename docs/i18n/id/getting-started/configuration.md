# Panduan Pengaturan

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16-10-2025  
**Bahasa**: Prancis

---

## Ringkasan

Panduan ini mencakup konfigurasi semua komponen platform termasuk Airbyte, Dremio, dbt, Apache Superset, PostgreSQL, MinIO dan Elasticsearch. Konfigurasi yang tepat memastikan kinerja, keamanan, dan integrasi antar layanan yang optimal.

§§§KODE_0§§§

---

## File Konfigurasi

### File Konfigurasi Utama

§§§KODE_1§§§

---

## Variabel Lingkungan

### Pengaturan Dasar

Buat atau edit file `.env` di root proyek:

§§§KODE_3§§§

### Praktik Keamanan yang Baik

**Buat kata sandi yang aman:**
§§§KODE_4§§§

**Jangan pernah memasukkan data sensitif:**
§§§KODE_5§§§

---

## Konfigurasi Layanan

### 1. Konfigurasi PostgreSQL

#### Pengaturan Koneksi

**Berkas**: `config/postgres.conf`

§§§KODE_7§§§

#### Membuat Database

§§§KODE_8§§§

### 2. Pengaturan Dremio

#### Pengaturan Memori

**Berkas**: `config/dremio.conf`

§§§KODE_10§§§

#### Mengonfigurasi Sumber Data

§§§KODE_11§§§

### 3. Pengaturan Airbyte

#### Pengaturan Ruang Kerja

**Berkas**: `config/airbyte/config.yaml`

§§§KODE_13§§§

#### Konfigurasi Sumber Saat Ini

**Sumber PostgreSQL:**
§§§KODE_14§§§

**Tujuan S3 (MinIO):**
§§§KODE_15§§§

### 4. pengaturan dbt

#### Konfigurasi Proyek

**Berkas**: `dbt/dbt_project.yml`

§§§KODE_17§§§

#### Konfigurasi Profil

**Berkas**: `dbt/profiles.yml`

§§§KODE_19§§§

### 5. Konfigurasi Superset Apache

#### Pengaturan Aplikasi

**Berkas**: `config/superset_config.py`

§§§KODE_21§§§

### 6. Konfigurasi MinIO

#### Konfigurasi Keranjang

§§§KODE_22§§§

#### Kebijakan Akses

§§§KODE_23§§§

### 7. Penyiapan Elasticsearch

**Berkas**: `config/elasticsearch.yml`

§§§KODE_25§§§

---

## Konfigurasi Jaringan

### Jaringan Docker

**File**: `docker-compose.yml` (bagian jaringan)

§§§KODE_27§§§

### Komunikasi antar Layanan

§§§KODE_28§§§

---

## Manajemen Volume

### Volume Persisten

**File**: `docker-compose.yml` (bagian volume)

§§§KODE_30§§§

### Strategi Cadangan

§§§KODE_31§§§

---

## Konfigurasi Otomatis

### Skrip Konfigurasi

**Berkas**: `scripts/configure_platform.py`

§§§KODE_33§§§

**Jalankan penyiapan:**
§§§KODE_34§§§

---

## Langkah Selanjutnya

Setelah pengaturan:

1. **Periksa Pengaturan** - Jalankan pemeriksaan kesehatan
2. **Langkah Pertama** - Lihat [Panduan Langkah Pertama](first-steps.md)
3. **Konfigurasi Airbyte** - Lihat [Integrasi Airbyte](../guides/airbyte-integration.md)
4. **Konfigurasi Dremio** - Lihat [Konfigurasi Dremio](../guides/dremio-setup.md)

---

**Versi Panduan Konfigurasi**: 3.2.0  
**Terakhir Diperbarui**: 16-10-2025  
**Dikelola Oleh**: Tim Platform Data