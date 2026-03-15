# Interfaz LGC — Contexto del Proyecto

## Qué es
Aplicación web que convierte palabras en números usando el alfabeto español (A=1, B=2 ... N=14, Ñ=15, O=16 ... Z=27). Cada letra tiene un valor fijo y el "potencial" de una palabra es la suma de sus letras. La app explora conexiones numéricas entre palabras.

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | Flask 3.1, SQLAlchemy, Flask-Migrate (Alembic), Flask-Login, Authlib (Google OAuth) |
| BD producción | PostgreSQL (Render) |
| BD local | SQLite (`palabras.db`) |
| Frontend | SPA vanilla JS, Tailwind CSS 3.4 con `@tailwindcss/forms` |
| Fuente | Inter (Google Fonts) |
| Deploy | Render — `gunicorn wsgi:app` |

## Convenciones CRÍTICAS de JavaScript

- **`app.js`** usa ES6 (const, let, arrow functions) — es la SPA pública original
- **`dashboard.js`**, **`autocomplete.js`**, **`calendaria.js`** usan **ES5 estricto**: solo `var`, funciones con `function`, IIFE `(function(){ "use strict"; ... })()`. **NO usar** `const`, `let`, arrow functions, template literals, ni destructuring en estos archivos
- Todos los JS del dashboard son IIFE auto-ejecutables

## Diseño y CSS

- **Glass morphism**: Componentes con `backdrop-filter: blur()` y transparencias
- **Modo oscuro/claro**: Variable `data-theme` en `<html>`, CSS variables en `input.css`
- **Acento naranja**: `--c-accent: 249 115 22` (dark) / `234 88 12` (light)
- **Clases glass**: `glass-card`, `glass-input`, `glass-button`, `glass-panel`
- **Sidebar**: `sidebar-link`, `sidebar-link.active`, `sidebar-link.disabled`
- **Build CSS**: `npx tailwindcss -i static/css/input.css -o static/css/output.css --minify`
- **Colores Tailwind custom**: `th-bg`, `th-text`, `th-accent`, `th-muted`, `th-error`, `th-surface`

## Estructura de archivos clave

```
app.py                     # App factory, create_app(), _ensure_*_columns()
models.py                  # User, Palabra, Ranking
calculos.py                # Lógica pura: calcular_potencial(), normalizar(), calcular_lupa()
data.py                    # Caché de territorios.json y tabla_periodica.json
routes/
  api.py                   # /api/buscar, /api/guardar, /api/ranking, /api/stats
  auth.py                  # Google OAuth: /auth/login, /auth/callback, /auth/logout
  public.py                # / (SPA), /privacy-policy
  dashboard.py             # /dashboard, /dashboard/perfil, /dashboard/usuarios
templates/
  index.html               # SPA pública (extiende base_public.html)
  base_dashboard.html      # Layout dashboard: sidebar + topbar + user menu
  dashboard/
    control.html            # Centro de Control (owner only) — KPIs, top 10, recientes
    perfil.html             # Mi Perfil — nombre, fecha, país/ciudad con autocomplete
    usuarios.html           # Lista de usuarios (owner only) — tabla con búsqueda
static/
  js/app.js                # SPA completa (IIFE, ES6)
  js/dashboard.js          # Sidebar, theme, user menu, Centro de Control renders
  js/autocomplete.js       # Widget LgcAutocomplete reutilizable (ES5)
  js/calendaria.js         # Motor de cálculos Calendaria (ES5)
  css/input.css            # Tailwind source + variables de tema + componentes glass
  css/output.css           # CSS compilado (no editar directamente)
  data/
    countries.json          # 196 países [{code, name, phone}]
    cities/{CC}.json        # ~245 archivos, ciudades por país ["Ciudad, Región", ...]
    area_codes/{CC}.json    # ~20 archivos, {región: código_de_área}
```

## Modelo User

