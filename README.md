# Recomendador de películas y juegos por trama

Aplicación web que recibe el título de una película o un juego y devuelve los títulos con la **trama más parecida**, ya sean películas, juegos o ambos. La similitud no se calcula con géneros ni etiquetas: se calcula comparando **embeddings de las sinopsis** guardados en una base de datos vectorial.

> Proyecto personal sin fines de lucro, hecho como portfolio. Estado: **en desarrollo**.

## Qué hace

- **Similares por título:** "The Matrix" devuelve las 10 películas y juegos con la trama más parecida, sin incluir a The Matrix.
- **Filtros:** solo películas, solo juegos, año mínimo, género y plataforma.
- **Búsqueda por descripción:** "un detective investiga crímenes en una ciudad futurista" devuelve los títulos cuya sinopsis más se acerca al texto.
- **Recomendaciones cruzadas:** juegos parecidos a una película y viceversa.
- **Puntaje de similitud** visible en porcentaje.
- **Autocompletado tolerante a errores** ("matrx" → "The Matrix").

## Arquitectura

```
┌──────────────┐  HTTP  ┌──────────────────────┐  SQL  ┌───────────────────────┐
│ Frontend web │ ─────► │ API backend (FastAPI)│ ────► │ Supabase              │
│ React + Vite │        │                      │       │ Postgres + pgvector   │
└──────────────┘        │  Modelo de embeddings│       └───────────────────────┘
                        │  multilingual-e5-small│                 ▲
                        └──────────────────────┘                  │ guarda
                                   ▲                              │
                                   │ mismo modelo                 │
┌──────────────────┐ datos ┌───────┴──────────┐                   │
│ Wikidata + Gemini│ ────► │ Script de carga  │ ──────────────────┘
└──────────────────┘       └──────────────────┘
```

- El **backend** recibe las búsquedas, genera embeddings con un modelo local y consulta Supabase.
- El **modelo solo se usa** en la búsqueda por descripción. Para "similares a un título" se usa el vector que ya está guardado.
- El **script de carga** vive en el mismo proyecto que el backend y usa el mismo código para generar embeddings, así los vectores del catálogo y los de las consultas siempre son comparables.
- Por ahora el backend corre **localmente**. Más adelante: frontend en Cloudflare Pages y backend en Render.

## Stack

| Capa | Tecnología |
| --- | --- |
| Frontend | React con Vite |
| Backend | Python con FastAPI |
| Base de datos | Supabase: PostgreSQL con pgvector (índice HNSW) y pg_trgm (plan gratuito) |
| Embeddings | `multilingual-e5-small` con sentence-transformers y PyTorch (local, gratuito, 384 dimensiones) |
| Datos | Wikidata (datos exactos, CC0) y sinopsis generadas con Gemini (plan gratuito) |
| Respaldo de sinopsis | Introducción de Wikipedia (CC BY-SA) para títulos que Gemini no conoce |
| CI | GitHub Actions |

## Estructura del repositorio

> Estructura propuesta; puede cambiar durante el desarrollo.

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI: endpoints
│   │   ├── db.py            # conexión a Supabase
│   │   └── embeddings.py    # carga del modelo y generación de vectores
│   ├── scripts/
│   │   └── cargar_catalogo.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   └── package.json
├── db/
│   └── schema.sql
└── .github/
    └── workflows/
```

## Puesta en marcha

### Requisitos

- Python 3.11 o superior
- Node.js 20 o superior
- Una cuenta gratuita de [Supabase](https://supabase.com)
- Una clave gratuita de la API de Gemini (solo para cargar el catálogo)

### 1. Base de datos

Creá un proyecto en Supabase y ejecutá `db/schema.sql` en el editor SQL. El esquema base es:

```sql
create extension if not exists vector;
create extension if not exists pg_trgm;

create table contenido (
  id               text primary key,          -- ej: 'pelicula-matrix-1999'
  tipo             text not null check (tipo in ('pelicula', 'juego')),
  titulo           text not null,
  titulo_es        text,
  sinopsis         text not null,             -- en inglés; origen del vector
  sinopsis_es      text,                      -- solo para mostrar
  anio             int,
  generos          text[],
  extra            jsonb,                     -- actores, director, plataformas, desarrollador
  wikidata_id      text,
  url_wikipedia    text,
  origen_sinopsis  text not null check (origen_sinopsis in ('gemini', 'wikipedia', 'manual')),
  modelo_sinopsis  text,
  version_prompt   text,
  modelo_embedding text not null,
  embedding        vector(384) not null
);

