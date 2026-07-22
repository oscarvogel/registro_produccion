<template>
  <div class="mx-auto max-w-7xl px-3 py-3 pb-[7rem] md:px-4 md:pt-4">
    <!-- Header -->
    <div class="mb-3 flex items-center justify-between px-1">
      <div class="flex items-center gap-2.5">
      <button
        @click="$router.push({ name: 'home' })"
        class="p-2 rounded-lg text-neutral-500 hover:bg-neutral-200 transition-colors"
      >
        <AppIcon name="back" />
      </button>
      <h1 class="text-2xl font-bold text-neutral-900 leading-none">Carga de Producción</h1>
      </div>
      <button class="p-2 text-neutral-500" type="button" aria-label="Más opciones">
        <AppIcon name="more" />
      </button>
    </div>

    <!-- Loading catalogs -->
    <div v-if="store.loading" class="flex items-center justify-center py-20">
      <AppIcon name="loading" size="xl" class="animate-spin text-primary" />
    </div>

    <form v-else class="md:grid md:grid-cols-[13.5rem_minmax(0,1fr)] md:items-start md:gap-3 xl:grid-cols-[14.5rem_minmax(0,1fr)]" novalidate @submit.prevent="handleSubmit">

      <!-- Step indicator -->
      <aside class="app-card mb-4 rounded-xl p-3 md:sticky md:top-20 md:mb-0 md:p-2.5">
        <div class="md:hidden">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-medium text-neutral-400">Paso {{ pasoActual + 1 }} de {{ totalPasos }}</span>
            <span class="text-xs font-semibold text-neutral-700">{{ pasos[pasoActual] }}</span>
          </div>
          <div class="h-2 bg-neutral-200 rounded-full overflow-hidden">
            <div class="h-full bg-primary rounded-full transition-all duration-500 ease-out" :style="{ width: `${((pasoActual + 1) / totalPasos) * 100}%` }"></div>
          </div>
        </div>

        <div class="hidden md:block">
          <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Carga guiada</p>
          <h2 class="mt-1 text-lg font-extrabold text-primary-dark">Paso {{ pasoActual + 1 }} de {{ totalPasos }}</h2>
          <div class="mt-3 space-y-1.5">
            <button
              v-for="(paso, i) in pasos"
              :key="paso"
              type="button"
              :disabled="i > pasoActual"
              @click="irAPaso(i)"
              :class="[
                'flex w-full items-center gap-2 rounded-lg border px-2.5 py-2 text-left text-sm transition-colors',
                i === pasoActual
                  ? 'border-primary bg-primary/10 text-primary-dark'
                : i < pasoActual
                    ? 'app-surface-muted text-neutral-700 hover:border-primary/40'
                    : 'border-neutral-200 bg-transparent text-neutral-400',
              ]"
            >
              <span
                :class="[
                   'flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-extrabold',
                  i < pasoActual ? 'bg-success text-white' : i === pasoActual ? 'bg-primary text-on-primary' : 'app-surface-muted text-neutral-500',
                ]"
              >
                {{ i < pasoActual ? 'OK' : i + 1 }}
              </span>
              <span class="min-w-0 flex-1 truncate font-semibold">{{ paso }}</span>
              <span class="text-[11px] font-bold uppercase tracking-wide opacity-70">{{ stepStatus(i) }}</span>
            </button>
          </div>
        </div>
      </aside>

      <div class="min-w-0 space-y-3">

      <div class="app-card mb-3 rounded-xl p-3.5">
        <div class="mb-2.5 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">Carga en curso</p>
            <p class="text-lg font-extrabold text-primary-dark">Estado: Sin guardar</p>
          </div>
          <span class="w-fit rounded-full bg-warning-light px-3 py-1 text-xs font-bold text-warning-dark">Borrador local</span>
        </div>
        <div class="grid grid-cols-1 gap-2 text-sm text-neutral-700 sm:grid-cols-2 lg:grid-cols-5">
          <div class="truncate"><span class="font-bold text-neutral-900">Fecha:</span> {{ formatFechaResumen(form.fecha) }}</div>
          <div class="truncate"><span class="font-bold text-neutral-900">UN:</span> {{ getUnidadNombre(form.un_id) || 'Pendiente' }}</div>
          <div class="truncate"><span class="font-bold text-neutral-900">Operador:</span> {{ getOperadorNombre(form.operador_id) || 'Pendiente' }}</div>
          <div class="truncate"><span class="font-bold text-neutral-900">Equipo:</span> {{ movilSeleccionadoDetalle || 'Pendiente' }}</div>
          <div class="truncate"><span class="font-bold text-neutral-900">Proceso:</span> {{ tipoProcesoNombre || 'Pendiente' }}</div>
        </div>
      </div>

      <!-- ═══ 1. FECHA ═══ -->
      <SectionCard v-show="pasoActual === 0" title="Contexto de Carga">
        <p class="mb-3 text-sm text-neutral-500">
          Seleccioná el día correspondiente y la unidad de negocio para la que se cargará la producción.
        </p>
        <InputField
          label="Fecha"
          type="date"
          v-model="form.fecha"
          required
        />
        <p class="mt-2 text-xs text-neutral-400">Si estás cargando una producción atrasada, modificá esta fecha.</p>

        <div class="mt-3">
          <AutocompleteField
            label="Unidad de Negocio"
            v-model="form.un_id"
            :items="store.unidadesNegocio"
            labelKey="nombre"
            valueKey="idUnidadNegocio"
            placeholder="Seleccionar unidad"
            :loading="catalogLoading('unidadesNegocio')"
            :error="catalogError('unidadesNegocio')"
            :errorMessage="catalogErrorMessage('unidades de negocio')"
            emptyMessage="Sin unidades de negocio configuradas"
            :stale="catalogStale('unidadesNegocio')"
            @select="onUnidadChange"
          />
          <button
            v-if="catalogHasError('unidadesNegocio')"
            type="button"
            class="mt-2 text-xs font-semibold text-primary underline underline-offset-2"
            @click="store.retryCatalogo('unidadesNegocio')"
          >
            Reintentar carga de unidades
          </button>
        </div>
      </SectionCard>

      <!-- ═══ 2. UNIDAD DE NEGOCIO ═══ -->
      <SectionCard v-show="pasoActual === 3" title="Proceso / Actividad">
        <p class="mb-3 text-sm text-neutral-500">
          Seleccioná el tipo de proceso que corresponde a esta carga. Los campos de producción se ajustan según esta selección.
        </p>
        <AutocompleteField v-if="false"
          label="Unidad de Negocio"
          v-model="form.un_id"
          :items="store.unidadesNegocio"
          labelKey="nombre"
          valueKey="idUnidadNegocio"
          placeholder="— Escribí para buscar —"
          @select="onUnidadChange"
        />

        <div class="mt-3">
          <AutocompleteField
            label="Tipo de Proceso"
            v-model="form.tipo_de_proceso_id"
            :items="store.tiposProceso"
            labelKey="nombre"
            valueKey="id"
            :disabled="!form.un_id || catalogLoading('tiposProceso')"
            :placeholder="!form.un_id ? '— Primero seleccioná UN —' : catalogHasError('tiposProceso') ? '— Error de carga —' : store.tiposProceso.length === 0 ? '— Sin procesos disponibles —' : '— Escribí para buscar —'"
            :loading="catalogLoading('tiposProceso')"
            :error="catalogError('tiposProceso')"
            :errorMessage="catalogErrorMessage('tipos de proceso')"
            emptyMessage="Sin procesos configurados para esta unidad"
            :stale="catalogStale('tiposProceso')"
            @select="onTipoProcesoChange"
          />
          <button
            v-if="catalogHasError('tiposProceso')"
            type="button"
            class="mt-2 text-xs font-semibold text-primary underline underline-offset-2"
            @click="store.retryCatalogo('tiposProceso', form.un_id)"
          >
            Reintentar tipos de proceso
          </button>
        </div>
      </SectionCard>

      <!-- ═══ 3. OPERADOR ═══ -->
      <SectionCard v-show="pasoActual === 1" title="Identificacion del Operador">
        <!-- Si es operador: bloqueado -->
        <div v-if="!canSelectOperador">
          <label class="block text-sm font-medium text-neutral-700 mb-1">Operador</label>
          <div class="app-input w-full rounded-xl border px-4 py-2.5">
            {{ authStore.userName }}
          </div>
        </div>
        <!-- Si es encargado: seleccionar (requiere UN primero) -->
        <div v-else>
          <AutocompleteField
            label="Seleccionar Operador"
            v-model="form.operador_id"
            :items="store.operadores"
            labelKey="nombre"
            valueKey="idPersonal"
            :disabled="!form.un_id || catalogLoading('operadores')"
            :placeholder="!form.un_id ? '— Primero seleccioná UN —' : catalogHasError('operadores') ? '— Error de carga —' : store.operadores.length === 0 ? '— Sin operadores —' : '— Escribí para buscar —'"
            :loading="catalogLoading('operadores')"
            :error="catalogError('operadores')"
            :errorMessage="catalogErrorMessage('operadores')"
            emptyMessage="Sin operadores configurados para esta unidad"
            :stale="catalogStale('operadores')"
            @select="onOperadorChange"
          />
          <button
            v-if="catalogHasError('operadores')"
            type="button"
            class="mt-2 text-xs font-semibold text-primary underline underline-offset-2"
            @click="store.retryCatalogo('operadores', form.un_id)"
          >
            Reintentar operadores
          </button>
        </div>
      </SectionCard>

      <!-- ═══ 4. MAQUINARIA ═══ -->
      <SectionCard v-show="pasoActual === 2" title="Equipo / Maquinaria">
        <!-- ── Estado: Máquina ya seleccionada ── -->
        <div v-if="form.cod_equipo && !mostrandoBuscador" class="space-y-3">
          <div class="flex items-center gap-3 p-3 bg-success-light/40 border border-success/30 rounded-xl">
            <AppIcon name="success" class="text-success-dark shrink-0" />
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
                class="app-button-soft max-w-full truncate rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors"
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
                class="app-surface-muted w-full rounded-lg border px-3 py-2 text-left transition-colors hover:border-primary/30"
              >
                <p class="text-sm font-semibold text-neutral-900 truncate">{{ asig.detalle }}</p>
                <p class="text-[11px] text-neutral-400">{{ asig.patente }} · {{ getProcesoTexto(asig.idProceso) }}</p>
              </button>
            </div>
          </div>

          <!-- Mensaje si no hay asignaciones ni movilAsignado -->
          <div v-else-if="!form.operador_id" class="app-surface-muted mb-3 rounded-lg border p-3 text-sm text-neutral-500">
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
                @focus="abrirListaMoviles"
                @click="abrirListaMoviles"
                @input="abrirListaMoviles"
                @blur="onInputBlur"
                :class="fieldClass"
                placeholder="Ej: 1470, JOHN DEERE, N° 3..."
              />
              <button
                v-if="busquedaMovil.trim()"
                type="button"
                @mousedown.prevent="limpiarBusquedaMovil"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
              >
                <AppIcon name="close" size="sm" />
              </button>
            </div>
            <div
              v-if="mostrarListaMoviles"
              data-moviles-dropdown
              class="app-table mt-1.5 max-h-52 overflow-y-auto rounded-xl"
            >
              <button
                v-for="movil in movilesFiltrados"
                :key="movil.idMovil"
                type="button"
                data-moviles-item
                @mousedown.prevent="seleccionarMovil(movil)"
                class="app-table-row w-full border-b border-neutral-100 px-3 py-2 text-left last:border-b-0"
              >
                <p class="text-sm font-medium text-neutral-900 truncate">{{ movil.detalle }}</p>
                <p class="text-[11px] text-neutral-400">{{ movil.patente }} · ID {{ movil.idMovil }}</p>
              </button>
            </div>
            <div
              v-else-if="mostrarNoResultados"
              class="app-surface-muted mt-1.5 rounded-lg p-2.5 text-xs text-neutral-400"
            >
              Sin resultados para "{{ busquedaMovil }}".
            </div>
            <div
              v-else-if="mostrarSinMoviles"
              class="app-surface-muted mt-1.5 rounded-lg p-2.5 text-xs text-neutral-400"
            >
              {{ mensajeMovilesVacios }}
              <button
                v-if="catalogHasError('moviles')"
                type="button"
                class="ml-1 font-semibold text-primary underline underline-offset-2"
                @mousedown.prevent="store.retryCatalogo('moviles', form.un_id)"
              >
                Reintentar
              </button>
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
            min="1"
            step="any"
            :invalid="mostrarErrorHoras"
            required
          />
          <InputField
            label="Hora Fin"
            type="number"
            v-model.number="form.hr_fin"
            placeholder="Ej: 1850"
            min="1"
            step="any"
            :invalid="mostrarErrorHoras"
            required
          />
        </div>
        <div
          v-if="mostrarErrorHoras"
          class="mt-3 px-3 py-2 bg-error-light/40 border border-error/30 rounded-lg text-sm text-error-dark"
        >
          <span v-if="Number(form.hr_inicio) > 0 && ultimaHoraFinRef > 0 && Number(form.hr_inicio) < ultimaHoraFinRef">
            La hora de inicio ({{ form.hr_inicio }}) no puede ser menor al fin del registro anterior ({{ ultimaHoraFinRef }}).
          </span>
          <span v-else>
            La hora de inicio y fin deben ser mayores a 0, y la hora final no puede ser menor a la inicial.
          </span>
        </div>
        <div class="grid grid-cols-2 gap-4 mt-3">
          <InputField
            label="Hs No Operativas"
            type="number"
            v-model.number="form.hrs_no_op"
            min="0"
          />
          <div>
            <AutocompleteField
              v-model="motivoSeleccionado"
              label="Motivo (lista)"
              :items="motivosNoOperativos"
              placeholder="Buscar motivo"
            />
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

          <!-- Pies y Pulpable (exclusivo cuando esProceso) -->
          <template v-if="esProceso">
            <InputField
              label="16 Pies"
              type="number"
              v-model.number="form.pies_16"
              placeholder="0"
              min="0"
              step="0.01"
            />
            <InputField
              label="14 Pies"
              type="number"
              v-model.number="form.pies_14"
              placeholder="0"
              min="0"
              step="0.01"
            />
            <InputField
              label="12 Pies"
              type="number"
              v-model.number="form.pies_12"
              placeholder="0"
              min="0"
              step="0.01"
            />
            <InputField
              label="10 Pies"
              type="number"
              v-model.number="form.pies_10"
              placeholder="0"
              min="0"
              step="0.01"
            />
            <InputField
              label="Pulpable"
              type="number"
              v-model.number="form.pulpable"
              placeholder="0"
              min="0"
              step="0.01"
            />
          </template>

          <!-- Hora inicio / fin (para HORAS MAQUINAS) -->
          <div v-if="camposActivos.includes('hora_inicio')" class="grid grid-cols-2 gap-4">
            <InputField
              label="Hora Inicio Máq."
              type="number"
              v-model.number="form.hr_inicio"
              placeholder="Ej: 1200"
              min="1"
              step="any"
              :invalid="mostrarErrorHoras || (mostrarErrorProduccion && form.hr_inicio <= 0)"
            />
            <InputField
              label="Hora Fin Máq."
              type="number"
              v-model.number="form.hr_fin"
              placeholder="Ej: 1850"
              min="1"
              step="any"
              :invalid="mostrarErrorHoras || (mostrarErrorProduccion && form.hr_fin <= form.hr_inicio)"
            />
          </div>
          <div v-if="camposActivos.includes('hora_inicio') && form.hr_fin > form.hr_inicio"
               class="px-3 py-2 bg-info-light/50 border border-info/30 rounded-lg text-sm text-info-dark">
            Horas trabajadas: <strong>{{ form.hr_fin - form.hr_inicio }}</strong>
          </div>
          <div v-if="camposActivos.includes('hora_inicio') && mostrarErrorHoras"
               class="px-3 py-2 bg-error-light/40 border border-error/30 rounded-lg text-sm text-error-dark">
            La hora de inicio y fin deben ser mayores a 0, y la hora final debe ser mayor a la inicial.
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
        <div
          v-if="mostrarErrorProduccion"
          class="mt-3 px-3 py-2 bg-error-light/40 border border-error/30 rounded-lg text-sm text-error-dark"
        >
          No se puede continuar con valores en 0. Completá los campos de producción con valores mayores a 0.
        </div>
      </SectionCard>

      <div v-show="pasoActual === 5" v-if="form.tipo_de_proceso_id && camposActivos.length === 0" class="app-surface-muted rounded-lg border p-3 text-sm text-neutral-500">
        No hay campos de producción definidos para este tipo de proceso.
      </div>

      <!-- ═══ 7. COMBUSTIBLE ═══ -->
      <SectionCard v-show="pasoActual === 6" title="Combustible">
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

      <!-- ═══ 8. ACEITES ═══ -->
      <SectionCard v-show="pasoActual === 6" title="Consumos">
        <div class="space-y-3">
          <InputField
            label="Hidráulico (litros)"
            type="number"
            v-model.number="form.aceite_hidraulico"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Motor (litros)"
            type="number"
            v-model.number="form.aceite_motor"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Transmisión (litros)"
            type="number"
            v-model.number="form.aceite_transmision"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Embrague (litros)"
            type="number"
            v-model.number="form.aceite_embrague"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Cadena (litros)"
            type="number"
            v-model.number="form.aceite_cadena"
            placeholder="0"
            min="0"
          />
        </div>
      </SectionCard>

      <!-- ═══ 9. SISTEMA DE CORTE (solo para PROCESO) ═══ -->
      <SectionCard v-show="pasoActual === 6" v-if="esProceso" title="Sistema de Corte">
        <div class="space-y-3">
          <InputField
            label="Espada"
            type="number"
            v-model.number="form.espada"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Puntera"
            type="number"
            v-model.number="form.puntera"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Cadena"
            type="number"
            v-model.number="form.cadena"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Piñón"
            type="number"
            v-model.number="form.pinon"
            placeholder="0"
            min="0"
          />
          <InputField
            label="Cantidad de Cadenas"
            type="number"
            v-model.number="form.cantidad_cadenas"
            placeholder="0"
            min="0"
          />
        </div>
      </SectionCard>

      <!-- ═══ 10. UBICACIÓN Y REFERENCIA ═══ -->
      <SectionCard v-show="pasoActual === 7" title="Ubicación y Referencia">
        <div>
          <AutocompleteField
            label="Lugar de Carga"
            v-model="form.lugar_carga_id"
            :items="store.lugaresCarga"
            labelKey="detalle"
            valueKey="idLugarCarga"
            placeholder="— Buscar lugar de carga —"
            :loading="catalogLoading('lugaresCarga')"
            :error="catalogError('lugaresCarga')"
            :errorMessage="catalogErrorMessage('lugares de carga')"
            emptyMessage="Sin lugares de carga configurados para esta unidad"
            :stale="catalogStale('lugaresCarga')"
          />
          <button
            v-if="catalogHasError('lugaresCarga')"
            type="button"
            class="mt-2 text-xs font-semibold text-primary underline underline-offset-2"
            @click="store.retryCatalogo('lugaresCarga', form.un_id)"
          >
            Reintentar lugares de carga
          </button>
        </div>

        <template v-if="ubicacionOperativaRequerida">
          <div v-if="requiereActa" class="mt-3">
            <AutocompleteField
              label="Acta"
              :modelValue="form.acta"
              :items="store.actas"
              labelKey="numero"
              valueKey="numero"
              placeholder="— Buscar acta —"
              :loading="catalogLoading('actas')"
              :error="catalogError('actas')"
              :errorMessage="catalogErrorMessage('actas')"
              emptyMessage="Sin actas configuradas"
              :stale="catalogStale('actas')"
              @select="item => { form.acta = item ? item.numero : '' }"
            />
            <button
              v-if="catalogHasError('actas')"
              type="button"
              class="mt-2 text-xs font-semibold text-primary underline underline-offset-2"
              @click="store.retryCatalogo('actas')"
            >
              Reintentar actas
            </button>
          </div>

          <div v-if="requierePredio" class="mt-3">
            <AutocompleteField
              label="Predio"
              v-model="form.predio_id"
              :items="store.predios"
              labelKey="nombre"
              valueKey="idPredio"
              placeholder="— Buscar predio —"
              :loading="catalogLoading('predios')"
              :error="catalogError('predios')"
              :errorMessage="catalogErrorMessage('predios')"
              emptyMessage="Sin predios configurados"
              :stale="catalogStale('predios')"
              @select="onPredioChange"
            />
            <button
              v-if="catalogHasError('predios')"
              type="button"
              class="mt-2 text-xs font-semibold text-primary underline underline-offset-2"
              @click="store.retryCatalogo('predios')"
            >
              Reintentar predios
            </button>
          </div>

          <div v-if="requiereRodal" class="mt-3">
            <AutocompleteField
              v-if="store.rodales.length > 0"
              label="Rodal"
              v-model="form.rodal_id"
              :items="store.rodales"
              labelKey="rodal"
              valueKey="idRodal"
              placeholder="— Buscar rodal —"
              :loading="catalogLoading('rodales')"
              :error="catalogError('rodales')"
              :errorMessage="catalogErrorMessage('rodales')"
              emptyMessage="Sin rodales configurados para este predio"
              :stale="catalogStale('rodales')"
            />
            <div v-else-if="catalogHasError('rodales')" class="app-surface-muted rounded-lg border p-3 text-sm text-neutral-600">
              No se pudo cargar rodales.
              <button
                type="button"
                class="font-semibold text-primary underline underline-offset-2"
                @click="store.retryCatalogo('rodales', form.predio_id)"
              >
                Reintentar
              </button>
            </div>
            <div v-else>
              <label class="block text-sm font-medium text-neutral-700 mb-1">Rodal</label>
              <input
                type="text"
                v-model="form.rodal_manual"
                placeholder="Ingresá el rodal manualmente"
                :class="fieldClass"
              />
            </div>
          </div>
        </template>

        <div v-else class="app-surface-muted mt-3 rounded-lg border p-3 text-sm text-neutral-500">
          Acta, Predio y Rodal no aplican para este tipo de trabajo.
        </div>
        <div
          v-if="mostrarErrorUbicacion"
          class="mt-3 px-3 py-2 bg-error-light/40 border border-error/30 rounded-lg text-sm text-error-dark"
        >
          {{ mensajeUbicacionIncompleta }}
        </div>
      </SectionCard>

      <!-- ═══ OBSERVACIONES ═══ -->
      <SectionCard v-show="pasoActual === 7" title="Observaciones">
        <textarea
          v-model="form.observaciones"
          rows="3"
          placeholder="Notas adicionales..."
          :class="`${fieldClass} resize-none min-h-32`"
        />
      </SectionCard>

      <SectionCard v-show="pasoActual === 8" title="Revisión y Confirmación">
        <p class="mb-3 text-sm text-neutral-500">
          Revisá los datos principales antes de guardar el registro de producción.
        </p>
        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <div
            v-for="item in revisionItems"
            :key="item.label"
            class="app-surface-muted rounded-lg border px-3 py-2.5"
          >
            <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">{{ item.label }}</p>
            <p class="mt-1 text-sm font-extrabold text-neutral-900">{{ item.value }}</p>
          </div>
        </div>
      </SectionCard>

      <!-- Error -->
      <div
        v-if="store.error"
        class="flex items-center gap-2 p-3 bg-error-light text-error-dark rounded-lg text-sm"
      >
        <AppIcon name="error" class="text-error shrink-0" />
        <span>{{ store.error }}</span>
      </div>
      <div class="app-card hidden items-center justify-between gap-3 rounded-xl p-3.5 md:flex">
        <p class="max-w-md text-sm font-semibold text-error-dark">
          {{ mensajePasoIncompleto }}
        </p>
        <div class="flex items-center justify-end gap-3">
        <button
          v-if="pasoActual > 0"
          type="button"
          @click="retroceder"
          class="app-button-soft rounded-xl border px-4 py-2.5 text-sm font-bold text-neutral-700 hover:border-primary/30"
        >
          Anterior
        </button>
        <button
          type="button"
          @click="guardarBorrador"
          class="app-button-soft rounded-xl border px-4 py-2.5 text-sm font-bold text-neutral-500 hover:border-primary/30"
        >
          Guardar borrador
        </button>
        <button
          v-if="pasoActual < totalPasos - 1"
          type="button"
          @click="avanzar"
          :disabled="!puedeAvanzar"
          class="rounded-xl bg-primary px-5 py-2.5 text-sm font-extrabold text-on-primary disabled:cursor-not-allowed disabled:opacity-40"
        >
          Siguiente
        </button>
        <button
          v-else
          type="submit"
          :disabled="store.submitting"
          class="rounded-xl bg-primary px-5 py-2.5 text-sm font-extrabold text-on-primary disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ store.submitting ? 'Guardando...' : 'Guardar Registro' }}
        </button>
        </div>
      </div>
      </div>

      <!-- Step navigation — fixed bottom -->
      <div class="app-card-glass fixed bottom-0 left-0 right-0 z-30 px-3 py-3 md:hidden">
        <div class="mx-auto flex max-w-2xl items-center gap-3">
          <button
            v-if="pasoActual > 0"
            type="button"
            @click="retroceder"
            class="app-button-soft flex flex-1 items-center justify-center gap-2 rounded-xl border px-4 py-3.5 font-semibold text-neutral-700 transition-colors"
          >
            <AppIcon name="back" size="sm" :stroke-width="2.5" />
            Anterior
          </button>
          <div v-else class="flex-1" />

          <button
            v-if="pasoActual < totalPasos - 1"
            type="button"
            @click="avanzar"
            :disabled="!puedeAvanzar"
            class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3.5 font-bold text-on-primary shadow-[0_4px_14px_rgba(20,61,35,0.25)] transition-colors active:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
          >
            Siguiente
            <AppIcon name="forward" size="sm" :stroke-width="2.5" />
          </button>
          <button
            v-else
            type="submit"
            :disabled="store.submitting"
            class="flex flex-1 items-center justify-center gap-2.5 rounded-xl bg-primary px-4 py-3.5 font-bold text-on-primary shadow-[0_8px_18px_rgba(20,61,35,0.25)] transition-colors active:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-60"
          >
            <AppIcon v-if="store.submitting" name="loading" class="animate-spin" />
            <AppIcon v-else name="save" />
            {{ store.submitting ? 'Guardando...' : 'Guardar Registro' }}
          </button>
        </div>
        <p v-if="mensajePasoIncompleto" class="mx-auto mt-2 max-w-2xl px-1 text-xs text-error-dark">
          {{ mensajePasoIncompleto }}
        </p>
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
import AutocompleteField from '@/components/AutocompleteField.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import motivosNoOperativos from '@/data/motivosNoOperativos.json'
import { cleanLocationValues, getLocationRequirements, shouldShowActaPredioFields } from '@/services/actaPredioRules'
import { focusInside } from '@/utils/focusInside'

