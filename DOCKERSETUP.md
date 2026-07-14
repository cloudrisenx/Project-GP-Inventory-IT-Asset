# 🐳 Panduan Setup Docker - IT Asset Management

Dokumen ini memandu Anda melakukan deployment dan menjalankan aplikasi **IT Asset Management - Griya Persada Hotel & Resort** di lingkungan terisolasi menggunakan **Docker** dan **Docker Compose**.

---

## 🏛️ Arsitektur Container

Setup ini terdiri dari dua container utama yang berjalan di dalam network terisolasi yang sama:

1.  **`gp_inventory_web`** (Aplikasi Flask):
    *   Menggunakan base image `python:3.10-slim`.
    *   Dipasang dependensi sistem (`libpq-dev` & `gcc`) untuk menghubungkan database PostgreSQL.
    *   Expose port `5000:5000`.
2.  **`gp_inventory_db`** (Database PostgreSQL 15):
    *   Menggunakan image `postgres:15-alpine`.
    *   Volume persisten `pgdata` untuk menyimpan database secara aman.
    *   Secara otomatis mengimpor data awal dari `backup_inventory_db.sql` pada startup pertama.

---

## ⚙️ Persyaratan Sistem

Sebelum memulai, pastikan Anda telah memasang:
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS) atau Docker Engine & Docker Compose (Linux).

---

## 🚀 Panduan Memulai (Quick Start)

### 1. Sesuaikan Konfigurasi Kredensial
Sebelum menjalankan container, buka file [docker-compose.yml](file:///g:/Project_magang/Project-GP-Inventory-IT-Asset/docker-compose.yml) dan sesuaikan variabel sandi di bawah ini untuk keamanan:

```yaml
# Pada Service 'web'
- DB_PASSWORD=password_postgres_kamu

# Pada Service 'db'
POSTGRES_PASSWORD: password_postgres_kamu
```

> [!IMPORTANT]
> Pastikan nilai `DB_PASSWORD` pada service `web` **sama persis** dengan `POSTGRES_PASSWORD` pada service `db`.

### 2. Build & Jalankan Container
Jalankan perintah berikut di direktori root project untuk membangun image dan mengaktifkan container di latar belakang (*detached mode*):

```bash
docker compose up --build -d
```

### 3. Verifikasi Container Berjalan
Untuk memastikan semua container aktif tanpa masalah:

```bash
# Periksa status kontainer
docker compose ps

# Periksa log aktif untuk memastikan tidak ada error startup
docker compose logs -f
```

---

## 🔗 Mengakses Aplikasi

Karena aplikasi ini dikonfigurasi menggunakan WSGI middleware [ReverseProxied](file:///g:/Project_magang/Project-GP-Inventory-IT-Asset/Web/middleware/reverse_proxy.py) dengan subpath `/inventory`, aplikasi harus diakses menggunakan URL berikut:

*   **Halaman Utama / Login**: [http://localhost:5000/inventory](http://localhost:5000/inventory)
*   **Halaman Detail Aset (QR Scan)**: `http://localhost:5000/inventory/scan/<barcode_id>`

---

## 🛠️ Menjalankan Utilitas di Dalam Container

Anda dapat memicu script Python di dalam container `gp_inventory_web` tanpa perlu keluar dari host machine.

### 1. Mereset Kata Sandi Pengguna (`admin` dan `guest`)
Jika Anda perlu mereset sandi bawaan pengguna ke `admin123`, jalankan perintah berikut:

```bash
docker compose exec web python resetpw.py
```

### 2. Membuka PostgreSQL CLI (psql)
Untuk berinteraksi langsung dengan database di dalam container:

```bash
docker compose exec db psql -U postgres -d inventory_db
```

---

## 🧹 Menghentikan & Mereset Database

*   **Menghentikan Container**:
    ```bash
    docker compose down
    ```
*   **Menghapus Container & Volume Data (Pembersihan Total)**:
    Jika Anda ingin menghapus seluruh data database dan mengimpor ulang dari file `backup_inventory_db.sql` pada startup berikutnya:
    ```bash
    docker compose down -v
    ```

---

## ❓ Troubleshooting (Penanganan Masalah)

*   **Port 5000 atau 5432 Sudah Digunakan**:
    Jika port lokal Anda tabrakan dengan aplikasi lain, ubah port mapping pada sisi kiri tanda titik dua `:` di file [docker-compose.yml](file:///g:/Project_magang/Project-GP-Inventory-IT-Asset/docker-compose.yml):
    ```yaml
    ports:
      - "5001:5000" # Mengubah port akses web host menjadi 5001
    ```
*   **Database Tidak Terisi Otomatis**:
    Proses inisialisasi otomatis `/docker-entrypoint-initdb.d/init.sql` hanya berjalan **sekali** saat folder data PostgreSQL kosong. Jika database gagal terisi, jalankan `docker compose down -v` terlebih dahulu lalu nyalakan ulang dengan `docker compose up -d` untuk memicu inisialisasi ulang.
