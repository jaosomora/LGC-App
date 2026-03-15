#!/usr/bin/env python3
"""
generate_cities.py — Descarga el dataset GeoNames cities15000
y genera un JSON por país en static/data/cities/{CC}.json.

Uso:
    python scripts/generate_cities.py

Cada archivo es un array JSON de nombres de ciudad ordenados
por población descendente. Ejemplo CO.json:
    ["Bogotá", "Medellín", "Cali", "Barranquilla", ...]
"""

import io
import json
import os
import sys
import zipfile
from collections import defaultdict
from urllib.request import urlretrieve

URL = "https://download.geonames.org/export/dump/cities15000.zip"
INNER_FILE = "cities15000.txt"

# Columnas del TSV de GeoNames (0-indexed)
COL_NAME = 1          # nombre UTF-8
COL_COUNTRY = 8       # ISO-3166 alpha-2
COL_POPULATION = 14   # población

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "static", "data", "cities")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Descargar ──
    zip_path = os.path.join(SCRIPT_DIR, "cities15000.zip")
    if not os.path.exists(zip_path):
        print(f"Descargando {URL} ...")
        urlretrieve(URL, zip_path)
        print("Descarga completa.")
    else:
        print(f"Usando cache local: {zip_path}")

    # ── Parsear TSV ──
    cities = defaultdict(list)  # {country_code: [(name, population), ...]}

    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(INNER_FILE) as f:
            reader = io.TextIOWrapper(f, encoding="utf-8")
            for line in reader:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 15:
                    continue
                name = parts[COL_NAME]
                country = parts[COL_COUNTRY]
                try:
                    pop = int(parts[COL_POPULATION])
                except ValueError:
                    pop = 0
                cities[country].append((name, pop))

    # ── Generar JSONs ──
    total_cities = 0
    for cc, city_list in sorted(cities.items()):
        # Ordenar por población descendente
        city_list.sort(key=lambda x: x[1], reverse=True)
        names = [c[0] for c in city_list]
        total_cities += len(names)

        path = os.path.join(OUTPUT_DIR, f"{cc}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(names, f, ensure_ascii=False)

    print(f"Generados {len(cities)} archivos en {OUTPUT_DIR}")
    print(f"Total ciudades: {total_cities}")


if __name__ == "__main__":
    main()
