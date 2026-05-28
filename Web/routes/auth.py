from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from psycopg2 import errors
from functools import wraps

from database.db import get_db
from services.helper_service import rows_to_dict
from models.user import User

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Akses ditolak! Fitur ini khusus Administrator.', 'error')
            return redirect(url_for('assets.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'user']:
            flash('Akses ditolak! Fitur ini hanya untuk Admin dan User.', 'error')
            return redirect(url_for('assets.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('assets.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with get_db() as conn:
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("SELECT id, username, password, nama_lengkap, role FROM users WHERE username = %s", (username,))
                        user_data = cur.fetchone()

                        if user_data and check_password_hash(user_data[2], password):
                            user = User(id=user_data[0], username=user_data[1], nama_lengkap=user_data[3], role=user_data[4])
                            login_user(user)
                            next_page = request.args.get('next')
                            return redirect(next_page or url_for('assets.index'))
                        else:
                            flash('Username atau password salah!', 'error')
                except Exception as e:
                    print(f"Error during login: {e}")
                    flash('Terjadi kesalahan sistem saat memproses login.', 'error')
            else:
                flash('Gagal terhubung ke database. Silakan coba lagi.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar dari sistem.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/tambah-user', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nama_lengkap = request.form.get('nama_lengkap')
        role = request.form.get('role')
        hashed_password = generate_password_hash(password)

        with get_db() as conn:
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO users (username, password, nama_lengkap, role) VALUES (%s, %s, %s, %s)", 
                                    (username, hashed_password, nama_lengkap, role))
                        conn.commit()
                        flash('Pengguna baru berhasil ditambahkan!', 'success')
                        return redirect(url_for('auth.tambah_user'))
                except errors.UniqueViolation:
                    conn.rollback()
                    flash('Gagal: Username sudah digunakan!', 'error')
                except Exception as e:
                    conn.rollback()
                    flash('Terjadi kesalahan sistem saat menyimpan user.', 'error')
    
    users = []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, username, nama_lengkap, role FROM users ORDER BY id ASC")
                    users = rows_to_dict(cur)
            except Exception as e:
                pass
            
    return render_template('tambah-user.html', user=current_user, users=users)

@auth_bp.route('/ganti-password', methods=['GET', 'POST'])
@login_required
@admin_or_user_required
def ganti_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Password baru dan konfirmasi tidak cocok!', 'error')
            return redirect(url_for('auth.ganti_password'))

        with get_db() as conn:
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("SELECT password FROM users WHERE id = %s", (current_user.id,))
                        db_password = cur.fetchone()[0]

                        if check_password_hash(db_password, old_password):
                            hashed_password = generate_password_hash(new_password)
                            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, current_user.id))
                            conn.commit()
                            flash('Password berhasil diubah!', 'success')
                        else:
                            flash('Password lama yang Anda masukkan salah!', 'error')
                except Exception as e:
                    pass
    return render_template('ganti_password.html', user=current_user)

@auth_bp.route('/edit-user', methods=['POST'])
@login_required
@admin_required
def edit_user():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    nama_lengkap = request.form.get('nama_lengkap')
    role = request.form.get('role')
    password = request.form.get('password')
    
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if password and password.strip() != "":
                        hashed_password = generate_password_hash(password)
                        cur.execute("UPDATE users SET username=%s, nama_lengkap=%s, role=%s, password=%s WHERE id=%s", 
                                    (username, nama_lengkap, role, hashed_password, user_id))
                    else:
                        cur.execute("UPDATE users SET username=%s, nama_lengkap=%s, role=%s WHERE id=%s", 
                                    (username, nama_lengkap, role, user_id))
                    conn.commit()
                    flash('Data pengguna berhasil diperbarui!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'Gagal memperbarui pengguna: {e}', 'error')
    return redirect(url_for('auth.tambah_user'))

@auth_bp.route('/hapus-user/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus_user(id):
    if id == current_user.id:
        flash('Anda tidak dapat menghapus akun sendiri!', 'error')
        return redirect(url_for('auth.tambah_user'))
        
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM users WHERE id=%s", (id,))
                    conn.commit()
                    flash('Pengguna berhasil dihapus!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'Gagal menghapus pengguna: {e}', 'error')
    return redirect(url_for('auth.tambah_user'))