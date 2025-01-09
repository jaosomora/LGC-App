import unicodedata
import os
import json
import time
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, session
from flask_cors import CORS  # Asegúrate de importar CORS

# Configuración inicial de la aplicación Flask y sus componentes

# Obtener la ruta del directorio donde está ubicado el script
directorio_base = os.path.dirname(os.path.abspath(__file__))

# Definir las rutas absolutas de los archivos
archivo_territorios = os.path.join(
    directorio_base, "territorios.json"
)  # Archivo con códigos de territorios
archivo_tabla_periodica = os.path.join(
    directorio_base, "tabla_periodica.json"
)  # Archivo con datos de la tabla periódica
archivo_ranking = os.path.join(
    directorio_base, "ranking.txt"
)  # Archivo con palabras y su ranking

# Inicializar Flask
app = Flask(__name__)

# Configuración de la base de datos SQLite
if os.getenv("RENDER") and os.getenv("ENV") == "PRODUCTION":
    # Producción: utilizar ruta persistente en Render
    if not os.path.exists("/mnt/data"):
        os.makedirs("/mnt/data")  # Crear el directorio si no existe
    db_path = os.path.join("/mnt/data", "palabras.db")  # Ruta persistente en Render
else:
    # Desarrollo: utilizar la ruta local
    db_path = os.path.join(directorio_base, "palabras.db")  # Ruta en local

# Crear el archivo de base de datos si no existe
if not os.path.exists(db_path):
    print(f"Creando archivo de base de datos en: {db_path}")
    open(db_path, "w").close()


# Crear el archivo de base de datos si no existe
if not os.path.exists(db_path):
    print(f"Creando archivo de base de datos en: {db_path}")
    open(db_path, "w").close()

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Evitar advertencias innecesarias
db = SQLAlchemy(app)

# Configurar CORS para permitir el acceso desde julianosoriom.com
CORS(app, origins=["https://www.julianosoriom.com"])

# Configurar cookies para trabajar en iframes
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # Permitir compartir cookies en iframes
app.config["SESSION_COOKIE_SECURE"] = True  # HTTPS obligatorio en producción

# Configuración de la clave secreta para sesiones
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")

# Crear las tablas automáticamente al iniciar la aplicación
with app.app_context():
    db.create_all()  # Esto crea las tablas en la base de datos si no existen


