"""
data.py — Carga y caché de archivos JSON (territorios, tabla periódica).
"""
import os
import json

_base_dir = os.path.dirname(os.path.abspath(__file__))
_territorios = None
_tabla_periodica = None


def _cargar_json(nombre):
    path = os.path.join(_base_dir, nombre)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_territorios():
    global _territorios
    if _territorios is None:
        _territorios = _cargar_json("territorios.json")
    return _territorios


def get_tabla_periodica():
    global _tabla_periodica
    if _tabla_periodica is None:
        _tabla_periodica = _cargar_json("tabla_periodica.json")
    return _tabla_periodica
