# Panduan Konfigurasi Dremio

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Konfigurasi Awal](#konfigurasi awal)
3. [Konfigurasi Sumber Data](#konfigurasi-sumber-data)
4. [Kumpulan Data Virtual](#kumpulan data virtual)
5. [Pikiran (Kueri Akselerasi)](#kueri-akselerasi-pikiran)
6. [Kontrol Keamanan dan Akses](#kontrol keamanan dan akses)
7. [Optimasi Kinerja](#optimasi kinerja)
8. [Integrasi dengan dbt](#integrasi-dengan-dbt)
9. [Pemantauan dan Pemeliharaan](#pemantauan-dan-pemeliharaan)
10. [Pemecahan Masalah](#pemecahan masalah)

---

## Ringkasan

Dremio adalah platform data lakehouse yang menyediakan antarmuka terpadu untuk menanyakan data di berbagai sumber. Panduan ini mencakup semuanya mulai dari penyiapan awal hingga teknik pengoptimalan tingkat lanjut.

### Apa itu Dremio?

Dremio menggabungkan fleksibilitas data lake dengan kinerja gudang data:

- **Virtualisasi Data**: Mengkueri data tanpa memindahkan atau menyalinnya
- **Akselerasi Kueri**: Penyimpanan cache otomatis dengan refleksi
- **Analisis Layanan Mandiri**: Pengguna bisnis dapat langsung menjelajahi data
- **Standar SQL**: Tidak ada bahasa kueri kepemilikan
- **Apache Arrow**: Format kolom berperforma tinggi

### Fitur Utama

| Fitur | Deskripsi | Keuntungan |
|----------------|---------|---------|
| **Pikiran** | Akselerasi Kueri Cerdas | Kueri 10-100x lebih cepat |
| **Virtualisasi Data** | Pandangan terpadu tentang sumber | Tidak ada duplikasi data |
| **Penerbangan Panah** | Transfer data berkecepatan tinggi | 20-50x lebih cepat dari ODBC/JDBC |
| **Lapisan Semantik** | Nama bidang berorientasi bisnis | Analisis layanan mandiri |
| **Git untuk Data** | Kontrol versi kumpulan data | Kolaborasi dan kembalikan |

---

## Konfigurasi Awal

### Prasyarat

Sebelum memulai, pastikan Anda memiliki:
- Kontainer Dremio berjalan (lihat [Panduan Instalasi](../getting-started/installation.md))
- Akses ke sumber data (MinIO, PostgreSQL, dll.)
- Kredensial admin

### Koneksi Pertama

§§§KODE_0§§§

#### Langkah 1: Akses Antarmuka Dremio

Buka browser Anda dan navigasikan ke:
§§§KODE_1§§§

#### Langkah 2: Buat Akun Admin

Pada peluncuran pertama, Anda akan diminta untuk membuat akun admin:

§§§KODE_2§§§

**Catatan Keamanan**: Gunakan kata sandi yang kuat dengan minimal 12 karakter, termasuk huruf besar, huruf kecil, angka, dan karakter khusus.

#### Langkah 3: Pengaturan Awal

§§§KODE_3§§§

### File Konfigurasi

Konfigurasi Dremio dikelola melalui `dremio.conf`:

§§§KODE_5§§§

### Variabel Lingkungan

§§§KODE_6§§§

### Koneksi melalui Proksi PostgreSQL

Dremio memperlihatkan antarmuka yang kompatibel dengan PostgreSQL pada port 31010, memungkinkan alat yang kompatibel dengan PostgreSQL untuk terhubung tanpa modifikasi.

#### Arsitektur Koneksi Dremio

§§§KODE_7§§§

#### Alur Kueri melalui Proksi PostgreSQL

§§§KODE_8§§§

#### Konfigurasi Proksi

Proksi PostgreSQL diaktifkan secara otomatis di `dremio.conf`:

§§§KODE_10§§§

#### Koneksi dengan psql

§§§KODE_11§§§

#### Koneksi dengan DBeaver/pgAdmin

Pengaturan koneksi:

§§§KODE_12§§§

#### Saluran Koneksi

**JDBC:**
§§§KODE_13§§§

**ODBC (DSN):**
§§§KODE_14§§§

**Piton (psycopg2):**
§§§KODE_15§§§

#### Kapan Menggunakan Proksi PostgreSQL

§§§KODE_16§§§

| Skenario | Gunakan Proksi PostgreSQL | Gunakan Panah Penerbangan |
|---------|----------------------------|----------------------|
| **Alat BI Legacy** (tidak mendukung Arrow Flight) | ✅ Ya | ❌ Tidak |
| **Migrasi dari PostgreSQL** (kode JDBC/ODBC yang ada) | ✅ Ya | ❌ Tidak |
| **Produksi berkinerja tinggi** | ❌ Tidak | ✅ Ya (20-50x lebih cepat) |
| **Superset, dbt, alat modern** | ❌ Tidak | ✅ Ya |
| **Pengembangan/pengujian cepat** | ✅ Ya (akrab) | ⚠️ Keduanya oke |

#### Perbandingan Performa 3 Port

§§§KODE_17§§§

**Rekomendasi**: Gunakan proksi PostgreSQL (port 31010) untuk **kompatibilitas** dan Arrow Flight (port 32010) untuk **kinerja produksi**.

---

## Mengonfigurasi Sumber Data

### Tambahkan Sumber MinIO S3

MinIO adalah penyimpanan data lake utama Anda.

#### Langkah 1: Navigasikan ke Sumber

§§§KODE_18§§§

#### Langkah 2: Konfigurasikan Koneksi S3

§§§KODE_19§§§

#### Langkah 3: Uji Koneksi

§§§KODE_20§§§

**Hasil yang Diharapkan**:
§§§KODE_21§§§

### Tambahkan Sumber PostgreSQL

#### Pengaturan

§§§KODE_22§§§

§§§KODE_23§§§

### Tambahkan Sumber Elasticsearch

§§§KODE_24§§§

### Organisasi Sumber

§§§KODE_25§§§

---

## Kumpulan Data Virtual

Kumpulan data virtual memungkinkan Anda membuat tampilan data yang diubah dan dapat digunakan kembali.

### Membuat Kumpulan Data Virtual

#### Dari Editor SQL

§§§KODE_26§§§

**Simpan Lokasi**:
§§§KODE_27§§§

#### Dari Antarmuka

§§§KODE_28§§§

**Tangga**:
1. Navigasikan ke sumber MinIO
2. Telusuri ke `datalake/bronze/customers/`
3. Klik tombol “Format File”.
4. Periksa pola yang terdeteksi
5. Klik “Simpan” untuk mempromosikan ke kumpulan data

### Organisasi Kumpulan Data

Buat struktur logis dengan Spasi dan Folder:

§§§KODE_30§§§

### Lapisan Semantik

Tambahkan nama dan deskripsi berorientasi bisnis:

§§§KODE_31§§§

**Tambahkan Deskripsi**:
§§§KODE_32§§§

---

## Refleksi (Pertanyaan Akselerasi)

Refleksi adalah mekanisme caching cerdas Dremio yang secara signifikan meningkatkan kinerja kueri.

### Jenis Refleksi

#### 1. Refleksi Mentah

Simpan subset kolom untuk pengambilan cepat:

§§§KODE_33§§§

**Kasus Penggunaan**:
- Dasbor menanyakan kolom tertentu
- Laporan dengan subset kolom
- Pertanyaan eksplorasi

#### 2. Refleksi Agregasi

Perhitungan awal agregasi untuk hasil instan:

§§§KODE_34§§§

**Kasus Penggunaan**:
- Dasbor eksekutif
- Ringkasan laporan
- Analisis tren

### Refleksi Konfigurasi

§§§KODE_35§§§

#### Kebijakan Penyegaran

§§§KODE_36§§§

**Pilihan**:
- **Never Refresh**: Data statis (misalnya arsip sejarah)
- **Segarkan Setiap [1 jam]**: Pembaruan berkala
- **Refresh Saat Set Data Berubah**: Sinkronisasi Real-time

§§§KODE_37§§§

#### Kebijakan Kedaluwarsa

§§§KODE_38§§§

### Praktik yang Baik untuk Refleksi

#### 1. Mulailah dengan Kueri Bernilai Tinggi

Identifikasi kueri lambat dari riwayat:

§§§KODE_39§§§

#### 2. Ciptakan Refleksi yang Tertarget

§§§KODE_40§§§

#### 3. Pantau Refleksi Cakupan

§§§KODE_41§§§

### Dampak Pemikiran Kinerja

| Ukuran Kumpulan Data | Ketik Kueri | Tanpa Refleksi | Dengan Refleksi | Akselerasi |
|----------------|-------------|----------------|----------------|-------------|
| 1 juta baris | PILIH Sederhana | 500 md | 50 md | 10x |
| 10 juta baris | Agregasi | 15 detik | 200 md | 75x |
| 100 juta baris | Kompleks GABUNG | 2 menit | 1d | 120x |
| baris 1B | KELOMPOK BERDASARKAN | 10 menit | 5 detik | 120x |

---

## Keamanan dan Kontrol Akses

### Manajemen Pengguna

#### Buat Pengguna

§§§KODE_42§§§

§§§KODE_43§§§

#### Peran Pengguna

| Peran | Izin | Kasus Penggunaan |
|------|-------------|-------------|
| **Admin** | Akses penuh | Administrasi sistem |
| **Pengguna** | Kueri, buat kumpulan data pribadi | Analis, ilmuwan data |
| **Pengguna Terbatas** | Hanya kueri, bukan pembuatan kumpulan data | Pengguna bisnis, pemirsa |

### Izin ruang

§§§KODE_44§§§

**Jenis Izin**:
- **Tampilan**: Dapat melihat dan menanyakan kumpulan data
- **Modifikasi**: Dapat mengedit definisi set data
- **Kelola Hibah**: Dapat mengelola izin
- **Pemilik**: Kontrol penuh

**Contoh**:
§§§KODE_45§§§

### Keamanan Tingkat Jalur

Terapkan pemfilteran tingkat baris:

§§§KODE_46§§§

### Kolom Tingkat Keamanan

Sembunyikan kolom sensitif:

§§§KODE_47§§§

### Integrasi OAuth

§§§KODE_48§§§

---

## Optimasi Kinerja

### Teknik Optimasi Kueri

#### 1. Pemangkasan Partisi

§§§KODE_49§§§

#### 2. Pemangkasan Kolom

§§§KODE_50§§§

#### 3. Predikat Pushdown

§§§KODE_51§§§

#### 4. Gabung Optimasi

§§§KODE_52§§§

### Konfigurasi Memori

§§§KODE_53§§§

### Ukuran klaster

| Jenis Beban | Koordinator | Pelaksana | Jumlah Klaster |
|-------------|---------|------------|---------------|
| **Kecil** | 4 CPU, 16GB | 2x (8 CPU, 32 GB) | 20 CPU, 80GB |
| **Sedang** | 8 CPU, 32GB | 4x (16 CPU, 64GB) | 72 CPU, 288GB |
| **Besar** | 16 CPU, 64GB | 8x (32 CPU, 128GB) | CPU 272, 1088GB |

### Pemantauan Kinerja

§§§KODE_54§§§

---

## Integrasi dengan dbt

### Dremio sebagai Target dbt

Konfigurasikan `profiles.yml`:

§§§KODE_56§§§

### model dbt di Dremio

§§§KODE_57§§§

### Eksploitasi Refleksi di dbt

§§§KODE_58§§§

---

## Pemantauan dan Pemeliharaan

### Metrik Utama yang Harus Dipantau

§§§KODE_59§§§

### Tugas Pemeliharaan

#### 1. Segarkan Pikiran

§§§KODE_60§§§

#### 2. Bersihkan Data Lama

§§§KODE_61§§§

#### 3. Perbarui Statistik

§§§KODE_62§§§

---

## Pemecahan masalah

### Masalah Umum

#### Masalah 1: Performa Kueri Lambat

**Gejala**: Kueri membutuhkan waktu beberapa menit, bukan detik

**Diagnosa**:
§§§KODE_63§§§

**Solusi**:
1. Ciptakan pemikiran yang tepat
2. Tambahkan filter pemangkasan partisi
3. Meningkatkan memori pelaksana
4. Aktifkan Antrian Antrian

#### Masalah 2: Refleksi Tidak Terbangun

**Gejala**: Refleksi terjebak dalam kondisi “SEGAR”.

**Diagnosa**:
§§§KODE_64§§§

**Solusi**:
1. Periksa data sumber untuk perubahan skema
2. Periksa ruang disk yang cukup
3. Meningkatkan refleksi konstruksi batas waktu
4. Nonaktifkan dan aktifkan kembali refleksi

#### Masalah 3: Batas Waktu Koneksi

**Gejala**: Kesalahan “Batas waktu koneksi” saat menanyakan sumber

**Solusi**:
§§§KODE_65§§§

#### Masalah 4: Kurangnya Memori

**Gejala**: "OutOfMemoryError" di log

**Solusi**:
§§§KODE_66§§§

### Pertanyaan Diagnostik

§§§KODE_67§§§

---

## Ringkasan

Panduan komprehensif ini mencakup:

- **Konfigurasi Awal**: Konfigurasi pertama kali, pembuatan akun admin, file konfigurasi
- **Sumber Data**: Koneksi MinIO, PostgreSQL, dan Elasticsearch
- **Kumpulan Data Virtual**: Pembuatan tampilan transformasi yang dapat digunakan kembali dengan lapisan semantik
- **Refleksi**: Refleksi dan agregasi mentah untuk akselerasi kueri 10-100x
- **Keamanan**: Manajemen pengguna, izin ruang, keamanan tingkat baris/kolom
- **Kinerja**: Optimasi kueri, konfigurasi memori, ukuran cluster
- **integrasi dbt**: Gunakan Dremio sebagai target dbt dengan manajemen refleksi
- **Pemantauan**: Metrik utama, tugas pemeliharaan, permintaan diagnostik
- **Pemecahan Masalah**: Masalah umum dan solusinya

Poin-poin penting yang perlu diingat:
- Dremio menyediakan antarmuka SQL terpadu di semua sumber data
- Pemikiran penting untuk kinerja produksi
- Konfigurasi keamanan yang tepat memungkinkan analisis layanan mandiri
- Pemantauan rutin memastikan kinerja optimal

**Dokumentasi Terkait:**
- [Komponen Arsitektur](../architecture/components.md)
- [Aliran Data](../architecture/data-flow.md)
- [Panduan Pengembangan dbt](./dbt-development.md)
- [Integrasi Airbyte](./airbyte-integration.md)

---

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025