from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
from psycopg2 import extras, errors
import paramiko
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from sshtunnel import SSHTunnelForwarder
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# --- MONKEY PATCH PENTING UNTUK PARAMIKO ---
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = None

# ==========================================
# 1. INISIALISASI FLASK & KONFIGURASI
# ==========================================
app = Flask(__name__)
app.config.from_object('config.Config')

# SECRET KEY (Wajib untuk session & flash)
app.secret_key = 'gp-bandungan-secret-key-123' 

# KONFIGURASI AUTO LOGOUT (30 MENIT INAKTIVITAS)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.before_request
def make_session_permanent():
    # Menandai sesi sebagai permanen agar menggunakan timeout yang kita set di atas
    session.permanent = True

# ==========================================
# 2. SETUP FLASK-LOGIN
# ==========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Silakan login terlebih dahulu untuk mengakses halaman ini."
login_manager.login_message_category = "error"

class User(UserMixin):
    def __init__(self, id, username, nama_lengkap, role):
        self.id = id
        self.username = username
        self.nama_lengkap = nama_lengkap
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, username, nama_lengkap, role FROM users WHERE id = %s", (int(user_id),))
            user_data = cur.fetchone()
            cur.close()
            if user_data:
                return User(id=user_data[0], username=user_data[1], nama_lengkap=user_data[2], role=user_data[3])
        except Exception as e:
            print(f"Error loading user: {e}")
        finally:
            conn.close()
            tunnel.stop()
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Akses ditolak! Fitur ini khusus Administrator.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'user']:
            flash('Akses ditolak! Fitur ini hanya untuk Admin dan User.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 3. HELPER FUNCTIONS & DATABASE CONNECTION
# ==========================================
class PostgreEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.strftime('%d-%m-%Y')
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def rows_to_dict(cursor):
    colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in cursor.fetchall()]

def get_db_connection():
    try:
        tunnel = SSHTunnelForwarder(
            (app.config['SSH_HOST'], 22),
            ssh_username=app.config['SSH_USER'],
            ssh_password=app.config['SSH_PASSWORD'],
            remote_bind_address=(app.config['DB_HOST'], app.config['DB_PORT'])
        )
        tunnel.start()
        
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']
        )
        return conn, tunnel
    except Exception as e:
        print(f"ERROR KONEKSI: {e}")
        return None, None

# ==========================================
# 4. RUTE AUTHENTICATION & USER MANAGEMENT
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn, tunnel = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, username, password, nama_lengkap, role FROM users WHERE username = %s", (username,))
                user_data = cur.fetchone()
                cur.close()

                if user_data and check_password_hash(user_data[2], password):
                    user = User(id=user_data[0], username=user_data[1], nama_lengkap=user_data[3], role=user_data[4])
                    login_user(user)
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('index'))
                else:
                    flash('Username atau password salah!', 'error')
            except Exception as e:
                print(f"Error during login: {e}")
                flash('Terjadi kesalahan sistem saat memproses login.', 'error')
            finally:
                conn.close()
                tunnel.stop()
        else:
            flash('Gagal terhubung ke database. Silakan coba lagi.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar dari sistem.', 'success')
    return redirect(url_for('login'))

@app.route('/tambah-user', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nama_lengkap = request.form.get('nama_lengkap')
        role = request.form.get('role')
        hashed_password = generate_password_hash(password)

        conn, tunnel = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO users (username, password, nama_lengkap, role) VALUES (%s, %s, %s, %s)", 
                            (username, hashed_password, nama_lengkap, role))
                conn.commit()
                cur.close()
                flash('Pengguna baru berhasil ditambahkan!', 'success')
                return redirect(url_for('tambah_user'))
            except errors.UniqueViolation:
                conn.rollback()
                flash('Gagal: Username sudah digunakan!', 'error')
            except Exception as e:
                conn.rollback()
                flash('Terjadi kesalahan sistem saat menyimpan user.', 'error')
            finally:
                conn.close()
                tunnel.stop()
    
    # Ambil daftar users untuk ditampilkan di tabel
    users = []
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, username, nama_lengkap, role FROM users ORDER BY id ASC")
            users = rows_to_dict(cur)
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
            
    return render_template('tambah-user.html', user=current_user, users=users)

@app.route('/ganti-password', methods=['GET', 'POST'])
@login_required
@admin_or_user_required
def ganti_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Password baru dan konfirmasi tidak cocok!', 'error')
            return redirect(url_for('ganti_password'))

        conn, tunnel = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT password FROM users WHERE id = %s", (current_user.id,))
                db_password = cur.fetchone()[0]

                if check_password_hash(db_password, old_password):
                    hashed_password = generate_password_hash(new_password)
                    cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, current_user.id))
                    conn.commit()
                    flash('Password berhasil diubah!', 'success')
                else:
                    flash('Password lama yang Anda masukkan salah!', 'error')
                cur.close()
            finally:
                conn.close()
                tunnel.stop()
    return render_template('ganti_password.html', user=current_user)

