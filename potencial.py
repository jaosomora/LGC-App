import unicodedata
from collections import defaultdict
import os
import json
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

# Obtener la ruta del directorio donde está ubicado el script
directorio_base = os.path.dirname(os.path.abspath(__file__))

# Definir las rutas absolutas de los archivos
archivo_territorios = os.path.join(directorio_base, "territorios.json")  # Nuevo archivo para territorios
archivo_palabras = os.path.join(directorio_base, "palabras.txt")
archivo_ranking = os.path.join(directorio_base, "ranking.txt")
archivo_tabla_periodica = os.path.join(directorio_base, "tabla_periodica.json")

# Mapeo personalizado de valores de letras según la tabla
valores_letras = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "\u00d1": 15, "O": 16, "P": 17, "Q": 18,
    "R": 19, "S": 20, "T": 21, "U": 22, "V": 23, "W": 24, "X": 25, "Y": 26, "Z": 27
}

# Función para normalizar palabras (preservar espacios)
def normalizar_palabra_con_espacios(palabra):
    palabra = ''.join(
        char for char in unicodedata.normalize('NFD', palabra) 
        if unicodedata.category(char) != 'Mn'
    )
    palabra = ''.join(char for char in palabra.upper() if char in valores_letras or char == " ")
    return palabra

# Función para calcular el potencial
def calcular_potencial(palabra):
    palabra_normalizada = normalizar_palabra_con_espacios(palabra)
    return sum(valores_letras[letra] for letra in palabra_normalizada if letra != " ")

# Función para calcular el detalle del potencial
def detalle_potencial(palabra):
    palabra_normalizada = normalizar_palabra_con_espacios(palabra)
    valores = [valores_letras[letra] for letra in palabra_normalizada if letra != " "]
    return valores

# Función para calcular la Lupa
def calcular_lupa(potencial):
    return round(potencial * 1.21, 2)

# Función para actualizar palabras nuevas
def actualizar_palabras(archivo, palabra):
    try:
        with open(archivo, "r+", encoding="utf-8") as f:
            palabras = [linea.strip() for linea in f.readlines()]
            if palabra not in palabras:  # Comparar con el formato original (preservar espacios)
                f.write(palabra + "\n")
    except FileNotFoundError:
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(palabra + "\n")

# Cargar datos de la tabla periódica
def cargar_tabla_periodica(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}\u2718 El archivo '{archivo}' no existe.")
        return []

# Función para buscar elementos químicos por potencial
def buscar_elementos_por_potencial(tabla_periodica, potencial_objetivo, lupa_objetivo=None):
    resultados = []
    for elemento in tabla_periodica:
        nombre = elemento["nombre"]
        simbolo = elemento["simbolo"]
        numero_atomico = elemento["numero_atomico"]
        masa = elemento["masa"]
        potencial_nombre = calcular_potencial(nombre)
        potencial_simbolo = calcular_potencial(simbolo)

        # Coincidencias por potencial calculado (nombre o símbolo)
        if potencial_nombre == potencial_objetivo:
            tipo_coincidencia = f"nombre (potencial del nombre: {potencial_nombre})"
            resultados.append((elemento, tipo_coincidencia))
        elif potencial_simbolo == potencial_objetivo:
            tipo_coincidencia = f"símbolo (potencial del símbolo: {potencial_simbolo})"
            resultados.append((elemento, tipo_coincidencia))
        # Coincidencias por lupa
        elif lupa_objetivo and round(potencial_nombre * 1.21, 2) == lupa_objetivo:
            tipo_coincidencia = f"lupa del nombre ({lupa_objetivo})"
            resultados.append((elemento, tipo_coincidencia))
        elif lupa_objetivo and round(potencial_simbolo * 1.21, 2) == lupa_objetivo:
            tipo_coincidencia = f"lupa del símbolo ({lupa_objetivo})"
            resultados.append((elemento, tipo_coincidencia))
        # Coincidencias directas con propiedades de la tabla periódica
        elif numero_atomico == potencial_objetivo:
            tipo_coincidencia = f"número atómico ({numero_atomico})"
            resultados.append((elemento, tipo_coincidencia))
        elif round(masa, 2) == round(potencial_objetivo, 2):
            tipo_coincidencia = f"masa atómica ({masa})"
            resultados.append((elemento, tipo_coincidencia))
    return resultados

