# CHANGELOG


## [2.0.1] - 2026-03-10
### Mejorado
- **Comparar — Labels**: Labels actualizados a "Primera palabra o frase" / "Segunda palabra o frase" con placeholder "Escribe aquí..." consistente con Conversor.
- **Comparar — Paneles**: Los paneles "Palabras Relacionadas" y "Total Invertido" ahora se llenan correctamente usando el total (suma) en modo Comparar.
- **Orden por frecuencia**: Las palabras relacionadas e invertidas se ordenan de más buscada a menos buscada (por ranking), tanto en Conversor como en Comparar.

### Corregido
- **Exclusión en Comparar**: Corregido bug donde las palabras buscadas no se excluían de sus propios resultados en modo Comparar (el backend ahora parsea múltiples términos separados por coma).

---

## [2.0.0] - 2026-03-09
### Reescritura completa
- **Arquitectura SPA**: Aplicación reconstruida como Single Page Application con vanilla JS (IIFE), eliminando navegación multi-página.
- **Nuevo sistema de diseño**: Glass morphism con modo oscuro/claro, acento naranja, orbes animados de fondo y tipografía Inter.
- **CSS Custom Properties**: Variables de tema con valores RGB separados para compatibilidad con opacidad de Tailwind.

### Nuevas funcionalidades
- **Conversor inteligente**: Fusión de Conversor y Buscador en un solo input con detección automática texto/número vía regex (`/^\d+$/`).
- **Modo Comparar**: Renombrado de "Calculadora" a "Comparar" para mayor claridad. Permite comparar dos palabras con suma y resta.
- **Suma y Resta en Conversor**: Para frases multi-palabra, muestra automáticamente suma y resta de los potenciales.
- **Chips de letras**: Desglose visual con chips individuales (letra en color suave + número en naranja) en lugar de texto plano.
- **Mapa interactivo**: Mapa de letras (A=1 ... Z=27) con resaltado dinámico de letras activas y auto-expansión en modo texto.
- **Calculadora visual**: Grid 0-9 con resaltado de dígitos del resultado.
- **Limpiar historial**: Botón dentro de Historial y Ranking para borrar el historial local.
- **Auto-guardado**: Guardado automático a los 2 segundos sin botón manual.

### Mejoras de UX
- **Compartir rediseñado**: Modal con botón WhatsApp (naranja + ícono) y Copiar resultado (solo texto+resultado+lupa, sin URL). Auto-cierra tras copiar con confirmación toast.
- **Botón Compartir naranja**: Estilo primario consistente con la identidad visual.
- **Footer sticky**: Siempre visible al fondo con flexbox.
- **Ranking con badges**: Números completos con badge naranja en lugar de posiciones.
- **Ortografía correcta**: Tildes en todos los textos estáticos (lógico, búsqueda, número, Julián, etc.).
- **Novedades**: Enlace actualizado al canal de Telegram.

### Eliminado
- Modelo y endpoint de Feedback.
- Resonancia Geográfica y Resonancia Elemental.
- Modo Buscador separado (fusionado en Conversor).
- Botón "Guardar búsqueda" (reemplazado por auto-guardado).
- Argentinismos en textos ("Escribí" → "Escribe").

---

## [1.3.19] - 2025-03-21
### Cambiado
- **Interfaz de Usuario**:
  - Cambiada la nomenclatura de "Frecuencia" a "Número" en toda la aplicación
  - Actualizado el procesamiento del historial para manejar ambos términos
  - Mejorada la consistencia visual de la interfaz con la nueva terminología

### Corregido
- **Historial de Búsquedas**:
  - Solucionado problema donde entradas con "Número:" no aparecían correctamente en el historial
  - Implementada compatibilidad con entradas antiguas que usaban "Frecuencia:"
  - Optimizado el sistema de enlaces en el historial para mantener funcionalidad con ambos formatos


## [1.3.18] - 2025-03-21
### Corregido
- **Historial de Búsquedas**:
  - Resuelto problema de duplicación de entradas en el historial
  - Implementada normalización unificada para prevenir duplicados con variaciones de acentos
  - Mejorado el seguimiento de búsquedas únicas en todas las opciones

### Optimizado
- **Sistema de Historial**:
  - Refinado el proceso de extracción y comparación de palabras
  - Agregado conjunto de seguimiento para eliminar entradas repetidas
  - Mantenida la estructura original de los datos de historial

## [1.3.17] - 2025-03-20
### Corregido
- **Normalización de Palabras**:
  - Solucionado bug donde las palabras con/sin acentos (ej. "acción"/"accion") aparecían duplicadas en los resultados.
  - Mejorada la comparación de palabras utilizando normalización consistente en todas las funciones.
  - Actualizado el algoritmo de filtrado para reconocer variantes de palabras con tilde como equivalentes.

