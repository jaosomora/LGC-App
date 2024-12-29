import unicodedata
import os
import json
import time
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, session
from flask_cors import CORS  # Asegúrate de importar CORS

# Obtener la ruta del directorio donde está ubicado el script
directorio_base = os.path.dirname(os.path.abspath(__file__))

# Definir las rutas absolutas de los archivos
archivo_territorios = os.path.join(directorio_base, "territorios.json")  # Añadido correctamente
archivo_tabla_periodica = os.path.join(directorio_base, "tabla_periodica.json")
archivo_ranking = os.path.join(directorio_base, "ranking.txt")

# Inicializar Flask
app = Flask(__name__)

# Usar almacenamiento persistente en Render para la base de datos
db_path = os.path.join('/mnt/data', 'palabras.db')  # Ruta persistente en Render
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Evitar advertencias innecesarias
db = SQLAlchemy(app)

# Configurar CORS para permitir el acceso desde julianosoriom.com
CORS(app, origins=["https://www.julianosoriom.com"])

# Configurar cookies para trabajar en iframes
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Permitir compartir cookies en iframes
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS obligatorio en producción

# Configuración de la clave secreta para sesiones
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-por-defecto')

# Crear las tablas automáticamente al iniciar la aplicación
with app.app_context():
    db.create_all()  # Esto crea las tablas en la base de datos si no existen

# Definición de la clase Palabra (ubicada antes de la función que la usa)
class Palabra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    palabra = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Palabra {self.palabra}>'

# Validar que una palabra sea alfabética
def es_palabra_valida(palabra):
    return palabra.isalpha()

# Modificar guardar_palabra para evitar duplicados y validar palabras
def guardar_palabra(palabra):
    try:
        # Validar que sea una palabra válida
        if not es_palabra_valida(palabra):
            print(f"La palabra '{palabra}' no es válida.")
            return

        palabra_normalizada = normalizar_palabra_con_espacios(palabra)
        existing_word = Palabra.query.filter_by(palabra=palabra_normalizada).first()
        if not existing_word:
            new_palabra = Palabra(palabra=palabra_normalizada)
            db.session.add(new_palabra)
            db.session.commit()
            print(f"La palabra '{palabra}' ha sido guardada correctamente.")
        else:
            print(f"La palabra '{palabra}' ya existe en la base de datos.")
    except Exception as e:
        print(f"Error al guardar la palabra '{palabra}': {e}")

# Limpieza de la base de datos para eliminar duplicados o palabras irrelevantes
def limpiar_base_datos():
    try:
        palabras = Palabra.query.all()
        palabras_validas = set()

        for palabra in palabras:
            if es_palabra_valida(palabra.palabra):
                if palabra.palabra not in palabras_validas:
                    palabras_validas.add(palabra.palabra)
                else:
                    db.session.delete(palabra)
            else:
                db.session.delete(palabra)

        db.session.commit()
        print("Base de datos limpiada exitosamente.")
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")

# Crear rutas para limpiar la base de datos (opcional y protegida)
@app.route('/limpiar_base', methods=['POST'])
def limpiar_base_route():
    limpiar_base_datos()
    return "Base de datos limpiada exitosamente.", 200

# Mapeo personalizado de valores de letras según la tabla
valores_letras = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "Ñ": 15, "O": 16, "P": 17, "Q": 18,
    "R": 19, "S": 20, "T": 21, "U": 22, "V": 23, "W": 24, "X": 25, "Y": 26, "Z": 27
}

# Funciones para cálculos y procesamiento de datos
def normalizar_palabra_con_espacios(palabra):
    palabra = ''.join(
        char for char in unicodedata.normalize('NFD', palabra)
        if unicodedata.category(char) != 'Mn'
    )
    palabra = ''.join(char for char in palabra.upper() if char in valores_letras or char == " ")
    return palabra

def calcular_potencial(palabra):
    palabra_normalizada = normalizar_palabra_con_espacios(palabra)
    return sum(valores_letras[letra] for letra in palabra_normalizada if letra != " ")

def calcular_lupa(potencial):
    return round(potencial * 1.21, 2)

def detalle_potencial(palabra):
    palabra_normalizada = normalizar_palabra_con_espacios(palabra)
    valores = [valores_letras[letra] for letra in palabra_normalizada if letra != " "]
    return valores

