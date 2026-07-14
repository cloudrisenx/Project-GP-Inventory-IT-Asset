# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching
COPY requirements.txt .

# Install dependensi sistem yang mungkin dibutuhkan psycopg2 dan package Python
RUN apt-get update && apt-get install -y libpq-dev gcc \
    && pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Expose port yang digunakan Flask (biasanya 5000)
EXPOSE 5000

# Jalankan aplikasi (sesuaikan nama file utama jika bukan app.py)
CMD ["python", "app.py"] 
# atau jika menggunakan gunicorn: CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]