### Optimizado
- **Sistema de Búsqueda**:
  - Refinado el proceso de normalización de palabras para comparaciones más precisas.
  - Implementada normalización uniforme en las tres rutas de búsqueda (opciones 1, 2 y 3).
  - Mejorado el filtrado de resultados para eliminar falsos positivos debido a la normalización.


## [1.3.16] - 2025-03-20
### Corregido
- **Funcionalidad de Palabras Invertidas**:
  - Solucionado bug donde no se mostraban las "Palabras desde el Futuro" cuando se buscaba directamente un número.
  - Añadida búsqueda de palabras con valor invertido en la función `resultado_opcion1`.
  - Implementado paso de valores invertidos al template para visualización correcta.

### Mejorado
- **Renderizado de Resultados**:
  - Actualizada la plantilla para mostrar consistentemente las palabras relacionadas, tanto con valor directo como invertido.
  - Optimizado el renderizado para mantener consistencia en ambas rutas de búsqueda.


## [1.3.15] - 2025-03-19
### Mejorado
- **Sistema de Analítica y Seguridad**:
  - Implementada autenticación básica HTTP para proteger el panel de estadísticas.
  - Creado nuevo endpoint específico para eventos personalizados de la aplicación.
  - Separada la captura de eventos específicos del flujo general de analytics.
  - Mejorada la visualización de eventos específicos de la aplicación en el panel administrativo.

### Optimizado
- **Panel de Estadísticas**:
  - Rediseñado el panel de estadísticas para mostrar primero los eventos específicos.
  - Añadido botón de actualización manual para refrescar datos sin recargar toda la página.
  - Integrado enlace directo a Google Analytics para análisis más detallados.
  - Mejorada la visualización de datos para facilitar la interpretación.

### Seguridad
- **Gestión de Credenciales**:
  - Migradas credenciales de acceso administrativo a variables de entorno.
  - Eliminadas contraseñas hardcodeadas para mayor seguridad.
  - Implementada verificación de entorno para facilitar el desarrollo local.


## [1.3.14] - 2025-03-18
### Añadido
- **Sistema de Analítica y Seguimiento**:
  - Implementado Google Analytics con consentimiento de cookies.
  - Añadido banner de cookies para cumplimiento de normativas.
  - Creado sistema de seguimiento local para análisis detallado.
  - Desarrollado panel administrativo de estadísticas.
  - Añadido seguimiento de dispositivos, sistemas operativos y navegadores.
  - Implementada funcionalidad para medir uso de características específicas.

### Mejorado
- **Estructura Modular**:
  - Creado blueprint `analytics_blueprint.py` para centralizar la funcionalidad de analítica.
  - Implementado sistema de logging específico para estadísticas.
  - Optimizada la recopilación de datos para minimizar el impacto en rendimiento.

### Optimizado
- **Rendimiento y Privacidad**:
  - Los scripts de análisis solo se cargan con consentimiento explícito.
  - Implementada carga asíncrona de Google Analytics.
  - Datos de uso almacenados de forma anónima para proteger la privacidad.
  

## [1.3.13] - 2025-03-18
### Añadido
- **Sistema de Feedback de Usuarios**:
  - Implementado botón "Enviar Feedback" en el footer.
  - Creado componente modal para recopilar feedback de usuarios.
  - Añadido sistema de respaldo para almacenar feedback en la base de datos cuando el email falla.
  - Integrado formulario de feedback en todas las páginas de la aplicación.
  - Implementada lógica para transmitir los comentarios al correo info@julianosoriom.com.

### Mejorado
- **Estructura Modular del Código**:
  - Creado directorio blueprint para organizar funcionalidades relacionadas.
  - Implementado feedback_blueprint.py para modularizar la funcionalidad de feedback.
  - Mejorada la gestión de excepciones con mensajes detallados en logs.
  - Añadido sistema de logging específico para la funcionalidad de feedback.

### Optimizado
- **Interfaz de Usuario**:
  - Reorganizado el footer para mejor equilibrio visual con la nueva funcionalidad.
  - Optimizados estilos consistentes con el sistema de diseño existente.
  - Mejorada la experiencia en dispositivos móviles.

### Documentación
- **README**:
  - Completamente reescrito para facilitar instalación y uso.
  - Añadida documentación de características automáticas y configuración.
  - Mejoradas instrucciones para despliegue local y en Render.
  - Agregada sección de solución de problemas comunes.


