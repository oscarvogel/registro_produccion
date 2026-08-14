<template>
  <div class="mx-auto max-w-7xl px-3 py-3 pb-[7rem] md:px-4 md:pt-4">
    <div class="mb-3 flex items-center justify-between px-1">
      <div class="flex items-center gap-2.5">
        <button @click="$router.push({ name: 'home' })" class="p-2 rounded-lg text-neutral-500 hover:bg-neutral-200 transition-colors">
          <AppIcon name="back" />
        </button>
        <h1 class="text-2xl font-bold text-neutral-900 leading-none">Carga de Producción</h1>
      </div>
      <button class="p-2 text-neutral-500" type="button" aria-label="Más opciones"><AppIcon name="more" /></button>
    </div>

    <form class="md:grid md:grid-cols-[13.5rem_minmax(0,1fr)] md:items-start md:gap-3 xl:grid-cols-[14.5rem_minmax(0,1fr)]" novalidate @submit.prevent="guardar">
      <aside class="app-card mb-4 rounded-xl p-3 md:sticky md:top-20 md:mb-0 md:p-2.5">
        <div class="md:hidden">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-medium text-neutral-400">Paso {{ pasoActual + 1 }} de {{ totalPasos }}</span>
            <span class="text-xs font-semibold text-neutral-700">{{ pasos[pasoActual] }}</span>
          </div>
          <div class="h-2 bg-neutral-200 rounded-full overflow-hidden"><div class="h-full bg-primary rounded-full transition-all" :style="{ width: `${((pasoActual + 1) / totalPasos) * 100}%` }"></div></div>
        </div>
        <div class="hidden md:block">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Carga guiada</p>
          <h2 class="mt-1 text-lg font-extrabold text-primary-dark">Paso {{ pasoActual + 1 }} de {{ totalPasos }}</h2>
          <div class="mt-3 space-y-1.5">
            <button v-for="(paso, i) in pasos" :key="paso" type="button" :disabled="i > pasoActual" @click="irAPaso(i)" :class="['flex w-full items-center gap-2 rounded-lg border px-2.5 py-2 text-left text-sm transition-colors', i === pasoActual ? 'border-primary bg-primary/10 text-primary-dark' : i < pasoActual ? 'app-surface-muted text-neutral-700 hover:border-primary/40' : 'border-neutral-200 bg-transparent text-neutral-400']">
              <span :class="['flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-extrabold', i < pasoActual ? 'bg-success text-white' : i === pasoActual ? 'bg-primary text-on-primary' : 'app-surface-muted text-neutral-500']">{{ i < pasoActual ? 'OK' : i + 1 }}</span>
              <span class="min-w-0 flex-1 truncate font-semibold">{{ paso }}</span>
            </button>
          </div>
        </div>
      </aside>

      <div class="min-w-0 space-y-3">
        <div class="app-card mb-3 rounded-xl p-3.5">
          <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">Carga en curso</p>
          <p class="text-lg font-extrabold text-primary-dark">Estado: Sin guardar</p>
          <div class="mt-2 grid grid-cols-1 gap-2 text-sm text-neutral-700 sm:grid-cols-2 lg:grid-cols-5">
            <div><b>Fecha:</b> {{ form.fecha }}</div><div><b>UN:</b> {{ props.unidad.nombre }}</div><div><b>Operador:</b> {{ operadorNombre(form.cod_operador) || 'Pendiente' }}</div><div><b>Equipo:</b> {{ equipoSeleccionado()?.detalle || 'Pendiente' }}</div><div><b>Procesos:</b> {{ procesos.length }}</div>
          </div>
        </div>

        <SectionCard v-show="pasoActual === 0" title="Contexto de Carga">
          <p class="mb-3 text-sm text-neutral-500">Seleccioná el día correspondiente y verificá la unidad de negocio.</p>
          <InputField label="Fecha" type="date" v-model="form.fecha" required />
          <div class="mt-3">
            <label class="block text-sm font-medium text-neutral-700 mb-1">Unidad de Negocio</label>
            <div class="app-input flex w-full items-center justify-between rounded-xl border px-4 py-2.5">
              <span class="font-semibold">{{ props.unidad.nombre }}</span>
              <button type="button" class="text-sm font-semibold text-primary underline underline-offset-2" @click="$emit('back')">Cambiar</button>
            </div>
          </div>
        </SectionCard>

        <SectionCard v-show="pasoActual === 1" title="Identificación del Operador">
          <AutocompleteField
            v-if="canSelectOperador"
            label="Seleccionar Operador"
            v-model="form.cod_operador"
            :items="store.operadores"
            labelKey="nombre"
            valueKey="idPersonal"
            placeholder="— Escribí para buscar —"
            emptyMessage="Sin operadores configurados para esta unidad"
          />
          <div v-else><label class="mb-1 block text-sm font-medium">Operador</label><div class="app-input rounded-xl border px-4 py-2.5">{{ authStore.userName }}</div></div>
        </SectionCard>

        <SectionCard v-show="pasoActual === 2" title="Equipo / Maquinaria">
          <label class="mb-1 block text-sm font-medium">Equipo / Máquina</label>
          <select v-model.number="form.cod_equipo" :class="fieldClass"><option :value="0">Seleccionar equipo</option><option v-for="item in store.moviles" :key="item.idMovil" :value="item.idMovil">{{ item.detalle }} · {{ item.patente }}</option></select>
        </SectionCard>

        <SectionCard v-show="pasoActual === 3" title="Procesos / Actividades">
          <div class="mb-3 flex items-center justify-between gap-3"><p class="text-sm text-neutral-500">Agregá todas las tareas realizadas en la jornada.</p><button type="button" class="rounded-xl bg-primary px-3 py-2 text-sm font-bold text-on-primary" @click="agregarProceso">+ Agregar proceso</button></div>
          <div class="space-y-3"><div v-for="(proceso, index) in procesos" :key="proceso.key" class="rounded-xl border border-neutral-200 p-3"><div class="mb-2 flex justify-between"><b>Proceso {{ index + 1 }}</b><button v-if="procesos.length > 1" type="button" class="text-sm font-semibold text-error-dark" @click="quitarProceso(index)">Quitar</button></div><select v-model.number="proceso.tipo_proceso_id" :class="fieldClass"><option :value="0">Seleccionar proceso</option><option v-for="tipo in store.tiposProceso" :key="tipo.id" :value="tipo.id" :disabled="procesoUsado(tipo.id, proceso.key)">{{ tipo.nombre }}</option></select></div></div>
        </SectionCard>

        <SectionCard v-show="pasoActual === 4" title="Control de Tiempo">
          <div class="grid grid-cols-2 gap-4"><InputField label="Hora Inicio" type="number" step="0.01" min="0" v-model.number="form.hr_inicio" /><InputField label="Hora Fin" type="number" step="0.01" min="0" v-model.number="form.hr_fin" /></div>
          <div class="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2"><InputField label="Hs No Operativas" type="number" step="0.01" min="0" v-model.number="form.hrs_no_op" /><InputField label="Motivo no operativo" v-model="form.motivo_no_op" /></div>
        </SectionCard>

        <SectionCard v-show="pasoActual === 5" title="Datos de Producción">
          <div class="space-y-3"><div v-for="(proceso, index) in procesos" :key="proceso.key" class="rounded-xl border border-neutral-200 p-3"><p class="mb-3 font-bold">{{ nombreProceso(proceso.tipo_proceso_id) || `Proceso ${index + 1}` }}</p><div class="grid gap-3 md:grid-cols-2"><div v-if="requierePredio(proceso)"><label class="mb-1 block text-sm font-medium">Predio</label><select v-model.number="proceso.predio_id" :class="fieldClass"><option :value="0">Seleccionar predio</option><option v-for="predio in store.predios" :key="predio.idPredio" :value="predio.idPredio">{{ predio.nombre }}</option></select></div><div v-if="requiereActa(proceso)"><label class="mb-1 block text-sm font-medium">Acta</label><select v-model="proceso.acta" :class="fieldClass"><option value="">Seleccionar acta</option><option v-for="acta in store.actas" :key="acta.id || acta.numero" :value="acta.numero">{{ acta.numero }}</option></select></div><InputField v-if="requiereRodal(proceso)" label="Rodal" v-model="proceso.rodal" /><InputField v-if="esProceso(proceso, 'PERFILADO')" label="KM perfilado" type="number" step="0.01" min="0" v-model.number="proceso.km_perfilado" /><InputField v-if="esProceso(proceso, 'DISPOSICION')" label="Horas a disposición" type="number" step="0.01" min="0" v-model.number="proceso.hr_disposicion" /><InputField v-if="esProceso(proceso, 'REMOLQUE')" label="Horas de remolque" type="number" step="0.01" min="0" v-model.number="proceso.hr_remolque" /></div></div></div>
        </SectionCard>

        <SectionCard v-show="pasoActual === 6" title="Consumos">
          <label class="mb-3 flex items-center gap-2 text-sm font-semibold"><input v-model="cargaCombustible" type="checkbox" /> Se cargó combustible durante la jornada</label>
          <div v-if="cargaCombustible" class="grid gap-3 md:grid-cols-3"><InputField label="Litros" type="number" min="0" v-model.number="form.combustible" /><InputField label="Km / Horómetro" type="number" min="0" v-model.number="form.km_combustible" /><div><label class="mb-1 block text-sm font-medium">Lugar de carga</label><select v-model.number="form.lugar_carga" :class="fieldClass"><option :value="0">Seleccionar lugar</option><option v-for="lugar in store.lugaresCarga" :key="lugar.idLugarCarga" :value="lugar.idLugarCarga">{{ lugar.detalle }}</option></select></div><InputField label="Remito 1" v-model="form.remito" /><InputField label="Remito 2" v-model="form.remito2" /><InputField label="Remito 3" v-model="form.remito3" /></div>
          <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5"><InputField label="Aceite cadena" type="number" min="0" v-model.number="form.aceite_cadena" /><InputField label="Hidráulico" type="number" min="0" v-model.number="form.aceite_hidraulico" /><InputField label="Motor" type="number" min="0" v-model.number="form.aceite_motor" /><InputField label="Transmisión" type="number" min="0" v-model.number="form.aceite_transmision" /><InputField label="Embrague" type="number" min="0" v-model.number="form.aceite_embrague" /></div>
        </SectionCard>

        <SectionCard v-show="pasoActual === 7" title="Observaciones"><textarea v-model="form.observaciones" rows="4" maxlength="150" :class="`${fieldClass} resize-none`" placeholder="Observaciones del parte" /></SectionCard>

        <SectionCard v-show="pasoActual === 8" title="Revisión y Confirmación">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-2"><div class="app-surface-muted rounded-lg border px-3 py-2.5"><small>Unidad</small><p class="font-bold">{{ props.unidad.nombre }}</p></div><div class="app-surface-muted rounded-lg border px-3 py-2.5"><small>Procesos</small><p class="font-bold">{{ procesos.map(p => nombreProceso(p.tipo_proceso_id)).filter(Boolean).join(' + ') || 'Pendiente' }}</p></div><div class="app-surface-muted rounded-lg border px-3 py-2.5"><small>Equipo</small><p class="font-bold">{{ equipoSeleccionado()?.detalle || 'Pendiente' }}</p></div><div class="app-surface-muted rounded-lg border px-3 py-2.5"><small>Horario</small><p class="font-bold">{{ form.hr_inicio }} a {{ form.hr_fin }}</p></div></div>
        </SectionCard>

        <div v-if="errorLocal" class="rounded-xl border border-error/30 bg-error-light/40 px-4 py-3 text-sm font-semibold text-error-dark">{{ errorLocal }}</div>
        <div class="app-card hidden items-center justify-end gap-3 rounded-xl p-3.5 md:flex"><button v-if="pasoActual > 0" type="button" class="app-button-soft rounded-xl border px-4 py-2.5 font-bold" @click="retroceder">Anterior</button><button v-if="pasoActual < totalPasos - 1" type="button" class="rounded-xl bg-primary px-5 py-2.5 font-extrabold text-on-primary disabled:opacity-40" :disabled="!puedeAvanzar" @click="avanzar">Siguiente</button><button v-else type="submit" class="rounded-xl bg-primary px-5 py-2.5 font-extrabold text-on-primary disabled:opacity-60" :disabled="store.submitting">{{ store.submitting ? 'Guardando...' : `Guardar parte (${procesos.length} proceso${procesos.length === 1 ? '' : 's'})` }}</button></div>
      </div>

      <div class="app-card-glass fixed bottom-0 left-0 right-0 z-30 px-3 py-3 md:hidden"><div class="mx-auto flex max-w-2xl items-center gap-3"><button v-if="pasoActual > 0" type="button" @click="retroceder" class="app-button-soft flex flex-1 items-center justify-center rounded-xl border px-4 py-3.5 font-semibold">Anterior</button><div v-else class="flex-1" /><button v-if="pasoActual < totalPasos - 1" type="button" @click="avanzar" :disabled="!puedeAvanzar" class="flex flex-1 items-center justify-center rounded-xl bg-primary px-4 py-3.5 font-bold text-on-primary disabled:opacity-40">Siguiente</button><button v-else type="submit" :disabled="store.submitting" class="flex flex-1 items-center justify-center rounded-xl bg-primary px-4 py-3.5 font-bold text-on-primary disabled:opacity-60">{{ store.submitting ? 'Guardando...' : 'Guardar Registro' }}</button></div></div>
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
import AutocompleteField from '@/components/AutocompleteField.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({ unidad: { type: Object, required: true } })
defineEmits(['back'])
const router = useRouter(); const authStore = useAuthStore(); const store = useProduccionStore()
const canSelectOperador = computed(() => authStore.isAdmin || authStore.user?.encargado === 1)
const fieldClass = 'app-input w-full rounded-xl border px-4 py-2.5 placeholder:text-neutral-400 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:bg-neutral-200 transition-colors'
const today = new Date().toISOString().split('T')[0]; const cargaCombustible = ref(false); const errorLocal = ref(''); const pasoActual = ref(0); let processKey = 0
const pasos = ['Contexto', 'Operador', 'Equipo', 'Proceso', 'Tiempo', 'Producción', 'Consumos', 'Observaciones', 'Revisión']; const totalPasos = pasos.length
const form = reactive({ fecha: today, cod_operador: canSelectOperador.value ? 0 : Number(authStore.user?.idPersonal || 0), cod_equipo: 0, hr_inicio: 0, hr_fin: 0, hrs_no_op: 0, motivo_no_op: '', combustible: 0, km_combustible: 0, lugar_carga: 0, remito: '', remito2: '', remito3: '', aceite_cadena: 0, aceite_hidraulico: 0, aceite_motor: 0, aceite_transmision: 0, aceite_embrague: 0, observaciones: '' })
function nuevoProceso(){ processKey += 1; return reactive({ key: processKey, tipo_proceso_id:0, predio_id:0, acta:'', rodal:'', km_perfilado:0, hr_disposicion:0, hr_remolque:0 }) }
const procesos = reactive([nuevoProceso()]); function agregarProceso(){ procesos.push(nuevoProceso()) } function quitarProceso(i){ if(procesos.length>1) procesos.splice(i,1) }
function tipoProceso(id){ return store.tiposProceso.find(x=>Number(x.id)===Number(id))||null } function nombreProceso(id){ return tipoProceso(id)?.nombre||'' } function esProceso(p,n){ return nombreProceso(p.tipo_proceso_id).trim().toUpperCase()===n } function procesoUsado(id,key){ return procesos.some(x=>x.key!==key&&Number(x.tipo_proceso_id)===Number(id)) }
function requierePredio(p){ const n=nombreProceso(p.tipo_proceso_id).trim().toUpperCase(); return ['PERFILADO','DISPOSICION','REMOLQUE'].includes(n)||!!tipoProceso(p.tipo_proceso_id)?.requiere_predio } function requiereActa(p){ const n=nombreProceso(p.tipo_proceso_id).trim().toUpperCase(); if(n==='PERFILADO')return true; if(['DISPOSICION','REMOLQUE'].includes(n))return false; return !!tipoProceso(p.tipo_proceso_id)?.requiere_acta } function requiereRodal(p){ const n=nombreProceso(p.tipo_proceso_id).trim().toUpperCase(); if(n==='PERFILADO')return true; if(['DISPOSICION','REMOLQUE'].includes(n))return false; return !!tipoProceso(p.tipo_proceso_id)?.requiere_rodal }
function predioNombre(id){ return store.predios.find(x=>Number(x.idPredio)===Number(id))?.nombre||'' } function operadorNombre(id){ if(!canSelectOperador.value)return authStore.userName||''; return store.operadores.find(x=>Number(x.idPersonal)===Number(id))?.nombre||'' } function equipoSeleccionado(){ return store.moviles.find(x=>Number(x.idMovil)===Number(form.cod_equipo))||null }
const procesosTiposValidos = computed(()=>procesos.length>0&&procesos.every(p=>p.tipo_proceso_id>0)); const horasValidas = computed(()=>Number(form.hr_inicio)>0&&Number(form.hr_fin)>Number(form.hr_inicio));
const produccionValida = computed(()=>procesos.every(p=>{ if(requierePredio(p)&&!p.predio_id)return false; if(requiereActa(p)&&!String(p.acta||'').trim())return false; if(requiereRodal(p)&&!String(p.rodal||'').trim())return false; return Number(p.km_perfilado||0)>0||Number(p.hr_disposicion||0)>0||Number(p.hr_remolque||0)>0 }))
const consumosValidos = computed(()=>!cargaCombustible.value||(Number(form.combustible)>0&&Number(form.km_combustible)>0&&Number(form.lugar_carga)>0&&String(form.remito||'').trim().length>0))
const puedeAvanzar = computed(()=>[!!form.fecha, !!form.cod_operador, !!form.cod_equipo, procesosTiposValidos.value, horasValidas.value, produccionValida.value, consumosValidos.value, true, true][pasoActual.value])
function avanzar(){ if(puedeAvanzar.value&&pasoActual.value<totalPasos-1){pasoActual.value+=1; window.scrollTo({top:0,behavior:'smooth'})}} function retroceder(){if(pasoActual.value>0){pasoActual.value-=1; window.scrollTo({top:0,behavior:'smooth'})}} function irAPaso(i){if(i<pasoActual.value){pasoActual.value=i; window.scrollTo({top:0,behavior:'smooth'})}}
function validar(){ if(!form.fecha)return 'Indicá la fecha del parte.'; if(!form.cod_operador)return 'Seleccioná el operador.'; if(!form.cod_equipo)return 'Seleccioná el equipo.'; if(!procesosTiposValidos.value)return 'Completá los procesos del parte.'; if(!horasValidas.value)return 'La hora fin debe ser mayor que la hora inicio.'; if(Number(form.hrs_no_op)>0&&!String(form.motivo_no_op||'').trim())return 'Indicá el motivo de las horas no operativas.'; if(!produccionValida.value)return 'Completá ubicación y métricas de todos los procesos.'; if(!consumosValidos.value)return 'Completá los datos de combustible.'; return '' }
async function guardar(){ if(pasoActual.value<totalPasos-1){avanzar(); return} errorLocal.value=validar(); if(errorLocal.value)return; const equipo=equipoSeleccionado(); const payload={UN:props.unidad.nombre,fecha:form.fecha,equipo:equipo?`${equipo.detalle} - ${equipo.patente}`:'',operador:operadorNombre(form.cod_operador),cod_operador:Number(form.cod_operador),cod_equipo:Number(form.cod_equipo),cod_un:Number(props.unidad.idUnidadNegocio),hr_inicio:Number(form.hr_inicio),hr_fin:Number(form.hr_fin),combustible:cargaCombustible.value?Number(form.combustible||0):0,km_combustible:cargaCombustible.value?Number(form.km_combustible||0):0,lugar_carga:cargaCombustible.value?Number(form.lugar_carga||0):0,remito:cargaCombustible.value?String(form.remito||'').trim():'',remito2:cargaCombustible.value?String(form.remito2||'').trim():'',remito3:cargaCombustible.value?String(form.remito3||'').trim():'',aceite_cadena:Number(form.aceite_cadena||0),aceite_hidraulico:Number(form.aceite_hidraulico||0),aceite_motor:Number(form.aceite_motor||0),aceite_transmision:Number(form.aceite_transmision||0),aceite_embrague:Number(form.aceite_embrague||0),hrs_no_op:Number(form.hrs_no_op||0),motivo_no_op:String(form.motivo_no_op||'').trim(),observaciones:String(form.observaciones||'').trim(),procesos:procesos.map(p=>({tipo_proceso_id:Number(p.tipo_proceso_id),predio:requierePredio(p)?predioNombre(p.predio_id):'',acta:requiereActa(p)?String(p.acta||'').trim():'',rodal:requiereRodal(p)?String(p.rodal||'').trim():'',km_perfilado:Number(p.km_perfilado||0),hr_disposicion:Number(p.hr_disposicion||0),hr_remolque:Number(p.hr_remolque||0)}))}; try{await store.submitParteCaminos(payload); router.push({name:'home'})}catch{errorLocal.value=store.error||'No se pudo guardar el parte.'} }
watch(cargaCombustible,(activo)=>{if(activo)return; form.combustible=0;form.km_combustible=0;form.lugar_carga=0;form.remito='';form.remito2='';form.remito3=''})
onMounted(async()=>{await Promise.all([store.fetchTiposProceso(props.unidad.idUnidadNegocio),store.fetchMoviles(props.unidad.idUnidadNegocio),store.fetchLugaresCarga(props.unidad.idUnidadNegocio),store.fetchPredios(),store.fetchActas(),canSelectOperador.value?store.fetchOperadores(props.unidad.idUnidadNegocio):Promise.resolve()])})
</script>
