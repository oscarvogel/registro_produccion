# Evidencia visual — Issue #184 (Caminos: composición del total del turno)

Capturas del paso "Datos de Producción" del formulario de la UN **Caminos** con el texto
ajustado de la composición del turno (issue #184, follow-up de #181).

## Qué cambió respecto de las capturas del issue #181

El bloque informativo pasó de esto:

```text
Total del turno: 12 h
Jornada 6 h + horas no operativas 0 h + horas a disposición 6 h.
```

a esto:

```text
Total del turno: 12 h
No operativas 0 h + trabajadas (horómetro) 6 h + a disposición 6 h.
Las horas de perfilado se trabajan pero no se anotan como horas: ya van dentro de las trabajadas.
Es un cálculo, no un dato a cargar: sirve para ver si el turno cuadra.
```

El **número no cambia**: el total sigue siendo `jornada + hrs_no_op + hrs_disposicion`, que
equivale a `no operativas + (remolque + perfilado) + disposición` porque la jornada (horómetro)
*es* las horas trabajadas.

## Cómo se generaron

Sin tocar datos productivos: la app se levantó con **Vite en modo mock** (sin base de datos)
replicando el catálogo real de la UN Caminos leído de `fg` con un `SELECT`:

| Tipo de proceso | id | requiere acta | requiere predio |
| --- | --- | --- | --- |
| PERFILADO | 9 | sí | sí |
| DISPOSICION | 22 | sí | sí |
| REMOLQUE | 23 | no | sí |

Datos del parte de la captura (mismo caso real del 22/10/2026, MOTON-Nº2):

- Horómetro: `8286` → `8292` (6 h de jornada = horas trabajadas)
- Proceso DISPOSICION: 6 h a disposición
- Proceso REMOLQUE: 6 h de remolque
- Horas no operativas: 0
- **Total del turno: 12 h**

## Archivos

| Archivo | Qué muestra |
| --- | --- |
| `1638x969-05-produccion.png` | Paso 6 en la resolución del cliente (1638x969) |
| `1638x969-05-produccion-full.png` | Lo mismo, con la página completa |
| `1638x969-08-revision.png` | Paso 9 "Revisión" |
| `1366x768-05-produccion.png` | Paso 6 en pantalla chica (1366x768) |
| `1366x768-05-produccion-full.png` | Lo mismo, con la página completa |
| `1366x768-08-revision.png` | Paso 9 "Revisión" |
| `390x844-05-produccion-full.png` | Paso 6 en móvil (390x844) |
| `390x844-08-revision.png` | Paso 9 "Revisión" |

## Qué hay que mirar

1. La composición se lee con el vocabulario de la regla: **no operativas + trabajadas
   (horómetro) + a disposición**.
2. La nota aclara que **las horas de perfilado se trabajan pero no se anotan como horas** y que
   ya van dentro de las trabajadas.
3. El total sigue siendo 12 h y las horas de remolque no se suman (van dentro de la jornada).
4. En ninguna resolución los textos se superponen ni quedan recortados.
