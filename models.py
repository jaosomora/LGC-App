"""
models.py — Modelos SQLAlchemy para Interfaz LGC.
Tablas: Palabra, Ranking, User.
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Palabra(db.Model):
    __tablename__ = "palabra"
    id = db.Column(db.Integer, primary_key=True)
    palabra = db.Column(db.Text, unique=True, nullable=False)


class Ranking(db.Model):
    __tablename__ = "ranking"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    palabra = db.Column(db.Text, unique=True, nullable=False)
    puntuacion = db.Column(db.Integer, nullable=False, default=1)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False, default="")
    avatar_url = db.Column(db.Text, nullable=True)
    plan = db.Column(db.String(20), nullable=False, default="free")
    is_owner = db.Column(db.Boolean, nullable=False, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Perfil
    birth_date = db.Column(db.Date, nullable=True)
    fecha_derivacion = db.Column(db.Date, nullable=True)  # Fecha derivación fundante
    pais_nacimiento = db.Column(db.String(5), nullable=True)    # ISO code: "CO"
    ciudad_nacimiento = db.Column(db.String(200), nullable=True)
    pais_residencia = db.Column(db.String(5), nullable=True)    # ISO code: "CO"
    ciudad_residencia = db.Column(db.String(200), nullable=True)
    user_timezone = db.Column(db.String(100), nullable=True)
    nombre_custom = db.Column(db.Boolean, nullable=False, default=False)