@app.route('/edit-user', methods=['POST'])
@login_required
@admin_required
def edit_user():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    nama_lengkap = request.form.get('nama_lengkap')
    role = request.form.get('role')
    password = request.form.get('password')
    
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Cek apakah password diisi (ingin diubah) atau kosong (tetap)
            if password and password.strip() != "":
                hashed_password = generate_password_hash(password)
                cur.execute("UPDATE users SET username=%s, nama_lengkap=%s, role=%s, password=%s WHERE id=%s", 
                            (username, nama_lengkap, role, hashed_password, user_id))
            else:
                cur.execute("UPDATE users SET username=%s, nama_lengkap=%s, role=%s WHERE id=%s", 
                            (username, nama_lengkap, role, user_id))
            
            conn.commit()
            cur.close()
            flash('Data pengguna berhasil diperbarui!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Gagal memperbarui pengguna: {e}', 'error')
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('tambah_user'))

@app.route('/hapus-user/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus_user(id):
    # Mencegah admin menghapus dirinya sendiri
    if id == current_user.id:
        flash('Anda tidak dapat menghapus akun sendiri!', 'error')
        return redirect(url_for('tambah_user'))
        
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id=%s", (id,))
            conn.commit()
            cur.close()
            flash('Pengguna berhasil dihapus!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Gagal menghapus pengguna: {e}', 'error')
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('tambah_user'))

# ==========================================
# 5. RUTE UTAMA (DASHBOARD & TABEL ASSET) 
# ==========================================
@app.route('/')
@login_required
def index():
    conn, tunnel = get_db_connection()
    total_assets, recent_items = 0, []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM assets")
            total_assets = cur.fetchone()[0]
            
            cur.execute("SELECT product_name, barcode, created_at FROM assets ORDER BY created_at DESC LIMIT 5")
            recent_items = rows_to_dict(cur)
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return render_template('index.html', total_assets=total_assets, recent_items=recent_items, user=current_user)

