# Komponen Platform

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16-10-2025  
**Bahasa**: Prancis

---

## Ikhtisar Komponen

Platform Data terdiri dari 7 komponen utama yang bekerja sama untuk memberikan solusi lengkap.

§§§KODE_0§§§

---

## 1. Airbyte – Platform Integrasi Data

### Ringkasan

Airbyte adalah mesin integrasi data sumber terbuka yang menggabungkan data dari berbagai sumber ke tujuan.

**Versi**: 0.50.33  
**Lisensi**: MIT  
**Situs Web**: https://airbyte.com

### Fitur Utama

- **300+ Konektor Bawaan**: Basis data, API, file, aplikasi SaaS
- **Ubah Pengambilan Data (CDC)**: Replikasi data waktu nyata
- **Konektor Khusus**: Dibuat dengan Python atau CDK kode rendah
- **Normalisasi**: Mengubah JSON menjadi tabel relasional
- **Sinkronisasi Tambahan**: Hanya menyinkronkan data baru/yang dimodifikasi
- **Pemantauan**: Sinkronisasi status pelacakan terintegrasi

### Arsitektur

§§§KODE_1§§§

### Kasus Penggunaan

- **ELT Pipelines**: Alur Kerja Ekstrak-Muat-Transformasi
- **Replikasi Basis Data**: Menjaga basis data tetap tersinkronisasi
- **Integrasi API**: Ekstrak data dari REST API
- **Penyerapan Data Lake**: Memuat data ke S3/MinIO
- **Migrasi Cloud**: Memindahkan data lokal ke cloud

### Pengaturan

§§§KODE_2§§§

### Poin Integrasi

- **Output ke**: MinIO S3, PostgreSQL, Dremio
- **Orkestrasi**: Dapat dipicu oleh Airflow, Prefek
- **Pemantauan**: Titik akhir metrik Prometheus

---

## 2. Dremio – Platform Data Lakehouse

### Ringkasan

Dremio menyediakan antarmuka SQL terpadu untuk semua sumber data dengan akselerasi kueri.

**Versi**: 26.0 OSS  
**Lisensi**: Apache 2.0  
**Situs Web**: https://www.dremio.com

### Fitur Utama

- **Data Lakehouse**: Menggabungkan fleksibilitas lake dengan kinerja gudang
- **Pemikiran**: Akselerasi kueri otomatis (hingga 100x lebih cepat)
- **Penerbangan Panah**: Transfer data berkinerja tinggi
- **Virtualisasi Data**: Kueri tanpa memindahkan data
- **Lapisan Semantik**: Definisi data yang ramah bisnis
- **Perjalanan Waktu**: Kueri berdasarkan versi historis

### Arsitektur

§§§KODE_3§§§

### Kasus Penggunaan

- **Analisis Layanan Mandiri**: Memungkinkan pengguna bisnis menjelajahi data
- **Data Mesh**: Akses gabungan ke data
- **Akselerasi Kueri**: Mempercepat kueri dasbor
- **Katalog Data**: Temukan dan kelola data
- **Aktivasi BI**: Power Tableau, Power BI, Superset

### Pengaturan

§§§KODE_4§§§

### Poin Integrasi

- **Dibaca dari**: MinIO S3, PostgreSQL, Elasticsearch
- **Transformasi dengan**: dbt
- **Digunakan untuk**: Superset, Tableau, Power BI

### Proksi PostgreSQL untuk Dremio

Dremio dapat meniru server PostgreSQL, memungkinkan alat yang kompatibel dengan PostgreSQL untuk terhubung ke Dremio seolah-olah itu adalah database PostgreSQL standar.

#### Arsitektur Proksi PostgreSQL

§§§KODE_5§§§

#### Perbandingan 3 Port Dremio

§§§KODE_6§§§

#### Konfigurasi Proksi

§§§KODE_7§§§

#### Kasus Penggunaan Proksi

1. **Alat BI Legacy**: Hubungkan alat yang tidak mendukung Arrow Flight
2. **Migrasi Mudah**: Ganti PostgreSQL dengan Dremio tanpa mengubah kode
3. **Kompatibilitas ODBC/JDBC**: Gunakan driver PostgreSQL standar
4. **Pengembangan**: Uji dengan alat PostgreSQL yang sudah dikenal (psql, pgAdmin)

#### Contoh Koneksi

§§§KODE_8§§§

#### Keterbatasan

- **Kinerja**: Arrow Flight (port 32010) 20-50x lebih cepat
- **Fitur**: Beberapa fungsi PostgreSQL tingkat lanjut tidak didukung
- **Rekomendasi**: Gunakan Arrow Flight untuk produksi, proksi PostgreSQL untuk kompatibilitas

#### Alur Koneksi melalui Proksi PostgreSQL

§§§KODE_9§§§

#### Perbandingan Protokol