# Función para buscar palabras con el mismo potencial
def buscar_palabras_por_potencial(archivo, archivo_ranking, potencial_objetivo, palabra_ingresada=None):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            palabras = [linea.strip() for linea in f.readlines()]
        palabras_unicas = set(palabras)
        resultados_normalizados = {
            normalizar_palabra_con_espacios(palabra): palabra for palabra in palabras_unicas
        }
        resultados = [
            resultados_normalizados[normalizada] 
            for normalizada in resultados_normalizados
            if calcular_potencial(normalizada) == potencial_objetivo
        ]
        if palabra_ingresada:
            palabra_ingresada_normalizada = normalizar_palabra_con_espacios(palabra_ingresada)
            resultados = [
                palabra for palabra in resultados 
                if normalizar_palabra_con_espacios(palabra) != palabra_ingresada_normalizada
            ]
        return resultados
    except FileNotFoundError:
        print(f"{Fore.RED}\u2718 El archivo '{archivo}' no existe.")
        return []
    except KeyError as e:
        print(f"{Fore.RED}\u2718 Letra no reconocida en la base de datos: {e}")
        return []

# Cargar códigos de territorios desde archivo JSON
def cargar_codigos_territorios(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}\u2718 El archivo '{archivo}' no existe.")
        return []
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}\u2718 Error al cargar el archivo de territorios: {e}")
        return []

# Función para buscar códigos telefónicos, incluyendo normalización
def buscar_codigo_territorio(codigos, valor_objetivo):
    resultados = []
    valor_objetivo = str(valor_objetivo)  # Convertir el valor ingresado a cadena para comparaciones
    for territorio in codigos:
        codigo_normalizado = str(territorio["codigo"]).split("-")[-1]  # Tomar la parte final del código
        if codigo_normalizado == valor_objetivo:  # Comparar con el valor objetivo
            resultados.append(territorio)
    return resultados

