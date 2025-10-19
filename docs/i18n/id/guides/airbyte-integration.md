# Panduan Integrasi Airbyte

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Bahasa**: Prancis

---

## Ringkasan

Airbyte adalah platform integrasi data sumber terbuka yang menyederhanakan pemindahan data dari berbagai sumber ke tujuan. Panduan ini mencakup pengintegrasian Airbyte ke dalam platform data, mengonfigurasi konektor, dan membangun saluran data.

§§§KODE_0§§§

---

## Apa itu Airbyte?

### Fitur Utama

- **300+ Konektor Bawaan**: API, database, file, aplikasi SaaS
- **Sumber Terbuka**: Dihosting sendiri dengan kontrol data penuh
- **Ubah Pengambilan Data (CDC)**: Sinkronisasi data waktu nyata
- **Konektor Khusus**: Membangun konektor dengan Python atau CDK kode rendah
- **Normalisasi Data**: Ubah JSON mentah menjadi tabel terstruktur
- **Pemantauan & Peringatan**: Lacak status sinkronisasi dan kualitas data

### Arsitektur

§§§KODE_1§§§

---

## Fasilitas

### Mulai Cepat

Airbyte termasuk dalam platform. Mulailah dengan:

§§§KODE_2§§§

### Layanan Dimulai

| Layanan | Pelabuhan | Deskripsi |
|--------|------|-------------|
| **airbyte-webapp** | 8000 | Antarmuka pengguna web |
| **server-airbyte** | 8001 | Server API |
| **pekerja airbyte** | - | Mesin eksekusi pekerjaan |
| **airbyte-temporal** | 7233 | Orkestrasi alur kerja |
| **airbyte-db** | 5432 | Basis data metadata (PostgreSQL) |

### Akses Pertama

**Antarmuka Web:**
§§§KODE_3§§§

**Pengidentifikasi default:**
- **Email**: `airbyte@example.com`
- **Sandi**: `password`

**Ganti kata sandi** saat login pertama kali demi keamanan.

---

## Konfigurasi

### Panduan Konfigurasi

Pada akses pertama, selesaikan wizard konfigurasi:

1. **Preferensi Email**: Konfigurasikan notifikasi
2. **Data Residency**: Pilih lokasi penyimpanan data
3. **Statistik Penggunaan Anonim**: Menerima/menolak telemetri

### Pengaturan ruang kerja

Navigasikan ke **Pengaturan > Ruang Kerja**:

§§§KODE_6§§§

### Batasan Sumber Daya

**Berkas**: `config/airbyte/config.yaml`

§§§KODE_8§§§

---

## Konektor

### Konektor Sumber

#### Sumber PostgreSQL

**Kasus Penggunaan**: Ekstrak data dari database transaksional

**Konfigurasi:**

1. Navigasikan ke **Sumber > Sumber Baru**
2. Pilih **PostgreSQL**
3. Konfigurasikan koneksi:

§§§KODE_9§§§

**Uji Koneksi** → **Siapkan sumber**

#### Sumber REST API

**Kasus Penggunaan**: Ekstrak data dari API

**Konfigurasi:**

§§§KODE_10§§§

#### File Sumber (CSV)

**Kasus Penggunaan**: Impor file CSV

**Konfigurasi:**

§§§KODE_11§§§

#### Sumber Umum

| Sumber | Kasus Penggunaan | Dukungan CDC |
|--------|--------|-------------|
| **PostgreSQL** | Komik transaksional | ✅ Ya |
| **MySQL** | Komik transaksional | ✅ Ya |
| **MongoDB** | Dokumen NoSQL | ✅ Ya |
| **Tenaga Penjualan** | Data CRM | ❌ Tidak |
| **Google Spreadsheet** | Spreadsheet | ❌ Tidak |
| **Garis** | Data pembayaran | ❌ Tidak |
| **API REST** | API Khusus | ❌ Tidak |
| **S3** | Penyimpanan berkas | ❌ Tidak |

### Konektor Tujuan

#### Tujuan MinIO S3

**Kasus Penggunaan**: Menyimpan data mentah di data lake

**Konfigurasi:**

1. Navigasikan ke **Tujuan > Tujuan Baru**
2. Pilih **S3**
3. Konfigurasikan koneksi:

§§§KODE_12§§§

**Uji Koneksi** → **Siapkan tujuan**

#### Tujuan PostgreSQL

