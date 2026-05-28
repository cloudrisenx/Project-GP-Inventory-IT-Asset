# 🏢 IT Asset Management System - Griya Persada Hotel & Resort

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12%20%7C%2013%20%7C%2014%20%7C%2015%20%7C%2016-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](#)

Sistem Manajemen Inventaris Aset IT Griya Persada Hotel & Resort adalah aplikasi berbasis web yang dirancang khusus untuk memantau, mendata, dan mengelola seluruh siklus hidup perangkat IT perusahaan secara profesional, terintegrasi, dan presisi.

---

## 🚀 Fitur Utama

Aplikasi ini dilengkapi dengan fitur kelas premium untuk menjamin efisiensi kerja tim IT:

*   🖥️ **Apple-Inspired Elegant UI**: Tampilan antarmuka modern yang bersih dan intuitif dengan dukungan font profesional *Plus Jakarta Sans* dan *JetBrains Mono*.
*   🌓 **Symmetric Dark/Light Mode**: Sinkronisasi tema terintegrasi yang menyimpan preferensi pengguna secara lokal (`localStorage`) dan diwarisi secara otomatis di semua halaman.
*   🏷️ **Smart Auto-Barcode (Tag ID)**: Pembuat nomor kode aset otomatis dengan format standardisasi industri: 
    `MAINGROUP/SUBGROUP-INISIAL_MODEL/LOKASI/TANGGAL_BELI/KODE_HOTEL-001` (misal: `IT/LAP-T14/SRV/2026-05/GPB-001`).
*   📉 **Excel-Style Depreciation Engine**: Kalkulasi penyusutan nilai aset otomatis dari harga beli asli hingga nilai sisa aset saat ini berdasarkan perkiraan usia produktif (menggunakan formula matematika *Excel DATEDIF Style*).
*   🖨️ **Advanced QR Code Labeling**: 
    - Render otomatis QR Code interaktif untuk setiap aset tunggal menggunakan `QRCode.js`.
    - Dilengkapi fitur zoom gambar dan cetak satuan (*ZPL style label*).
    - **Cetak Massal**: Memungkinkan cetak QR Code sekaligus berdasarkan rentang baris data dalam format grid siap print.
*   🔄 **Database Barcode Regenerator**: Fitur sinkronisasi massal untuk memperbarui format barcode seluruh aset di database jika terjadi perubahan kode divisi/kategori terbaru.

---

## 🛠️ Tech Stack & Dependencies

*   **Backend**: Python (Flask Framework)
*   **Database**: PostgreSQL (menggunakan *psycopg2-binary connection pooling* untuk menjamin stabilitas konkurensi data)
*   **Frontend**: HTML5 (Jinja2 Templates), Vanilla CSS (Theme-Aware Variables), Vanilla JavaScript
*   **Keamanan**: `Flask-Login` untuk manajemen sesi admin, enkripsi password `Werkzeug` (PBKDF2-SHA256).

---

## 📁 Struktur Direktori Proyek

```text
├── Web/
│   ├── database/          # Modul koneksi PostgreSQL & Pool management
│   │   ├── pool.py        # Pengatur pool koneksi PostgreSQL
│   │   └── db.py          # Context manager untuk meminjam/melepas koneksi
│   ├── middleware/        # Middleware WSGI (Reverse Proxy helper)
│   │   └── reverse_proxy.py
│   ├── models/            # Struktur representasi data (User)
│   │   └── user.py
│   ├── routes/            # Pengatur logika routing aplikasi (Blueprints)
│   │   ├── auth.py        # Modul Autentikasi Admin & Manajemen User
│   │   ├── assets.py      # Modul Utama Aset (CRUD, Depresiasi, Cetak)
│   │   ├── settings.py    # Modul Pengaturan Kategori, Departemen, & Supplier
│   │   ├── api.py         # RESTful API Endpoint (Autocomplete & Auto-barcode)
│   │   └── scanner.py     # Modul pembaca barcode aset
│   ├── services/          # Kelas utilitas pembantu encoder
│   │   └── helper_service.py
│   ├── static/            # Kumpulan berkas aset statis
│   │   ├── alur_program.xml # Diagram Alur Program (Draw.io compatible)
│   │   ├── erd.xml        # Diagram ERD Database (Draw.io compatible)
│   │   ├── *.css          # Berkas gaya tampilan halaman (Theme-Aware)
│   │   └── *.js           # Logika interaksi frontend
│   ├── templates/         # Berkas HTML template Jinja2
│   ├── config.py          # File konfigurasi utama Flask
│   ├── requirements.txt   # Daftar dependensi modul Python
│   ├── wsgi.py            # Entrypoint WSGI Server Gunicorn
│   ├── app.py             # Inisialisasi awal server Flask
│   └── .env               # Kredensial rahasia (Database & Secret Key)
├── backup_inventory_db.sql # Cadangan database (format SQL)
├── inventory_db.dump      # Cadangan database (format binary dump)
├── README.md              # Dokumentasi proyek ini
└── run.sh                 # Skrip deployment otomatis di Linux (Nginx/Gunicorn)
```

---

## 📊 Visualisasi & Dokumentasi Arsitektur

Kami menyediakan diagram interaktif yang dapat Anda impor langsung ke **[draw.io](https://app.diagrams.net)** untuk memudahkan analisis sistem:

*   **ERD Database (`Web/static/erd.xml`)**: Diagram relasional 6 tabel database (`assets`, `departments`, `categories`, `locations`, `asset_status`, `suppliers`) dengan tipe data, *Primary Key* (PK), *Foreign Key* (FK), dan garis relasi.
*   **Alur Program (`Web/static/alur_program.xml`)**: Flowchart visual yang mendokumentasikan alur data aplikasi dari autentikasi hingga pengelolaan aset dan pencetakan QR Code.

> **Cara Membaca Diagram**: Buka draw.io -> Klik **File > Import From > Device...** -> Pilih salah satu file XML di atas.

---

## ⚙️ Panduan Instalasi & Konfigurasi

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal Anda:

### 1. Prasyarat Sistem
*   Python 3.8 ke atas terinstal di sistem Anda.
*   PostgreSQL server aktif.

### 2. Persiapan Folder & Virtual Environment
Buka terminal/CMD Anda, lalu jalankan perintah berikut:
```bash
# Masuk ke folder proyek
cd "3. Project-IT-Asset"

# Membuat Virtual Environment (venv)
python -m venv venv

# Mengaktifkan venv (Windows)
venv\Scripts\activate

# Mengaktifkan venv (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependensi Python
```bash
pip install -r Web/requirements.txt
```

### 4. Setup Database PostgreSQL
1. Buat database baru di PostgreSQL Anda (misal nama database: `inventory_db`).
2. Buat user admin PostgreSQL (misal user: `inventory_admin` dengan password `GPBandungan2025`).
3. Restore database menggunakan salah satu dari berkas cadangan yang kami sediakan:

**Menggunakan berkas `.sql` (Recommended):**
```bash
psql -U inventory_admin -d inventory_db -f backup_inventory_db.sql
```

**Menggunakan berkas `.dump` (Alternatif):**
```bash
pg_restore -U inventory_admin -d inventory_db -v inventory_db.dump
```

### 5. Konfigurasi Variabel Lingkungan (`.env`)
Buat berkas bernama `.env` di dalam direktori `Web/` (`Web/.env`) dan sesuaikan kredensial koneksi database Anda:
```env
SECRET_KEY=gp-bandungan-secret-key-123-production-change-me
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=inventory_db
DB_USER=inventory_admin
DB_PASSWORD=GPBandungan2025
DB_POOL_MINCONN=1
DB_POOL_MAXCONN=20
```

### 6. Menjalankan Aplikasi
**Mode Pengembangan (Development):**
```bash
python Web/app.py
```
Aplikasi akan berjalan secara lokal di `http://127.0.0.1:5000`.

**Mode Produksi (Production - Linux Gunicorn):**
```bash
# Menjalankan skrip restart otomatis
chmod +x run.sh
./run.sh
```

---

## 📝 Lisensi
Dokumen ini dibuat dan dikembangkan sepenuhnya oleh **IT Department - Griya Persada Hotel & Resort**. Hak cipta dilindungi undang-undang.