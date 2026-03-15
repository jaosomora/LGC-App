"""
routes/dashboard.py — Rutas del dashboard (requieren autenticación).
"""
from functools import wraps
from datetime import date
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


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
        lugar_nac = request.form.get("lugar_nacimiento", "").strip()
        lugar_res = request.form.get("lugar_residencia", "").strip()
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

        current_user.lugar_nacimiento = lugar_nac or None
        current_user.lugar_residencia = lugar_res or None
        current_user.user_timezone = tz or None

        db.session.commit()
        flash("Perfil actualizado.", "success")
        return redirect(url_for("dashboard.perfil"))

    espacio = User.query.filter(User.created_at <= current_user.created_at).count() - 1
    return render_template("dashboard/perfil.html", espacio=espacio)


@dashboard_bp.route("/usuarios")
@owner_required
def usuarios():
    from models import User
    users = User.query.order_by(User.created_at.asc()).all()
    return render_template("dashboard/usuarios.html", users=users)