## [1.3.12] - 2025-03-16
### Mejorado
- **Diseño de Páginas de Resultados**:
  - Rediseñado el estilo de los títulos en las páginas de resultados.
  - Añadido resaltado con marca de color primario para palabras clave.
  - Implementada tipografía más grande y bold para mayor impacto visual.
  - Agregado soporte para modo claro y oscuro en los títulos.
  - Mejora de la responsividad del título para diferentes tamaños de pantalla.


## [1.3.11] - 2025-03-16
### Mejorado
- **Historial de búsquedas**:
  - El historial ahora muestra enlaces interactivos que permiten volver rápidamente a resultados anteriores.
  - Cambiado el título de la columna "Veces buscado" a "Cuántas veces se ha buscado" para mayor claridad.
  - Mejora en la visualización del contador de búsquedas para una experiencia más intuitiva.
  - Añadido mensaje de bienvenida para nuevos usuarios que explica la funcionalidad del historial.


## [1.3.10] - 2025-03-16
### Mejorado
- **Funcionalidad de compartir resultados**:
  - Se implementó normalización de URLs para manejar caracteres especiales y acentos.
  - Las URLs compartidas ahora funcionan correctamente para todas las opciones.
  - Mejorada la visualización del texto compartido para mantener saltos de línea.


## [1.3.9] - 2025-03-16
### Añadido
- **Nueva "Calculadora de Operaciones entre Palabras"**:
  - Se implementó una tercera opción en el menú principal que permite comparar dos palabras o frases.
  - **Ahora puedes visualizar claramente la suma y resta** de los valores numéricos entre dos palabras.
  - **Ahora puedes descubrir palabras relacionadas** con los resultados de las operaciones.
  - Se mejoró el modal de búsqueda para soportar la entrada de dos palabras simultáneamente.

### Detalles técnicos
- Extensión de la plantilla `resultado.html` para mostrar la comparación detallada.
- Implementación de lógica en el backend para procesar ambas palabras y calcular operaciones.
- Nueva ruta `/resultado_opcion3` sin afectar las funcionalidades existentes.
- Adaptación del sistema de compartir resultados para soportar el nuevo formato de comparación.

### Mejoras de interfaz
- Diseño vertical y ordenado de los resultados, optimizado para dispositivos móviles.
- Simplificación de la visualización, eliminando la calculadora numérica en la opción 3.
- Consistencia visual con las opciones existentes, manteniendo la misma experiencia de usuario.


## [1.3.8] - 2025-03-16
### Mejoras y cambios principales
- **Implementación de componentes modulares para mejorar el mantenimiento del código**:
  - Se creó un componente reutilizable `search_modal.html` que centraliza la funcionalidad del modal de búsqueda.
  - **Ahora puedes realizar nuevas búsquedas directamente desde la página de resultados** con un nuevo botón "Nueva Búsqueda" que mantiene coherencia con la opción usada inicialmente.
  - Se eliminó código duplicado de los modales en `base.html` y otras plantillas, mejorando la mantenibilidad del proyecto.

### Detalles técnicos
- Uso de macros Jinja2 para implementar componentes reutilizables.
- Exposición de funciones JavaScript globales (`showSearchModal`, `closeSearchModal`, `submitSearchInput`) para garantizar la interoperabilidad entre componentes.
- Detección automática del tipo de búsqueda previa (opción 1 o 2) para mantener consistencia en la experiencia del usuario.

---

## [1.3.7] - 2025-02-04
### Mejoras y cambios técnicos
- Se agregó configuración condicional de cookies de sesión en `app.py`:
  - En **PRODUCTION** se requiere HTTPS y se utiliza `SESSION_COOKIE_SAMESITE = "None"` para permitir iframes.
  - En **DEVELOPMENT** y entornos locales se usa `SESSION_COOKIE_SAMESITE = "Lax"` y `SESSION_COOKIE_SECURE = False`, permitiendo que el historial se almacene correctamente en HTTP.

---

## [1.3.6] - 2025-01-30
### Mejoras y cambios principales
- **Ahora puedes interactuar más fácilmente con las herramientas**:
  - Se mejoró la presentación de las **tarjetas del menú principal**, asegurando que los usuarios comprendan su propósito de manera más intuitiva.
  - **Ahora puedes notar más claramente que las tarjetas son interactivas** gracias a un efecto de **hover mejorado**, evitando que los textos cambien de color de forma inesperada.
  - Se implementó una animación **"wiggle"** en el icono de la mano **👆**, que desaparece tras la primera interacción, para guiar mejor a los usuarios en móviles.