const router = useRouter()
const authStore = useAuthStore()
const store = useProduccionStore()

const isAdmin = computed(() => authStore.isAdmin)
const isEncargado = computed(() => authStore.user?.encargado === 1)
const canSelectOperador = computed(() => isEncargado.value || isAdmin.value)
const cargoCombustible = ref(false)
const motivoSeleccionado = ref('')
const busquedaMovil = ref('')
const mostrandoBuscador = ref(false)
const listaMovilesAbierta = ref(false)
const inputBuscadorMovil = ref(null)
const ultimaHoraFinRef = ref(0)
const fieldClass = 'app-input w-full rounded-xl border px-4 py-2.5 placeholder:text-neutral-400 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:bg-neutral-200 transition-colors'
const preferenciasKey = computed(() => `produccion_preferencias_${authStore.user?.idPersonal || 'anon'}`)

// ─── Wizard steps ───
const pasoActual = ref(0)
const pasos = ['Contexto', 'Operador', 'Equipo', 'Proceso', 'Tiempo', 'Producción', 'Consumos', 'Ubicación', 'Revisión']
const totalPasos = pasos.length

// Determina si el tipo de proceso elegido es "PROCESO"
const esProceso = computed(() => tipoProcesoNombre.value.trim().toUpperCase() === 'PROCESO')

