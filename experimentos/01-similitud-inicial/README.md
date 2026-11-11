# Experimento 01: similitud inicial

## Objetivo

Validar, antes de armar la base de datos y la API, que los embeddings de las sinopsis sirven para recomendar por trama. En concreto:

- comprobar que `intfloat/multilingual-e5-small` agrupa bien tramas parecidas, incluso entre películas y juegos;
- elegir el prefijo de e5 (`passage: ` + `query: ` contra `query: ` en todo);
- definir el reescalado del puntaje a partir de la distribución real de similitudes;
- medir la RAM que ocupa el modelo.

Todo corre en local, sin base de datos ni API.

## Set de títulos

Nueve títulos en tres grupos temáticos (dos películas y un juego por grupo) y dos títulos sin relación con ninguno, como control.

| id | título | año | tipo | grupo |
| --- | --- | --- | --- | --- |
| matrix-1999 | The Matrix | 1999 | movie | realidad_simulada |
| truman-show-1998 | The Truman Show | 1998 | movie | realidad_simulada |
| talos-principle-2014 | The Talos Principle | 2014 | game | realidad_simulada |
| the-road-2009 | The Road | 2009 | movie | supervivencia |
| children-of-men-2006 | Children of Men | 2006 | movie | supervivencia |
| last-of-us-2013 | The Last of Us | 2013 | game | supervivencia |
| alien-1979 | Alien | 1979 | movie | terror_espacial |
| event-horizon-1997 | Event Horizon | 1997 | movie | terror_espacial |
| dead-space-2008 | Dead Space | 2008 | game | terror_espacial |
| toy-story-1995 | Toy Story | 1995 | movie | sin_relacion |
| stardew-valley-2016 | Stardew Valley | 2016 | game | sin_relacion |

El grupo **no** se le manda a Gemini: solo id, título, año y tipo.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `titulos.json` | Los 11 títulos con su grupo. |
| `prompt_sinopsis.txt` | Prompt fijo para Gemini. `{TITULOS}` se reemplaza con una línea por título. |
| `generar_sinopsis.py` | Etapa 1: pide las sinopsis a Gemini en una sola solicitud (temperatura 0.2) y las guarda en `sinopsis.json`. |
| `prueba.py` | Etapa 2: genera los embeddings, corre el análisis y escribe `resultados.md`. |
| `.env.example` | Variables que necesita la etapa 1. |

## Cómo ejecutarlo

Desde esta carpeta:

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Etapa 1, generar las sinopsis (usa la clave de Gemini):

```bash
copy .env.example .env            # Linux/macOS: cp .env.example .env
# completar GEMINI_API_KEY y GEMINI_MODEL en .env
python generar_sinopsis.py        # agregar --forzar para regenerarlas
```

Etapa 2, el análisis:

```bash
python prueba.py
```

La primera vez descarga el modelo desde Hugging Face (unos 470 MB, queda en la caché del usuario, fuera del repo).

## Análisis

Todo se calcula dos veces, una por variante de prefijo, con `normalize_embeddings=True`:

- **Variante A:** `passage: ` delante de cada sinopsis y `query: ` delante de las búsquedas libres.
- **Variante B:** `query: ` delante de todo.

1. Matriz de similitud coseno entre todos los títulos.
2. Acierto top-2: para los 9 títulos con grupo temático, cuántos de sus 2 vecinos más cercanos son de su grupo (total sobre 18).
3. Separación: similitud media entre pares del mismo grupo temático contra la media del resto de los pares (el par Toy Story – Stardew Valley cuenta como "grupos distintos").
4. Juegos: si el vecino más cercano de cada juego es de su grupo o es otro juego de otro grupo.
5. Outliers: similitud máxima de Toy Story y de Stardew Valley con cualquier otro título.
6. Distribución: mínimo, p25, mediana, p75 y máximo de las similitudes entre pares distintos.
7. Búsquedas libres: top-3 para tres consultas en lenguaje natural.

También mide el RSS del proceso antes y después de cargar el modelo, y después de generar los embeddings.

## Resultados

> Pendiente: copiar acá el contenido de `resultados.md` después de correr `prueba.py`.

## Conclusiones

> **BORRADOR, para revisar.** Completar con los números de `resultados.md`.

- **Agrupamiento:** _¿El acierto top-2 se acerca a 18/18? ¿Qué títulos fallan y con quién se confunden?_
- **Películas y juegos:** _¿Los juegos encuentran primero a su grupo temático o tienden a juntarse con otros juegos? Si pasa lo segundo, el estilo de las sinopsis todavía delata el tipo._
- **Prefijo:** _Elegir la variante con mejor acierto top-2 y mayor diferencia de separación. Si empatan, preferir A, que es el uso recomendado de e5 para búsqueda asimétrica._
- **Reescalado del puntaje:** _Usar la distribución de pares: tomar algo cercano al p25 o a la mediana como 0 % y el máximo observado como 100 %, en lugar del rango 0,7–1,0 que propone hoy el README del proyecto._
- **Outliers:** _Si la similitud máxima de Toy Story y Stardew Valley queda cerca de la de pares del mismo grupo, el modelo no separa lo suficiente y el umbral para mostrar resultados tiene que ser más alto._
- **RAM:** _Anotar cuánto suma el modelo y si entra en el plan gratuito de Render (512 MB)._
