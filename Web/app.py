from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import extras
import paramiko
import json
from datetime import date, datetime
from decimal import Decimal
from sshtunnel import SSHTunnelForwarder

# --- MONKEY PATCH ---
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = None

app = Flask(__name__)
app.config.from_object('config.Config')

# Encoder khusus untuk tipe data Postgres
class PostgreEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.strftime('%d-%m-%Y')
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def rows_to_dict(cursor):
    """Mengubah hasil fetchall() menjadi list of dictionary berdasarkan nama kolom"""
    colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in cursor.fetchall()]

def get_db_connection():
    """Membuka sesi koneksi Tunnel dan Database"""
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
            # Tidak menggunakan RealDictCursor secara global untuk stabilitas
        )
        return conn, tunnel
    except Exception as e:
        print(f"ERROR KONEKSI: {e}")
        return None, None

@app.route('/')
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
    return render_template('index.html', total_assets=total_assets, recent_items=recent_items)

@app.route('/lihat-tabel')
def lihat_tabel():
    conn, tunnel = get_db_connection()
    assets_list = []
    if conn:
        try:
            cur = conn.cursor()
            # Hanya mengambil 3 kolom supplier yang tersedia di DB
            query = """
                SELECT a.asset_id, a.barcode, a.product_name, a.model, a.serial_number, 
                       a.purchase_date, a.purchase_cost, a.specs, 
                       c.name AS category_name, 
                       st.status_name,
                       COALESCE(l.site_name, '') || ' - ' || COALESCE(l.room_name, '') AS lokasi_full, 
                       s.company_name AS supplier_name,
                       s.phone AS supplier_phone, 
                       s.contact_person AS supplier_contact
                FROM assets a
                LEFT JOIN categories c ON a.category_id = c.category_id
                LEFT JOIN locations l ON a.location_id = l.location_id
                LEFT JOIN suppliers s ON a.supplier_id = s.supplier_id
                LEFT JOIN asset_status st ON a.status_id = st.status_id
                ORDER BY a.created_at DESC;
            """
            cur.execute(query)
            assets_list = rows_to_dict(cur)
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    
    # JSON String digunakan oleh JavaScript (Detail & QR)
    assets_json_str = json.dumps(assets_list, cls=PostgreEncoder)
    return render_template('tabel.html', assets=assets_list, assets_json=assets_json_str)

@app.route('/edit-tabel')
def edit_tabel():
    conn, tunnel = get_db_connection()
    assets_list, categories, locations, suppliers, statuses = [], [], [], [], []
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT a.*, c.name AS category_name, st.status_name,
                       COALESCE(l.site_name, '') || ' - ' || COALESCE(l.room_name, '') AS lokasi_full, 
                       s.company_name AS supplier_name
                FROM assets a
                LEFT JOIN categories c ON a.category_id = c.category_id
                LEFT JOIN locations l ON a.location_id = l.location_id
                LEFT JOIN suppliers s ON a.supplier_id = s.supplier_id
                LEFT JOIN asset_status st ON a.status_id = st.status_id
                ORDER BY a.created_at DESC;
            """
            cur.execute(query)
            assets_list = rows_to_dict(cur)
            
            # Data Dropdown
            cur.execute("SELECT category_id, name FROM categories ORDER BY name ASC")
            categories = rows_to_dict(cur)
            cur.execute("SELECT location_id, site_name, room_name FROM locations ORDER BY site_name ASC")
            locations = rows_to_dict(cur)
            cur.execute("SELECT supplier_id, company_name FROM suppliers ORDER BY company_name ASC")
            suppliers = rows_to_dict(cur)
            cur.execute("SELECT status_id, status_name FROM asset_status ORDER BY status_id ASC")
            statuses = rows_to_dict(cur)
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
            
    assets_json_str = json.dumps(assets_list, cls=PostgreEncoder)
    return render_template('edit-tabel.html', assets=assets_list, assets_json=assets_json_str,
                           categories=categories, locations=locations, suppliers=suppliers, statuses=statuses)

@app.route('/tambah-data')
def tambah_data():
    conn, tunnel = get_db_connection()
    categories, locations, suppliers, statuses = [], [], [], []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT category_id, name FROM categories ORDER BY name ASC")
            categories = rows_to_dict(cur)
            cur.execute("SELECT location_id, site_name, room_name FROM locations ORDER BY site_name ASC")
            locations = rows_to_dict(cur)
            cur.execute("SELECT supplier_id, company_name FROM suppliers ORDER BY company_name ASC")
            suppliers = rows_to_dict(cur)
            cur.execute("SELECT status_id, status_name FROM asset_status ORDER BY status_id ASC")
            statuses = rows_to_dict(cur)
            cur.close()
        finally:
            conn.close()
            tunnel.stop()
    return render_template('tambah-data.html', categories=categories, locations=locations, 
                           suppliers=suppliers, statuses=statuses)

@app.route('/simpan-data', methods=['POST'])
@app.route('/update-data', methods=['POST'])
def process_data():
    """Fungsi tunggal untuk handle Insert dan Update agar lebih efisien"""
    is_update = request.path == '/update-data'
    asset_id = request.form.get('asset_id')
    
    get_val = lambda key: request.form.get(key) or None
    get_int = lambda key: int(request.form.get(key)) if request.form.get(key) else None
    
    specs = get_val('specs') or '{}'
    
    data_tuple = (
        get_val('product_name'), get_val('barcode'), get_val('serial_number'), 
        get_val('model'), get_val('manufacturer'),
        get_int('category_id'), get_int('status_id'), get_int('location_id'), get_int('supplier_id'),
        get_val('purchase_date'), float(get_val('purchase_cost')) if get_val('purchase_cost') else None,
        specs
    )
    
    conn, tunnel = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if is_update and asset_id:
                cur.execute("""
                    UPDATE assets SET
                        product_name=%s, barcode=%s, serial_number=%s, model=%s, manufacturer=%s, 
                        category_id=%s, status_id=%s, location_id=%s, supplier_id=%s, purchase_date=%s, purchase_cost=%s, specs=%s
                    WHERE asset_id=%s
                """, data_tuple + (asset_id,))
            else:
                cur.execute("""
                    INSERT INTO assets (
                        product_name, barcode, serial_number, model, manufacturer, 
                        category_id, status_id, location_id, supplier_id, purchase_date, purchase_cost, specs
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, data_tuple)
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"ERROR DATABASE OP: {e}")
            conn.rollback()
        finally:
            conn.close()
            tunnel.stop()
            
    return redirect(url_for('edit_tabel'))

@app.route('/hapus-data/<int:asset_id>', methods=['POST'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)