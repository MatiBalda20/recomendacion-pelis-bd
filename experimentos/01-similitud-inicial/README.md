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
python generar_sinopsis.py --modelos   # lista los modelos disponibles para la clave
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

Copia de `resultados.md` de la corrida del 11/11/2026.

Modelo: `intfloat/multilingual-e5-small`. Títulos analizados: 11 de 11.

### Variante A

Prefijo de sinopsis: `passage: ` · prefijo de búsquedas libres: `query: `

#### 1. Matriz de similitud

|  | matrix-1999 | truman-show-1998 | talos-principle-2014 | the-road-2009 | children-of-men-2006 | last-of-us-2013 | alien-1979 | event-horizon-1997 | dead-space-2008 | toy-story-1995 | stardew-valley-2016 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| matrix-1999 | 1.000 | 0.839 | 0.852 | 0.824 | 0.843 | 0.828 | 0.854 | 0.811 | 0.832 | 0.828 | 0.812 |
| truman-show-1998 | 0.839 | 1.000 | 0.825 | 0.822 | 0.822 | 0.817 | 0.822 | 0.797 | 0.818 | 0.823 | 0.838 |
| talos-principle-2014 | 0.852 | 0.825 | 1.000 | 0.828 | 0.826 | 0.829 | 0.834 | 0.826 | 0.827 | 0.812 | 0.824 |
| the-road-2009 | 0.824 | 0.822 | 0.828 | 1.000 | 0.859 | 0.847 | 0.837 | 0.814 | 0.823 | 0.811 | 0.848 |
| children-of-men-2006 | 0.843 | 0.822 | 0.826 | 0.859 | 1.000 | 0.862 | 0.834 | 0.798 | 0.807 | 0.813 | 0.834 |
| last-of-us-2013 | 0.828 | 0.817 | 0.829 | 0.847 | 0.862 | 1.000 | 0.847 | 0.827 | 0.847 | 0.817 | 0.818 |
| alien-1979 | 0.854 | 0.822 | 0.834 | 0.837 | 0.834 | 0.847 | 1.000 | 0.875 | 0.870 | 0.827 | 0.820 |
| event-horizon-1997 | 0.811 | 0.797 | 0.826 | 0.814 | 0.798 | 0.827 | 0.875 | 1.000 | 0.866 | 0.810 | 0.793 |
| dead-space-2008 | 0.832 | 0.818 | 0.827 | 0.823 | 0.807 | 0.847 | 0.870 | 0.866 | 1.000 | 0.812 | 0.809 |
| toy-story-1995 | 0.828 | 0.823 | 0.812 | 0.811 | 0.813 | 0.817 | 0.827 | 0.810 | 0.812 | 1.000 | 0.798 |
| stardew-valley-2016 | 0.812 | 0.838 | 0.824 | 0.848 | 0.834 | 0.818 | 0.820 | 0.793 | 0.809 | 0.798 | 1.000 |

#### 2. Acierto top-2

| título | grupo | vecino 1 | vecino 2 | aciertos |
| --- | --- | --- | --- | --- |
| matrix-1999 | realidad_simulada | alien-1979 (0.854) | talos-principle-2014 (0.852) | 1/2 |
| truman-show-1998 | realidad_simulada | matrix-1999 (0.839) | stardew-valley-2016 (0.838) | 1/2 |
| talos-principle-2014 | realidad_simulada | matrix-1999 (0.852) | alien-1979 (0.834) | 1/2 |
| the-road-2009 | supervivencia | children-of-men-2006 (0.859) | stardew-valley-2016 (0.848) | 1/2 |
| children-of-men-2006 | supervivencia | last-of-us-2013 (0.862) | the-road-2009 (0.859) | 2/2 |
| last-of-us-2013 | supervivencia | children-of-men-2006 (0.862) | alien-1979 (0.847) | 1/2 |
| alien-1979 | terror_espacial | event-horizon-1997 (0.875) | dead-space-2008 (0.870) | 2/2 |
| event-horizon-1997 | terror_espacial | alien-1979 (0.875) | dead-space-2008 (0.866) | 2/2 |
| dead-space-2008 | terror_espacial | alien-1979 (0.870) | event-horizon-1997 (0.866) | 2/2 |

**Total: 13/18**

#### 3. Separación

| media mismo grupo | media grupos distintos | diferencia |
| --- | --- | --- |
| 0.855 | 0.823 | 0.032 |

#### 4. Vecino más cercano de cada juego

| juego | grupo | vecino más cercano | similitud | resultado |
| --- | --- | --- | --- | --- |
| talos-principle-2014 | realidad_simulada | matrix-1999 | 0.852 | mismo grupo |
| last-of-us-2013 | supervivencia | children-of-men-2006 | 0.862 | mismo grupo |
| dead-space-2008 | terror_espacial | alien-1979 | 0.870 | mismo grupo |
| stardew-valley-2016 | sin_relacion | the-road-2009 | 0.848 | película de otro grupo |

#### 5. Outliers

| título | similitud máxima | con |
| --- | --- | --- |
| toy-story-1995 | 0.828 | matrix-1999 |
| stardew-valley-2016 | 0.848 | the-road-2009 |

