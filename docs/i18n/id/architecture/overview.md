# Ikhtisar Arsitektur

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16-10-2025  
**Bahasa**: Prancis

---

## Perkenalan

Platform data adalah arsitektur cloud-native modern yang dibangun berdasarkan teknologi sumber terbuka. Ini memberikan solusi komprehensif untuk penyerapan, penyimpanan, transformasi, dan visualisasi data, yang dirancang untuk beban kerja analitis skala perusahaan.

§§§KODE_0§§§

---

## Prinsip Desain

### 1. Open Source Pertama

**Filosofi**: Gunakan teknologi sumber terbuka untuk menghindari vendor lock-in dan menjaga fleksibilitas.

**Manfaat**:
- Tidak ada biaya lisensi
- Pengembangan masyarakat
- Kemampuan penyesuaian penuh
- Audit keamanan transparan
- Kompatibilitas ekosistem yang luas

### 2. Arsitektur Berlapis

**Filosofi**: Pisahkan permasalahan ke dalam beberapa lapisan berbeda untuk kemudahan pemeliharaan dan skalabilitas.

**Lapisan**:
§§§KODE_1§§§

### 3. ELT, bukan ETL

**Filosofi**: Muat data mentah terlebih dahulu, ubah menjadi tujuan (ELT).

**Mengapa ELT?**
- **Fleksibilitas**: Mengubah data dalam berbagai cara tanpa ekstraksi ulang
- **Kinerja**: Gunakan penghitungan tujuan untuk transformasi
- **Auditabilitas**: Data mentah selalu tersedia untuk verifikasi
- **Biaya**: Mengurangi beban ekstraksi pada sistem sumber

**Mengalir**:
§§§KODE_2§§§

### 4. Model Data Lakehouse

**Filosofi**: Menggabungkan fleksibilitas data lake dengan kinerja gudang data.

**Fitur**:
- **Transaksi ACID**: Operasi Data Tepercaya
- **Aplikasi skema**: Jaminan kualitas data
- **Perjalanan waktu**: Mengkueri versi historis
- **Format terbuka**: Parket, Gunung Es, Danau Delta
- **Akses file langsung**: Tidak ada penguncian kepemilikan

### 5. Desain Cloud-Native

**Filosofi**: Desain untuk lingkungan dalam container dan terdistribusi.

**Pelaksanaan**:
- Kontainer Docker untuk semua layanan
- Skalabilitas horizontal
- Infrastruktur sebagai kode
- Tanpa kewarganegaraan sedapat mungkin
- Konfigurasi melalui variabel lingkungan

---

## Model Arsitektur

### Arsitektur Lambda (Batch + Aliran)

§§§KODE_3§§§

**Lapisan Batch** (Data Historis):
- Data dalam jumlah besar
- Perawatan berkala (setiap jam/harian)
- Latensi tinggi yang dapat diterima
- Pemrosesan ulang yang lengkap mungkin dilakukan

**Lapisan Kecepatan** (Data Waktu Nyata):
- Ubah Pengambilan Data (CDC)
- Diperlukan latensi rendah
- Pembaruan tambahan saja
- Mengelola data terkini

**Lapisan Layanan**:
- Menggabungkan tampilan batch dan kecepatan
- Antarmuka permintaan tunggal (Dremio)
- Pemilihan tampilan otomatis

### Medali Arsitektur (Perunggu → Perak → Emas)

§§§KODE_4§§§

**Lapisan perunggu** (Mentah):
- Data apa adanya dari sumber
- Tidak ada transformasi
- Sejarah lengkap dilestarikan
- Airbyte dimuat di sini

**Lapisan perak** (Dibersihkan):
- Kualitas data yang diterapkan
- Format standar
- templat pementasan dbt
- Analisis siap

**Lapisan Emas** (Profesi):
- Metrik gabungan
- Logika bisnis terapan
- Model dbt Mart
- Dioptimalkan untuk konsumsi

---

## Interaksi antar Komponen

### Alur Penyerapan Data

§§§KODE_5§§§

### Saluran Transformasi

§§§KODE_6§§§

### Menjalankan Kueri

§§§KODE_7§§§

---

## Model Skalabilitas

### Penskalaan Horisontal

**Layanan Tanpa Kewarganegaraan** (dapat berkembang dengan bebas):
- Pekerja Airbyte: Berevolusi untuk sinkronisasi paralel
- Pelaksana Dremio: Skala untuk kinerja kueri
- Web Superset: Berevolusi untuk pengguna yang bersaing

**Layanan Stateful** (memerlukan koordinasi):
- PostgreSQL: Replikasi replika primer
- MinIO: Mode terdistribusi (beberapa node)
- Elasticsearch: Cluster dengan sharding

### Penskalaan Vertikal

**Intensif dalam Memori**:
- Dremio: Tingkatkan tumpukan JVM untuk kueri besar
- PostgreSQL: Lebih banyak RAM untuk buffer cache
- Elasticsearch: Lebih banyak tumpukan untuk pengindeksan

**Intensif CPU**:
- dbt: Lebih banyak inti untuk model konstruksi paralel
- Airbyte: Transformasi data lebih cepat

### Partisi Data

§§§KODE_8§§§

---

## Ketersediaan Tinggi

### Redundansi Layanan

§§§KODE_9§§§

### Skenario Kegagalan

| Komponen | Kerusakan | Pemulihan |
|---------------|-------|---------|
| **Pekerja Airbyte** | Kecelakaan kontainer | Mulai ulang otomatis, lanjutkan sinkronisasi |
| **Pelaksana Dremio** | Kegagalan simpul | Permintaan dialihkan ke pelaksana lain |
| **PostgreSQL** | Layanan utama tidak berfungsi | Promosikan replika di |
| **Node MinIO** | Kegagalan disk | Pengkodean penghapusan merekonstruksi data |
| **Superset** | Layanan di luar layanan | Penyeimbang mengalihkan lalu lintas |

