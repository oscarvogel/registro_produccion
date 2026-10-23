# Revisión visual — Issue #184 · Caminos: composición del total del turno

## Datos

- **Fecha**: 23/10/2026
- **Issue**: [#184](https://github.com/oscarvogel/registro_produccion/issues/184) (follow-up de [#181](https://github.com/oscarvogel/registro_produccion/issues/181))
- **Rama**: `codex/issue-184-composicion-turno`
- **Base**: `origin/main` (`13a6984`, el merge de #182)

## Por qué el cambio

La regla de negocio confirmada por Oscar el 23/10/2026 es:

```text
turno = horas no operativas + horas trabajadas + horas a disposición
horas trabajadas = horas de remolque + horas de perfilado
```

Las horas de perfilado **se trabajan pero no se anotan como horas** (el perfilado se carga en
km). El texto anterior ("Jornada 6 h + horas no operativas 0 h + horas a disposición 6 h")
decía "Jornada" sin decir que esas son las horas trabajadas, y no aclaraba que las horas de
perfilado ya están adentro. El número del total no cambia.

## Comandos ejecutados

```bash
# Frontend
npm ci
npm test                    # 53 files / 326 tests passed
npm run check               # vite build OK

# Backend
python -m pytest            # 294 passed

# Repo
git diff --check
```

## Flujo probado

Formulario de la UN Caminos completo, con el catálogo real de la UN replicado en mock (sin
base de datos): Contexto → Operador → Equipo → Procesos (DISPOSICION + REMOLQUE) → Control de
tiempo (horómetro `8286` → `8292`) → Datos de producción (6 h a disposición + 6 h de remolque,
predio y acta) → Revisión (total del turno = 12 h).

## Capturas

En `docs/screenshots/issue-184-composicion-turno/` (ver el README de esa carpeta).

| Resolución | Resultado |
| --- | --- |
| 1638x969 (pantalla del cliente) | La composición y la nota de perfilado se ven completas, sin superposición ni recorte |
| 1366x768 | Ídem: el contenido se ve bien y la página scrollea normal |
| 390x844 (móvil) | Ídem: textos legibles y el bloque visible |

## Hallazgos

- **Errores de consola durante la captura**: ninguno.
- No se detectó ningún solapamiento ni recorte de los textos en ninguna de las tres
  resoluciones.
- Recordatorio de la verificación: en dev el service worker de la PWA intercepta los catálogos
  y hay que bloquearlo (`serviceWorkers: 'block'`) para poder mockear; y el login tiene dos
  formularios con breakpoint `lg` (1024px), así que hay que elegir el campo por ancho de
  viewport y no por visibilidad.

## Veredicto

**Aprobado visualmente.**

## Pendientes

- El total del turno **se muestra, no se deriva**. Derivarlo requiere que la duración del
  turno exista como dato; la opción que mejor encaja con la regla es **registrar las horas de
  perfilado** (hoy no existen). Queda en [#183](https://github.com/oscarvogel/registro_produccion/issues/183).