# Menú principal
def menu_principal():
    tabla_periodica = cargar_tabla_periodica(archivo_tabla_periodica)
    try:
        territorios = cargar_codigos_territorios(archivo_territorios)  # Cargar territorios
        if not territorios:
            raise ValueError("Territorios no cargados correctamente.")
    except Exception as e:
        print(f"{Fore.RED}\u2718 Error al inicializar territorios: {e}")
        territorios = []

    while True:
        print(f"\n{Fore.BLUE}==============================")
        print(f"{Fore.CYAN}          INTERFAZ LGC")
        print(f"{Fore.BLUE}==============================")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Calcular Palabras por Frecuencia Numérica")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Calcular Frecuencia de una Palabra")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Salir")
        print(f"{Fore.BLUE}==============================")
        
        opcion = input("Selecciona una opción (1/2/3): ")
        
        if opcion == "1":
            print(f"\n{Fore.GREEN}--- BÚSQUEDA POR FRECUENCIA ---")
            try:
                potencial_objetivo = int(input("Ingresa la frecuencia (potencial): "))
                lupa_objetivo = calcular_lupa(potencial_objetivo)  # Calcular la Lupa del potencial
                palabras_resultados = buscar_palabras_por_potencial(archivo_palabras, archivo_ranking, potencial_objetivo)
                elementos_resultados = buscar_elementos_por_potencial(tabla_periodica, potencial_objetivo, lupa_objetivo)
                
                print(f"\n{Fore.BLUE}**Resultado: Frecuencia {potencial_objetivo}**")
                print(f"{Fore.BLUE}-------------------------------")
                
                # Mostrar la Lupa
                print(f"\n{Fore.MAGENTA}**Valor con Lupa (1.21x)**:")
                print(f"   - {lupa_objetivo}")
                
                # Mostrar palabras con el mismo potencial
                print(f"\n{Fore.MAGENTA}**Palabras asociadas a la Frecuencia**:")
                if palabras_resultados:
                    for palabra in palabras_resultados:
                        print(f"   - {palabra}")
                else:
                    print(f"   {Fore.RED}\u2718 No se encontraron palabras con esa frecuencia.")
                
                # Buscar coincidencias con códigos de territorio
                print(f"\n{Fore.MAGENTA}**Resonancia Geográfica**:")
                territorios_encontrados = buscar_codigo_territorio(territorios, potencial_objetivo)
                if territorios_encontrados:
                    for territorio in territorios_encontrados:
                        print(f"   - Código Territorial: +{territorio['codigo']} ({territorio['pais']})")
                else:
                    print(f"   {Fore.RED}\u2718 No se encontraron coincidencias geográficas.")
                
                # Mostrar elementos químicos encontrados
                print(f"\n{Fore.MAGENTA}**Resonancia Elemental**:")
                if elementos_resultados:
                    for elemento, tipo_coincidencia in elementos_resultados:
                        print(f"   - Elemento: {elemento['nombre']} ({elemento['simbolo']})")
                        print(f"     - Número Atómico: {elemento['numero_atomico']}")
                        print(f"     - Masa: {elemento['masa']}")
                        print(f"     - Coincidencia: {tipo_coincidencia}")
                else:
                    print(f"   {Fore.RED}\u2718 No se encontraron elementos químicos asociados.")
            except ValueError:
                print(f"{Fore.RED}\u2718 Por favor, ingresa un número válido.")
        
        elif opcion == "2":
            print(f"\n{Fore.GREEN}--- CÁLCULO DE FRECUENCIA ---")
            palabra = input("Ingresa la palabra o frase: ").strip()
            if palabra.isdigit():  # Validar si la entrada es un número
                print(f"{Fore.RED}\u2718 Por favor, ingresa una palabra o frase, no un número.")
                continue
            if palabra:
                potencial = calcular_potencial(palabra)
                lupa = calcular_lupa(potencial)
                valores = detalle_potencial(palabra)
                
                print(f"\n{Fore.BLUE}**Resultado: {palabra}**")
                print(f"{Fore.BLUE}-------------------------------")
                
                # Mostrar detalle del potencial
                print(f"\n{Fore.MAGENTA}**Detalle del Potencial**:")
                print(f"   - Valores: {valores}")
                print(f"   - Suma Total: {potencial}")
                
                # Mostrar la Lupa
                print(f"\n{Fore.MAGENTA}**Valor con Lupa (1.21x)**:")
                print(f"   - {lupa}")
                
                # Guardar la palabra original
                actualizar_palabras(archivo_palabras, palabra)
                
                # Mostrar palabras relacionadas
                print(f"\n{Fore.MAGENTA}**Palabras asociadas a la Frecuencia**:")
                resultados = buscar_palabras_por_potencial(archivo_palabras, archivo_ranking, potencial, palabra)
                if resultados:
                    for palabra_relacionada in resultados:
                        print(f"   - {palabra_relacionada}")
                else:
                    print(f"   {Fore.RED}\u2718 No se encontraron palabras relacionadas.")
                
                # Buscar coincidencias con códigos de territorio
                print(f"\n{Fore.MAGENTA}**Resonancia Geográfica**:")
                territorios_encontrados = buscar_codigo_territorio(territorios, potencial)
                if territorios_encontrados:
                    for territorio in territorios_encontrados:
                        print(f"   - Código Territorial: +{territorio['codigo']} ({territorio['pais']})")
                else:
                    print(f"   {Fore.RED}\u2718 No se encontraron coincidencias geográficas.")
                
                # Buscar coincidencias con la tabla periódica
                print(f"\n{Fore.MAGENTA}**Resonancia Elemental**:")
                elementos_resultados = buscar_elementos_por_potencial(tabla_periodica, potencial, lupa)
                if elementos_resultados:
                    for elemento, tipo_coincidencia in elementos_resultados:
                        print(f"   - Elemento: {elemento['nombre']} ({elemento['simbolo']})")
                        print(f"     - Número Atómico: {elemento['numero_atomico']}")
                        print(f"     - Masa: {elemento['masa']}")
                        print(f"     - Coincidencia: {tipo_coincidencia}")
                else:
                    print(f"   {Fore.RED}\u2718 No se encontraron elementos químicos asociados.")
            else:
                print(f"{Fore.RED}\u2718 Por favor, ingresa una palabra válida.")
        elif opcion == "3":
            print(f"\n{Fore.GREEN}\u00a1Gracias por usar el programa! [FINALIZADO]")
            break
        else:
            print(f"{Fore.RED}\u2718 Opción no válida. Por favor, selecciona 1, 2 o 3.")

# Ejecutar el programa
menu_principal()