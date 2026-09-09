# Contexto de agentes y arquitectura

Este documento define cómo deben trabajar los agentes de desarrollo en `registro_produccion/`.
Es de cumplimiento obligatorio para cambios de backend, API, persistencia y reglas de negocio.

## Reglas obligatorias

1. Usar la skill `clean-ddd-hexagonal` en toda tarea que diseñe, modifique o migre lógica de backend.
2. Aplicar Clean Architecture + DDD + Hexagonal Architecture:
   - las dependencias apuntan hacia el dominio;
   - el dominio no importa FastAPI, SQLAlchemy, Pydantic, HTTP, filesystem ni servicios externos;
   - los casos de uso coordinan la operación;
   - las rutas HTTP son adaptadores de entrada;
   - la base de datos y las integraciones son adaptadores de salida;
   - los puertos son contratos, no implementaciones concretas.
3. Aplicar SOLID en cada diseño:
   - **S**: cada módulo, clase o función tiene una sola responsabilidad;
   - **O**: extender mediante puertos y estrategias sin modificar reglas estables;
   - **L**: toda implementación respeta el contrato de su abstracción;
   - **I**: interfaces pequeñas y orientadas al caso de uso;
   - **D**: el dominio y la aplicación dependen de abstracciones, no de infraestructura.
4. No crear un `repository` por tabla automáticamente. Crear repositorios por aggregate root.
5. No permitir que un controlador llame directamente a una sesión SQLAlchemy o a un repositorio.
6. No compartir entidades internas entre bounded contexts. Cruzar contextos mediante IDs, DTOs,
   eventos de dominio o un anti-corruption layer cuando sea necesario.
7. No introducir CQRS, Event Sourcing, microservicios ni un bus de eventos como patrón por defecto.
   Se adoptan únicamente si existe una necesidad concreta y documentada.
8. Mantener los cambios incrementales. El código legado puede permanecer temporalmente, pero todo
   código nuevo o migrado debe acercarse a estas reglas y no aumentar el acoplamiento existente.
9. Una regla de negocio debe vivir en el dominio o en un caso de uso, no duplicarse en rutas,
   schemas, stores de Vue y consultas SQL.
10. Cada cambio de comportamiento debe incluir pruebas proporcionales: dominio sin infraestructura,
    casos de uso con dobles de prueba y, cuando corresponda, integración HTTP/persistencia.
11. Las pruebas visuales de cambios frontend son obligatorias y deben ejecutarse en Microsoft Edge.

## Agentes y bounded contexts

Cada agente debe trabajar dentro de un único bounded context principal. Antes de modificar archivos,
debe identificar el contexto dueño de la regla y declarar cualquier dependencia con otro contexto.

### Agente de arquitectura y límites

- **Bounded context:** transversal; no es dueño de datos de negocio.
- **Responsabilidad:** mantener el mapa de contextos, los puertos, las reglas de dependencia y la
  composición de adaptadores.
- **Puede tocar:** estructura de módulos, contratos compartidos mínimos, composición de dependencias,
  documentación y pruebas de arquitectura.
- **No puede:** absorber reglas de otros contextos ni crear un modelo global compartido.
- **Criterio de salida:** toda dependencia entre contextos queda explícita y apunta mediante contrato,
  DTO, evento o ACL.

### Agente de identidad y acceso

- **Bounded context:** `Identity & Access`.
- **Responsabilidad:** autenticación, sesión, autorización, roles, estado de acceso y alcance por
  unidad de negocio.
- **Superficie actual:** `api/routes/auth.py`, `api/deps.py`, `core/security.py`, schemas de auth,
  `Personal` y relaciones de personal con unidades.
- **Aggregate roots candidatos:** `Usuario/Personal` y `AsignaciónDeAcceso`.
- **Regla:** los demás contextos consultan una capacidad de autorización mediante un puerto; no
  reimplementan permisos ni leen tablas de usuarios directamente.

### Agente de operación productiva

- **Bounded context:** `Production Operations`.
- **Responsabilidad:** registrar producción, validar el flujo operativo, operadores, asignaciones,
  móviles, procesos y relaciones necesarias para ejecutar una operación.
- **Superficie actual:** `api/routes/produccion.py`, schemas de producción y registros, `Produccion`,
  `AsignacionOperativa`, `MovilOperador`, `Movil` y `TipoDeProceso`.
- **Aggregate root principal:** `RegistroDeProducción`/`TableroProduccion`.
- **Regla:** un registro de producción se valida dentro de este contexto. La identidad, los catálogos
  y la analítica se consumen por puertos o referencias estables, no mediante lógica duplicada.

### Agente de combustible y abastecimiento

- **Bounded context:** `Fuel & Refueling`.
- **Responsabilidad:** cargas de combustible, remitos, idempotencia, lugar de carga habilitado y
  compatibilidad con el móvil o la unidad de negocio.
- **Superficie actual:** `api/routes/combustible.py`, schemas de combustible, `CargaComb` y modelos
  de lugares de carga.
