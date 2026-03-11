"""
routes/public.py — Rutas de páginas públicas.
"""
from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return render_template("index.html")


@public_bp.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")
