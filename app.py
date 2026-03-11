"""
app.py — Interfaz LGC: App factory mínima.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User


def create_app():
    app = Flask(__name__)

    # --- Base de datos ---
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Render usa postgres:// pero SQLAlchemy 2.x requiere postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "palabras.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")

    # --- Sesión ---
    env = os.getenv("ENV", "LOCAL")
    if env == "PRODUCTION":
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = False

    # --- CORS ---
    CORS(app, origins=["https://www.julianosoriom.com"])

    # --- Inicializar BD y migraciones ---
    db.init_app(app)
    Migrate(app, db)

    # --- Flask-Login ---
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- OAuth ---
    from routes.auth import auth_bp, init_oauth
    init_oauth(app)

    # --- Blueprints ---
    from routes.api import api_bp
    from routes.public import public_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)

    # --- Crear tablas (solo dev local con SQLite) ---
    if not database_url:
        with app.app_context():
            db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
