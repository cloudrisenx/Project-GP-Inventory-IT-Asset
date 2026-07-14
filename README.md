# 🏢 IT Asset Management - Griya Persada Hotel & Resort

A comprehensive, lightweight internal web application to register, track, and audit the lifecycle of IT assets across the entire property of Griya Persada Hotel & Resort.

---

## 🚀 Fitur Utama & Logika Bisnis

### 1. Desain UI/UX Modern & Responsif
*   **Apple-Style Layout**: Menggunakan antarmuka bersih, minimalis, dan modern dengan font sistem yang diadaptasi untuk desktop maupun perangkat mobile.
*   **Symmetric Dark & Light Mode**: Tema gelap dan terang terintegrasi penuh, disimpan secara persisten di `localStorage` peramban client untuk kenyamanan visual.

### 2. Generator Tag & Barcode Otomatis
Sistem ini menggunakan penamaan barcode deterministik untuk standardisasi pelabelan inventaris dengan format:
`MAINGROUP/SUBGROUP-INISIAL_MODEL/LOKASI/TANGGAL_BELI/KODE_HOTEL-001`

*   **MAINGROUP**: Kode Departemen (contoh: `IT` atau `ENG`)
*   **SUBGROUP**: Kode Kategori barang (contoh: `LAP` untuk Laptop)
*   **INISIAL_MODEL**: 5 huruf pertama dari kata pertama tipe model yang dikonversi ke huruf kapital (contoh: Lenovo Thinkpad T14 -> `T14` -> `T14` atau model kosong -> `GEN`)
*   **LOKASI**: Kode Lokasi aset ditempatkan (contoh: `SRV` untuk Ruang Server)
*   **TANGGAL_BELI**: Format tanggal pembelian `YYYY-MM`
*   **KODE_HOTEL**: Kode hotel tetap (default: `GPB` - Griya Persada Bandungan)
*   **Suffix Urutan**: Kode urutan kuantitas (`-001`, `-002`, dst.)

### 3. Kalkulasi Penyusutan Nilai Aset (Depresiasi)
Aplikasi menghitung depresiasi aset secara langsung (Straight-line Depreciation) berdasarkan bulan berjalan secara real-time. Rumus perhitungan penyusutan:
$$\text{Current Value} = \max\left(0, \text{Purchase Cost} - \left( \frac{\text{Purchase Cost}}{\text{Age Asset (Months)}} \times \text{Months Passed} \right)\right)$$

*   *Months Passed* dihitung dari selisih bulan berjalan dengan bulan pada `purchase_date`.
*   Jika umur manfaat (*Age Asset*) terlewati, sistem secara otomatis mengunci nilai sisa di angka Rp0,00 tanpa menghasilkan nilai minus.

### 4. Sistem QR Code & Labeling Dinamis
*   **Generasi QR Instan**: Dibuat di sisi client menggunakan `QRCode.js` berdasarkan string barcode unik aset.
*   **Cetak Massal (Bulk Printing)**: Memungkinkan operator mencetak beberapa label QR Code sekaligus berdasarkan baris tabel yang dipilih.
*   **Unauthenticated Scanner View**: Kode QR merujuk ke rute `/scan/<barcode>` yang dapat diakses oleh publik tanpa login. Memudahkan staf lapangan memeriksa spesifikasi unit, nomor seri, status garansi, serta langsung menghubungi supplier via tombol chat WhatsApp otomatis yang memformat nomor telepon menjadi prefiks internasional (`62`).

### 5. Sinkronisasi Data & Update Cascading Barcode
*   **Pembaruan Kode Master**: Jika kode departemen, kategori, atau lokasi diubah dalam menu master data, aplikasi secara otomatis menelusuri database dan memperbarui (cascade rewrite) string barcode seluruh aset terkait agar tetap sinkron.
*   **Regenerasi Barcode Database**: Menyediakan API internal (`/api/regenerate-barcode`) untuk memperbarui format barcode seluruh aset secara massal apabila terjadi migrasi data atau perubahan pola penomoran.
*   **Bulk Quantity Insertion**: Saat menambahkan data dengan Qty > 1, backend secara otomatis membuat entri terpisah untuk masing-masing unit dengan suffix berurutan (`-001` hingga `-qty`).

---

## 🛠️ Tech Stack & Dependencies

*   **Backend**: Python 3.8+ (Flask Framework)
*   **Database**: PostgreSQL 12+ (psycopg2 connection pooling)
*   **Frontend**: Jinja2 Templates, Vanilla CSS (CSS Variables), Vanilla JavaScript, QRCode.js
*   **Autentikasi**: Flask-Login, enkripsi password via `werkzeug.security`

---

## 📁 Struktur Direktori

