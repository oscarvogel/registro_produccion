<template>
  <div class="max-w-2xl mx-auto px-4 py-6">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button
        @click="$router.push({ name: 'home' })"
        class="p-2 rounded-lg text-neutral-500 hover:bg-neutral-200 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>
      <h1 class="text-xl font-bold text-neutral-900">Carga de Producción</h1>
    </div>

    <!-- Loading catalogs -->
    <div v-if="store.loading" class="flex items-center justify-center py-20">
      <svg class="w-8 h-8 animate-spin text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-5">

      <!-- ═══ 1. FECHA ═══ -->
      <SectionCard title="Fecha de Registro">
        <InputField
          label="Fecha"
          type="date"
          v-model="form.fecha"
          required
        />
      </SectionCard>

      <!-- ═══ 2. UNIDAD DE NEGOCIO ═══ -->
      <SectionCard title="Unidad de Negocio">
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-1">Unidad de Negocio</label>
          <select
            v-model="form.un_id"
            @change="onUnidadChange"
            required
            class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
          >
            <option value="" disabled>— Seleccionar —</option>
            <option v-for="un in store.unidadesNegocio" :key="un.idUnidadNegocio" :value="un.idUnidadNegocio">
              {{ un.nombre }}
            </option>
          </select>
        </div>

        <div class="mt-3">
          <label class="block text-sm font-medium text-neutral-700 mb-1">Tipo de Proceso</label>
          <select
            v-model="form.tipo_de_proceso_id"
            @change="onTipoProcesoChange"
            required
            :disabled="!form.un_id || store.tiposProceso.length === 0"
            class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
                   disabled:bg-neutral-100 disabled:cursor-not-allowed transition-colors"
          >
            <option value="" disabled>
              {{ !form.un_id ? '— Primero seleccioná UN —' : store.tiposProceso.length === 0 ? '— Sin procesos disponibles —' : '— Seleccionar —' }}
            </option>
            <option v-for="tp in store.tiposProceso" :key="tp.id" :value="tp.id">
              {{ tp.nombre }}
            </option>
          </select>
        </div>
      </SectionCard>

      <!-- ═══ 3. OPERADOR ═══ -->
      <SectionCard title="Identificación del Operador">
        <!-- Si es operador: bloqueado -->
        <div v-if="!isEncargado">
          <label class="block text-sm font-medium text-neutral-700 mb-1">Operador</label>
          <div class="w-full px-4 py-2.5 bg-neutral-100 border border-neutral-200 rounded-lg text-neutral-700">
            {{ authStore.userName }}
          </div>
        </div>
        <!-- Si es encargado: seleccionar (requiere UN primero) -->
        <div v-else>
          <label class="block text-sm font-medium text-neutral-700 mb-1">Seleccionar Operador</label>
          <select
            v-model="form.operador_id"
            @change="onOperadorChange"
            required
            :disabled="!form.un_id || store.operadores.length === 0"
            class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
                   disabled:bg-neutral-100 disabled:cursor-not-allowed transition-colors"
          >
            <option value="" disabled>
              {{ !form.un_id ? '— Primero seleccioná UN —' : store.operadores.length === 0 ? '— Sin operadores —' : '— Seleccionar operador —' }}
            </option>
            <option v-for="op in store.operadores" :key="op.idPersonal" :value="op.idPersonal">
              {{ op.nombre }}
            </option>
          </select>
        </div>
      </SectionCard>

      <!-- ═══ 4. MAQUINARIA ═══ -->
      <SectionCard title="Asignación de Maquinaria">
        <div v-if="store.movilAsignado" class="space-y-2">
          <div class="flex items-center gap-3 p-3 bg-success-light/50 border border-success/30 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-success-dark shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <div>
              <p class="font-medium text-neutral-900">{{ store.movilAsignado.patente }}</p>
              <p class="text-sm text-neutral-600">{{ store.movilAsignado.detalle }}</p>
            </div>
          </div>
        </div>
        <div v-else-if="form.operador_id" class="p-3 bg-warning-light/50 border border-warning/30 rounded-lg text-sm text-warning-dark">
          No se encontró maquinaria asignada a este operador.
        </div>
        <div v-else class="p-3 bg-neutral-50 border border-neutral-200 rounded-lg text-sm text-neutral-500">
          Seleccioná un operador para ver la máquina asignada.
        </div>
      </SectionCard>

      <!-- ═══ 5. CONTROL DE TIEMPO ═══ -->
      <SectionCard title="Control de Tiempo">
        <div class="grid grid-cols-2 gap-4">
          <InputField
            label="Hora Inicio"
            type="number"
            v-model.number="form.hr_inicio"
            placeholder="Ej: 1200"
            min="0"
            required
          />
          <InputField
            label="Hora Fin"
            type="number"
            v-model.number="form.hr_fin"
            placeholder="Ej: 1850"
            min="0"
            required
          />
        </div>
        <div class="grid grid-cols-2 gap-4 mt-3">
          <InputField
            label="Hs No Operativas"
            type="number"
            v-model.number="form.hrs_no_op"
            min="0"
          />
          <InputField
            label="Motivo"
            type="text"
            v-model="form.motivo_no_op"
            placeholder="Motivo..."
          />
        </div>
      </SectionCard>

      <!-- ═══ 6. DATOS DE PRODUCCIÓN (dinámico según tipo de proceso) ═══ -->
      <SectionCard v-if="camposActivos.length > 0" title="Datos de Producción">
        <div class="space-y-3">
          <!-- TN Despachadas -->
          <InputField
            v-if="camposActivos.includes('tn_despachadas')"
            label="TN Despachadas"
            type="number"
            v-model.number="form.tn_despachadas"
            placeholder="Toneladas"
            min="0"
          />

          <!-- Carros -->
          <InputField
            v-if="camposActivos.includes('carros')"
            label="Carros"
            type="number"
            v-model.number="form.carros"
            placeholder="Cantidad de carros"
            min="0"
          />

          <!-- Distancia recorrida -->
          <InputField
            v-if="camposActivos.includes('distancia_recorrida')"
            label="Distancia Recorrida (mts)"
            type="number"
            v-model.number="form.mtrs_recorridos"
            placeholder="Metros"
            min="0"
          />

          <!-- M3 -->
          <InputField
            v-if="camposActivos.includes('m3')"
            label="M³ (metros cúbicos)"
            type="number"
            v-model.number="form.m3"
            placeholder="M³"
            min="0"
          />

          <!-- Plantas -->
          <InputField
            v-if="camposActivos.includes('plantas')"
            label="Plantas"
            type="number"
            v-model.number="form.plantas"
            placeholder="Cantidad de plantas"
            min="0"
          />

          <!-- Hora inicio / fin (para HORAS MAQUINAS) -->
          <div v-if="camposActivos.includes('hora_inicio')" class="grid grid-cols-2 gap-4">
            <InputField
              label="Hora Inicio Máq."
              type="number"
              v-model.number="form.hr_inicio"
              placeholder="Ej: 1200"
              min="0"
            />
            <InputField
              label="Hora Fin Máq."
              type="number"
              v-model.number="form.hr_fin"
              placeholder="Ej: 1850"
              min="0"
            />
          </div>
          <div v-if="camposActivos.includes('hora_inicio') && form.hr_fin > form.hr_inicio"
               class="px-3 py-2 bg-info-light/50 border border-info/30 rounded-lg text-sm text-info-dark">
            Horas trabajadas: <strong>{{ form.hr_fin - form.hr_inicio }}</strong>
          </div>

          <!-- HAS (hectáreas) -->
          <InputField
            v-if="camposActivos.includes('has')"
            label="Hectáreas (HAS)"
            type="number"
            v-model.number="form.has"
            placeholder="Hectáreas"
            min="0"
            step="0.01"
          />

          <!-- Horas a disposición -->
          <InputField
            v-if="camposActivos.includes('horas_disposicion')"
            label="Horas a Disposición"
            type="number"
            v-model.number="form.hr_disposicion"
            placeholder="Horas"
            min="0"
          />

          <!-- KM -->
          <InputField
            v-if="camposActivos.includes('km')"
            label="Kilómetros (KM)"
            type="number"
            v-model.number="form.km"
            placeholder="KM"
            min="0"
          />
        </div>
      </SectionCard>

      <div v-else-if="form.tipo_de_proceso_id" class="p-3 bg-neutral-50 border border-neutral-200 rounded-lg text-sm text-neutral-500">
        No hay campos de producción definidos para este tipo de proceso.
      </div>

      <!-- ═══ 7. COMBUSTIBLE ═══ -->
      <SectionCard title="Combustible">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-neutral-700">¿Se cargó combustible?</span>
          <button
            type="button"
            @click="cargoCombustible = !cargoCombustible"
            :class="[
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
              cargoCombustible ? 'bg-primary' : 'bg-neutral-300',
            ]"
          >
            <span
              :class="[
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                cargoCombustible ? 'translate-x-6' : 'translate-x-1',
              ]"
            />
          </button>
        </div>

        <div v-if="cargoCombustible" class="mt-3">
          <InputField
            label="Litros de gasoil"
            type="number"
            v-model.number="form.combustible"
            placeholder="Ej: 150"
            min="0"
            required
          />
        </div>
      </SectionCard>

      <!-- ═══ 8. UBICACIÓN Y REFERENCIA ═══ -->
      <SectionCard title="Ubicación y Referencia">
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-1">Acta</label>
          <select
            v-model="form.acta"
            class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
          >
            <option value="">— Sin acta —</option>
            <option v-for="a in store.actas" :key="a.id" :value="a.numero">
              {{ a.numero }}
            </option>
          </select>
        </div>

        <div class="mt-3">
          <label class="block text-sm font-medium text-neutral-700 mb-1">Predio</label>
          <select
            v-model="form.predio_id"
            @change="onPredioChange"
            class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
          >
            <option value="">— Sin predio —</option>
            <option v-for="p in store.predios" :key="p.idPredio" :value="p.idPredio">
              {{ p.nombre }}
            </option>
          </select>
        </div>

        <div class="mt-3">
          <label class="block text-sm font-medium text-neutral-700 mb-1">Rodal</label>
          <select
            v-if="store.rodales.length > 0"
            v-model="form.rodal_id"
            class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
          >
            <option value="">— Seleccionar rodal —</option>
            <option v-for="r in store.rodales" :key="r.idRodal" :value="r.idRodal">
              {{ r.rodal }}
            </option>
          </select>
          <input
            v-else
            type="text"
            v-model="form.rodal_manual"
            placeholder="Ingresá el rodal manualmente"
            class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                   placeholder:text-neutral-400
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
          />
        </div>
      </SectionCard>

      <!-- ═══ OBSERVACIONES ═══ -->
      <SectionCard title="Observaciones">
        <textarea
          v-model="form.observaciones"
          rows="3"
          placeholder="Notas adicionales..."
          class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-neutral-900
                 placeholder:text-neutral-400 resize-none
                 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
        />
      </SectionCard>

      <!-- Error -->
      <div
        v-if="store.error"
        class="flex items-center gap-2 p-3 bg-error-light text-error-dark rounded-lg text-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-error shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" /><line x1="12" x2="12" y1="8" y2="12" /><line x1="12" x2="12.01" y1="16" y2="16" />
        </svg>
        <span>{{ store.error }}</span>
      </div>

      <!-- Submit -->
      <button
        type="submit"
        :disabled="store.submitting"
        class="w-full py-3 px-4 bg-primary hover:bg-primary-dark text-white font-bold text-lg
               rounded-xl transition-colors duration-200
               focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
               disabled:opacity-60 disabled:cursor-not-allowed
               flex items-center justify-center gap-2"
      >
        <svg v-if="store.submitting" class="w-5 h-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span>{{ store.submitting ? 'Guardando...' : 'Guardar Registro' }}</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import Swal from 'sweetalert2'
