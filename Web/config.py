import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Keamanan
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-secret-key'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Konfigurasi Database
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'inventory_db')
    DB_USER = os.environ.get('DB_USER', 'inventory_admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'GPBandungan2025')
    
    # Konfigurasi Connection Pool
    DB_POOL_MINCONN = int(os.environ.get('DB_POOL_MINCONN', 1))
    DB_POOL_MAXCONN = int(os.environ.get('DB_POOL_MAXCONN', 20))
