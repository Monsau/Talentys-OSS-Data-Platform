# Panduan Kualitas Data

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Kerangka Kualitas Data](#kerangka kualitas data)
3. [tes dbt](#tes dbt)
4. [Integrasi Harapan Besar](#integrasi-harapan besar)
5. [Aturan Validasi Data](#aturan-validasi-data)
6. [Pemantauan dan Peringatan](#pemantauan-dan-peringatan)
7. [Metrik Kualitas Data](#metrik kualitas data)
8. [Strategi Remediasi](#strategi-remediasi)
9. [Praktik yang Baik](#praktik yang baik)
10. [Studi Kasus](#studi kasus)

---

## Ringkasan

Kualitas data sangat penting untuk analisis dan pengambilan keputusan yang andal. Panduan ini mencakup strategi komprehensif untuk memastikan, memantau, dan meningkatkan kualitas data di seluruh platform.

### Mengapa Kualitas Data Penting

§§§KODE_0§§§

### Dimensi Kualitas Data

| Dimensi | Deskripsi | Contoh Verifikasi |
|----------|-------------|----------------------|
| **Akurasi** | Data mewakili kenyataan dengan benar | Validasi format email |
| **Kelengkapan** | Tidak diperlukan nilai yang hilang | BUKAN NULL cek |
| **Konsistensi** | Kecocokan data antar sistem | Hubungan luar negeri utama |
| **Berita** | Data terkini dan tersedia bila diperlukan | Pemeriksaan kesegaran |
| **Validitas** | Data sesuai dengan aturan bisnis | Pemeriksaan rentang nilai |
| **Keunikan** | Tidak ada catatan duplikat | Keunikan kunci utama |

---

## Kerangka Kualitas Data

### Kualitas Pintu Arsitektur

§§§KODE_1§§§

### Popok Berkualitas

§§§KODE_2§§§

---

## tes dbt

### Tes Terpadu

#### Tes Generik

§§§KODE_3§§§

#### Tes Hubungan

§§§KODE_4§§§

### Tes yang Dipersonalisasi

#### Tes Tunggal

§§§KODE_5§§§

§§§KODE_6§§§

§§§KODE_7§§§

#### Makro Uji Generik

§§§KODE_8§§§

§§§KODE_9§§§

§§§KODE_10§§§

Menggunakan:
§§§KODE_11§§§

### Eksekusi Tes

§§§KODE_12§§§

### Konfigurasi Tes

§§§KODE_13§§§

---

## Integrasi Harapan Besar

### Fasilitas

§§§KODE_14§§§

### Pengaturan

§§§KODE_15§§§

Instal paket:
§§§KODE_16§§§

### Menguji Ekspektasi

§§§KODE_17§§§

### Harapan yang Dipersonalisasi

§§§KODE_18§§§

---

## Aturan Validasi Data

### Validasi Logika Bisnis

§§§KODE_19§§§

### Tabel Pemantauan Kualitas Data

§§§KODE_20§§§

---

## Pemantauan dan Peringatan

### Dasbor Metrik Kualitas

§§§KODE_21§§§

### Peringatan Otomatis

§§§KODE_22§§§

### Pemeriksaan Kualitas Data Aliran Udara

§§§KODE_23§§§

---

## Metrik Kualitas Data

### Indikator Kinerja Utama

§§§KODE_24§§§

### Analisis Tren

§§§KODE_25§§§

---

## Strategi Remediasi

### Aturan Pembersihan Data

§§§KODE_26§§§

### Proses Karantina

§§§KODE_27§§§

---

## Praktik Terbaik

### 1. Tes Sejak Dini dan Sering

§§§KODE_28§§§

### 2. Gunakan Tingkat Keparahan

§§§KODE_29§§§

### 3. Aturan Kualitas Data Dokumen

§§§KODE_30§§§

### 4. Pantau Tren, Bukan Hanya Poin

§§§KODE_31§§§

### 5. Otomatiskan Remediasi Jika Memungkinkan

§§§KODE_32§§§

---

## Studi Kasus

### Studi Kasus 1: Validasi Email

**Masalah**: 15% email pelanggan tidak valid (@tidak ada, format salah)

**Larutan**:
§§§KODE_33§§§

**Remediasi**:
§§§KODE_34§§§

**Hasil**: Email tidak valid berkurang dari 15% menjadi 2%

### Studi Kasus 2: Kesalahan Perhitungan Pendapatan

**Masalah**: 5% pesanan memiliki jumlah_total ≠ jumlah + pajak + ongkos kirim

**Larutan**:
§§§KODE_35§§§

**Remediasi**:
§§§KODE_36§§§

**Hasil**: Kesalahan penghitungan berkurang hingga <0,1%

---

## Ringkasan

Panduan kualitas data komprehensif ini mencakup:

- **Kerangka**: Pintu, lapisan, arsitektur berkualitas
- **tes dbt**: Tes terintegrasi, tes yang dipersonalisasi, tes makro generik
- **Ekspektasi Besar**: Validasi tingkat lanjut dengan lebih dari 50 jenis ekspektasi
- **Aturan Validasi**: Logika bisnis, penilaian kualitas, tabel pemantauan
- **Pemantauan**: Peringatan otomatis, integrasi Aliran Udara, dasbor
- **Metrik**: KPI, analisis tren, penilaian kualitas
- **Remediasi**: Aturan kebersihan, proses karantina, koreksi otomatis
- **Praktik yang Baik**: Uji lebih awal, gunakan tingkat keparahan, pantau tren
- **Studi Kasus**: Contoh nyata dan solusinya

Poin-poin penting yang perlu diingat:
- Menerapkan pemeriksaan kualitas di setiap lapisan (Perunggu → Perak → Emas)
- Gunakan tes dbt untuk validasi struktural, Harapan Besar untuk validasi statistik
- Pantau tren temporal, bukan hanya metrik titik waktu
- Mengotomatiskan remediasi untuk masalah umum dan dapat diprediksi
- Waspada tentang penurunan kualitas sebelum dampak bisnis
- Mendokumentasikan aturan kualitas dan strategi remediasi

**Dokumentasi Terkait:**
- [Panduan Pengembangan dbt](./dbt-development.md)
- [Arsitektur: Aliran Data](../architecture/data-flow.md)
- [Panduan Pengaturan Dremio](./dremio-setup.md)
- [Panduan Mengatasi Masalah](./troubleshooting.md)

---

**Versi**: 3.2.0  
**Pembaruan Terakhir**: 16 Oktober 2025