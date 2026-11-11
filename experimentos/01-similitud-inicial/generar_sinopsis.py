"""Genera las sinopsis de los títulos con Gemini y las guarda en sinopsis.json.

Uso:
    python generar_sinopsis.py            # no llama a la API si sinopsis.json ya existe
    python generar_sinopsis.py --forzar   # vuelve a generarlas
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

CARPETA = Path(__file__).parent
ARCHIVO_TITULOS = CARPETA / "titulos.json"
ARCHIVO_PROMPT = CARPETA / "prompt_sinopsis.txt"
ARCHIVO_SALIDA = CARPETA / "sinopsis.json"
TEMPERATURA = 0.2


def main():
    forzar = "--forzar" in sys.argv[1:]
    if ARCHIVO_SALIDA.exists() and not forzar:
        print(f"{ARCHIVO_SALIDA.name} ya existe. Usá --forzar para volver a generarlo.")
        return

    load_dotenv(CARPETA / ".env")
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    modelo = os.getenv("GEMINI_MODEL", "").strip()
    faltantes = [nombre for nombre, valor in
                 [("GEMINI_API_KEY", api_key), ("GEMINI_MODEL", modelo)] if not valor]
    if faltantes:
        sys.exit(f"Error: faltan variables en {CARPETA / '.env'}: {', '.join(faltantes)}")

    titulos = json.loads(ARCHIVO_TITULOS.read_text(encoding="utf-8"))
    # Al modelo solo se le mandan id, título, año y tipo. Nunca el grupo.
    lineas = [f"- id: {t['id']} | {t['titulo']} | {t['anio']} | {t['tipo']}" for t in titulos]
    prompt = ARCHIVO_PROMPT.read_text(encoding="utf-8").replace("{TITULOS}", "\n".join(lineas))

    print(f"Pidiendo {len(titulos)} sinopsis a {modelo}...")
    cliente = genai.Client(api_key=api_key)
    respuesta = cliente.models.generate_content(
        model=modelo,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=TEMPERATURA,
            response_mime_type="application/json",
        ),
    )

    texto = (respuesta.text or "").strip()
    # Por si el modelo igual envuelve la respuesta en un bloque de markdown.
    if texto.startswith("```"):
        texto = texto.strip("`").removeprefix("json").strip()
    try:
        sinopsis = json.loads(texto)
    except json.JSONDecodeError:
        sys.exit(f"Error: la respuesta no es JSON válido:\n{texto}")
    if not isinstance(sinopsis, list):
        sys.exit(f"Error: se esperaba un array JSON y llegó:\n{texto}")

    ids_pedidos = {t["id"] for t in titulos}
    ids_recibidos = {s.get("id") for s in sinopsis}
    if ids_pedidos - ids_recibidos:
        print(f"Aviso: faltan sinopsis para: {', '.join(sorted(ids_pedidos - ids_recibidos))}")
    if ids_recibidos - ids_pedidos:
        print(f"Aviso: ids inesperados: {', '.join(sorted(map(str, ids_recibidos - ids_pedidos)))}")

    ARCHIVO_SALIDA.write_text(
        json.dumps(sinopsis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Guardadas {len(sinopsis)} sinopsis en {ARCHIVO_SALIDA.name}")


if __name__ == "__main__":
    main()
