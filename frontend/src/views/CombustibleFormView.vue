<template>
  <div class="mx-auto max-w-6xl px-3 py-3 pb-20 md:px-4 md:pt-4">
    <PageHeader
      title="Carga de Combustible"
      description="Abastecimientos sin parte de producción, con lectura real del equipo."
    >
      <template #kicker>
        <span class="rounded-full bg-warning-light/60 px-3 py-1 text-xs font-extrabold uppercase tracking-wide text-warning-dark">
          Combustible
        </span>
        <span class="rounded-full border px-3 py-1 text-xs font-extrabold app-state-inactive">
          {{ unidadLabel }}
        </span>
      </template>
    </PageHeader>

    <div class="mt-3 grid gap-3 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <SectionCard title="Nueva carga">
        <form class="space-y-3" @submit.prevent="submit">
          <div v-if="store.error || formError" class="rounded-lg border border-error/35 bg-error-light/30 p-3 text-sm font-semibold text-error-dark">
            {{ formError || store.error }}
          </div>

          <div v-if="successMessage" class="rounded-lg border border-success/30 bg-success-light/40 p-3 text-sm font-semibold text-success-dark">
            {{ successMessage }}
          </div>

          <div class="rounded-lg border border-info/30 bg-info-light/40 p-3 text-sm text-info-dark">
            Usá esta sección sólo cuando el abastecimiento no esté asociado a un parte de producción. Si lo registraste en Producción, no lo repitas aquí.
          </div>

          <div class="grid gap-3 md:grid-cols-2">
            <InputField
              v-model="form.fecha"
              label="Fecha de carga"
              type="date"
              required
            />

            <div>
              <AutocompleteField
                v-model="form.id_movil"
                :items="movilOptions"
                label="Equipo / movil"
                labelKey="_label"
                valueKey="idMovil"
                placeholder="Buscar por patente o detalle"
                selectedDisplay="input"
                :disabled="store.loadingMoviles"
                :invalid="Boolean(formError && !form.id_movil)"
              />
              <p class="mt-1 text-xs font-semibold text-neutral-400">
                {{ store.loadingMoviles ? 'Cargando moviles...' : `${movilOptions.length} moviles disponibles` }}
              </p>
            </div>

            <InputField
              v-model.number="form.litros"
              label="Litros"
              type="number"
              min="0.01"
              step="0.01"
              required
            />

            <InputField
              v-model.number="form.km"
              label="Kilometraje / horometro"
              type="number"
              min="1"
              required
            />

            <div class="md:col-span-2">
              <AutocompleteField
                v-model="form.id_lugar_carga"
                :items="store.lugaresCarga"
                label="Lugar de carga"
                labelKey="detalle"
                valueKey="idLugarCarga"
                placeholder="Seleccionar lugar"
                selectedDisplay="input"
                :disabled="!form.id_movil || store.loadingLugares"
                :loading="store.loadingLugares"
                :invalid="Boolean(formError && !form.id_lugar_carga)"
                emptyMessage="Sin lugares habilitados para la unidad del equipo"
              />
            </div>
          </div>

          <div class="grid gap-3 sm:grid-cols-3">
            <InputField
              v-model="form.remito"
              label="Remito 1"
              placeholder="Obligatorio"
              maxlength="12"
              required
              :invalid="Boolean(formError && !form.remito.trim())"
            />
            <InputField
              v-model="form.remito2"
              label="Remito 2"
              placeholder="Opcional"
              maxlength="12"
            />
            <InputField
              v-model="form.remito3"
              label="Remito 3"
              placeholder="Opcional"
              maxlength="12"
            />
          </div>

          <label class="block">
            <span class="mb-1 block text-sm font-medium text-neutral-700">Observaciones</span>
            <textarea
              v-model="form.observaciones"
              rows="3"
              class="app-input min-h-10 w-full rounded-lg border px-3 py-2 text-sm placeholder:text-neutral-400 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30 sm:px-3.5"
              placeholder="Opcional"
            ></textarea>
          </label>

          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-end">
            <AppButton type="button" variant="secondary" @click="resetForm">
              <AppIcon name="retry" size="sm" />
              Limpiar
            </AppButton>
            <AppButton :loading="store.saving" type="submit">
              <AppIcon name="save" size="sm" />
              Registrar carga
            </AppButton>
          </div>
        </form>
      </SectionCard>

      <aside class="space-y-3">
        <SectionCard title="Operador">
          <div class="space-y-3 text-sm">
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Nombre</p>
              <p class="mt-1 font-extrabold text-neutral-900">{{ authStore.userName }}</p>
            </div>
            <div>
              <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Unidades habilitadas</p>
              <p class="mt-1 font-semibold text-neutral-700">{{ unidadLabel }}</p>
            </div>
          </div>
        </SectionCard>

        <SectionCard v-if="store.lastCarga" title="Última carga">
          <div class="space-y-2 text-sm text-neutral-700">
            <p><strong>{{ store.lastCarga.movil }}</strong></p>
            <p>{{ Number(store.lastCarga.litros).toLocaleString('es-AR') }} L</p>
            <p>KM/HM {{ Number(store.lastCarga.km).toLocaleString('es-AR') }}</p>
          </div>
        </SectionCard>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCombustibleStore } from '@/stores/combustible'
