"""Prueba de similitud entre películas y juegos con embeddings de sus sinopsis.

Lee titulos.json y sinopsis.json, corre el análisis con dos variantes de
prefijo de e5 y escribe los resultados en consola y en resultados.md.
"""

import json
from pathlib import Path

import numpy as np
import psutil

CARPETA = Path(__file__).parent
ARCHIVO_TITULOS = CARPETA / "titulos.json"
ARCHIVO_SINOPSIS = CARPETA / "sinopsis.json"
ARCHIVO_RESULTADOS = CARPETA / "resultados.md"
ARCHIVO_SINOPSIS_MD = CARPETA / "sinopsis.md"

MODELO = "intfloat/multilingual-e5-small"
SIN_GRUPO = "sin_relacion"
OUTLIERS = ["toy-story-1995", "stardew-valley-2016"]
CONSULTAS = [
    "a man discovers his whole life is fake",
    "a father protects his son in a dying world",
    "crew members hunted by a creature on a spaceship",
]
# C usa los prefijos de A, pero le resta a cada vector el promedio de las
# sinopsis del catálogo (centrado) y lo vuelve a normalizar.
VARIANTES = {
    "A": {"pasaje": "passage: ", "consulta": "query: ", "centrar": False},
    "B": {"pasaje": "query: ", "consulta": "query: ", "centrar": False},
    "C": {"pasaje": "passage: ", "consulta": "query: ", "centrar": True},
}

lineas_salida = []


def escribir(texto=""):
    print(texto)
    lineas_salida.append(texto)


def tabla(encabezados, filas):
    escribir("| " + " | ".join(encabezados) + " |")
    escribir("| " + " | ".join("---" for _ in encabezados) + " |")
    for fila in filas:
        escribir("| " + " | ".join(str(celda) for celda in fila) + " |")
    escribir()


def ram_mb():
    return psutil.Process().memory_info().rss / 1024**2


def f(numero):
    return f"{numero:.3f}"


# --- Datos -------------------------------------------------------------------

ram_inicio = ram_mb()

titulos = json.loads(ARCHIVO_TITULOS.read_text(encoding="utf-8"))
sinopsis_por_id = {
    s["id"]: (s.get("synopsis") or "").strip()
    for s in json.loads(ARCHIVO_SINOPSIS.read_text(encoding="utf-8"))
}

descartados = [t for t in titulos if sinopsis_por_id.get(t["id"], "").lower() in ("", "unknown")]
for t in descartados:
    print(f"Aviso: se descarta {t['titulo']} ({t['id']}): sinopsis 'unknown' o ausente")
items = [t for t in titulos if t not in descartados]
for t in items:
    t["sinopsis"] = sinopsis_por_id[t["id"]]

ids = [t["id"] for t in items]
grupos = [t["grupo"] for t in items]
n = len(items)

# Copia legible de lo que devolvió Gemini, para revisar las sinopsis a mano.
lineas_sinopsis = ["# Sinopsis generadas por Gemini", ""]
for t in titulos:
    texto = sinopsis_por_id.get(t["id"]) or "(ausente)"
    lineas_sinopsis += [f"## {t['titulo']} ({t['anio']}, {t['tipo']})", "",
                        f"`{t['id']}` · grupo: {t['grupo']} · {len(texto.split())} palabras", "",
                        texto, ""]
ARCHIVO_SINOPSIS_MD.write_text("\n".join(lineas_sinopsis), encoding="utf-8")

# --- Modelo ------------------------------------------------------------------

from sentence_transformers import SentenceTransformer  # noqa: E402 (se importa acá para medir la RAM)

ram_antes_modelo = ram_mb()
modelo = SentenceTransformer(MODELO, device="cpu")
ram_despues_modelo = ram_mb()


def vectorizar(textos):
    return modelo.encode(textos, normalize_embeddings=True, convert_to_numpy=True)


def normalizar(vectores):
    return vectores / np.linalg.norm(vectores, axis=-1, keepdims=True)


# --- Análisis por variante ---------------------------------------------------

escribir("# Resultados: similitud inicial")
escribir()
escribir(f"Modelo: `{MODELO}`. Títulos analizados: {n} de {len(titulos)}.")
if descartados:
    escribir(f"Descartados por sinopsis 'unknown': {', '.join(t['id'] for t in descartados)}.")
escribir()

resumen = []