import SectionCard from '@/components/SectionCard.vue'
import InputField from '@/components/InputField.vue'

const router = useRouter()
const authStore = useAuthStore()
const store = useProduccionStore()

const isEncargado = computed(() => authStore.user?.encargado === 1)
const cargoCombustible = ref(false)

// Campos dinámicos según tipo de proceso seleccionado
const camposActivos = computed(() => {
  if (!form.tipo_de_proceso_id) return []
  const tipo = store.tiposProceso.find(t => t.id === form.tipo_de_proceso_id)
    || store.todosLosTipos.find(t => t.id === form.tipo_de_proceso_id)
  if (!tipo || !tipo.campos) return []
  return tipo.campos.split(',').map(c => c.trim())
})

// Nombre del tipo de proceso seleccionado
const tipoProcesoNombre = computed(() => {
  if (!form.tipo_de_proceso_id) return ''
  const tipo = store.tiposProceso.find(t => t.id === form.tipo_de_proceso_id)
    || store.todosLosTipos.find(t => t.id === form.tipo_de_proceso_id)
  return tipo?.nombre || ''
})

const today = new Date().toISOString().split('T')[0]

const form = reactive({
  fecha: today,
  operador_id: isEncargado.value ? '' : authStore.user?.idPersonal,
  un_id: '',
  tipo_de_proceso_id: '',
  hr_inicio: 0,
  hr_fin: 0,
  hrs_no_op: 0,
  motivo_no_op: '',
  combustible: 0,
  aceite_cadena: 0,
  // Campos de producción específicos
  m3: 0,
  carros: 0,
  tn_despachadas: 0,
  has: 0,
  plantas: 0,
  mtrs_recorridos: 0,
  km_carreteo: 0,
  km_perfilado: 0,
  hr_disposicion: 0,
  km: 0, // temporal, se resuelve en submit a km_carreteo o km_perfilado
  // Ubicación
  acta: '',
  predio_id: '',
  rodal_id: '',
  rodal_manual: '',
  observaciones: '',
})