- **Aggregate root principal:** `CargaDeCombustible`.
- **Regla:** la idempotencia y las validaciones de una carga pertenecen a este contexto. No deben
  quedar repartidas entre la ruta FastAPI, el frontend y triggers implícitos.

### Agente de datos maestros y configuración operativa

- **Bounded context:** `Master Data & Operational Configuration`.
- **Responsabilidad:** alta, baja, modificación y vigencia de unidades de negocio, tipos de móvil,
  tipos de proceso, lugares de carga y datos geográficos o documentales administrables.
- **Superficie actual:** rutas `admin_*`, `admin_legacy.py`, schemas de admin y modelos de catálogos,
  incluyendo `UnidadNegocio`, `TipoMovil`, `TipoDeProceso`, `LugarCarga`, `Acta`, `Predio` y `Rodal`.
- **Regla:** este contexto administra el ciclo de vida de los catálogos. Los contextos consumidores
  reciben una proyección o referencia por ID y no modifican catálogos por conveniencia.

### Agente de analítica y reportes

- **Bounded context:** `Analytics & Reporting`.
- **Responsabilidad:** KPIs, evolución, rankings, filtros, dashboards, listados y vistas de lectura
  para administración.
- **Superficie actual:** `api/routes/dashboard.py`, `api/routes/admin_dashboard.py` y modelos de
  dashboard.
- **Regla:** es preferentemente de solo lectura. No debe cambiar aggregates transaccionales ni
  convertirse en el dueño de la lógica de producción. Si necesita una consulta especializada, crear
  una proyección/read model o un puerto de consulta.

### Agente de experiencia y adaptadores frontend

- **Bounded context:** `User Experience` como adaptador del sistema, sin autoridad sobre reglas de
  negocio.
- **Responsabilidad:** vistas Vue, stores Pinia, navegación, estados offline, mensajes y consumo de
  contratos HTTP.
- **Superficie actual:** `frontend/src/views`, `frontend/src/stores`, `frontend/src/services` y
  `frontend/src/router`.
- **Regla:** el frontend no decide permisos, idempotencia, cálculos de producción ni reglas de
  combustible. Debe representar el contrato de la API y delegar la decisión al backend.

## Dependencias permitidas

La dirección válida es:

```text
Adaptadores HTTP / DB / externos
                ↓
          Aplicación
                ↓
             Dominio
```

Dentro de cada bounded context se prefiere esta forma:

```text
backend/app/<contexto>/
├── domain/
│   ├── entities.py
│   ├── value_objects.py
│   ├── services.py
│   ├── events.py
│   └── ports.py
├── application/
│   ├── commands_or_queries.py
│   ├── use_cases.py
│   └── ports.py
└── infrastructure/
    ├── persistence/
    ├── http/
    └── integrations/
```

La estructura puede adaptarse al tamaño del módulo, pero no la dirección de dependencias. La
composición de implementaciones concretas se realiza en el punto de entrada de la aplicación.

## Integración entre contextos

- Usar el lenguaje ubicuo de cada contexto; no reutilizar un nombre porque tenga el mismo nombre de
  tabla.
- Compartir únicamente tipos técnicos muy estables y sin comportamiento de negocio.
- Para una consulta síncrona, definir un puerto de consulta pequeño y devolver un DTO.
- Para consistencia eventual, publicar un evento de dominio en pasado, por ejemplo
  `ProduccionRegistrada` o `CargaDeCombustibleRegistrada`.
- Para integrar un modelo externo o legado, usar un anti-corruption layer; no filtrar sus nombres y
  restricciones hacia el dominio nuevo.
- Una transacción debe tener un único aggregate root como límite principal. La consistencia entre
  aggregates o contextos se resuelve con eventos, compensación o una operación explícita.

## Flujo obligatorio para nuevos cambios

1. Identificar el bounded context dueño y escribir la regla en su lenguaje ubicuo.
2. Separar entidad, value object, aggregate, servicio de dominio y caso de uso según corresponda.
3. Definir primero los puertos y contratos necesarios.
4. Implementar la lógica de dominio sin FastAPI, SQLAlchemy ni Pydantic.
5. Implementar el caso de uso y sus pruebas con dobles de infraestructura.
6. Adaptar la ruta HTTP, schemas y persistencia al caso de uso.
7. Revisar SOLID, dependencias entre contextos y posibles duplicaciones de reglas.
8. Ejecutar `git diff --check`, tests de backend y los tests frontend afectados.
9. Documentar cualquier deuda de migración o excepción temporal en el PR.

## Señales de rechazo

El agente debe detenerse y reportar la decisión si el cambio:

- agrega lógica de negocio directamente en una ruta o componente Vue;
- hace que el dominio importe una librería de infraestructura;
- crea una transacción que modifica aggregates de varios contextos sin una justificación;
- usa una tabla compartida como contrato entre contextos;
- introduce una abstracción genérica que oculta reglas distintas;
- requiere una modificación productiva, migración destructiva o credencial no provista.
