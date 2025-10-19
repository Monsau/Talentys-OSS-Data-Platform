# Panduan Dasbor Apache Superset

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Konfigurasi Awal](#konfigurasi awal)
3. [Koneksi Sumber Data](#koneksi-sumber-data)
4. [Pembuatan Grafis](#pembuatan grafis)
5. [Konstruksi Dasbor](#konstruksi-dasbor)
6. [Fitur Lanjutan](#fitur-lanjutan)
7. [Keamanan dan Izin](#keamanan-dan-izin)
8. [Optimasi Kinerja](#optimasi kinerja)
9. [Integrasi dan Berbagi](#integrasi-dan-berbagi)
10. [Praktik yang Baik](#praktik yang baik)

---

## Ringkasan

Apache Superset adalah aplikasi web intelijen bisnis modern dan siap pakai yang memungkinkan pengguna menjelajahi dan memvisualisasikan data melalui dasbor dan bagan intuitif.

### Fitur Utama

| Fitur | Deskripsi | Keuntungan |
|----------------|---------|---------|
| **IDE SQL** | Editor SQL interaktif dengan pelengkapan otomatis | Analisis ad-hoc |
| **Visualisasi Kaya** | 50+ jenis bagan | Berbagai representasi data |
| **Pembuat Dasbor** | Antarmuka seret dan lepas | Pembuatan dasbor yang mudah |
| **Caching** | Kueri hasil cache | Waktu pemuatan cepat |
| **Keamanan** | Keamanan tingkat baris, akses berbasis peran | Tata Kelola Data |
| **Peringatan** | Notifikasi email/Slack otomatis | Pemantauan proaktif |

### Integrasi Arsitektur

§§§KODE_0§§§

---

## Konfigurasi Awal

### Koneksi Pertama

Akses Superset di `http://localhost:8088`:

§§§KODE_2§§§

**Catatan Keamanan**: Ubah kata sandi default segera setelah login pertama.

### Pengaturan Awal

§§§KODE_3§§§

### Berkas Konfigurasi

§§§KODE_4§§§

---

## Koneksi Sumber Data

### Masuk ke Dremio

#### Langkah 1: Instal Driver Basis Data Dremio

§§§KODE_5§§§

#### Langkah 2: Tambahkan Basis Data Dremio

§§§KODE_6§§§

**Konfigurasi**:
§§§KODE_7§§§

#### Langkah 3: Uji Koneksi

§§§KODE_8§§§

### Menghubungkan ke PostgreSQL

§§§KODE_9§§§

### Menghubungkan ke Elasticsearch

§§§KODE_10§§§

---

## Pembuatan Grafik

### Alur Kerja Pembuatan Grafis

§§§KODE_11§§§

### Pemilihan Tipe Grafis

| Tipe Grafis | Terbaik Untuk | Contoh Kasus Penggunaan |
|----------------|---------------|---------------------|
| **Bagan Linier** | Tren temporal | Tren pendapatan harian |
| **Bagan Batang** | Perbandingan | Pendapatan berdasarkan kategori produk |
| **Bagan Sektor** | Bagian dari total | Pangsa pasar berdasarkan wilayah |
| **Tabel** | Data rinci | Daftar pelanggan dengan metrik |
| **Jumlah Besar** | Metrik Tunggal | Total Pendapatan Tahun Berjalan |
| **Kartu Panas** | Deteksi pola | Penjualan per hari/jam |
| **Titik Awan** | Korelasi | Nilai pelanggan vs frekuensi |
| **Diagram Sankey** | Analisis aliran | Perjalanan pengguna |

### Contoh: Grafik Linier (Tren Pendapatan)

#### Langkah 1: Buat Kumpulan Data

§§§KODE_12§§§

**Konfigurasi**:
- **Pangkalan Data**: Dremio
- **Diagram**: Produksi.Mart
- **Tabel**: pendapatan_harian_mart

#### Langkah 2: Buat Bagan

§§§KODE_13§§§

**Parameter**:
§§§KODE_14§§§

**SQL Dihasilkan**:
§§§KODE_15§§§

### Contoh: Bar Chart (Pelanggan Teratas)

§§§KODE_16§§§

### Contoh: PivotTable

§§§KODE_17§§§

### Contoh: Angka Besar dengan Trend

§§§KODE_18§§§

---

## Dasbor Konstruksi

### Proses Pembuatan Dasbor

§§§KODE_19§§§

### Langkah 1: Buat Dasbor

§§§KODE_20§§§

**Pengaturan Dasbor**:
§§§KODE_21§§§

### Langkah 2: Tambahkan Grafik

Seret dan lepas grafik dari panel kiri atau buat yang baru:

§§§KODE_22§§§

### Langkah 3: Desain Tata Letak

**Sistem Grid**:
- Lebar 12 kolom
- Grafik masuk ke grid
- Gesek untuk mengubah ukuran dan memposisikan ulang

**Contoh Tata Letak**:
§§§KODE_23§§§

### Langkah 4: Tambahkan Filter Dasbor

§§§KODE_24§§§

**Filter Rentang Tanggal**:
§§§KODE_25§§§

**Filter Kategori**:
§§§KODE_26§§§

**Filter Digital**:
§§§KODE_27§§§

### Langkah 5: Penyaringan Silang

Aktifkan pemfilteran silang dasbor:

§§§KODE_28§§§

**Konfigurasi**:
§§§KODE_29§§§

**Pengalaman Pengguna**:
- Klik pada bilah → filter seluruh dasbor
- Klik pada pembagian sektor → perbarui grafik terkait
- Hapus filter → atur ulang ke tampilan default

---

## Fitur Lanjutan

### Laboratorium SQL

Editor SQL interaktif untuk kueri ad-hoc.

#### Jalankan Kueri

§§§KODE_30§§§

**Fitur**:
- Penyelesaian otomatis untuk tabel dan kolom
- Minta riwayat
- Banyak tab
- Ekspor hasil (CSV, JSON)
- Simpan permintaan untuk digunakan kembali

#### Membuat Tabel dari Query (CTAS)

§§§KODE_31§§§

### Templat Jinja

SQL dinamis dengan templat Jinja2:

§§§KODE_32§§§

**Variabel Templat**:
- `{{ from_dttm }}` - Rentang tanggal mulai
- `{{ to_dttm }}` - Rentang tanggal akhir
- `{{ filter_values('column') }}` - Nilai filter yang dipilih
- `{{ current_username }}` - Pengguna yang masuk

### Peringatan dan Laporan

#### Buat Peringatan

§§§KODE_37§§§

**Konfigurasi**:
§§§KODE_38§§§

#### Buat Laporan

§§§KODE_39§§§

### Plugin Visualisasi Khusus

Buat tipe grafik khusus:

§§§KODE_40§§§

Bangun dan pasang:
§§§KODE_41§§§

---

## Keamanan dan Izin

### Kontrol Akses Berbasis Peran (RBAC)

§§§KODE_42§§§

### Peran Terintegrasi

| Peran | Izin | Kasus Penggunaan |
|------|-------------|-------------|
| **Admin** | Semua izin | Administrator sistem |
| **Alfa** | Membuat, mengedit, menghapus dasbor/grafik | Analis data |
| **Gamma** | Lihat dasbor, jalankan kueri SQL Lab | Pengguna bisnis |
| **sql_lab** | Hanya akses SQL Lab | Ilmuwan data |
| **Publik** | Lihat dasbor publik saja | Pengguna anonim |

### Buat Peran Khusus

§§§KODE_43§§§

**Contoh: Peran Analis Pemasaran**
§§§KODE_44§§§

### Keamanan Tingkat Jalur (RLS)

Batasi data berdasarkan atribut pengguna:

§§§KODE_45§§§

**Contoh: RLS Berbasis Wilayah**
§§§KODE_46§§§

**Contoh: RLS Berbasis Klien**
§§§KODE_47§§§

### Keamanan Koneksi Basis Data

§§§KODE_48§§§

---

## Optimasi Kinerja

### Kueri Caching

§§§KODE_49§§§

**Strategi Tembolok**:
§§§KODE_50§§§

### Permintaan Asinkron

Aktifkan eksekusi kueri asinkron untuk kueri panjang:

§§§KODE_51§§§

### Optimasi Kueri Basis Data

§§§KODE_52§§§

### Optimasi Pemuatan Dasbor

§§§KODE_53§§§

### Pemantauan Kinerja

§§§KODE_54§§§

---

## Integrasi dan Berbagi

### Dasbor Publik

Jadikan dasbor dapat diakses tanpa koneksi:

§§§KODE_55§§§

**URL Publik**:
§§§KODE_56§§§

### Integrasi iframe

Integrasikan dasbor ke dalam aplikasi eksternal:

§§§KODE_57§§§

**Pengaturan Integrasi**:
- `standalone=1` - Sembunyikan navigasi
- `show_filters=0` - Sembunyikan panel filter
- `show_title=0` - Sembunyikan judul dasbor

### Otentikasi Token Tamu

Akses terprogram untuk dasbor terintegrasi:

§§§KODE_61§§§

### Ekspor Dasbor

§§§KODE_62§§§

---

## Praktik Terbaik

### Desain Dasbor

1. **Hierarki Tata Letak**
   §§§KODE_63§§§

2. **Konsistensi Warna**
   - Gunakan skema warna yang konsisten di semua dasbor
   - Hijau untuk metrik positif, merah untuk metrik negatif
   - Warna merek untuk kategori

3. **Kinerja**
   - Batasi grafik per dasbor (<15)
   - Gunakan tingkat agregasi yang sesuai
   - Aktifkan cache untuk data statis
   - Tetapkan batas garis yang masuk akal

4. **Interaktivitas**
   - Tambahkan filter yang bermakna
   - Aktifkan pemfilteran silang untuk eksplorasi
   - Menyediakan kemampuan menelusuri

### Pilihan Grafis

| Tipe Data | Grafik yang Direkomendasikan | Hindari |
|--------------|----------------------------|--------|
| **Rangkaian Waktu** | Linier, Luas | Sektor, Cincin |
| **Perbandingan** | Batang, Kolom | Linear (beberapa titik data) |
| **Bagian dari Total** | Sektor, Lingkaran, Peta Hierarki | Batangan (juga kategori) |
| **Distribusi** | Histogram, Plot Kotak | Sektor |
| **Korelasi** | Titik Awan, Gelembung | Batangan |
| **Geografis** | Peta, Choropleth | Tabel |

### Optimasi Kueri

§§§KODE_64§§§

### Keamanan

1. **Kontrol Akses**
   - Gunakan RBAC untuk manajemen pengguna
   - Menerapkan RLS untuk isolasi data
   - Batasi koneksi database berdasarkan peran

2. **Tata Kelola Data**
   - Properti kumpulan data dokumen
   - Tentukan jadwal penyegaran data
   - Pantau kinerja kueri

3. **Kepatuhan**
   - Sembunyikan PII dalam visualisasi
   - Akses dasbor audit
   - Menerapkan kebijakan penyimpanan data

---

## Ringkasan

Panduan Superset komprehensif ini telah mencakup:

- **Konfigurasi**: Instalasi, konfigurasi, koneksi database
- **Grafik**: Lebih dari 50 tipe grafik, konfigurasi, pembuatan SQL
- **Dasbor**: Desain tata letak, filter, pemfilteran silang
- **Fitur Lanjutan**: Lab SQL, templat Jinja, peringatan, plugin khusus
- **Keamanan**: RBAC, RLS, keamanan koneksi database
- **Kinerja**: Caching, kueri asinkron, pengoptimalan kueri
- **Integrasi**: Dasbor publik, integrasi iframe, token tamu
- **Praktik yang Baik**: Prinsip desain, pemilihan grafis, keamanan

Poin-poin penting yang perlu diingat:
- Superset terhubung ke Dremio untuk analisis kinerja tinggi
- Pustaka visualisasi yang kaya mendukung berbagai kasus penggunaan
- Caching bawaan dan kueri asinkron memastikan dasbor cepat
- RBAC dan RLS memungkinkan analisis layanan mandiri yang aman
- Kemampuan integrasi memungkinkan integrasi dengan aplikasi eksternal

**Dokumentasi Terkait:**
- [Panduan Pengaturan Dremio](./dremio-setup.md)
- [Arsitektur: Aliran Data](../architecture/data-flow.md)
- [Tutorial Langkah Pertama](../getting-started/first-steps.md)
- [Panduan Kualitas Data](./data-quality.md)

---

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025