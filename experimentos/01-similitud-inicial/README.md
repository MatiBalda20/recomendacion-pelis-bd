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

Segunda corrida: se suman 35 títulos en tres grupos más grandes (46 en total).

| grupo | películas | juegos |
| --- | --- | --- |
| western | The Good, the Bad and the Ugly (1966), Unforgiven (1992), Django Unchained (2012), Once Upon a Time in the West (1968), No Country for Old Men (2007), True Grit (2010), The Hateful Eight (2015), 3:10 to Yuma (2007), The Magnificent Seven (1960), Butch Cassidy and the Sundance Kid (1969) | Red Dead Redemption 2 (2018), Call of Juarez: Gunslinger (2013) |
| mafia | The Godfather (1972), The Godfather Part II (1974), Goodfellas (1990), Once Upon a Time in America (1984), Scarface (1983), The Departed (2006), Casino (1995), The Irishman (2019), The Untouchables (1987), Donnie Brasco (1997) | Mafia: Definitive Edition (2020), Sleeping Dogs (2012) |
| antiguedad | Gladiator (2000), Ben-Hur (1959), Troy (2004), 300 (2006), Spartacus (1960), Agora (2009), Alexander (2004), Gladiator II (2024), Cleopatra (1963), The Fall of the Roman Empire (1964) | Assassin's Creed Odyssey (2018) |

Los ids están en `titulos.json`. `generar_sinopsis.py` solo pide las sinopsis que faltan, así que las 11 de la primera corrida no cambian.

El grupo **no** se le manda a Gemini: solo id, título, año y tipo.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `titulos.json` | Los 46 títulos con su grupo. |
| `prompt_sinopsis.txt` | Prompt fijo para Gemini. `{TITULOS}` se reemplaza con una línea por título. |
| `generar_sinopsis.py` | Etapa 1: pide a Gemini, en una sola solicitud (temperatura 0.2), las sinopsis que faltan en `sinopsis.json` y las agrega. |
| `prueba.py` | Etapa 2: genera los embeddings, corre el análisis y escribe `resultados.md` y `sinopsis.md` (las sinopsis de Gemini en formato legible). |
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
python generar_sinopsis.py        # pide solo las que faltan; --forzar las regenera todas
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
- **Variante C:** los prefijos de A, más **centrado**. Se calcula el vector promedio de todas las sinopsis del catálogo, se le resta a cada vector (sinopsis y búsquedas libres) y se vuelve a normalizar. Así se elimina lo que todas las sinopsis tienen en común y queda lo propio de cada una. Con el centrado, la similitud puede ser negativa y su escala no se puede comparar con la de A y B.

1. Matriz de similitud coseno entre todos los títulos.
2. Acierto top-2: para cada título con grupo temático, cuántos de sus 2 vecinos más cercanos son de su grupo (total sobre el doble de esos títulos: 18 en la primera corrida, 88 en la segunda).
3. Separación: similitud media entre pares del mismo grupo temático contra la media del resto de los pares (el par Toy Story – Stardew Valley cuenta como "grupos distintos").
4. Juegos: si el vecino más cercano de cada juego es de su grupo o es otro juego de otro grupo.
5. Outliers: similitud máxima de Toy Story y de Stardew Valley con cualquier otro título.
6. Distribución: mínimo, p25, mediana, p75 y máximo de las similitudes entre pares distintos.
7. Búsquedas libres: top-3 para tres consultas en lenguaje natural.

También mide el RSS del proceso antes y después de cargar el modelo, y después de generar los embeddings.

## Resultados

El detalle completo de la última corrida (matrices, vecinos de cada título, búsquedas libres) está en [`resultados.md`](resultados.md), y las sinopsis usadas en [`sinopsis.md`](sinopsis.md).

Las dos corridas son del 11/11/2026, con `intfloat/multilingual-e5-small` y sinopsis de `gemini-3.8-flash` (temperatura 0.2).