### Strategi Cadangan

§§§KODE_10§§§

---

## Arsitektur Keamanan

### Keamanan Jaringan

§§§KODE_11§§§

### Otentikasi dan Otorisasi

**Otentikasi Layanan**:
- **Dremio**: integrasi LDAP/AD, OAuth2, SAML
- **Superset**: Otentikasi Basis Data, LDAP, OAuth2
- **Airbyte**: Auth Dasar, OAuth2 (perusahaan)
- **MinIO**: kebijakan IAM, token STS

**Tingkat Otorisasi**:
§§§KODE_12§§§

### Enkripsi Data

**Saat Istirahat**:
- MinIO: Enkripsi sisi server (AES-256)
- PostgreSQL: Enkripsi Data Transparan (TDE)
- Elasticsearch: Indeks terenkripsi

**Dalam perjalanan**:
- TLS 1.3 untuk semua komunikasi antar layanan
- Penerbangan Panah dengan TLS untuk Dremio ↔ Superset
- HTTPS untuk antarmuka web

---

## Pemantauan dan Observabilitas

### Pengumpulan Metrik

§§§KODE_13§§§

**Metrik Utama**:
- **Airbyte**: Tingkat keberhasilan sinkronisasi, rekaman disinkronkan, byte ditransfer
- **Dremio**: Latensi permintaan, tingkat cache hit, penggunaan sumber daya
- **dbt**: Waktu konstruksi model, kegagalan pengujian
- **Superset**: Waktu pemuatan dasbor, pengguna aktif
- **Infrastruktur**: CPU, memori, disk, jaringan

### Pencatatan

**Logging Terpusat**:
§§§KODE_14§§§

### Pelacakan

**Pelacakan Terdistribusi**:
- Integrasi Jaeger atau Zipkin
- Lacak permintaan antar layanan
- Identifikasi hambatan
- Men-debug masalah kinerja

---

## Topologi Penerapan

### Lingkungan Pengembangan

§§§KODE_15§§§

### Lingkungan Pementasan

§§§KODE_16§§§

### Lingkungan Produksi

§§§KODE_17§§§

---

## Justifikasi Pilihan Teknologi

### Mengapa Airbyte?

- **300+ konektor**: Integrasi bawaan
- **Sumber terbuka**: Tidak ada penguncian pemasok
- **Komunitas aktif**: 12k+ bintang GitHub
- **Dukungan CDC**: Pengambilan data waktu nyata
- **Standarisasi**: Integrasi dbt bawaan

### Mengapa Dremio?

- **Akselerasi kueri**: Kueri 10-100x lebih cepat
- **Penerbangan Panah**: Transfer data berkinerja tinggi
- **Kompatibilitas data lake**: Tidak ada pergerakan data
- **Layanan mandiri**: Pengguna bisnis menjelajahi data
- **Menguntungkan**: Mengurangi biaya gudang

### Mengapa harus dbt?

- **Berbasis SQL**: Familiar bagi analis
- **Kontrol versi**: Integrasi Git
- **Tes**: Uji kualitas data terintegrasi
- **Dokumentasi**: Dokumen yang dibuat secara otomatis
- **Komunitas**: tersedia 5k+ paket

### Mengapa Superset?

- **UI Modern**: Antarmuka intuitif
- **SQL IDE**: Kemampuan kueri tingkat lanjut
- **Visualisasi kaya**: 50+ jenis grafik
- **Dapat Diperluas**: Plugin khusus
- **Sumber terbuka**: Apache Foundation yang didukung

### Mengapa PostgreSQL?

- **Keandalan**: Kepatuhan ACID
- **Kinerja**: Terbukti dalam skala besar
- **Fitur**: JSON, pencarian teks lengkap, ekstensi
- **Komunitas**: Ekosistem yang matang
- **Biaya**: Gratis dan sumber terbuka

### Mengapa MinIO?

- **Kompatibilitas S3**: API standar industri
- **Kinerja**: Laju aliran tinggi
- **Penghapusan kode**: Daya tahan data
- **Multi-cloud**: Terapkan di mana saja
- **Hemat biaya**: Alternatif yang dihosting sendiri

---

## Evolusi Arsitektur Masa Depan

### Perbaikan yang Direncanakan

1. **Katalog Data** (Integrasi OpenMetadata)
   - Manajemen metadata
   - Pelacakan silsilah
   - Penemuan data

2. **Kualitas Data** (Harapan Besar)
   - Validasi otomatis
   - Deteksi anomali
   - Dasbor berkualitas

3. **Operasi ML** (MLflow)
   - Model saluran pelatihan
   - Daftar model
   - Otomatisasi penerapan

4. **Pemrosesan streaming** (Apache Flink)
   - Transformasi waktu nyata
   - Pemrosesan acara yang kompleks
   - Analisis streaming

5. **Tata Kelola Data** (Apache Atlas)
   - Penerapan kebijakan
   - Akses audit
   - Laporan kepatuhan

---

## Referensi

- [Rincian Komponen](components.md)
- [Aliran Data](data-flow.md)
- [Panduan Penerapan](deployment.md)
- [Integrasi Airbyte](../guides/airbyte-integration.md)

---

**Versi Ikhtisar Arsitektur**: 3.2.0  
**Terakhir Diperbarui**: 16-10-2025  
**Dikelola Oleh**: Tim Platform Data