from flask import Flask, session
from flask_login import LoginManager
from config import Config
from middleware.reverse_proxy import ReverseProxied
from database.pool import init_pool, close_pool
import logging
import atexit

# Inisialisasi Ekstensi
login_manager = LoginManager()

def create_app():
    # Setup Logging
    logging.basicConfig(level=logging.INFO)
    
    # Setup Flask App
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inisialisasi Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Silakan login terlebih dahulu untuk mengakses halaman ini."
    login_manager.login_message_category = "error"

    # Middleware Reverse Proxy untuk Nginx Subpath
    app.wsgi_app = ReverseProxied(app.wsgi_app, script_name='/inventory')

    # Inisialisasi Database Connection Pool
    with app.app_context():
        init_pool()
        
    # Pastikan pool ditutup saat aplikasi berhenti
    atexit.register(close_pool)

    # Setup User Loader
    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # Registrasi Blueprints (Routes)
    from routes.auth import auth_bp
    from routes.assets import assets_bp
    from routes.settings import settings_bp
    from routes.api import api_bp
    from routes.scanner import scanner_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(scanner_bp)

    return app

# Untuk eksekusi development (python app.py)
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)