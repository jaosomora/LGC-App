#!/usr/bin/env python3
"""
generate_cities.py — Descarga el dataset GeoNames cities5000
y admin1CodesASCII, genera un JSON por país en static/data/cities/{CC}.json.

Uso:
    python scripts/generate_cities.py

Cada archivo es un array JSON de strings "Ciudad, Región" ordenados
por población descendente. Ejemplo CO.json:
    ["Bogotá, Bogota D.C.", "Medellín, Antioquia", "Cali, Valle del Cauca", ...]
"""

import io
import json
import os
import zipfile
from collections import defaultdict
from urllib.request import urlretrieve

CITIES_URL = "https://download.geonames.org/export/dump/cities5000.zip"
CITIES_INNER = "cities5000.txt"
ADMIN1_URL = "https://download.geonames.org/export/dump/admin1CodesASCII.txt"

# Columnas del TSV de GeoNames (0-indexed)
COL_NAME = 1          # nombre UTF-8
COL_COUNTRY = 8       # ISO-3166 alpha-2
COL_ADMIN1 = 10       # código admin1
COL_POPULATION = 14   # población

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "static", "data", "cities")


def download(url, local_name):
    """Descarga un archivo si no existe localmente."""
    path = os.path.join(SCRIPT_DIR, local_name)
    if not os.path.exists(path):
        print(f"Descargando {url} ...")
        urlretrieve(url, path)
        print("Descarga completa.")
    else:
        print(f"Usando cache local: {path}")
    return path


def load_admin1(path):
    """Carga admin1CodesASCII.txt → dict {CC.CODE: nombre}"""
    admin1 = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                # parts[0] = "CO.11", parts[1] = "Bogota D.C."
                admin1[parts[0]] = parts[1]
    print(f"Cargadas {len(admin1)} regiones admin1.")
    return admin1


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Descargar archivos ──
    zip_path = download(CITIES_URL, "cities5000.zip")
    admin1_path = download(ADMIN1_URL, "admin1CodesASCII.txt")

    # ── Cargar admin1 ──
    admin1 = load_admin1(admin1_path)

    # ── Parsear ciudades ──
    cities = defaultdict(list)  # {country_code: [(display_name, population), ...]}

    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(CITIES_INNER) as f:
            reader = io.TextIOWrapper(f, encoding="utf-8")
            for line in reader:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 15:
                    continue

                name = parts[COL_NAME]
                country = parts[COL_COUNTRY]
                admin1_code = parts[COL_ADMIN1]

                try:
                    pop = int(parts[COL_POPULATION])
                except ValueError:
                    pop = 0

                # Buscar nombre de la región
                admin1_key = f"{country}.{admin1_code}"
                region = admin1.get(admin1_key, "")

                # Formato: "Ciudad, Región" o solo "Ciudad" si no hay región
                display = f"{name}, {region}" if region else name

                cities[country].append((display, pop))

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