function catalogState(name) {
  return store.catalogStatus?.[name] || {}
}

function catalogLoading(name) {
  return catalogState(name).state === 'loading'
}

function catalogHasError(name) {
  return catalogState(name).state === 'error'
}

function catalogError(name) {
  return catalogHasError(name) ? catalogState(name).lastError || true : ''
}

function catalogErrorMessage(label) {
  return `No se pudo cargar ${label}. Reintentar`
}

function catalogStale(name) {
  return !!catalogState(name).stale
}

const puedeAvanzar = computed(() => {
  switch (pasoActual.value) {
    case 0: return !!form.fecha && !!form.un_id
    case 1: return !!form.operador_id
    case 2: return form.cod_equipo > 0
    case 3: return !!form.tipo_de_proceso_id
    case 4: return horasValidas.value
    case 5: return produccionValida.value
    case 6: return true
    case 7: return ubicacionValida.value
    case 8: return true
    default: return true
  }
})

function avanzar() {
  if (puedeAvanzar.value && pasoActual.value < totalPasos - 1) {
    pasoActual.value += 1
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function retroceder() {
  if (pasoActual.value > 0) {
    pasoActual.value -= 1
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
  const tipo = tipoProcesoSeleccionado.value
  if (!tipo || !tipo.campos) return []
  return tipo.campos.split(',').map(c => c.trim())
})

const tipoProcesoSeleccionado = computed(() => {
  if (!form.tipo_de_proceso_id) return null
  return store.tiposProceso.find(t => t.id === form.tipo_de_proceso_id)
    || store.todosLosTipos.find(t => t.id === form.tipo_de_proceso_id)
    || null
})

// Nombre del tipo de proceso seleccionado
const tipoProcesoNombre = computed(() => {
  return tipoProcesoSeleccionado.value?.nombre || ''
})

const requisitosUbicacion = computed(() => getLocationRequirements(tipoProcesoSeleccionado.value))
const requiereActa = computed(() => requisitosUbicacion.value.requiere_acta)
const requierePredio = computed(() => requisitosUbicacion.value.requiere_predio)
const requiereRodal = computed(() => requisitosUbicacion.value.requiere_rodal)
const ubicacionOperativaRequerida = computed(() => shouldShowActaPredioFields(tipoProcesoSeleccionado.value))

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
  return !!form.un_id && listaMovilesAbierta.value && movilesFiltrados.value.length > 0
})

