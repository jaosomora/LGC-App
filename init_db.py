from app import db, app

def inicializar_tablas():
    """
    Crea las tablas necesarias en la base de datos si no existen.
    """
    print("Inicializando tablas en la base de datos...")
    with app.app_context():  # Aseguramos que 'db' use el contexto de 'app'
        db.create_all()  # Crear todas las tablas definidas
    print("Tablas creadas exitosamente.")

if __name__ == '__main__':
    inicializar_tablas()