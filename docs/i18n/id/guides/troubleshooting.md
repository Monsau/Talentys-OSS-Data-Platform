# Panduan Mengatasi Masalah

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Pendekatan pemecahan masalah umum](#pendekatan-pemecahan masalah umum)
3. [Masalah Airbyte](#masalah-airbyte)
4. [Masalah Dremio](#masalah-dremio)
5. [masalah dbt](#masalah-dbt)
6. [Masalah Superset](#masalah-superset)
7. [Masalah PostgreSQL](#masalah-postgresql)
8. [Masalah MinIO](#masalah minio)
9. [Masalah Elasticsearch](#elasticsearch-issues)
10. [Jaringan dan Konektivitas](#jaringan-dan-konektivitas)
11. [Masalah kinerja](#masalah-kinerja)
12. [Masalah kualitas data](#masalah-kualitas data)

---

## Ringkasan

Panduan pemecahan masalah komprehensif ini membantu Anda mendiagnosis dan menyelesaikan masalah umum di seluruh komponen platform. Masalah disusun berdasarkan komponen yang memiliki gejala, diagnosis, dan solusi yang jelas.

### Metodologi Pemecahan Masalah

§§§KODE_0§§§

---

## Pendekatan pemecahan masalah umum

### Langkah 1: Periksa status layanan

§§§KODE_1§§§

### Langkah 2: Periksa log

§§§KODE_2§§§

### Langkah 3: Periksa konektivitas jaringan

§§§KODE_3§§§

### Langkah 4: Periksa penggunaan sumber daya

§§§KODE_4§§§

### Perbaikan cepat umum

§§§KODE_5§§§

---

## Masalah Airbyte

### Masalah 1: Antarmuka Airbyte tidak dimuat

**Gejala** :
- Browser menampilkan "Tidak dapat terhubung" atau batas waktu habis
- URL: `http://localhost:8000` tidak merespons

**Diagnosa**:
§§§KODE_7§§§

**Solusi**:

1. **Periksa apakah port tidak digunakan**:
   §§§KODE_8§§§

2. **Mulai Ulang Kontainer Airbyte**:
   §§§KODE_9§§§

3. **Periksa apakah server dalam keadaan sehat**:
   §§§KODE_10§§§

### Masalah 2: Sinkronisasi gagal dengan "Batas Waktu Koneksi"

**Gejala** :
- Tugas sinkronisasi langsung gagal atau hang
- Kesalahan: "Batas waktu koneksi" atau "Tidak dapat terhubung ke sumber"

**Diagnosa**:
§§§KODE_11§§§

**Solusi**:

1. **Periksa pengidentifikasi sumber**:
   §§§KODE_12§§§

2. **Tambahkan batas waktu**:
   §§§KODE_13§§§

3. **Periksa jaringan**:
   §§§KODE_14§§§

### Masalah 3: Kehabisan memori selama sinkronisasi

**Gejala** :
- Pekerja kontainer mogok selama sinkronisasi besar
- Kesalahan: "OutOfMemoryError" atau "Java heap space"

**Diagnosa**:
§§§KODE_15§§§

**Solusi**:

1. **Meningkatkan memori pekerja**:
   §§§KODE_16§§§

2. **Mengurangi ukuran batch**:
   §§§KODE_17§§§

3. **Gunakan sinkronisasi tambahan**:
   §§§KODE_18§§§

### Masalah 4: Data tidak muncul di tujuan

**Gejala** :
- Sinkronisasi berhasil diselesaikan
- Tidak ada kesalahan dalam log
- Data tidak ada di MinIO/tujuan

**Diagnosa**:
§§§KODE_19§§§

**Solusi**:

1. **Periksa konfigurasi tujuan**:
   §§§KODE_20§§§

2. **Periksa normalisasi**:
   §§§KODE_21§§§

3. **Verifikasi manual**:
   §§§KODE_22§§§

---

## Masalah Dremio

### Masalah 1: Tidak dapat terhubung ke antarmuka Dremio

**Gejala** :
- Browser menunjukkan kesalahan koneksi di `http://localhost:9047`

**Diagnosa**:
§§§KODE_24§§§

**Solusi**:

1. **Tunggu hingga startup selesai** (mungkin memerlukan waktu 2-3 menit):
   §§§KODE_25§§§

2. **Meningkatkan memori**:
   §§§KODE_26§§§

3. **Bersihkan data Dremio** (⚠️ mengatur ulang konfigurasi):
   §§§KODE_27§§§

### Masalah 2: "Sumber Offline" untuk MinIO

**Gejala** :
- Sumber MinIO menampilkan indikator “Offline” berwarna merah
- Kesalahan: "Tidak dapat terhubung ke sumber"

**Diagnosa**:
§§§KODE_28§§§

**Solusi**:

1. **Periksa titik akhir MinIO**:
   §§§KODE_29§§§

2. **Periksa kredensial**:
   §§§KODE_30§§§

3. **Segarkan metadata**:
   §§§KODE_31§§§

### Masalah 3: Performa kueri lambat

**Gejala** :
- Kueri membutuhkan waktu 10+ detik
- Dasbor lambat dimuat

**Diagnosa**:
§§§KODE_32§§§

**Solusi**:

1. **Buat refleksi**:
   §§§KODE_33§§§

2. **Tambahkan filter partisi**:
   §§§KODE_34§§§

3. **Meningkatkan memori pelaksana**:
   §§§KODE_35§§§

### Masalah 4: Refleksi tidak terbangun

**Gejala** :
- Refleksi tetap terjebak dalam keadaan "REFRESHING".
- Tidak pernah berakhir

**Diagnosa**:
§§§KODE_36§§§

**Solusi**:

1. **Nonaktifkan dan aktifkan kembali**:
   §§§KODE_37§§§

2. **Periksa data sumber**:
   §§§KODE_38§§§

3. **Tambahkan batas waktu**:
   §§§KODE_39§§§

---

## masalah dbt

### Masalah 1: "Kesalahan Koneksi" saat menjalankan dbt

**Gejala** :
- `dbt debug` gagal
- Kesalahan: "Tidak dapat terhubung ke Dremio"

**Diagnosa**:
§§§KODE_41§§§

**Solusi**:

1. **Periksa profiles.yml**:
   §§§KODE_42§§§

2. **Uji konektivitas Dremio**:
   §§§KODE_43§§§

3. **Pasang adaptor Dremio**:
   §§§KODE_44§§§

### Masalah 2: Model gagal dibuat

**Gejala** :
- `dbt run` gagal untuk model tertentu
- Kesalahan kompilasi atau eksekusi SQL

**Diagnosa**:
§§§KODE_46§§§

**Solusi**:

1. **Periksa sintaks model**:
   §§§KODE_47§§§

2. **Uji dulu di IDE SQL**:
   §§§KODE_48§§§

3. **Periksa dependensi**:
   §§§KODE_49§§§

### Masalah 3: Tes gagal

**Gejala** :
- `dbt test` melaporkan kegagalan
- Masalah kualitas data terdeteksi

**Diagnosa**:
§§§KODE_51§§§

**Solusi**:

1. **Perbaiki data sumber**:
   §§§KODE_52§§§

2. **Sesuaikan ambang batas pengujian**:
   §§§KODE_53§§§

3. **Selidiki akar permasalahannya**:
   §§§KODE_54§§§

### Masalah 4: Model inkremental tidak berfungsi

**Gejala** :
- Model inkremental dibangun kembali sepenuhnya setiap kali dijalankan
- Tidak ada perilaku tambahan

**Diagnosa**:
§§§KODE_55§§§

**Solusi**:

1. **Tambahkan persyaratan sistem**:
   §§§KODE_56§§§

2. **Tambahkan logika tambahan**:
   §§§KODE_57§§§

3. **Paksa penyegaran penuh satu kali**:
   §§§KODE_58§§§

---

## Masalah Superset

### Masalah 1: Tidak dapat terhubung ke Superset

**Gejala** :
- Halaman login menampilkan "Kredensial tidak valid"
- Pasangan admin/admin default tidak berfungsi

**Diagnosa**:
§§§KODE_59§§§

**Solusi**:

1. **Setel ulang kata sandi admin**:
   §§§KODE_60§§§

2. **Buat pengguna admin**:
   §§§KODE_61§§§

3. **Setel Ulang Superset**:
   §§§KODE_62§§§

### Masalah 2: Koneksi database gagal

**Gejala** :
- Tombol “Uji Koneksi” gagal
- Kesalahan: "Tidak dapat terhubung ke database"

**Diagnosa**:
§§§KODE_63§§§

**Solusi**:

1. **Gunakan URI SQLAlchemy yang benar**:
   §§§KODE_64§§§

2. **Instal driver yang diperlukan**:
   §§§KODE_65§§§

3. **Periksa jaringan**:
   §§§KODE_66§§§

### Masalah 3: Grafik tidak dimuat

**Gejala** :
- Dasbor menampilkan pemintal pemuatan tanpa batas waktu
- Grafik menampilkan "Kesalahan memuat data"

**Diagnosa**:
§§§KODE_67§§§

**Solusi**:

1. **Periksa batas waktu kueri**:
   §§§KODE_68§§§

2. **Aktifkan permintaan asinkron**:
   §§§KODE_69§§§

3. **Hapus cache**:
   §§§KODE_70§§§

### Masalah 4: Kesalahan izin

**Gejala** :
- Pengguna tidak dapat melihat dasbor
- Kesalahan: "Anda tidak memiliki akses ke dasbor ini"

**Diagnosa**:
§§§KODE_71§§§

**Solusi**:

1. **Tambahkan pengguna ke peran**:
   §§§KODE_72§§§

2. **Berikan akses ke dasbor**:
   §§§KODE_73§§§

3. **Periksa aturan RLS**:
   §§§KODE_74§§§

---

## Masalah PostgreSQL

### Masalah 1: Koneksi ditolak

**Gejala** :
- Aplikasi tidak dapat terhubung ke PostgreSQL
- Kesalahan: "Koneksi ditolak" atau "Tidak dapat terhubung"

**Diagnosa**:
§§§KODE_75§§§

**Solusi**:

1. **Mulai ulang PostgreSQL**:
   §§§KODE_76§§§

2. **Periksa pemetaan port**:
   §§§KODE_77§§§

3. **Periksa kredensial**:
   §§§KODE_78§§§

### Masalah 2: Kurangnya koneksi

**Gejala** :
- Kesalahan: "FATAL: slot koneksi yang tersisa sudah dipesan"
- Aplikasi kadang-kadang gagal terhubung

**Diagnosa**:
§§§KODE_79§§§

**Solusi**:

1. **Tingkatkan max_connections**:
   §§§KODE_80§§§

2. **Gunakan pengumpulan koneksi**:
   §§§KODE_81§§§

3. **Membunuh koneksi yang menganggur**:
   §§§KODE_82§§§

### Masalah 3: Kueri lambat

**Gejala** :
- Kueri basis data memerlukan waktu beberapa detik
- Aplikasi kedaluwarsa

**Diagnosa**:
§§§KODE_83§§§

**Solusi**:

1. **Buat indeks**:
   §§§KODE_84§§§

2. **Jalankan ANALISIS**:
   §§§KODE_85§§§

3. **Meningkatkan shared_buffer**:
   §§§KODE_86§§§

---

##Masalah MinIO

### Masalah 1: Tidak dapat mengakses konsol MinIO

**Gejala** :
- Browser menampilkan kesalahan pada `http://localhost:9001`

**Diagnosa**:
§§§KODE_88§§§

**Solusi**:

1. **Periksa port**:
   §§§KODE_89§§§

2. **Akses URL yang benar**:
   §§§KODE_90§§§

3. **Mulai ulang MinIO**:
   §§§KODE_91§§§

### Masalah 2: Kesalahan Akses Ditolak

**Gejala** :
- Aplikasi tidak dapat membaca/menulis ke S3
- Kesalahan: "Akses Ditolak" atau "403 Dilarang"

**Diagnosa**:
§§§KODE_92§§§

**Solusi**:

1. **Periksa kredensial**:
   §§§KODE_93§§§

2. **Periksa kebijakan keranjang**:
   §§§KODE_94§§§

3. **Buat kunci akses untuk aplikasi**:
   §§§KODE_95§§§

### Masalah 3: Bucket tidak ditemukan

**Gejala** :
- Kesalahan: "Bucket yang ditentukan tidak ada"

**Diagnosa**:
§§§KODE_96§§§

**Solusi**:

1. **Buat keranjang**:
   §§§KODE_97§§§

2. **Periksa nama bucket di konfigurasi**:
   §§§KODE_98§§§

---

## Jaringan dan konektivitas

### Masalah: Layanan tidak dapat berkomunikasi

**Gejala** :
- "Koneksi ditolak" antar kontainer
- Kesalahan “Host tidak ditemukan”.

**Diagnosa**:
§§§KODE_99§§§

**Solusi**:

1. **Pastikan semua layanan berada di jaringan yang sama**:
   §§§KODE_100§§§

2. **Gunakan nama container, bukan localhost**:
   §§§KODE_101§§§

3. **Membuat ulang jaringan**:
   §§§KODE_102§§§

---

## Masalah kinerja

### Masalah: Penggunaan CPU yang tinggi

**Diagnosa**:
§§§KODE_103§§§

**Solusi**:

1. **Batasi permintaan yang bersaing**:
   §§§KODE_104§§§

2. **Optimalkan kueri** (lihat [masalah Dremio](#dremio-issues))

3. **Meningkatkan alokasi CPU**:
   §§§KODE_105§§§

### Masalah: Penggunaan memori tinggi

**Diagnosa**:
§§§KODE_106§§§

**Solusi**:

1. **Meningkatkan ukuran heap**:
   §§§KODE_107§§§

2. **Aktifkan tumpahan disk**:
   §§§KODE_108§§§

---

## Masalah kualitas data

Lihat detail solusinya di [Panduan Kualitas Data](./data-quality.md).

### Pemeriksaan cepat

§§§KODE_109§§§

---

## Ringkasan

Panduan pemecahan masalah ini mencakup:

- **Pendekatan umum**: Metodologi sistematis untuk mendiagnosis masalah
- **Masalah berdasarkan komponen**: Solusi untuk 7 layanan platform
- **Masalah Jaringan**: Masalah konektivitas kontainer
- **Masalah kinerja**: CPU, memori, dan pengoptimalan kueri
- **Masalah kualitas data**: Masalah dan pemeriksaan data umum

**Poin penting**:
- Selalu periksa log terlebih dahulu: `docker-compose logs [service]`
- Gunakan nama container, bukan localhost, untuk komunikasi antar layanan
- Uji konektivitas: `docker exec [container] ping [target]`
- Pantau sumber daya: `docker stats`
- Mulailah dengan sederhana: mulai ulang layanan sebelum proses debug yang rumit

**Dokumentasi terkait:**
- [Panduan Instalasi](../getting-started/installation.md)
- [Panduan Konfigurasi](../getting-started/configuration.md)
- [Panduan Kualitas Data](./data-quality.md)
- [Arsitektur: Penerapan](../architecture/deployment.md)

**Butuh bantuan lebih lanjut?**
- Periksa log komponen: `docker-compose logs -f [service]`
- Konsultasikan dokumentasi layanan
- Cari masalah GitHub
- Hubungi tim dukungan

---

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025