# Modelo de datos para representar palabras en la base de datos
class Palabra(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único
    palabra = db.Column(
        db.String(100), unique=True, nullable=False
    )  # Palabra única, no nula

    def __repr__(self):
        return f"<Palabra {self.palabra}>"


def es_palabra_valida(palabra):
    """
    Verifica que una palabra o frase contenga solo caracteres alfabéticos, espacios o números.
    """
    return all(
        letra.isalpha() or letra.isspace() or letra.isdigit() for letra in palabra
    )


def inicializar_base_datos():
    """
    Garantiza que todas las tablas estén creadas antes de iniciar el servidor.
    """
    print("Inicializando tablas en la base de datos...")
    with app.app_context():
        db.create_all()
    print("✅ Tablas creadas exitosamente.")


# Guardar palabras en la base de datos con validación y prevención de duplicados
def guardar_palabra(palabra):
    try:
        # Normalizar palabra o frase solo una vez
        print(
            f"[DEBUG] Palabra antes de normalizar en guardar_palabra: {palabra}"
        )  # LOG NUEVO
        palabra_normalizada = normalizar_palabra_con_espacios(palabra)
        print(
            f"[DEBUG] Palabra después de normalizar en guardar_palabra: {palabra_normalizada}"
        )  # LOG NUEVO

        # Verificar si la palabra es válida
        if not es_palabra_valida(palabra_normalizada):
            print(
                f"La entrada '{palabra}' no es válida. Solo se permiten letras, espacios o números."
            )
            return

        # Verificar si ya existe en la base de datos
        print(
            f"[DEBUG] Consultando la base de datos con: {palabra_normalizada}"
        )  # LOG NUEVO
        existing_word = Palabra.query.filter_by(palabra=palabra_normalizada).first()
        print(
            f"[DEBUG] Resultado de la consulta en guardar_palabra: {existing_word}"
        )  # LOG NUEVO
        if not existing_word:
            # Crear nueva palabra y guardar
            print(
                f"[DEBUG] Guardando nueva palabra en la base de datos: {palabra_normalizada}"
            )  # LOG NUEVO
            new_palabra = Palabra(palabra=palabra_normalizada)
            db.session.add(new_palabra)
            db.session.commit()
            print(
                f"La palabra o frase '{palabra_normalizada}' ha sido guardada correctamente."
            )
        else:
            print(
                f"La palabra o frase '{palabra_normalizada}' ya existe en la base de datos."
            )
    except Exception as e:
        # Manejo de excepciones con mensaje de error
        print(f"Error al guardar la palabra o frase '{palabra}': {e}")


import os


def inicializar_tablas():
    """
    Crea la tabla 'ranking' en la base de datos si no existe.
    """
    try:
        print(f"Verificando base de datos en: {db_path}")
        if not os.path.exists(db_path):
            print(
                f"Base de datos no encontrada. Creando un nuevo archivo en: {db_path}"
            )
            open(db_path, "w").close()

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ranking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                palabra TEXT NOT NULL UNIQUE,
                puntuacion INTEGER NOT NULL
            )
        """
        )
        connection.commit()
        print("Tabla 'ranking' inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"Error al inicializar las tablas: {e}")
    finally:
        connection.close()


# Limpieza de la base de datos para eliminar duplicados o palabras irrelevantes
def limpiar_base_datos():
    """
    Limpia la base de datos eliminando duplicados y palabras no válidas.
    """
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


# Ruta para limpiar la base de datos manualmente (protegida)
@app.route("/limpiar_base", methods=["POST"])
def limpiar_base_route():
    """
    Endpoint para ejecutar la limpieza de la base de datos.
    """
    limpiar_base_datos()
    return "Base de datos limpiada exitosamente.", 200


# Mapeo personalizado de valores de letras según la tabla
valores_letras = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "I": 9,
    "J": 10,
    "K": 11,
    "L": 12,
    "M": 13,
    "N": 14,
    "Ñ": 15,
    "O": 16,
    "P": 17,
    "Q": 18,
    "R": 19,
    "S": 20,
    "T": 21,
    "U": 22,
    "V": 23,
    "W": 24,
    "X": 25,
    "Y": 26,
    "Z": 27,
}


def detalle_potencial(palabra):
    """
    Devuelve una lista de valores numéricos para cada letra de la palabra.
    Filtra caracteres no alfabéticos antes de procesarlos y asegura que la letra Ñ
    sea tratada correctamente, sin ser alterada por la normalización.
    """
    palabra_normalizada = normalizar_palabra_con_espacios(palabra)
    valores = [
        valores_letras.get(
            letra.upper(), 0
        )  # Usa get para evitar errores si no existe la clave
        for letra in palabra_normalizada
        if letra.isalpha() or letra.lower() == "ñ"  # Asegura que Ñ no se excluya
    ]
    return valores


def normalizar_palabra_con_espacios(palabra):
    """
    Normaliza palabras o frases:
    - Convierte a minúsculas
    - Conserva la 'ñ' correctamente
    - Elimina tildes de otras letras
    - Reemplaza espacios múltiples por uno solo
    """
    import unicodedata

    print(f"[DEBUG] Palabra antes de normalizar: {palabra}")

    # Reemplazar espacios múltiples por uno y convertir a minúsculas
    palabra = " ".join(palabra.strip().split()).lower()

    # Proteger la letra 'ñ' temporalmente
    palabra_protegida = palabra.replace("ñ", "__PROTECCION_N__")

    # Normalizar y eliminar tildes
    palabra_normalizada = "".join(
        c
        for c in unicodedata.normalize("NFD", palabra_protegida)
        if unicodedata.category(c) != "Mn"
    )

    # Restaurar la 'ñ'
    palabra_normalizada = palabra_normalizada.replace("__PROTECCION_N__", "ñ")

    print(f"[DEBUG] Palabra después de normalizar: {palabra_normalizada}")
    return palabra_normalizada


def calcular_potencial(palabra):
    """
    Calcula el potencial de una palabra sumando los valores de sus letras.
    Convierte las letras a mayúsculas para buscar en el diccionario `valores_letras`.
    """
    palabra_normalizada = normalizar_palabra_con_espacios(
        palabra
    ).upper()  # Convertir a mayúsculas
    return sum(
        valores_letras[letra] for letra in palabra_normalizada if letra.isalpha()
    )


def calcular_lupa(potencial):
    """
    Calcula el valor amplificado del potencial (factor de 1.21).
    """
    return round(potencial * 1.21, 2)


def calcular_frecuencia_por_palabra(frase):
    """
    Calcula la frecuencia por letra y la suma para cada palabra en una frase.
    Retorna un diccionario con los resultados por palabra y la suma total.
    """
    palabras = frase.split()  # Divide la frase en palabras
    resultado = {}
    suma_total = 0

    # Diccionario extendido con valores para todas las variantes de letras
    valores_letras_actualizado = {
        **valores_letras,
        "Ñ": 15,  # Valor para Ñ mayúscula
        "ñ": 15,  # Valor para ñ minúscula
    }

    for palabra in palabras:
        # Normalización cuidadosa
        palabra_normalizada = "".join(
            char
            if char in {"Ñ", "ñ"} else unicodedata.normalize("NFD", char)[0]
            for char in palabra
            if unicodedata.category(char) != "Mn" or char in {"Ñ", "ñ"}
        )

        # Depuración para verificar la palabra normalizada
        print(f"[DEBUG] Palabra normalizada: {palabra_normalizada}")

        # Calcular frecuencias por letra
        frecuencias = []
        for letra in palabra_normalizada:
            if letra.upper() in valores_letras_actualizado:
                valor = valores_letras_actualizado[letra.upper()]
                frecuencias.append(valor)
                print(f"[DEBUG] Letra '{letra}' encontrada con valor {valor}.")
            else:
                frecuencias.append(0)
                print(f"[DEBUG] Letra '{letra}' no encontrada en el diccionario.")

        # Depuración de frecuencias calculadas
        print(f"[DEBUG] Frecuencias para {palabra}: {frecuencias}")

        suma_palabra = sum(frecuencias)

        # Almacenar los resultados
        resultado[palabra] = {
            "frecuencia_por_letra": frecuencias,
            "suma": suma_palabra,
        }
        suma_total += suma_palabra

    # Depuración final
    print(f"[DEBUG] Frecuencias por palabra: {resultado}")
    print(f"[DEBUG] Suma total de frecuencias: {suma_total}")

    return resultado, suma_total


# Funciones para manejo de datos externos
def cargar_codigos_territorios(archivo):
    """
    Carga datos de territorios desde un archivo JSON.
    """
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def buscar_codigo_territorio(codigos, valor_objetivo):
    """
    Busca territorios que coincidan con un valor objetivo.
    """
    resultados = []
    valor_objetivo = str(valor_objetivo)  # Convertir a cadena para comparaciones
    for territorio in codigos:
        codigo_normalizado = str(territorio["codigo"]).split("-")[-1]
        if codigo_normalizado == valor_objetivo:
            resultados.append(territorio)
    return resultados


def cargar_tabla_periodica(archivo):
    """
    Carga datos de elementos químicos desde un archivo JSON.
    """
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def buscar_elementos_por_potencial(
    tabla_periodica, potencial_objetivo, lupa_objetivo=None
):
    """
    Busca elementos químicos en la tabla periódica según el potencial o lupa.
    """
    resultados = []
    for elemento in tabla_periodica:
        nombre = elemento["nombre"]
        simbolo = elemento["simbolo"]
        numero_atomico = elemento["numero_atomico"]
        masa = elemento["masa"]
        potencial_nombre = calcular_potencial(nombre)
        potencial_simbolo = calcular_potencial(simbolo)

        if potencial_nombre == potencial_objetivo:
            resultados.append(
                f"<strong>Elemento:</strong> {nombre} ({simbolo}) - <strong>Coincidencia:</strong> Potencial del nombre ({potencial_nombre})"
            )
        elif numero_atomico == potencial_objetivo:
            resultados.append(
                f"<strong>Elemento:</strong> {nombre} ({simbolo}) - <strong>Coincidencia:</strong> Número atómico ({numero_atomico})"
            )
    return resultados


def cargar_ranking_desde_bd():
    """
    Carga el ranking de palabras desde la base de datos.
    Retorna una lista de tuplas (palabra, puntuacion) ordenadas por puntuacion descendente.
    """
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Verificar si la tabla existe
        cursor.execute(
            """
            SELECT name FROM sqlite_master WHERE type='table' AND name='ranking';
        """
        )
        if not cursor.fetchone():
            print("La tabla 'ranking' no existe. Creándola ahora.")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ranking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    palabra TEXT NOT NULL UNIQUE,
                    puntuacion INTEGER NOT NULL
                )
            """
            )
            connection.commit()

        # Cargar datos del ranking
        cursor.execute(
            "SELECT palabra, puntuacion FROM ranking ORDER BY puntuacion DESC"
        )
        ranking = cursor.fetchall()
        connection.close()
        return ranking

    except sqlite3.Error as e:
        print(f"Error al cargar el ranking desde la base de datos: {e}")
        return []


