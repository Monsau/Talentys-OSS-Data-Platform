# Referensi API Airbyte

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Otentikasi](#autentikasi)
3. [Ruang Kerja](#ruang kerja)
4. [Sumber](#sumber)
5. [Tujuan](#tujuan)
6. [Koneksi](#koneksi)
7. [Pekerjaan dan sinkronisasi](#pekerjaan-dan-sinkronisasi)
8. [Contoh Python](#contoh-python)

---

## Ringkasan

Airbyte API memungkinkan pengelolaan saluran data terprogram.

**URL Dasar**: `http://localhost:8001/api/v1`

### Arsitektur API

§§§KODE_1§§§

---

## Otentikasi

Airbyte menggunakan otentikasi dasar dalam penerapan Docker.

§§§KODE_2§§§

---

## Ruang Kerja

### Daftar ruang kerja

§§§KODE_3§§§

**Menjawab** :
§§§KODE_4§§§

### Dapatkan ruang kerja

§§§KODE_5§§§

---

## Sumber

### Daftar definisi sumber

§§§KODE_6§§§

**Jawab**: Daftar lebih dari 300 konektor sumber yang tersedia

### Dapatkan definisi sumber

§§§KODE_7§§§

### Buat sumber

#### Sumber PostgreSQL

§§§KODE_8§§§

**Menjawab** :
§§§KODE_9§§§

#### Sumber API

§§§KODE_10§§§

### Uji koneksi sumber

§§§KODE_11§§§

**Menjawab** :
§§§KODE_12§§§

### Daftar sumber

§§§KODE_13§§§

---

## Tujuan

### Buat tujuan (S3/MinIO)

§§§KODE_14§§§

### Buat tujuan (PostgreSQL)

§§§KODE_15§§§

### Uji koneksi tujuan

§§§KODE_16§§§

---

## Koneksi

### Temukan diagramnya

§§§KODE_17§§§

**Menjawab** :
§§§KODE_18§§§

### Buat koneksi

§§§KODE_19§§§

### Pembantu Python

§§§KODE_20§§§

### Perbarui koneksi

§§§KODE_21§§§

---

## Pekerjaan dan sinkronisasi

### Memicu sinkronisasi manual

§§§KODE_22§§§

**Menjawab** :
§§§KODE_23§§§

### Mendapatkan status pekerjaan

§§§KODE_24§§§

**Menjawab** :
§§§KODE_25§§§

### Pantau kemajuan pekerjaan

§§§KODE_26§§§

### Daftar tugas koneksi

§§§KODE_27§§§

### Membatalkan pekerjaan

§§§KODE_28§§§

---

## Contoh Python

### Selesaikan konfigurasi saluran

§§§KODE_29§§§

---

## Ringkasan

Referensi API ini mencakup:

- **Ruang Kerja**: Dapatkan konteks ruang kerja
- **Sumber**: Lebih dari 300 konektor (PostgreSQL, API, database)
- **Tujuan**: S3/MinIO, PostgreSQL, gudang data
- **Koneksi**: Konfigurasi sinkronisasi dengan penjadwalan
- **Pekerjaan**: Memicu, memantau, dan mengelola sinkronisasi
- **Klien Python**: Contoh otomatisasi lengkap

**Poin penting**:
- Gunakan REST API untuk otomatisasi lengkap
- Uji koneksi sebelum membuat sinkronisasi
- Pantau status pekerjaan untuk jalur produksi
- Gunakan sinkronisasi tambahan dengan bidang kursor
- Rencanakan sinkronisasi berdasarkan kebutuhan kesegaran data

**Dokumentasi terkait:**
- [Panduan Integrasi Airbyte](../guides/airbyte-integration.md)
- [Arsitektur: Aliran Data](../architecture/data-flow.md)
- [Panduan Mengatasi Masalah](../guides/troubleshooting.md)

---

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025