"""
models.py — Modelos SQLAlchemy para Interfaz LGC.
3 tablas: Palabra, Ranking, Feedback.
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


class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ip = db.Column(db.Text)
    user_agent = db.Column(db.Text)
    referer = db.Column(db.Text)