def actualizar_ranking(palabra):
    try:
        # Normalizar palabra o frase asegurando que 'ñ' se maneje correctamente
        print(
            f"[DEBUG] Palabra antes de normalizar en actualizar_ranking: {palabra}"
        )  # LOG NUEVO
        palabra_normalizada = normalizar_palabra_con_espacios(palabra)
        print(
            f"[DEBUG] Palabra después de normalizar en actualizar_ranking: {palabra_normalizada}"
        )  # LOG NUEVO

        print(f"Intentando actualizar ranking para: {palabra_normalizada}")

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Verificar si ya existe en el ranking
        print(
            f"[DEBUG] Consultando la tabla ranking con: {palabra_normalizada}"
        )  # LOG NUEVO
        cursor.execute(
            "SELECT puntuacion FROM ranking WHERE palabra = ?", (palabra_normalizada,)
        )
        resultado = cursor.fetchone()
        print(
            f"[DEBUG] Resultado de la consulta en actualizar_ranking: {resultado}"
        )  # LOG NUEVO

        if resultado:
            # Incrementar puntuación
            nueva_puntuacion = resultado[0] + 1
            print(
                f"[DEBUG] Actualizando puntuación en la tabla ranking para: {palabra_normalizada}, nueva puntuación: {nueva_puntuacion}"
            )  # LOG NUEVO
            cursor.execute(
                "UPDATE ranking SET puntuacion = ? WHERE palabra = ?",
                (nueva_puntuacion, palabra_normalizada),
            )
            print(
                f"Ranking actualizado: {palabra_normalizada} -> Puntuación: {nueva_puntuacion}"
            )
        else:
            # Agregar nueva palabra o frase
            cursor.execute(
                "INSERT INTO ranking (palabra, puntuacion) VALUES (?, ?)",
                (palabra_normalizada, 1),
            )
            print(
                f"'{palabra_normalizada}' añadida al ranking con puntuación inicial de 1."
            )

        # Depuración adicional para verificar el estado final de la tabla
        cursor.execute(
            "SELECT * FROM ranking WHERE palabra = ?", (palabra_normalizada,)
        )
        final_resultado = cursor.fetchone()
        print(
            f"Estado final en la base de datos para '{palabra_normalizada}': {final_resultado}"
        )

        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        print(f"Error al actualizar el ranking para '{palabra}': {e}")