const mostrarNoResultados = computed(() => {
  return !!form.un_id
    && listaMovilesAbierta.value
    && busquedaNormalizada.value.length >= 1
    && (store.moviles || []).length > 0
    && movilesFiltrados.value.length === 0
})

const mostrarSinMoviles = computed(() => {
  return !!form.un_id
    && listaMovilesAbierta.value
    && !catalogLoading('moviles')
    && (store.moviles || []).length === 0
})

const mensajeMovilesVacios = computed(() => {
  if (catalogHasError('moviles')) return 'No se pudo cargar equipos.'
  if (catalogStale('moviles')) return 'Usando equipos guardados en este dispositivo.'
  return 'No hay equipos disponibles para esta unidad.'
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
  operador_id: canSelectOperador.value ? '' : authStore.user?.idPersonal,
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
  aceite_hidraulico: 0,
  aceite_motor: 0,
  aceite_transmision: 0,
  aceite_embrague: 0,
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
  // Mecánica / Sistema de Corte
  espada: 0,
  puntera: 0,
  cadena: 0,
  pinon: 0,
  cantidad_cadenas: 0,
  // Pies y pulpable (PROCESO)
  pies_16: 0,
  pies_14: 0,
  pies_12: 0,
  pies_10: 0,
  pulpable: 0,
  // Lugar de carga
  lugar_carga_id: 0,
})

