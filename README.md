# LGC-App

## Descripción General

LGC-App es una aplicación web interactiva desarrollada con **Flask** que permite realizar análisis semánticos avanzados, gestionar información territorial y explorar datos químicos de la tabla periódica. Diseñada para ser modular y fácilmente desplegable, la aplicación ofrece una experiencia profesional y optimizada.

### Características principales:

- **Análisis semántico avanzado**: Calcula el "potencial" de palabras y frases basándose en frecuencias.
- **Gestión de territorios**: Proporciona información detallada sobre códigos de país y territorios asociados.
- **Exploración química**: Consulta datos clave sobre elementos químicos de la tabla periódica.
- **Validación de entradas**: Verifica que las palabras ingresadas contengan solo caracteres válidos (alfabéticos y espacios).
- **Compatibilidad para despliegue**: Diseñada para integrarse con plataformas como Render, soportando configuraciones automáticas para entornos local y de producción.

---

## Requisitos Previos

- **Python 3.8 o superior**
- Administrador de paquetes `pip`
- Cuenta en [Render](https://render.com) para despliegue (opcional)

---

## Instalación Local

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/usuario/proyecto.git
   cd proyecto
   ```

2. **Crea un entorno virtual:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   Crea un archivo `.env` en el directorio raíz con el siguiente contenido:

   ```env
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   SECRET_KEY=tu_clave_secreta
   ENV=DEVELOPMENT
   ```

5. **Inicializa la base de datos:**
   Ejecuta el script de inicialización:

   ```bash
   python init_db.py
   ```

6. **Inicia la aplicación:**

   ```bash
   flask run
   ```

7. **Accede a la interfaz web:**
   Abre tu navegador y visita [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Base de Datos: **SQLite**

### Descripción:

La aplicación utiliza **SQLite** para almacenar las palabras y datos ingresados.

- **Tabla `palabra`**: Almacena palabras únicas ingresadas por los usuarios.
- **Tabla `ranking`**: Almacena las palabras junto con su puntuación basada en el potencial calculado.

### Inicialización Automática:

1. El archivo `init_db.py` se encarga de verificar y crear las tablas necesarias durante el despliegue o en la ejecución local.

   ```bash
   python init_db.py
   ```

2. Durante el despliegue en Render, el comando de inicio incluye este script de forma automática.

### Configuración Automática por Entorno:

- **Producción en Render:**
  La base de datos utiliza una ruta persistente en `/mnt/data/palabras.db`.
- **Desarrollo Local:**
  La base de datos utiliza la ruta `./palabras.db` en el directorio del proyecto.

Esto asegura compatibilidad y configuración sin necesidad de ajustes manuales.

---

## Validación de Entradas

Las palabras ingresadas son validadas para garantizar que contengan solo caracteres alfabéticos y espacios. Si se detectan caracteres no válidos, se muestra un mensaje de error amigable al usuario sin procesar la solicitud.

### Ejemplo de error mostrado:

"La palabra contiene caracteres no válidos. Por favor, ingrese solo letras y espacios."

---

## Despliegue en Render

1. **Sube el proyecto a GitHub:**
   Asegúrate de tener el proyecto actualizado en un repositorio.

2. **Configura el servicio en Render:**

   - Ve a [Render](https://render.com) y crea un nuevo servicio web.
   - Selecciona tu repositorio y configura los siguientes valores:
     - **Branch:** `develop` o `main` según el entorno.
     - **Build Command:** `pip install -r requirements.txt`.
     - **Start Command:** `gunicorn wsgi:app`.

3. **Configura las variables de entorno en Render:**

   - Agrega las siguientes variables:
     ```env
     FLASK_ENV=production
     SECRET_KEY=tu_clave_secreta
     ENV=PRODUCTION
     ```

4. **Despliegue:**
   Una vez configurado, Render generará una URL pública para tu aplicación.

---

## Nuevos Archivos

- **`init_db.py`**: Script para inicializar y verificar la base de datos.
- **`wsgi.py`**: Archivo de entrada para Gunicorn.

---

## Estructura del Proyecto

```plaintext
proyecto/
├── app.py                 # Lógica principal de la aplicación Flask
├── init_db.py             # Script para inicializar la base de datos
├── wsgi.py                # Archivo de entrada para Gunicorn
├── requirements.txt       # Dependencias del proyecto
├── palabras.db            # Base de datos SQLite
├── tabla_periodica.json   # Datos JSON de la tabla periódica
├── territorios.json       # Datos JSON de territorios
├── static/                # Archivos estáticos
├── templates/             # Plantillas HTML
│   ├── base.html          # Plantilla base
│   ├── menu.html          # Menú principal
│   ├── opcion1.html       # Opción 1
│   ├── opcion2.html       # Opción 2
│   ├── resultado.html     # Resultados
│   └── embed.html         # Para incrustación con timestamp
```

---

## Cambios Recientes

- **Validación de entradas:**
  La aplicación ahora valida caracteres en las palabras ingresadas.
- **Inicialización de base de datos:**
  Automatizada para entornos local y de producción.
- **Script `init_db.py`:**
  Nuevo archivo para garantizar que las tablas de la base de datos estén creadas antes del inicio del servidor.
- **Archivo `wsgi.py`:**
  Añadido para manejar Gunicorn en despliegues de producción.

---

## Guía de Contribución

1. **Haz un fork del repositorio.**
2. **Crea una rama para tus cambios:**
   ```bash
   git checkout -b mi-funcion
   ```
3. **Realiza tus cambios y un commit claro:**
   ```bash
   git commit -m "Descripción clara del cambio"
   ```
4. **Envía tus cambios al repositorio remoto:**
   ```bash
   git push origin mi-funcion
   ```
5. **Abre un Pull Request.**

---

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## Soporte

Si tienes dudas o problemas, abre un **issue** en el repositorio o contacta a [info@julianosoriom.com](mailto:info@julianosoriom.com).