| corrida | títulos | con grupo temático | sinopsis |
| --- | --- | --- | --- |
| 1 | 11 | 9 (3 grupos de 3) | 104 a 109 palabras |
| 2 | 46 | 44 (3 grupos de 3 + western 12, mafia 12, antigüedad 11) | las 11 de la corrida 1 + 35 nuevas de 80 a 88 palabras |

En las dos corridas, ninguna sinopsis salió `unknown`.

### Comparación de variantes

| corrida | variante | acierto top-2 | media mismo grupo | media grupos distintos | diferencia |
| --- | --- | --- | --- | --- | --- |
| 1 | A | 13/18 (72 %) | 0.855 | 0.823 | 0.032 |
| 1 | B | 13/18 (72 %) | 0.864 | 0.834 | 0.030 |
| 2 | A | 79/88 (90 %) | 0.853 | 0.816 | 0.037 |
| 2 | B | 79/88 (90 %) | 0.866 | 0.833 | 0.033 |
| 2 | C | **82/88 (93 %)** | 0.127 | -0.057 | **0.184** |

La diferencia de C no se puede comparar directamente con la de A y B, porque el centrado estira la escala. Una medida comparable es dividir la diferencia por el rango intercuartil (p75 − p25) de cada variante: A da 0,037 / 0,033 ≈ **1,1** y C da 0,184 / 0,131 ≈ **1,4**. En C los grupos se separan más, pero la mejora es de alrededor de un 25 %, no de 5 veces.

### Acierto top-2 por grupo (corrida 2)

| grupo | A | B | C |
| --- | --- | --- | --- |
| realidad_simulada | 3/6 | 2/6 | 3/6 |
| supervivencia | 4/6 | 3/6 | 4/6 |
| terror_espacial | 6/6 | 6/6 | 6/6 |
| western | 24/24 | 24/24 | 24/24 |
| mafia | 20/24 | 22/24 | 23/24 |
| antiguedad | 22/22 | 22/22 | 22/22 |
| **total** | **79/88** | **79/88** | **82/88** |

### Vecino más cercano de cada juego (corrida 2)

| juego | grupo | A | B | C |
| --- | --- | --- | --- | --- |
| The Talos Principle | realidad_simulada | The Matrix ✓ | The Matrix ✓ | The Matrix ✓ |
| The Last of Us | supervivencia | Butch Cassidy ✗ | Children of Men ✓ | Children of Men ✓ |
| Dead Space | terror_espacial | Alien ✓ | Alien ✓ | Event Horizon ✓ |
| Red Dead Redemption 2 | western | Unforgiven ✓ | Unforgiven ✓ | Unforgiven ✓ |
| Call of Juarez: Gunslinger | western | Unforgiven ✓ | Unforgiven ✓ | Unforgiven ✓ |
| Mafia: Definitive Edition | mafia | Red Dead Redemption 2 ✗ (otro juego) | Goodfellas ✓ | Once Upon a Time in America ✓ |
| Sleeping Dogs | mafia | Goodfellas ✓ | The Departed ✓ | The Departed ✓ |
| Assassin's Creed Odyssey | antiguedad | 300 ✓ | 300 ✓ | 300 ✓ |
| Stardew Valley | sin_relacion | Once Upon a Time in the West (0.853) | Once Upon a Time in the West (0.865) | The Road (0.118) |

### Distribución de similitudes entre pares distintos

| corrida | variante | mínimo | p25 | mediana | p75 | máximo |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A | 0.793 | 0.815 | 0.826 | 0.838 | 0.875 |
| 1 | B | 0.816 | 0.828 | 0.834 | 0.847 | 0.890 |
| 2 | A | 0.752 | 0.806 | 0.823 | 0.839 | 0.909 |
| 2 | B | 0.788 | 0.824 | 0.838 | 0.854 | 0.912 |
| 2 | C | -0.279 | -0.096 | -0.037 | 0.035 | 0.457 |

### Búsquedas libres (top-3, corrida 2)

Variante C:

| consulta | 1° | 2° | 3° |
| --- | --- | --- | --- |
| "a man discovers his whole life is fake" | The Truman Show (0.244) | No Country for Old Men (0.154) | The Road (0.121) |
| "a father protects his son in a dying world" | The Road (0.421) | The Godfather (0.244) | Children of Men (0.161) |
| "crew members hunted by a creature on a spaceship" | Alien (0.447) | Event Horizon (0.387) | Dead Space (0.319) |

Variante A:

| consulta | 1° | 2° | 3° |
| --- | --- | --- | --- |
| "a man discovers his whole life is fake" | The Truman Show (0.822) | No Country for Old Men (0.807) | Donnie Brasco (0.805) |
| "a father protects his son in a dying world" | The Road (0.881) | The Godfather (0.854) | Children of Men (0.828) |
| "crew members hunted by a creature on a spaceship" | Alien (0.866) | Event Horizon (0.840) | Dead Space (0.832) |

### RAM del proceso (RSS)

| momento | corrida 1 (MB) | corrida 2 (MB) |
| --- | --- | --- |
| inicio del script | 30 | 30 |
| antes de cargar el modelo (con librerías importadas) | 388 | 387 |
| después de cargar el modelo | 1174 | 1174 |
| después de generar los embeddings | 1222 | 1213 |

## Conclusiones

> **BORRADOR, para revisar.** Son dos corridas con 11 y 46 títulos: sigue siendo una muestra chica, y las diferencias de milésimas no son concluyentes.

- **Con grupos más grandes, el agrupamiento mejora mucho: de 72 % a 90 % de acierto top-2.** Western (24/24) y antigüedad (22/22) aciertan todo: son grupos con un escenario muy marcado (el Oeste, Roma o Grecia) y vocabulario propio. Esto confirma lo que se veía en la primera corrida: el modelo capta más el **escenario y la época** que el **tema**.
- **Los grupos chicos y temáticos siguen flojos.** Realidad simulada y supervivencia no mejoran, y ahora pierden vecinos contra los westerns. The Truman Show queda más cerca de Once Upon a Time in the West que de The Talos Principle; The Road, de 3:10 to Yuma. Probablemente influye que esos grupos tienen 3 títulos contra 11 o 12 de los nuevos.
- **Mafia y western se cruzan.** Los fallos de mafia caen en westerns (Red Dead Redemption 2, 3:10 to Yuma, Butch Cassidy): comparten crimen, armas, forajidos y época.
- **Películas y juegos: bien, con ventaja de B.** En B los 8 juegos con grupo tienen como vecino más cercano a un título de su grupo. En A fallan dos: The Last of Us (Butch Cassidy) y Mafia: Definitive Edition, que es el primer caso de un juego cuyo vecino más cercano es otro juego de otro grupo (Red Dead Redemption 2).
- **Prefijo: sigue el empate.** Mismo acierto total (79/88). A separa un poco más (0,037 contra 0,033) y tiene el rango más amplio; B acierta más en mafia (22 contra 20) y en los juegos, y menos en los grupos chicos. Se mantiene la propuesta de usar **A** (`passage:` para sinopsis y `query:` para búsquedas), que es el uso documentado de e5 para búsqueda asimétrica, pero la ventaja de B con los juegos merece otra medición.
- **Centrado (variante C): es la mejor variante hasta ahora.** Llega a 82/88, con mafia en 23/24, y los 8 juegos con grupo tienen como vecino más cercano a un título de su grupo. Los outliers quedan más abajo: Stardew Valley llega como máximo a 0,118 y Toy Story a 0,143, por debajo de casi todos los pares de los grupos grandes. Los grupos chicos (realidad simulada y supervivencia) no mejoran: en esos casos el problema es el tema abstracto, no la componente común. No cuesta RAM ni tiempo: es una resta de vectores.
  - **Cuidado:** el promedio depende del catálogo. Si se agregan muchos títulos, hay que recalcularlo y volver a centrar todos los vectores guardados. Si el catálogo está muy cargado de un género, el promedio se corre hacia ese género y los títulos de ese género se separan menos entre sí. En la base habría que guardar el promedio junto con los vectores y centrar cada búsqueda con ese mismo promedio.