def buscar_palabras_por_potencial(palabras, potencial_objetivo):
    """
    Busca palabras en la base de datos que coincidan con un potencial dado.
    """
    resultados = []
    for palabra in palabras:
        if calcular_potencial(palabra) == potencial_objetivo:
            resultados.append(palabra)
    return resultados


# Función para cargar las palabras desde la base de datos
def cargar_palabras():
    """
    Devuelve una lista de todas las palabras almacenadas en la base de datos.
    """
    palabras = Palabra.query.all()
    return [p.palabra for p in palabras]


# Rutas para la aplicación Flask
@app.route("/")
def menu_principal():
    """
    Muestra el menú principal con opciones disponibles.
    Ordena el historial de búsquedas según el ranking.
    """
    print(
        "Historial desde /:", session.get("historial", [])
    )  # Log para verificar el historial
    historial = session.get("historial", [])

    # Cargar el ranking desde la base de datos
    ranking = cargar_ranking_desde_bd()
    ranking_dict = {}
    for palabra, puntuacion in ranking:
        palabra_normalizada = normalizar_palabra_con_espacios(palabra).lower()
        ranking_dict[palabra_normalizada] = puntuacion
    print(f"Ranking dict procesado correctamente: {ranking_dict}")

    # Logs de depuración
    print(f"Ranking desde BD: {ranking}")
    print(f"Ranking dict procesado: {ranking_dict}")

    # Normalizar las palabras en el historial para evitar duplicados
    historial_normalizado = []
    for entry in historial:
        try:
            # Extraer palabra o frecuencia del historial
            if "Palabra:" in entry:
                palabra_extraida = (
                    entry.split("Palabra:")[1].split("->")[0].strip().lower()
                )
            elif "Frecuencia:" in entry:
                palabra_extraida = (
                    entry.split("Frecuencia:")[1].split("->")[0].strip().lower()
                )
            else:
                palabra_extraida = None

            # Agregar al historial normalizado con su puntuación correspondiente
            historial_normalizado.append(
                {
                    "item": entry,
                    "palabra": palabra_extraida,
                    "puntuacion": ranking_dict.get(palabra_extraida, None),
                }
            )
        except IndexError:
            historial_normalizado.append(
                {"item": entry, "palabra": None, "puntuacion": None}
            )

    # Convertir a lista ordenada y única
    historial_unico = historial_normalizado
    historial_unico.sort(
        key=lambda x: ranking_dict.get(
            normalizar_palabra_con_espacios(x["palabra"]).lower(), 0
        ),
        reverse=True,
    )

    # Log del historial ordenado
    print(f"Historial único ordenado: {historial_unico}")

    # Retornar el render correctamente
    return render_template("menu.html", historial=historial_unico, ranking=ranking_dict)


