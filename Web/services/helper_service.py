import json
from datetime import date, datetime
from decimal import Decimal

class PostgreEncoder(json.JSONEncoder):
    """Custom JSON Encoder untuk tipe data PostgreSQL (datetime, Decimal)."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.strftime('%d-%m-%Y')
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def rows_to_dict(cursor):
    """Mengubah hasil fetchall PostgreSQL menjadi list of dictionaries."""
    colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in cursor.fetchall()]