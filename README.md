# Interfaz LGC

Aplicación web que convierte palabras en números usando el alfabeto español (A=1 ... Z=27, Ñ=15). Explora el potencial lógico de las palabras y descubre conexiones numéricas entre ellas.

## Funcionalidades

- **Conversor** — Escribe una palabra, frase o número. Detección automática texto/número.
- **Comparar** — Compara dos palabras con suma y resta de potenciales.
- **Mapa interactivo** — Visualiza qué letras están activas en tu búsqueda.
- **Palabras relacionadas** — Encuentra otras palabras con el mismo potencial.
- **Total invertido** — Descubre palabras con el potencial invertido (ej. 68 → 86).
- **Historial y Ranking** — Registro local de búsquedas y ranking global.

## Stack

- **Backend**: Flask 3.1, SQLAlchemy, SQLite
- **Frontend**: SPA con vanilla JS, Tailwind CSS 3.4
- **Diseño**: Glass morphism, modo oscuro/claro, acento naranja

## Instalación

```bash
git clone https://github.com/jaosomora/LGC-App.git
cd LGC-App
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre http://localhost:8080

## Estructura

```
├── app.py              # App factory Flask
├── models.py           # Modelos: Palabra, Ranking
├── calculos.py         # Lógica de cálculo (potencial, lupa, normalización)
├── data.py             # Datos del alfabeto español
├── routes/api.py       # API: /api/buscar, /api/guardar, /api/ranking
├── templates/index.html
├── static/js/app.js    # SPA completa (IIFE)
├── static/css/
│   ├── input.css       # Tailwind + variables de tema
│   └── output.css      # CSS compilado
└── tailwind.config.js
```

## Despliegue (Render)

```
Build:  pip install -r requirements.txt
Start:  gunicorn wsgi:app
```

Variables de entorno: `ENV=PRODUCTION`, `SECRET_KEY`.

## Licencia

MIT — [Julián Osorio Mora](https://julianosoriom.com)