const actaNormalizada = computed(() => String(form.acta ?? '').trim())

const horasValidas = computed(() => {
  const inicio = Number(form.hr_inicio)
  const fin = Number(form.hr_fin)
  if (inicio <= 0 || fin <= 0) return false
  if (fin < inicio) return false
  // hr_inicio no puede ser menor al hr_fin del registro anterior
  if (ultimaHoraFinRef.value > 0 && inicio < ultimaHoraFinRef.value) return false
  return true
})

const produccionValida = computed(() => {
  if (!form.tipo_de_proceso_id || camposActivos.value.length === 0) return true

  const validadores = {
    tn_despachadas: () => Number(form.tn_despachadas) > 0,
    carros: () => Number(form.carros) > 0,
    distancia_recorrida: () => Number(form.mtrs_recorridos) > 0,
    m3: () => Number(form.m3) > 0,
    plantas: () => Number(form.plantas) > 0,
    has: () => Number(form.has) > 0,
    horas_disposicion: () => Number(form.hr_disposicion) > 0,
    km: () => Number(form.km) > 0,
    hora_inicio: () => horasValidas.value,
  }

  return camposActivos.value.every((campo) => {
    const validar = validadores[campo]
    return typeof validar === 'function' ? validar() : true
  })
})

const rodalCompleto = computed(() => {
  if (form.rodal_id) return true
  return String(form.rodal_manual ?? '').trim().length > 0
})

