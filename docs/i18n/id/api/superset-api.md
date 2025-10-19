# Referensi API Superset

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025  
**Bahasa**: Prancis

## Daftar isi

1. [Ikhtisar](#ikhtisar)
2. [Otentikasi](#autentikasi)
3. [Dasbor](#dasbor)
4. [Grafik](#grafis)
5. [Kumpulan Data](#Kumpulan Data)
6. [Lab SQL](#lab-sql)
7. [Keamanan](#keamanan)
8. [Contoh Python](#contoh-python)

---

## Ringkasan

Apache Superset menyediakan REST API untuk akses terprogram.

**URL Dasar**: `http://localhost:8088/api/v1`

### Arsitektur API

§§§KODE_1§§§

---

## Otentikasi

### Masuk

**Titik akhir**: `POST /api/v1/security/login`

§§§KODE_3§§§

**Menjawab** :
§§§KODE_4§§§

### Segarkan token

**Titik akhir**: `POST /api/v1/security/refresh`

§§§KODE_6§§§

### Pembantu Otentikasi Python

§§§KODE_7§§§

---

## Dasbor

### Daftar dasbor

**Titik akhir**: `GET /api/v1/dashboard/`

§§§KODE_9§§§

**Menjawab** :
§§§KODE_10§§§

### Dapatkan dasbor

**Titik akhir**: `GET /api/v1/dashboard/{id}`

§§§KODE_12§§§

**Menjawab** :
§§§KODE_13§§§

### Buat dasbor

**Titik akhir**: `POST /api/v1/dashboard/`

§§§KODE_15§§§

### Contoh Python

§§§KODE_16§§§

### Perbarui dasbor

**Titik akhir**: `PUT /api/v1/dashboard/{id}`

§§§KODE_18§§§

### Hapus dasbor

**Titik akhir**: `DELETE /api/v1/dashboard/{id}`

§§§KODE_20§§§

### Ekspor dasbor

**Titik akhir**: `GET /api/v1/dashboard/export/`

§§§KODE_22§§§

### Impor dasbor

**Titik akhir**: `POST /api/v1/dashboard/import/`

§§§KODE_24§§§

---

## Grafik

### Daftar grafik

**Titik akhir**: `GET /api/v1/chart/`

§§§KODE_26§§§

### Dapatkan grafik

**Titik akhir**: `GET /api/v1/chart/{id}`

§§§KODE_28§§§

**Menjawab** :
§§§KODE_29§§§

### Buat bagan

**Titik akhir**: `POST /api/v1/chart/`

§§§KODE_31§§§

### Dapatkan data dari grafik

**Titik akhir**: `POST /api/v1/chart/data`

§§§KODE_33§§§

**Menjawab** :
§§§KODE_34§§§

---

## Kumpulan data

### Daftar kumpulan data

**Titik akhir**: `GET /api/v1/dataset/`

§§§KODE_36§§§

### Dapatkan kumpulan data

**Titik akhir**: `GET /api/v1/dataset/{id}`

§§§KODE_38§§§

**Menjawab** :
§§§KODE_39§§§

### Buat kumpulan data

**Titik akhir**: `POST /api/v1/dataset/`

§§§KODE_41§§§

### Tambahkan metrik terhitung

**Titik akhir**: `POST /api/v1/dataset/{id}/metric`

§§§KODE_43§§§

---

## Laboratorium SQL

### Jalankan kueri SQL

**Titik akhir**: `POST /api/v1/sqllab/execute/`

§§§KODE_45§§§

**Menjawab** :
§§§KODE_46§§§

### Eksekusi Python SQL

§§§KODE_47§§§

### Dapatkan hasil kueri

**Titik akhir**: `GET /api/v1/sqllab/results/{query_id}`

§§§KODE_49§§§

---

## Keamanan

### Token tamu

**Titik akhir**: `POST /api/v1/security/guest_token/`

§§§KODE_51§§§

### Daftar peran

**Titik akhir**: `GET /api/v1/security/roles/`

§§§KODE_53§§§

### Buat pengguna

**Titik akhir**: `POST /api/v1/security/users/`

§§§KODE_55§§§

---

## Contoh Python

### Otomatisasi dasbor lengkap

§§§KODE_56§§§

### Ekspor dasbor secara batch

§§§KODE_57§§§

---

## Ringkasan

Referensi API ini mencakup:

- **Otentikasi**: Otentikasi berdasarkan token JWT
- **Dasbor**: Operasi CRUD, ekspor/impor
- **Bagan**: Membuat, memperbarui, mengkueri data
- **Kumpulan Data**: Pengelolaan tabel/tampilan, metrik
- **SQL Lab**: Menjalankan kueri secara terprogram
- **Keamanan**: Token tamu, pengguna, peran
- **Contoh Python**: Skrip otomatisasi lengkap

**Poin-poin penting**:
- Gunakan API untuk otomatisasi dasbor
- Token tamu memungkinkan integrasi yang aman
- SQL Lab API untuk kueri ad-hoc
- Ekspor/impor untuk kontrol versi
- Buat kumpulan data dengan metrik yang dihitung

**Dokumentasi Terkait**:
- [Panduan Dasbor Superset](../guides/superset-dashboards.md)
- [Arsitektur: Aliran Data](../architecture/data-flow.md)
- [Panduan Mengatasi Masalah](../guides/troubleshooting.md)

---

**Versi**: 3.2.0  
**Terakhir diperbarui**: 16 Oktober 2025