def cargar_codigos_territorios(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def buscar_codigo_territorio(codigos, valor_objetivo):
    resultados = []
    valor_objetivo = str(valor_objetivo)  # Convertir a cadena para comparaciones
    for territorio in codigos:
        codigo_normalizado = str(territorio["codigo"]).split("-")[-1]
        if codigo_normalizado == valor_objetivo:
            resultados.append(territorio)
    return resultados

def cargar_tabla_periodica(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def buscar_elementos_por_potencial(tabla_periodica, potencial_objetivo, lupa_objetivo=None):
    resultados = []
    for elemento in tabla_periodica:
        nombre = elemento["nombre"]
        simbolo = elemento["simbolo"]
        numero_atomico = elemento["numero_atomico"]
        masa = elemento["masa"]
        potencial_nombre = calcular_potencial(nombre)
        potencial_simbolo = calcular_potencial(simbolo)

        if potencial_nombre == potencial_objetivo:
            resultados.append(f"<strong>Elemento:</strong> {nombre} ({simbolo}) - <strong>Coincidencia:</strong> Potencial del nombre ({potencial_nombre})")
        elif numero_atomico == potencial_objetivo:
            resultados.append(f"<strong>Elemento:</strong> {nombre} ({simbolo}) - <strong>Coincidencia:</strong> Número atómico ({numero_atomico})")
    return resultados

def cargar_ranking(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            palabras = {}
            for line in f:
                palabra, puntuacion = line.strip().split(":")
                palabra_normalizada = normalizar_palabra_con_espacios(palabra)
                palabras[palabra_normalizada] = int(puntuacion)
            ranking = sorted(palabras.items(), key=lambda x: x[1], reverse=True)
            return ranking
    except FileNotFoundError:
        return []

def buscar_palabras_por_potencial(palabras, potencial_objetivo):
    resultados = []
    for palabra in palabras:
        if calcular_potencial(palabra) == potencial_objetivo:
            resultados.append(palabra)
    return resultados

# Función para cargar las palabras desde la base de datos
def cargar_palabras():
    palabras = Palabra.query.all()
    return [p.palabra for p in palabras]

# Rutas para la aplicación Flask
@app.route('/')
def menu_principal():
    print("Historial desde /:", session.get('historial', []))  # Log para verificar el historial
    historial = session.get('historial', ["Realidad", "Elemental", "Frecuencia"])
    return render_template('menu.html', historial=historial)

@app.route('/opcion1')
def opcion1():
    return render_template('opcion1.html')

@app.route('/opcion2')
def opcion2():
    return render_template('opcion2.html')

@app.route('/ranking')
def mostrar_ranking():
    ranking = cargar_ranking(archivo_ranking)
    return render_template('ranking.html', ranking=ranking)

@app.route('/resultado_opcion2', methods=['POST'])
def resultado_opcion2():
    palabra = request.form.get('palabra')
    potencial = calcular_potencial(palabra)
    lupa = calcular_lupa(potencial)
    detalle = detalle_potencial(palabra)

    territorios = cargar_codigos_territorios(archivo_territorios)
    territorios_encontrados = buscar_codigo_territorio(territorios, potencial)

    tabla_periodica = cargar_tabla_periodica(archivo_tabla_periodica)
    elementos = buscar_elementos_por_potencial(tabla_periodica, potencial, lupa)

    palabras = cargar_palabras()
    palabras_encontradas = buscar_palabras_por_potencial(palabras, potencial)
    palabras_encontradas = list(set(normalizar_palabra_con_espacios(p) for p in palabras_encontradas))  # Eliminar duplicados normalizando
    palabras_encontradas.sort(key=lambda p: calcular_potencial(p), reverse=True)

    guardar_palabra(palabra)

    if 'historial' not in session:
        session['historial'] = []
    session['historial'].append(f"Palabra: {palabra} -> Potencial: {potencial}, Lupa: {lupa}")
    session.modified = True

    return render_template('resultado.html', palabra=palabra, potencial=potencial, lupa=lupa, detalle=detalle, territorios=territorios_encontrados, palabras=palabras_encontradas, elementos=elementos)

@app.route('/resultado_opcion1', methods=['POST'])
def resultado_opcion1():
    frecuencia = int(request.form.get('frecuencia'))
    lupa = calcular_lupa(frecuencia)

    territorios = cargar_codigos_territorios(archivo_territorios)
    territorios_encontrados = buscar_codigo_territorio(territorios, frecuencia)

    tabla_periodica = cargar_tabla_periodica(archivo_tabla_periodica)
    elementos = buscar_elementos_por_potencial(tabla_periodica, frecuencia, lupa)

    palabras = cargar_palabras()
    palabras_encontradas = buscar_palabras_por_potencial(palabras, frecuencia)
    palabras_encontradas = list(set(normalizar_palabra_con_espacios(p) for p in palabras_encontradas))  # Eliminar duplicados normalizando
    palabras_encontradas.sort(key=lambda p: calcular_potencial(p), reverse=True)

    if 'historial' not in session:
        session['historial'] = []
    session['historial'].append(f"Frecuencia: {frecuencia} -> Lupa: {lupa}")
    session.modified = True

    return render_template('resultado.html', frecuencia=frecuencia, lupa=lupa, territorios=territorios_encontrados, palabras=palabras_encontradas, elementos=elementos)

@app.route('/embed_page')
def embed_page():
    print("Historial desde /embed_page:", session.get('historial', []))  # Log para verificar el historial
    historial = session.get('historial', ["Realidad", "Elemental", "Frecuencia"])
    return render_template('embed.html', historial=historial)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)