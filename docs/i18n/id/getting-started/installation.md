# Panduan Instalasi

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16-10-2025  
**Bahasa**: Prancis

---

## Ringkasan

Panduan ini memberikan petunjuk langkah demi langkah untuk menginstal dan mengonfigurasi platform data lengkap, termasuk Airbyte, Dremio, dbt, Apache Superset, dan infrastruktur pendukung.

§§§KODE_0§§§

---

## Prasyarat

### Persyaratan Sistem

**Persyaratan Minimum:**
- **CPU**: 4 core (disarankan 8+)
- **RAM**: 8 GB (disarankan 16+ GB)
- **Ruang Disk**: tersedia 20 GB (disarankan 50+ GB)
- **Jaringan**: Koneksi Internet stabil untuk image Docker

**Sistem operasi:**
- Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- macOS (11.0+)
- Windows 10/11 dengan WSL2

### Perangkat Lunak yang Diperlukan

#### 1. Buruh pelabuhan

**Versi**: 20.10 atau lebih tinggi

**Fasilitas:**

**Linux:**
§§§KODE_1§§§

**macOS:**
§§§KODE_2§§§

**Jendela:**
§§§KODE_3§§§

#### 2. Penulisan Docker

**Versi**: 2.0 atau lebih tinggi

**Fasilitas:**

§§§KODE_4§§§

**Catatan**: Docker Desktop untuk macOS dan Windows menyertakan Docker Compose.

#### 3. Piton

**Versi**: 3.11 atau lebih tinggi

**Fasilitas:**

**Linux (Ubuntu/Debian):**
§§§KODE_5§§§

**macOS:**
§§§KODE_6§§§

**Jendela:**
§§§KODE_7§§§

**Verifikasi:**
§§§KODE_8§§§

#### 4. Git

**Fasilitas:**

§§§KODE_9§§§

**Verifikasi:**
§§§KODE_10§§§

---

## Langkah Instalasi

### Langkah 1: Kloning Repositori

§§§KODE_11§§§

**Struktur yang diharapkan:**
§§§KODE_12§§§

### Langkah 2: Konfigurasikan Lingkungan

#### Buat File Lingkungan

§§§KODE_13§§§

#### Variabel Lingkungan

**Konfigurasi Dasar:**
§§§KODE_14§§§

### Langkah 3: Instal Dependensi Python

#### Ciptakan Lingkungan Virtual

§§§KODE_15§§§

#### Persyaratan Penginstalan

§§§KODE_16§§§

**Paket kunci yang diinstal:**
- `pyarrow>=21.0.0` - Pelanggan Penerbangan Panah
- `pandas>=2.3.0` - Manipulasi data
- `dbt-core>=1.10.0` - Transformasi data
- `sqlalchemy>=2.0.0` - Konektivitas basis data
- `pyyaml>=6.0.0` - Manajemen konfigurasi

### Langkah 4: Mulai Layanan Docker

#### Mulai Layanan Utama

§§§KODE_22§§§

**Layanan dimulai:**
- PostgreSQL (pelabuhan 5432)
- Dremio (port 9047, 32010)
-Apache Superset (pelabuhan 8088)
- MinIO (port 9000, 9001)
- Pencarian elastis (pelabuhan 9200)

#### Mulai Airbyte (Tulis Terpisah)

§§§KODE_23§§§

**Layanan Airbyte dimulai:**
- Server Airbyte (pelabuhan 8001)
- UI Web Airbyte (pelabuhan 8000)
- Pekerja Airbyte
- Airbyte Sementara
- Basis Data Airbyte

#### Periksa Status Layanan

§§§KODE_24§§§

---

## Verifikasi

### Langkah 5: Periksa Layanan

#### 1. PostgreSQL

§§§KODE_25§§§

**Hasil yang diharapkan:**
§§§KODE_26§§§

#### 2. Dremio

**Antarmuka Web:**
§§§KODE_27§§§

**Koneksi pertama:**
- Nama pengguna: `admin`
- Kata sandi: `admin123`
- Anda akan diminta untuk membuat akun administrator pada akses pertama

**Uji koneksi:**
§§§KODE_30§§§

