# CHANGELOG

## [1.2.7] - 2025-01-14
### Added
- Inclusión de la funcionalidad para mostrar las palabras o frases en **negrita** en el análisis de resultados.
- Nueva lógica en el backend para diferenciar correctamente entre palabras únicas y frases al formatear los resultados:
  - Se elimina el "= suma" redundante en palabras únicas.
  - Para frases, se mantiene el detalle completo, incluyendo la suma total.
- Ajuste en el título dinámico del análisis:
  - Actualizado a "Métricas de 'Palabra o Frase'" con formato capitalizado, simplificando la presentación.
- Personalización del encabezado "Relación Numérica con Palabras":
  - Cambiado a "Palabras con la misma Frecuencia Numérica" para mayor claridad.
- Inclusión de comentarios explicativos en el código fuente (`resultado.html`) para facilitar la comprensión por parte de otros desarrolladores.

### Changed
- Refinamiento en la visualización de resultados:
  - Para palabras únicas, se eliminó el `= suma` redundante en la línea de detalle.
  - Mejoras en la consistencia visual y legibilidad de los resultados en todas las secciones.

---

## [1.2.6] - 2025-01-12
### Added
- Integración del botón flotante de Ko-fi para donaciones en todas las páginas.
  - Botón configurado para desplegarse como un "floating chat" con un diseño minimalista y llamativo.
  - Colores personalizados adaptados a la paleta del proyecto.
- Mejora de la experiencia de usuario con un acceso claro para apoyar al desarrollador.

### Changed
- Ajustes menores en el diseño para garantizar la correcta visualización del botón Ko-fi en dispositivos móviles y de escritorio.

---

## [1.2.5] - 2025-01-11
### Added
- Implementación de una calculadora visual interactiva en la página de resultados.
- Animación CSS de "latido" (`pulse`) para los números resaltados en la calculadora, mejorando la experiencia visual.
- Ajustes dinámicos en la lógica de resaltar números para admitir listas de dígitos (`numero_resaltado`).

### Fixed
- Lógica para calcular y resaltar números en la calculadora, evitando errores al interpretar `numero_resaltado`.

---

## [1.2.4] - 2025-01-09
### Added
- Implementación de un modal interactivo con efecto de desenfoque (`blur`) en el fondo, utilizando Tailwind CSS, para una experiencia más inmersiva en la selección de opciones del menú principal.
- Validaciones dinámicas en el modal:
  - Para la opción "Ingresa número", permite únicamente números y activa automáticamente el teclado numérico en dispositivos móviles.
  - Para la opción "Ingresa palabra o frase", valida que solo se ingresen letras y espacios. Si se ingresan caracteres no válidos, se muestra un mensaje de error y el fondo del input cambia a rojo.
- Optimización del diseño visual del modal:
  - Botones "Confirmar" y "Cancelar" con estilos modernos y animaciones de transición.
  - Texto del placeholder dinámico según la opción seleccionada.
- Nueva funcionalidad en el encabezado del menú principal:
  - Texto dinámico y estilizado utilizando la clase `mark` de Tailwind CSS para resaltar palabras clave, mejorando la apariencia visual.

### Fixed
- Corrección de validaciones en el modal para evitar errores de entrada al enviar formularios:
  - Se evita el envío si los datos ingresados no cumplen con las reglas específicas de cada opción.
- Solucionado un problema que permitía ingresar números en la opción "Ingresa palabra o frase", ahora gestionado en tiempo real con cambios visuales inmediatos.

---

## [1.2.3] - 2025-01-08
### Added
- Implementación de la funcionalidad para mostrar "Número por letra" solo cuando se ingresan frases con más de una palabra en la opción `resultado_opcion2`.
- El encabezado dinámico en la opción 2 ahora utiliza la frase buscada como título para los "Números por letra".
- Nueva lógica en el controlador para manejar entradas con múltiples palabras, pasando una bandera (`mostrar_numeros_por_letra`) al template para controlar la visualización.

### Fixed
- Ajustes en la plantilla `resultado.html` para mantener consistencia visual y no mostrar "Número por letra" en entradas con una sola palabra.
- Verificación adicional para evitar duplicados en las entradas del historial.

---

## [1.2.2] - 2025-01-08
### Added
- Inclusión de todos los países reconocidos por la ONU y territorios adicionales en el archivo `territorios_final.json`, asegurando que cada país tenga su respectivo código telefónico internacional.
- Reformateo del archivo `territorios_final.json` para cumplir con el estándar compacto solicitado.

### Fixed
- Corrección de códigos ausentes en los países faltantes para una representación precisa de los datos.

---

## [1.2.1] - 2025-01-03
### Fixed
- Resolución del problema con el cálculo incorrecto de la frecuencia de la letra `ñ` en la función `calcular_frecuencia_por_palabra`.
- Ajuste en la normalización de palabras para preservar correctamente la `ñ` y evitar errores al calcular sus frecuencias.
- Corrección de valores cero en las frecuencias por palabra relacionadas con normalización de letras y mapeo en el diccionario `valores_letras`.

### Added
- Nuevos comentarios en el código para mejorar la comprensión de la lógica en `calcular_frecuencia_por_palabra`.

---

## [1.2.0] - 2025-01-02
### Added
- Migración completa a Tailwind CSS para un diseño más moderno y consistente.
- Nuevas configuraciones en `tailwind.config.js` para colores personalizados (`primary`, `secondary`, `accent`, `light`) y fuentes (`Poppins`, `Roboto`).
- Mejora de responsividad en todas las plantillas (`base.html`, `menu.html`, `resultado.html`, `historial.html`).
- Elementos de diseño optimizados para dispositivos móviles.

### Removed
- `styles.css` eliminado tras completar la transición a Tailwind CSS.

### Fixed
- Ajuste de layouts para evitar solapamientos y mejorar la visualización de "Historial de Búsquedas".
- Resolución de problemas relacionados con el renderizado inconsistente de cajas en dispositivos móviles.

---

## [1.1.0] - 2024-12-31
### Added
- `init_db.py` para inicialización automática de la base de datos.
- `wsgi.py` para compatibilidad con gunicorn.
- Validación de caracteres en palabras ingresadas.
- Configuración dinámica de base de datos según entorno.

### Fixed
- Correcciones en el manejo de sesiones.
- Eliminación de errores relacionados con tablas SQLite.

---

## [1.0.0] - 2024-12-15
- Primera versión estable.