const ubicacionValida = computed(() => {
  if (!ubicacionOperativaRequerida.value) return true
  if (requiereActa.value && (!actaNormalizada.value || actaNormalizada.value === '0')) return false
  if (requierePredio.value && !form.predio_id) return false
  if (requiereRodal.value && !rodalCompleto.value) return false
  return true
})

const ubicacionCatalogosConError = computed(() => {
  if (!ubicacionOperativaRequerida.value) return []
  const catalogos = []
  if (requiereActa.value && catalogHasError('actas') && store.actas.length === 0) catalogos.push('actas')
  if (requierePredio.value && catalogHasError('predios') && store.predios.length === 0) catalogos.push('predios')
  if (requiereRodal.value && form.predio_id && catalogHasError('rodales') && store.rodales.length === 0) catalogos.push('rodales')
  return catalogos
})

const mensajeUbicacionIncompleta = computed(() => {
  if (!ubicacionOperativaRequerida.value) return ''
  if (ubicacionCatalogosConError.value.length > 0) {
    return `No se pudo cargar ${ubicacionCatalogosConError.value.join(', ')}. Reintentá el catálogo para completar la ubicación.`
  }
  const pendientes = []
  if (requiereActa.value) pendientes.push('Acta')
  if (requierePredio.value) pendientes.push('Predio')
  if (requiereRodal.value) pendientes.push('Rodal')
  return `Completá ${pendientes.join(', ')} para este tipo de trabajo.`
})

const mostrarErrorHoras = computed(() => {
  return pasoActual.value >= 4 && !horasValidas.value
})

const mostrarErrorProduccion = computed(() => {
  return pasoActual.value >= 5 && !produccionValida.value
})

const mostrarErrorUbicacion = computed(() => {
  return pasoActual.value >= 7 && !ubicacionValida.value
})

const stepComplete = computed(() => [
  !!form.fecha && !!form.un_id,
  !!form.operador_id,
  form.cod_equipo > 0,
  !!form.tipo_de_proceso_id,
  horasValidas.value,
  produccionValida.value,
  true,
  ubicacionValida.value,
  puedeAvanzar.value,
])