create index on contenido using hnsw (embedding vector_cosine_ops);
create index on contenido using gin (titulo gin_trgm_ops);
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # completar las variables
uvicorn app.main:app --reload
```

La documentación interactiva de la API queda en `http://localhost:8000/docs`.

La primera vez se descarga el modelo de embeddings desde Hugging Face. Después se carga en memoria una sola vez, al iniciar el backend.

### 3. Cargar el catálogo

```bash
cd backend
python scripts/cargar_catalogo.py titulos.csv
```

`titulos.csv` es una lista de títulos elegidos a mano, con su año (y la plataforma, en el caso de los juegos). Ver [Estrategia de carga](#estrategia-de-carga).

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

## Variables de entorno

Van en `backend/.env`. Este archivo **nunca** se sube al repositorio.

| Variable | Descripción |
| --- | --- |
| `DATABASE_URL` | Cadena de conexión de Postgres de Supabase |
| `GEMINI_API_KEY` | Clave de la API de Gemini (solo la usa el script de carga) |
| `EMBEDDING_MODEL` | Nombre del modelo de embeddings (`intfloat/multilingual-e5-small`) |
| `CORS_ORIGINS` | Orígenes permitidos para el frontend (ej: `http://localhost:5173`) |

## API

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/buscar?q=` | Títulos que coinciden con el texto (búsqueda difusa, para autocompletar) |
| `GET` | `/similares/{id}?tipo=&limite=` | Los más parecidos al título indicado, excluyendo el propio |
| `POST` | `/buscar-por-trama` | Recibe una descripción, genera su embedding y devuelve los más cercanos |
| `GET` | `/contenido/{id}` | Ficha completa de un título |

## Cómo funciona la similitud

1. Cada sinopsis se convierte en un vector de 384 números con `multilingual-e5-small`.
2. Para "similares a un título", se toma el vector guardado de ese título y se buscan los vecinos más cercanos por **distancia coseno** con el índice HNSW de pgvector.
3. Para la búsqueda por descripción, se genera el vector del texto del usuario y se busca igual.

Detalles importantes:

- **Solo se vectoriza la sinopsis.** El título, el elenco y la plataforma quedan como datos para filtrar, así no distorsionan la similitud de trama.
- **Prefijos de e5:** el modelo espera un prefijo delante de cada texto (`query: ` o `passage: `). Se usa siempre el mismo criterio, porque cambiarlo cambia los vectores.
- **Reescalado del puntaje:** e5 suele dar similitudes entre 0,7 y 1,0 aunque los textos no se parezcan tanto, así que el puntaje se reescala antes de mostrarlo (por ejemplo, 0,7–1,0 → 0–100 %).
- **Mismo modelo en todos lados:** si se cambia el modelo o su versión, hay que regenerar todos los vectores del catálogo.
- **Multilingüe:** las sinopsis se vectorizan en inglés, pero una búsqueda escrita en español también encuentra resultados.

## Estrategia de carga

Las sinopsis las escribe Gemini y los datos exactos vienen de Wikidata. Así todas las sinopsis tienen el mismo estilo, lo que mejora las recomendaciones cruzadas entre películas y juegos, y los datos duros no dependen de la memoria de la IA.

1. **Elegir títulos:** se cargan a mano, en tandas, con su año (y la plataforma, si es un juego).
2. **Completar con Wikidata:** año, géneros, plataformas, director o desarrollador, título en español y enlace a Wikipedia. Si no hay coincidencia o hay varias, el título queda para revisión manual.
3. **Generar la sinopsis con Gemini:** prompt fijo, con hasta 10 títulos por solicitud y respuesta en JSON. Solo la trama, en inglés, de 80 a 120 palabras, sin spoilers ni mecánicas de juego, y `unknown` si el modelo no conoce el título con certeza.
4. **Filtrar y guardar:** se descartan los `unknown`; el resto se guarda con sus campos de trazabilidad y su embedding.
5. **Revisar:** se revisa a mano el 10 % de cada tanda. Si hay errores, se corrige el prompt y se regeneran esos registros.

Los campos `origen_sinopsis`, `modelo_sinopsis` y `version_prompt` permiten saber qué registros regenerar si cambia el prompt o el modelo. La interfaz muestra **"Sinopsis generada por IA"** cuando corresponde.

## Fuentes de datos y atribución

| Fuente | Uso | Licencia |
| --- | --- | --- |
| [Wikidata](https://www.wikidata.org) | Títulos, años, géneros, plataformas, elenco | [CC0](https://www.wikidata.org/wiki/Wikidata:Licensing) |
| Gemini (Google) | Sinopsis generadas | Plan gratuito; las solicitudes pueden usarse para mejorar los productos de Google, por eso solo se envían títulos y años |
| [Wikipedia](https://www.wikipedia.org) | Sinopsis de respaldo | [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/): se enlaza el artículo y la licencia en cada ficha que la use |

TMDB no se usa: sus términos de API prohíben usar su contenido en aplicaciones basadas en machine learning o IA, como esta.

## Mantenimiento

- **Pausa de Supabase:** los proyectos gratuitos se pausan después de una semana sin actividad. Un workflow semanal de GitHub Actions hace una consulta simple para mantenerlo activo.
- **Seguridad:** la cadena de conexión y las claves viven solo en el `.env` del backend. El frontend nunca habla directo con Supabase.

## Convenciones de commits

Los commits siguen [Conventional Commits 1.0.0](https://www.conventionalcommits.org/es/v1.0.0/):

```
<tipo>(<alcance opcional>): <descripción>

<cuerpo opcional>

<pie opcional>
```

| Tipo | Uso | Ejemplo |
| --- | --- | --- |
| `feat` | Funcionalidad nueva | `feat(api): agregar endpoint de similares` |
| `fix` | Corrección de un error | `fix(carga): descartar sinopsis vacías` |
| `docs` | Solo documentación | `docs: explicar variables del archivo .env` |
| `style` | Formato, sin cambios de lógica | `style(front): ordenar imports` |
| `refactor` | Cambio interno sin agregar ni corregir nada | `refactor(api): separar acceso a la base` |
| `perf` | Mejora de rendimiento | `perf(db): agregar índice HNSW` |
| `test` | Tests nuevos o corregidos | `test(api): cubrir filtro por tipo` |
| `build` | Dependencias o empaquetado | `build: fijar versión de sentence-transformers` |
| `ci` | Workflows de GitHub Actions | `ci: agregar consulta semanal a Supabase` |
| `chore` | Mantenimiento general | `chore: actualizar .gitignore` |

Reglas:

- Alcances sugeridos: `api`, `front`, `carga`, `db`, `modelo`.
- Descripción en imperativo, en minúscula, sin punto final y con un máximo de 72 caracteres.
- Los cambios que rompen compatibilidad llevan `!` (`feat(api)!: ...`) o un pie `BREAKING CHANGE:`.
- Un commit hace una sola cosa.

### Autoría

- El autor y el committer de cada commit son siempre una persona del proyecto.
- **Ningún asistente de IA figura como autor ni como coautor.** No se aceptan pies `Co-Authored-By` que nombren a una IA, ni líneas del tipo "Generated with" en commits o pull requests.
- Si se usa un asistente de IA para escribir código o mensajes, hay que configurarlo para que no agregue esas líneas y revisar el mensaje antes de confirmar.
- Un hook `commit-msg` (commitlint con Husky) y un chequeo en GitHub Actions sobre cada pull request rechazan los mensajes que no cumplen estas reglas.

## Hoja de ruta

- [ ] **Prueba de concepto:** 100 películas y 50 juegos, similares desde la terminal y medición de la RAM del modelo.
- [ ] **Carga del catálogo:** Wikidata + Gemini, entre 300 y 500 títulos revisados.
- [ ] **Backend y API:** los cuatro endpoints, con filtros y búsqueda difusa.
- [ ] **Frontend:** buscador, resultados, ficha y búsqueda por trama.
- [ ] **Despliegue:** frontend en Cloudflare Pages y backend en Render.

Fuera del alcance actual: cuentas de usuario, recomendaciones personalizadas, series y libros, panel de administración y app móvil nativa.

## Licencia

El código se publica bajo la licencia que se defina para el repositorio (por ejemplo, MIT). Los datos mantienen la licencia de su fuente: CC0 para Wikidata y CC BY-SA para el texto tomado de Wikipedia.