@app.route("/opcion1")
def opcion1():
    """
    Carga la página de la primera opción para calcular frecuencias.
    """
    return render_template("opcion1.html")


@app.route("/opcion2")
def opcion2():
    """
    Carga la página de la segunda opción para calcular potenciales.
    """
    return render_template("opcion2.html")


@app.route("/ranking")
def mostrar_ranking():
    """
    Muestra el ranking de palabras basado en un archivo de texto.
    """
    ranking = cargar_ranking(archivo_ranking)
    return render_template("ranking.html", ranking=ranking)


@app.route("/resultado_opcion2", methods=["POST"])
def resultado_opcion2():
    """
    Procesa la palabra o frase ingresada en la opción 2 y genera los resultados.
    """
    palabra = request.form.get("palabra")
    print(f"[DEBUG] Palabra ingresada por el usuario: {palabra}")  # LOG NUEVO

    # Verificar si la palabra contiene caracteres válidos (alfabéticos y espacios)
    if not palabra or not all(char.isalpha() or char.isspace() for char in palabra):
        # Si la palabra no es válida, retorna al formulario con un mensaje de error
        return render_template(
            "opcion2.html",
            error="La palabra contiene caracteres no válidos. Por favor, ingrese solo letras y espacios.",
        )

    # Continúa el procesamiento solo si la palabra es válida
    potencial = calcular_potencial(palabra)
    lupa = calcular_lupa(potencial)
    detalle = detalle_potencial(palabra)

    # Calcular frecuencia por palabra en caso de que sea una frase
    frecuencias_por_palabra, suma_total = calcular_frecuencia_por_palabra(palabra)

    # Depuración de los resultados
    print(f"[DEBUG] Frecuencias por palabra: {frecuencias_por_palabra}")
    print(f"[DEBUG] Suma total de frecuencias: {suma_total}")

    # Normalizar la palabra antes de guardar o actualizar
    palabra_normalizada = normalizar_palabra_con_espacios(palabra).lower()
    print(f"[DEBUG] Palabra normalizada: {palabra_normalizada}")

    # Guardar la palabra en la base de datos
    guardar_palabra(palabra_normalizada)

    # Actualizar el ranking
    actualizar_ranking(palabra_normalizada)

    # Verificar el ranking actualizado
    ranking_actualizado = cargar_ranking_desde_bd()
    print(f"[DEBUG] Ranking después de actualizar: {ranking_actualizado}")

    # Cargar y buscar territorios
    territorios = cargar_codigos_territorios(archivo_territorios)
    territorios_encontrados = buscar_codigo_territorio(territorios, potencial)

    # Cargar y buscar elementos químicos
    tabla_periodica = cargar_tabla_periodica(archivo_tabla_periodica)
    elementos = buscar_elementos_por_potencial(tabla_periodica, potencial, lupa)

    # Cargar palabras y buscar coincidencias
    palabras = cargar_palabras()
    palabras_encontradas = buscar_palabras_por_potencial(palabras, potencial)
    palabras_encontradas = list(
        set(normalizar_palabra_con_espacios(p) for p in palabras_encontradas)
    )
    palabras_encontradas = [
        p for p in palabras_encontradas if p.lower() != palabra.lower()
    ]  # Excluir la palabra buscada
    palabras_encontradas = [
        p for p in palabras_encontradas if p != palabra
    ]  # Eliminar duplicados normalizando
    palabras_encontradas.sort(key=lambda p: calcular_potencial(p), reverse=True)

    if palabras_encontradas:
        for palabra_encontrada in palabras_encontradas:
            palabra_normalizada = normalizar_palabra_con_espacios(
                palabra_encontrada
            ).lower()
            actualizar_ranking(palabra_normalizada)

    # Historial de búsqueda
    if "historial" not in session:
        session["historial"] = []

    nueva_entrada = f"Palabra: {palabra} -> Potencial: {potencial}, Lupa: {lupa}"
    if nueva_entrada.lower() not in [entry.lower() for entry in session["historial"]]:
        session["historial"].append(nueva_entrada)

    session.modified = True

    # Renderizado de resultados
    return render_template(
        "resultado.html",
        palabra=palabra,
        potencial=potencial,
        lupa=lupa,
        detalle=detalle,
        frecuencias_por_palabra=frecuencias_por_palabra,
        total=suma_total,  # Cambiado para incluir el total de frecuencias
        territorios=territorios_encontrados,
        palabras=palabras_encontradas,
        elementos=elementos,
        opcion=2,  # Identificar opción 2 en el template
    )


