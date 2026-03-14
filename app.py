"""
app.py — Interfaz LGC: App factory mínima.
"""
import os
import logging
import sqlite3
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
    CORS(app, origins=[
        "https://lgc.julianosoriom.com",
        "https://lgc-app-1.onrender.com",
    ])

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

    # --- Crear tablas si no existen ---
    with app.app_context():
        db.create_all()
        _migrate_sqlite_to_pg(app)

    return app


def _migrate_sqlite_to_pg(app):
    """Migración one-shot: copia datos de SQLite viejo a PostgreSQL.

    Se ejecuta solo si:
    - Estamos en modo PostgreSQL (DATABASE_URL existe)
    - El archivo SQLite de Render existe (/mnt/data/palabras.db)
    - Las tablas PostgreSQL están vacías (primera vez)

    Después de copiar, NO borra el SQLite — solo deja de copiar porque
    PostgreSQL ya tiene datos.
    """
    if not os.getenv("DATABASE_URL"):
        return  # Estamos en dev local con SQLite, nada que migrar

    sqlite_path = "/mnt/data/palabras.db"
    if not os.path.exists(sqlite_path):
        app.logger.info("migrate: No SQLite file found at %s, skipping.", sqlite_path)
        return

    # Solo migrar si PostgreSQL está vacío
    from models import Palabra, Ranking
    pg_count = Palabra.query.count() + Ranking.query.count()
    if pg_count > 0:
        app.logger.info("migrate: PostgreSQL already has %d rows, skipping.", pg_count)
        return

    app.logger.info("migrate: Starting SQLite → PostgreSQL migration...")

    try:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Migrar Palabra
        cur.execute("SELECT palabra FROM palabra")
        palabras = cur.fetchall()
        for row in palabras:
            db.session.add(Palabra(palabra=row["palabra"]))
        app.logger.info("migrate: %d palabras copied.", len(palabras))

        # Migrar Ranking
        cur.execute("SELECT palabra, puntuacion FROM ranking")
        rankings = cur.fetchall()
        for row in rankings:
            db.session.add(Ranking(palabra=row["palabra"], puntuacion=row["puntuacion"]))
        app.logger.info("migrate: %d rankings copied.", len(rankings))

        db.session.commit()
        conn.close()
        app.logger.info("migrate: SQLite → PostgreSQL migration completed successfully.")

    except Exception as e:
        db.session.rollback()
        app.logger.error("migrate: Migration failed: %s", e)


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