**Kasus Penggunaan**: Memuat data yang diubah untuk analisis

**Konfigurasi:**

§§§KODE_13§§§

#### Tujuan Dremio

**Kasus Penggunaan**: Memuat langsung ke data lakehouse

**Konfigurasi:**

§§§KODE_14§§§

---

## Koneksi

### Buat Koneksi

Koneksi menghubungkan sumber ke tujuan.

§§§KODE_15§§§

#### Langkah demi Langkah

1. **Navigasi ke Koneksi > Koneksi Baru**

2. **Pilih Sumber**: Pilih sumber yang dikonfigurasi (misal: PostgreSQL)

3. **Pilih Tujuan**: Pilih tujuan (misal: MinIO S3)

4. **Konfigurasi Sinkronisasi**:

§§§KODE_16§§§

5. **Konfigurasi Normalisasi** (opsional):

§§§KODE_17§§§

6. **Uji Koneksi** → **Siapkan koneksi**

### Mode Sinkronisasi

| Mode | Deskripsi | Kasus Penggunaan |
|------|-------------|-------------|
| **Penyegaran Penuh\| Timpa** | Ganti semua data | Tabel dimensi |
| **Penyegaran Penuh\| Tambahkan** | Tambahkan semua catatan | Pelacakan sejarah |
| **Tambahan\| Tambahkan** | Tambahkan catatan baru/diperbarui | Tabel fakta |
| **Tambahan\| Dikurangi** | Perbarui catatan yang ada | SCD Tipe 1 |

### Perencanaan

**Opsi Frekuensi:**
- **Manual**: Memicu secara manual
- **Setiap Jam**: Setiap jam
- **Harian**: Setiap 24 jam (sebutkan waktu)
- **Mingguan**: Hari-hari tertentu dalam seminggu
- **Cron**: Penjadwalan khusus (misal: `0 2 * * *`)

**Contoh Jadwal:**
§§§KODE_19§§§

---

## Transformasi Data

### Normalisasi Dasar

Airbyte menyertakan **Normalisasi Dasar** menggunakan dbt:

**Apa yang dia lakukan:**
- Mengonversi JSON bersarang menjadi tabel datar
- Membuat tabel `_airbyte_raw_*` (JSON mentah)
- Membuat tabel standar (terstruktur).
- Tambahkan kolom metadata (`_airbyte_emitted_at`, `_airbyte_normalized_at`)

**Contoh:**

**JSON mentah** (`_airbyte_raw_customers`):
§§§KODE_24§§§

**Tabel Standar:**

§§§KODE_25§§§:
§§§KODE_26§§§

§§§KODE_27§§§:
§§§KODE_28§§§

### Transformasi Khusus (dbt)

Untuk transformasi tingkat lanjut, gunakan dbt:

1. **Nonaktifkan Normalisasi Airbyte**
2. **Buat model dbt** tabel referensi `_airbyte_raw_*`
3. **Jalankan dbt** setelah sinkronisasi Airbyte

**Contoh model dbt:**
§§§KODE_30§§§

---

## Pemantauan

### Status Sinkronisasi

**Antarmuka Web Dasbor:**
- **Koneksi**: Lihat semua koneksi
- **Riwayat Sinkronisasi**: Pekerjaan sinkronisasi sebelumnya
- **Sync Logs**: Log terperinci per pekerjaan

**Indikator Status:**
- 🟢 **Berhasil**: Sinkronisasi berhasil diselesaikan
- 🔴 **Gagal**: Sinkronisasi gagal (periksa log)
- 🟡 **Berjalan**: Sinkronisasi sedang berlangsung
- ⚪ **Dibatalkan**: Sinkronisasi dibatalkan oleh pengguna

### Log

**Lihat log sinkronisasi:**
§§§KODE_31§§§

### Metrik

**Metrik Utama yang Harus Dipantau:**
- **Rekaman Tersinkronisasi**: Jumlah rekaman per sinkronisasi
- **Byte Tersinkronisasi**: Volume data yang ditransfer
- **Durasi Sinkronisasi**: Waktu yang dibutuhkan per sinkronisasi
- **Tingkat Kegagalan**: Persentase sinkronisasi yang gagal

**Metrik Ekspor:**
§§§KODE_32§§§

### Peringatan

**Konfigurasi peringatan** di **Pengaturan > Pemberitahuan**:

§§§KODE_33§§§

