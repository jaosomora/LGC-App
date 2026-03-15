"""
routes/auth.py — Autenticación con Google OAuth 2.0.
"""
import os
from flask import Blueprint, redirect, url_for, session, flash
from flask_login import login_user, logout_user, current_user
from authlib.integrations.flask_client import OAuth

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

oauth = OAuth()


def init_oauth(app):
    """Inicializa OAuth con la app Flask."""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


@auth_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    redirect_uri = url_for("auth.callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/callback")
def callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get("userinfo")
    if not user_info:
        flash("No se pudo obtener información de Google.", "error")
        return redirect(url_for("public.index"))

    from models import db, User

    user = User.query.filter_by(email=user_info["email"]).first()
    if not user:
        user = User(
            email=user_info["email"],
            nombre=user_info.get("name", ""),
            avatar_url=user_info.get("picture"),
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Actualizar avatar siempre; nombre solo si no fue editado en perfil
        if not user.nombre_custom:
            user.nombre = user_info.get("name", user.nombre)
        user.avatar_url = user_info.get("picture", user.avatar_url)
        db.session.commit()

    login_user(user, remember=True)

    # Registrar último login + auto-bootstrap owner
    from datetime import datetime, timezone as tz
    user.last_login = datetime.now(tz.utc)
    owner_email = os.getenv("OWNER_EMAIL", "")
    if owner_email and user.email == owner_email and not user.is_owner:
        user.is_owner = True
    db.session.commit()

    return redirect(url_for("dashboard.index"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("public.index"))