@app.route('/lihat-tabel')
@login_required
def lihat_tabel():
    conn, tunnel = get_db_connection()
    assets_list = []
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT a.asset_id, a.barcode, a.product_name, a.model, a.serial_number, 
                       a.purchase_date, a.purchase_cost, a.qty, a.keterangan, a.warranty_info,
                       c.name AS category_name, a.age_asset,
                       st.status_name,
                       d.name AS department_full, 
                       l.name AS lokasi_full, 
                       s.company_name AS supplier_name,
                       s.phone AS supplier_phone, 
                       s.contact_person AS supplier_contact
                FROM assets a
                LEFT JOIN categories c ON a.category_id = c.category_id
                LEFT JOIN departments d ON a.department_id = d.department_id 
                LEFT JOIN locations l ON a.location_id = l.location_id
                LEFT JOIN suppliers s ON a.supplier_id = s.supplier_id
                LEFT JOIN asset_status st ON a.status_id = st.status_id
                ORDER BY d.name ASC, a.created_at DESC;
            """
            cur.execute(query)
            assets_list = rows_to_dict(cur)
            
            # --- HITUNG NILAI SISA (DEPRESIASI) ---
            today = date.today()
            for asset in assets_list:
                cost = float(asset['purchase_cost']) if asset['purchase_cost'] else 0
                lifespan = int(asset['age_asset']) if asset['age_asset'] else 0
                p_date = asset['purchase_date']
                
                current_val = cost
                
                if lifespan > 0 and p_date:
                    if isinstance(p_date, datetime):
                        p_date = p_date.date()
                    
                    # Hitung bulan berjalan
                    months_passed = (today.year - p_date.year) * 12 + (today.month - p_date.month)
                    if months_passed > 0:
                        depreciation = (cost / lifespan) * months_passed
                        current_val = cost - depreciation
                
                # Pastikan nilai tidak minus
                asset['current_value'] = max(0, current_val)
            
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    
    assets_json_str = json.dumps(assets_list, cls=PostgreEncoder)
    return render_template('tabel.html', assets=assets_list, assets_json=assets_json_str, user=current_user)

# ==========================================
# 6. RUTE MANAJEMEN DATA ASSET (KHUSUS ADMIN)
# ==========================================
@app.route('/edit-tabel')
@login_required
@admin_required
def edit_tabel():
    conn, tunnel = get_db_connection()
    assets = []
    assets_json = "[]" 
    categories, locations, suppliers, statuses, departments = [], [], [], [], []
    
    if conn:
        try:
            # Menggunakan DictCursor agar data bisa dipanggil dengan nama kolom (misal: asset.name)
            cur = conn.cursor(cursor_factory=extras.DictCursor)
            
            # Ambil Semua Data Asset beserta Relasinya
            cur.execute("""
                SELECT a.*, 
                       d.name as department_name, 
                       c.name as category_name, 
                       l.name as lokasi_full, 
                       st.status_name
                FROM assets a
                LEFT JOIN departments d ON a.department_id = d.department_id
                LEFT JOIN categories c ON a.category_id = c.category_id
                LEFT JOIN locations l ON a.location_id = l.location_id
                LEFT JOIN asset_status st ON a.status_id = st.status_id
                ORDER BY a.asset_id DESC
            """)
            assets = cur.fetchall()

            # MEMBUAT DATA JSON AGAR DI-PASS KE {{ assets_json | safe }} DI HTML
            import json
            from datetime import date, datetime
            from decimal import Decimal
            
            assets_list = []
            for row in assets:
                asset_dict = dict(row)
                for key, val in asset_dict.items():
                    if isinstance(val, (date, datetime)):
                        asset_dict[key] = val.strftime('%Y-%m-%d')
                    elif isinstance(val, Decimal):
                        asset_dict[key] = float(val)
                assets_list.append(asset_dict)
            assets_json = json.dumps(assets_list)

            # Ambil data untuk opsi Dropdown
            cur.execute("SELECT category_id, name, department_id, code FROM categories ORDER BY name ASC")
            categories = cur.fetchall()
            
            cur.execute("SELECT location_id, name, code FROM locations ORDER BY name ASC")
            locations = cur.fetchall()
            
            cur.execute("SELECT supplier_id, company_name FROM suppliers ORDER BY company_name ASC")
            suppliers = cur.fetchall()
            
            cur.execute("SELECT status_id, status_name FROM asset_status ORDER BY status_id ASC")
            statuses = cur.fetchall()
            
            cur.execute("SELECT department_id, name, code FROM departments ORDER BY name ASC")
            departments = cur.fetchall()
            
            cur.close()
        except Exception as e:
            print(f"Error load data tabel: {e}")
        finally:
            # BLOK INI YANG SEBELUMNYA HILANG DAN MEMBUAT 'try:' ERROR
            conn.close()
            tunnel.stop()

    return render_template('edit-tabel.html', 
                           assets=assets, 
                           assets_json=assets_json, 
                           categories=categories, 
                           locations=locations, 
                           suppliers=suppliers, 
                           statuses=statuses, 
                           departments=departments, 
                           user=current_user)

@app.route('/tambah-data', methods=['GET', 'POST'])
@login_required
@admin_or_user_required
def tambah_data():
    conn, tunnel = get_db_connection()
    categories, locations, suppliers, statuses, departments = [], [], [], [], []
    
    if conn:
        try:
            # Gunakan DictCursor agar data bisa diakses sebagai dictionary (seperti d.code, d.name) di HTML
            cur = conn.cursor(cursor_factory=extras.DictCursor)
            
            # ==========================================
            # 1. PROSES POST (SAAT TOMBOL SIMPAN DITEKAN)
            # ==========================================
            if request.method == 'POST':
                try:
                    # Tangkap data dari form
                    barcode = request.form.get('barcode')
                    name = request.form.get('name')  
                    department_id = request.form.get('department_id') 
                    category_id = request.form.get('category_id')     
                    location_id = request.form.get('location_id')
                    purchase_date = request.form.get('purchase_date')
                    purchase_cost = request.form.get('purchase_cost')
                    supplier_id = request.form.get('supplier_id')
                    status_id = request.form.get('status_id')
                    
                    # Tangkap nilai age_asset
                    age_asset = request.form.get('age_asset')
                    
                    # Validasi Data Kosong (Ubah string kosong menjadi 0 atau None)
                    if not age_asset or str(age_asset).strip() == '':
                        age_asset = 0
                    else:
                        age_asset = int(age_asset)
                        
                    if not purchase_cost or str(purchase_cost).strip() == '':
                        purchase_cost = 0
                    else:
                        purchase_cost = float(purchase_cost)
                        
                    if not supplier_id or str(supplier_id).strip() == '':
                        supplier_id = None
                        
                    if not status_id or str(status_id).strip() == '':
                        status_id = 1
                        
                    # Eksekusi Query INSERT
                    cur.execute("""
                        INSERT INTO assets (
                            barcode, name, department_id, category_id, location_id, 
                            purchase_date, purchase_cost, supplier_id, age_asset, status_id
                        ) VALUES (
                            %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s
                        )
                    """, (
                        barcode, name, department_id, category_id, location_id,
                        purchase_date, purchase_cost, supplier_id, age_asset, status_id
                    ))
                    
                    conn.commit()
                    flash('Data asset berhasil ditambahkan!', 'success')
                    return redirect(url_for('tambah_data'))
                    
                except Exception as e:
                    conn.rollback()
                    flash(f'Terjadi kesalahan saat menyimpan data: {str(e)}', 'danger')

            # ==========================================
            # 2. PROSES GET (MENAMPILKAN DROPDOWN FORM)
            # ==========================================
            cur.execute("SELECT category_id, name, department_id, code FROM categories ORDER BY name ASC")
            categories = cur.fetchall()
            
            cur.execute("SELECT location_id, name, code FROM locations ORDER BY name ASC")
            locations = cur.fetchall()
            
            cur.execute("SELECT supplier_id, company_name FROM suppliers ORDER BY company_name ASC")
            suppliers = rows_to_dict(cur)
            
            cur.execute("SELECT status_id, status_name FROM asset_status ORDER BY status_id ASC")
            statuses = rows_to_dict(cur)
            
            cur.execute("SELECT department_id, name, code FROM departments ORDER BY name ASC")
            departments = cur.fetchall()
            
            cur.close()
            
        except Exception as e:
            # Opsional: Jika ada error koneksi atau fetch data
            print(f"Database error: {e}")
            
        finally:
            conn.close()
            tunnel.stop()
            
    return render_template('tambah-data.html', 
                           categories=categories, 
                           locations=locations, 
                           suppliers=suppliers, 
                           statuses=statuses, 
                           departments=departments, 
                           user=current_user)

@app.route('/simpan-data', methods=['POST'])
@app.route('/update-data', methods=['POST'])
@login_required
@admin_required
def process_data():
    is_update = request.path == '/update-data'
    asset_id = request.form.get('asset_id')
    
    # Fungsi pembantu untuk menangkap dan memvalidasi input
    get_val = lambda key: request.form.get(key) or None
    get_int = lambda key: int(request.form.get(key)) if request.form.get(key) and request.form.get(key).strip() != "" else None
    
    # Ambil semua data dari form HTML
    product_name = get_val('product_name')
    barcode = get_val('barcode')
    serial_number = get_val('serial_number')
    model = get_val('model')
    manufacturer = get_val('manufacturer')
    category_id = get_int('category_id')
    status_id = get_int('status_id')
    location_id = get_int('location_id')
    supplier_id = get_int('supplier_id')
    department_id = get_int('department_id')
    purchase_date = get_val('purchase_date')
    warranty_info = get_val('warranty_info')
    keterangan = get_val('keterangan')
    
    # Validasi Angka khusus
    purchase_cost = request.form.get('purchase_cost')
    purchase_cost = float(purchase_cost) if purchase_cost and purchase_cost.strip() != "" else 0.0

    age_asset = request.form.get('age_asset')
    age_asset = int(age_asset) if age_asset and age_asset.strip() != "" else 0

    qty = request.form.get('qty')
    qty = int(qty) if qty and qty.strip() != "" else 1

    # Susun Tuple untuk eksekusi Query
    data_tuple = (
        product_name, barcode, serial_number, model, manufacturer, 
        category_id, status_id, location_id, supplier_id, 
        department_id, purchase_date, purchase_cost, 
        warranty_info, keterangan, qty, age_asset # <-- age_asset ditambahkan di sini
    )
    
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if is_update and asset_id:
                # Proses UPDATE
                cur.execute("""
                    UPDATE assets SET
                        product_name=%s, barcode=%s, serial_number=%s, model=%s, manufacturer=%s, 
                        category_id=%s, status_id=%s, location_id=%s, supplier_id=%s, 
                        department_id=%s, purchase_date=%s, purchase_cost=%s, 
                        warranty_info=%s, keterangan=%s, qty=%s, age_asset=%s
                    WHERE asset_id=%s
                """, data_tuple + (asset_id,))
                flash('Data asset berhasil diperbarui!', 'success')
            else:
                # Proses INSERT (Tambah Baru)
                cur.execute("""
                    INSERT INTO assets (
                        product_name, barcode, serial_number, model, manufacturer, 
                        category_id, status_id, location_id, supplier_id, 
                        department_id, purchase_date, purchase_cost, 
                        warranty_info, keterangan, qty, age_asset
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, data_tuple) 
                flash('Data asset baru berhasil disimpan!', 'success')
                
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"ERROR DATABASE OP: {e}")
            conn.rollback()
            flash(f'Terjadi kesalahan saat menyimpan data: {str(e)}', 'error')
        finally:
            conn.close()
            tunnel.stop()
            
    return redirect(url_for('edit_tabel'))