### Mejoras en la experiencia visual
- **Ahora puedes notar que los botones son consistentes**:
  - Se unificaron los estilos de los botones **"Compartir Resultado"** y **"Volver al Menú Principal"**, asegurando que ambos tengan el mismo tamaño, bordes, colores y efectos de hover.
  - **Ahora puedes ver los botones con un diseño uniforme**, mejorando la coherencia visual en la app.

### Detalles técnicos
- Se realizaron ajustes en **tailwind.config.js** para mejorar las animaciones y transiciones, asegurando una mejor fluidez en la interfaz.
- Se corrigió el contraste de los botones y tarjetas en **hover**, evitando que los textos pierdan visibilidad al interactuar con ellos.

---

## [1.3.5] - 2025-01-30
### Mejoras y cambios principales
- **Ahora puedes navegar más fácilmente** con el nuevo diseño del **header**:
  - El **logo** con el texto **"Interfaz LGC"** ha sido destacado de manera más visual, mejorando la presencia de la marca.
  - **Ahora puedes explorar las características de la app** a través de un enlace directo titulado **"Ahora puedes"**, que te lleva a un documento de **Notion** para conocer todas las funcionalidades disponibles.
  - **Ahora puedes disfrutar de una experiencia más fluida** gracias a las transiciones suaves en los enlaces y elementos interactivos, mejorando la interacción del usuario.

### Cambios adicionales
- **Ahora puedes colaborar con el proyecto fácilmente**:
  - Un nuevo enlace en el **footer**, titulado **"¿Quieres colaborar con el proyecto?"**, con un ícono de **♥️** que te llevará a un enlace donde podrás obtener más información sobre cómo contribuir.
  - **Ahora puedes ver los créditos** con el nuevo mensaje **"Hecho 🚀 por"**, en lugar de "Hecho con ❤️ por", manteniendo un tono más dinámico y alineado con la visión del proyecto.
  
### Detalles adicionales
- **Ahora puedes sentir que todo está alineado**: El **header** y el **footer** han sido rediseñados para tener un estilo coherente con la identidad visual de la app.
- **Ahora puedes explorar mejor el contenido** del sitio con la actualización visual, brindando una experiencia de usuario más atractiva y fluida.

---

## [1.3.4] - 2025-01-30
### Mejoras y cambios principales
- **Implementación de Footer mejorado**:
  - Se implementó un nuevo diseño de Footer con tres secciones:
    - **GitHub** (izquierda).
    - **Newsletter** (centro).
    - **Créditos** (derecha).
  - Se mejoró la interactividad del ícono de **Newsletter** 📩, haciendo que cambie de color al pasar el mouse, para una experiencia más dinámica.

---

## [1.3.3] - 2025-01-29
### Mejoras y cambios principales
- **Migración completa a Tailwind CSS v3**:
  - Se actualizaron las configuraciones en `tailwind.config.js` para aprovechar las nuevas funcionalidades de Tailwind v3.
  - Se ajustaron las clases de Tailwind en `resultado.html` y otras plantillas para compatibilidad total con la nueva versión.
  - Se eliminó código CSS innecesario en `output.css`, reduciendo el peso del archivo final.

- **Refactorización del código JavaScript**:
  - Se consolidaron funciones redundantes en `resultado.html` para mejorar la eficiencia.
  - `closeShareModal()` se unificó para evitar múltiples declaraciones en distintos lugares.
  - Se optimizó el acceso a elementos del DOM mediante variables globales en lugar de llamadas repetitivas a `document.getElementById()`.
  - Se mejoró la gestión de clases CSS con `classList.toggle()` en lugar de múltiples `add` y `remove`.

- **Correcciones en el modal de compartir**:
  - Ahora el desenfoque del fondo (`backdrop-blur-md`) oculta correctamente la calculadora visual cuando el modal está abierto.
  - Se aseguraron transiciones más suaves al abrir y cerrar el modal.
  - Se corrigió la lógica para que el modal desaparezca inmediatamente tras copiar el texto.

### Correcciones de errores
- **Restauración del mensaje "¡Listo! Texto copiado"**:
  - Ahora el mensaje aparece inmediatamente después de copiar y se desvanece correctamente después de unos segundos.
  - Se solucionó un problema donde el mensaje no aparecía debido a un conflicto con la ejecución del cierre del modal.

- **Solución de problemas con compatibilidad en móviles**:
  - Se mejoró el soporte para dispositivos móviles en la visualización del modal.
  - Se ajustó la detección de `navigator.clipboard.writeText()` para evitar fallos en navegadores con restricciones.

