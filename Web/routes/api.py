from flask import Blueprint, jsonify, request
from flask_login import login_required
from datetime import datetime
from database.db import get_db
from routes.auth import admin_or_user_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/db-check')
def db_check():
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return {"status": "online"}
            except:
                return {"status": "offline"}
    return {"status": "offline"}

@api_bp.route('/regenerate-barcode', methods=['POST'])
@login_required
@admin_or_user_required
def regenerate_barcode():
    asset_id = request.form.get('asset_id')
    action = request.form.get('action') 
    
    response = {'status': 'error', 'message': 'Gagal terhubung database'}
    
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    if action == 'all':
                        cur.execute("""
                            SELECT a.asset_id, a.model, a.purchase_date, 
                                   d.code, c.code, l.code, a.barcode
                            FROM assets a
                            LEFT JOIN departments d ON a.department_id = d.department_id
                            LEFT JOIN categories c ON a.category_id = c.category_id
                            LEFT JOIN locations l ON a.location_id = l.location_id
                        """)
                        rows = cur.fetchall()
                        count = 0
                        
                        for row in rows:
                            aid, model, p_date, d_code, c_code, l_code, old_barcode = row
                            d_code = d_code or 'UNK'
                            c_code = c_code or 'UNK'
                            l_code = l_code or 'UNK'
                            
                            date_str = p_date.strftime('%Y-%m') if p_date else datetime.now().strftime('%Y-%m')
                            mod_str = model.split(' ')[0].upper()[:5] if model else 'GEN'
                            
                            suffix = "-001"
                            if old_barcode and "/" in old_barcode and "-" in old_barcode.split("/")[-1]:
                                last_part = old_barcode.split("/")[-1]
                                if len(last_part.split("-")) > 1 and last_part.split("-")[-1].isdigit():
                                    suffix = f"-{last_part.split('-')[-1]}"

                            new_barcode = f"{d_code}/{c_code}-{mod_str}/{l_code}/{date_str}/GPB{suffix}"
                            cur.execute("UPDATE assets SET barcode = %s WHERE asset_id = %s", (new_barcode, aid))
                            count += 1
                        
                        conn.commit()
                        response = {'status': 'success', 'message': f'Berhasil memperbarui {count} barcode asset.'}

                    elif asset_id:
                        query = """
                            SELECT a.model, a.purchase_date, 
                                   d.code as dept_code, 
                                   c.code as cat_code, 
                                   l.code as loc_code,
                                   a.barcode as old_barcode
                            FROM assets a
                            LEFT JOIN departments d ON a.department_id = d.department_id
                            LEFT JOIN categories c ON a.category_id = c.category_id
                            LEFT JOIN locations l ON a.location_id = l.location_id
                            WHERE a.asset_id = %s
                        """
                        cur.execute(query, (asset_id,))
                        row = cur.fetchone()
                        
                        if row:
                            model, p_date, d_code, c_code, l_code, old_barcode = row
                            d_code = d_code or 'UNK'
                            c_code = c_code or 'UNK'
                            l_code = l_code or 'UNK'
                            
                            date_str = p_date.strftime('%Y-%m') if p_date else datetime.now().strftime('%Y-%m')
                            mod_str = model.split(' ')[0].upper()[:5] if model else 'GEN'
                            
                            suffix = "-001"
                            if old_barcode and "/" in old_barcode and "-" in old_barcode.split("/")[-1]:
                                last_part = old_barcode.split("/")[-1]
                                if len(last_part.split("-")) > 1 and last_part.split("-")[-1].isdigit():
                                    suffix = f"-{last_part.split('-')[-1]}"

                            new_barcode = f"{d_code}/{c_code}-{mod_str}/{l_code}/{date_str}/GPB{suffix}"
                            
                            cur.execute("UPDATE assets SET barcode = %s WHERE asset_id = %s", (new_barcode, asset_id))
                            conn.commit()
                            response = {'status': 'success', 'new_barcode': new_barcode, 'message': 'Barcode berhasil diperbarui!'}
                        else:
                            response = {'status': 'error', 'message': 'Data asset tidak ditemukan'}
            except Exception as e:
                conn.rollback()
                response = {'status': 'error', 'message': str(e)}
    return jsonify(response)

@api_bp.route('/add-category', methods=['POST'])
@login_required
@admin_or_user_required
def api_add_category():
    name = request.form.get('category_name')
    code = request.form.get('category_code')
    dept_id = request.form.get('department_id')
    
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO categories (name, code, department_id) VALUES (%s, %s, %s) RETURNING category_id", 
                                (name, code, dept_id))
                    new_id = cur.fetchone()[0]
                    conn.commit()
                    return jsonify({'status': 'success', 'id': new_id, 'name': name, 'code': code, 'department_id': dept_id})
            except Exception as e:
                conn.rollback()
                return jsonify({'status': 'error', 'message': str(e)})
    return jsonify({'status': 'error', 'message': 'Gagal terhubung ke database'})

@api_bp.route('/add-location', methods=['POST'])
@login_required
@admin_or_user_required
def api_add_location():
    name = request.form.get('location_name')
    code = request.form.get('location_code')
    
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO locations (name, code) VALUES (%s, %s) RETURNING location_id", 
                                (name, code))
                    new_id = cur.fetchone()[0]
                    conn.commit()
                    return jsonify({'status': 'success', 'id': new_id, 'name': name, 'code': code})
            except Exception as e:
                conn.rollback()
                return jsonify({'status': 'error', 'message': str(e)})
    return jsonify({'status': 'error', 'message': 'Gagal terhubung ke database'})