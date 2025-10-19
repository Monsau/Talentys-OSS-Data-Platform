# Memulai Platform Data

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16-10-2025  
**Bahasa**: Prancis

---

## Ringkasan

Tutorial ini memandu Anda melalui interaksi pertama Anda dengan platform data, mulai dari menghubungkan ke layanan hingga membangun saluran data pertama Anda dengan Airbyte, Dremio, dbt, dan Superset.

§§§KODE_0§§§

**Perkiraan waktu**: 60-90 menit

---

## Prasyarat

Sebelum memulai, pastikan bahwa:

- ✅ Semua layanan diinstal dan dijalankan
- ✅ Anda dapat mengakses antarmuka web
- ✅ Lingkungan virtual Python diaktifkan
- ✅ Pemahaman dasar tentang SQL

**Periksa apakah layanan berfungsi:**
§§§KODE_1§§§

---

## Langkah 1: Akses Semua Layanan

### URL Layanan

| Layanan | URL | Kredensial Default |
|---------|----------|---------|
| **Airbyte** | http://localhost:8000 | airbyte@example.com / kata sandi |
| **Dremio** | http://localhost:9047 | admin/admin123 |
| **Superset** | http://localhost:8088 | admin / admin |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |

### Koneksi Pertama

**Bita Udara:**
1. Buka http://localhost:8000
2. Selesaikan wizard pengaturan
3. Tetapkan nama ruang kerja: “Produksi”
4. Ganti preferensi (konfigurasi selanjutnya dimungkinkan)

**Dremio:**
1. Buka http://localhost:9047
2. Buat pengguna administrator pada akses pertama:
   - Nama pengguna: `admin`
   - Email: `admin@example.com`
   - Kata sandi: `admin123`
3. Klik “Memulai”

**Superset:**
1. Buka http://localhost:8088
2. Masuk dengan kredensial default
3. Ubah kata sandi: Pengaturan → Info Pengguna → Atur Ulang Kata Sandi

---

## Langkah 2: Konfigurasikan Sumber Data Pertama Anda di Airbyte

### Buat Sumber PostgreSQL

**Skenario**: Ekstrak data dari database PostgreSQL.

1. **Navigasi ke Sumber**
   - Klik “Sumber” di menu sebelah kiri
   - Klik “+ Sumber baru”

2. **Pilih PostgreSQL**
   - Cari “PostgreSQL”
   - Klik pada konektor “PostgreSQL”.

3. **Konfigurasi Koneksi**
   §§§KODE_5§§§

4. **Uji dan Simpan**
   - Klik "Siapkan sumber"
   - Tunggu tes koneksi
   - Sumber dibuat ✅

### Buat Data Sampel (Opsional)

Jika Anda belum memiliki data apa pun, buatlah contoh tabel:

§§§KODE_6§§§

---

## Langkah 3: Konfigurasikan Tujuan MinIO S3

### Buat Tujuan

1. **Navigasi ke Tujuan**
   - Klik “Tujuan” di menu sebelah kiri
   - Klik “+ Tujuan baru”

2. **Pilih S3**
   - Cari “S3”
   - Klik pada konektor "S3".

3. **Konfigurasi MinIO sebagai S3**
   §§§KODE_7§§§

4. **Uji dan Simpan**
   - Klik “Siapkan tujuan”
   - Tes koneksi harus lulus ✅

---

## Langkah 4: Buat Koneksi Pertama Anda

### Tautan Sumber ke Tujuan

1. **Navigasi ke Koneksi**
   - Klik "Koneksi" di menu sebelah kiri
   - Klik “+ Koneksi baru”

2. **Pilih Sumber**
   - Pilih “Produksi PostgreSQL”
   - Klik “Gunakan sumber yang ada”

3. **Pilih Tujuan**
   - Pilih “Danau Data MinIO”
   - Klik “Gunakan tujuan yang ada”

4. **Konfigurasi Sinkronisasi**
   §§§KODE_8§§§