#### 3. Airbyte

**Antarmuka Web:**
§§§KODE_31§§§

**Pengidentifikasi default:**
- Email: `airbyte@example.com`
- Kata sandi: `password`

**Uji API:**
§§§KODE_34§§§

**Respon yang diharapkan:**
§§§KODE_35§§§

#### 4.Apache Superset

**Antarmuka Web:**
§§§KODE_36§§§

**Pengidentifikasi default:**
- Nama pengguna: `admin`
- Kata sandi: `admin`

**Uji koneksi:**
§§§KODE_39§§§

#### 5.MinIO

**UI Konsol:**
§§§KODE_40§§§

**Kredensial:**
- Nama pengguna: `minioadmin`
- Kata sandi: `minioadmin123`

**Uji API S3:**
§§§KODE_43§§§

#### 6. Pencarian elastis

**Uji koneksi:**
§§§KODE_44§§§

**Respon yang diharapkan:**
§§§KODE_45§§§

### Langkah 6: Jalankan Pemeriksaan Kesehatan

§§§KODE_46§§§

**Hasil yang diharapkan:**
§§§KODE_47§§§

---

## Konfigurasi Pasca Instalasi

### 1. Inisialisasi Dremio

§§§KODE_48§§§

**Membuat:**
- Pengguna admin
- Sumber default (PostgreSQL, MinIO)
- Contoh kumpulan data

### 2. Inisialisasi Superset

§§§KODE_49§§§

### 3. Konfigurasi dbt

§§§KODE_50§§§

### 4. Konfigurasikan Airbyte

**Melalui Antarmuka Web (http://localhost:8000):**

1. Selesaikan wizard pengaturan
2. Konfigurasikan sumber pertama (misal: PostgreSQL)
3. Konfigurasikan tujuan (misal: MinIO S3)
4. Buat koneksi
5. Jalankan sinkronisasi pertama

**Melalui API:**
§§§KODE_51§§§

---

## Struktur Direktori Setelah Instalasi

§§§KODE_52§§§

---

## Pemecahan masalah

### Masalah Umum

#### 1. Port Sudah Digunakan

**Kesalahan:**
§§§KODE_53§§§

**Larutan:**
§§§KODE_54§§§

#### 2. Memori Tidak Cukup

**Kesalahan:**
§§§KODE_55§§§

**Larutan:**
§§§KODE_56§§§

#### 3. Layanan Tidak Dimulai

**Periksa log:**
§§§KODE_57§§§

#### 4. Masalah Jaringan

**Setel ulang jaringan Docker:**
§§§KODE_58§§§

#### 5. Masalah Izin (Linux)

**Larutan:**
§§§KODE_59§§§

---

## Penghapusan instalasi

### Hentikan Layanan

§§§KODE_60§§§

### Hapus Data (Opsional)

§§§KODE_61§§§

### Hapus Gambar Docker

§§§KODE_62§§§

---

## Langkah Selanjutnya

Setelah instalasi berhasil:

1. **Konfigurasi Sumber Data** - Lihat [Panduan Konfigurasi](configuration.md)
2. **Tutorial Langkah Pertama** - Lihat [Langkah Pertama](first-steps.md)
3. **Konfigurasi Airbyte** - Lihat [Panduan Integrasi Airbyte](../guides/airbyte-integration.md)
4. **Pengaturan Dremio** - Lihat [Panduan Pengaturan Dremio](../guides/dremio-setup.md)
5. **Membuat Model dbt** - Lihat [Panduan Pengembangan dbt](../guides/dbt-development.md)
6. **Membuat Dasbor** - Lihat [Panduan Dasbor Superset](../guides/superset-dashboards.md)

---

## Mendukung

Untuk masalah instalasi:

- **Dokumentasi**: [Panduan Mengatasi Masalah](../guides/troubleshooting.md)
- **Masalah GitHub**: https://github.com/your-org/dremiodbt/issues
- **Komunitas**: https://github.com/your-org/dremiodbt/discussions

---

**Versi Panduan Instalasi**: 3.2.0  
**Terakhir Diperbarui**: 16-10-2025  
**Dikelola Oleh**: Tim Platform Data