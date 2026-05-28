from flask import Blueprint, render_template
from database.db import get_db

scanner_bp = Blueprint('scanner', __name__)

@scanner_bp.route('/scan/<path:barcode>')
def scan_asset(barcode):
    asset = None
    wa_link = None
    with get_db() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
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
                        
                        if asset.get('supplier_phone'):
                            phone = ''.join(filter(str.isdigit, str(asset['supplier_phone'])))
                            if phone.startswith('0'):
                                phone = '62' + phone[1:]
                            wa_link = f"https://wa.me/{phone}"
            except Exception as e:
                print(e)
            
    if not asset:
        return "<h2 style='font-family:sans-serif; text-align:center; padding:50px;'>Data Asset tidak ditemukan atau sudah dihapus.</h2>", 404
        
    return render_template('scan.html', asset=asset, wa_link=wa_link)