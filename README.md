# LGC-App

## Descripción General

LGC-App es una aplicación web interactiva desarrollada con Flask que permite realizar análisis semánticos avanzados, gestionar información territorial y explorar datos químicos de la tabla periódica. La aplicación está diseñada para ser altamente modular y fácil de integrar, ofreciendo una experiencia de usuario fluida y profesional.

## Características

- **Análisis semántico avanzado**: Calcula el "potencial" de palabras y frases basándose en frecuencias lógicas.
- **Gestión de territorios**: Proporciona información detallada sobre códigos de país y territorios asociados.
- **Exploración química**: Consulta datos clave sobre elementos químicos de la tabla periódica.
- **Interfaz profesional**: Optimizada para una experiencia de usuario limpia y eficiente, eliminando elementos visuales innecesarios como el Hero y barras redundantes.
- **Compatibilidad para despliegue**: Diseñada para integrarse fácilmente con servicios como Render y otras plataformas de hosting.

## Requisitos Previos

- **Python 3.8 o superior**
- Administrador de paquetes `pip`
- Cuenta en [Render](https://render.com) para despliegue (opcional)

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
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=tu_clave_secreta
   REDIS_HOST=redis://localhost:6379
   ```

5. **Inicia la aplicación:**
   ```bash
   flask run
   ```

6. **Accede a la interfaz web:**
   Abre tu navegador y visita [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Despliegue en Render

1. **Sube el proyecto a GitHub:**
   Asegúrate de tener el proyecto actualizado en un repositorio público o privado en GitHub.

2. **Configura el servicio en Render:**
   - Ve a [Render](https://render.com) y crea un nuevo servicio web.
   - Selecciona tu repositorio y configura los siguientes valores:
     - **Branch**: `main` (o la rama correspondiente).
     - **Build Command**: `pip install -r requirements.txt`.
     - **Start Command**: `gunicorn app:app`.

3. **Configura Redis en Render:**
   - Ve a la sección **Add a New Database** en Render y selecciona Redis.
   - Toma nota de la URL proporcionada y configúrala como variable de entorno:
     ```env
     REDIS_HOST=<URL de tu Redis en Render>
     ```

4. **Despliegue automático:**
   Render generará una URL pública para tu aplicación (por ejemplo: `https://lgc-app.onrender.com`).

## Incrustación en Systeme.io

Para incrustar tu aplicación en Systeme.io con un timestamp dinámico:

```html
<div style="width: 100%; height: 100vh; overflow: hidden;">
    <iframe 
        id="dynamicIframe"
        style="width: 100%; height: 100%; border: none;" 
        allowfullscreen>
    </iframe>
</div>

<script>
    // Genera un timestamp dinámico
    const timestamp = new Date().getTime();
    // Construye la URL con el parámetro nocache
    const iframe = document.getElementById('dynamicIframe');
    iframe.src = `https://lgc-app.onrender.com/?nocache=${timestamp}`;
</script>
```

## Estructura del Proyecto

```plaintext
proyecto/
├── app.py                 # Archivo principal de la aplicación Flask
├── requirements.txt       # Dependencias del proyecto
├── ranking.txt            # Datos de términos y puntuaciones
├── palabras.txt           # Archivo de palabras y frases clave
├── tabla_periodica.json   # Datos JSON de la tabla periódica
├── territorios.json       # Datos JSON de territorios y códigos
├── static/                # Archivos estáticos
│   └── styles.css         # Hojas de estilo
├── templates/             # Plantillas HTML
│   ├── base.html          # Plantilla base (modificada: Hero y barras eliminadas)
│   ├── menu.html          # Menú principal
│   ├── opcion1.html       # Opción 1
│   ├── opcion2.html       # Opción 2
│   ├── resultado.html     # Resultados
│   ├── embed.html         # Página para incrustación con timestamp dinámico
│   └── test.html          # Página de prueba
```

## Cambios Recientes

- **Nueva ruta `/embed_page`:** Permite renderizar un iframe con timestamp dinámico para evitar problemas de caché.
- **Sesiones persistentes con Redis:** Configuración añadida para manejar sesiones robustas en producción.
- **Incrustación optimizada:** Ejemplo implementado para Systeme.io.

## Contribuciones

¡Las contribuciones son bienvenidas! Si deseas colaborar, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tu función o corrección:
   ```bash
   git checkout -b nombre-de-tu-rama
   ```
3. Realiza tus cambios y realiza un commit claro:
   ```bash
   git commit -m "Descripción de los cambios realizados"
   ```
4. Sube tus cambios a tu fork:
   ```bash
   git push origin nombre-de-tu-rama
   ```
5. Abre un Pull Request en el repositorio principal.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Soporte

Si tienes dudas o problemas, no dudes en abrir un issue en el repositorio o contactarme directamente en [info@julianosoriom.com](mailto:info@julianosoriom.com).
