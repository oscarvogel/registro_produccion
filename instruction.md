## PROMPT PARA IA — SISTEMA DE KPIs Y DASHBOARD DE PRODUCCIÓN FORESTAL

### CONTEXTO DEL PROYECTO

Tenés una aplicación web de **Registro de Producción Forestal** con stack:
- **Backend**: FastAPI + SQLAlchemy + MariaDB
- **Frontend**: Vue 3 + Pinia + Tailwind CSS v4 + Vue Router
- **Autenticación**: JWT por DNI/contraseña, con roles `encargado` (supervisor) y operador

El sistema ya tiene las siguientes tablas clave:
- `tablero_produccion` — registros diarios de producción con campos como `UN`, `operacion`, `fecha`, `equipo`, `cod_equipo`, `cod_operador`, `produccion`, `tn_despachadas`, `m3`, `carros`, `plantas`, `mtrs_recorridos`, `km_carreteo`, `km_perfilado`, `hr_inicio`, `hr_fin`, `hrs_no_op`, `has`, `hr_disposicion`, `combustible`
- `tipo_de_proceso` — catálogo con columna `campos` (CSV de campos activos por proceso)
- `unidadnegocio_tipo_proceso` — pivot que asocia unidades de negocio con tipos de proceso
- `moviles` — maquinaria (`idMovil`, `Patente`, `Detalle`)
- `personal` — con campos `encargado` (0/1) y `unidad_negocio`
- `unidadnegocio` — unidades de negocio

Los tipos de proceso existentes y sus KPIs naturales son:

| id | Nombre | Campos activos |
|----|--------|---------------|
| 1 | CARGA | tn_despachadas |
| 2 | EXTRACCION | carros, distancia_recorrida |
| 3 | PROCESO | m3, plantas |
| 4 | VOLTEO | plantas |
| 5 | HORAS MAQUINAS | hora_inicio, hora_fin |
| 6 | DESPEJE Y SUBSOLADO | has |
| 7 | EMPUJE PESADO | has |
| 8 | DESTOCONADO Y SUBSOLADO | has, horas_disposicion |
| 9 | PERFILADO | km |
| 10 | CARRETEO | km |
| 11 | ACOPIO BIOMASA | tn_despachadas |
| 12 | CHIPEADO EN SUELO | tn_despachadas |
| 13 | CHIPEADO SOBRE CAMION | tn_despachadas |

---

### TAREA 1 — MIGRACIÓN SQL

Crear el script SQL `migrations_kpi.sql` con:

