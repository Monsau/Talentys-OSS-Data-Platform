# Referensi API Dremio

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Otentikasi](#autentikasi)
3. [REST API](#api-rest)
4. [Panah Penerbangan SQL](#panah-penerbangan-sql)
5. [ODBC/JDBC](#odbcjdbc)
6. [Klien Python](#klien-python)
7. [Klien Java](#klien Java)
8. [Contoh API](#dapi-contoh)

---

## Ringkasan

Dremio menyediakan beberapa API untuk berinteraksi dengan data lakehouse:

| Jenis API | Kasus penggunaan | Pelabuhan | Protokol |
|------------|--------|------|----------|
| API REST | Manajemen, metadata | 9047 | HTTP/HTTPS |
| PanahFlightSQL | Kueri berkinerja tinggi | 32010 | gRPC |
| ODBC | Konektivitas alat BI | 31010 | ODBC |
| JDBC | Aplikasi Java | 31010 | JDBC |

### Arsitektur API

§§§KODE_0§§§

---

## Otentikasi

### Buat token autentikasi

**Titik akhir**: `POST /apiv2/login`

**Meminta** :
§§§KODE_2§§§

**Menjawab** :
§§§KODE_3§§§

### Gunakan token dalam permintaan

§§§KODE_4§§§

### Kedaluwarsa token

Token akan kedaluwarsa setelah 24 jam secara default. Konfigurasikan dalam `dremio.conf`:

§§§KODE_6§§§

---

## API REST

### URL Dasar

§§§KODE_7§§§

### Header umum

§§§KODE_8§§§

### Manajemen katalog

#### Daftar item katalog

**Titik akhir**: `GET /catalog`

§§§KODE_10§§§

**Menjawab** :
§§§KODE_11§§§

#### Dapatkan item katalog berdasarkan jalur

**Titik akhir**: `GET /catalog/by-path/{path}`

§§§KODE_13§§§

**Menjawab** :
§§§KODE_14§§§

### Kumpulan Data Virtual (VDS)

#### Membuat kumpulan data virtual

**Titik akhir**: `POST /catalog`

§§§KODE_16§§§

**Menjawab** :
§§§KODE_17§§§

#### Perbarui kumpulan data virtual

**Titik akhir**: `PUT /catalog/{id}`

§§§KODE_19§§§

#### Menghapus kumpulan data

**Titik akhir**: `DELETE /catalog/{id}?tag={tag}`

§§§KODE_21§§§

### Eksekusi SQL

#### Jalankan kueri SQL

**Titik akhir**: `POST /sql`

§§§KODE_23§§§

**Menjawab** :
§§§KODE_24§§§

### Manajemen pekerjaan

#### Mendapatkan status pekerjaan

**Titik akhir**: `GET /job/{jobId}`

§§§KODE_26§§§

**Menjawab** :
§§§KODE_27§§§

#### Cantumkan pekerjaan terkini

**Titik akhir**: `GET /jobs`

§§§KODE_29§§§

#### Membatalkan pekerjaan

**Titik akhir**: `POST /job/{jobId}/cancel`

§§§KODE_31§§§

###Refleksi

#### Daftar refleksi

**Titik akhir**: `GET /reflections`

§§§KODE_33§§§

**Menjawab** :
§§§KODE_34§§§

#### Membuat refleksi

**Titik akhir**: `POST /reflections`

§§§KODE_36§§§

### Manajemen sumber

#### Tambahkan sumber S3

**Titik akhir**: `PUT /source/{name}`

§§§KODE_38§§§

#### Segarkan metadata sumber

**Titik akhir**: `POST /source/{name}/refresh`

§§§KODE_40§§§

---

## Panah Penerbangan SQL

Arrow Flight SQL menyediakan eksekusi kueri berkinerja tinggi (20-50x lebih cepat dibandingkan ODBC/JDBC).

### Klien Python dengan PyArrow

#### Fasilitas

§§§KODE_41§§§

#### Koneksi dan kueri

§§§KODE_42§§§

#### Contoh: Kueri dengan parameter

§§§KODE_43§§§

#### Pemrosesan batch

§§§KODE_44§§§

### Perbandingan kinerja

§§§KODE_45§§§

---

## ODBC/JDBC

### Koneksi ODBC

#### Pengaturan Windows

1. **Unduh driver ODBC**:
   §§§KODE_46§§§

2. **Konfigurasi DSN**:
   §§§KODE_47§§§

3. **String koneksi**:
   §§§KODE_48§§§

#### Pengaturan Linux

§§§KODE_49§§§

### Koneksi JDBC

#### Unduh drivernya

§§§KODE_50§§§

#### Rangkaian koneksi

§§§KODE_51§§§

#### Properti

§§§KODE_52§§§

---

## Klien Python

### Contoh lengkap

§§§KODE_53§§§

---

## Klien Java

### Ketergantungan Maven

§§§KODE_54§§§

### Contoh lengkap

§§§KODE_55§§§

---

## Contoh API

### Contoh 1: Pelaporan otomatis

§§§KODE_56§§§

### Contoh 2: Ekspor data

§§§KODE_57§§§

### Contoh 3: Penemuan metadata

§§§KODE_58§§§

---

## Ringkasan

Referensi API ini mencakup:

- **Otentikasi**: Autentikasi berbasis token dengan REST API
- **REST API**: Katalog, eksekusi SQL, pekerjaan, refleksi
- **Arrow Flight SQL**: Kueri berperforma tinggi (20-50x lebih cepat)
- **ODBC/JDBC**: Konektivitas alat BI
- **Klien Python**: Menyelesaikan implementasi klien
- **Klien Java**: Contoh JDBC
- **Contoh praktis**: Pelaporan, ekspor, penemuan metadata

**Poin penting**:
- Gunakan Arrow Flight SQL untuk akses data kinerja tinggi
- Gunakan REST API untuk manajemen dan otomatisasi
- Gunakan ODBC/JDBC untuk integrasi alat BI
- Selalu gunakan token otentikasi
- Memproses kueri besar secara berkelompok untuk kinerja yang lebih baik

**Dokumentasi terkait:**
- [Panduan Pengaturan Dremio](../guides/dremio-setup.md)
- [Arsitektur: Aliran Data](../architecture/data-flow.md)
- [panduan pengembangan dbt](../guides/dbt-development.md)

---

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025