# LGC-App

## Descripción General

Este proyecto es una aplicación web desarrollada con Flask que permite analizar datos semánticos, gestionar territorios internacionales, y explorar información química básica de la tabla periódica. Su diseño modular y su enfoque en datos JSON lo hacen ideal para aplicaciones educativas, analíticas o interactivas.

## Características

- **Análisis semántico**: Procesa palabras y frases clave para su evaluación.
- **Gestión de territorios**: Proporciona información detallada sobre países y códigos internacionales.
- **Exploración química**: Consulta datos básicos sobre elementos de la tabla periódica.
- **Interfaz web interactiva**: Diseñada con Flask para una experiencia de usuario accesible.

## Requisitos Previos

- **Python 3.8 o superior**
- Administrador de paquetes `pip`

## Instalación

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
   Asegúrate de establecer la clave secreta para Flask en un archivo `.env` o directamente en el entorno:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

## Uso

1. **Inicia la aplicación:**
   ```bash
   flask run
   ```

2. **Accede a la interfaz web:**
   Abre tu navegador y ve a [http://127.0.0.1:5000](http://127.0.0.1:5000).

3. **Explora las funcionalidades:**
   - **Análisis de palabras:** Carga archivos personalizados para procesar términos.
   - **Información territorial:** Consulta códigos de país y sus nombres asociados.
   - **Tabla periódica:** Accede a datos detallados sobre elementos químicos.

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
│   ├── base.html          # Plantilla base
│   ├── menu.html          # Menú principal
│   ├── opcion1.html       # Opción 1
│   ├── opcion2.html       # Opción 2
│   ├── resultado.html     # Resultados
│   └── test.html          # Página de prueba
```

## Contribuciones

¡Contribuciones son bienvenidas! Por favor, abre un issue o envía un pull request con tus sugerencias.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Soporte

Si tienes dudas o problemas, no dudes en abrir un issue en el repositorio o contactarme directamente en [info@julianosoriom.com](mailto:info@julianosoriom.com).