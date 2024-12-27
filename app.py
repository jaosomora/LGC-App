import unicodedata
import os
import json
from flask import Flask, request, render_template, session

# Inicializar Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Clave para manejar sesiones

# Obtener la ruta del directorio donde está ubicado el script
directorio_base = os.path.dirname(os.path.abspath(__file__))

# Definir las rutas absolutas de los archivos
archivo_territorios = os.path.join(directorio_base, "territorios.json")
archivo_palabras = os.path.join(directorio_base, "palabras.txt")
archivo_tabla_periodica = os.path.join(directorio_base, "tabla_periodica.json")
archivo_ranking = os.path.join(directorio_base, "ranking.txt")

# Mapeo personalizado de valores de letras según la tabla
valores_letras = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "\u00d1": 15, "O": 16, "P": 17, "Q": 18,
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
            resultados.append(f"Elemento: {nombre} ({simbolo}) - Coincidencia: Potencial del nombre ({potencial_nombre})")
        elif numero_atomico == potencial_objetivo:
            resultados.append(f"Elemento: {nombre} ({simbolo}) - Coincidencia: Número atómico ({numero_atomico})")
    return resultados

def cargar_palabras(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def cargar_ranking(archivo):
    """Carga y devuelve el ranking normalizado y ordenado por puntuación."""
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            palabras = {}
            for line in f:
                palabra, puntuacion = line.strip().split(":")
                palabra_normalizada = normalizar_palabra_con_espacios(palabra)
                palabras[palabra_normalizada] = int(puntuacion)
            print(f"Ranking cargado: {palabras}")  # Depuración
            ranking = sorted(palabras.items(), key=lambda x: x[1], reverse=True)
            return ranking
    except FileNotFoundError:
        return []

def buscar_palabras_por_potencial(palabras, potencial_objetivo):
    """Busca palabras en la lista que coincidan con el potencial dado."""
    resultados = []
    for palabra in palabras:
        if calcular_potencial(palabra) == potencial_objetivo:
            resultados.append(palabra)
    return resultados

def guardar_palabra(archivo, palabra):
    """Guarda una nueva palabra en el archivo si no existe ya."""
    try:
        palabra_normalizada = normalizar_palabra_con_espacios(palabra)
        palabras_existentes = cargar_palabras(archivo)
        if palabra_normalizada not in [normalizar_palabra_con_espacios(p) for p in palabras_existentes]:
            with open(archivo, "a", encoding="utf-8") as f:
                f.write(palabra + "\n")
            guardar_en_ranking(archivo_ranking, palabra)
            print(f"Palabra '{palabra}' guardada correctamente en {archivo}.")
        else:
            print(f"La palabra '{palabra}' ya existe en {archivo}.")
    except Exception as e:
        print(f"Error al guardar la palabra '{palabra}': {e}")

def guardar_en_ranking(archivo, palabra):
    """Guarda la palabra en el ranking si no existe o incrementa su puntuación."""
    try:
        palabra_normalizada = normalizar_palabra_con_espacios(palabra)
        ranking = cargar_ranking(archivo)
        palabras = {k: v for k, v in ranking}
        print(f"Ranking antes de actualizar: {palabras}")  # Depuración
        if palabra_normalizada in palabras:
            palabras[palabra_normalizada] += 1
        else:
            palabras[palabra_normalizada] = 1
        print(f"Ranking después de actualizar: {palabras}")  # Depuración
        palabras_ordenadas = sorted(palabras.items(), key=lambda x: x[1], reverse=True)
        with open(archivo, "w", encoding="utf-8") as f:
            for p, puntuacion in palabras_ordenadas:
                f.write(f"{p}:{puntuacion}\n")
    except Exception as e:
        print(f"Error al guardar en ranking: {e}")

# Rutas para la aplicación Flask
@app.route('/')
def menu_principal():
    historial = session.get('historial', [])
    return render_template('menu.html', historial=historial)

@app.route('/opcion1')
def opcion1():
    return render_template('opcion1.html')

@app.route('/opcion2')
def opcion2():
    return render_template('opcion2.html')

@app.route('/ranking')
def mostrar_ranking():
    """Muestra el ranking de palabras según su potencial."""
    ranking = cargar_ranking(archivo_ranking)
    return render_template('ranking.html', ranking=ranking)

@app.route('/agregar_palabra', methods=['GET', 'POST'])
def agregar_palabra():
    """Ruta para agregar nuevas palabras al archivo palabras.txt."""
    if request.method == 'POST':
        nueva_palabra = request.form.get('palabra', '').strip()
        if nueva_palabra:
            guardar_palabra(archivo_palabras, nueva_palabra)
            mensaje = f"Palabra '{nueva_palabra}' guardada con éxito."
        else:
            mensaje = "No se pudo guardar una palabra vacía."
        return render_template('agregar_palabra.html', mensaje=mensaje)
    return render_template('agregar_palabra.html')

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

    palabras = cargar_palabras(archivo_palabras)
    palabras_encontradas = buscar_palabras_por_potencial(palabras, potencial)
    palabras_encontradas.sort(key=lambda p: calcular_potencial(p), reverse=True)

    # Guardar la palabra en palabras.txt
    guardar_palabra(archivo_palabras, palabra)

    # Agregar al historial
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

    palabras = cargar_palabras(archivo_palabras)
    palabras_encontradas = buscar_palabras_por_potencial(palabras, frecuencia)
    palabras_encontradas.sort(key=lambda p: calcular_potencial(p), reverse=True)

    # Agregar al historial
    if 'historial' not in session:
        session['historial'] = []
    session['historial'].append(f"Frecuencia: {frecuencia} -> Lupa: {lupa}")
    session.modified = True

    return render_template('resultado.html', frecuencia=frecuencia, lupa=lupa, territorios=territorios_encontrados, palabras=palabras_encontradas, elementos=elementos)

if __name__ == '__main__':
    app.run(debug=True)