// ─── Load initial data ───
onMounted(async () => {
  await store.loadCatalogos()

  if (!isEncargado.value) {
    // Auto-fetch movil para operador logueado
    await store.fetchMovilByOperador(form.operador_id)
    // Auto-set tipo de proceso del operador si tiene uno
    if (authStore.user?.tipo_de_proceso_id) {
      form.tipo_de_proceso_id = authStore.user.tipo_de_proceso_id
    }
  }
  // Si es encargado, los operadores se cargan al elegir la UN
})

// ─── Helpers ───
function getOperadorNombre(id) {
  if (!isEncargado.value) return authStore.userName
  const op = store.operadores.find(o => o.idPersonal === id)
  return op?.nombre || ''
}

function getUnidadNombre(id) {
  const un = store.unidadesNegocio.find(u => u.idUnidadNegocio === id)
  return un?.nombre || ''
}

function getPredioNombre(id) {
  const p = store.predios.find(pr => pr.idPredio === id)
  return p?.nombre || ''
}

function getRodalNombre() {
  if (form.rodal_id) {
    const r = store.rodales.find(rd => rd.idRodal === form.rodal_id)
    return r?.rodal || ''
  }
  return form.rodal_manual || ''
}

// ─── Watchers ───
async function onOperadorChange() {
  if (form.operador_id) {
    await store.fetchMovilByOperador(form.operador_id)
    // Auto-set tipo de proceso del operador seleccionado
    const operador = store.operadores.find(o => o.idPersonal === form.operador_id)
    if (operador?.tipo_de_proceso_id) {
      form.tipo_de_proceso_id = operador.tipo_de_proceso_id
    }
  }
}

