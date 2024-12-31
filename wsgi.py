from app import app, inicializar_base_datos

# Inicializar tablas antes de arrancar el servidor
inicializar_base_datos()

# Exponer la aplicación para gunicorn
if __name__ != "__main__":
    print("Servidor listo para manejar solicitudes.")