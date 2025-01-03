# CHANGELOG

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

## [1.1.0] - 2024-12-31
### Added
- `init_db.py` para inicialización automática de la base de datos.
- `wsgi.py` para compatibilidad con gunicorn.
- Validación de caracteres en palabras ingresadas.
- Configuración dinámica de base de datos según entorno.

### Fixed
- Correcciones en el manejo de sesiones.
- Eliminación de errores relacionados con tablas SQLite.

## [1.0.0] - 2024-12-15
- Primera versión estable.