- **Separación: chica sin centrado.** En A, 0,853 contra 0,816. En C sube a 1,4 rangos intercuartiles, contra 1,1 en A. Los rankings sirven; los valores absolutos, poco.
- **Outliers: no quedan aislados.** Stardew Valley llega a 0,853 con Once Upon a Time in the West, más que muchos pares del mismo grupo. Un umbral fijo de similitud no alcanza para filtrar resultados sin relación.
- **Búsquedas libres: los resultados sin relación se meten en el top-3.** "a father protects his son in a dying world" trae The Godfather en 2° lugar, y "a man discovers his whole life is fake" trae No Country for Old Men y Donnie Brasco detrás de The Truman Show (The Matrix queda afuera).
- **Reescalado del puntaje: el rango 0,7–1,0 sigue sin servir.** Con 46 títulos la distribución de A se abre (0,752 a 0,909). Algo como **0,80 → 0 %** (cerca del p25) y **0,90 → 100 %** usa casi toda la escala. Conviene recalcularlo con el catálogo real o reescalar por percentiles. Con centrado (C) los valores cambian por completo (de -0,28 a 0,46), así que el reescalado por percentiles es la única opción que sirve para las dos.
- **RAM: no entra en 512 MB.** El modelo suma unos 790 MB y el proceso queda en unos 1,2 GB. Pasar de 11 a 46 títulos no cambia nada: el costo es el modelo, no los embeddings. No entra en el plan gratuito de Render. Opciones a evaluar: versión ONNX o cuantizada del modelo, generar los embeddings de las búsquedas fuera del backend, o una instancia paga.
- **Sesgo a tener en cuenta: el largo de las sinopsis.** Las 35 nuevas tienen 80 a 88 palabras y las 11 originales 104 a 109, con el mismo modelo y el mismo prompt (quizás porque se pidieron 35 juntas). Puede favorecer la similitud dentro de los grupos nuevos. Para comparar sin ese sesgo, habría que regenerar todo junto (`--forzar`) o pedirlas en tandas del mismo tamaño.
- **Calidad de las sinopsis: revisar el prompt.** En la primera corrida, Event Horizon revela el giro de la trama (el motor abrió un portal a una dimensión maligna), lo que viola la regla de no spoilers, y The Talos Principle ("intellect-testing challenges") y Dead Space ("using industrial tools") dejan entrever mecánicas de juego. De las 35 nuevas (revisadas a mano), todas respetan el largo y ninguna nombra actores, directores ni etiquetas de género, pero el problema de los spoilers se repite y es más común en las de mafia:
  - **Revelan el final:** The Godfather Part II ("ultimately leaves him entirely isolated"), Casino ("their empire rapidly collapses under its own excess") y Gladiator II, que arranca con la muerte del protagonista de Gladiator ("after the demise of a heroic gladiator"), un spoiler de otro título del set.
  - **Lo insinúan:** Once Upon a Time in America ("ultimate betrayal"), Scarface ("inviting retribution"), Goodfellas ("instinct for personal survival"), The Untouchables ("personal tragedy"), The Hateful Eight (confirma que alguien planea liberar a la prisionera), Butch Cassidy ("encroaching mortality") y The Magnificent Seven ("sacrifice").
  - **Mecánicas de juego, leves:** Assassin's Creed Odyssey ("takes on perilous contracts", "across land and sea"), Mafia: Definitive Edition ("violent assignments") y Call of Juarez: Gunslinger ("discrepancies arise in his colorful storytelling", que es el recurso del juego).
  - Las sinopsis no se modificaron, para no cambiar los resultados de esta corrida. Si se ajusta el prompt (por ejemplo, prohibir frases sobre cómo termina el arco del protagonista y sobre otros títulos de una saga), hay que regenerarlas con `--forzar` y volver a medir.