**1.1 Tabla `kpi_definicion`** — catálogo maestro de KPIs disponibles:
```sql
CREATE TABLE kpi_definicion (
  id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre          VARCHAR(100) NOT NULL COMMENT 'Ej: Toneladas Despachadas',
  campo_origen    VARCHAR(80)  NOT NULL COMMENT 'Columna en tablero_produccion que se agrega/promedia',
  agregacion      ENUM('SUM','AVG','COUNT','MAX','CUSTOM') NOT NULL DEFAULT 'SUM',
  unidad          VARCHAR(20)  NOT NULL DEFAULT '' COMMENT 'Ej: TN, M3, HAS, KM, HS',
  icono           VARCHAR(50)  NOT NULL DEFAULT '' COMMENT 'Nombre de ícono Lucide',
  descripcion     VARCHAR(255) NOT NULL DEFAULT '',
  activo          TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**1.2 Tabla `tipo_proceso_kpi`** — qué KPIs pertenecen a cada tipo de proceso:
```sql
CREATE TABLE tipo_proceso_kpi (
  tipo_proceso_id INT UNSIGNED NOT NULL,
  kpi_id          INT UNSIGNED NOT NULL,
  orden           TINYINT UNSIGNED NOT NULL DEFAULT 0,
  es_principal    TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 = KPI destacado/hero card',
  PRIMARY KEY (tipo_proceso_id, kpi_id),
  FOREIGN KEY (tipo_proceso_id) REFERENCES tipo_de_proceso(id) ON UPDATE CASCADE,
  FOREIGN KEY (kpi_id) REFERENCES kpi_definicion(id) ON UPDATE CASCADE
);
```

**1.3 INSERTs** — poblar `kpi_definicion` con al menos estos KPIs:

| campo_origen | nombre | agregacion | unidad | icono |
|---|---|---|---|---|
| tn_despachadas | Toneladas Despachadas | SUM | TN | truck |
| m3 | Metros Cúbicos | SUM | M³ | box |
| plantas | Plantas Procesadas | SUM | uds | leaf |
| carros | Carros | SUM | uds | layers |
| mtrs_recorridos | Metros Recorridos | SUM | mts | route |
| km_carreteo | KM Carreteo | SUM | km | map-pin |
| km_perfilado | KM Perfilado | SUM | km | map |
| has | Hectáreas | SUM | HAS | grid |
| hr_disposicion | Horas Disposición | SUM | hs | clock |
| combustible | Combustible Consumido | SUM | lts | fuel |
| hrs_no_op | Horas No Operativas | SUM | hs | alert-circle |
| CUSTOM:horas_trabajadas | Horas Trabajadas | CUSTOM | hs | timer | *(calculado: SUM(hr_fin - hr_inicio))* |
| CUSTOM:eficiencia | Eficiencia Operativa | CUSTOM | % | percent | *(calculado: (horas_trabajadas - hrs_no_op) / horas_trabajadas * 100)* |
| CUSTOM:registros | Registros del Período | COUNT | reg | clipboard-list |

Luego hacer INSERTs en `tipo_proceso_kpi` asignando KPIs a cada tipo de proceso de forma lógica. Por ejemplo:
- CARGA (1) → tn_despachadas (principal), combustible, horas_trabajadas, eficiencia, registros
- PROCESO (3) → m3 (principal), plantas, horas_trabajadas, eficiencia, combustible
- HORAS MAQUINAS (5) → horas_trabajadas (principal), hrs_no_op, eficiencia, combustible
- etc.

---

### TAREA 2 — BACKEND (FastAPI)

Crear el archivo `backend/app/api/routes/dashboard.py` con los siguientes endpoints:

**2.1 GET `/api/dashboard/kpis`**

Parámetros query:
- `un_id: int` — requerido, unidad de negocio del encargado
- `tipo_proceso_id: int | None` — filtro opcional
- `movil_id: int | None` — filtro opcional (filtra por `cod_equipo`)
- `fecha_desde: date | None`
- `fecha_hasta: date | None`

Lógica:
1. Obtener los `tipo_proceso_id` que pertenecen a la `un_id` consultando `unidadnegocio_tipo_proceso`
2. Si se pasa `tipo_proceso_id`, verificar que pertenezca a esa UN
3. Obtener los KPIs aplicables via `tipo_proceso_kpi` JOIN `kpi_definicion`
4. Para cada KPI, ejecutar la query apropiada sobre `tablero_produccion` aplicando los filtros
5. Para KPIs CUSTOM:
   - `horas_trabajadas`: `SUM(hr_fin - hr_inicio)`
   - `eficiencia`: `(SUM(hr_fin - hr_inicio) - SUM(hrs_no_op)) / NULLIF(SUM(hr_fin - hr_inicio), 0) * 100`
   - `registros`: `COUNT(*)`

Respuesta:
```json
{
  "kpis": [
    {
      "id": 1,
      "nombre": "Toneladas Despachadas",
      "valor": 1234.5,
      "unidad": "TN",
      "icono": "truck",
      "es_principal": true,
      "variacion_porcentual": 12.3  // vs periodo anterior equivalente
    }
  ],
  "filtros_aplicados": { "tipo_proceso": "CARGA", "movil": null, "fecha_desde": "...", "fecha_hasta": "..." }
}
```

**2.2 GET `/api/dashboard/evolucion`**

Mismos filtros. Devuelve la evolución temporal del KPI principal agrupado por día:
```json
{
  "labels": ["2025-01-01", "2025-01-02", ...],
  "datasets": [
    { "nombre": "Toneladas", "valores": [45.2, 38.7, ...] }
  ]
}
```

**2.3 GET `/api/dashboard/ranking-maquinas`**

Mismos filtros. Devuelve un ranking de máquinas por el KPI principal:
```json
[
  { "patente": "AB123CD", "detalle": "Harvester John Deere", "valor": 450.2, "registros": 12 },
  ...
]
```

**2.4 GET `/api/dashboard/tipos-proceso-disponibles`**

Parámetro: `un_id: int`
Devuelve los tipos de proceso disponibles para la UN dada (join con `unidadnegocio_tipo_proceso`).

**2.5 GET `/api/dashboard/moviles-disponibles`**

Parámetro: `un_id: int`, `tipo_proceso_id: int | None`
Devuelve máquinas que tienen registros en `tablero_produccion` para esa UN/proceso.

Crear también los modelos SQLAlchemy necesarios en `backend/app/models/dashboard.py` y los schemas Pydantic en `backend/app/schemas/dashboard.py`. Registrar el router en `main.py` con prefijo `/api`.

---

### TAREA 3 — STORE PINIA

Crear `frontend/src/stores/dashboard.js`:

```js
// Estado:
// - kpis: [], evolucion: {}, rankingMaquinas: []
// - filtros: { un_id, tipo_proceso_id, movil_id, fecha_desde, fecha_hasta }
// - tiposProceso: [], movilesDisponibles: []
// - loading: { kpis, evolucion, ranking }

