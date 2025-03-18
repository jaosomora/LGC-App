# Interfaz LGC

![Interfaz LGC Banner](https://www.julianosoriom.com/wp-content/uploads/2023/11/logo-lgc.png)

## 🌟 Descripción

Interfaz LGC es una aplicación web que explora la relación numérica entre palabras y números. La aplicación permite descubrir conexiones matemáticas entre palabras, fórmulas y conceptos mediante cálculos de potencial y frecuencia lógica, ofreciendo una perspectiva única sobre cómo las palabras pueden expresarse numéricamente.

### ✨ Características principales

- **Conversión de palabras a números**: Convierte cualquier palabra o frase en un valor numérico único utilizando un algoritmo especial
- **Búsqueda inversa**: Encuentra palabras que corresponden a un número específico
- **Comparación de palabras**: Analiza matemáticamente la relación entre dos o más palabras
- **Análisis detallado**: Visualiza el desglose letra por letra de cada cálculo
- **Historial de búsquedas**: Accede a tus consultas previas organizadas por relevancia
- **Sistema de feedback**: Comparte tu experiencia y sugerencias directamente desde la aplicación

## 🤖 Características Automáticas

Interfaz LGC está diseñada con un enfoque "plug and play", minimizando la configuración manual necesaria. Esto facilita tanto el desarrollo como el despliegue.

### Verificación e instalación automática de dependencias

La aplicación verifica automáticamente si las dependencias requeridas están instaladas. Si falta alguna:

```python
# Código que se ejecuta automáticamente al iniciar la aplicación
def instalar_dependencias():
    try:
        import flask_sqlalchemy
        import flask_cors
    except ImportError:
        print("Dependencias faltantes. Instalándolas...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
```

### Configuración adaptativa de base de datos

La aplicación detecta automáticamente el entorno y configura la base de datos en la ubicación adecuada:

```python
# En producción (Render)
if os.getenv("RENDER") and os.getenv("ENV") == "PRODUCTION":
    db_path = os.path.join("/mnt/data", "palabras.db")  # Ruta persistente
else:
    # En desarrollo local
    db_path = os.path.join(directorio_base, "palabras.db")  # Ruta local
```

### Inicialización automática de tablas

Las tablas de la base de datos se crean automáticamente al iniciar la aplicación:

```python
with app.app_context():
    db.create_all()  # Crea las tablas si no existen
```

### Protección de datos y normalización

- **Normalización de texto**: La aplicación normaliza automáticamente las palabras ingresadas, manteniendo caracteres especiales como la 'ñ' y eliminando tildes para mejores resultados.

- **Validación de entradas**: Verifica automáticamente que las palabras contengan solo caracteres válidos, mostrando mensajes de error apropiados.

- **Prevención de duplicados**: Evita automáticamente la duplicación de entradas en la base de datos.

### Gestión de sesiones adaptativa

La configuración de sesiones se ajusta automáticamente según el entorno:

```python
if env == "PRODUCTION":
    # Configuración para producción
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True
else:
    # Configuración para desarrollo/local
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
```

### Sistema de feedback con respaldo

El sistema de feedback intenta primero enviar por correo electrónico, pero si falla (por ejemplo, si no hay configuración SMTP), automáticamente guarda el feedback en la base de datos como respaldo.

### Historial de búsquedas inteligente

- **Almacenamiento de historial**: La aplicación guarda automáticamente las búsquedas en la sesión del usuario.
- **Normalización inteligente**: Detecta y normaliza diferentes formatos de datos para mayor compatibilidad.
- **Ranking automático**: Ordena las entradas según su popularidad.

## 🔧 Requisitos previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Acceso a la línea de comandos

## ⚙️ Instalación simplificada

Gracias a las características automáticas de la aplicación, la instalación es extremadamente sencilla:

### 1. Clonar el repositorio

```bash
git clone https://github.com/jaosomora/LGC-App.git
cd LGC-App
```

### 2. Configurar un entorno virtual (recomendado)

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

### 3. Ejecutar la aplicación

```bash
python app.py
```

¡Y eso es todo! La aplicación:

1. Verificará e instalará automáticamente las dependencias necesarias
2. Creará la base de datos SQLite en la ubicación adecuada
3. Inicializará todas las tablas requeridas
4. Iniciará el servidor en http://127.0.0.1:8080

### Configuración opcional

Si deseas personalizar la aplicación, puedes crear un archivo `.env` con las variables descritas en la sección de [Variables de Entorno](#-variables-de-entorno), pero esto no es necesario para el funcionamiento básico.

## 🌐 Variables de Entorno

La aplicación está diseñada para funcionar con configuración automática, adaptándose al entorno donde se ejecuta sin necesidad de ajustes manuales excesivos. Sin embargo, puedes personalizar ciertos aspectos mediante variables de entorno.

### Configuración automática

Interfaz LGC incluye las siguientes características automáticas:

- **Detección de entorno**: La aplicación detecta automáticamente si está ejecutándose en desarrollo local o en Render
- **Instalación de dependencias**: Verifica e instala automáticamente las dependencias necesarias si faltan
- **Creación de base de datos**: Genera y configura la base de datos SQLite en la ubicación adecuada según el entorno
- **Inicialización de tablas**: Crea todas las tablas necesarias al iniciar la aplicación

### Variables de entorno disponibles

#### Básicas (opcionales)

```env
# Define el entorno de ejecución (LOCAL, DEVELOPMENT, PRODUCTION)
# Por defecto: "LOCAL" si no se especifica
ENV=PRODUCTION

# Clave secreta para las sesiones de Flask
# Por defecto: Se usa una clave predeterminada
SECRET_KEY=tu-clave-secreta-personalizada

# Credenciales de acceso al panel de administración
ADMIN_USER=tu_nombre_de_usuario
ADMIN_PASSWORD=tu_contraseña_segura
```

#### Para el sistema de feedback por correo (opcionales)

```env
# Configuración del servidor SMTP para enviar feedback por correo
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-correo@gmail.com
SMTP_PASSWORD=tu-contraseña-de-aplicacion

# Nota: Si no se configuran, el feedback se guardará automáticamente en la base de datos
```

#### Para el sistema de analytics (opcionales)

```env
# Habilitar analytics incluso en entorno de desarrollo
ENABLE_ANALYTICS=1

# ID de Google Analytics (si no se configura, se usa uno predeterminado)
ANALYTICS_ID=G-XXXXXXXXXXXX
```

### Configuración automática según el entorno

1. **En entorno local**:
   - Base de datos: Se crea en `./palabras.db` (directorio actual)
   - Configuración de sesiones: Se usa SameSite=Lax y conexiones no seguras
   - Debug: Mensajes detallados en la consola
   - Panel de estadísticas: Accesible sin autenticación

2. **En Render (producción)**:
   - Base de datos: Se crea en `/mnt/data/palabras.db` (ubicación persistente)
   - Configuración de sesiones: Se usa SameSite=None y conexiones seguras
   - CORS: Configurado para permitir conexiones desde dominios específicos
   - Panel de estadísticas: Protegido con autenticación básica (requiere ADMIN_USER y ADMIN_PASSWORD)

### Cómo configurar variables en diferentes entornos

#### Desarrollo local

Para desarrollo local, puedes crear un archivo `.env` en la raíz del proyecto:

```env
ENV=DEVELOPMENT
SECRET_KEY=tu-clave-secreta
ADMIN_USER=admin
ADMIN_PASSWORD=password
```

**Nota**: No es necesario crear este archivo para que la aplicación funcione, ya que usa valores predeterminados seguros.

#### En Render

En Render, ve a la sección "Environment" de tu servicio web y añade las variables necesarias:

![Configuración de variables de entorno en Render](https://www.julianosoriom.com/wp-content/uploads/2023/11/render-env-config.png)

Los valores mínimos recomendados son:
- `ENV=PRODUCTION`
- `SECRET_KEY=tu-clave-secreta-personalizada` (opcional pero recomendado)
- `ADMIN_USER=tu_nombre_de_usuario` (requerido para acceder al panel de estadísticas)
- `ADMIN_PASSWORD=tu_contraseña_segura` (requerido para acceder al panel de estadísticas)

## 📊 Acceso al Panel de Estadísticas

Interfaz LGC incluye un panel de estadísticas que muestra métricas de uso detalladas complementarias a Google Analytics.

### Acceso en entorno de desarrollo

En entorno de desarrollo o local, puedes acceder al panel simplemente visitando:

```
http://localhost:8080/admin/stats
```

### Acceso en entorno de producción

En producción, el panel está protegido con autenticación básica. Para acceder:

1. Configura las variables de entorno `ADMIN_USER` y `ADMIN_PASSWORD` en tu servidor Render
2. Visita la URL:

```
https://tu-dominio.com/admin/stats
```

3. Introduce las credenciales cuando el navegador las solicite

### Características del panel

- **Eventos específicos**: Muestra eventos particulares de la aplicación
- **Métricas básicas**: Vistas de página, sesiones únicas y vistas por sesión
- **Distribución de usuarios**: Estadísticas por dispositivo, sistema operativo y navegador
- **Botón de actualización**: Permite refrescar los datos sin recargar la página completa
- **Enlace a Google Analytics**: Acceso rápido a estadísticas más detalladas

## 🚀 Despliegue en Render

### 1. Crear una cuenta en Render

Regístrate en [Render](https://render.com) si aún no tienes una cuenta.

### 2. Crear un nuevo servicio web

1. Haz clic en "New" y selecciona "Web Service"
2. Conecta con tu repositorio de GitHub donde has subido el código
3. Configura el servicio:
   - **Name**: Elige un nombre para tu servicio (ej. lgc-app)
   - **Region**: Selecciona la región más cercana a tus usuarios
   - **Branch**: `main` (o la rama que uses como principal)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: Free (o el plan que prefieras)

### 3. Configurar variables de entorno en Render

En la sección "Environment" de tu servicio, añade las siguientes variables:

```
ENV=PRODUCTION
SECRET_KEY=clave-secreta-personalizada
ADMIN_USER=tu_nombre_de_usuario
ADMIN_PASSWORD=tu_contraseña_segura

# Para funcionalidad de feedback por correo (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-correo@gmail.com
SMTP_PASSWORD=tu-contraseña-de-aplicacion-gmail
```

### 4. Desplegar el servicio

Haz clic en "Create Web Service" y espera a que se complete el despliegue. Render te proporcionará una URL donde podrás acceder a tu aplicación.

## 📦 Estructura del proyecto

```
LGC-App/
├── app.py                     # Aplicación principal Flask
├── wsgi.py                    # Punto de entrada para servidores WSGI
├── init_db.py                 # Script de inicialización de base de datos
├── requirements.txt           # Dependencias del proyecto
├── palabras.db                # Base de datos SQLite (generada localmente)
├── tabla_periodica.json       # Datos de elementos químicos
├── territorios.json           # Datos de códigos territoriales
├── static/                    # Archivos estáticos
│   ├── css/                   # Hojas de estilo
│   │   └── output.css         # CSS compilado (Tailwind)
│   └── js/                    # Scripts JavaScript
│       └── feedback.js        # Funcionalidad del formulario de feedback
├── templates/                 # Plantillas HTML
│   ├── base.html              # Plantilla base
│   ├── components/            # Componentes reutilizables
│   │   ├── search_modal.html  # Modal de búsqueda
│   │   └── feedback_modal.html # Modal de feedback
│   ├── menu.html              # Página principal
│   ├── opcion1.html           # Búsqueda por frecuencia
│   ├── opcion2.html           # Análisis de palabras
│   ├── resultado.html         # Página de resultados
│   └── embed.html             # Para integración externa
├── blueprints/                # Módulos Blueprint de Flask
│   ├── __init__.py
│   ├── feedback_blueprint.py  # Funcionalidad para feedback
│   └── analytics_blueprint.py # Funcionalidad para análisis y estadísticas
├── tailwind.config.js         # Configuración de Tailwind CSS
└── README.md                  # Este archivo
```

## 💾 Base de datos

La aplicación utiliza SQLite como base de datos local que almacena:

- **Palabras procesadas**: Todas las palabras y frases analizadas
- **Ranking**: Estadísticas de uso y búsqueda
- **Feedback**: Comentarios y sugerencias de los usuarios (si se usa el método de almacenamiento en DB)
- **Analytics**: Datos de uso y eventos específicos de la aplicación

### Ubicación de la base de datos:
- **Desarrollo local**: `./palabras.db` (en el directorio del proyecto)
- **Render (producción)**: `/mnt/data/palabras.db` (ruta persistente)

## 📋 Funcionalidades principales

### 1. Cálculo de frecuencia lógica
Ingresa un número y descubre palabras cuyo valor numérico coincida con ese número.

### 2. Análisis de potencial
Ingresa una palabra o frase para calcular su valor numérico y descubrir sus relaciones con otros conceptos.

### 3. Comparación de palabras
Compara dos palabras diferentes para analizar su suma y diferencia numérica, descubriendo palabras relacionadas matemáticamente.

### 4. Sistema de feedback
Envía comentarios, sugerencias o reporta problemas directamente desde la aplicación.

### 5. Analytics y estadísticas
Seguimiento detallado del uso de la aplicación con panel administrativo protegido.

## ⚠️ Solución de problemas comunes

### La aplicación no arranca
- Verifica que hayas activado el entorno virtual
- Confirma que todas las dependencias están instaladas correctamente: `pip install -r requirements.txt`
- Comprueba si algún otro servicio está usando el puerto 8080

### Error al enviar feedback
- Verifica las credenciales SMTP en las variables de entorno
- Si usas Gmail, asegúrate de haber generado una "Contraseña de aplicación" específica
- Como alternativa, el feedback siempre se guarda en la base de datos local

### No puedo acceder al panel de estadísticas
- En entorno de desarrollo, verifica que la URL sea correcta: `/admin/stats`
- En producción, asegúrate de haber configurado correctamente `ADMIN_USER` y `ADMIN_PASSWORD`
- Comprueba los logs del servidor para ver si hay errores de autenticación

### Problemas en Render
- Revisa los logs del servicio en el dashboard de Render
- Verifica que todas las variables de entorno estén configuradas correctamente
- Asegúrate de que el servicio tiene suficientes recursos asignados

## 🤝 Contribuir al proyecto

Si deseas contribuir a este proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad: `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m "Añadir nueva funcionalidad"`
4. Sube los cambios a tu fork: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request al repositorio original

## 📄 Licencia

Este proyecto está bajo licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 📱 Contacto y soporte

- **Web**: [https://julianosoriom.com](https://julianosoriom.com)
- **Email**: [info@julianosoriom.com](mailto:info@julianosoriom.com)
- **Newsletter**: [Suscríbete para recibir actualizaciones](https://www.julianosoriom.com/newsletter-lgc)
- **Apoyar el proyecto**: [Ko-fi](https://ko-fi.com/julianosoriom)

---

Desarrollado con 🚀 por [Julián Osorio Mora](https://www.instagram.com/julianosoriomora/)