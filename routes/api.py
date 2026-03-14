"""
routes/api.py — Endpoints JSON API para Interfaz LGC.
"""
import os
import logging
import sqlite3
from flask import Blueprint, request, jsonify
from models import db, Palabra, Ranking
from calculos import (
    normalizar, es_valida, calcular_potencial, calcular_lupa,
    buscar_codigo_territorio, buscar_elementos_por_potencial,
    buscar_palabras_por_potencial, invertir_numero,
)
from data import get_territorios, get_tabla_periodica

api_bp = Blueprint("api", __name__, url_prefix="/api")
logger = logging.getLogger("api")


@api_bp.route("/buscar")
def buscar():
    """Busca palabras relacionadas, territorios y elementos para un potencial dado."""
    potencial = request.args.get("potencial", type=int)
    if potencial is None:
        return jsonify({"error": "parámetro potencial requerido"}), 400

    excluir_raw = request.args.get("excluir", "").strip().lower()
    excluir_set = set(e.strip() for e in excluir_raw.split(",") if e.strip()) if excluir_raw else set()

    # Cargar todas las palabras de la BD
    todas = [p.palabra for p in Palabra.query.all()]

    # Palabras con mismo potencial
    encontradas = buscar_palabras_por_potencial(todas, potencial)
    encontradas = list(set(normalizar(p) for p in encontradas))
    if excluir_set:
        encontradas = [p for p in encontradas if p not in excluir_set]

    # Palabras con potencial invertido
    total_invertido = invertir_numero(potencial)
    invertidas = buscar_palabras_por_potencial(todas, total_invertido)
    invertidas = list(set(normalizar(p) for p in invertidas))
    if excluir_set:
        invertidas = [p for p in invertidas if p not in excluir_set]

    # Ordenar por frecuencia de búsqueda (más buscadas primero)
    all_words = set(encontradas + invertidas)
    ranking_map = {
        r.palabra: r.puntuacion
        for r in Ranking.query.filter(Ranking.palabra.in_(all_words)).all()
    } if all_words else {}
    encontradas.sort(key=lambda p: (-ranking_map.get(p, 0), p))
    invertidas.sort(key=lambda p: (-ranking_map.get(p, 0), p))

    # Territorios y elementos
    territorios = buscar_codigo_territorio(get_territorios(), potencial)
    elementos = buscar_elementos_por_potencial(get_tabla_periodica(), potencial)

    return jsonify({
        "palabras_relacionadas": encontradas,
        "palabras_invertidas": invertidas,
        "total_invertido": total_invertido,
        "territorios": territorios,
        "elementos": elementos,
    })


@api_bp.route("/guardar", methods=["POST"])
def guardar():
    """Guarda una palabra en la BD y actualiza su ranking."""
    data = request.get_json(silent=True) or {}
    palabra = data.get("palabra", "").strip()
    if not palabra:
        return jsonify({"error": "palabra requerida"}), 400

    palabra_norm = normalizar(palabra)

    # Guardar palabra si es nueva
    existente = Palabra.query.filter_by(palabra=palabra_norm).first()
    if not existente:
        db.session.add(Palabra(palabra=palabra_norm))

    # Actualizar ranking
    ranking = Ranking.query.filter_by(palabra=palabra_norm).first()
    if ranking:
        ranking.puntuacion += 1
    else:
        db.session.add(Ranking(palabra=palabra_norm, puntuacion=1))

    db.session.commit()

    score = Ranking.query.filter_by(palabra=palabra_norm).first()
    return jsonify({
        "success": True,
        "puntuacion": score.puntuacion if score else 1,
    })


@api_bp.route("/ranking")
def ranking():
    """Top palabras más buscadas."""
    limit = request.args.get("limit", 20, type=int)
    entries = Ranking.query.order_by(Ranking.puntuacion.desc()).limit(limit).all()
    return jsonify({
        "ranking": [{"palabra": e.palabra, "puntuacion": e.puntuacion} for e in entries],
    })


@api_bp.route("/migrate-sqlite", methods=["POST"])
def migrate_sqlite():
    """Migración manual: copia datos de SQLite a PostgreSQL. Temporal."""
    secret = request.args.get("key", "")
    if secret != os.getenv("SECRET_KEY", ""):
        return jsonify({"error": "unauthorized"}), 403

    paths = ["/mnt/data/palabras.db", "/opt/render/project/src/palabras.db", "palabras.db"]
    sqlite_path = None
    for p in paths:
        if os.path.exists(p):
            sqlite_path = p
            break

    if not sqlite_path:
        return jsonify({"error": "SQLite not found", "checked": paths}), 404

    try:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Contar antes
        pg_palabras = Palabra.query.count()
        pg_ranking = Ranking.query.count()

        # Migrar Palabra
        cur.execute("SELECT palabra FROM palabra")
        rows_p = cur.fetchall()
        added_p = 0
        for row in rows_p:
            if not Palabra.query.filter_by(palabra=row["palabra"]).first():
                db.session.add(Palabra(palabra=row["palabra"]))
                added_p += 1

        # Migrar Ranking
        cur.execute("SELECT palabra, puntuacion FROM ranking")
        rows_r = cur.fetchall()
        added_r = 0
        for row in rows_r:
            existing = Ranking.query.filter_by(palabra=row["palabra"]).first()
            if not existing:
                db.session.add(Ranking(palabra=row["palabra"], puntuacion=row["puntuacion"]))
                added_r += 1
            else:
                existing.puntuacion = max(existing.puntuacion, row["puntuacion"])

        db.session.commit()
        conn.close()

        return jsonify({
            "success": True,
            "sqlite_path": sqlite_path,
            "sqlite_palabras": len(rows_p),
            "sqlite_rankings": len(rows_r),
            "added_palabras": added_p,
            "added_rankings": added_r,
            "pg_before": {"palabras": pg_palabras, "ranking": pg_ranking},
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