5. **Normalisasi**
   §§§KODE_9§§§

6. **Cadangkan dan Sinkronisasi**
   - Klik "Siapkan koneksi"
   - Klik “Sinkronkan sekarang” untuk menjalankan sinkronisasi pertama
   - Pantau kemajuan sinkronisasi

### Pantau Sinkronisasi

§§§KODE_10§§§

**Periksa status sinkronisasi:**
- Status seharusnya menunjukkan "Berhasil" (hijau)
- Catatan yang disinkronkan: ~11 (5 pelanggan + 6 pesanan)
- Lihat log untuk detailnya

---

## Langkah 5: Hubungkan Dremio ke MinIO

### Tambahkan Sumber S3 di Dremio

1. **Navigasi ke Sumber**
   - Buka http://localhost:9047
   - Klik “Tambahkan Sumber” (+ ikon)

2. **Pilih S3**
   - Pilih “Amazon S3”
   - Konfigurasikan sebagai MinIO:

§§§KODE_11§§§

3. **Uji dan Simpan**
   - Klik “Simpan”
   - Dremio akan menganalisis bucket MinIO

### Telusuri Data

1. **Navigasi ke sumber MinIOLake**
   - Kembangkan “MinIOLake”
   - Kembangkan ember "datalake".
   - Perluas folder "data mentah".
   - Lihat folder "produksi_publik".

2. **Pratinjau Data**
   - Klik pada folder “pelanggan”.
   - Klik pada file Parket
   - Klik “Pratinjau” untuk melihat data
   - Data harus cocok dengan PostgreSQL ✅

### Membuat Kumpulan Data Virtual

1. **Data Kueri**
   §§§KODE_12§§§

2. **Simpan sebagai VDS**
   - Klik "Simpan Tampilan Sebagai"
   - Nama: `vw_customers`
   - Spasi: `@admin` (spasi Anda)
   - Klik “Simpan”

3. **Format Data** (opsional)
   - Klik pada `vw_customers`
   - Gunakan antarmuka untuk mengganti nama kolom, mengubah tipe
   - Contoh: Ganti nama `customer_id` menjadi `id`

---

## Langkah 6: Buat Templat dbt

### Inisialisasi Proyek dbt

§§§KODE_18§§§

### Buat Definisi Sumber

**Berkas**: `dbt/models/sources.yml`

§§§KODE_20§§§

### Membuat Templat Pementasan

**Berkas**: `dbt/models/staging/stg_customers.sql`

§§§KODE_22§§§

**Berkas**: `dbt/models/staging/stg_orders.sql`

§§§KODE_24§§§

### Membuat Templat Mart

**Berkas**: `dbt/models/marts/fct_customer_orders.sql`

§§§KODE_26§§§

### Jalankan Model dbt

§§§KODE_27§§§

### Periksa di Dremio

§§§KODE_28§§§

---

## Langkah 7: Buat Dasbor di Superset

### Tambahkan Basis Data Dremio

1. **Navigasi ke Database**
   - Buka http://localhost:8088
   - Klik “Data” → “Database”
   - Klik “+ Basis Data”

2. **Pilih Dremio**
   §§§KODE_29§§§

3. **Klik “Hubungkan”**

### Buat Kumpulan Data

1. **Navigasi ke Kumpulan Data**
   - Klik “Data” → “Kumpulan Data”
   - Klik “+ Kumpulan Data”

2. **Konfigurasi Kumpulan Data**
   §§§KODE_30§§§

3. **Klik “Buat Kumpulan Data dan Buat Bagan”**

### Buat Bagan

#### Bagan 1: Segmen Pelanggan (Diagram Melingkar)

§§§KODE_31§§§

#### Bagan 2: Pendapatan menurut Negara (Bagan Batang)

§§§KODE_32§§§

#### Bagan 3: Metrik Pelanggan (Jumlah Besar)

§§§KODE_33§§§

### Buat Dasbor