- **Ajustes en la calculadora visual**:
  - Se corrigió un problema donde algunos números resaltados no se mostraban correctamente tras la actualización a Tailwind v3.
  - Se optimizó la animación de los números resaltados para mejorar la experiencia del usuario.

### Eliminaciones
- Eliminación de estilos duplicados en `output.css`.
- Eliminación de código obsoleto en `resultado.html` y `app.py` relacionado con clases de Tailwind desactualizadas.

---

## [1.3.2] - 2025-01-18
### Added
- Soporte para solicitudes **GET** en la ruta `/resultado_opcion2`, lo que permite procesar frases enviadas como parámetros en la URL (`?frase=...`).
  - Ejemplo: `https://lgc.julianosoriom.com/resultado_opcion2?frase=coraz%C3%B3n%20abierto`.
- La ruta sigue siendo compatible con solicitudes **POST**, manteniendo el comportamiento original.

### Changed
- Ningún cambio en funcionalidades existentes. La implementación asegura la compatibilidad con el flujo actual.

---

## [1.3.1] - 2025-01-18
### Added
- **Implementación de activación automática del teclado** al abrir el modal en dispositivos móviles:
  - Se asegura que el campo de entrada (`input`) reciba el foco de manera automática al abrir el modal.
  - Se incluye una simulación de clic virtual para navegadores que requieren interacción explícita, como Safari en iOS.
  - Ajustado con un retardo breve para garantizar que el modal esté completamente visible antes de activar el teclado.

### Changed
- Refactorización en la función `showModal` para manejar de manera más robusta la compatibilidad con navegadores móviles:
  - Uso de `setTimeout` con retardo optimizado.
  - Inclusión de eventos `focus()` y `click()` aplicados secuencialmente para maximizar la compatibilidad.
  - Mejora de los comentarios en el código para documentar las razones detrás de estos ajustes.

---

## [1.3.0] - 2025-01-17
### Added
- Nueva funcionalidad para mostrar **palabras con el potencial invertido**:
  - Si la palabra buscada tiene un total de 57, se muestra una nueva sección con palabras cuyo total sea 75 (el inverso).
  - Implementada en la plantilla `resultado.html` con un bloque adicional similar al de "Palabras con la misma Frecuencia Numérica".
- Lógica en el backend (`app.py`):
  - Se calcula el total invertido y se buscan palabras con dicho total.
  - Los resultados se envían al template bajo el parámetro `palabras_invertidas`.
- Comentarios detallados para explicar el manejo de la lógica del potencial invertido en `app.py`.

### Changed
- Refactorización de partes del controlador `resultado_opcion2` para mejorar la legibilidad y evitar redundancia en la manipulación de listas y búsquedas.
- Ajuste del diseño de `resultado.html` para mantener consistencia visual al agregar la nueva funcionalidad.

### Fixed
- Se corrigió un error menor en la generación del historial de búsquedas que permitía duplicados en ciertas condiciones.
- Mejoras menores en los comentarios de código para claridad futura.

---

## [1.2.9] - 2025-01-16
### Added
- Inclusión del enlace **Convierte palabras en números: https://lgc.julianosoriom.com** al texto compartido:
  - En el texto copiado al portapapeles.
  - En el mensaje compartido vía WhatsApp.
- Mensaje temporal al copiar texto:
  - Añadido un mensaje visual "Texto copiado al portapapeles" que aparece automáticamente y desaparece con un efecto de desvanecimiento suave.
  - Implementado con transparencia ajustada para mayor sutileza visual.

### Changed
- Ajustes en el formato de las líneas de resultados para asegurar que no contengan espacios innecesarios ni indentaciones en:
  - Texto copiado al portapapeles.
  - Mensaje compartido por WhatsApp.
- Refinamiento del diseño del mensaje temporal:
  - Mayor transparencia en el fondo (`rgba(76, 175, 80, 0.6)`).
  - Aparición y desvanecimiento más suaves con transiciones optimizadas.

### Fixed
- Eliminación de tabs o espacios adicionales en los resultados generados.
- Garantía de que el diseño visual del mensaje temporal no interfiera con otros elementos de la interfaz.

---

## [1.2.8] - 2025-01-15
### Added
- Inclusión de un **botón para compartir resultados**, con opciones para:
  - Enviar los resultados por WhatsApp con formato claro y amigable.
  - Copiar los resultados al portapapeles.
- Efectos visuales en el modal:
  - **Desenfoque de fondo** (`blur`) al abrir el modal.
  - Fondo semitransparente para resaltar el contenido activo.

### Changed
- Optimización del modal para mayor consistencia visual:
  - Se ajustaron las clases de Tailwind para asegurar un diseño responsivo y visualmente atractivo.



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