from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from psycopg2 import extras
from database.db import get_db
from routes.auth import admin_required, admin_or_user_required
from services.helper_service import rows_to_dict

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
@admin_or_user_required
def settings_index():
    return render_template('settings.html', user=current_user)

@settings_bp.route('/locations')
@login_required
@admin_or_user_required
def locations():
    items = []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                    cur.execute("SELECT location_id, name, code FROM locations ORDER BY name ASC")
                    items = cur.fetchall()
            except Exception as e:
                pass
    return render_template('settings_locations.html', items=items, user=current_user)

@settings_bp.route('/locations/save', methods=['POST'])
@login_required
@admin_or_user_required
def save_location():
    loc_id = request.form.get('location_id')
    name = request.form.get('name')
    code = request.form.get('code')
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if loc_id and str(loc_id).strip() != "": 
                        cur.execute("SELECT code FROM locations WHERE location_id = %s", (loc_id,))
                        row = cur.fetchone()
                        old_code = row[0] if row else None

                        cur.execute("UPDATE locations SET name=%s, code=%s WHERE location_id=%s", (name, code, loc_id))
                        
                        if old_code and code and old_code != code:
                            cur.execute("SELECT asset_id, barcode FROM assets WHERE location_id = %s", (loc_id,))
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
            except Exception as e:
                conn.rollback()
                flash(f'Gagal menyimpan lokasi: {e}', 'error')
    return redirect(url_for('settings.locations'))

@settings_bp.route('/locations/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_location(id):
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM locations WHERE location_id=%s", (id,))
                    conn.commit()
            except Exception as e:
                conn.rollback()
    return redirect(url_for('settings.locations'))

@settings_bp.route('/categories')
@login_required
@admin_required
def categories():
    items, departments = [], []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                    cur.execute("""
                        SELECT c.category_id, c.name, c.code, 
                               d.department_id, d.name as department_name, d.code as dept_code
                        FROM categories c
                        LEFT JOIN departments d ON c.department_id = d.department_id
                        ORDER BY d.name ASC, c.name ASC
                    """)
                    items = cur.fetchall()
                    
                    cur.execute("SELECT department_id, name, code FROM departments ORDER BY name ASC")
                    departments = cur.fetchall()
            except Exception as e:
                pass
    return render_template('settings_categories.html', items=items, departments=departments, user=current_user)

@settings_bp.route('/categories/save', methods=['POST'])
@login_required
@admin_required
def save_category():
    cat_id = request.form.get('category_id')
    name = request.form.get('name')
    dept_id = request.form.get('department_id')
    code = request.form.get('code')
    
    if not code or code.strip() == "":
        code = None
        
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if cat_id and str(cat_id).strip() != "":
                        cur.execute("SELECT code FROM categories WHERE category_id = %s", (cat_id,))
                        row = cur.fetchone()
                        old_code = row[0] if row else None

                        cur.execute("UPDATE categories SET name=%s, department_id=%s, code=%s WHERE category_id=%s", (name, dept_id, code, cat_id))
                        
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
            except Exception as e:
                conn.rollback()
                flash(f'Gagal menyimpan kategori: {e}', 'error')
    return redirect(url_for('settings.categories'))

@settings_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM categories WHERE category_id = %s", (id,))
                    conn.commit()
                    flash('Kategori berhasil dihapus!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'Gagal menghapus kategori: {e}', 'error')
    return redirect(url_for('settings.categories'))

@settings_bp.route('/suppliers')
@login_required
@admin_or_user_required
def suppliers():
    items = []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM suppliers ORDER BY company_name ASC")
                    items = rows_to_dict(cur)
            except Exception as e:
                pass
    return render_template('settings_suppliers.html', items=items, user=current_user)

@settings_bp.route('/suppliers/save', methods=['POST'])
@login_required
@admin_or_user_required
def save_supplier():
    sup_id = request.form.get('supplier_id')
    company = request.form.get('company_name')
    contact = request.form.get('contact_person')
    phone = request.form.get('phone')
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if sup_id:
                        cur.execute("""UPDATE suppliers SET company_name=%s, contact_person=%s, phone=%s 
                                       WHERE supplier_id=%s""", (company, contact, phone, sup_id))
                    else:
                        cur.execute("""INSERT INTO suppliers (company_name, contact_person, phone) 
                                       VALUES (%s, %s, %s)""", (company, contact, phone))
                    conn.commit()
            except Exception as e:
                conn.rollback()
    return redirect(url_for('settings.suppliers'))

@settings_bp.route('/suppliers/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_supplier(id):
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM suppliers WHERE supplier_id=%s", (id,))
                    conn.commit()
            except Exception as e:
                conn.rollback()
    return redirect(url_for('settings.suppliers'))

@settings_bp.route('/status')
@login_required
@admin_required
def status():
    items = []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM asset_status ORDER BY status_id ASC")
                    items = rows_to_dict(cur)
            except Exception as e:
                pass
    return render_template('settings_status.html', items=items, user=current_user)

@settings_bp.route('/status/save', methods=['POST'])
@login_required
@admin_required
def save_status():
    stat_id = request.form.get('status_id')
    name = request.form.get('status_name')
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if stat_id:
                        cur.execute("UPDATE asset_status SET status_name=%s WHERE status_id=%s", (name, stat_id))
                    else:
                        cur.execute("INSERT INTO asset_status (status_name) VALUES (%s)", (name,))
                    conn.commit()
            except Exception as e:
                conn.rollback()
    return redirect(url_for('settings.status'))

@settings_bp.route('/status/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_status(id):
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM asset_status WHERE status_id=%s", (id,))
                    conn.commit()
            except Exception as e:
                conn.rollback()
    return redirect(url_for('settings.status'))

@settings_bp.route('/departments')
@login_required
@admin_required
def departments():
    items = []
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                    cur.execute("SELECT department_id, name, code FROM departments ORDER BY name ASC")
                    items = cur.fetchall()
            except Exception as e:
                pass
    return render_template('settings_departments.html', items=items, user=current_user)

@settings_bp.route('/departments/save', methods=['POST'])
@login_required
@admin_required
def save_department():
    dept_id = request.form.get('department_id')
    name = request.form.get('name') 
    code = request.form.get('code') 
    
    if not code or code.strip() == "":
        code = None
        
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if dept_id and str(dept_id).strip() != "": 
                        cur.execute("SELECT code FROM departments WHERE department_id = %s", (dept_id,))
                        row = cur.fetchone()
                        old_code = row[0] if row else None

                        cur.execute("UPDATE departments SET name=%s, code=%s WHERE department_id=%s", (name, code, dept_id))
                        
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
            except Exception as e:
                conn.rollback()
                flash(f'Gagal menyimpan departemen: {e}', 'error')
    return redirect(url_for('settings.categories')) 

@settings_bp.route('/departments/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_department(id):
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM departments WHERE department_id = %s", (id,))
                    conn.commit()
                    flash('Departemen berhasil dihapus!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'Gagal menghapus! Pastikan tidak ada kategori yang masih terhubung ke departemen ini.', 'error')
    return redirect(url_for('settings.categories'))