async function onUnidadChange() {
  // Reset dependientes
  form.tipo_de_proceso_id = ''
  form.operador_id = isEncargado.value ? '' : form.operador_id
  store.movilAsignado = null
  // Cargar tipos de proceso y operadores de esta UN en paralelo
  await Promise.all([
    store.fetchTiposProceso(form.un_id),
    isEncargado.value ? store.fetchOperadores(form.un_id) : Promise.resolve(),
  ])
}

function onTipoProcesoChange() {
  // Reset production data fields when switching process type
  form.m3 = 0
  form.carros = 0
  form.tn_despachadas = 0
  form.has = 0
  form.plantas = 0
  form.mtrs_recorridos = 0
  form.km_carreteo = 0
  form.km_perfilado = 0
  form.hr_disposicion = 0
  form.km = 0
}

async function onPredioChange() {
  form.rodal_id = ''
  form.rodal_manual = ''
  await store.fetchRodales(form.predio_id)
}

// ─── Watch combustible toggle ───
watch(cargoCombustible, (val) => {
  if (!val) form.combustible = 0
})

// ─── Determinar unidad de producción ───
function resolveUnidadProduccion() {
  const campos = camposActivos.value
  if (campos.includes('tn_despachadas')) return 'TN'
  if (campos.includes('m3')) return 'M3'
  if (campos.includes('has')) return 'HAS'
  if (campos.includes('plantas')) return 'PLANTAS'
  if (campos.includes('carros')) return 'CARROS'
  if (campos.includes('km')) return 'KM'
  if (campos.includes('distancia_recorrida')) return 'MTS'
  if (campos.includes('hora_inicio')) return 'HS'
  if (campos.includes('horas_disposicion')) return 'HS'
  return ''
}

