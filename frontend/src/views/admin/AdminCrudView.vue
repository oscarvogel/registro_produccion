<template>
  <div class="space-y-4">
    <SectionCard :title="meta.title">
      <div class="space-y-4">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p class="text-sm text-neutral-500">{{ meta.description }}</p>
            <p class="text-xs text-neutral-400 mt-1">
              Mostrando {{ filteredRows.length }} registro{{ filteredRows.length !== 1 ? 's' : '' }} de esta pagina.
            </p>
          </div>

          <div class="flex flex-col sm:flex-row gap-2 sm:items-center">
            <input
              v-model="searchText"
              type="search"
              class="w-full sm:w-64 px-4 py-2.5 bg-white border border-neutral-300 rounded-lg text-sm text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary/30"
              placeholder="Buscar"
            />

            <div
              v-if="showUnidadFilter"
              class="w-full sm:w-64"
            >
              <AutocompleteField
                v-model="unidadFilter"
                :items="referenceOptionsForEntity('unidades-negocio')"
                labelKey="_adminLabel"
                valueKey="idUnidadNegocio"
                placeholder="Todas las unidades"
              />
              <button
                v-if="unidadFilter"
                @click="unidadFilter = ''"
                class="mt-1 text-xs font-semibold text-neutral-400 underline underline-offset-2 hover:text-neutral-600"
                type="button"
              >
                Limpiar unidad
              </button>
            </div>

            <button
              @click="loadRows"
              class="inline-flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border border-neutral-300 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
              type="button"
            >
              <AppIcon name="refresh" size="sm" />
              Refrescar
            </button>

            <button
              v-if="entity !== 'asignaciones'"
              @click="openCreate"
              class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary-dark text-white text-sm font-semibold hover:bg-primary transition-colors"
              type="button"
            >
              <AppIcon name="add" size="sm" />
              Nuevo
            </button>
          </div>
        </div>

        <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
          {{ error }}
        </div>

        <div v-if="entity === 'asignaciones'" class="rounded-xl border border-neutral-200 bg-white p-4">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-end">
            <AutocompleteField
              v-model="quickAssignment.unidad_id"
              class="w-full lg:w-64"
              label="Unidad de Negocio"
              :items="referenceOptionsForEntity('unidades-negocio')"
              labelKey="_adminLabel"
              valueKey="idUnidadNegocio"
              placeholder="Buscar unidad"
            />

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 flex-1">
              <AutocompleteField
                v-model="quickAssignment.idChofer"
                label="Chofer"
                :items="assignmentOptions.personal"
                labelKey="_adminLabel"
                valueKey="idPersonal"
                :disabled="!quickAssignment.unidad_id"
                placeholder="Buscar chofer"
              />
              <AutocompleteField
                v-model="quickAssignment.idMovil"
                label="Movil"
                :items="assignmentOptions.moviles"
                labelKey="_adminLabel"
                valueKey="idMovil"
                :disabled="!quickAssignment.unidad_id"
                placeholder="Buscar movil"
              />
              <AutocompleteField
                v-model="quickAssignment.idProceso"
                label="Tipo de Proceso"
                :items="assignmentOptions.procesos"
                labelKey="_adminLabel"
                valueKey="id"
                :disabled="!quickAssignment.unidad_id"
                placeholder="Buscar proceso"
              />
            </div>

            <button
              @click="submitQuickAssignment"
              :disabled="submitting || !quickAssignmentReady"
              class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-primary-dark text-white text-sm font-semibold disabled:opacity-50"
              type="button"
            >
              <AppIcon name="assignment" size="sm" />
              Asignar
            </button>
          </div>
        </div>

        <div class="space-y-3 md:hidden">
          <div v-if="loading" class="rounded-xl border border-neutral-200 bg-white px-4 py-8 text-center text-sm text-neutral-500">
            Cargando...
          </div>

          <div v-else-if="filteredRows.length === 0" class="rounded-xl border border-neutral-200 bg-white px-4 py-8 text-center text-sm text-neutral-500">
            Sin registros para estos filtros.
          </div>

          <template v-else>
          <article
            v-for="row in filteredRows"
            :key="`mobile-${row[meta.idKey]}`"
            class="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm"
          >
            <div class="mb-3 flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wide text-neutral-400">{{ meta.singular }}</p>
                <p class="truncate text-base font-extrabold text-neutral-900">
                  {{ mobilePrimaryLabel(row) }}
                </p>
              </div>
              <span class="rounded-lg bg-neutral-100 px-2 py-1 text-xs font-bold text-neutral-500">
                #{{ row[meta.idKey] }}
              </span>
            </div>

            <dl class="space-y-2">
              <div
                v-for="column in mobileColumns"
                :key="`mobile-${row[meta.idKey]}-${column.key}`"
                class="grid grid-cols-[7.5rem_minmax(0,1fr)] gap-2 text-sm"
              >
                <dt class="text-xs font-semibold uppercase tracking-wide text-neutral-400">{{ column.label }}</dt>
                <dd class="min-w-0 text-right font-medium text-neutral-800">
                  <span
                    v-if="column.type === 'badge'"
                    :class="badgeClass(row[column.key], column)"
                  >
                    {{ badgeText(row[column.key], column) }}
                  </span>
                  <span v-else class="break-words">
                    {{ formatCellValue(row, column) }}
                  </span>
                </dd>
              </div>
            </dl>

            <div class="mt-4 grid grid-cols-2 gap-2">
              <button
                v-if="entity === 'unidades-negocio'"
                @click="toggleRelations(row[meta.idKey])"
                class="col-span-2 inline-flex items-center justify-center gap-2 rounded-lg border border-neutral-300 px-3 py-2 text-xs font-semibold text-neutral-700"
                type="button"
              >
                <AppIcon name="view" size="sm" />
                Relaciones
              </button>
              <button
                @click="openEdit(row)"
                class="inline-flex items-center justify-center gap-2 rounded-lg border border-neutral-300 px-3 py-2 text-xs font-semibold text-neutral-700"
                type="button"
              >
                <AppIcon name="edit" size="sm" />
                Editar
              </button>
              <button
                @click="removeRow(row[meta.idKey])"
                class="inline-flex items-center justify-center gap-2 rounded-lg border border-red-200 px-3 py-2 text-xs font-semibold text-red-700"
                type="button"
              >
                <AppIcon name="delete" size="sm" />
                {{ deleteLabel }}
              </button>
            </div>

            <div v-if="entity === 'unidades-negocio' && expandedUnidadId === row[meta.idKey]" class="mt-4 grid grid-cols-1 gap-3">
              <div
                v-for="block in unidadRelations(row[meta.idKey])"
                :key="`mobile-${row[meta.idKey]}-${block.title}`"
                class="rounded-lg border border-neutral-200 bg-neutral-50 p-3"
              >
                <div class="mb-2 flex items-center justify-between gap-3">
                  <p class="text-xs font-bold uppercase tracking-wide text-neutral-500">{{ block.title }}</p>
                  <span class="text-xs font-bold text-primary-dark">{{ block.items.length }}</span>
                </div>
                <div class="space-y-1">
                  <p
                    v-for="item in block.items.slice(0, 8)"
                    :key="item"
                    class="truncate text-sm text-neutral-700"
                  >
                    {{ item }}
                  </p>
                  <p v-if="block.items.length === 0" class="text-sm text-neutral-400">Sin vinculaciones.</p>
                  <p v-else-if="block.items.length > 8" class="text-xs text-neutral-400">
                    +{{ block.items.length - 8 }} mas
                  </p>
                </div>
              </div>
            </div>
          </article>
          </template>
        </div>

        <div class="hidden overflow-x-auto border border-neutral-200 rounded-xl bg-white md:block">
          <table class="min-w-full text-sm">
            <thead class="bg-neutral-50 text-neutral-600">
              <tr>
                <th
                  v-for="column in meta.columns"
                  :key="column.key"
                  class="text-left px-3 py-2.5 font-semibold border-b border-neutral-200 whitespace-nowrap"
                >
                  {{ column.label }}
                </th>
                <th class="text-right px-3 py-2.5 font-semibold border-b border-neutral-200 whitespace-nowrap">Acciones</th>
              </tr>
            </thead>

            <tbody>
              <tr v-if="loading">
                <td :colspan="meta.columns.length + 1" class="px-3 py-8 text-center text-neutral-500">Cargando...</td>
              </tr>

              <tr v-else-if="filteredRows.length === 0">
                <td :colspan="meta.columns.length + 1" class="px-3 py-8 text-center text-neutral-500">Sin registros para estos filtros.</td>
              </tr>

              <template v-for="row in filteredRows" :key="row[meta.idKey]">
                <tr class="hover:bg-neutral-50/70">
                  <td
                    v-for="column in meta.columns"
                    :key="`${row[meta.idKey]}-${column.key}`"
                    class="px-3 py-2.5 border-b border-neutral-100 align-middle"
                  >
                    <span
                      v-if="column.type === 'badge'"
                      :class="badgeClass(row[column.key], column)"
                    >
                      {{ badgeText(row[column.key], column) }}
                    </span>
                    <span v-else class="text-neutral-800">
                      {{ formatCellValue(row, column) }}
                    </span>
                  </td>

                  <td class="px-3 py-2.5 border-b border-neutral-100 whitespace-nowrap text-right">
                    <button
                      v-if="entity === 'unidades-negocio'"
                      @click="toggleRelations(row[meta.idKey])"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-neutral-300 text-neutral-700 hover:bg-neutral-100 mr-2"
                      type="button"
                    >
                      <AppIcon name="view" size="sm" />
                      Relaciones
                    </button>
                    <button
                      @click="openEdit(row)"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-neutral-300 text-neutral-700 hover:bg-neutral-100 mr-2"
                      type="button"
                    >
                      <AppIcon name="edit" size="sm" />
                      Editar
                    </button>
                    <button
                      @click="removeRow(row[meta.idKey])"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-red-200 text-red-700 hover:bg-red-50"
                      type="button"
                    >
                      <AppIcon name="delete" size="sm" />
                      {{ deleteLabel }}
                    </button>
                  </td>
                </tr>

                <tr v-if="entity === 'unidades-negocio' && expandedUnidadId === row[meta.idKey]">
                  <td :colspan="meta.columns.length + 1" class="px-3 py-3 border-b border-neutral-100 bg-neutral-50">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div
                        v-for="block in unidadRelations(row[meta.idKey])"
                        :key="block.title"
                        class="rounded-lg border border-neutral-200 bg-white p-3"
                      >
                        <div class="flex items-center justify-between gap-3 mb-2">
                          <p class="text-xs font-bold uppercase tracking-wide text-neutral-500">{{ block.title }}</p>
                          <span class="text-xs font-bold text-primary-dark">{{ block.items.length }}</span>
                        </div>
                        <div class="space-y-1 max-h-32 overflow-y-auto">
                          <p
                            v-for="item in block.items.slice(0, 12)"
                            :key="item"
                            class="text-sm text-neutral-700 truncate"
                          >
                            {{ item }}
                          </p>
                          <p v-if="block.items.length === 0" class="text-sm text-neutral-400">Sin vinculaciones.</p>
                          <p v-else-if="block.items.length > 12" class="text-xs text-neutral-400">
                            +{{ block.items.length - 12 }} mas
                          </p>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <label class="flex items-center gap-2 text-xs font-semibold text-neutral-500">
            Ver
            <select
              v-model.number="limit"
              @change="changePageSize"
              class="rounded-lg border border-neutral-200 bg-white px-2 py-1.5 text-xs font-bold text-neutral-700 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
            </select>
            por pagina
          </label>

          <div class="flex items-center justify-between gap-3 sm:justify-end">
          <button
            @click="prevPage"
            :disabled="page === 0 || loading"
            class="px-4 py-2 rounded-lg border border-neutral-300 text-sm font-semibold text-neutral-700 disabled:opacity-40"
            type="button"
          >
            Anterior
          </button>
          <span class="text-xs text-neutral-400">Pagina {{ page + 1 }}</span>
          <button
            @click="nextPage"
            :disabled="loading || rows.length < limit"
            class="px-4 py-2 rounded-lg border border-neutral-300 text-sm font-semibold text-neutral-700 disabled:opacity-40"
            type="button"
          >
            Siguiente
          </button>
          </div>
        </div>
      </div>
    </SectionCard>

    <div v-if="showForm" class="fixed inset-0 bg-black/35 z-50 flex items-center justify-center p-4" @click.self="closeForm">
      <div class="w-full max-w-4xl max-h-[90vh] overflow-hidden bg-white rounded-xl border border-neutral-200 shadow-xl flex flex-col">
        <div class="px-5 py-4 border-b border-neutral-200 flex items-center justify-between gap-4">
          <div>
            <h3 class="text-lg font-extrabold text-primary-dark">
              {{ editingId ? 'Editar' : 'Nuevo' }} {{ meta.singular }}
            </h3>
            <p class="text-xs text-neutral-400 mt-0.5">{{ meta.formHint }}</p>
          </div>
          <button @click="closeForm" class="text-neutral-500 hover:text-neutral-700" type="button">Cerrar</button>
        </div>

        <div v-if="formSections.length > 1" class="px-5 pt-4 flex flex-wrap gap-2">
          <button
            v-for="section in formSections"
            :key="section.key"
            @click="activeSection = section.key"
            :class="[
              'px-3 py-1.5 rounded-lg border text-xs font-bold transition-colors',
              activeSection === section.key
                ? 'bg-primary-dark border-primary-dark text-white'
                : 'bg-white border-neutral-200 text-neutral-600 hover:bg-neutral-50',
            ]"
            type="button"
          >
            {{ section.label }}
          </button>
        </div>

        <div class="p-5 overflow-y-auto">
          <div v-if="formError" class="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
            {{ formError }}
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <template v-for="field in visibleFields" :key="field.key">
              <div v-if="field.type === 'textarea'" :class="fieldClass(field)">
                <label class="block text-sm font-medium text-neutral-600 mb-1.5">{{ field.label }}</label>
                <textarea
                  v-model="form[field.key]"
                  rows="3"
                  class="w-full px-4 py-3 bg-neutral-100 border border-neutral-300 rounded-lg text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </div>

              <div v-else-if="field.type === 'autocomplete'" :class="fieldClass(field)">
                <AutocompleteField
                  v-model="form[field.key]"
                  :label="field.label"
                  :items="referenceOptions(field)"
                  labelKey="_adminLabel"
                  :valueKey="field.optionValue"
                  :placeholder="field.placeholder || 'Escribi para buscar'"
                />
              </div>

              <div v-else-if="field.type === 'select'" :class="fieldClass(field)">
                <AutocompleteField
                  v-model="form[field.key]"
                  :label="field.label"
                  :items="referenceOptions(field)"
                  labelKey="_adminLabel"
                  :valueKey="field.optionValue"
                  :placeholder="field.nullable ? 'Sin valor' : 'Escribi para buscar'"
                />
                <button
                  v-if="field.nullable && form[field.key]"
                  @click="form[field.key] = ''"
                  class="mt-1 text-xs font-semibold text-neutral-400 underline underline-offset-2 hover:text-neutral-600"
                  type="button"
                >
                  Limpiar
                </button>
              </div>

              <div v-else-if="field.type === 'multiselect'" class="md:col-span-2">
                <label class="block text-sm font-medium text-neutral-600 mb-1.5">{{ field.label }}</label>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
                  <label
                    v-for="option in referenceData[field.optionsEntity] || []"
                    :key="option[field.optionValue]"
                    class="flex items-center gap-2 text-sm text-neutral-700"
                  >
                    <input
                      type="checkbox"
                      class="w-4 h-4 accent-primary"
                      :checked="isMultiSelected(field.key, option[field.optionValue])"
                      @change="toggleMultiValue(field.key, option[field.optionValue], $event.target.checked)"
                    />
                    <span>{{ formatOptionLabel(option, field) }}</span>
                  </label>
                </div>
              </div>

              <div v-else-if="field.type === 'checkbox'" class="flex items-center gap-3 py-3">
                <input :id="field.key" v-model="form[field.key]" type="checkbox" class="w-4 h-4 accent-primary" />
                <label :for="field.key" class="text-sm font-medium text-neutral-700">{{ field.label }}</label>
              </div>

              <InputField
                v-else
                v-model="form[field.key]"
                :label="field.label"
                :type="field.type"
                :required="Boolean(field.required)"
              />
            </template>
          </div>
        </div>

        <div class="px-5 py-4 border-t border-neutral-200 flex items-center justify-end gap-2">
          <button
            @click="closeForm"
            class="px-4 py-2 rounded-lg border border-neutral-300 text-sm font-semibold text-neutral-700"
            type="button"
          >
            Cancelar
          </button>
          <button
            @click="submitForm"
            :disabled="submitting"
            class="px-4 py-2 rounded-lg bg-primary-dark text-white text-sm font-semibold disabled:opacity-60"
            type="button"
          >
            {{ submitting ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <AppModal
      v-model="showDeleteConfirm"
      title="Confirmar accion"
      :description="`Vas a ${deleteLabel.toLowerCase()} este registro. Esta accion puede afectar datos vinculados.`"
    >
      <div class="flex flex-col gap-4">
        <p class="text-sm text-neutral-700">
          Confirma que queres continuar con <strong>{{ pendingDeleteLabel }}</strong>.
        </p>
        <div class="flex justify-end gap-2">
          <AppButton variant="secondary" @click="cancelDelete">Cancelar</AppButton>
          <AppButton variant="danger" :loading="submitting" @click="confirmDelete">{{ deleteLabel }}</AppButton>
        </div>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AutocompleteField from '@/components/AutocompleteField.vue'
import InputField from '@/components/InputField.vue'
import SectionCard from '@/components/SectionCard.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import { useAdminStore } from '@/stores/admin'

const SECTIONS = {
  principal: 'Principal',
  relaciones: 'Relaciones',
  acceso: 'Acceso',
  horarios: 'Horarios',
  tecnico: 'Tecnico',
  documentacion: 'Documentacion',
  observaciones: 'Observaciones',
}

const ENTITY_DEFINITIONS = {
  personal: {
    title: 'Personal',
    singular: 'persona',
    description: 'Gestiona datos basicos, permisos y unidades vinculadas del personal.',
    formHint: 'Los datos operativos y de acceso estan separados para editar con menos ruido.',
    idKey: 'idPersonal',
    deleteVerb: 'Desactivar',
    extraReferences: ['unidades-negocio', 'tipos-proceso'],
    columns: [
      { key: 'idPersonal', label: 'ID' },
      { key: 'nombre', label: 'Nombre' },
      { key: 'dni', label: 'DNI' },
      { key: 'unidad_ids', label: 'Unidades', type: 'multiLookup', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre' },
      { key: 'encargado', label: 'Encargado', type: 'badge', trueText: 'Si', falseText: 'No' },
      { key: 'is_admin', label: 'Admin', type: 'badge', trueText: 'Si', falseText: 'No' },
      { key: 'activo', label: 'Estado', type: 'badge', trueText: 'Activo', falseText: 'Inactivo' },
    ],
    fields: [
      { key: 'nombre', label: 'Nombre', type: 'text', required: true, section: 'principal' },
      { key: 'dni', label: 'DNI', type: 'text', section: 'principal' },
      { key: 'cuit', label: 'CUIT', type: 'text', section: 'principal' },
      { key: 'id_puesto', label: 'ID Puesto', type: 'number', default: 1, section: 'principal' },
      { key: 'telefono', label: 'Telefono', type: 'text', section: 'principal' },
      { key: 'domicilio', label: 'Domicilio', type: 'text', section: 'principal' },
      { key: 'fecha_nacimiento', label: 'Fecha Nacimiento', type: 'date', nullable: true, section: 'principal' },
      { key: 'fecha_ingreso', label: 'Fecha Ingreso', type: 'date', nullable: true, section: 'principal' },
      { key: 'unidad_negocio', label: 'Unidad Principal', type: 'autocomplete', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre', default: 1, section: 'relaciones' },
      { key: 'unidad_ids', label: 'Unidades vinculadas', type: 'multiselect', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre', default: [1], section: 'relaciones' },
      { key: 'tipo_de_proceso_id', label: 'Tipo de Proceso', type: 'autocomplete', optionsEntity: 'tipos-proceso', optionValue: 'id', optionLabel: 'nombre', nullable: true, section: 'relaciones' },
      { key: 'entrada_m', label: 'Entrada Manana', type: 'text', default: '00:00', section: 'horarios' },
      { key: 'salida_m', label: 'Salida Manana', type: 'text', default: '00:00', section: 'horarios' },
      { key: 'entrada_t', label: 'Entrada Tarde', type: 'text', default: '00:00', section: 'horarios' },
      { key: 'salida_t', label: 'Salida Tarde', type: 'text', default: '00:00', section: 'horarios' },
      { key: 'activo', label: 'Activo', type: 'checkbox', output: 'int', default: true, section: 'acceso' },
      { key: 'encargado', label: 'Encargado', type: 'checkbox', output: 'int', default: false, section: 'acceso' },
      { key: 'is_admin', label: 'Acceso Admin', type: 'checkbox', output: 'int', default: false, section: 'acceso' },
      { key: 'password', label: 'Password', type: 'password', nullable: true, section: 'acceso' },
    ],
  },
  moviles: {
    title: 'Moviles',
    singular: 'movil',
    description: 'Administra unidades operativas, documentacion y datos tecnicos.',
    formHint: 'Los datos tecnicos quedan agrupados para evitar formularios interminables.',
    idKey: 'idMovil',
    deleteVerb: 'Desactivar',
    extraReferences: ['unidades-negocio'],
    columns: [
      { key: 'idMovil', label: 'ID' },
      { key: 'patente', label: 'Patente' },
      { key: 'detalle', label: 'Detalle' },
      { key: 'id_unidad_negocio', label: 'Unidad', type: 'lookup', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre' },
      { key: 'activo', label: 'Estado', type: 'badge', trueText: 'Activo', falseText: 'Inactivo' },
    ],
    fields: [
      { key: 'patente', label: 'Patente', type: 'text', required: true, section: 'principal' },
      { key: 'detalle', label: 'Detalle', type: 'text', required: true, section: 'principal' },
      { key: 'id_unidad_negocio', label: 'Unidad de Negocio', type: 'autocomplete', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre', default: 1, section: 'principal' },
      { key: 'activo', label: 'Activo', type: 'checkbox', output: 'int', default: true, section: 'principal' },
      { key: 'tipo_proceso', label: 'Tipo Proceso', type: 'text', default: '1', section: 'tecnico' },
      { key: 'tipo_movil', label: 'Tipo Movil', type: 'number', default: 1, section: 'tecnico' },
      { key: 'cant_neumaticos', label: 'Cantidad Neumaticos', type: 'number', default: 0, section: 'tecnico' },
      { key: 'capacidad_tanque', label: 'Capacidad Tanque', type: 'number', default: 0, section: 'tecnico' },
      { key: 'consumo_promedio', label: 'Consumo Promedio', type: 'number', default: 0, section: 'tecnico' },
      { key: 'anio_fabricacion', label: 'Año Fabricacion', type: 'number', default: 0, section: 'documentacion' },
      { key: 'nro_chasis', label: 'Numero Chasis', type: 'text', section: 'documentacion' },
      { key: 'nro_motor', label: 'Numero Motor', type: 'text', section: 'documentacion' },
      { key: 'venc_tecnica', label: 'Vencimiento Tecnica', type: 'date', nullable: true, section: 'documentacion' },
      { key: 'ruta', label: 'Ruta habilitada', type: 'checkbox', output: 'bool', default: false, section: 'documentacion' },
      { key: 'venc_ruta', label: 'Vencimiento Ruta', type: 'date', nullable: true, section: 'documentacion' },
      { key: 'observaciones', label: 'Observaciones', type: 'textarea', nullable: true, section: 'observaciones', span: 2 },
    ],
  },
  'unidades-negocio': {
    title: 'Unidades de Negocio',
    singular: 'unidad de negocio',
    description: 'Mantiene unidades y permite revisar sus vinculaciones operativas.',
    formHint: 'Usa Relaciones en la tabla para ver personal, moviles y procesos asociados.',
    idKey: 'idUnidadNegocio',
    deleteVerb: 'Desactivar',
    extraReferences: ['personal', 'moviles', 'tipos-proceso'],
    columns: [
      { key: 'idUnidadNegocio', label: 'ID' },
      { key: 'nombre', label: 'Nombre' },
      { key: 'prefijo', label: 'Prefijo' },
      { key: 'activo', label: 'Estado', type: 'badge', trueText: 'Activo', falseText: 'Inactivo' },
    ],
    fields: [
      { key: 'nombre', label: 'Nombre', type: 'text', required: true, section: 'principal' },
      { key: 'prefijo', label: 'Prefijo', type: 'text', section: 'principal' },
      { key: 'codigo_kobo', label: 'Codigo Kobo', type: 'text', section: 'principal' },
      { key: 'activo', label: 'Activo', type: 'checkbox', output: 'int', default: true, section: 'principal' },
    ],
  },
  'tipos-proceso': {
    title: 'Tipos de Proceso',
    singular: 'tipo de proceso',
    description: 'Define procesos disponibles y las unidades donde se pueden usar.',
    formHint: 'Habilita procesos por unidad para controlar la carga de produccion.',
    idKey: 'id',
    deleteVerb: 'Desactivar',
    extraReferences: ['unidades-negocio'],
    columns: [
      { key: 'id', label: 'ID' },
      { key: 'nombre', label: 'Nombre' },
      { key: 'unidad_ids', label: 'Unidades', type: 'multiLookup', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre' },
      { key: 'campos', label: 'Campos' },
      { key: 'activo', label: 'Estado', type: 'badge', trueText: 'Activo', falseText: 'Inactivo' },
    ],
    fields: [
      { key: 'nombre', label: 'Nombre', type: 'text', required: true, section: 'principal' },
      { key: 'campos', label: 'Campos', type: 'text', section: 'principal', span: 2 },
      { key: 'unidad_ids', label: 'Unidades habilitadas', type: 'multiselect', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre', default: [], section: 'relaciones' },
      { key: 'activo', label: 'Activo', type: 'checkbox', output: 'int', default: true, section: 'principal' },
    ],
  },
  'lugares-carga': {
    title: 'Lugares de Carga',
    singular: 'lugar de carga',
    description: 'Administra lugares de carga por unidad de negocio.',
    formHint: 'Cada lugar queda disponible solo para su unidad.',
    idKey: 'idLugarCarga',
    deleteVerb: 'Desactivar',
    extraReferences: ['unidades-negocio'],
    columns: [
      { key: 'idLugarCarga', label: 'ID' },
      { key: 'detalle', label: 'Detalle' },
      { key: 'unidad_negocio', label: 'Unidad', type: 'lookup', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre' },
      { key: 'activo', label: 'Estado', type: 'badge', trueText: 'Activo', falseText: 'Inactivo' },
    ],
    fields: [
      { key: 'detalle', label: 'Detalle', type: 'text', required: true, section: 'principal' },
      { key: 'unidad_negocio', label: 'Unidad de Negocio', type: 'autocomplete', optionsEntity: 'unidades-negocio', optionValue: 'idUnidadNegocio', optionLabel: 'nombre', default: 1, section: 'principal' },
      { key: 'activo', label: 'Activo', type: 'checkbox', output: 'int', default: true, section: 'principal' },
    ],
  },
  predios: {
    title: 'Predios',
    singular: 'predio',
    description: 'Catalogo simple de predios.',
    formHint: 'Campos minimos para identificar el predio.',
    idKey: 'idPredio',
    deleteVerb: 'Eliminar',
    columns: [
      { key: 'idPredio', label: 'ID' },
      { key: 'nombre', label: 'Nombre' },
      { key: 'empresa', label: 'Empresa' },
    ],
    fields: [
      { key: 'idPredio', label: 'ID (opcional)', type: 'number', nullable: true, section: 'principal' },
      { key: 'nombre', label: 'Nombre', type: 'text', required: true, section: 'principal' },
      { key: 'empresa', label: 'Empresa', type: 'text', required: true, section: 'principal' },
      { key: 'codigo_kobo', label: 'Codigo Kobo', type: 'text', nullable: true, section: 'principal' },
    ],
  },
  rodales: {
    title: 'Rodales',
    singular: 'rodal',
    description: 'Catalogo de rodales con valores operativos.',
    formHint: 'El predio se busca por autocompletado.',
    idKey: 'idRodal',
    deleteVerb: 'Eliminar',
    extraReferences: ['predios'],
    columns: [
      { key: 'idRodal', label: 'ID' },
      { key: 'rodal', label: 'Rodal' },
      { key: 'idPredio', label: 'Predio', type: 'lookup', optionsEntity: 'predios', optionValue: 'idPredio', optionLabel: 'nombre' },
      { key: 'vam', label: 'VAM' },
    ],
    fields: [
      { key: 'rodal', label: 'Rodal', type: 'text', required: true, section: 'principal' },
      { key: 'idPredio', label: 'Predio', type: 'autocomplete', optionsEntity: 'predios', optionValue: 'idPredio', optionLabel: 'nombre', section: 'principal' },
      { key: 'vam', label: 'VAM', type: 'number', default: 0, section: 'tecnico' },
      { key: 'tarifa', label: 'Tarifa', type: 'number', default: 0, section: 'tecnico' },
      { key: 'extraccion', label: 'Extraccion', type: 'number', default: 0, section: 'tecnico' },
      { key: 'carga', label: 'Carga', type: 'number', default: 0, section: 'tecnico' },
    ],
  },
  asignaciones: {
    title: 'Asignaciones Operativas',
    singular: 'asignacion operativa',
    description: 'Asigna choferes, moviles y procesos con filtros por unidad.',
    formHint: 'El flujo principal esta en el panel superior; el modal queda para editar.',
    idKey: 'idAsignacion',
    deleteVerb: 'Eliminar',
    extraReferences: ['unidades-negocio', 'moviles', 'personal', 'tipos-proceso'],
    columns: [
      { key: 'idAsignacion', label: 'ID' },
      { key: 'idMovil', label: 'Movil', type: 'lookup', optionsEntity: 'moviles', optionValue: 'idMovil', optionLabel: 'detalle' },
      { key: 'idChofer', label: 'Chofer', type: 'lookup', optionsEntity: 'personal', optionValue: 'idPersonal', optionLabel: 'nombre' },
      { key: 'idProceso', label: 'Proceso', type: 'lookup', optionsEntity: 'tipos-proceso', optionValue: 'id', optionLabel: 'nombre' },
    ],
    fields: [
      { key: 'idMovil', label: 'Movil', type: 'autocomplete', optionsEntity: 'moviles', optionValue: 'idMovil', optionLabel: 'detalle', section: 'principal' },
      { key: 'idChofer', label: 'Chofer', type: 'autocomplete', optionsEntity: 'personal', optionValue: 'idPersonal', optionLabel: 'nombre', section: 'principal' },
      { key: 'idProceso', label: 'Tipo de Proceso', type: 'autocomplete', optionsEntity: 'tipos-proceso', optionValue: 'id', optionLabel: 'nombre', section: 'principal' },
    ],
  },
}

const route = useRoute()
const router = useRouter()
const adminStore = useAdminStore()

const rows = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)
const formError = ref(null)
const searchText = ref('')
const unidadFilter = ref('')
const expandedUnidadId = ref(null)
const activeSection = ref('principal')
const showDeleteConfirm = ref(false)
const pendingDeleteId = ref(null)
const pendingDeleteLabel = ref('')

const showForm = ref(false)
const editingId = ref(null)
const form = reactive({})
const referenceData = reactive({})
const quickAssignment = reactive({
  unidad_id: '',
  idChofer: '',
  idMovil: '',
  idProceso: '',
})

const page = ref(0)
const limit = ref(5)
const pageSizeOptions = [5, 10, 25, 50]
const referenceCache = new Map()

const entity = computed(() => String(route.params.entity || ''))
const meta = computed(() => ENTITY_DEFINITIONS[entity.value] || null)
const deleteLabel = computed(() => meta.value?.deleteVerb || 'Eliminar')

const formSections = computed(() => {
  const fields = meta.value?.fields || []
  const keys = [...new Set(fields.map((field) => field.section || 'principal'))]
  return keys.map((key) => ({ key, label: SECTIONS[key] || key }))
})

const visibleFields = computed(() => {
  return (meta.value?.fields || []).filter((field) => (field.section || 'principal') === activeSection.value)
})

const showUnidadFilter = computed(() => {
  return ['personal', 'moviles', 'tipos-proceso', 'lugares-carga', 'asignaciones'].includes(entity.value)
})

const filteredRows = computed(() => {
  const query = searchText.value.trim().toLowerCase()
  const selectedUnidad = Number(unidadFilter.value || 0)

  return rows.value.filter((row) => {
    if (selectedUnidad && !rowUnidadIds(row).includes(selectedUnidad)) return false
    if (!query) return true
    return searchableText(row).includes(query)
  })
})

const mobileColumns = computed(() => {
  const columns = meta.value?.columns || []
  return columns.filter((column) => column.key !== meta.value?.idKey).slice(0, 5)
})

const quickAssignmentReady = computed(() => {
  return quickAssignment.unidad_id && quickAssignment.idChofer && quickAssignment.idMovil && quickAssignment.idProceso
})

const assignmentOptions = computed(() => {
  const unidadId = Number(quickAssignment.unidad_id || 0)
  return {
    personal: referenceOptionsForEntity('personal', { unidadId }),
    moviles: referenceOptionsForEntity('moviles', { unidadId }),
    procesos: referenceOptionsForEntity('tipos-proceso', { unidadId }),
  }
})

watch(
  entity,
  async () => {
    if (!meta.value) {
      router.replace({ name: 'admin-dashboard' })
      return
    }
    page.value = 0
    searchText.value = ''
    unidadFilter.value = ''
    expandedUnidadId.value = null
    resetQuickAssignment()
    resetForm()
    await loadReferences()
    await loadRows()
  },
  { immediate: true }
)

watch(
  () => quickAssignment.unidad_id,
  () => {
    quickAssignment.idChofer = ''
    quickAssignment.idMovil = ''
    quickAssignment.idProceso = ''
  }
)

function resetForm() {
  Object.keys(form).forEach((key) => delete form[key])
  if (!meta.value) return

  for (const field of meta.value.fields) {
    if (field.type === 'checkbox') {
      form[field.key] = Boolean(field.default ?? false)
    } else if (field.type === 'multiselect') {
      form[field.key] = Array.isArray(field.default) ? [...field.default] : []
    } else if (field.default !== undefined) {
      form[field.key] = field.default
    } else {
      form[field.key] = ''
    }
  }
  activeSection.value = formSections.value[0]?.key || 'principal'
  formError.value = null
}

function resetQuickAssignment() {
  quickAssignment.unidad_id = ''
  quickAssignment.idChofer = ''
  quickAssignment.idMovil = ''
  quickAssignment.idProceso = ''
}

async function loadReferences() {
  if (!meta.value) return
  const fromFields = meta.value.fields.filter((field) => field.optionsEntity).map((field) => field.optionsEntity)
  const needed = [...new Set([...(meta.value.extraReferences || []), ...fromFields])]

  await Promise.all(needed.map(async (refEntity) => {
    if (referenceCache.has(refEntity)) {
      referenceData[refEntity] = referenceCache.get(refEntity)
      return
    }

    try {
      const data = await adminStore.fetchEntity(refEntity, { skip: 0, limit: 1000 })
      referenceCache.set(refEntity, data)
      referenceData[refEntity] = data
    } catch {
      referenceData[refEntity] = []
    }
  }))
}

async function loadRows() {
  if (!meta.value) return
  loading.value = true
  error.value = null
  try {
    rows.value = await adminStore.fetchEntity(entity.value, { skip: page.value * limit.value, limit: limit.value })
  } catch (err) {
    rows.value = []
    error.value = err.response?.data?.detail || `No se pudo cargar ${meta.value.title.toLowerCase()}`
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  resetForm()
  showForm.value = true
}

function openEdit(row) {
  if (!meta.value) return
  editingId.value = row[meta.value.idKey]
  resetForm()
  for (const field of meta.value.fields) {
    const value = row[field.key]
    if (field.type === 'checkbox') {
      form[field.key] = Boolean(value)
    } else if (field.type === 'multiselect') {
      form[field.key] = Array.isArray(value) ? value.map(Number) : []
    } else if (value === null || value === undefined) {
      form[field.key] = ''
    } else {
      form[field.key] = value
    }
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  submitting.value = false
  formError.value = null
}

function normalizePayload() {
  const payload = {}
  for (const field of meta.value.fields) {
    let value = form[field.key]

    if (field.key === 'password' && editingId.value && !value) continue

    if (field.type === 'checkbox') {
      payload[field.key] = field.output === 'bool' ? Boolean(value) : (value ? 1 : 0)
      continue
    }

    if (field.type === 'multiselect') {
      payload[field.key] = Array.isArray(value) ? value.map(Number).filter(Boolean) : []
      continue
    }

    if (field.type === 'number') {
      payload[field.key] = value === '' || value === null || value === undefined ? (field.nullable ? null : 0) : Number(value)
      continue
    }

    if (field.type === 'select' || field.type === 'autocomplete') {
      payload[field.key] = value === '' || value === null || value === undefined ? (field.nullable ? null : 0) : Number(value)
      continue
    }

    if (field.type === 'date') {
      payload[field.key] = value || null
      continue
    }

    payload[field.key] = value ?? ''
  }
  return payload
}

function validatePayload(payload) {
  if (entity.value === 'personal' && !payload.nombre?.trim()) return 'Nombre es obligatorio.'
  if (entity.value === 'personal' && (!payload.unidad_ids || payload.unidad_ids.length === 0)) return 'Selecciona al menos una unidad vinculada.'
  if (entity.value === 'moviles' && (!payload.patente?.trim() || !payload.detalle?.trim())) return 'Patente y detalle son obligatorios.'
  if (entity.value === 'tipos-proceso' && !payload.nombre?.trim()) return 'Nombre es obligatorio.'
  if (entity.value === 'asignaciones') return validateAssignment(payload)
  return ''
}

function validateAssignment(payload) {
  if (!payload.idMovil || !payload.idChofer || !payload.idProceso) {
    return 'Completa movil, chofer y tipo de proceso.'
  }

  const movil = findReference('moviles', payload.idMovil, 'idMovil')
  const chofer = findReference('personal', payload.idChofer, 'idPersonal')
  const proceso = findReference('tipos-proceso', payload.idProceso, 'id')
  if (!movil || !chofer || !proceso) return 'La asignacion contiene datos no disponibles.'

  const unidadMovil = Number(movil.id_unidad_negocio || 0)
  if (unidadMovil && Array.isArray(chofer.unidad_ids) && !chofer.unidad_ids.map(Number).includes(unidadMovil)) {
    return 'El chofer no pertenece a la unidad del movil.'
  }
  if (unidadMovil && Array.isArray(proceso.unidad_ids) && proceso.unidad_ids.length > 0 && !proceso.unidad_ids.map(Number).includes(unidadMovil)) {
    return 'El tipo de proceso no esta habilitado para la unidad del movil.'
  }

  const duplicate = rows.value.find((row) => {
    const sameValues = Number(row.idMovil) === payload.idMovil
      && Number(row.idChofer) === payload.idChofer
      && Number(row.idProceso) === payload.idProceso
    return sameValues && (!editingId.value || Number(row.idAsignacion) !== Number(editingId.value))
  })
  if (duplicate) return 'Esta asignacion ya existe.'

  return ''
}

async function submitForm() {
  if (!meta.value) return
  submitting.value = true
  formError.value = null
  error.value = null

  try {
    const payload = normalizePayload()
    const validation = validatePayload(payload)
    if (validation) {
      formError.value = validation
      return
    }

    if (editingId.value) {
      await adminStore.updateEntity(entity.value, editingId.value, payload)
    } else {
      await adminStore.createEntity(entity.value, payload)
    }
    clearReferenceCacheFor(entity.value)
    await Promise.all([loadRows(), loadReferences()])
    closeForm()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'No se pudo guardar el registro'
  } finally {
    submitting.value = false
  }
}

async function submitQuickAssignment() {
  formError.value = null
  error.value = null
  const payload = {
    idChofer: Number(quickAssignment.idChofer),
    idMovil: Number(quickAssignment.idMovil),
    idProceso: Number(quickAssignment.idProceso),
  }

  const validation = validateAssignment(payload)
  if (validation) {
    error.value = validation
    return
  }

  submitting.value = true
  try {
    await adminStore.createEntity('asignaciones', payload)
    clearReferenceCacheFor('asignaciones')
    resetQuickAssignment()
    await loadRows()
  } catch (err) {
    error.value = err.response?.data?.detail || 'No se pudo crear la asignacion'
  } finally {
    submitting.value = false
  }
}

async function removeRow(id) {
  pendingDeleteId.value = id
  pendingDeleteLabel.value = `${deleteLabel.value.toLowerCase()} registro #${id}`
  showDeleteConfirm.value = true
}

function cancelDelete() {
  showDeleteConfirm.value = false
  pendingDeleteId.value = null
  pendingDeleteLabel.value = ''
}

async function confirmDelete() {
  if (!pendingDeleteId.value) return
  const id = pendingDeleteId.value
  const verb = deleteLabel.value.toLowerCase()
  error.value = null
  submitting.value = true
  try {
    await adminStore.deleteEntity(entity.value, id)
    clearReferenceCacheFor(entity.value)
    await loadRows()
  } catch (err) {
    error.value = err.response?.data?.detail || `No se pudo ${verb} el registro`
  } finally {
    submitting.value = false
    cancelDelete()
  }
}

function clearReferenceCacheFor(changedEntity) {
  referenceCache.delete(changedEntity)
  for (const key of ['personal', 'moviles', 'tipos-proceso', 'unidades-negocio', 'predios']) {
    if (changedEntity === key) referenceCache.delete(key)
  }
}

function prevPage() {
  if (page.value === 0) return
  page.value -= 1
  loadRows()
}

function nextPage() {
  if (rows.value.length < limit.value) return
  page.value += 1
  loadRows()
}

function changePageSize() {
  page.value = 0
  loadRows()
}

function toggleRelations(id) {
  expandedUnidadId.value = expandedUnidadId.value === id ? null : id
}

function unidadRelations(unidadId) {
  const id = Number(unidadId)
  const personal = (referenceData.personal || [])
    .filter((item) => Array.isArray(item.unidad_ids) && item.unidad_ids.map(Number).includes(id))
    .map((item) => item.nombre)
  const moviles = (referenceData.moviles || [])
    .filter((item) => Number(item.id_unidad_negocio) === id)
    .map((item) => formatOptionLabel(item, { optionsEntity: 'moviles', optionLabel: 'detalle' }))
  const procesos = (referenceData['tipos-proceso'] || [])
    .filter((item) => Array.isArray(item.unidad_ids) && item.unidad_ids.map(Number).includes(id))
    .map((item) => item.nombre)

  return [
    { title: 'Personal', items: personal },
    { title: 'Moviles', items: moviles },
    { title: 'Procesos', items: procesos },
  ]
}

function fieldClass(field) {
  return field.span === 2 ? 'md:col-span-2' : ''
}

function isMultiSelected(key, value) {
  return Array.isArray(form[key]) && form[key].map(Number).includes(Number(value))
}

function toggleMultiValue(key, value, checked) {
  if (!Array.isArray(form[key])) form[key] = []
  const parsed = Number(value)
  if (checked && !form[key].map(Number).includes(parsed)) form[key].push(parsed)
  if (!checked) form[key] = form[key].filter((item) => Number(item) !== parsed)

  if (key === 'unidad_ids' && entity.value === 'personal') {
    form.unidad_negocio = form[key][0] || form.unidad_negocio || 1
  }
}

function findReference(refEntity, value, key) {
  return (referenceData[refEntity] || []).find((item) => Number(item[key]) === Number(value))
}

function lookupLabel(value, column) {
  const option = findReference(column.optionsEntity, value, column.optionValue)
  return option ? formatOptionLabel(option, column) : value
}

function rowUnidadIds(row) {
  if (entity.value === 'personal') return Array.isArray(row.unidad_ids) ? row.unidad_ids.map(Number) : [Number(row.unidad_negocio || 0)]
  if (entity.value === 'moviles') return [Number(row.id_unidad_negocio || 0)]
  if (entity.value === 'tipos-proceso') return Array.isArray(row.unidad_ids) ? row.unidad_ids.map(Number) : []
  if (entity.value === 'lugares-carga') return [Number(row.unidad_negocio || 0)]
  if (entity.value === 'asignaciones') {
    const movil = findReference('moviles', row.idMovil, 'idMovil')
    return movil ? [Number(movil.id_unidad_negocio || 0)] : []
  }
  return []
}

function searchableText(row) {
  const values = meta.value.columns.map((column) => String(formatCellValue(row, column) ?? ''))
  return values.join(' ').toLowerCase()
}

function formatOptionLabel(option, field) {
  if (!option) return ''
  if (field.optionsEntity === 'moviles') return [option.patente, option.detalle].filter(Boolean).join(' - ')
  if (field.optionsEntity === 'personal') return [option.nombre, option.dni ? `DNI ${option.dni}` : ''].filter(Boolean).join(' - ')
  return option[field.optionLabel] ?? option.nombre ?? option.detalle ?? option.id
}

function referenceOptions(field) {
  return referenceOptionsForEntity(field.optionsEntity).map((option) => ({
    ...option,
    _adminLabel: formatOptionLabel(option, field),
  }))
}

function referenceOptionsForEntity(refEntity, { unidadId = 0 } = {}) {
  return (referenceData[refEntity] || [])
    .filter((option) => {
      if (!unidadId) return true
      if (refEntity === 'personal') return Array.isArray(option.unidad_ids) && option.unidad_ids.map(Number).includes(Number(unidadId))
      if (refEntity === 'moviles') return Number(option.id_unidad_negocio) === Number(unidadId)
      if (refEntity === 'tipos-proceso') return Array.isArray(option.unidad_ids) && option.unidad_ids.map(Number).includes(Number(unidadId))
      return true
    })
    .map((option) => ({
      ...option,
      _adminLabel: formatOptionLabel(option, optionFieldForEntity(refEntity)),
    }))
}

function optionFieldForEntity(refEntity) {
  const map = {
    personal: { optionsEntity: 'personal', optionLabel: 'nombre' },
    moviles: { optionsEntity: 'moviles', optionLabel: 'detalle' },
    'tipos-proceso': { optionsEntity: 'tipos-proceso', optionLabel: 'nombre' },
    'unidades-negocio': { optionsEntity: 'unidades-negocio', optionLabel: 'nombre' },
    predios: { optionsEntity: 'predios', optionLabel: 'nombre' },
  }
  return map[refEntity] || { optionsEntity: refEntity, optionLabel: 'nombre' }
}

function formatCellValue(row, column) {
  const value = row[column.key]
  if (column.type === 'lookup') return lookupLabel(value, column)
  if (column.type === 'multiLookup') {
    if (!Array.isArray(value) || value.length === 0) return '-'
    return value.map((item) => lookupLabel(item, column)).join(', ')
  }
  if (value === null || value === undefined || value === '') return '-'
  if (Array.isArray(value)) return value.length ? value.join(', ') : '-'
  if (value === 1 || value === 0) return value === 1 ? 'Si' : 'No'
  return value
}

function mobilePrimaryLabel(row) {
  const preferred = ['nombre', 'detalle', 'patente', 'rodal', 'descripcion']
  const key = preferred.find((item) => row[item])
  if (key) return row[key]
  const firstColumn = mobileColumns.value[0]
  return firstColumn ? formatCellValue(row, firstColumn) : row[meta.value.idKey]
}

function badgeText(value, column) {
  return Number(value) === 1 || value === true ? (column.trueText || 'Si') : (column.falseText || 'No')
}

function badgeClass(value, column) {
  const active = Number(value) === 1 || value === true
  const base = 'inline-flex items-center px-2 py-1 rounded-md text-xs font-bold border'
  if (column.key === 'activo') {
    return active
      ? `${base} bg-emerald-50 text-emerald-700 border-emerald-200`
      : `${base} bg-neutral-100 text-neutral-500 border-neutral-200`
  }
  return active
    ? `${base} bg-primary/10 text-primary-dark border-primary/20`
    : `${base} bg-neutral-100 text-neutral-500 border-neutral-200`
}
</script>
