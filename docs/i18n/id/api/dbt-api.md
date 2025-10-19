# referensi API dbt

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Perintah CLI](#perintah-cli)
3. [API Python](#api-python)
4. [File metadata](#file-metadata)
5. [API Cloud dbt](#api-dbt-cloud)
6. [Makro khusus](#makro khusus)

---

## Ringkasan

dbt menyediakan tiga antarmuka utama:

| Antarmuka | Kasus penggunaan | Akses |
|---------------|-------------|-------|
| CLI | Pengembangan, CI/CD | Baris perintah |
| API Python | Eksekusi Terprogram | Kode piton |
| API Awan dbt | Layanan Terkelola | API REST |
| Metadata | Introspeksi | File JSON |

---

## Perintah CLI

### Perintah utama

#### harus dijalankan

Jalankan model untuk mengubah data.

§§§KODE_0§§§

**Pilihan**:
§§§KODE_1§§§

#### tes dbt

Jalankan pengujian kualitas data.

§§§KODE_2§§§

#### pembuatan dbt

Jalankan model, pengujian, seed, dan snapshot secara bersamaan.

§§§KODE_3§§§

#### dokumen dbt

Menghasilkan dan menyajikan dokumentasi.

§§§KODE_4§§§

### Perintah pengembang

#### kompilasi dbt

Kompilasi model ke dalam SQL tanpa menjalankannya.

§§§KODE_5§§§

#### debug dbt

Uji koneksi dan konfigurasi database.

§§§KODE_6§§§

#### dbt ls (daftar)

Daftar sumber daya proyek.

§§§KODE_7§§§

### Perintah data

#### benih dbt

Muat file CSV ke dalam database.

§§§KODE_8§§§

#### cuplikan dbt

Buat tabel dimensi tipe 2 yang perlahan berubah.

§§§KODE_9§§§

### Perintah utilitas

#### dbt bersih

Hapus file dan artefak yang dikompilasi.

§§§KODE_10§§§

#### deps dbt

Instal paket dari paket.yml.

§§§KODE_11§§§

#### dbt init

Inisialisasi proyek dbt baru.

§§§KODE_12§§§

---

## API Python

### Eksekusi dasar

§§§KODE_13§§§

### Bungkus Python lengkap

§§§KODE_14§§§

### Integrasi aliran udara

§§§KODE_15§§§

---

## File metadata

### manifes.json

Berisi metadata proyek lengkap.

**Lokasi**: `target/manifest.json`

§§§KODE_17§§§

### jalankan_results.json

Berisi hasil eksekusi eksekusi terakhir.

**Lokasi**: `target/run_results.json`

§§§KODE_19§§§

### katalog.json

Berisi informasi skema database.

**Lokasi**: `target/catalog.json`

§§§KODE_21§§§

---

## dbt Cloud API

Jika Anda menggunakan dbt Cloud (tidak berlaku untuk instalasi lokal), API tersedia.

**URL Dasar**: `https://cloud.getdbt.com/api/v2`

### Otentikasi

§§§KODE_23§§§

### Memicu pekerjaan

§§§KODE_24§§§

---

## Makro khusus

### Buat makro khusus

**Berkas**: `macros/custom_tests.sql`

§§§KODE_26§§§

### Gunakan dalam pengujian

**Berkas**: `models/staging/schema.yml`

§§§KODE_28§§§

### Makro tingkat lanjut dengan argumen

§§§KODE_29§§§

### Panggil makro

§§§KODE_30§§§

---

## Ringkasan

Referensi API ini mencakup:

- **Perintah CLI**: Referensi lengkap untuk semua perintah dbt
- **Python API**: Eksekusi terprogram dengan wrapper Python
- **File metadata**: manifest.json, run_results.json, catalog.json
- **dbt Cloud API**: Tugas pemicu (jika menggunakan dbt Cloud)
- **Makro Khusus**: Membuat dan menggunakan fitur khusus

**Poin-poin penting**:
- Gunakan CLI untuk pengembangan dan pekerjaan interaktif
- Gunakan API Python untuk otomatisasi dan orkestrasi
- Analisis file metadata untuk introspeksi
- Buat makro khusus untuk logika yang dapat digunakan kembali
- Integrasikan dengan Airflow untuk perencanaan produksi

**Dokumentasi Terkait**:
- [panduan pengembangan dbt](../guides/dbt-development.md)
- [Panduan kualitas data](../guides/data-quality.md)
- [Arsitektur: Aliran Data](../architecture/data-flow.md)

---

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025