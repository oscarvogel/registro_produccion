<template>
  <div class="mx-auto max-w-6xl px-3 py-3 pb-20 md:px-4 md:pt-4">
    <PageHeader
      title="Carga de Combustible"
      description="Registro independiente de cargas por movil y operador."
    >
      <template #kicker>
        <span class="rounded-full bg-warning-light/60 px-3 py-1 text-xs font-extrabold uppercase tracking-wide text-warning-dark">
          Combustible
        </span>
        <span class="rounded-full bg-neutral-100 px-3 py-1 text-xs font-extrabold text-neutral-600">
          {{ unidadLabel }}
        </span>
      </template>
    </PageHeader>

    <div class="mt-3 grid gap-3 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <SectionCard title="Nueva carga">
        <form class="space-y-3" @submit.prevent="submit">
          <div v-if="store.error || formError" class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">
            {{ formError || store.error }}
          </div>

          <div v-if="successMessage" class="rounded-lg border border-success/30 bg-success-light/40 p-3 text-sm font-semibold text-success-dark">
            {{ successMessage }}
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
              required
            />

            <InputField
              v-model.number="form.km"
              label="Kilometraje / horometro"
              type="number"
              required
            />
          </div>

          <label class="block">
            <span class="mb-1 block text-sm font-medium text-neutral-700">Observaciones</span>
            <textarea
              v-model="form.observaciones"
              rows="3"
              class="w-full rounded-xl border border-neutral-300 bg-neutral-100 px-4 py-2.5 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30"
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

        <SectionCard v-if="store.lastCarga" title="Ultima carga">
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
import { computed, onMounted, reactive, ref } from 'vue'
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
const form = reactive({
  fecha: today,
  id_movil: '',
  litros: '',
  km: '',
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

onMounted(() => {
  store.fetchMoviles()
})

function validateForm() {
  if (!form.fecha) return 'Selecciona la fecha de carga.'
  if (!form.id_movil) return 'Selecciona un equipo o movil.'
  if (!Number(form.litros) || Number(form.litros) <= 0) return 'Ingresa una cantidad de litros mayor a cero.'
  if (form.km === '' || Number(form.km) < 0) return 'Ingresa kilometraje u horometro valido.'
  return ''
}

function resetForm() {
  form.fecha = today
  form.id_movil = ''
  form.litros = ''
  form.km = ''
  form.observaciones = ''
  formError.value = ''
  successMessage.value = ''
}

async function submit() {
  formError.value = validateForm()
  successMessage.value = ''
  if (formError.value) return

  try {
    const carga = await store.createCarga({
      fecha: form.fecha,
      id_movil: Number(form.id_movil),
      litros: Number(form.litros),
      km: Number(form.km),
      observaciones: form.observaciones?.trim() || null,
    })
    successMessage.value = `Carga registrada para ${carga.movil}.`
    form.id_movil = ''
    form.litros = ''
    form.km = ''
    form.observaciones = ''
  } catch {
    formError.value = store.error
  }
}
</script>
