"""
routes/api.py — Endpoints JSON API para Interfaz LGC.
"""
import os
import logging
from flask import Blueprint, request, jsonify
from models import db, Palabra, Ranking, User
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


@api_bp.route("/stats")
def stats():
    """Estadísticas de la app. Protegido con sesión (owner) o SECRET_KEY."""
    from flask_login import current_user
    secret = request.args.get("key", "")
    expected_key = os.getenv("SECRET_KEY", "")
    is_authorized = (
        (current_user.is_authenticated and current_user.is_owner)
        or (expected_key and secret == expected_key)
    )
    if not is_authorized:
        return jsonify({"error": "unauthorized"}), 403

    from sqlalchemy import func
    from datetime import datetime, timezone as tz, timedelta

    total_palabras = Palabra.query.count()
    total_rankings = Ranking.query.count()
    total_users = User.query.count()
    users_free = User.query.filter_by(plan="free").count()
    users_paid = total_users - users_free

    # Usuarios nuevos hoy
    today_start = datetime.now(tz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    users_today = User.query.filter(User.created_at >= today_start).count()

    # Top 10 más buscadas
    top = Ranking.query.order_by(Ranking.puntuacion.desc()).limit(10).all()

    # Usuarios registrados (últimos 10) con número de orden
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    all_ids_ordered = [u.id for u in User.query.order_by(User.created_at.asc()).all()]
    id_to_num = {uid: i + 1 for i, uid in enumerate(all_ids_ordered)}

    # Total de búsquedas (suma de todas las puntuaciones)
    total_searches = db.session.query(func.sum(Ranking.puntuacion)).scalar() or 0

    return jsonify({
        "palabras": total_palabras,
        "rankings": total_rankings,
        "users": total_users,
        "users_free": users_free,
        "users_paid": users_paid,
        "users_today": users_today,
        "total_searches": total_searches,
        "top_10": [{"palabra": r.palabra, "puntuacion": r.puntuacion} for r in top],
        "recent_users": [
            {
                "email": u.email,
                "nombre": u.nombre,
                "plan": u.plan,
                "is_owner": u.is_owner,
                "pais_residencia": u.pais_residencia or "",
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "num": id_to_num.get(u.id, 0),
            }
            for u in recent_users
        ],
    })


