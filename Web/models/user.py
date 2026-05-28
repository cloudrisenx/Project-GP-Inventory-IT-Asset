from flask_login import UserMixin
from database.db import get_db

class User(UserMixin):
    def __init__(self, id, username, nama_lengkap, role):
        self.id = id
        self.username = username
        self.nama_lengkap = nama_lengkap
        self.role = role

    @staticmethod
    def get(user_id):
        with get_db() as conn:
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("SELECT id, username, nama_lengkap, role FROM users WHERE id = %s", (int(user_id),))
                        user_data = cur.fetchone()
                        if user_data:
                            return User(
                                id=user_data[0], 
                                username=user_data[1], 
                                nama_lengkap=user_data[2], 
                                role=user_data[3]
                            )
                except Exception as e:
                    print(f"Error loading user: {e}")
        return None