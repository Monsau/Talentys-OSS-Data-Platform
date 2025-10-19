# Arsitektur Aliran Data

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Aliran Data Ujung-ke-Ujung](#aliran data ujung-ke-ujung)
3. [Lapisan Penyerapan](#lapisan penyerapan)
4. [Lapisan Penyimpanan](#lapisan penyimpanan)
5. [Lapisan Pemrosesan](#lapisan pemrosesan)
6. [Lapisan Presentasi](#lapisan presentasi)
7. [Model Aliran Data](#model aliran data)
8. [Pertimbangan Kinerja](#pertimbangan-kinerja)
9. [Pemantauan Aliran Data](#pemantauan aliran data)
10. [Praktik yang Baik](#praktik yang baik)

---

## Ringkasan

Dokumen ini merinci arsitektur aliran data platform secara lengkap, mulai dari penyerapan data awal hingga konsumsi akhir. Memahami alur ini sangat penting untuk mengoptimalkan kinerja, memecahkan masalah, dan merancang saluran data yang efektif.

### Prinsip Aliran Data

Arsitektur kami mengikuti prinsip-prinsip dasar berikut:

1. **Aliran Searah**: Data bergerak ke arah yang jelas dan dapat diprediksi
2. **Pemrosesan Berlapis**: Setiap lapisan memiliki tanggung jawab khusus
3. **Komponen Terpisah**: Layanan berkomunikasi melalui antarmuka yang terdefinisi dengan baik
4. **Idempotence**: Pengoperasian dapat diulangi dengan aman
5. **Observabilitas**: Setiap langkah dicatat dan dipantau

### Lapisan Arsitektur

§§§KODE_0§§§

---

## Aliran Data Ujung-ke-Ujung

### Urutan Saluran Pipa Lengkap

§§§KODE_1§§§

### Langkah Aliran Data

| Langkah | Komponen | Pintu masuk | Keluar | Latensi |
|-------|----------|--------|--------|---------|
| **Ekstrak** | Airbyte | API/BD Eksternal | JSON/CSV mentah | 1-60 menit |
| **Memuat** | Lapisan Penyimpanan | File Mentah | Bucket Pilihan | <1 menit |
| **Katalogisasi** | Dremio | Jalur penyimpanan | Kumpulan data virtual | <1 menit |
| **Transformasi** | dbt | Meja Perunggu | Meja Perak/Emas | 5-30 menit |
| **Pengoptimalan** | Pikiran Dremio | Kueri Mentah | Hasil tersembunyi | Waktu nyata |
| **Visualisasi** | Superset | Kueri SQL | Bagan/Dasbor | <5 detik |

---

## Lapisan Penelanan

### Ekstraksi Data Airbyte

Airbyte mengelola semua penyerapan data dari sumber eksternal.

#### Alur Koneksi Sumber

§§§KODE_2§§§

#### Metode Ekstraksi Data

**1. Penyegaran Penuh**
§§§KODE_3§§§

**2. Sinkronisasi Tambahan**
§§§KODE_4§§§

**3. Ubah Pengambilan Data (CDC)**
§§§KODE_5§§§

### Integrasi API Airbyte

§§§KODE_6§§§

### Kinerja Ekstraksi

| Jenis Sumber | Aliran | Frekuensi yang Direkomendasikan |
|----------------|-------|----------------------|
| PostgreSQL | 50-100 ribu baris/dtk | Setiap 15-60 menit |
| API REST | 1-10 ribu permintaan/dtk | Setiap 5-30 menit |
| File CSV | 100-500 MB/dtk | Harian |
| MongoDB | 10-50 ribu dokumen/dtk | Setiap 15-60 menit |
| CDC MySQL | Waktu nyata | Terus menerus |

---

## Lapisan Penyimpanan

### Penyimpanan MinIO S3

MinIO menyimpan data mentah dan diproses dalam struktur hierarki.

#### Organisasi Keranjang

§§§KODE_7§§§

#### Struktur Jalur Data

§§§KODE_8§§§

### Strategi Format Penyimpanan

| Lapisan | Format | Kompresi | Partisi | Alasan |
|--------|--------|-------------|-----------------|--------|
| **Perunggu** | Parket | Tajam | Berdasarkan tanggal | Menulis cepat, kompresi bagus |
| **Perak** | Parket | Tajam | Berdasarkan kunci bisnis | Kueri yang efektif |
| **Emas** | Parket | ZSTD | Berdasarkan jangka waktu | Kompresi Maksimum |
| **Log** | JSON | Gzip | Berdasarkan layanan/tanggal | Dapat dibaca oleh manusia |

### Penyimpanan Metadata PostgreSQL

Toko PostgreSQL:
- Konfigurasi dan status Airbyte
- Metadata dan riwayat eksekusi dbt
- Dasbor dan pengguna superset
- Log dan metrik aplikasi

§§§KODE_9§§§

### Penyimpanan Dokumen Elasticsearch

Elasticsearch mengindeks log dan memungkinkan pencarian teks lengkap.

§§§KODE_10§§§

---

## Lapisan Pemrosesan

### Virtualisasi Data Dremio

Dremio membuat tampilan terpadu di semua sumber penyimpanan.

#### Pembuatan Kumpulan Data Virtual

§§§KODE_11§§§

#### Akselerasi dengan Refleksi

Refleksi Dremio menghitung hasil kueri terlebih dahulu untuk kinerja instan.

§§§KODE_12§§§

**Dampak Kinerja Refleksi:**

| Jenis Kueri | Tanpa Refleksi | Dengan Refleksi | Akselerasi |
|-----------------|----------------|----------------|---------|
| PILIH Sederhana | 500 md | 50 md | 10x |
| Agregasi | 5 detik | 100 md | 50x |
| GABUNG Kompleks | 30an | 500 md | 60x |
| Pemindaian Besar | 120an | 2 detik | 60x |

### transformasi dbt

dbt mengubah data mentah menjadi model yang siap untuk bisnis.

#### Aliran Transformasi

§§§KODE_13§§§

#### Contoh Alur Transformasi

§§§KODE_14§§§

§§§KODE_15§§§

§§§KODE_16§§§

#### Alur Eksekusi dbt

§§§KODE_17§§§

### Ketertelusuran Silsilah Data

§§§KODE_18§§§

---

## Lapisan Presentasi

### Alur Eksekusi Kueri

§§§KODE_19§§§

### Model Akses API

#### 1. Dasbor Superset (BI Interaktif)

§§§KODE_20§§§

#### 2. API Penerbangan Panah (Performa Tinggi)

§§§KODE_21§§§

#### 3. REST API (Integrasi Eksternal)

§§§KODE_22§§§

---

## Model Aliran Data

### Model 1: Pipa Batch ETL

§§§KODE_23§§§

### Model 2: Streaming Waktu Nyata

§§§KODE_24§§§

### Pola 3: Pembaruan Tambahan

§§§KODE_25§§§

### Model 4: Arsitektur Lambda (Batch + Aliran)

§§§KODE_26§§§

---

## Pertimbangan Kinerja

### Optimasi Penyerapan

§§§KODE_27§§§

### Optimasi Penyimpanan

§§§KODE_28§§§

### Optimasi Kueri

§§§KODE_29§§§

### Optimalisasi Transformasi

§§§KODE_30§§§

### Tolok Ukur Kinerja

| Operasi | Kumpulan Data Kecil<br/>(1 juta baris) | Kumpulan Data Sedang<br/>(100 juta baris) | Kumpulan Data Besar<br/>(1 miliar baris) |
|-------------|----------------------------|-------------------------------|------------------------------------------|
| **Sinkronkan Airbyte** | 2 menit | 30 menit | 5 jam |
| **eksekusi dbt** | 30 detik | 10 menit | 2 jam |
| **Refleksi Konstruksi** | 10 detik | 5 menit | 30 menit |
| **Permintaan Dasbor** | <100 md | <500 md | <2dtk |

---

## Pemantauan Aliran Data

### Metrik Utama untuk Dilacak

§§§KODE_31§§§

### Dasbor Pemantauan

§§§KODE_32§§§

### Agregasi Log

§§§KODE_33§§§

---

## Praktik Terbaik

### Desain Aliran Data

1. **Desain untuk Idempotensi**
   - Menjamin bahwa operasi dapat diulang dengan aman
   - Gunakan kunci unik untuk deduplikasi
   - Menerapkan penanganan kesalahan yang tepat

2. **Menerapkan Kontrol Kualitas Data**
   §§§KODE_34§§§

3. **Partisi Kumpulan Data Besar**
   §§§KODE_35§§§

4. **Gunakan Mode Sinkronisasi yang Sesuai**
   - Penyegaran Penuh: Tabel dimensi kecil
   - Inkremental: Tabel fakta berukuran besar
   - CDC: Persyaratan waktu nyata

### Penyesuaian Kinerja

1. **Optimalkan Penjadwalan Sinkronisasi Airbyte**
   §§§KODE_36§§§

2. **Ciptakan Pemikiran Strategis**
   §§§KODE_37§§§

3. **Optimalkan Model dbt**
   §§§KODE_38§§§

### Pemecahan Masalah Umum

| Masalah | Gejala | Solusi |
|---------|---------|----------|
| **Sinkronisasi Airbyte Lambat** | Waktu untuk menyinkronkan | Tingkatkan ukuran batch, gunakan mode tambahan |
| **Kurangnya Memori** | Model dbt gagal | Terwujud secara bertahap, tambahkan partisi |
| **Pertanyaan Lambat** | Dasbor batas waktu | Buat refleksi, tambahkan indeks |
| **Penyimpanan Penuh** | Kegagalan menulis | Terapkan retensi data, kompres data lama |
| **Data Usang** | Metrik lama | Tingkatkan frekuensi sinkronisasi, periksa jadwal |

### Praktik Keamanan yang Baik

1. **Enkripsi Data dalam Transit**
   §§§KODE_39§§§

2. **Menerapkan Kontrol Akses**
   §§§KODE_40§§§

3. **Akses Data Audit**
   §§§KODE_41§§§

---

## Ringkasan

Dokumen ini merinci arsitektur aliran data lengkap:

- **Lapisan Penyerapan**: Airbyte mengekstrak data dari berbagai sumber melalui penyegaran penuh, inkremental, atau CDC
- **Lapisan Penyimpanan**: MinIO, PostgreSQL, dan Elasticsearch menyimpan data mentah dan diproses dalam lapisan terorganisir
- **Lapisan Pemrosesan**: Dremio memvirtualisasikan data dan dbt mengubahnya melalui model staging, perantara, dan mart
- **Lapisan Presentasi**: Dasbor dan API superset menyediakan akses ke data siap bisnis

Poin-poin penting yang perlu diingat:
- Data mengalir searah melalui lapisan yang terdefinisi dengan jelas
- Setiap komponen memiliki tanggung jawab dan antarmuka tertentu
- Kinerja dioptimalkan melalui refleksi, partisi dan caching
- Pemantauan dan observasi terintegrasi ke dalam setiap lapisan
- Praktik yang baik menjamin keandalan, kinerja, dan keamanan

**Dokumentasi Terkait:**
- [Ikhtisar Arsitektur](./overview.md)
- [Komponen](./components.md)
- [Penerapan](./deployment.md)
- [Panduan Integrasi Airbyte](../guides/airbyte-integration.md)
- [Panduan Pengembangan dbt](../guides/dbt-development.md)

---

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025