---

## Penggunaan API

### Otentikasi

§§§KODE_34§§§

### Panggilan API Umum

#### Daftar Sumber

§§§KODE_35§§§

#### Buat Koneksi

§§§KODE_36§§§

#### Sinkronisasi Pemicu

§§§KODE_37§§§

#### Dapatkan Status Pekerjaan

§§§KODE_38§§§

---

## Integrasi dengan Dremio

### Alur Kerja

§§§KODE_39§§§

### Langkah Konfigurasi

1. **Konfigurasi Airbyte untuk mengisi daya ke MinIO S3** (lihat di atas)

2. **Tambahkan sumber S3 di Dremio:**

§§§KODE_40§§§

3. **Meminta data Airbyte di Dremio:**

§§§KODE_41§§§

4. **Buat Kumpulan Data Virtual Dremio:**

§§§KODE_42§§§

5. **Penggunaan dalam model dbt:**

§§§KODE_43§§§

---

## Praktik Terbaik

### Pertunjukan

1. **Gunakan Sinkronisasi Tambahan** bila memungkinkan
2. **Jadwalkan sinkronisasi di luar jam sibuk**
3. **Gunakan format Parket** untuk kompresi yang lebih baik
4. **Partisi tabel besar** berdasarkan tanggal
5. **Pantau penggunaan sumber daya** dan sesuaikan batasnya

### Kualitas Data

1. **Aktifkan validasi data** di konektor sumber
2. **Gunakan kunci utama** untuk mendeteksi duplikat
3. **Konfigurasi peringatan** untuk kegagalan sinkronisasi
4. Metrik **Pantau kesegaran data**
5. **Menerapkan pengujian dbt** pada data mentah

### Keamanan

1. **Gunakan pengenal hanya-baca** untuk sumber
2. **Simpan rahasia** dalam variabel lingkungan
3. **Aktifkan SSL/TLS** untuk koneksi
4. **Perbarui pengenal Anda** secara berkala
5. **Audit log akses** secara berkala

### Optimasi Biaya

1. **Gunakan kompresi** (GZIP, SNAPPY)
2. **Hapus duplikat data** di sumbernya
3. **Arsipkan data lama** ke cold storage
4. **Pantau frekuensi sinkronisasi** vs persyaratan
5. **Bersihkan data sinkronisasi yang gagal**

---

## Pemecahan masalah

### Masalah Umum

#### Kegagalan Sinkronisasi: Batas Waktu Koneksi habis

**Gejala:**
§§§KODE_44§§§

**Larutan:**
§§§KODE_45§§§

#### Kesalahan Kehabisan Memori

**Gejala:**
§§§KODE_46§§§

**Larutan:**
§§§KODE_47§§§

#### Normalisasi Gagal

**Gejala:**
§§§KODE_48§§§

**Larutan:**
§§§KODE_49§§§

#### Performa Sinkronisasi Lambat

**Diagnosa:**
§§§KODE_50§§§

**Solusi:**
- Tingkatkan frekuensi sinkronisasi tambahan
- Tambahkan indeks ke bidang kursor
- Gunakan CDC untuk sumber real-time
- Menskalakan sumber daya pekerja

---

## Topik Lanjutan

### Konektor Khusus

Bangun konektor khusus dengan Airbyte CDK:

§§§KODE_51§§§

### Orkestrasi API

Otomatiskan Airbyte dengan Python:

§§§KODE_52§§§

---

## Sumber daya

### Dokumentasi

- **Dokumen Airbyte**: https://docs.airbyte.com
- **Katalog Konektor**: https://docs.airbyte.com/integrations
- **Referensi API**: https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html

### Komunitas

- **Slack**: https://slack.airbyte.io
- **GitHub**: https://github.com/airbytehq/airbyte
- **Forum**: https://discuss.airbyte.io

---

## Langkah Selanjutnya

Setelah mengonfigurasi Airbyte:

1. **Pengaturan Dremio** - [Panduan Pengaturan Dremio](dremio-setup.md)
2. **Membuat Model dbt** - [Panduan Pengembangan dbt](dbt-development.md)
3. **Membuat Dasbor** - [Panduan Dasbor Superset](superset-dashboards.md)
4. **Pantau Kualitas** - [Panduan Kualitas Data](data-quality.md)

---

**Versi Panduan Integrasi Airbyte**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Dikelola Oleh**: Tim Platform Data