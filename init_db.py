import os
from app import db, inicializar_tablas

def main():
    """
    Inicializa la base de datos y crea las tablas necesarias.
    """
    print("Iniciando la configuración de la base de datos...")
    inicializar_tablas()  # Crear tabla 'ranking' si no existe
    with db.app.app_context():
        db.create_all()  # Crear las tablas definidas en los modelos SQLAlchemy
    print("Base de datos configurada exitosamente.")

if __name__ == "__main__":
    main()