```text
├── Web/
│   ├── database/          # Modul koneksi PostgreSQL & Connection Pool management
│   │   ├── pool.py        # Pengatur pool koneksi PostgreSQL
│   │   └── db.py          # Context manager untuk meminjam/melepas koneksi
│   ├── middleware/        # Middleware WSGI (Reverse Proxy helper)
│   │   └── reverse_proxy.py # Memastikan routing bekerja pada subpath /inventory
│   ├── models/            # Struktur representasi data (User)
│   │   └── user.py
│   ├── routes/            # Rute URL dan logika bisnis aplikasi
│   │   ├── auth.py        # Autentikasi Admin, User & Manajemen Pengguna
│   │   ├── assets.py      # CRUD Aset, Perhitungan Depresiasi, dan QR Layout
│   │   ├── settings.py    # Master Data (Departemen, Lokasi, Kategori, Supplier)
│   │   ├── api.py         # Endpoint API pendukung (Autocomplete & Barcode Generator)
│   │   └── scanner.py     # Modul pembaca/detail barcode publik
│   ├── services/          # Kelas helper (Custom JSON encoder)
│   │   └── helper_service.py
│   ├── static/            # Berkas statis frontend (CSS, JS, Gambar, Diagram)
│   │   ├── alur_program.xml # Diagram Alur Program (Draw.io compatible)
│   │   ├── erd.xml        # Diagram ERD Database (Draw.io compatible)
│   │   ├── *.css          # Berkas layout modular CSS
│   │   └── *.js           # Interaktivitas JS frontend
│   ├── templates/         # Berkas HTML template Jinja2
│   ├── config.py          # Konfigurasi parameter lingkungan aplikasi Flask
│   ├── requirements.txt   # Dependensi modul python
│   ├── wsgi.py            # Entrypoint WSGI Server (Gunicorn)
│   ├── app.py             # Inisialisasi awal server Flask
│   ├── resetpw.py         # Script utility untuk meriset sandi admin/guest
│   └── .env               # File konfigurasi lokal (Database & Secret Key)
├── backup_inventory_db.sql # Backup skema & data awal database (format SQL)
├── inventory_db.dump      # Backup database (format binary dump)
├── README.md              # Dokumentasi ini
├── MIND.md                # Memori semantik repository untuk AI Assistant
└── run.sh                 # Script deployment otomatis di Linux (Nginx/Gunicorn)
```

---

## 📊 Visualisasi & Dokumentasi Arsitektur

#### 🔄 Alur Kerja Sistem (Workflow)
![Alur Kerja](Inventory.drawio.png)

#### 🗄️ Database Schema (ERD)
![ERD Database](ERD_inventory.drawio.png)

Kami menyediakan diagram interaktif yang dapat Anda impor langsung ke **[draw.io](https://app.diagrams.net)** untuk memudahkan analisis sistem:

*   **ERD Database (`Web/static/erd.xml`)**: Diagram relasional database (`assets`, `departments`, `categories`, `locations`, `asset_status`, `suppliers`, `users`) dengan relasi lengkap.
*   **Alur Program (`Web/static/alur_program.xml`)**: Flowchart visual yang mendokumentasikan alur data aplikasi dari autentikasi hingga pengelolaan aset dan pencetakan QR Code.

> **Cara Membaca Diagram**: Buka draw.io -> Klik **File > Import From > Device...** -> Pilih salah satu file XML di atas.

---

## ⚙️ Panduan Instalasi & Konfigurasi

### 1. Persiapan Virtual Environment
Jalankan perintah berikut di terminal:
```bash
# Masuk ke folder proyek
cd "Project-GP-Inventory-IT-Asset"

# Membuat Virtual Environment (venv)
python -m venv venv

# Mengaktifkan venv (Windows)
venv\Scripts\activate

# Mengaktifkan venv (macOS/Linux)
source venv/bin/activate
```

### 2. Install Dependensi
```bash
pip install -r Web/requirements.txt
```

### 3. Setup Database PostgreSQL
1. Buat database kosong baru di PostgreSQL Anda (contoh nama database: `inventory_db`).
2. Daftarkan user admin PostgreSQL (contoh user: `inventory_admin` dengan password `GPBandungan2025`).
3. Impor data menggunakan berkas SQL backup yang disediakan:

```bash
psql -U inventory_admin -d inventory_db -f backup_inventory_db.sql
```

### 4. Konfigurasi Environment File (`Web/.env`)
Buat file baru bernama `.env` di dalam folder `Web/` (`Web/.env`) dan isi dengan kredensial database Anda:
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

### 5. Akun Default & Reset Password
Data contoh di dalam database menyediakan empat akun default:
*   **Administrator**: `admin` (Role: `admin`)
*   **Griya Persada**: `griyapersada` (Role: `admin`)
*   **CloudRisenx**: `risenx` (Role: `user`)
*   **Guest/Tamu**: `guest` (Role: `guest`)

Jika Anda lupa sandi akun `admin` atau `guest`, Anda dapat meresetnya menjadi `admin123` dengan menjalankan perintah utility:
```bash
python Web/resetpw.py
```

### 6. Menjalankan Aplikasi

**Mode Pengembangan (Development):**
```bash
python Web/app.py
```
Aplikasi akan aktif secara lokal di `http://127.0.0.1:5000`.

**Mode Produksi (Linux dengan Gunicorn & Nginx Reverse Proxy):**
Jika di-deploy ke server di bawah subpath proxy (misal: `domain.com/inventory`), pastikan proxy meneruskan header dengan benar. Jalankan aplikasi menggunakan gunicorn daemon:
```bash
chmod +x run.sh
./run.sh
```

---

## 🔒 Hak Akses (User Roles Matrix)

| Fitur | Admin | User | Guest |
| :--- | :---: | :---: | :---: |
| Lihat Tabel & Detail Aset | ✅ | ✅ | ❌ |
| Tambah / Edit Aset & Master Data | ✅ | ✅ | ❌ |
| Cetak Label / QR Code | ✅ | ✅ | ❌ |
| Hapus Aset / Master Data | ✅ | ❌ | ❌ |
| Tambah / Kelola Pengguna | ✅ | ❌ | ❌ |
| Scan QR Code (Public Route) | ✅ | ✅ | ✅ |

---

## 📝 Lisensi
Dokumen ini dibuat dan dikembangkan sepenuhnya oleh **IT Department - Griya Persada Hotel & Resort**. Hak cipta dilindungi undang-undang.