const revisionItems = computed(() => [
  { label: 'Fecha', value: formatFechaResumen(form.fecha) },
  { label: 'Unidad de negocio', value: getUnidadNombre(form.un_id) || 'Pendiente' },
  { label: 'Operador', value: getOperadorNombre(form.operador_id) || 'Pendiente' },
  { label: 'Equipo', value: movilSeleccionadoDetalle.value || 'Pendiente' },
  { label: 'Proceso', value: tipoProcesoNombre.value || 'Pendiente' },
  { label: 'Horario', value: `${form.hr_inicio || '-'} a ${form.hr_fin || '-'}` },
  { label: 'Producción', value: `${resolveProduccion() || 0} ${resolveUnidadProduccion() || ''}`.trim() },
  { label: 'Ubicación', value: [form.acta ? `Acta ${form.acta}` : '', getPredioNombre(form.predio_id), getRodalNombre()].filter(Boolean).join(' / ') || 'Pendiente' },
])

function stepStatus(index) {
  if (index === pasoActual.value) return 'Actual'
  if (index < pasoActual.value && stepComplete.value[index]) return 'Validado'
  return 'Pendiente'
}

const mensajePasoIncompleto = computed(() => {
  if (pasoActual.value === 4 && !horasValidas.value) {
    const inicio = Number(form.hr_inicio)
    if (ultimaHoraFinRef.value > 0 && inicio > 0 && inicio < ultimaHoraFinRef.value) {
      return `La hora de inicio (${form.hr_inicio}) no puede ser menor al fin del registro anterior (${ultimaHoraFinRef.value}).`
    }
    return 'Revisá las horas: inicio y fin deben ser mayores a 0, y fin no puede ser menor al inicio.'
  }
  if (pasoActual.value === 5 && !produccionValida.value) {
    return 'Completá los campos de producción con valores mayores a 0 para continuar.'
  }
  if (pasoActual.value === 7 && !ubicacionValida.value) {
    return mensajeUbicacionIncompleta.value
  }
  return ''
})

// ─── Load initial data ───
onMounted(async () => {
  await store.loadCatalogos()
  await aplicarUnidadInicial()
  await aplicarPreferenciasGuardadas()

  if (!canSelectOperador.value) {
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

    await autocompletarHoraInicio({ force: true })
  }
  // Si es encargado, los operadores se cargan al elegir la UN
})

// ─── Helpers ───
function formatFechaResumen(fecha) {
  if (!fecha) return 'Pendiente'
  const [year, month, day] = String(fecha).split('-')
  if (!year || !month || !day) return fecha
  return `${day}/${month}/${year}`
}

