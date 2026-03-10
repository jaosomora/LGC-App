"""
routes/api.py — Endpoints JSON API para Interfaz LGC.
"""
import logging
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

    excluir = request.args.get("excluir", "").strip().lower()

    # Cargar todas las palabras de la BD
    todas = [p.palabra for p in Palabra.query.all()]

    # Palabras con mismo potencial
    encontradas = buscar_palabras_por_potencial(todas, potencial)
    encontradas = sorted(set(normalizar(p) for p in encontradas))
    if excluir:
        encontradas = [p for p in encontradas if normalizar(p) != excluir]

    # Palabras con potencial invertido
    total_invertido = invertir_numero(potencial)
    invertidas = buscar_palabras_por_potencial(todas, total_invertido)
    invertidas = sorted(set(normalizar(p) for p in invertidas))
    if excluir:
        invertidas = [p for p in invertidas if normalizar(p) != excluir]

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


