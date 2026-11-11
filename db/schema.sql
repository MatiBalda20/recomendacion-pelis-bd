-- Esquema de la base de datos (Supabase: Postgres + pgvector + pg_trgm).
-- Ejecutar completo en el editor SQL de Supabase. Es idempotente.

create extension if not exists vector;
create extension if not exists pg_trgm;

create table if not exists contenido (
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

-- Vecinos más cercanos por distancia coseno.
create index if not exists contenido_embedding_hnsw
  on contenido using hnsw (embedding vector_cosine_ops);

-- Búsqueda difusa de títulos (autocompletado tolerante a errores).
create index if not exists contenido_titulo_trgm
  on contenido using gin (titulo gin_trgm_ops);
create index if not exists contenido_titulo_es_trgm
  on contenido using gin (titulo_es gin_trgm_ops);

-- Filtros frecuentes.
create index if not exists contenido_tipo_anio on contenido (tipo, anio);
create index if not exists contenido_generos on contenido using gin (generos);

-- El frontend nunca habla directo con Supabase: se activa RLS sin políticas
-- para que la API pública de Supabase (anon) no pueda leer ni escribir.
-- El backend se conecta con la cadena de Postgres, que no pasa por RLS.
alter table contenido enable row level security;