#### 6. Distribución de similitudes entre pares distintos

| mínimo | p25 | mediana | p75 | máximo |
| --- | --- | --- | --- | --- |
| 0.793 | 0.815 | 0.826 | 0.838 | 0.875 |

#### 7. Búsquedas libres (top-3)

| consulta | 1° | 2° | 3° |
| --- | --- | --- | --- |
| "a man discovers his whole life is fake" | truman-show-1998 (0.822) | the-road-2009 (0.803) | matrix-1999 (0.792) |
| "a father protects his son in a dying world" | the-road-2009 (0.881) | children-of-men-2006 (0.828) | stardew-valley-2016 (0.810) |
| "crew members hunted by a creature on a spaceship" | alien-1979 (0.866) | event-horizon-1997 (0.840) | dead-space-2008 (0.832) |

### Variante B

Prefijo de sinopsis: `query: ` · prefijo de búsquedas libres: `query: `

#### 1. Matriz de similitud

|  | matrix-1999 | truman-show-1998 | talos-principle-2014 | the-road-2009 | children-of-men-2006 | last-of-us-2013 | alien-1979 | event-horizon-1997 | dead-space-2008 | toy-story-1995 | stardew-valley-2016 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| matrix-1999 | 1.000 | 0.849 | 0.864 | 0.834 | 0.846 | 0.833 | 0.863 | 0.829 | 0.840 | 0.833 | 0.830 |
| truman-show-1998 | 0.849 | 1.000 | 0.838 | 0.831 | 0.832 | 0.827 | 0.837 | 0.818 | 0.828 | 0.834 | 0.851 |
| talos-principle-2014 | 0.864 | 0.838 | 1.000 | 0.833 | 0.835 | 0.834 | 0.848 | 0.841 | 0.836 | 0.824 | 0.834 |
| the-road-2009 | 0.834 | 0.831 | 0.833 | 1.000 | 0.862 | 0.850 | 0.842 | 0.826 | 0.830 | 0.817 | 0.855 |
| children-of-men-2006 | 0.846 | 0.832 | 0.835 | 0.862 | 1.000 | 0.868 | 0.847 | 0.816 | 0.821 | 0.824 | 0.848 |
| last-of-us-2013 | 0.833 | 0.827 | 0.834 | 0.850 | 0.868 | 1.000 | 0.855 | 0.838 | 0.846 | 0.829 | 0.831 |
| alien-1979 | 0.863 | 0.837 | 0.848 | 0.842 | 0.847 | 0.855 | 1.000 | 0.890 | 0.877 | 0.836 | 0.843 |
| event-horizon-1997 | 0.829 | 0.818 | 0.841 | 0.826 | 0.816 | 0.838 | 0.890 | 1.000 | 0.875 | 0.828 | 0.818 |
| dead-space-2008 | 0.840 | 0.828 | 0.836 | 0.830 | 0.821 | 0.846 | 0.877 | 0.875 | 1.000 | 0.822 | 0.825 |
| toy-story-1995 | 0.833 | 0.834 | 0.824 | 0.817 | 0.824 | 0.829 | 0.836 | 0.828 | 0.822 | 1.000 | 0.817 |
| stardew-valley-2016 | 0.830 | 0.851 | 0.834 | 0.855 | 0.848 | 0.831 | 0.843 | 0.818 | 0.825 | 0.817 | 1.000 |

#### 2. Acierto top-2

| título | grupo | vecino 1 | vecino 2 | aciertos |
| --- | --- | --- | --- | --- |
| matrix-1999 | realidad_simulada | talos-principle-2014 (0.864) | alien-1979 (0.863) | 1/2 |
| truman-show-1998 | realidad_simulada | stardew-valley-2016 (0.851) | matrix-1999 (0.849) | 1/2 |
| talos-principle-2014 | realidad_simulada | matrix-1999 (0.864) | alien-1979 (0.848) | 1/2 |
| the-road-2009 | supervivencia | children-of-men-2006 (0.862) | stardew-valley-2016 (0.855) | 1/2 |
| children-of-men-2006 | supervivencia | last-of-us-2013 (0.868) | the-road-2009 (0.862) | 2/2 |
| last-of-us-2013 | supervivencia | children-of-men-2006 (0.868) | alien-1979 (0.855) | 1/2 |
| alien-1979 | terror_espacial | event-horizon-1997 (0.890) | dead-space-2008 (0.877) | 2/2 |
| event-horizon-1997 | terror_espacial | alien-1979 (0.890) | dead-space-2008 (0.875) | 2/2 |
| dead-space-2008 | terror_espacial | alien-1979 (0.877) | event-horizon-1997 (0.875) | 2/2 |

**Total: 13/18**

#### 3. Separación

| media mismo grupo | media grupos distintos | diferencia |
| --- | --- | --- |
| 0.864 | 0.834 | 0.030 |

#### 4. Vecino más cercano de cada juego

