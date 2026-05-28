from contextlib import contextmanager
from database.pool import get_db_connection, release_db_connection

@contextmanager
def get_db():
    """Context manager untuk meminjam dan melepaskan koneksi database secara otomatis."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        if conn:
            release_db_connection(conn)