for nombre, prefijos in VARIANTES.items():
    escribir(f"## Variante {nombre}")
    escribir()
    escribir(f"Prefijo de sinopsis: `{prefijos['pasaje']}` · "
             f"prefijo de búsquedas libres: `{prefijos['consulta']}` · "
             f"centrado: {'sí' if prefijos['centrar'] else 'no'}")
    escribir()

    vectores = vectorizar([prefijos["pasaje"] + t["sinopsis"] for t in items])
    # Centrado: el promedio del catálogo es lo que todas las sinopsis tienen en
    # común. Restarlo deja solo lo propio de cada una. Las búsquedas libres se
    # centran con el mismo promedio, para que queden en el mismo espacio.
    media = vectores.mean(axis=0) if prefijos["centrar"] else 0
    vectores = normalizar(vectores - media)
    sim = vectores @ vectores.T
    # Vecinos de cada título ordenados de mayor a menor similitud, sin él mismo.
    vecinos = [[j for j in np.argsort(-sim[i]) if j != i] for i in range(n)]

    # 1. Matriz de similitud
    escribir("### 1. Matriz de similitud")
    escribir()
    tabla([""] + ids, [[ids[i]] + [f(sim[i, j]) for j in range(n)] for i in range(n)])

    # 2. Acierto top-2
    escribir("### 2. Acierto top-2")
    escribir()
    filas = []
    aciertos = 0
    posibles = 0
    for i in range(n):
        if grupos[i] == SIN_GRUPO:
            continue
        top2 = vecinos[i][:2]
        acierto = sum(grupos[j] == grupos[i] for j in top2)
        aciertos += acierto
        posibles += 2
        filas.append([ids[i], grupos[i]]
                     + [f"{ids[j]} ({f(sim[i, j])})" for j in top2] + [f"{acierto}/2"])
    tabla(["título", "grupo", "vecino 1", "vecino 2", "aciertos"], filas)
    escribir(f"**Total: {aciertos}/{posibles}**")
    escribir()

    # 3. Separación
    # "Mismo grupo": pares del mismo grupo temático. Todo lo demás cuenta como
    # "grupos distintos", incluido el par Toy Story – Stardew Valley.
    dentro, entre = [], []
    for i in range(n):
        for j in range(i + 1, n):
            mismo = grupos[i] == grupos[j] and grupos[i] != SIN_GRUPO
            (dentro if mismo else entre).append(sim[i, j])
    media_dentro = float(np.mean(dentro))
    media_entre = float(np.mean(entre))
    escribir("### 3. Separación")
    escribir()
    tabla(["media mismo grupo", "media grupos distintos", "diferencia"],
          [[f(media_dentro), f(media_entre), f(media_dentro - media_entre)]])

    # 4. Juegos
    escribir("### 4. Vecino más cercano de cada juego")
    escribir()
    filas = []
    for i in range(n):
        if items[i]["tipo"] != "game":
            continue
        j = vecinos[i][0]
        if grupos[i] != SIN_GRUPO and grupos[j] == grupos[i]:
            veredicto = "mismo grupo"
        elif items[j]["tipo"] == "game":
            veredicto = "otro juego de otro grupo"
        else:
            veredicto = "película de otro grupo"
        filas.append([ids[i], grupos[i], ids[j], f(sim[i, j]), veredicto])
    tabla(["juego", "grupo", "vecino más cercano", "similitud", "resultado"], filas)

    # 5. Outliers
    escribir("### 5. Outliers")
    escribir()
    filas = []
    for id_outlier in OUTLIERS:
        if id_outlier not in ids:
            continue
        i = ids.index(id_outlier)
        j = vecinos[i][0]
        filas.append([id_outlier, f(sim[i, j]), ids[j]])
    tabla(["título", "similitud máxima", "con"], filas)

    # 6. Distribución
    pares = sim[np.triu_indices(n, k=1)]
    escribir("### 6. Distribución de similitudes entre pares distintos")
    escribir()
    tabla(["mínimo", "p25", "mediana", "p75", "máximo"],
          [[f(np.min(pares)), f(np.percentile(pares, 25)), f(np.median(pares)),
            f(np.percentile(pares, 75)), f(np.max(pares))]])

    # 7. Búsquedas libres
    escribir("### 7. Búsquedas libres (top-3)")
    escribir()
    vectores_consultas = normalizar(
        vectorizar([prefijos["consulta"] + c for c in CONSULTAS]) - media)
    filas = []
    for consulta, vector in zip(CONSULTAS, vectores_consultas, strict=True):
        sim_consulta = vectores @ vector
        top3 = np.argsort(-sim_consulta)[:3]
        filas.append([f'"{consulta}"'] + [f"{ids[j]} ({f(sim_consulta[j])})" for j in top3])
    tabla(["consulta", "1°", "2°", "3°"], filas)

    resumen.append([nombre, f"{aciertos}/{posibles}", f(media_dentro), f(media_entre),
                    f(media_dentro - media_entre)])

ram_despues_embeddings = ram_mb()

# --- RAM y comparación final -------------------------------------------------

escribir("## RAM del proceso (RSS)")
escribir()
tabla(["momento", "MB"], [
    ["inicio del script", f"{ram_inicio:.0f}"],
    ["antes de cargar el modelo (con librerías importadas)", f"{ram_antes_modelo:.0f}"],
    ["después de cargar el modelo", f"{ram_despues_modelo:.0f}"],
    ["después de generar los embeddings", f"{ram_despues_embeddings:.0f}"],
])
escribir(f"Carga del modelo: +{ram_despues_modelo - ram_antes_modelo:.0f} MB. "
         f"Total desde el inicio: +{ram_despues_embeddings - ram_inicio:.0f} MB.")
escribir()

escribir("## Comparación de variantes")
escribir()
tabla(["variante", "acierto top-2", "media mismo grupo", "media grupos distintos",
       "diferencia"], resumen)

ARCHIVO_RESULTADOS.write_text("\n".join(lineas_salida), encoding="utf-8")
print(f"Resultados guardados en {ARCHIVO_RESULTADOS.name}")
