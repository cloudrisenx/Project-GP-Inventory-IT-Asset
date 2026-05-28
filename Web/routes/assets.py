import json
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from psycopg2 import extras
from database.db import get_db
from routes.auth import admin_required, admin_or_user_required
from services.helper_service import rows_to_dict, PostgreEncoder

assets_bp = Blueprint('assets', __name__)

@assets_bp.route('/')
@login_required
def index():
    total_assets, recent_items = 0, []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM assets")
                    total_assets = cur.fetchone()[0]
                    
                    cur.execute("SELECT product_name, barcode, created_at FROM assets ORDER BY created_at DESC LIMIT 5")
                    recent_items = rows_to_dict(cur)
            except Exception as e:
                pass
    return render_template('index.html', total_assets=total_assets, recent_items=recent_items, user=current_user)

@assets_bp.route('/lihat-tabel')
@login_required
def lihat_tabel():
    assets_list = []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
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
                    
                    today = date.today()
                    for asset in assets_list:
                        bc = asset.get('barcode') or ''
                        if bc and '-' in bc.split('/')[-1] and bc.split('-')[-1].isdigit():
                            asset['base_barcode'] = bc.rsplit('-', 1)[0]
                        else:
                            asset['base_barcode'] = bc

                        cost = float(asset['purchase_cost']) if asset['purchase_cost'] else 0
                        lifespan = int(asset['age_asset']) if asset['age_asset'] else 0
                        p_date = asset['purchase_date']
                        
                        current_val = cost
                        
                        if lifespan > 0 and p_date:
                            if isinstance(p_date, datetime):
                                p_date = p_date.date()
                            months_passed = (today.year - p_date.year) * 12 + (today.month - p_date.month)
                            if months_passed > 0:
                                depreciation = (cost / lifespan) * months_passed
                                current_val = cost - depreciation
                        
                        asset['current_value'] = max(0, current_val)
            except Exception as e:
                pass
    
    assets_json_str = json.dumps(assets_list, cls=PostgreEncoder)
    return render_template('tabel.html', assets=assets_list, assets_json=assets_json_str, user=current_user)