function getOperadorNombre(id) {
  if (!canSelectOperador.value) return authStore.userName
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

async function aplicarUnidadInicial() {
  if (isAdmin.value) return
  if (form.un_id) return

  if (store.unidadesNegocio.length === 1) {
    form.un_id = store.unidadesNegocio[0].idUnidadNegocio
    await onUnidadChange()
    return
  }

  const userUnits = Array.isArray(authStore.user?.unidad_ids) ? authStore.user.unidad_ids : []
  if (userUnits.length === 1 && store.unidadesNegocio.some((un) => un.idUnidadNegocio === userUnits[0])) {
    form.un_id = userUnits[0]
    await onUnidadChange()
  }
}

// ─── Watchers ───
async function aplicarPreferenciasGuardadas() {
  if (isAdmin.value) return
  if (form.un_id) return
  try {
    const prefs = JSON.parse(localStorage.getItem(preferenciasKey.value) || '{}')
    if (prefs.un_id && store.unidadesNegocio.some((un) => un.idUnidadNegocio === prefs.un_id)) {
      form.un_id = prefs.un_id
      await onUnidadChange()
      if (prefs.tipo_de_proceso_id && store.tiposProceso.some((tipo) => tipo.id === prefs.tipo_de_proceso_id)) {
        form.tipo_de_proceso_id = prefs.tipo_de_proceso_id
      }
      if (prefs.movil && store.moviles.some((movil) => movil.idMovil === prefs.movil.idMovil)) {
        seleccionarMovil(prefs.movil)
      }
    }
  } catch {
    localStorage.removeItem(preferenciasKey.value)
  }
}

function guardarPreferenciasProduccion() {
  const movil = (store.moviles || []).find((item) => item.idMovil === form.cod_equipo)
  localStorage.setItem(preferenciasKey.value, JSON.stringify({
    un_id: form.un_id || '',
    tipo_de_proceso_id: form.tipo_de_proceso_id || '',
    movil: movil ? { idMovil: movil.idMovil, patente: movil.patente, detalle: movil.detalle } : null,
  }))
}

function guardarBorrador() {
  guardarPreferenciasProduccion()
  localStorage.setItem(`${preferenciasKey.value}_borrador`, JSON.stringify({
    ...form,
    guardado_en: new Date().toISOString(),
  }))
  Swal.fire({
    icon: 'success',
    title: 'Borrador guardado',
    text: 'La carga quedo guardada en este dispositivo.',
    confirmButtonColor: '#3d935d',
    timer: 1400,
    showConfirmButton: false,
  })
}

function limpiarUbicacionSiNoAplica() {
  if (form.tipo_de_proceso_id && tipoProcesoSeleccionado.value) {
    cleanLocationValues(form, requisitosUbicacion.value)
  }
}

async function onOperadorChange() {
  if (!form.operador_id) return
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

  await autocompletarHoraInicio({ force: true })
}

async function onUnidadChange() {
  // Reset dependientes
  form.tipo_de_proceso_id = ''
  form.operador_id = canSelectOperador.value ? '' : form.operador_id
  limpiarMovilSeleccionado()
  store.movilAsignado = null
  if (!form.un_id) return
  // Cargar tipos de proceso y operadores de esta UN en paralelo
  await Promise.all([
    store.fetchTiposProceso(form.un_id),
    store.fetchMoviles(form.un_id),
    store.fetchLugaresCarga(form.un_id),
    canSelectOperador.value ? store.fetchOperadores(form.un_id) : Promise.resolve(),
  ])
  guardarPreferenciasProduccion()
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
  limpiarUbicacionSiNoAplica()

  autocompletarHoraInicio({ force: true })
  guardarPreferenciasProduccion()
}

async function onPredioChange() {
  form.rodal_id = ''
  form.rodal_manual = ''
  if (form.predio_id) {
    await store.fetchRodales(form.predio_id)
  }
}

// ─── Watch combustible toggle ───
watch(cargoCombustible, (val) => {
  if (!val) form.combustible = 0
})

watch(() => [form.tipo_de_proceso_id, tipoProcesoNombre.value], () => {
  limpiarUbicacionSiNoAplica()
})

// Removed old busquedaMovil watcher — selection/buscador now handled via mostrandoBuscador state

function formatearMovil(movil) {
  return `${movil.detalle} - ${movil.patente}`
}

function seleccionarMovil(movil) {
  form.equipo = formatearMovil(movil)
  form.cod_equipo = movil.idMovil || 0
  busquedaMovil.value = ''
  listaMovilesAbierta.value = false
  mostrandoBuscador.value = false

  autocompletarHoraInicio({ force: true })
  guardarPreferenciasProduccion()
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
  listaMovilesAbierta.value = false
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
  listaMovilesAbierta.value = false
}

function abrirListaMoviles() {
  if (!form.un_id) return
  listaMovilesAbierta.value = true
}

// iOS / mobile: mousedown.prevent no previene el blur con timing
// suficiente. Usamos relatedTarget del blur: si el focus va a un item
// del propio dropdown, NO cerramos. Patron equivalente al que usa
// AutocompleteField para el campo de operador.
function onInputBlur(event) {
  if (focusInside(event, '[data-moviles-dropdown]')) return
  listaMovilesAbierta.value = false
}

function limpiarBusquedaMovil() {
  busquedaMovil.value = ''
  abrirListaMoviles()
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

async function autocompletarHoraInicio({ force = false } = {}) {
  // Need at least a machine or an operator to query
  if (!form.cod_equipo && !form.operador_id) return

  const params = {
    // When machine is selected, omit cod_operador so the backend searches
    // across ALL operators for that machine (last hr_fin of the machine itself).
    ...(form.cod_equipo
      ? { cod_equipo: form.cod_equipo }
      : { cod_operador: form.operador_id }),
    cod_un: form.un_id || undefined,
    codigo_tabla: form.tipo_de_proceso_id || undefined,
  }

  const data = await store.fetchUltimaHoraFin(params)
  const ultimaHoraFin = Number(data?.hr_fin || 0)
  ultimaHoraFinRef.value = ultimaHoraFin

  if (ultimaHoraFin > 0 && (force || form.hr_inicio <= 0)) {
    form.hr_inicio = ultimaHoraFin
  }
}

// ─── Submit ───
async function handleSubmit() {
  // Guard: if Enter pressed on non-final step, advance instead
  if (pasoActual.value < totalPasos - 1) {
    avanzar()
    return
  }

  if (!puedeAvanzar.value) {
    return
  }

  try {
    if (requiereActa.value && (!actaNormalizada.value || actaNormalizada.value === '0')) {
      await Swal.fire({
        icon: 'warning',
        title: 'Acta obligatoria',
        text: 'Debés seleccionar un acta para poder guardar el registro.',
        confirmButtonColor: '#3d935d',
      })
      return
    }

    if (!horasValidas.value) {
      const inicio = Number(form.hr_inicio)
      const msg = (ultimaHoraFinRef.value > 0 && inicio > 0 && inicio < ultimaHoraFinRef.value)
        ? `La hora de inicio (${form.hr_inicio}) no puede ser menor al fin del registro anterior (${ultimaHoraFinRef.value}).`
        : 'La hora de inicio y fin deben ser mayores a 0, y la hora final no puede ser menor a la inicial.'
      await Swal.fire({
        icon: 'warning',
        title: 'Horas inválidas',
        text: msg,
        confirmButtonColor: '#3d935d',
      })
      return
    }

    if (!produccionValida.value) {
      await Swal.fire({
        icon: 'warning',
        title: 'Producción inválida',
        text: 'No se puede guardar con valores de producción en 0. Completá los campos requeridos con valores mayores a 0.',
        confirmButtonColor: '#3d935d',
      })
      return
    }

    if (ubicacionOperativaRequerida.value && !ubicacionValida.value) {
      await Swal.fire({
        icon: 'warning',
        title: 'Ubicación incompleta',
        text: mensajeUbicacionIncompleta.value,
        confirmButtonColor: '#3d935d',
      })
      return
    }

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
      aceite_hidraulico: form.aceite_hidraulico,
      aceite_motor: form.aceite_motor,
      aceite_transmision: form.aceite_transmision,
      aceite_embrague: form.aceite_embrague,
      acta: requiereActa.value ? form.acta : '',
      rodal: requiereRodal.value ? getRodalNombre() : '',
      predio: requierePredio.value ? getPredioNombre(form.predio_id) : '',
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
      espada: form.espada,
      puntera: form.puntera,
      cadena: form.cadena,
      pinon: form.pinon,
      cantidad_cadenas: form.cantidad_cadenas,
      pies_16: esProceso.value ? form.pies_16 : 0,
      pies_14: esProceso.value ? form.pies_14 : 0,
      pies_12: esProceso.value ? form.pies_12 : 0,
      pies_10: esProceso.value ? form.pies_10 : 0,
      pulpable: esProceso.value ? form.pulpable : 0,
      lugar_carga: form.lugar_carga_id || 0,
      unidad_produccion: resolveUnidadProduccion(),
      tabla: 'tipo_de_proceso',
      codigo_tabla: form.tipo_de_proceso_id || 0,
    }

    const result = await store.submitProduccion(payload)

    if (result?.offline) {
      await Swal.fire({
        icon: 'info',
        title: 'Guardado solo en este teléfono',
        text: 'El servidor todavía no confirmó este registro. Quedó en Pendientes y la aplicación seguirá intentando mientras esté abierta.',
        confirmButtonColor: '#3d935d',
        confirmButtonText: 'Entendido',
      })
    } else {
      await Swal.fire({
        icon: 'success',
        title: 'Registro guardado',
        text: 'El registro de producción se guardó correctamente.',
        confirmButtonColor: '#3d935d',
      })
    }

    router.push({ name: 'home' })
  } catch {
    // error handled by store
  }
}
</script>