@app.route('/hapus-data/<int:asset_id>', methods=['POST'])
@login_required
@admin_required
def hapus_data(asset_id):
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM assets WHERE asset_id = %s", (asset_id,))
            conn.commit()
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('edit_tabel'))


# ==========================================
# 7. RUTE PENGATURAN (SETTINGS) - KHUSUS ADMIN
# ==========================================
@app.route('/settings')
@login_required
@admin_or_user_required
def settings():
    return render_template('settings.html', user=current_user)

@app.route('/settings/locations')
@login_required
@admin_or_user_required
def settings_locations():
    conn, tunnel = get_db_connection()
    items = []
    if conn:
        try:
            cur = conn.cursor(cursor_factory=extras.DictCursor)
            cur.execute("SELECT location_id, name, code FROM locations ORDER BY name ASC")
            items = cur.fetchall()
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return render_template('settings_locations.html', items=items, user=current_user)

@app.route('/settings/locations/save', methods=['POST'])
@login_required
@admin_or_user_required
def save_location():
    loc_id = request.form.get('location_id')
    name = request.form.get('name')
    code = request.form.get('code')
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if loc_id and str(loc_id).strip() != "": 
                # 1. Ambil kode lama sebelum update untuk perbandingan
                cur.execute("SELECT code FROM locations WHERE location_id = %s", (loc_id,))
                row = cur.fetchone()
                old_code = row[0] if row else None

                # 2. Lakukan Update Data Lokasi
                cur.execute("UPDATE locations SET name=%s, code=%s WHERE location_id=%s", (name, code, loc_id))
                
                # 3. Jika kode berubah, update otomatis barcode asset yang terkait
                if old_code and code and old_code != code:
                    # Ambil semua asset di lokasi ini
                    cur.execute("SELECT asset_id, barcode FROM assets WHERE location_id = %s", (loc_id,))
                    assets = cur.fetchall()
                    
                    updated_count = 0
                    for asset in assets:
                        asset_id, barcode = asset
                        if barcode and '/' in barcode:
                            # Split barcode berdasarkan '/', ganti bagian yang sama persis dengan old_code
                            parts = barcode.split('/')
                            new_parts = [code if part == old_code else part for part in parts]
                            new_barcode = "/".join(new_parts)
                            
                            if new_barcode != barcode:
                                cur.execute("UPDATE assets SET barcode = %s WHERE asset_id = %s", (new_barcode, asset_id))
                                updated_count += 1
                    
                    if updated_count > 0:
                        flash(f'Lokasi disimpan & {updated_count} barcode asset berhasil diperbarui otomatis!', 'success')
                    else:
                        flash('Data lokasi berhasil disimpan!', 'success')
                else:
                    flash('Data lokasi berhasil disimpan!', 'success')
            else: 
                cur.execute("INSERT INTO locations (name, code) VALUES (%s, %s)", (name, code))
                flash('Data lokasi berhasil disimpan!', 'success')
            
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            flash(f'Gagal menyimpan lokasi: {e}', 'error')
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_locations'))

