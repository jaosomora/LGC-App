"""
routes/auth.py — Autenticación con Google OAuth 2.0.
"""
import os
from datetime import datetime, timezone as tz
from flask import Blueprint, redirect, url_for, session, flash
from flask_login import login_required, login_user, logout_user, current_user
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
    user.last_login = datetime.now(tz.utc)
    owner_email = os.getenv("OWNER_EMAIL", "")
    if owner_email and user.email == owner_email and not user.is_owner:
        user.is_owner = True
    db.session.commit()

    return redirect(url_for("dashboard.index"))


# ── Google Docs OAuth (flujo separado) ──

GDOCS_SCOPES = (
    "openid email profile "
    "https://www.googleapis.com/auth/documents "
    "https://www.googleapis.com/auth/drive.file"
)


@auth_bp.route("/connect-gdocs")
@login_required
def connect_gdocs():
    """Inicia OAuth para permisos de Google Docs/Drive."""
    redirect_uri = url_for("auth.gdocs_callback", _external=True)
    return oauth.google.authorize_redirect(
        redirect_uri,
        access_type="offline",
        prompt="consent",
        scope=GDOCS_SCOPES,
    )


@auth_bp.route("/gdocs-callback")
@login_required
def gdocs_callback():
    """Callback: guarda tokens de Google Docs."""
    from models import db

    token = oauth.google.authorize_access_token()
    current_user.google_access_token = token.get("access_token")
    current_user.google_refresh_token = token.get("refresh_token")
    if token.get("expires_at"):
        current_user.google_token_expires_at = datetime.fromtimestamp(
            token["expires_at"], tz=tz.utc
        )
    db.session.commit()
    flash("Google Docs conectado exitosamente.", "success")
    return redirect(url_for("dashboard.reactivos"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("public.index"))
