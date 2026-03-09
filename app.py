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

from flask import Flask, render_template
from flask_cors import CORS
from models import db


def create_app():
    app = Flask(__name__)

    # --- Base de datos ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.getenv("RENDER") and os.getenv("ENV") == "PRODUCTION":
        os.makedirs("/mnt/data", exist_ok=True)
        db_path = os.path.join("/mnt/data", "palabras.db")
    else:
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

    # --- Inicializar BD ---
    db.init_app(app)

    # --- Blueprints ---
    from routes.api import api_bp
    app.register_blueprint(api_bp)

    # --- Rutas HTML ---
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/privacy-policy")
    def privacy_policy():
        return render_template("privacy_policy.html")

    # --- Crear tablas ---
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
