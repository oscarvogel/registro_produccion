<template>
  <div class="max-w-2xl mx-auto px-3 py-4 pb-[7.5rem] md:px-4 md:pt-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-5 px-1">
      <div class="flex items-center gap-2.5">
      <button
        @click="$router.push({ name: 'home' })"
        class="p-2 rounded-lg text-neutral-500 hover:bg-neutral-200 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>
      <h1 class="text-2xl font-bold text-neutral-900 leading-none">Carga de Producción</h1>
      </div>
      <button class="p-2 text-neutral-500" type="button" aria-label="Más opciones">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="5" r="1.2" />
          <circle cx="12" cy="12" r="1.2" />
          <circle cx="12" cy="19" r="1.2" />
        </svg>
      </button>
    </div>

    <!-- Loading catalogs -->
    <div v-if="store.loading" class="flex items-center justify-center py-20">
      <svg class="w-8 h-8 animate-spin text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <form v-else @submit.prevent="handleSubmit">

      <!-- Step indicator -->
      <div class="mb-5">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-medium text-neutral-400">Paso {{ pasoActual + 1 }} de {{ totalPasos }}</span>
          <span class="text-xs font-semibold text-neutral-700">{{ pasos[pasoActual] }}</span>
        </div>
        <div class="h-1.5 bg-neutral-200 rounded-full overflow-hidden">
          <div class="h-full bg-primary rounded-full transition-all duration-500 ease-out" :style="{ width: `${((pasoActual + 1) / totalPasos) * 100}%` }"></div>
        </div>
        <div class="flex justify-between mt-2.5 px-0.5">
          <button
            v-for="(paso, i) in pasos"
            :key="i"
            type="button"
            @click="irAPaso(i)"
            :class="['w-2.5 h-2.5 rounded-full transition-all duration-300 focus:outline-none',
              i === pasoActual ? 'bg-primary scale-125' : i < pasoActual ? 'bg-primary/60 hover:bg-primary/80 cursor-pointer' : 'bg-neutral-300 cursor-default']"
          />
        </div>
      </div>

      <!-- ═══ 1. FECHA ═══ -->
      <SectionCard v-show="pasoActual === 0" title="Fecha de Registro">
        <InputField
          label="Fecha"
          type="date"
          v-model="form.fecha"
          required
        />
      </SectionCard>

      <!-- ═══ 2. UNIDAD DE NEGOCIO ═══ -->
      <SectionCard v-show="pasoActual === 1" title="Unidad de Negocio">
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-1">Unidad de Negocio</label>
          <select
            v-model="form.un_id"
            @change="onUnidadChange"
            required
            :class="fieldClass"
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
            :class="fieldClass"
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
      <SectionCard v-show="pasoActual === 2" title="Identificación del Operador">
        <!-- Si es operador: bloqueado -->
        <div v-if="!isEncargado">
          <label class="block text-sm font-medium text-neutral-700 mb-1">Operador</label>
          <div class="w-full px-4 py-3 bg-neutral-100 border border-neutral-300 rounded-xl text-neutral-700">
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
            :class="fieldClass"
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
      <SectionCard v-show="pasoActual === 3" title="Asignación de Maquinaria">
        <!-- ── Estado: Máquina ya seleccionada ── -->
        <div v-if="form.cod_equipo && !mostrandoBuscador" class="space-y-3">
          <div class="flex items-center gap-3 p-3 bg-success-light/40 border border-success/30 rounded-xl">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-success-dark shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-bold text-neutral-900 truncate">{{ movilSeleccionadoDetalle }}</p>
              <p class="text-xs text-neutral-500">{{ movilSeleccionadoPatente }} · ID {{ form.cod_equipo }}</p>
            </div>
            <button
              type="button"
              @click="abrirBuscador"
              class="shrink-0 text-xs font-medium text-primary hover:text-primary-dark underline underline-offset-2"
            >
              Cambiar
            </button>
          </div>

          <!-- Accesos rápidos: sólo si hay asignaciones y la seleccionada NO es de asignación -->
          <div v-if="store.asignaciones.length > 0 && !asignacionSeleccionada">
            <p class="text-[11px] font-semibold text-neutral-400 uppercase tracking-wide mb-1.5">Asignaciones rápidas</p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="asig in store.asignaciones"
                :key="asig.idAsignacion"
                type="button"
                @click="seleccionarDesdeAsignacion(asig)"
                class="px-3 py-1.5 text-xs font-medium bg-neutral-100 border border-neutral-200 rounded-lg hover:bg-neutral-200 transition-colors truncate max-w-full"
              >
                {{ asig.detalle }}
              </button>
            </div>
          </div>
        </div>

        <!-- ── Estado: Buscador abierto / sin selección ── -->
        <div v-else>
          <!-- Asignaciones del operador como opciones rápidas -->
          <div v-if="store.asignaciones.length > 0" class="mb-3">
            <p class="text-[11px] font-semibold text-neutral-400 uppercase tracking-wide mb-1.5">Asignaciones del operador</p>
            <div class="space-y-1.5">
              <button
                v-for="asig in store.asignaciones"
                :key="asig.idAsignacion"
                type="button"
                @click="seleccionarDesdeAsignacion(asig)"
                class="w-full text-left px-3 py-2 rounded-lg border border-neutral-200 bg-neutral-50 hover:bg-primary/5 hover:border-primary/30 transition-colors"
              >
                <p class="text-sm font-semibold text-neutral-900 truncate">{{ asig.detalle }}</p>
                <p class="text-[11px] text-neutral-400">{{ asig.patente }} · {{ getProcesoTexto(asig.idProceso) }}</p>
              </button>
            </div>
          </div>

          <!-- Mensaje si no hay asignaciones ni movilAsignado -->
          <div v-else-if="!form.operador_id" class="p-3 bg-neutral-50 border border-neutral-200 rounded-lg text-sm text-neutral-500 mb-3">
            Seleccioná un operador para autocompletar la máquina.
          </div>

          <!-- Buscador -->
          <div>
            <label class="block text-xs font-medium text-neutral-500 mb-1">Buscar máquina</label>
            <div class="relative">
              <input
                ref="inputBuscadorMovil"
                type="text"
                v-model="busquedaMovil"
                :class="fieldClass"
                placeholder="Ej: 1470, JOHN DEERE, N° 3..."
              />
              <button
                v-if="busquedaMovil.trim()"
                type="button"
                @click="busquedaMovil = ''"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div
              v-if="mostrarListaMoviles"
              class="mt-1.5 border border-neutral-200 rounded-xl bg-white max-h-52 overflow-y-auto shadow-sm"
            >
              <button
                v-for="movil in movilesFiltrados"
                :key="movil.idMovil"
                type="button"
                @click="seleccionarMovil(movil)"
                class="w-full text-left px-3 py-2 border-b last:border-b-0 border-neutral-100 hover:bg-neutral-50 transition-colors"
              >
                <p class="text-sm font-medium text-neutral-900 truncate">{{ movil.detalle }}</p>
                <p class="text-[11px] text-neutral-400">{{ movil.patente }} · ID {{ movil.idMovil }}</p>
              </button>
            </div>
            <div
              v-else-if="mostrarNoResultados"
              class="mt-1.5 p-2.5 text-xs text-neutral-400 bg-neutral-50 rounded-lg"
            >
              Sin resultados para "{{ busquedaMovil }}".
            </div>

            <!-- Botón cancelar si ya había máquina seleccionada -->
            <button
              v-if="mostrandoBuscador && form.cod_equipo"
              type="button"
              @click="cerrarBuscador"
              class="mt-2 text-xs text-neutral-400 hover:text-neutral-600 underline underline-offset-2"
            >
              Cancelar
            </button>
          </div>
        </div>
      </SectionCard>

      <!-- ═══ 5. CONTROL DE TIEMPO ═══ -->
      <SectionCard v-show="pasoActual === 4" title="Control de Tiempo">
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
          <div>
            <label class="block text-sm font-medium text-neutral-600 mb-1.5">Motivo (lista)</label>
            <select
              v-model="motivoSeleccionado"
              :class="fieldClass"
            >
              <option value="">— Seleccionar motivo —</option>
              <option v-for="motivo in motivosNoOperativos" :key="motivo" :value="motivo">
                {{ motivo }}
              </option>
            </select>
          </div>
        </div>
        <div class="mt-3">
          <label class="block text-sm font-medium text-neutral-600 mb-1.5">Motivo (detalle libre)</label>
          <textarea
            v-model="form.motivo_no_op"
            rows="4"
            placeholder="Describí el motivo..."
            :class="`${fieldClass} resize-none min-h-28`"
          />
        </div>
      </SectionCard>

      <!-- ═══ 6. DATOS DE PRODUCCIÓN (dinámico según tipo de proceso) ═══ -->
      <SectionCard v-show="pasoActual === 5" v-if="camposActivos.length > 0" title="Datos de Producción">
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

      <div v-show="pasoActual === 5" v-if="form.tipo_de_proceso_id && camposActivos.length === 0" class="p-3 bg-neutral-50 border border-neutral-200 rounded-lg text-sm text-neutral-500">
        No hay campos de producción definidos para este tipo de proceso.
      </div>

      <!-- ═══ 7. COMBUSTIBLE ═══ -->
      <SectionCard v-show="pasoActual === 5" title="Combustible">
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
      <SectionCard v-show="pasoActual === 6" title="Ubicación y Referencia">
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-1">Acta</label>
          <select
            v-model="form.acta"
            :class="fieldClass"
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
            :class="fieldClass"
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
            :class="fieldClass"
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
            :class="fieldClass"
          />
        </div>
      </SectionCard>

      <!-- ═══ OBSERVACIONES ═══ -->
      <SectionCard v-show="pasoActual === 6" title="Observaciones">
        <textarea
          v-model="form.observaciones"
          rows="3"
          placeholder="Notas adicionales..."
          :class="`${fieldClass} resize-none min-h-32`"
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

      <!-- Step navigation — fixed bottom -->
      <div class="fixed bottom-0 left-0 right-0 z-30 border-t border-neutral-200 bg-white/95 backdrop-blur-sm px-3 py-3">
        <div class="max-w-2xl mx-auto flex items-center gap-3">
          <button
            v-if="pasoActual > 0"
            type="button"
            @click="retroceder"
            class="flex-1 py-3.5 px-4 bg-neutral-100 text-neutral-700 font-semibold rounded-2xl border border-neutral-200 flex items-center justify-center gap-2 active:bg-neutral-200 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6" />
            </svg>
            Anterior
          </button>
          <div v-else class="flex-1" />

          <button
            v-if="pasoActual < totalPasos - 1"
            type="button"
            @click="avanzar"
            :disabled="!puedeAvanzar"
            class="flex-1 py-3.5 px-4 bg-primary text-white font-bold rounded-2xl flex items-center justify-center gap-2 shadow-[0_4px_14px_rgba(20,61,35,0.25)] disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed active:bg-primary-dark transition-colors"
          >
            Siguiente
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="m9 18 6-6-6-6" />
            </svg>
          </button>
          <button
            v-else
            type="submit"
            :disabled="store.submitting"
            class="flex-1 py-3.5 px-4 bg-primary text-white font-bold rounded-2xl flex items-center justify-center gap-2.5 shadow-[0_8px_18px_rgba(20,61,35,0.25)] disabled:opacity-60 disabled:cursor-not-allowed active:bg-primary-dark transition-colors"
          >
            <svg v-if="store.submitting" class="w-5 h-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/>
              <polyline points="7 3 7 8 15 8"/>
            </svg>
            {{ store.submitting ? 'Guardando...' : 'Guardar Registro' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProduccionStore } from '@/stores/produccion'
import Swal from 'sweetalert2'
import SectionCard from '@/components/SectionCard.vue'
import InputField from '@/components/InputField.vue'
import motivosNoOperativos from '@/data/motivosNoOperativos.json'

const router = useRouter()
const authStore = useAuthStore()
const store = useProduccionStore()

const isEncargado = computed(() => authStore.user?.encargado === 1)
const cargoCombustible = ref(false)
const motivoSeleccionado = ref('')
const busquedaMovil = ref('')
const mostrandoBuscador = ref(false)
const inputBuscadorMovil = ref(null)
const fieldClass = 'w-full px-4 py-3 bg-neutral-100 border border-neutral-300 rounded-xl text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/40 disabled:bg-neutral-200 disabled:cursor-not-allowed transition-colors'

// ─── Wizard steps ───
const pasoActual = ref(0)
const pasos = ['Fecha', 'Unidad de Negocio', 'Operador', 'Maquinaria', 'Tiempo', 'Producción', 'Ubicación']
const totalPasos = pasos.length

const puedeAvanzar = computed(() => {
  switch (pasoActual.value) {
    case 0: return !!form.fecha
    case 1: return !!form.un_id && !!form.tipo_de_proceso_id
    case 2: return !!form.operador_id
    case 3: return form.cod_equipo > 0
    case 4: return true
    default: return true
  }
})

function avanzar() {
  if (puedeAvanzar.value && pasoActual.value < totalPasos - 1) {
    pasoActual.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function retroceder() {
  if (pasoActual.value > 0) {
    pasoActual.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function irAPaso(i) {
  if (i < pasoActual.value) {
    pasoActual.value = i
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

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

const movilesFiltrados = computed(() => {
  const texto = (busquedaMovil.value || '').trim().toLowerCase()
  const lista = store.moviles || []
  if (!texto) return lista.slice(0, 12)
  return lista
    .filter((movil) => {
      const detalle = (movil.detalle || '').toLowerCase()
      const patente = (movil.patente || '').toLowerCase()
      const id = String(movil.idMovil || '')
      return detalle.includes(texto) || patente.includes(texto) || id.includes(texto)
    })
    .slice(0, 12)
})

const asignacionSeleccionada = computed(() => {
  if (!form.cod_equipo) return null
  return (store.asignaciones || []).find((asig) => asig.idMovil === form.cod_equipo) || null
})

const busquedaNormalizada = computed(() => (busquedaMovil.value || '').trim().toLowerCase())

const mostrarListaMoviles = computed(() => {
  return !!form.un_id && busquedaNormalizada.value.length >= 1 && movilesFiltrados.value.length > 0
})

const mostrarNoResultados = computed(() => {
  return !!form.un_id && busquedaNormalizada.value.length >= 2 && movilesFiltrados.value.length === 0
})

const movilSeleccionadoDetalle = computed(() => {
  if (!form.cod_equipo) return ''
  const asig = (store.asignaciones || []).find(a => a.idMovil === form.cod_equipo)
  if (asig) return asig.detalle
  const movil = (store.moviles || []).find(m => m.idMovil === form.cod_equipo)
  if (movil) return movil.detalle
  return form.equipo.split(' - ')[0] || form.equipo
})

const movilSeleccionadoPatente = computed(() => {
  if (!form.cod_equipo) return ''
  const asig = (store.asignaciones || []).find(a => a.idMovil === form.cod_equipo)
  if (asig) return asig.patente
  const movil = (store.moviles || []).find(m => m.idMovil === form.cod_equipo)
  if (movil) return movil.patente
  return form.equipo.split(' - ')[1] || ''
})

const today = new Date().toISOString().split('T')[0]

const form = reactive({
  fecha: today,
  operador_id: isEncargado.value ? '' : authStore.user?.idPersonal,
  equipo: '',
  cod_equipo: 0,
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
    // Auto-fetch asignaciones + fallback para operador logueado
    await Promise.all([
      store.fetchAsignaciones(form.operador_id),
      store.fetchMovilByOperador(form.operador_id),
    ])
    if (form.un_id) {
      await store.fetchMoviles(form.un_id)
    }
    if (store.asignaciones.length > 0) {
      const asig = store.asignaciones[0]
      seleccionarMovil({ idMovil: asig.idMovil, patente: asig.patente, detalle: asig.detalle })
      if (asig.idProceso) {
        form.tipo_de_proceso_id = asig.idProceso
      }
    } else if (store.movilAsignado) {
      seleccionarMovil(store.movilAsignado)
    }
    // Auto-set tipo de proceso del operador si no se seteó por asignación
    if (!form.tipo_de_proceso_id && authStore.user?.tipo_de_proceso_id) {
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

function getProcesoTexto(idProceso) {
  const tipo = store.tiposProceso.find((t) => t.id === idProceso)
    || store.todosLosTipos.find((t) => t.id === idProceso)
  if (tipo?.nombre) {
    return `Proceso: ${tipo.nombre}`
  }
  return `Proceso ID ${idProceso}`
}

// ─── Watchers ───
async function onOperadorChange() {
  if (form.operador_id) {
    // Fetch asignaciones operativas + fallback legacy
    await Promise.all([
      store.fetchAsignaciones(form.operador_id),
      store.fetchMovilByOperador(form.operador_id),
    ])

    if (store.asignaciones.length > 0) {
      // Si hay asignaciones, usar la primera como default
      const asig = store.asignaciones[0]
      seleccionarMovil({ idMovil: asig.idMovil, patente: asig.patente, detalle: asig.detalle })
      // Auto-set tipo de proceso si hay uno solo o coincide con el actual
      if (asig.idProceso && (!form.tipo_de_proceso_id || store.asignaciones.length === 1)) {
        form.tipo_de_proceso_id = asig.idProceso
      }
    } else if (store.movilAsignado) {
      seleccionarMovil(store.movilAsignado)
    } else {
      limpiarMovilSeleccionado()
    }

    // Auto-set tipo de proceso del operador si no se seteó por asignación
    if (!form.tipo_de_proceso_id) {
      const operador = store.operadores.find(o => o.idPersonal === form.operador_id)
      if (operador?.tipo_de_proceso_id) {
        form.tipo_de_proceso_id = operador.tipo_de_proceso_id
      }
    }
  }
}

async function onUnidadChange() {
  // Reset dependientes
  form.tipo_de_proceso_id = ''
  form.operador_id = isEncargado.value ? '' : form.operador_id
  limpiarMovilSeleccionado()
  store.movilAsignado = null
  // Cargar tipos de proceso y operadores de esta UN en paralelo
  await Promise.all([
    store.fetchTiposProceso(form.un_id),
    store.fetchMoviles(form.un_id),
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

// Removed old busquedaMovil watcher — selection/buscador now handled via mostrandoBuscador state

function formatearMovil(movil) {
  return `${movil.detalle} - ${movil.patente}`
}

function seleccionarMovil(movil) {
  form.equipo = formatearMovil(movil)
  form.cod_equipo = movil.idMovil || 0
  busquedaMovil.value = ''
  mostrandoBuscador.value = false
}

function seleccionarDesdeAsignacion(asig) {
  seleccionarMovil({ idMovil: asig.idMovil, patente: asig.patente, detalle: asig.detalle })
  if (asig.idProceso) {
    form.tipo_de_proceso_id = asig.idProceso
  }
}

function limpiarMovilSeleccionado() {
  form.equipo = ''
  form.cod_equipo = 0
  busquedaMovil.value = ''
  mostrandoBuscador.value = false
}

function abrirBuscador() {
  mostrandoBuscador.value = true
  busquedaMovil.value = ''
  nextTick(() => {
    inputBuscadorMovil.value?.focus()
  })
}

function cerrarBuscador() {
  mostrandoBuscador.value = false
  busquedaMovil.value = ''
}

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
  // Guard: if Enter pressed on non-final step, advance instead
  if (pasoActual.value < totalPasos - 1) {
    avanzar()
    return
  }
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
      equipo: form.equipo || '',
      operador: getOperadorNombre(form.operador_id),
      cod_operador: form.operador_id || 0,
      cod_equipo: form.cod_equipo || 0,
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
      tabla: 'tipo_de_proceso',
      codigo_tabla: form.tipo_de_proceso_id || 0,
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
