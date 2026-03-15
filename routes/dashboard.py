"""
routes/dashboard.py — Rutas del dashboard (requieren autenticación).
"""
import json
import os
from functools import wraps
from datetime import date
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# Cargar países una sola vez al importar el módulo
_countries_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static", "data", "countries.json"
)
with open(_countries_path, encoding="utf-8") as _f:
    COUNTRIES = json.load(_f)

# Lookup rápido: ISO code → nombre del país
_COUNTRY_MAP = {c["code"]: c["name"] for c in COUNTRIES}


def _country_name(code):
    """Devuelve nombre del país dado su ISO code, o cadena vacía."""
    return _COUNTRY_MAP.get(code, "") if code else ""


def owner_required(f):
    """Decorator: login + is_owner check."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_owner:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route("/")
@login_required
def index():
    if current_user.is_owner:
        return render_template("dashboard/control.html")
    return render_template("dashboard/index.html")


@dashboard_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    from models import db, User

    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre", "").strip()
        birth_str = request.form.get("birth_date", "").strip()
        deriv_str = request.form.get("fecha_derivacion", "").strip()
        pais_nac = request.form.get("pais_nacimiento", "").strip()
        ciudad_nac = request.form.get("ciudad_nacimiento", "").strip()
        pais_res = request.form.get("pais_residencia", "").strip()
        ciudad_res = request.form.get("ciudad_residencia", "").strip()
        tz = request.form.get("timezone", "").strip()

        if nuevo_nombre:
            if nuevo_nombre != current_user.nombre:
                current_user.nombre = nuevo_nombre
                current_user.nombre_custom = True

        if birth_str:
            try:
                p = birth_str.split("-")
                current_user.birth_date = date(int(p[0]), int(p[1]), int(p[2]))
            except (ValueError, IndexError):
                pass
        else:
            current_user.birth_date = None

        if deriv_str:
            try:
                p = deriv_str.split("-")
                current_user.fecha_derivacion = date(int(p[0]), int(p[1]), int(p[2]))
            except (ValueError, IndexError):
                pass
        else:
            current_user.fecha_derivacion = None

        current_user.pais_nacimiento = pais_nac or None
        current_user.ciudad_nacimiento = ciudad_nac or None
        current_user.pais_residencia = pais_res or None
        current_user.ciudad_residencia = ciudad_res or None
        current_user.user_timezone = tz or None

        db.session.commit()
        flash("Perfil actualizado.", "success")
        return redirect(url_for("dashboard.perfil"))

    espacio = User.query.filter(User.created_at <= current_user.created_at).count() - 1
    return render_template(
        "dashboard/perfil.html",
        espacio=espacio,
        countries=COUNTRIES,
        country_name_nac=_country_name(current_user.pais_nacimiento),
        country_name_res=_country_name(current_user.pais_residencia),
    )


@dashboard_bp.route("/usuarios")
@owner_required
def usuarios():
    from models import User
    users = User.query.order_by(User.created_at.asc()).all()
    return render_template("dashboard/usuarios.html", users=users, country_map=_COUNTRY_MAP)