| Protokol | Pelabuhan | Kinerja | Latensi | Kasus Penggunaan |
|---------------|------|-------------|---------|--------|
| **API REST** | 9047 | Standar | ~50-100 md | UI Web, administrasi |
| **ODBC/JDBC (Proksi PostgreSQL)** | 31010 | Bagus | ~20-50 md | Alat BI lama, kompatibilitas |
| **Penerbangan Panah** | 32010 | Luar Biasa (20-50x) | ~5-10 md | Produksi, Superset, dbt |

#### Performa Komparatif

§§§KODE_10§§§

---

## 3.dbt - Alat Transformasi Data

### Ringkasan

dbt (alat pembuatan data) memungkinkan insinyur analitik mengubah data menggunakan SQL.

**Versi**: 1.10+  
**Lisensi**: Apache 2.0  
**Situs Web**: https://www.getdbt.com

### Fitur Utama

- **Berbasis SQL**: Menulis transformasi dalam SQL
- **Kontrol Versi**: Integrasi Git untuk kolaborasi
- **Tes**: Uji kualitas data terintegrasi
- **Dokumentasi**: Kamus data yang dibuat secara otomatis
- **Modularitas**: Makro dan paket yang dapat digunakan kembali
- **Model Tambahan**: Hanya memproses data baru

### Arsitektur

§§§KODE_11§§§

### Kasus Penggunaan

- **Pemodelan Data**: Membuat diagram bintang/serpihan
- **Kualitas Data**: Validasi integritas data
- **Dimensi Berubah Secara Perlahan**: Melacak riwayat perubahan
- **Agregasi Data**: Membuat tabel ringkasan
- **Dokumentasi Data**: Menghasilkan katalog data

### Pengaturan

§§§KODE_12§§§

### Poin Integrasi

- **Membaca dari**: Kumpulan Data Dremio
- **Ditulis ke**: Dremio (melalui Arrow Flight)
- **Diatur oleh**: Airflow, cron, Airbyte pasca-sinkronisasi

---

## 4. Apache Superset – Platform Intelijen Bisnis

### Ringkasan

Superset adalah platform eksplorasi dan visualisasi data modern.

**Versi**: 3.0  
**Lisensi**: Apache 2.0  
**Situs Web**: https://superset.apache.org

### Fitur Utama

- **SQL IDE**: Editor SQL tingkat lanjut dengan pelengkapan otomatis
- **Visualisasi Kaya**: 50+ jenis bagan
- **Dasbor Interaktif**: Telusuri, filter, pemfilteran silang
- **SQL Lab**: Antarmuka kueri ad-hoc
- **Peringatan**: Laporan dan peringatan terjadwal
- **Caching**: Hasil kueri cache untuk kinerja

### Arsitektur

§§§KODE_13§§§

### Kasus Penggunaan

- **Dasbor Eksekutif**: Pemantauan KPI
- **Analisis Operasional**: Pemantauan waktu nyata
- **BI Self-Service**: Memberdayakan analis
- **Analisis Tertanam**: integrasi iframe dalam aplikasi
- **Eksplorasi Data**: Analisis ad-hoc

### Pengaturan

§§§KODE_14§§§

### Poin Integrasi

- **Permintaan**: Dremio (melalui Penerbangan Arrow)
- **Otentikasi**: LDAP, OAuth2, Basis Data
- **Peringatan**: Email, Slack

---

## 5. PostgreSQL - Basis Data Relasional

### Ringkasan

PostgreSQL adalah sistem manajemen basis data relasional sumber terbuka yang canggih.

**Versi**: 16  
**Lisensi**: Lisensi PostgreSQL  
**Situs Web**: https://www.postgresql.org

### Fitur Utama

- **Kepatuhan ACID**: Transaksi yang andal
- **Dukungan JSON**: Jenis JSON/JSONB asli
- **Pencarian Teks Lengkap**: Kemampuan pencarian terintegrasi
- **Ekstensi**: PostGIS, pg_stat_statements, TimescaleDB
- **Replikasi**: Replikasi streaming, replikasi logis
- **Partisi**: Partisi tabel asli

### Arsitektur

§§§KODE_15§§§

### Kasus Penggunaan

- **Penyimpanan Metadata**: Menyimpan metadata sistem
- **Beban Transaksional**: Aplikasi OLTP
- **Tabel Pementasan**: Pemrosesan data sementara
- **Konfigurasi Penyimpanan**: Pengaturan aplikasi
- **Log Audit**: Melacak perubahan sistem

### Pengaturan

§§§KODE_16§§§

### Poin Integrasi

- **Dibaca oleh**: Dremio, Superset, Airbyte
- **Ditulis oleh**: Airbyte, dbt, aplikasi
- **Dikelola oleh**: Pencadangan otomatis, replikasi

---

