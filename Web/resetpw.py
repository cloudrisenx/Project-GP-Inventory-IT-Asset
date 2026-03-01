from app import get_db_connection
from werkzeug.security import generate_password_hash

def reset_passwords():
    print("Menghubungkan ke database...")
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Membuat hash password yang dijamin cocok dengan sistem Anda
            hashed_pw = generate_password_hash('admin123')
            
            # Update password untuk admin dan guest
            cur.execute("UPDATE users SET password = %s WHERE username IN ('admin', 'guest')", (hashed_pw,))
            conn.commit()
            cur.close()
            print("SUKSES: Password 'admin' dan 'guest' berhasil diubah menjadi 'admin123'!")
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()
            tunnel.stop()
    else:
        print("Gagal terhubung ke database.")

if __name__ == "__main__":
    reset_passwords()