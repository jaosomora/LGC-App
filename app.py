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
        _ensure_owner_columns(app)
        _ensure_profile_columns(app)
        _bootstrap_owner(app)
        _migrate_sqlite_if_needed(app)

    return app


def _ensure_owner_columns(app):
    """Agrega columnas is_owner y last_login si no existen (para PG existente)."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    with db.engine.connect() as conn:
        if "is_owner" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_owner BOOLEAN DEFAULT FALSE NOT NULL"))
            conn.commit()
            app.logger.info("Added is_owner column to users table.")
        if "last_login" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP"))
            conn.commit()
            app.logger.info("Added last_login column to users table.")


def _ensure_profile_columns(app):
    """Agrega columnas de perfil si no existen (para PG existente)."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    new_cols = [
        ("birth_date", "DATE"),
        ("fecha_derivacion", "DATE"),
        ("pais_nacimiento", "VARCHAR(5)"),
        ("ciudad_nacimiento", "VARCHAR(200)"),
        ("pais_residencia", "VARCHAR(5)"),
        ("ciudad_residencia", "VARCHAR(200)"),
        ("user_timezone", "VARCHAR(100)"),
        ("nombre_custom", "BOOLEAN DEFAULT FALSE NOT NULL"),
        ("google_access_token", "TEXT"),
        ("google_refresh_token", "TEXT"),
        ("google_token_expires_at", "TIMESTAMP"),
    ]
    with db.engine.connect() as conn:
        for col_name, col_type in new_cols:
            if col_name not in columns:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                app.logger.info(f"Added {col_name} column to users table.")


def _bootstrap_owner(app):
    """Setea is_owner=True para el email en OWNER_EMAIL."""
    owner_email = os.getenv("OWNER_EMAIL")
    if not owner_email:
        return
    owner = User.query.filter_by(email=owner_email).first()
    if owner and not owner.is_owner:
        owner.is_owner = True
        db.session.commit()
        app.logger.info("Owner bootstrapped: %s", owner_email)


def _migrate_sqlite_if_needed(app):
    """
    Auto-migración one-shot: si PostgreSQL está conectado, el archivo SQLite
    existe en /mnt/data/palabras.db, y la tabla Palabra está vacía,
    copia palabras y rankings desde SQLite a PostgreSQL.
    Se ejecuta solo una vez (cuando PG está vacío).
    """
    from models import Palabra, Ranking
    import sqlite3

    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        return  # Estamos en local con SQLite, no migrar

    sqlite_path = "/mnt/data/palabras.db"
    if not os.path.exists(sqlite_path):
        app.logger.info("Auto-migrate: SQLite file not found at %s, skipping.", sqlite_path)
        return

    # Solo migrar si PostgreSQL está vacío
    count = Palabra.query.count()
    if count > 0:
        app.logger.info("Auto-migrate: Palabra table has %d records, skipping.", count)
        return

    app.logger.info("Auto-migrate: PostgreSQL vacío, iniciando migración desde SQLite...")

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Migrar palabras (batch — tabla ya está vacía)
        cursor.execute("SELECT palabra FROM palabra")
        palabras_rows = cursor.fetchall()
        seen_p = set()
        batch_p = []
        for (p,) in palabras_rows:
            if p and p.strip() and p.strip() not in seen_p:
                seen_p.add(p.strip())
                batch_p.append(Palabra(palabra=p.strip()))
        if batch_p:
            db.session.bulk_save_objects(batch_p)
            db.session.commit()
        app.logger.info("Auto-migrate: %d palabras agregadas.", len(batch_p))

        # Migrar rankings (batch — tabla ya está vacía)
        cursor.execute("SELECT palabra, puntuacion FROM ranking")
        ranking_rows = cursor.fetchall()
        seen_r = set()
        batch_r = []
        for palabra, puntuacion in ranking_rows:
            if palabra and palabra.strip() and palabra.strip() not in seen_r:
                seen_r.add(palabra.strip())
                batch_r.append(Ranking(palabra=palabra.strip(), puntuacion=puntuacion or 1))
        if batch_r:
            db.session.bulk_save_objects(batch_r)
            db.session.commit()
        app.logger.info("Auto-migrate: %d rankings agregados.", len(batch_r))

        conn.close()
        app.logger.info("Auto-migrate: Migración completada exitosamente.")

    except Exception as e:
        db.session.rollback()
        app.logger.error("Auto-migrate: Error durante migración: %s", e)


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
