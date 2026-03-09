"""
models.py — Modelos SQLAlchemy para Interfaz LGC.
2 tablas: Palabra, Ranking.
"""
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