1. **Navigasi ke Dasbor**
   - Klik pada “Dasbor”
   - Klik “+ Dasbor”

2. **Konfigurasi Dasbor**
   §§§KODE_34§§§

3. **Tambahkan Grafik**
   - Seret dan lepas grafik yang dibuat
   - Atur dalam kotak:
     §§§KODE_35§§§

4. **Tambahkan Filter** (opsional)
   - Klik “Tambahkan Filter”
   - Filter berdasarkan: kode_negara
   - Terapkan ke semua grafik

5. **Simpan Dasbor**

---

## Langkah 8: Periksa Kelengkapan Pipeline

### Pengujian Ujung-ke-Ujung

§§§KODE_36§§§

### Tambahkan Data Baru

1. **Masukkan catatan baru di PostgreSQL**
   §§§KODE_37§§§

2. **Memicu sinkronisasi Airbyte**
   - Buka antarmuka Airbyte
   - Buka koneksi "PostgreSQL → MinIO"
   - Klik "Sinkronkan sekarang"
   - Tunggu sampai akhir ✅

3. **Jalankan dbt**
   §§§KODE_38§§§

4. **Segarkan Dasbor Superset**
   - Buka dasbor
   - Klik tombol "Segarkan".
   - Data baru akan muncul ✅

### Periksa Aliran Data

§§§KODE_39§§§

---

## Langkah 9: Otomatiskan Pipeline

### Jadwalkan Sinkronisasi Airbyte

Sudah dikonfigurasi untuk berjalan setiap 24 jam pada pukul 02:00.

Untuk mengedit:
1. Buka koneksi di Airbyte
2. Buka tab “Pengaturan”.
3. Perbarui “Frekuensi replikasi”
4. Simpan

### Jadwalkan Eksekusi dbt

**Opsi 1: Pekerjaan Cron (Linux)**
§§§KODE_40§§§

**Opsi 2: Skrip Python**

**Berkas**: `scripts/run_pipeline.py`
§§§KODE_42§§§

### Jadwalkan dengan Docker Compose

**Berkas**: `docker-compose.scheduler.yml`
§§§KODE_44§§§

---

## Langkah Selanjutnya

Selamat! Anda telah membangun saluran data menyeluruh yang lengkap. 🎉

### Pelajari Lebih Lanjut

1. **Airbyte Advanced** - [Panduan Integrasi Airbyte](../guides/airbyte-integration.md)
2. **Optimasi Dremio** - [Panduan Pengaturan Dremio](../guides/dremio-setup.md)
3. **Model dbt Kompleks** - [Panduan Pengembangan dbt](../guides/dbt-development.md)
4. **Dasbor Tingkat Lanjut** - [Panduan Dasbor Superset](../guides/superset-dashboards.md)
5. **Kualitas Data** - [Panduan Kualitas Data](../guides/data-quality.md)

### Pemecahan masalah

Jika Anda mempunyai masalah, lihat:
- [Panduan Mengatasi Masalah](../guides/troubleshooting.md)
- [Panduan Instalasi](installation.md#pemecahan masalah)
- [Panduan Konfigurasi](configuration.md)

---

## Ringkasan

Anda telah berhasil:

- ✅ Akses 7 layanan platform
- ✅ Konfigurasikan sumber Airbyte (PostgreSQL)
- ✅ Konfigurasikan tujuan Airbyte (MinIO S3)
- ✅ Buat koneksi Airbyte pertama Anda
- ✅ Hubungkan Dremio ke MinIO
- ✅ Buat templat dbt (pementasan + mart)
- ✅ Bangun Dasbor Superset
- ✅ Periksa aliran data ujung ke ujung
- ✅ Mengotomatiskan eksekusi pipeline

**Platform data Anda sekarang sudah beroperasi!** 🚀

---

**Versi Panduan Langkah Pertama**: 3.2.0  
**Terakhir Diperbarui**: 16-10-2025  
**Dikelola Oleh**: Tim Platform Data