@app.route('/settings/locations/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_location(id):
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM locations WHERE location_id=%s", (id,))
            conn.commit()
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_locations'))

@app.route('/settings/categories')
@login_required
@admin_required
def settings_categories():
    conn, tunnel = get_db_connection()
    items, departments = [], []
    if conn:
        try:
            cur = conn.cursor(cursor_factory=extras.DictCursor)
            
            # Ambil Kategori Join Departemen
            cur.execute("""
                SELECT c.category_id, c.name, c.code, 
                       d.department_id, d.name as department_name, d.code as dept_code
                FROM categories c
                LEFT JOIN departments d ON c.department_id = d.department_id
                ORDER BY d.name ASC, c.name ASC
            """)
            items = cur.fetchall()
            
            # Ambil Departemen
            cur.execute("SELECT department_id, name, code FROM departments ORDER BY name ASC")
            departments = cur.fetchall()
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return render_template('settings_categories.html', items=items, departments=departments, user=current_user)

@app.route('/settings/categories/save', methods=['POST'])
@login_required
@admin_required
def save_category():
    cat_id = request.form.get('category_id')
    name = request.form.get('name')
    dept_id = request.form.get('department_id')
    code = request.form.get('code')
    
    # Mencegah error UNIQUE jika code kosong
    if not code or code.strip() == "":
        code = None
        
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if cat_id and str(cat_id).strip() != "":
                # 1. Ambil kode lama sebelum update
                cur.execute("SELECT code FROM categories WHERE category_id = %s", (cat_id,))
                row = cur.fetchone()
                old_code = row[0] if row else None

                # 2. Update Data Kategori
                cur.execute("UPDATE categories SET name=%s, department_id=%s, code=%s WHERE category_id=%s", (name, dept_id, code, cat_id))
                
                # 3. Update Barcode Asset Otomatis
                if old_code and code and old_code != code:
                    cur.execute("SELECT asset_id, barcode FROM assets WHERE category_id = %s", (cat_id,))
                    assets = cur.fetchall()
                    updated_count = 0
                    for asset in assets:
                        asset_id, barcode = asset
                        if barcode and '/' in barcode:
                            parts = barcode.split('/')
                            new_parts = [code if part == old_code else part for part in parts]
                            new_barcode = "/".join(new_parts)
                            if new_barcode != barcode:
                                cur.execute("UPDATE assets SET barcode = %s WHERE asset_id = %s", (new_barcode, asset_id))
                                updated_count += 1
                    flash(f'Kategori disimpan & {updated_count} barcode asset diperbarui!', 'success')
                else:
                    flash('Data kategori berhasil disimpan!', 'success')
            else:
                cur.execute("INSERT INTO categories (name, department_id, code) VALUES (%s, %s, %s)", (name, dept_id, code))
                flash('Data kategori berhasil disimpan!', 'success')
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            flash(f'Gagal menyimpan kategori: {e}', 'error')
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_categories'))

@app.route('/settings/categories/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM categories WHERE category_id = %s", (id,))
            conn.commit()
            cur.close()
            flash('Kategori berhasil dihapus!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Gagal menghapus kategori: {e}', 'error')
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_categories'))

@app.route('/settings/suppliers')
@login_required
@admin_or_user_required
def settings_suppliers():
    conn, tunnel = get_db_connection()
    items = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM suppliers ORDER BY company_name ASC")
            items = rows_to_dict(cur)
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return render_template('settings_suppliers.html', items=items, user=current_user)

@app.route('/settings/suppliers/save', methods=['POST'])
@login_required
@admin_or_user_required
def save_supplier():
    sup_id = request.form.get('supplier_id')
    company = request.form.get('company_name')
    contact = request.form.get('contact_person')
    phone = request.form.get('phone')
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if sup_id:
                cur.execute("""UPDATE suppliers SET company_name=%s, contact_person=%s, phone=%s 
                               WHERE supplier_id=%s""", (company, contact, phone, sup_id))
            else:
                cur.execute("""INSERT INTO suppliers (company_name, contact_person, phone) 
                               VALUES (%s, %s, %s)""", (company, contact, phone))
            conn.commit()
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_suppliers'))

@app.route('/settings/suppliers/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_supplier(id):
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM suppliers WHERE supplier_id=%s", (id,))
            conn.commit()
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_suppliers'))

@app.route('/settings/status')
@login_required
@admin_required
def settings_status():
    conn, tunnel = get_db_connection()
    items = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM asset_status ORDER BY status_id ASC")
            items = rows_to_dict(cur)
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return render_template('settings_status.html', items=items, user=current_user)

@app.route('/settings/status/save', methods=['POST'])
@login_required
@admin_required
def save_status():
    stat_id = request.form.get('status_id')
    name = request.form.get('status_name')
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if stat_id:
                cur.execute("UPDATE asset_status SET status_name=%s WHERE status_id=%s", (name, stat_id))
            else:
                cur.execute("INSERT INTO asset_status (status_name) VALUES (%s)", (name,))
            conn.commit()
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_status'))

@app.route('/settings/status/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_status(id):
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM asset_status WHERE status_id=%s", (id,))
            conn.commit()
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_status'))

@app.route('/settings/departments')
@login_required
@admin_required
def settings_departments():
    conn, tunnel = get_db_connection()
    items = []
    if conn:
        try:
            cur = conn.cursor(cursor_factory=extras.DictCursor)
            cur.execute("SELECT department_id, name, code FROM departments ORDER BY name ASC")
            items = cur.fetchall()
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return render_template('settings_departments.html', items=items, user=current_user)

@app.route('/settings/departments/save', methods=['POST'])
@login_required
@admin_required
def save_department():
    dept_id = request.form.get('department_id')
    name = request.form.get('name') 
    code = request.form.get('code') 
    
    # Mencegah error UNIQUE jika code kosong
    if not code or code.strip() == "":
        code = None
        
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if dept_id and str(dept_id).strip() != "": 
                # 1. Ambil kode lama sebelum update
                cur.execute("SELECT code FROM departments WHERE department_id = %s", (dept_id,))
                row = cur.fetchone()
                old_code = row[0] if row else None

                # 2. Update Data Departemen
                cur.execute("UPDATE departments SET name=%s, code=%s WHERE department_id=%s", (name, code, dept_id))
                
                # 3. Update Barcode Asset Otomatis
                if old_code and code and old_code != code:
                    cur.execute("SELECT asset_id, barcode FROM assets WHERE department_id = %s", (dept_id,))
                    assets = cur.fetchall()
                    updated_count = 0
                    for asset in assets:
                        asset_id, barcode = asset
                        if barcode and '/' in barcode:
                            parts = barcode.split('/')
                            new_parts = [code if part == old_code else part for part in parts]
                            new_barcode = "/".join(new_parts)
                            if new_barcode != barcode:
                                cur.execute("UPDATE assets SET barcode = %s WHERE asset_id = %s", (new_barcode, asset_id))
                                updated_count += 1
                    flash(f'Departemen disimpan & {updated_count} barcode asset diperbarui!', 'success')
                else:
                    flash('Data departemen berhasil disimpan!', 'success')
            else: 
                cur.execute("INSERT INTO departments (name, code) VALUES (%s, %s)", (name, code))
                flash('Data departemen berhasil disimpan!', 'success')
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            flash(f'Gagal menyimpan departemen: {e}', 'error')
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_categories')) 

@app.route('/settings/departments/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_department(id):
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM departments WHERE department_id = %s", (id,))
            conn.commit()
            cur.close()
            flash('Departemen berhasil dihapus!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Gagal menghapus! Pastikan tidak ada kategori yang masih terhubung ke departemen ini.', 'error')
        finally:
            conn.close()
            tunnel.stop()
    return redirect(url_for('settings_categories'))

# ==========================================
# 8. API & PUBLIC ROUTES (SCANNER)
# ==========================================
@app.route('/api/db-check')
def db_check():
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            return {"status": "online"}
        except:
            return {"status": "offline"}
        finally:
            conn.close()
            if tunnel: tunnel.stop()
    return {"status": "offline"}

@app.route('/scan/<path:barcode>')
def scan_asset(barcode):
    # Rute ini SENGAJA DIBUAT PUBLIK (tanpa @login_required)
    # Agar HP yang menge-scan QR bisa langsung melihat detail sebagai guest.
    conn, tunnel = get_db_connection()
    asset = None
    wa_link = None
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT a.*, c.name AS category_name, st.status_name,
                       d.name AS department_full, 
                       l.name AS lokasi_full, 
                       s.company_name AS supplier_name,
                       s.phone AS supplier_phone,
                       s.contact_person AS supplier_contact,
                       a.age_asset
                FROM assets a
                LEFT JOIN categories c ON a.category_id = c.category_id
                LEFT JOIN departments d ON a.department_id = d.department_id 
                LEFT JOIN locations l ON a.location_id = l.location_id
                LEFT JOIN suppliers s ON a.supplier_id = s.supplier_id
                LEFT JOIN asset_status st ON a.status_id = st.status_id
                WHERE a.barcode = %s
            """
            cur.execute(query, (barcode,))
            columns = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            if row:
                asset = dict(zip(columns, row))
                
                # Buat link WA otomatis menggunakan Python (Aman)
                if asset.get('supplier_phone'):
                    phone = ''.join(filter(str.isdigit, str(asset['supplier_phone'])))
                    if phone.startswith('0'):
                        phone = '62' + phone[1:]
                    wa_link = f"https://wa.me/{phone}"
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
            
    if not asset:
        return "<h2 style='font-family:sans-serif; text-align:center; padding:50px;'>Data Asset tidak ditemukan atau sudah dihapus.</h2>", 404
        
    return render_template('scan.html', asset=asset, wa_link=wa_link)

@app.route('/api/regenerate-barcode', methods=['POST'])
@login_required
@admin_or_user_required
def regenerate_barcode():
    asset_id = request.form.get('asset_id')
    action = request.form.get('action') # Tambahan untuk handling 'all'
    
    conn, tunnel = get_db_connection()
    response = {'status': 'error', 'message': 'Gagal terhubung database'}
    
    if conn:
        try:
            cur = conn.cursor()
            
            # --- LOGIC UPDATE MASSAL ---
            if action == 'all':
                # Ambil semua asset yang perlu diupdate
                cur.execute("""
                    SELECT a.asset_id, a.model, a.purchase_date, 
                           d.code, c.code, l.code
                    FROM assets a
                    LEFT JOIN departments d ON a.department_id = d.department_id
                    LEFT JOIN categories c ON a.category_id = c.category_id
                    LEFT JOIN locations l ON a.location_id = l.location_id
                """)
                rows = cur.fetchall()
                count = 0
                
                for row in rows:
                    aid, model, p_date, d_code, c_code, l_code = row
                    # Fallback jika kode kosong
                    d_code = d_code or 'UNK'
                    c_code = c_code or 'UNK'
                    l_code = l_code or 'UNK'
                    
                    # Format Tanggal (YYYY-MM) & Model (Kata pertama, kapital)
                    date_str = p_date.strftime('%Y-%m') if p_date else datetime.now().strftime('%Y-%m')
                    mod_str = model.split(' ')[0].upper()[:5] if model else 'GEN'
                    
                    # Susun Barcode Baru: DEP/CAT-MOD/LOC/YYYY-MM/GPB
                    new_barcode = f"{d_code}/{c_code}-{mod_str}/{l_code}/{date_str}/GPB"
                    
                    cur.execute("UPDATE assets SET barcode = %s WHERE asset_id = %s", (new_barcode, aid))
                    count += 1
                
                conn.commit()
                response = {'status': 'success', 'message': f'Berhasil memperbarui {count} barcode asset.'}

            # --- LOGIC UPDATE SATUAN (EXISTING) ---
            elif asset_id:
                # Ambil data relasi terbaru untuk menyusun barcode
                query = """
                    SELECT a.model, a.purchase_date, 
                           d.code as dept_code, 
                           c.code as cat_code, 
                           l.code as loc_code
                    FROM assets a
                    LEFT JOIN departments d ON a.department_id = d.department_id
                    LEFT JOIN categories c ON a.category_id = c.category_id
                    LEFT JOIN locations l ON a.location_id = l.location_id
                    WHERE a.asset_id = %s
                """
                cur.execute(query, (asset_id,))
                row = cur.fetchone()
                
                if row:
                    model, p_date, d_code, c_code, l_code = row
                    # Fallback jika kode kosong
                    d_code = d_code or 'UNK'
                    c_code = c_code or 'UNK'
                    l_code = l_code or 'UNK'
                    
                    # Format Tanggal (YYYY-MM) & Model (Kata pertama, kapital)
                    date_str = p_date.strftime('%Y-%m') if p_date else datetime.now().strftime('%Y-%m')
                    mod_str = model.split(' ')[0].upper()[:5] if model else 'GEN'
                    
                    # Susun Barcode Baru: DEP/CAT-MOD/LOC/YYYY-MM/GPB
                    new_barcode = f"{d_code}/{c_code}-{mod_str}/{l_code}/{date_str}/GPB"
                    
                    cur.execute("UPDATE assets SET barcode = %s WHERE asset_id = %s", (new_barcode, asset_id))
                    conn.commit()
                    response = {'status': 'success', 'new_barcode': new_barcode, 'message': 'Barcode berhasil diperbarui!'}
                else:
                    response = {'status': 'error', 'message': 'Data asset tidak ditemukan'}
            
            cur.close()
        except Exception as e:
            conn.rollback()
            response = {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
            tunnel.stop()
    return jsonify(response)

# ==========================================
# 10. API TAMBAH DATA CEPAT (MODAL)
# ==========================================
@app.route('/api/add-category', methods=['POST'])
@login_required
@admin_or_user_required
def api_add_category():
    name = request.form.get('category_name')
    code = request.form.get('category_code')
    dept_id = request.form.get('department_id')
    
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO categories (name, code, department_id) VALUES (%s, %s, %s) RETURNING category_id", 
                        (name, code, dept_id))
            new_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return jsonify({'status': 'success', 'id': new_id, 'name': name, 'code': code, 'department_id': dept_id})
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            conn.close()
            tunnel.stop()
    return jsonify({'status': 'error', 'message': 'Gagal terhubung ke database'})

@app.route('/api/add-location', methods=['POST'])
@login_required
@admin_or_user_required
def api_add_location():
    name = request.form.get('location_name')
    code = request.form.get('location_code')
    
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO locations (name, code) VALUES (%s, %s) RETURNING location_id", 
                        (name, code))
            new_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return jsonify({'status': 'success', 'id': new_id, 'name': name, 'code': code})
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            conn.close()
            tunnel.stop()
    return jsonify({'status': 'error', 'message': 'Gagal terhubung ke database'})

# ==========================================
# 11. EKSEKUSI APLIKASI
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)