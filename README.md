# Interfaz LGC

Aplicación web que convierte palabras en números usando el alfabeto español (A=1 ... Z=27, Ñ=15). Explora el potencial lógico de las palabras y descubre conexiones numéricas entre ellas.

## Funcionalidades

### Herramientas
- **Conversor** — Escribe una palabra, frase o número. Detección automática texto/número.
- **Comparar** — Compara dos palabras con suma y resta de potenciales.
- **Calendaria** — Calendario con cálculos de día solar, vueltas, anillo de fuego y más. Inputs DD/MM/AAAA.
- **Mapa interactivo** — Visualiza qué letras están activas en tu búsqueda.
- **Palabras relacionadas** — Encuentra otras palabras con el mismo potencial.
- **Total invertido** — Descubre palabras con el potencial invertido (ej. 68 → 86).
- **Historial y Ranking** — Registro local de búsquedas y ranking global.

### Dashboard
- **Mi Perfil** — Nombre, fecha de nacimiento, país y ciudad con autocomplete, zona horaria.
- **Centro de Control** — Gestión de usuarios (solo owner), numeración por orden de registro.
- **Autenticación** — Google OAuth con Authlib, protección de nombre editado (`nombre_custom`).

### Datos geográficos
- **196 países** con códigos ISO y indicativos telefónicos (`static/data/countries.json`).
- **68,000+ ciudades** del mundo con región/departamento, desde GeoNames cities5000 (`static/data/cities/`).
- **Códigos de área regionales** para 20 países: CO, MX, AR, BR, CL, PE, EC, VE, BO, PY, UY, CU, ES, FR, DE, IT, PT, GB, US, CA (`static/data/area_codes/`).
- **Autocomplete inteligente** para países y ciudades con normalización de acentos, teclado y mouse.

## Stack

- **Backend**: Flask 3.1, SQLAlchemy, Flask-Migrate (Alembic), Flask-Login, Authlib
- **Base de datos**: PostgreSQL (producción / Render), SQLite (local)
- **Frontend**: SPA con vanilla JS (ES5 IIFE), Tailwind CSS 3.4
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

### Regenerar datos geográficos (opcional)

```bash
python scripts/generate_cities.py       # Descarga GeoNames y genera JSONs de ciudades
python scripts/generate_area_codes.py   # Genera JSONs de códigos de área regionales
```

## Estructura

```
├── app.py                  # App factory Flask
├── models.py               # Modelos: User, Palabra, Ranking
├── calculos.py             # Lógica de cálculo (potencial, lupa, normalización)
├── data.py                 # Datos del alfabeto español
├── routes/
│   ├── api.py              # API: /api/buscar, /api/guardar, /api/ranking
│   ├── auth.py             # Google OAuth login/callback/logout
│   └── dashboard.py        # Dashboard: perfil, usuarios
├── templates/
│   ├── index.html          # SPA principal
│   ├── base_dashboard.html # Layout dashboard con sidebar
│   └── dashboard/          # Perfil, control, usuarios
├── static/
│   ├── js/
│   │   ├── app.js          # SPA completa (IIFE)
│   │   ├── calendaria.js   # Motor de cálculos Calendaria
│   │   └── autocomplete.js # Widget autocomplete ES5
│   ├── css/
│   │   ├── input.css       # Tailwind + variables de tema
│   │   └── output.css      # CSS compilado
│   └── data/
│       ├── countries.json  # 196 países (ISO + indicativo)
│       ├── cities/         # 245 JSONs de ciudades por país
│       └── area_codes/     # 20 JSONs de códigos de área por país
├── scripts/
│   ├── generate_cities.py      # Genera datos de ciudades desde GeoNames
│   └── generate_area_codes.py  # Genera datos de códigos de área
└── tailwind.config.js
```

## Despliegue (Render)

```
Build:  pip install -r requirements.txt
Start:  gunicorn wsgi:app
```

Variables de entorno: `ENV=PRODUCTION`, `SECRET_KEY`, `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.

## Licencia

MIT — [Julián Osorio Mora](https://julianosoriom.com)
