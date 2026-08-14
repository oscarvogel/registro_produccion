<template>
  <div class="mx-auto max-w-5xl px-3 py-4 pb-24 md:px-5">
    <div class="mb-4 flex items-center justify-between gap-3">
      <div>
        <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Unidad de negocio</p>
        <h1 class="text-2xl font-extrabold text-neutral-900">Parte diario · Caminos</h1>
        <p class="mt-1 text-sm text-neutral-500">Un equipo, una jornada y todos los procesos realizados.</p>
      </div>
      <button type="button" class="app-button-soft rounded-xl border px-3 py-2 text-sm font-semibold" @click="$emit('back')">
        Cambiar UN
      </button>
    </div>

    <form class="space-y-4" @submit.prevent="guardar">
      <SectionCard title="Cabecera del parte">
        <div class="grid gap-3 md:grid-cols-2">
          <InputField label="Fecha" type="date" v-model="form.fecha" required />

          <div v-if="canSelectOperador">
            <label class="mb-1 block text-sm font-medium text-neutral-700">Operador</label>
            <select v-model.number="form.cod_operador" :class="fieldClass" required>
              <option :value="0">Seleccionar operador</option>
              <option v-for="item in store.operadores" :key="item.idPersonal" :value="item.idPersonal">
                {{ item.nombre }}
              </option>
            </select>
          </div>
          <div v-else>
            <label class="mb-1 block text-sm font-medium text-neutral-700">Operador</label>
            <div class="app-input rounded-xl border px-4 py-2.5">{{ authStore.userName }}</div>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-neutral-700">Equipo / Máquina</label>
            <select v-model.number="form.cod_equipo" :class="fieldClass" required>
              <option :value="0">Seleccionar equipo</option>
              <option v-for="item in store.moviles" :key="item.idMovil" :value="item.idMovil">
                {{ item.detalle }} · {{ item.patente }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <InputField label="Hora inicio" type="number" step="0.01" min="0" v-model.number="form.hr_inicio" required />
            <InputField label="Hora fin" type="number" step="0.01" min="0" v-model.number="form.hr_fin" required />
          </div>
        </div>

        <div class="mt-4 grid gap-3 md:grid-cols-2">
          <InputField label="Horas no operativas" type="number" step="0.01" min="0" v-model.number="form.hrs_no_op" />
          <div>
            <label class="mb-1 block text-sm font-medium text-neutral-700">Motivo no operativo</label>
            <input v-model="form.motivo_no_op" :class="fieldClass" maxlength="150" placeholder="Obligatorio si hay horas no operativas" />
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Procesos del parte">
        <div class="mb-3 flex items-center justify-between gap-3">
          <p class="text-sm text-neutral-500">Agregá cada tarea realizada durante la misma jornada.</p>
          <button type="button" class="rounded-xl bg-primary px-3 py-2 text-sm font-bold text-on-primary" @click="agregarProceso">
            + Agregar proceso
          </button>
        </div>

        <div class="space-y-3">
          <div v-for="(proceso, index) in procesos" :key="proceso.key" class="rounded-xl border border-neutral-200 p-3">
            <div class="mb-3 flex items-start justify-between gap-3">
              <div>
                <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Proceso {{ index + 1 }}</p>
                <p class="font-bold text-neutral-900">{{ nombreProceso(proceso.tipo_proceso_id) || 'Sin seleccionar' }}</p>
              </div>
              <button v-if="procesos.length > 1" type="button" class="text-sm font-semibold text-error-dark" @click="quitarProceso(index)">
                Quitar
              </button>
            </div>

            <div class="grid gap-3 md:grid-cols-2">
              <div>
                <label class="mb-1 block text-sm font-medium text-neutral-700">Tipo de proceso</label>
                <select v-model.number="proceso.tipo_proceso_id" :class="fieldClass" required>
                  <option :value="0">Seleccionar proceso</option>
                  <option
                    v-for="tipo in store.tiposProceso"
                    :key="tipo.id"
                    :value="tipo.id"
                    :disabled="procesoUsado(tipo.id, proceso.key)"
                  >
                    {{ tipo.nombre }}
                  </option>
                </select>
              </div>

              <div v-if="requierePredio(proceso)">
                <label class="mb-1 block text-sm font-medium text-neutral-700">Predio</label>
                <select v-model.number="proceso.predio_id" :class="fieldClass" required>
                  <option :value="0">Seleccionar predio</option>
                  <option v-for="predio in store.predios" :key="predio.idPredio" :value="predio.idPredio">
                    {{ predio.nombre }}
                  </option>
                </select>
              </div>

              <div v-if="requiereActa(proceso)">
                <label class="mb-1 block text-sm font-medium text-neutral-700">Acta</label>
                <select v-model="proceso.acta" :class="fieldClass" required>
                  <option value="">Seleccionar acta</option>
                  <option v-for="acta in store.actas" :key="acta.id" :value="acta.numero">{{ acta.numero }}</option>
                </select>
              </div>

              <div v-if="requiereRodal(proceso)">
                <label class="mb-1 block text-sm font-medium text-neutral-700">Rodal</label>
                <input v-model="proceso.rodal" :class="fieldClass" maxlength="10" placeholder="Rodal" required />
              </div>

              <InputField
                v-if="esProceso(proceso, 'PERFILADO')"
                label="KM perfilado"
                type="number"
                step="0.01"
                min="0"
                v-model.number="proceso.km_perfilado"
              />
              <InputField
                v-if="esProceso(proceso, 'DISPOSICION')"
                label="Horas a disposición"
                type="number"
                step="0.01"
                min="0"
                v-model.number="proceso.hr_disposicion"
              />
              <InputField
                v-if="esProceso(proceso, 'REMOLQUE')"
                label="Horas de remolque"
                type="number"
                step="0.01"
                min="0"
                v-model.number="proceso.hr_remolque"
              />

              <template v-if="!esProceso(proceso, 'PERFILADO') && !esProceso(proceso, 'DISPOSICION') && !esProceso(proceso, 'REMOLQUE') && proceso.tipo_proceso_id">
                <InputField label="KM perfilado" type="number" step="0.01" min="0" v-model.number="proceso.km_perfilado" />
                <InputField label="Horas a disposición" type="number" step="0.01" min="0" v-model.number="proceso.hr_disposicion" />
                <InputField label="Horas de remolque" type="number" step="0.01" min="0" v-model.number="proceso.hr_remolque" />
              </template>
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Combustible y lubricantes">
        <label class="mb-3 flex items-center gap-2 text-sm font-semibold text-neutral-700">
          <input v-model="cargaCombustible" type="checkbox" />
          Se cargó combustible durante la jornada
        </label>

        <div v-if="cargaCombustible" class="grid gap-3 md:grid-cols-3">
          <InputField label="Litros" type="number" min="0" v-model.number="form.combustible" />
          <InputField label="Km / Horómetro" type="number" min="0" v-model.number="form.km_combustible" />
          <div>
            <label class="mb-1 block text-sm font-medium text-neutral-700">Lugar de carga</label>
            <select v-model.number="form.lugar_carga" :class="fieldClass">
              <option :value="0">Seleccionar lugar</option>
              <option v-for="lugar in store.lugaresCarga" :key="lugar.idLugarCarga" :value="lugar.idLugarCarga">{{ lugar.detalle }}</option>
            </select>
          </div>
          <InputField label="Remito 1" v-model="form.remito" />
          <InputField label="Remito 2" v-model="form.remito2" />
          <InputField label="Remito 3" v-model="form.remito3" />
        </div>

        <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <InputField label="Aceite cadena" type="number" min="0" v-model.number="form.aceite_cadena" />
          <InputField label="Hidráulico" type="number" min="0" v-model.number="form.aceite_hidraulico" />
          <InputField label="Motor" type="number" min="0" v-model.number="form.aceite_motor" />
          <InputField label="Transmisión" type="number" min="0" v-model.number="form.aceite_transmision" />
          <InputField label="Embrague" type="number" min="0" v-model.number="form.aceite_embrague" />
        </div>
      </SectionCard>

      <SectionCard title="Observaciones">
        <textarea v-model="form.observaciones" rows="3" maxlength="150" :class="`${fieldClass} resize-none`" placeholder="Observaciones del parte" />
      </SectionCard>

      <div v-if="errorLocal" class="rounded-xl border border-error/30 bg-error-light/40 px-4 py-3 text-sm font-semibold text-error-dark">
        {{ errorLocal }}
      </div>

      <div class="sticky bottom-3 flex justify-end">
        <button type="submit" :disabled="store.submitting" class="rounded-xl bg-primary px-6 py-3 font-extrabold text-on-primary shadow-lg disabled:opacity-60">
          {{ store.submitting ? 'Guardando...' : `Guardar parte (${procesos.length} proceso${procesos.length === 1 ? '' : 's'})` }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import SectionCard from '@/components/SectionCard.vue'
import InputField from '@/components/InputField.vue'

const props = defineProps({
  unidad: { type: Object, required: true },
})
defineEmits(['back'])

const router = useRouter()
const authStore = useAuthStore()
const store = useProduccionStore()
const canSelectOperador = computed(() => authStore.isAdmin || authStore.user?.encargado === 1)
const fieldClass = 'app-input w-full rounded-xl border px-4 py-2.5 placeholder:text-neutral-400 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:bg-neutral-200 transition-colors'
const today = new Date().toISOString().split('T')[0]
const cargaCombustible = ref(false)
const errorLocal = ref('')
let processKey = 0

const form = reactive({
  fecha: today,
  cod_operador: canSelectOperador.value ? 0 : Number(authStore.user?.idPersonal || 0),
  cod_equipo: 0,
  hr_inicio: 0,
  hr_fin: 0,
  hrs_no_op: 0,
  motivo_no_op: '',
  combustible: 0,
  km_combustible: 0,
  lugar_carga: 0,
  remito: '',
  remito2: '',
  remito3: '',
  aceite_cadena: 0,
  aceite_hidraulico: 0,
  aceite_motor: 0,
  aceite_transmision: 0,
  aceite_embrague: 0,
  observaciones: '',
})

function nuevoProceso() {
  processKey += 1
  return reactive({
    key: processKey,
    tipo_proceso_id: 0,
    predio_id: 0,
    acta: '',
    rodal: '',
    km_perfilado: 0,
    hr_disposicion: 0,
    hr_remolque: 0,
  })
}

const procesos = reactive([nuevoProceso()])

function agregarProceso() {
  procesos.push(nuevoProceso())
}

function quitarProceso(index) {
  if (procesos.length > 1) procesos.splice(index, 1)
}

function tipoProceso(id) {
  return store.tiposProceso.find((item) => Number(item.id) === Number(id)) || null
}

function nombreProceso(id) {
  return tipoProceso(id)?.nombre || ''
}

function esProceso(proceso, nombre) {
  return nombreProceso(proceso.tipo_proceso_id).trim().toUpperCase() === nombre
}

function procesoUsado(id, currentKey) {
  return procesos.some((item) => item.key !== currentKey && Number(item.tipo_proceso_id) === Number(id))
}

function requierePredio(proceso) {
  const nombre = nombreProceso(proceso.tipo_proceso_id).trim().toUpperCase()
  return ['PERFILADO', 'DISPOSICION', 'REMOLQUE'].includes(nombre) || !!tipoProceso(proceso.tipo_proceso_id)?.requiere_predio
}

function requiereActa(proceso) {
  const nombre = nombreProceso(proceso.tipo_proceso_id).trim().toUpperCase()
  if (nombre === 'PERFILADO') return true
  if (['DISPOSICION', 'REMOLQUE'].includes(nombre)) return false
  return !!tipoProceso(proceso.tipo_proceso_id)?.requiere_acta
}

function requiereRodal(proceso) {
  const nombre = nombreProceso(proceso.tipo_proceso_id).trim().toUpperCase()
  if (nombre === 'PERFILADO') return true
  if (['DISPOSICION', 'REMOLQUE'].includes(nombre)) return false
  return !!tipoProceso(proceso.tipo_proceso_id)?.requiere_rodal
}

function predioNombre(id) {
  return store.predios.find((item) => Number(item.idPredio) === Number(id))?.nombre || ''
}

function operadorNombre(id) {
  if (!canSelectOperador.value) return authStore.userName || ''
  return store.operadores.find((item) => Number(item.idPersonal) === Number(id))?.nombre || ''
}

function equipoSeleccionado() {
  return store.moviles.find((item) => Number(item.idMovil) === Number(form.cod_equipo)) || null
}

function validar() {
  if (!form.fecha) return 'Indicá la fecha del parte.'
  if (!form.cod_operador) return 'Seleccioná el operador.'
  if (!form.cod_equipo) return 'Seleccioná el equipo.'
  if (Number(form.hr_inicio) <= 0 || Number(form.hr_fin) <= Number(form.hr_inicio)) {
    return 'La hora fin debe ser mayor que la hora inicio.'
  }
  if (Number(form.hrs_no_op) > 0 && !String(form.motivo_no_op || '').trim()) {
    return 'Indicá el motivo de las horas no operativas.'
  }
  if (!procesos.length) return 'Agregá al menos un proceso.'

  for (let index = 0; index < procesos.length; index += 1) {
    const proceso = procesos[index]
    const etiqueta = `Proceso ${index + 1}`
    if (!proceso.tipo_proceso_id) return `${etiqueta}: seleccioná el tipo de proceso.`
    if (requierePredio(proceso) && !proceso.predio_id) return `${etiqueta}: seleccioná el predio.`
    if (requiereActa(proceso) && !String(proceso.acta || '').trim()) return `${etiqueta}: seleccioná el acta.`
    if (requiereRodal(proceso) && !String(proceso.rodal || '').trim()) return `${etiqueta}: indicá el rodal.`
    if (
      Number(proceso.km_perfilado || 0) <= 0
      && Number(proceso.hr_disposicion || 0) <= 0
      && Number(proceso.hr_remolque || 0) <= 0
    ) {
      return `${etiqueta}: cargá al menos una métrica mayor a cero.`
    }
  }

  if (cargaCombustible.value) {
    if (Number(form.combustible) <= 0) return 'Indicá los litros de combustible.'
    if (Number(form.km_combustible) <= 0) return 'Indicá el km/horómetro de la carga.'
    if (!form.lugar_carga) return 'Seleccioná el lugar de carga.'
    if (!String(form.remito || '').trim()) return 'Indicá al menos el Remito 1.'
  }
  return ''
}

async function guardar() {
  errorLocal.value = validar()
  if (errorLocal.value) return

  const equipo = equipoSeleccionado()
  const payload = {
    UN: props.unidad.nombre,
    fecha: form.fecha,
    equipo: equipo ? `${equipo.detalle} - ${equipo.patente}` : '',
    operador: operadorNombre(form.cod_operador),
    cod_operador: Number(form.cod_operador),
    cod_equipo: Number(form.cod_equipo),
    cod_un: Number(props.unidad.idUnidadNegocio),
    hr_inicio: Number(form.hr_inicio),
    hr_fin: Number(form.hr_fin),
    combustible: cargaCombustible.value ? Number(form.combustible || 0) : 0,
    km_combustible: cargaCombustible.value ? Number(form.km_combustible || 0) : 0,
    lugar_carga: cargaCombustible.value ? Number(form.lugar_carga || 0) : 0,
    remito: cargaCombustible.value ? String(form.remito || '').trim() : '',
    remito2: cargaCombustible.value ? String(form.remito2 || '').trim() : '',
    remito3: cargaCombustible.value ? String(form.remito3 || '').trim() : '',
    aceite_cadena: Number(form.aceite_cadena || 0),
    aceite_hidraulico: Number(form.aceite_hidraulico || 0),
    aceite_motor: Number(form.aceite_motor || 0),
    aceite_transmision: Number(form.aceite_transmision || 0),
    aceite_embrague: Number(form.aceite_embrague || 0),
    hrs_no_op: Number(form.hrs_no_op || 0),
    motivo_no_op: String(form.motivo_no_op || '').trim(),
    observaciones: String(form.observaciones || '').trim(),
    procesos: procesos.map((proceso) => ({
      tipo_proceso_id: Number(proceso.tipo_proceso_id),
      predio: requierePredio(proceso) ? predioNombre(proceso.predio_id) : '',
      acta: requiereActa(proceso) ? String(proceso.acta || '').trim() : '',
      rodal: requiereRodal(proceso) ? String(proceso.rodal || '').trim() : '',
      km_perfilado: Number(proceso.km_perfilado || 0),
      hr_disposicion: Number(proceso.hr_disposicion || 0),
      hr_remolque: Number(proceso.hr_remolque || 0),
    })),
  }

  try {
    const result = await store.submitParteCaminos(payload)
    if (result?.offline) {
      router.push({ name: 'home' })
      return
    }
    router.push({ name: 'home' })
  } catch {
    errorLocal.value = store.error || 'No se pudo guardar el parte.'
  }
}

watch(cargaCombustible, (activo) => {
  if (activo) return
  form.combustible = 0
  form.km_combustible = 0
  form.lugar_carga = 0
  form.remito = ''
  form.remito2 = ''
  form.remito3 = ''
})

onMounted(async () => {
  await Promise.all([
    store.fetchTiposProceso(props.unidad.idUnidadNegocio),
    store.fetchMoviles(props.unidad.idUnidadNegocio),
    store.fetchLugaresCarga(props.unidad.idUnidadNegocio),
    store.fetchPredios(),
    store.fetchActas(),
    canSelectOperador.value ? store.fetchOperadores(props.unidad.idUnidadNegocio) : Promise.resolve(),
  ])
})
</script>
