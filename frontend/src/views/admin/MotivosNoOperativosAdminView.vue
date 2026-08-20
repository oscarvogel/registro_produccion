<template>
  <div class="space-y-3">
    <PageHeader
      kicker="Administración"
      title="Motivos no operativos"
      description="Agregá motivos y definí en qué unidades de negocio están disponibles."
    >
      <template #actions>
        <AppButton variant="secondary" :loading="loading" @click="load">Refrescar</AppButton>
        <AppButton @click="openCreate">Nuevo motivo</AppButton>
      </template>
    </PageHeader>

    <SectionCard title="Catálogo">
      <div class="mb-3 flex flex-col gap-2 sm:flex-row">
        <input v-model="buscar" class="app-input min-h-10 flex-1 rounded-lg border px-3 py-2" placeholder="Buscar motivo" />
        <select v-model="filtroUnidad" class="app-input min-h-10 rounded-lg border px-3 py-2 sm:w-64">
          <option value="">Todas las unidades</option>
          <option v-for="unidad in unidades" :key="unidad.idUnidadNegocio" :value="unidad.idUnidadNegocio">{{ unidad.nombre }}</option>
        </select>
      </div>

      <div v-if="error" class="mb-3 rounded-lg border border-error/25 bg-error-light/30 p-3 text-sm font-semibold text-error-dark">{{ error }}</div>
      <div v-if="loading" class="py-6 text-center text-sm text-neutral-500">Cargando...</div>
      <div v-else class="space-y-2">
        <article v-for="motivo in motivos" :key="motivo.id" class="app-card flex flex-col gap-3 rounded-xl p-3 sm:flex-row sm:items-center sm:justify-between">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <strong class="text-sm text-neutral-900">{{ motivo.nombre }}</strong>
              <span :class="motivo.activo ? 'app-state-success' : 'app-state-inactive'" class="rounded-full border px-2 py-0.5 text-xs font-bold">
                {{ motivo.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <p class="mt-1 text-xs text-neutral-500">{{ unidadLabels(motivo.unidad_ids) }}</p>
          </div>
          <div class="flex gap-2">
            <AppButton variant="secondary" @click="openEdit(motivo)">Editar</AppButton>
            <AppButton :variant="motivo.activo ? 'danger' : 'secondary'" @click="toggleActivo(motivo)">
              {{ motivo.activo ? 'Desactivar' : 'Activar' }}
            </AppButton>
          </div>
        </article>
        <p v-if="motivos.length === 0" class="py-6 text-center text-sm text-neutral-500">No hay motivos para estos filtros.</p>
      </div>
    </SectionCard>

    <AppModal v-model="showForm" :title="editingId ? 'Editar motivo' : 'Nuevo motivo'" description="El motivo puede habilitarse para una o varias unidades de negocio.">
      <div class="space-y-4">
        <InputField v-model="form.nombre" label="Motivo" required placeholder="Ej: FALLA MECANICA" />
        <label class="flex items-center gap-2 text-sm font-semibold text-neutral-700">
          <input v-model="form.activo" type="checkbox" class="h-4 w-4 accent-primary" /> Activo
        </label>
        <div>
          <p class="mb-2 text-sm font-semibold text-neutral-700">Unidades de negocio</p>
          <div class="app-surface-muted grid gap-2 rounded-lg border p-3 sm:grid-cols-2">
            <label v-for="unidad in unidades" :key="unidad.idUnidadNegocio" class="flex items-center gap-2 text-sm text-neutral-700">
              <input
                type="checkbox"
                class="h-4 w-4 accent-primary"
                :checked="form.unidad_ids.includes(Number(unidad.idUnidadNegocio))"
                @change="toggleUnidad(unidad.idUnidadNegocio, $event.target.checked)"
              />
              {{ unidad.nombre }}
            </label>
          </div>
        </div>
        <div v-if="formError" class="rounded-lg border border-error/25 bg-error-light/30 p-3 text-sm font-semibold text-error-dark">{{ formError }}</div>
        <div class="flex justify-end gap-2">
          <AppButton variant="secondary" @click="showForm = false">Cancelar</AppButton>
          <AppButton :loading="saving" @click="save">Guardar</AppButton>
        </div>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import api from '@/services/api'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import InputField from '@/components/InputField.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionCard from '@/components/SectionCard.vue'

const motivos = ref([])
const unidades = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const formError = ref('')
const buscar = ref('')
const filtroUnidad = ref('')
const showForm = ref(false)
const editingId = ref(null)
const form = reactive({ nombre: '', activo: true, unidad_ids: [] })
let timer = null

function safeMessage(err, fallback) { return err?.response?.data?.detail || fallback }
function unidadLabels(ids) {
  const labels = unidades.value.filter(u => (ids || []).includes(Number(u.idUnidadNegocio))).map(u => u.nombre)
  return labels.length ? labels.join(' · ') : 'Sin unidades asignadas'
}
function resetForm() { form.nombre = ''; form.activo = true; form.unidad_ids = unidades.value.map(u => Number(u.idUnidadNegocio)); formError.value = '' }
function openCreate() { editingId.value = null; resetForm(); showForm.value = true }
function openEdit(motivo) { editingId.value = motivo.id; form.nombre = motivo.nombre; form.activo = Boolean(motivo.activo); form.unidad_ids = [...(motivo.unidad_ids || [])].map(Number); formError.value = ''; showForm.value = true }
function toggleUnidad(id, checked) { const value = Number(id); if (checked && !form.unidad_ids.includes(value)) form.unidad_ids.push(value); if (!checked) form.unidad_ids = form.unidad_ids.filter(x => x !== value) }

async function loadUnidades() {
  const { data } = await api.get('/api/admin/unidades-negocio', { params: { skip: 0, limit: 1000 }, _suppressErrorToast: true })
  unidades.value = Array.isArray(data) ? data : []
}
async function load() {
  loading.value = true; error.value = ''
  try {
    const params = { skip: 0, limit: 1000 }
    if (buscar.value.trim()) params.buscar = buscar.value.trim()
    if (filtroUnidad.value) params.unidad_id = Number(filtroUnidad.value)
    const { data } = await api.get('/api/admin/motivos-no-operativos', { params, _suppressErrorToast: true })
    motivos.value = Array.isArray(data) ? data : []
  } catch (err) { motivos.value = []; error.value = safeMessage(err, 'No se pudieron cargar los motivos') }
  finally { loading.value = false }
}
async function save() {
  if (!form.nombre.trim()) { formError.value = 'Ingresá el nombre del motivo'; return }
  saving.value = true; formError.value = ''
  const payload = { nombre: form.nombre.trim(), activo: Boolean(form.activo), unidad_ids: form.unidad_ids }
  try {
    if (editingId.value) await api.put(`/api/admin/motivos-no-operativos/${editingId.value}`, payload)
    else await api.post('/api/admin/motivos-no-operativos', payload)
    showForm.value = false
    await load()
  } catch (err) { formError.value = safeMessage(err, 'No se pudo guardar el motivo') }
  finally { saving.value = false }
}
async function toggleActivo(motivo) {
  try {
    await api.put(`/api/admin/motivos-no-operativos/${motivo.id}`, { activo: !motivo.activo })
    await load()
  } catch (err) { error.value = safeMessage(err, 'No se pudo actualizar el motivo') }
}
watch([buscar, filtroUnidad], () => { clearTimeout(timer); timer = setTimeout(load, 250) })
onMounted(async () => { try { await loadUnidades(); await load() } catch (err) { error.value = safeMessage(err, 'No se pudo cargar la gestión de motivos') } })
</script>