| juego | grupo | vecino más cercano | similitud | resultado |
| --- | --- | --- | --- | --- |
| talos-principle-2014 | realidad_simulada | matrix-1999 | 0.864 | mismo grupo |
| last-of-us-2013 | supervivencia | children-of-men-2006 | 0.868 | mismo grupo |
| dead-space-2008 | terror_espacial | alien-1979 | 0.877 | mismo grupo |
| stardew-valley-2016 | sin_relacion | the-road-2009 | 0.855 | película de otro grupo |

#### 5. Outliers

| título | similitud máxima | con |
| --- | --- | --- |
| toy-story-1995 | 0.836 | alien-1979 |
| stardew-valley-2016 | 0.855 | the-road-2009 |

#### 6. Distribución de similitudes entre pares distintos

| mínimo | p25 | mediana | p75 | máximo |
| --- | --- | --- | --- | --- |
| 0.816 | 0.828 | 0.834 | 0.847 | 0.890 |

#### 7. Búsquedas libres (top-3)

| consulta | 1° | 2° | 3° |
| --- | --- | --- | --- |
| "a man discovers his whole life is fake" | truman-show-1998 (0.792) | matrix-1999 (0.773) | the-road-2009 (0.770) |
| "a father protects his son in a dying world" | the-road-2009 (0.856) | children-of-men-2006 (0.802) | stardew-valley-2016 (0.794) |
| "crew members hunted by a creature on a spaceship" | alien-1979 (0.871) | event-horizon-1997 (0.850) | dead-space-2008 (0.834) |

### RAM del proceso (RSS)

| momento | MB |
| --- | --- |
| inicio del script | 30 |
| antes de cargar el modelo (con librerías importadas) | 388 |
| después de cargar el modelo | 1174 |
| después de generar los embeddings | 1222 |

Carga del modelo: +786 MB. Total desde el inicio: +1192 MB.

### Comparación de variantes

| variante | acierto top-2 | media mismo grupo | media grupos distintos | diferencia |
| --- | --- | --- | --- | --- |
| A | 13/18 | 0.855 | 0.823 | 0.032 |
| B | 13/18 | 0.864 | 0.834 | 0.030 |

## Conclusiones

> **BORRADOR, para revisar.** Escrito a partir de una sola corrida con 11 títulos: es una muestra muy chica y las diferencias de milésimas no son concluyentes.

Corrida del 11/11/2026. Sinopsis generadas con `gemini-3.8-flash` (temperatura 0.2). Las 11 salieron válidas (ninguna `unknown`), de 104 a 109 palabras.

- **Agrupamiento: parcial (13/18 en las dos variantes).** Terror espacial acierta 6/6: las tres sinopsis comparten vocabulario muy concreto (nave, tripulación, criatura). Realidad simulada es el grupo más flojo (3/6): The Matrix queda más cerca de Alien que de The Truman Show, probablemente por el vocabulario de ciencia ficción, y The Truman Show queda casi empatado con Stardew Valley (pueblo idílico, vida rutinaria). Parece que el modelo capta más el **escenario** que el **tema**.
- **Películas y juegos: bien.** Los tres juegos con grupo encuentran primero a una película de su grupo, nunca a otro juego. El estilo neutro del prompt cumple: las sinopsis no delatan si son de un juego.
- **Separación: muy chica.** Pares del mismo grupo contra el resto: 0,855 contra 0,823 (diferencia de 0,032) en A. Todas las similitudes caen entre 0,79 y 0,88. Los rankings sirven más que los valores absolutos.
- **Outliers: no quedan aislados.** Stardew Valley llega a 0,848 con The Road, más que varios pares del mismo grupo (por ejemplo, The Truman Show con The Talos Principle: 0,825). Un umbral fijo de similitud no alcanza para filtrar resultados sin relación.
- **Prefijo: empate, con leve ventaja de A.** Mismo acierto top-2, y A tiene un poco más de separación (0,032 contra 0,030) y un rango más amplio. En las búsquedas libres empatan: B ubica mejor a The Matrix en "a man discovers his whole life is fake", y en las otras dos el orden es el mismo. Propuesta: usar **A** (`passage:` para sinopsis y `query:` para búsquedas), que es el uso documentado de e5 para búsqueda asimétrica, y volver a medir con más títulos.
- **Reescalado del puntaje: el rango 0,7–1,0 del README no sirve.** Con ese rango, todo quedaría entre 31 % y 58 %. Con la distribución de A, algo como **0,81 → 0 %** (cerca del p25) y **0,88 → 100 %** (cerca del máximo) usa toda la escala. Conviene recalcularlo con el catálogo real, o reescalar por percentiles en lugar de por valores fijos.
- **RAM: no entra en 512 MB.** Cargar el modelo suma unos 790 MB y el proceso termina en unos 1,2 GB (medido con el modelo ya descargado). No entra en el plan gratuito de Render. Opciones a evaluar: versión ONNX o cuantizada del modelo, generar los embeddings de las búsquedas fuera del backend, o una instancia paga.
- **Calidad de las sinopsis: revisar el prompt.** Event Horizon revela el giro de la trama (el motor abrió un portal a una dimensión maligna), lo que viola la regla de no spoilers. The Talos Principle ("intellect-testing challenges") y Dead Space ("using industrial tools") dejan entrever mecánicas de juego.