@assets_bp.route('/edit-tabel')
@login_required
@admin_required
def edit_tabel():
    assets_list = []
    assets_json = "[]" 
    categories, locations, suppliers, statuses, departments = [], [], [], [], []
    
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                    cur.execute("""
                        SELECT a.*, 
                               d.name as department_full, 
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
                    assets_list = [dict(row) for row in assets]
                    assets_json = json.dumps(assets_list, cls=PostgreEncoder)

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
            except Exception as e:
                print(f"Error load data tabel: {e}")

    return render_template('edit-tabel.html', 
                           assets=assets_list, 
                           assets_json=assets_json, 
                           categories=categories, 
                           locations=locations, 
                           suppliers=suppliers, 
                           statuses=statuses, 
                           departments=departments, 
                           user=current_user)

@assets_bp.route('/tambah-data', methods=['GET', 'POST'])
@login_required
@admin_or_user_required
def tambah_data():
    categories, locations, suppliers, statuses, departments = [], [], [], [], []
    
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                    if request.method == 'POST':
                        try:
                            barcode = request.form.get('barcode')
                            name = request.form.get('name')  
                            department_id = request.form.get('department_id') 
                            category_id = request.form.get('category_id')     
                            location_id = request.form.get('location_id')
                            purchase_date = request.form.get('purchase_date')
                            purchase_cost = request.form.get('purchase_cost')
                            supplier_id = request.form.get('supplier_id')
                            status_id = request.form.get('status_id')
                            
                            age_asset = request.form.get('age_asset')
                            qty = request.form.get('qty')
                            qty = int(qty) if qty and str(qty).strip() != '' else 1
                            
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
                                
                            if qty > 1:
                                for i in range(1, qty + 1):
                                    current_barcode = barcode
                                    if current_barcode and current_barcode.endswith("-001"):
                                        current_barcode = current_barcode[:-4] + f"-{i:03d}"
                                    elif current_barcode:
                                        current_barcode = f"{current_barcode}-{i:03d}"
                                    
                                    cur.execute("""
                                        INSERT INTO assets (
                                            barcode, product_name, department_id, category_id, location_id, 
                                            purchase_date, purchase_cost, supplier_id, age_asset, status_id, qty
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (
                                        current_barcode, name, department_id, category_id, location_id,
                                        purchase_date, purchase_cost, supplier_id, age_asset, status_id, 1
                                    ))
                            else:
                                cur.execute("""
                                    INSERT INTO assets (
                                        barcode, product_name, department_id, category_id, location_id, 
                                        purchase_date, purchase_cost, supplier_id, age_asset, status_id, qty
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    barcode, name, department_id, category_id, location_id,
                                    purchase_date, purchase_cost, supplier_id, age_asset, status_id, qty
                                ))
                            
                            conn.commit()
                            flash('Data asset berhasil ditambahkan!', 'success')
                            return redirect(url_for('assets.tambah_data'))
                        except Exception as e:
                            conn.rollback()
                            flash(f'Terjadi kesalahan saat menyimpan data: {str(e)}', 'danger')

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
            except Exception as e:
                print(f"Database error: {e}")
            
    return render_template('tambah-data.html', 
                           categories=categories, locations=locations, suppliers=suppliers, 
                           statuses=statuses, departments=departments, user=current_user)

@assets_bp.route('/simpan-data', methods=['POST'])
@assets_bp.route('/update-data', methods=['POST'])
@login_required
@admin_required
def process_data():
    is_update = request.path == '/update-data'
    asset_id = request.form.get('asset_id')
    
    get_val = lambda key: request.form.get(key) or None
    get_int = lambda key: int(request.form.get(key)) if request.form.get(key) and request.form.get(key).strip() != "" else None
    
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
    
    purchase_cost = request.form.get('purchase_cost')
    purchase_cost = float(purchase_cost) if purchase_cost and purchase_cost.strip() != "" else 0.0

    age_asset = request.form.get('age_asset')
    age_asset = int(age_asset) if age_asset and age_asset.strip() != "" else 0

    qty = request.form.get('qty')
    qty = int(qty) if qty and qty.strip() != "" else 1

    data_tuple = (
        product_name, barcode, serial_number, model, manufacturer, 
        category_id, status_id, location_id, supplier_id, 
        department_id, purchase_date, purchase_cost, 
        warranty_info, keterangan, qty, age_asset
    )
    
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if is_update and asset_id:
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
                        if qty > 1:
                            base_barcode = barcode
                            for i in range(1, qty + 1):
                                current_barcode = base_barcode
                                if current_barcode and current_barcode.endswith("-001"):
                                    current_barcode = current_barcode[:-4] + f"-{i:03d}"
                                elif current_barcode:
                                    current_barcode = f"{current_barcode}-{i:03d}"
                                
                                insert_tuple = (
                                    product_name, current_barcode, serial_number, model, manufacturer, 
                                    category_id, status_id, location_id, supplier_id, 
                                    department_id, purchase_date, purchase_cost, 
                                    warranty_info, keterangan, 1, age_asset
                                )
                                cur.execute("""
                                    INSERT INTO assets (
                                        product_name, barcode, serial_number, model, manufacturer, 
                                        category_id, status_id, location_id, supplier_id, 
                                        department_id, purchase_date, purchase_cost, 
                                        warranty_info, keterangan, qty, age_asset
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, insert_tuple) 
                        else:
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
            except Exception as e:
                print(f"ERROR DATABASE OP: {e}")
                conn.rollback()
                flash(f'Terjadi kesalahan saat menyimpan data: {str(e)}', 'error')
    return redirect(url_for('assets.edit_tabel'))

@assets_bp.route('/hapus-data/<int:asset_id>', methods=['POST'])
@login_required
@admin_required
def hapus_data(asset_id):
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM assets WHERE asset_id = %s", (asset_id,))
                    conn.commit()
            except Exception as e:
                conn.rollback()
    return redirect(url_for('assets.edit_tabel'))