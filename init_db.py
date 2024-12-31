from app import db, app

def inicializar_tablas():
    """
    Inicializa las tablas en la base de datos si no existen.
    """
    print("Inicializando tablas en la base de datos...")
    with app.app_context():
        db.create_all()
    print("Tablas creadas exitosamente.")

if __name__ == '__main__':
    try:
        inicializar_tablas()
    except Exception as e:
        print(f"Error al inicializar las tablas: {e}")