#!/bin/bash

# --- KONFIGURASI PATH ---
APP_DIR="/var/www/inventory-app/Web"
VENV_BIN="/var/www/inventory-app/my-flask-app/venv/bin"

echo "==============================================="
echo "   RESTARTING INVENTORY APP SERVICES          "
echo "==============================================="

# 1. Restart Nginx (Pintu Depan)
echo "[1/4] Mengatur ulang Nginx..."
sudo systemctl restart nginx

# 2. Matikan Gunicorn yang mungkin masih jalan agar tidak bentrok
echo "[2/4] Membersihkan proses Gunicorn lama..."
pkill -f gunicorn || true
sleep 1 # Tunggu sebentar agar port benar-benar lepas

# 3. Masuk ke direktori aplikasi
cd $APP_DIR
echo "[3/4] Masuk ke folder: $APP_DIR"

# 4. Jalankan Gunicorn di background (Daemon)
# Ini menggantikan 'python3 app.py' agar aplikasi tetap hidup saat terminal ditutup
echo "[4/4] Menjalankan app.py melalui Gunicorn..."
$VENV_BIN/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app --daemon

echo "==============================================="
echo " STATUS: SEMUA LAYANAN BERHASIL RESTART!      "
echo " Silakan cek browser Anda.                     "
echo "==============================================="