```python
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id              # PK
    email           # Único, de Google OAuth
    nombre          # Nombre de Google (o editado por usuario)
    avatar_url      # Foto de Google
    plan            # "free" (default) o "paid"
    is_owner        # True para el admin (OWNER_EMAIL en .env)
    last_login      # Último login
    created_at      # Fecha de registro
    birth_date      # Fecha de nacimiento (Date)
    pais_nacimiento # ISO code 2 letras ("CO", "MX", ...)
    ciudad_nacimiento  # "Ciudad, Región" (texto libre)
    pais_residencia # ISO code 2 letras
    ciudad_residencia  # "Ciudad, Región" (texto libre)
    user_timezone   # IANA timezone ("America/Bogota")
    nombre_custom   # True si el usuario editó su nombre → Google no lo sobreescribe
```

## Conceptos del negocio

- **Potencial**: Suma de valores de letras (A=1...Z=27, Ñ=15)
- **Lupa**: Potencial × 1.21
- **Normalización**: Minúsculas, elimina tildes (preserva ñ), colapsa espacios
- **Palabras relacionadas**: Palabras en BD con el mismo potencial
- **Total invertido**: Dígitos invertidos del potencial (68 → 86)
- **Espacio**: Número de registro del usuario (orden por created_at, base 0)
- **nombre_custom**: Protege el nombre editado para que Google OAuth no lo sobreescriba al hacer login

## Datos geográficos

- **countries.json**: 196 países con `code` (ISO 2), `name`, `phone` (indicativo)
- **cities/{CC}.json**: Arrays de strings `"Ciudad, Región"` ordenados por población desc. Generados desde GeoNames cities5000
- **area_codes/{CC}.json**: Objeto `{región: código_de_área}`. 20 países: CO, MX, AR, BR, CL, PE, EC, VE, BO, PY, UY, CU, ES, FR, DE, IT, PT, GB, US, CA
- Los nombres de región deben coincidir con los de GeoNames `admin1CodesASCII.txt`
- **Scripts**: `scripts/generate_cities.py`, `scripts/generate_area_codes.py`

## Widget Autocomplete (LgcAutocomplete)

Widget ES5 reutilizable en `static/js/autocomplete.js`:
- `new LgcAutocomplete(inputEl, {data, onSelect, onClear, strict, displayFn})`
- `setData(newArray)` para actualizar opciones dinámicamente
- `setValue(value, label)` para setear programáticamente
- Modo `strict`: solo permite valores del array (países). Sin strict: texto libre (ciudades)
- Normalización NFD para búsqueda sin acentos

## Decoradores de ruta

- `@login_required` — requiere autenticación (Flask-Login)
- `@owner_required` — requiere `is_owner == True` (definido en `routes/dashboard.py`)

## Variables de entorno

```
SECRET_KEY          # Clave secreta Flask
DATABASE_URL        # PostgreSQL connection string (Render)
GOOGLE_CLIENT_ID    # OAuth
GOOGLE_CLIENT_SECRET # OAuth
OWNER_EMAIL         # Email del admin (auto-bootstrap is_owner=True)
ENV                 # "PRODUCTION" o "LOCAL"
```

## Producción vs Local

- **Producción**: PostgreSQL, `SESSION_COOKIE_SECURE=True`, `SameSite=None`, CORS para `lgc.julianosoriom.com`
- **Local**: SQLite, `SESSION_COOKIE_SECURE=False`, `SameSite=Lax`, puerto 8080
- `_ensure_owner_columns()` y `_ensure_profile_columns()` agregan columnas faltantes en PostgreSQL existente sin necesidad de migraciones manuales

## Cosas a tener en cuenta

- Al regenerar archivos de ciudades en macOS, pueden aparecer archivos duplicados con sufijo " 2" por el filesystem case-insensitive. Limpiar con: `cd static/data/cities && for f in *" 2.json"; do rm "$f"; done`
- El sidebar está en `base_dashboard.html`. Las herramientas deshabilitadas usan `<span class="sidebar-link disabled">` en vez de `<a>`
- La sección de herramientas se llama "Herramientas LGC"
- "La tabla te habla" es una herramienta pendiente (equivalente a tabla periódica de elementos)
- Versión actual: v2.1.0