@app.route("/resultado_opcion1", methods=["POST"])
def resultado_opcion1():
    """
    Procesa la frecuencia ingresada en la opción 1 y genera los resultados.
    """
    frecuencia = int(request.form.get("frecuencia"))
    lupa = calcular_lupa(frecuencia)

    # Detalles para la frecuencia ingresada
    detalle = [
        frecuencia
    ]  # Frecuencia por letra sería el número en sí mismo para esta opción

    # Cargar datos geográficos
    territorios = cargar_codigos_territorios(archivo_territorios)
    territorios_encontrados = buscar_codigo_territorio(territorios, frecuencia)

    # Cargar elementos de la tabla periódica
    tabla_periodica = cargar_tabla_periodica(archivo_tabla_periodica)
    elementos = buscar_elementos_por_potencial(tabla_periodica, frecuencia, lupa)

    # Cargar palabras desde la base de datos y buscar coincidencias por potencial
    palabras = cargar_palabras()
    palabras_encontradas = buscar_palabras_por_potencial(palabras, frecuencia)

    # Asegurar que las palabras estén normalizadas y eliminar duplicados
    palabras_encontradas = list(
        set(normalizar_palabra_con_espacios(p) for p in palabras_encontradas)
    )

    # Filtrar palabras no válidas
    palabras_encontradas = [
        p
        for p in palabras_encontradas
        if calcular_potencial(p) == frecuencia and all(letra.isalpha() for letra in p)
    ]

    if not palabras_encontradas:
        print(
            "No se encontraron palabras válidas después de filtrar caracteres no alfabéticos."
        )

    palabras_encontradas.sort(key=lambda p: calcular_potencial(p), reverse=True)

    # Normalizar la frecuencia y tratarla como palabra para el ranking
    print(f"Frecuencia ingresada: {frecuencia}")
    frecuencia_normalizada = normalizar_palabra_con_espacios(str(frecuencia))
    print(f"Frecuencia normalizada: {frecuencia_normalizada}")
    print(f"Ranking antes de actualizar: {cargar_ranking_desde_bd()}")

    guardar_palabra(frecuencia_normalizada)
    actualizar_ranking(frecuencia_normalizada)

    print(f"Ranking después de actualizar: {cargar_ranking_desde_bd()}")

    if "historial" not in session:
        session["historial"] = []
    nueva_entrada = f"Frecuencia: {frecuencia} -> Lupa: {lupa}"
    if nueva_entrada.lower() not in [entry.lower() for entry in session["historial"]]:
        session["historial"].append(nueva_entrada)
    session.modified = True

    # Actualizar ranking basado en palabras encontradas
    if palabras_encontradas:
        print(f"Palabras encontradas para actualizar ranking: {palabras_encontradas}")
        for palabra in palabras_encontradas:
            if all(letra.isalpha() for letra in palabra):
                actualizar_ranking(palabra)
                print(f"Actualizando ranking para: {palabra.lower()}")
            else:
                print(f"Palabra ignorada por contener caracteres no válidos: {palabra}")
    else:
        print("No se encontraron palabras para actualizar ranking.")

    return render_template(
        "resultado.html",
        palabra=str(frecuencia),
        frecuencia=frecuencia,
        lupa=lupa,
        detalle=detalle,  # Mantener detalle
        territorios=territorios_encontrados,  # Mantener Resonancia Geográfica
        palabras=palabras_encontradas,  # Mantener Resonancias de Palabras Relacionadas
        elementos=elementos,  # Mantener Resonancia Elemental
        opcion=1,  # Identificar opción 1 en el template
    )


@app.route("/embed_page")
def embed_page():
    """
    Carga una página embebida con el historial del usuario.
    """
    print(
        "Historial desde /embed_page:", session.get("historial", [])
    )  # Log para verificar el historial
    historial = session.get("historial", [])
    return render_template("embed.html", historial=historial)


if __name__ == "__main__":
    print("Verificando e inicializando tablas...")
    with app.app_context():
        db.create_all()  # Crear todas las tablas definidas
        print("✅ Tablas creadas exitosamente en el contexto de Flask.")
    app.run(debug=False, host="0.0.0.0", port=8080)
