# Evidencia visual — Issue #181 (Caminos: horas a disposición y total del turno)

Capturas del formulario de la UN **Caminos** (`CaminosFormView.vue`) con los cambios del
issue #181: texto de ayuda en "Horas a disposición" y "Horas de remolque", y el bloque
informativo "Total del turno".

## Cómo se generaron

Sin tocar datos productivos: la app se levantó con **Vite en modo mock** (sin base de
datos) replicando el catálogo real de la UN Caminos leído de `fg` con un `SELECT`:

| Tipo de proceso | id | requiere acta | requiere predio |
| --- | --- | --- | --- |
| PERFILADO | 9 | sí | sí |
| DISPOSICION | 22 | sí | sí |
| REMOLQUE | 23 | no | sí |

Datos del parte de la captura (mismo caso real del 22/10/2026, MOTON-Nº2):

- Horómetro: `8286` → `8292` (jornada de 6 h)
- Proceso DISPOSICION: 6 h a disposición
- Proceso REMOLQUE: 6 h de remolque
- Horas no operativas: 0
- **Total del turno: 12 h** (6 h de jornada + 0 h no operativas + 6 h a disposición)

## Archivos

| Archivo | Qué muestra |
| --- | --- |
| `1638x969-05-produccion.png` | Paso 6 "Datos de Producción" en la resolución del cliente: las dos ayudas y el total del turno |
| `1638x969-05-produccion-full.png` | Lo mismo, con la página completa |
| `1638x969-08-revision.png` | Paso 9 "Revisión": el tile "Total del turno" |
| `1366x768-05-produccion.png` | Paso 6 en pantalla chica (1366x768) |
| `1366x768-05-produccion-full.png` | Lo mismo, con la página completa |
| `1366x768-08-revision.png` | Paso 9 "Revisión" en pantalla chica |
| `390x844-05-produccion-full.png` | Paso 6 en móvil (390x844) |
| `390x844-08-revision.png` | Paso 9 "Revisión" en móvil |

## Qué hay que mirar

1. La ayuda de **Horas a disposición** dice que es el complemento del turno y que no son
   horas de trabajo.
2. La ayuda de **Horas de remolque** dice que van dentro de la jornada.
3. El bloque **Total del turno** muestra 12 h y el detalle de cómo se compone. Las horas de
   remolque **no** se suman: siguen dentro de la jornada.
4. En ninguna resolución los textos se superponen ni quedan recortados.
