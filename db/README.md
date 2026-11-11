# Base de datos

`schema.sql` crea la tabla `contenido`, las extensiones `vector` y `pg_trgm` y sus índices.

## Aplicar el esquema

1. Abrí el proyecto de Supabase → **SQL Editor**.
2. Pegá el contenido de `schema.sql` y ejecutalo. Se puede volver a correr sin romper nada.

También se puede aplicar desde la terminal:

```bash
psql "$DATABASE_URL" -f db/schema.sql
```

## Notas

- La dimensión del vector (384) corresponde a `multilingual-e5-small`. Si se cambia el modelo, hay que cambiar la columna y regenerar todo el catálogo.
- RLS queda activado sin políticas: la API REST de Supabase no expone la tabla. Solo el backend accede, con la cadena de conexión de Postgres.
