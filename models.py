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
    palabra = db.Column(db.String(100), unique=True, nullable=False)


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
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