// ─── Calcular producción principal ───
function resolveProduccion() {
  const campos = camposActivos.value
  if (campos.includes('tn_despachadas')) return form.tn_despachadas
  if (campos.includes('m3')) return form.m3
  if (campos.includes('has')) return form.has
  if (campos.includes('plantas')) return form.plantas
  if (campos.includes('carros')) return form.carros
  if (campos.includes('km')) return form.km
  if (campos.includes('distancia_recorrida')) return form.mtrs_recorridos
  if (campos.includes('horas_disposicion')) return form.hr_disposicion
  return 0
}

// ─── Submit ───
async function handleSubmit() {
  try {
    const nombre = tipoProcesoNombre.value

    // Resolver km según tipo de proceso
    let kmCarreteo = form.km_carreteo
    let kmPerfilado = form.km_perfilado
    if (camposActivos.value.includes('km')) {
      if (nombre === 'CARRETEO') kmCarreteo = form.km
      else if (nombre === 'PERFILADO') kmPerfilado = form.km
    }

    const payload = {
      UN: getUnidadNombre(form.un_id),
      operacion: nombre,
      fecha: form.fecha,
      equipo: store.movilAsignado?.patente || '',
      operador: getOperadorNombre(form.operador_id),
      cod_operador: form.operador_id || 0,
      cod_equipo: store.movilAsignado?.idMovil || 0,
      cod_un: form.un_id || 0,
      hr_inicio: form.hr_inicio,
      hr_fin: form.hr_fin,
      combustible: form.combustible,
      aceite_cadena: form.aceite_cadena,
      acta: form.acta,
      rodal: getRodalNombre(),
      predio: getPredioNombre(form.predio_id),
      m3: form.m3,
      carros: form.carros,
      tn_despachadas: form.tn_despachadas,
      has: form.has,
      produccion: resolveProduccion(),
      plantas: form.plantas,
      mtrs_recorridos: form.mtrs_recorridos,
      km_carreteo: kmCarreteo,
      km_perfilado: kmPerfilado,
      hr_disposicion: form.hr_disposicion,
      hrs_no_op: form.hrs_no_op,
      motivo_no_op: form.motivo_no_op,
      observaciones: form.observaciones,
      unidad_produccion: resolveUnidadProduccion(),
    }

    await store.submitProduccion(payload)

    await Swal.fire({
      icon: 'success',
      title: 'Registro guardado',
      text: 'El registro de producción se guardó correctamente.',
      confirmButtonColor: '#3d935d',
    })

    router.push({ name: 'home' })
  } catch {
    // error handled by store
  }
}
</script>