// Actions:
// - loadTiposProceso(unId)
// - loadMovilesDisponibles(unId, tipoProcesoId)
// - fetchKpis()  → llama /api/dashboard/kpis con filtros actuales
// - fetchEvolucion()
// - fetchRanking()
// - fetchAll()  → fetchKpis + fetchEvolucion + fetchRanking en paralelo
// - setFiltro(campo, valor) → actualiza filtros y llama fetchAll()
```

---

### TAREA 4 — VISTA DASHBOARD

Crear `frontend/src/views/DashboardView.vue` con un **dashboard interactivo y profesional** que respete el design system existente (colores `--color-primary`, `--color-primary-dark`, `--color-neutral-*`, etc. definidos en `style.css`).

**Estructura de la vista:**

**4.1 Barra de Filtros** (sticky en desktop, colapsable en mobile):
- Selector "Tipo de Proceso" (dropdown con los tipos de la UN del usuario)
- Selector "Máquina/Equipo" (dropdown, se actualiza al cambiar tipo de proceso)
- Rango de fechas: inputs `fecha_desde` y `fecha_hasta` con valores por defecto al mes actual
- Botón "Limpiar filtros"
- Badge contador de filtros activos

**4.2 KPI Cards (Hero Section)**:
- El KPI principal (`es_principal: true`) ocupa una card grande estilo "hero" con:
  - Valor grande y prominente con la unidad
  - Ícono Lucide correspondiente
  - Indicador de variación vs período anterior (verde ↑ / rojo ↓ con porcentaje)
- Las demás KPIs se muestran en una grilla responsive (2 cols mobile, 3-4 desktop) con cards compactas
- Cada card tiene: ícono, nombre, valor + unidad, variación

**4.3 Gráfico de Evolución Temporal**:
- Implementarlo con SVG puro (NO usar librerías externas de charts)
- Gráfico de línea/área con la evolución diaria del KPI principal
- Eje X: fechas, Eje Y: valores
- Tooltip al hacer hover sobre los puntos
- Área bajo la curva con gradiente en `--color-primary` semitransparente
- Título dinámico según KPI seleccionado

**4.4 Ranking de Máquinas**:
- Lista rankeada con número de posición
- Barra de progreso relativa al máximo para comparación visual
- Patente de la máquina como título, detalle como subtítulo
- Valor del KPI y cantidad de registros

**4.5 Estado vacío y loading**:
- Skeletons animados mientras cargan los datos (usar `animate-pulse` de Tailwind)
- Estado vacío con ilustración SVG inline y mensaje cuando no hay datos para los filtros aplicados

**Requisitos de UX/UI:**
- Transiciones suaves al cambiar filtros (los números deben animarse con conteo)
- El dashboard debe ser **100% funcional sin librerías de gráficos externas**
- Responsive: mobile-first, se ve bien desde 320px
- Los KPI cards deben tener micro-interacciones al hover
- Usar `lucide-vue-next` para todos los íconos
- Paleta de colores: usar estrictamente las variables CSS ya definidas en `style.css`
- El encargado solo ve datos de **su propia unidad de negocio** (leer `authStore.user.unidad_negocio`)

---

### TAREA 5 — INTEGRACIÓN EN LA APP

**5.1** Agregar la ruta en `frontend/src/router/index.js`:
```js
{
  path: '/dashboard',
  name: 'dashboard',
  component: () => import('../views/DashboardView.vue'),
  meta: { requiresAuth: true, requiresEncargado: true }
}
```

Actualizar el guard de navegación para redirigir si `user.encargado !== 1`.

**5.2** Agregar el ítem de navegación "Dashboard" tanto en la barra de desktop (`App.vue`) como en la barra inferior mobile, **solo visible si `authStore.user?.encargado === 1`**.

Usar este ícono SVG para el nav:
```html
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
  <rect x="3" y="3" width="7" height="7" rx="1"/>
  <rect x="14" y="3" width="7" height="7" rx="1"/>
  <rect x="3" y="14" width="7" height="7" rx="1"/>
  <rect x="14" y="14" width="7" height="7" rx="1"/>
</svg>
```

**5.3** En `HomeView.vue`, si el usuario es encargado, agregar un segundo botón "Ver Dashboard" debajo del botón de carga.

---

### TAREA 6 — SEGURIDAD Y VALIDACIONES

- Todos los endpoints de `/api/dashboard/*` deben verificar que el `un_id` recibido **coincide con la unidad de negocio del usuario autenticado** (extraer del JWT). Si no coincide, devolver 403.
- Implementar una dependencia FastAPI `get_current_user` que decodifique el JWT (usando `verify_token` de `core/security.py`) e inyecte el usuario actual.
- Los endpoints deben devolver 403 si `user.encargado != 1`.

---

### CONVENCIONES A RESPETAR

- **Python**: snake_case, type hints, Pydantic v2
- **Vue**: Composition API con `<script setup>`, `defineProps`, `defineEmits`
- **Tailwind**: Solo clases utilitarias del design system ya configurado. Las variables de color se acceden como `text-primary`, `bg-primary-dark`, etc.
- **Nombres de archivos**: snake_case para Python, PascalCase para componentes Vue
- **No instalar dependencias nuevas** salvo que sean estrictamente necesarias y justificadas
- Mantener coherencia visual y estructural con los componentes ya existentes (`SectionCard.vue`, `InputField.vue`)

---

### ORDEN DE IMPLEMENTACIÓN SUGERIDO

1. `migrations_kpi.sql`
2. Modelos SQLAlchemy (`dashboard.py`)
3. Schemas Pydantic (`dashboard.py`)
4. Endpoints FastAPI (`dashboard.py`) + registro en `main.py`
5. Store Pinia (`dashboard.js`)
6. Vista `DashboardView.vue`
7. Integración en router y `App.vue`