import AutocompleteField from '@/components/AutocompleteField.vue'
import InputField from '@/components/InputField.vue'
import SectionCard from '@/components/SectionCard.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const authStore = useAuthStore()
const store = useCombustibleStore()
const formError = ref('')
const successMessage = ref('')

const today = new Date().toISOString().slice(0, 10)
const createFormUuid = () => (
  globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
)
const form = reactive({
  form_uuid: createFormUuid(),
  fecha: today,
  id_movil: '',
  litros: '',
  km: '',
  id_lugar_carga: '',
  remito: '',
  remito2: '',
  remito3: '',
  observaciones: '',
})

const unidadLabel = computed(() => {
  const ids = Array.isArray(authStore.user?.unidad_ids) && authStore.user.unidad_ids.length
    ? authStore.user.unidad_ids
    : [authStore.user?.unidad_negocio].filter(Boolean)
  return ids.length ? `UN ${ids.join(', ')}` : 'Sin unidad asignada'
})

const movilOptions = computed(() => store.moviles.map((movil) => ({
  ...movil,
  _label: [movil.patente, movil.detalle].filter(Boolean).join(' - '),
})))

const movilSeleccionado = computed(() => (
  store.moviles.find((movil) => String(movil.idMovil) === String(form.id_movil))
))

onMounted(() => {
  store.fetchMoviles()
})

watch(() => form.id_movil, async () => {
  form.id_lugar_carga = ''
  await store.fetchLugaresCarga(movilSeleccionado.value?.id_unidad_negocio)
})

function validateForm() {
  if (!form.fecha) return 'Selecciona la fecha de carga.'
  if (!form.id_movil) return 'Selecciona un equipo o movil.'
  if (!Number(form.litros) || Number(form.litros) <= 0) return 'Ingresa una cantidad de litros mayor a cero.'
  if (!Number(form.km) || Number(form.km) <= 0) return 'Ingresa un kilometraje u horometro mayor a cero.'
  if (!form.id_lugar_carga) return 'Selecciona el lugar de carga.'
  if (!form.remito.trim()) return 'Ingresa el Remito 1.'
  return ''
}

function clearFormFields() {
  form.form_uuid = createFormUuid()
  form.fecha = today
  form.id_movil = ''
  form.litros = ''
  form.km = ''
  form.id_lugar_carga = ''
  form.remito = ''
  form.remito2 = ''
  form.remito3 = ''
  form.observaciones = ''
}

function resetForm() {
  clearFormFields()
  formError.value = ''
  successMessage.value = ''
}

async function submit() {
  formError.value = validateForm()
  successMessage.value = ''
  if (formError.value) return

  try {
    const carga = await store.createCarga({
      form_uuid: form.form_uuid,
      fecha: form.fecha,
      id_movil: Number(form.id_movil),
      litros: Number(form.litros),
      km: Number(form.km),
      id_lugar_carga: Number(form.id_lugar_carga),
      id_tipo_comb: 1,
      remito: form.remito.trim(),
      remito2: form.remito2.trim(),
      remito3: form.remito3.trim(),
      observaciones: form.observaciones?.trim() || null,
    })
    successMessage.value = `Carga registrada para ${carga.movil}.`
    clearFormFields()
  } catch {
    formError.value = store.error
  }
}
</script>