## 6. MinIO – Penyimpanan Objek yang Kompatibel dengan S3

### Ringkasan

MinIO adalah sistem penyimpanan objek berkinerja tinggi yang kompatibel dengan S3.

**Versi**: Terbaru  
**Lisensi**: AGPLv3  
**Situs Web**: https://min.io

### Fitur Utama

- **S3 API**: 100% kompatibel dengan Amazon S3
- **Performa Tinggi**: Throughput multi-GB/dtk
- **Pengkodean Penghapusan**: Data keberlanjutan dan ketersediaan
- **Versi**: Kontrol versi objek
- **Enkripsi**: Sisi server dan sisi klien
- **Multi-Cloud**: Disebarkan di mana saja

### Arsitektur

§§§KODE_17§§§

### Kasus Penggunaan

- **Data Lake**: Menyimpan data mentah dan diproses
- **Penyimpanan Objek**: File, gambar, video
- **Penyimpanan Cadangan**: Cadangan basis data dan sistem
- **Arsip**: Penyimpanan data jangka panjang
- **Data Staging**: Penyimpanan pemrosesan sementara

### Pengaturan

§§§KODE_18§§§

### Poin Integrasi

- **Ditulis oleh**: Airbyte, dbt, aplikasi
- **Dibaca oleh**: Dremio, ilmuwan data
- **Dikelola oleh**: mc (Klien MinIO), s3cmd

---

## 7. Elasticsearch - Mesin Pencari dan Analisis

### Ringkasan

Elasticsearch adalah mesin pencarian dan analisis terdistribusi yang dibangun di Apache Lucene.

**Versi**: 8.15  
**Lisensi**: Lisensi Elastis 2.0  
**Situs Web**: https://www.elastic.co

### Fitur Utama

- **Pencarian Teks Lengkap**: Kemampuan pencarian lanjutan
- **Pengindeksan Waktu Nyata**: Ketersediaan data mendekati waktu nyata
- **Terdistribusi**: Skalabilitas horizontal
- **Agregasi**: Analisis kompleks
- **API RESTful**: API HTTP sederhana
- **Pembelajaran Mesin**: Deteksi anomali

### Arsitektur

§§§KODE_19§§§

### Kasus Penggunaan

- **Log Analitik**: Logging terpusat (tumpukan ELK)
- **Pencarian Aplikasi**: Katalog produk, pencarian situs
- **Analisis Keamanan**: Kasus penggunaan SIEM
- **Kemampuan Pengamatan**: Metrik dan pelacakan
- **Analisis Teks**: NLP dan analisis sentimen

### Pengaturan

§§§KODE_20§§§

### Poin Integrasi

- **Diindeks oleh**: Logstash, Filebeat
- **Diminta oleh**: Dremio, Kibana
- **Dipantau oleh**: Pemantauan Elasticsearch

---

## Perbandingan Komponen

| Komponen | Ketik | Kegunaan Utama | Skalabilitas | Negara |
|---------------|------|-----------------|-------------|------|
| **Airbyte** | Integrasi | Penyerapan data | Horisontal (pekerja) | Tanpa kewarganegaraan |
| **Dremio** | Mesin Kueri | Akses data | Horisontal (pelaksana) | Tanpa kewarganegaraan |
| **dbt** | Transformasi | Pemodelan data | Vertikal (hati) | Tanpa kewarganegaraan |
| **Superset** | platform BI | Visualisasi | Horisontal (web) | Tanpa kewarganegaraan |
| **PostgreSQL** | Basis Data | Penyimpanan metadata | Vertikal (+ replikasi) | Berstatus |
| **MinIO** | Penyimpanan Objek | Danau data | Horisontal (terdistribusi) | Berstatus |
| **Penelusuran elastis** | Mesin Pencari | Pencarian teks lengkap | Horisontal (cluster) | Berstatus |

---

## Persyaratan Sumber Daya

### Konfigurasi Minimum (Pengembangan)

§§§KODE_21§§§

### Konfigurasi yang Direkomendasikan (Produksi)

§§§KODE_22§§§

---

## Matriks Kompatibilitas Versi

| Komponen | Rilis | Kompatibel Dengan |
|----------|---------|-------|
| Airbyte | 0,50+ | Semua tujuan |
| Dremio | 26.0 | dbt 1.8+, pelanggan Penerbangan Panah |
| dbt | 1.10+ | Dremio 23.0+ |
| Superset | 3.0+ | Dremio 22.0+, PostgreSQL 12+ |
| PostgreSQL | 16 | Semua komponen |
| MiniO | Terbaru | Klien yang kompatibel dengan S3 |
| Pencarian elastis | 8.15 | Dremio 26.0+, Logstash 8.x |

---

**Versi Panduan Komponen**: 3.2.0  
**Terakhir Diperbarui**: 16-10-2025  
**Dikelola Oleh**: Tim Platform Data