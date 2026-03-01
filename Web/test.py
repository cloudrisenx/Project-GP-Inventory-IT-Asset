import psycopg2
from psycopg2 import extras
import paramiko
from sshtunnel import SSHTunnelForwarder
from config import Config

# --- MONKEY PATCH (Penting untuk menghindari error DSSKey) ---
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = None

def test_db_connection():
    print("--- MEMULAI PENGECEKAN DATABASE ---")
    
    try:
        # 1. Setup SSH Tunnel
        tunnel = SSHTunnelForwarder(
            (Config.SSH_HOST, 22),
            ssh_username=Config.SSH_USER,
            ssh_password=Config.SSH_PASSWORD,
            remote_bind_address=(Config.DB_HOST, Config.DB_PORT)
        )
        tunnel.start()
        print("[OK] SSH Tunnel berhasil dibuka.")

        # 2. Setup Koneksi Database
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            dbname=Config.DB_NAME
        )
        cur = conn.cursor(cursor_factory=extras.DictCursor)
        print("[OK] Koneksi Database berhasil.")

        # 3. Cek Isi Tabel Departments (Gunakan kolom 'name' sesuai struktur Anda)
        print("\n--- Mengecek Tabel Departments ---")
        cur.execute("SELECT * FROM departments;")
        depts = cur.fetchall()
        if depts:
            for d in depts:
                # Menggunakan d['name'] sesuai struktur di image_6c98a0.png
                print(f"ID: {d['department_id']} | Nama: {d['name']}")
        else:
            print("[!] Tabel departments kosong.")

        # 4. Cek Sinkronisasi Asset & Department
        print("\n--- Mengecek Relasi Asset ke Department ---")
        query = """
            SELECT a.barcode, a.product_name, d.name as nama_dept
            FROM assets a
            LEFT JOIN departments d ON a.department_id = d.department_id
            LIMIT 5;
        """
        cur.execute(query)
        assets = cur.fetchall()
        
        if assets:
            for row in assets:
                dept_name = row['nama_dept'] if row['nama_dept'] else "TIDAK TERHUBUNG (NULL)"
                print(f"Asset: {row['product_name']} ({row['barcode']}) -> Dept: {dept_name}")
        else:
            print("[!] Tabel assets kosong.")

        # Bersihkan
        cur.close()
        conn.close()
        tunnel.stop()
        print("\n--- PENGECEKAN SELESAI ---")

    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan: {e}")

if __name__ == "__main__":
    test_db_connection()