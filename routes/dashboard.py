"""
routes/dashboard.py — Rutas del dashboard (requieren autenticación).
"""
from functools import wraps
from flask import Blueprint, render_template, abort
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


@dashboard_bp.route("/usuarios")
@owner_required
def usuarios():
    from models import User
    users = User.query.order_by(User.created_at.asc()).all()
    return render_template("dashboard/usuarios.html", users=users)
