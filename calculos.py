"""
calculos.py — Lógica matemática pura para Interfaz LGC.
Sin dependencias de Flask. Solo Python estándar.
"""
import unicodedata

VALORES_LETRAS = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
    "I": 9, "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "Ñ": 15,
    "O": 16, "P": 17, "Q": 18, "R": 19, "S": 20, "T": 21, "U": 22,
    "V": 23, "W": 24, "X": 25, "Y": 26, "Z": 27,
}


def normalizar(palabra):
    """Normaliza texto: minúsculas, conserva ñ, elimina tildes, colapsa espacios."""
    palabra = " ".join(palabra.strip().split()).lower()
    protegida = palabra.replace("ñ", "__Ñ__")
    limpia = "".join(
        c for c in unicodedata.normalize("NFD", protegida)
        if unicodedata.category(c) != "Mn"
    )
    return limpia.replace("__Ñ__", "ñ")


def es_valida(texto):
    """Verifica que el texto solo contenga letras y espacios."""
    return all(c.isalpha() or c.isspace() for c in texto) and len(texto.strip()) > 0


def calcular_potencial(palabra):
    """Suma los valores numéricos de cada letra."""
    texto = normalizar(palabra).upper()
    return sum(VALORES_LETRAS.get(c, 0) for c in texto if c.isalpha())


def calcular_lupa(potencial):
    """Potencial amplificado × 1.21."""
    return round(potencial * 1.21, 2)


def detalle_potencial(palabra):
    """Lista de {letra, valor} para cada carácter alfabético."""
    texto = normalizar(palabra).upper()
    return [
        {"letra": c, "valor": VALORES_LETRAS.get(c, 0)}
        for c in texto if c.isalpha()
    ]


def desglose_por_palabra(frase):
    """Desglose letra por letra para cada palabra en una frase.
    Retorna lista de {palabra, letras: [{letra, valor}], suma}."""
    palabras = frase.split()
    resultado = []
    for palabra in palabras:
        norm = normalizar(palabra).upper()
        letras = [
            {"letra": c, "valor": VALORES_LETRAS.get(c, 0)}
            for c in norm if c.isalpha()
        ]
        resultado.append({
            "palabra": palabra,
            "letras": letras,
            "suma": sum(l["valor"] for l in letras),
        })
    return resultado


def invertir_numero(n):
    """Invierte los dígitos de un número: 123 → 321."""
    return int(str(abs(int(n)))[::-1])


def buscar_codigo_territorio(codigos, valor_objetivo):
    """Busca territorios cuyo código coincida con el valor."""
    valor_str = str(valor_objetivo)
    return [
        t for t in codigos
        if str(t["codigo"]).split("-")[-1] == valor_str
    ]


def buscar_elementos_por_potencial(tabla_periodica, potencial_objetivo):
    """Busca elementos por potencial del nombre o número atómico."""
    resultados = []
    for elem in tabla_periodica:
        pot_nombre = calcular_potencial(elem["nombre"])
        if pot_nombre == potencial_objetivo:
            resultados.append({
                "nombre": elem["nombre"],
                "simbolo": elem["simbolo"],
                "numero_atomico": elem["numero_atomico"],
                "masa": elem["masa"],
                "tipo_coincidencia": "potencial_nombre",
                "valor_coincidencia": pot_nombre,
            })
        elif elem["numero_atomico"] == potencial_objetivo:
            resultados.append({
                "nombre": elem["nombre"],
                "simbolo": elem["simbolo"],
                "numero_atomico": elem["numero_atomico"],
                "masa": elem["masa"],
                "tipo_coincidencia": "numero_atomico",
                "valor_coincidencia": elem["numero_atomico"],
            })
    return resultados


def buscar_palabras_por_potencial(palabras, potencial_objetivo):
    """Encuentra palabras cuyo potencial coincida con el objetivo."""
    return [p for p in palabras if calcular_potencial(p) == potencial_objetivo]
