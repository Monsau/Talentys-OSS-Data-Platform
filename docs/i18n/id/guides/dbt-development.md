# Panduan Pengembangan dbt

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Konfigurasi Proyek](#konfigurasi proyek)
3. [Pemodelan Data](#pemodelan data)
4. [Kerangka Uji](#kerangka uji)
5. [Dokumentasi](#dokumentasi)
6. [Makro dan Paket](#makro-dan-paket)
7. [Model Tambahan](#model tambahan)
8. [Alur Kerja Orkestrasi](#alur kerja-orkestrasi)
9. [Praktik yang Baik](#praktik yang baik)
10. [Pemecahan Masalah](#pemecahan masalah)

---

## Ringkasan

dbt (alat pembuatan data) memungkinkan teknisi analitik mengubah data di gudang menggunakan SQL dan praktik terbaik rekayasa perangkat lunak. Panduan ini mencakup semuanya mulai dari inisialisasi proyek hingga teknik pengembangan lanjutan.

### Apa itu dbt?

dbt mengubah data mentah menjadi kumpulan data yang siap analisis menggunakan:

- **Transformasi SQL**: Tulis pernyataan SELECT, dbt menangani sisanya
- **Kontrol Versi**: Integrasi Git untuk kolaborasi
- **Pengujian**: Kerangka pengujian kualitas data terintegrasi
- **Dokumentasi**: Dokumentasi yang dibuat sendiri dengan silsilah
- **Modularitas**: Templat dan makro yang dapat digunakan kembali

### Konsep Utama

§§§KODE_0§§§

### alur kerja dbt

§§§KODE_1§§§

---

## Konfigurasi Proyek

### Inisialisasi Proyek dbt

§§§KODE_2§§§

### Konfigurasikan profil.yml

§§§KODE_3§§§

### Konfigurasikan dbt_project.yml

§§§KODE_4§§§

### Variabel Lingkungan

§§§KODE_5§§§

### Uji Koneksi

§§§KODE_6§§§

---

## Pemodelan Data

### Model Pementasan

Model pementasan membersihkan dan menstandarkan data mentah dari sumber.

#### Tetapkan Sumber

§§§KODE_7§§§

#### Contoh Model Pementasan

§§§KODE_8§§§

§§§KODE_9§§§

### Model Menengah

Model perantara menggabungkan dan memperkaya data.

§§§KODE_10§§§

### Tabel Dibuat

§§§KODE_11§§§

### Tabel Dimensi

§§§KODE_12§§§

### Model Pasar

§§§KODE_13§§§

---

## Kerangka Uji

### Tes Terpadu

§§§KODE_14§§§

### Tes yang Dipersonalisasi

§§§KODE_15§§§

§§§KODE_16§§§

### Tes Generik

§§§KODE_17§§§

Menggunakan:
§§§KODE_18§§§

### Jalankan Tes

§§§KODE_19§§§

---

## Dokumentasi

### Dokumentasi Model

§§§KODE_20§§§

### Tambahkan Deskripsi

§§§KODE_21§§§

### Hasilkan Dokumentasi

§§§KODE_22§§§

**Dokumentasi Fitur**:
- **Grafik Silsilah**: Representasi visual dari dependensi model
- **Rincian Kolom**: Deskripsi, jenis, pengujian
- **Kesegaran Sumber**: Saat data telah dimuat
- **Tampilan Proyek**: konten README
- **Pencarian**: Temukan model, kolom, deskripsi

---

## Makro dan Paket

### Makro Khusus

§§§KODE_23§§§

Menggunakan:
§§§KODE_24§§§

### Cuplikan SQL yang dapat digunakan kembali

§§§KODE_25§§§

### Instal Paket

§§§KODE_26§§§

Instal paket:
§§§KODE_27§§§

### Gunakan Paket Makro

§§§KODE_28§§§

§§§KODE_29§§§

---

## Model Tambahan

### Model Tambahan Dasar

§§§KODE_30§§§

### Strategi Tambahan

#### 1. Tambahkan Strategi

§§§KODE_31§§§

#### 2. Penggabungan Strategi

§§§KODE_32§§§

#### 3. Hapus+Sisipkan strategi

§§§KODE_33§§§

### Penyegaran Lengkap

§§§KODE_34§§§

---

## Alur Kerja Orkestrasi

### dbt Jalankan Perintah

§§§KODE_35§§§

### Saluran Pipa Penuh

§§§KODE_36§§§

### Integrasi aliran udara

§§§KODE_37§§§

---

## Praktik Terbaik

### 1. Konvensi Penamaan

§§§KODE_38§§§

### 2. Struktur Folder

§§§KODE_39§§§

### 3. Gunakan CTE

§§§KODE_40§§§

### 4. Tambahkan Tes Lebih Awal

§§§KODE_41§§§

### 5. Dokumentasikan Semuanya

§§§KODE_42§§§

---

## Pemecahan masalah

### Masalah Umum

#### Masalah 1: Kesalahan Kompilasi

**Kesalahan**: `Compilation Error: Model not found`

**Larutan**:
§§§KODE_44§§§

#### Masalah 2: Ketergantungan Melingkar

**Kesalahan**: `Compilation Error: Circular dependency detected`

**Larutan**:
§§§KODE_46§§§

#### Masalah 3: Tes Gagal

**Kesalahan**: `ERROR test not_null_stg_customers_email (FAIL 15)`

**Larutan**:
§§§KODE_48§§§

#### Masalah 4: Model Tambahan Tidak Berfungsi

**Kesalahan**: Model inkremental dibangun kembali dari awal setiap saat

**Larutan**:
§§§KODE_49§§§

---

## Ringkasan

Panduan pengembangan dbt lengkap ini telah mencakup:

- **Konfigurasi Proyek**: Inisialisasi, konfigurasi, konfigurasi lingkungan
- **Pemodelan Data**: Model pementasan, perantara, fakta, dimensi, dan pasar
- **Tes Kerangka**: Tes terintegrasi, tes khusus, tes generik
- **Dokumentasi**: Dokumentasi model, dokumen situs yang dibuat secara otomatis
- **Makro dan Paket**: Kode yang dapat digunakan kembali, dbt_utils, ekspektasi
- **Model Tambahan**: Strategi menambahkan, menggabungkan, menghapus+memasukkan
- **Orkestrasi Alur Kerja**: perintah dbt, skrip saluran pipa, integrasi Aliran Udara
- **Praktik yang Baik**: Konvensi penamaan, struktur folder, dokumentasi
- **Pemecahan Masalah**: Masalah umum dan solusinya

Poin-poin penting yang perlu diingat:
- Gunakan pernyataan SQL SELECT, dbt mengelola DDL/DML
- Uji lebih awal dan sering dengan kerangka pengujian terintegrasi
- Model dokumen untuk analisis layanan mandiri
- Gunakan model inkremental untuk tabel besar
- Ikuti konvensi penamaan yang konsisten
- Memanfaatkan paket untuk fitur-fitur umum

**Dokumentasi Terkait:**
- [Panduan Pengaturan Dremio](./dremio-setup.md)
- [Panduan Kualitas Data](./data-quality.md)
- [Arsitektur: Aliran Data](../architecture/data-flow.md)
- [Tutorial Langkah Pertama](../getting-started/first-steps.md)

---

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025