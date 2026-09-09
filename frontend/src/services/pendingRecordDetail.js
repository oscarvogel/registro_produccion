export function buildCaminosProcessGroups(payload = {}) {
  const procesos = Array.isArray(payload?.procesos) ? payload.procesos : []

  return procesos.map((proceso, index) => {
    const label = String(proceso?.operacion || proceso?.nombre || '').trim()
    const fields = [
      detailField('tipo_proceso_id', 'Tipo de proceso ID', proceso?.tipo_proceso_id, 'number'),
      detailField('predio', 'Predio', proceso?.predio),
      detailField('acta', 'Acta', proceso?.acta),
      detailField('rodal', 'Rodal', proceso?.rodal),
      detailField('km_perfilado', 'Kilómetros de perfilado', proceso?.km_perfilado, 'number'),
      detailField('hr_disposicion', 'Horas a disposición', proceso?.hr_disposicion, 'number'),
      detailField('hr_remolque', 'Horas de remolque', proceso?.hr_remolque, 'number'),
    ].filter((field) => hasDetailValue(field.value))

    return {
      key: `proceso-${index + 1}`,
      title: label ? `Proceso ${index + 1}: ${label}` : `Proceso ${index + 1}`,
      fields,
    }
  }).filter((group) => group.fields.length > 0)
}

function detailField(key, label, value, type = 'text') {
  return { key, label, value, type }
}

function hasDetailValue(value) {
  return value !== null && value !== undefined && value !== '' && value !== 0 && value !== '0'
}
