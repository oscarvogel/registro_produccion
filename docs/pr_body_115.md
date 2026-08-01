## Contexto

Levantar la stack local de desarrollo (MariaDB + `backend/.env`) desde cero fallaba por tres gaps pre-existentes (issue #115) que se manifestaban al cargar el dump `fg_structure.sql` y correr el seed demo:

1. `app/models/item.py` declaraba `name = Column(String)` sin longitud → `VARCHAR requires a length on dialect mysql`.
2. `app/models/movil.py` no declaraba `usa_planificacion` (ni `codigo_fg` ni `modelo_normalizado` que la DB de prod sí tiene) → `Field 'X' doesn't have a default value` durante el INSERT del seed.
3. `app/models/__init__.py` estaba vacío → `Base.metadata.create_all` no creaba ninguna tabla (los modelos no se conocían).

## Cambio

- `backend/app/models/item.py`: `name` ahora es `String(200)` y `description` es `String(500)`. Sigue el patrón de `moviles.Detalle varchar(200)`.
- `backend/app/models/movil.py`: agrega 3 columnas que el dump de prod tiene y el modelo no declaraba:
  - `usa_planificacion = Column(SmallInteger, default=0)` (issue #115 original).
  - `codigo_fg = Column(String(50), default="")` (encontrada durante la prueba del seed).
  - `modelo_normalizado = Column(String(80), default="")` (encontrada durante la prueba del seed).
- `backend/app/models/__init__.py`: importa explícitamente todos los modelos para que `Base.metadata` los registre. Sin esto, `create_all` no crea ninguna tabla.

## Validaciones

- [x] `py -3.12 -m compileall app` — ok
- [x] `py -3.12 -m pytest` — **134 passed** (no regresiones)
- [x] `py -3.12 -c "from app.core.database import Base, engine; import app.models; Base.metadata.create_all(engine)"` — ahora crea 20 tablas en una DB limpia (antes: 0)
- [x] Flujo end-to-end de la issue #115 verificado en local:
  ```bash
  # DB limpia
  mysql -e "DROP DATABASE fg; CREATE DATABASE fg CHARACTER SET utf8mb4;"
  # Dump + charset explícito (el dump es latin1)
  mysql --default-character-set=utf8mb4 fg < fg_structure.sql
  # Migraciones idempotentes
  for sql in db_migrations/*.sql; do mysql fg < "$sql"; done
  # Seed
  ALLOW_DEMO_SEED=true APP_INSTANCE=indufor_demo APP_ENV=staging \
    py -3.12 -m app.seed.demo_data --force-instance
  # → 6 móviles, 10 personales, 200 producción, 50 cargas combustible, 0 errores
  ```

## Hallazgos durante la implementación (gaps adicionales)

El `fg_structure.sql` está desactualizado respecto a la DB de prod. Aparecieron 2 columnas extra en `moviles` que no estaban en la issue original (`codigo_fg`, `modelo_normalizado`). Las agregué al modelo para que el seed corra. **Pero seguramente hay más columnas en otras tablas** (el dump es de una fecha anterior a varias migraciones que no quedaron registradas como archivos en `db_migrations/`).

**Recomendación:** un issue aparte para "Sincronizar el modelo SQLAlchemy con el dump real de prod". No es trivial:
- Requiere acceso a la DB de prod para hacer `DESCRIBE` de cada tabla.
- Requiere comparar contra el modelo actual y agregar todas las columnas faltantes.
- Alternativa: regenerar el `fg_structure.sql` con un dump fresco de prod.

## Fuera de alcance

- No se regenera el `fg_structure.sql` desde prod (requiere dump real + revisión de Oscar).
- No se cambia el `demo_data.py` para incluir las columnas nuevas explícitamente (los defaults son suficientes para el seed).
- No se cambia el flujo de migraciones (siguen siendo scripts en `db_migrations/`).
- No se tocan los tests del seed (siguen pasando).

## Archivos modificados

- `backend/app/models/__init__.py` (nuevo contenido, 27 líneas)
- `backend/app/models/item.py` (+6/-3 líneas)
- `backend/app/models/movil.py` (+3 líneas)

## Después del merge

Para levantar la stack local de dev desde cero (con datos demo), el flujo documentado en el issue #115 ahora funciona:

```bash
mysql -h 127.0.0.1 -P 3306 -u root -e "CREATE DATABASE fg CHARACTER SET utf8mb4;"
mysql --default-character-set=utf8mb4 fg < fg_structure.sql
for sql in db_migrations/*.sql; do mysql fg < "$sql"; done
cd backend
ALLOW_DEMO_SEED=true APP_INSTANCE=indufor_demo APP_ENV=staging \
  py -3.12 -m app.seed.demo_data --force-instance
```

O más corto, con `create_all` desde el modelo (no necesita dump pero los datos son vacíos):

```bash
mysql -e "CREATE DATABASE fg CHARACTER SET utf8mb4;"
py -3.12 -c "from app.core.database import Base, engine; import app.models; Base.metadata.create_all(engine)"
ALLOW_DEMO_SEED=true APP_INSTANCE=indufor_demo APP_ENV=staging \
  py -3.12 -m app.seed.demo_data --force-instance
```

Deploy a prod: este PR no toca prod (no es código que se ejecute en el flujo normal del backend). Es un fix solo de dev/seed. **No requiere migración nueva ni acción en prod**.
