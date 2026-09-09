<template>
  <div class="space-y-3">
    <SectionCard title="Configuración de Acceso">
      <FeedbackMessage v-if="saveError" tone="error" :message="saveError" class="mb-3" />
      <div class="mb-3 rounded-lg border border-warning/30 bg-warning-light/30 px-3.5 py-2.5 text-sm font-semibold text-warning-dark">
        Desde aquí se puede habilitar o deshabilitar acceso admin a otros usuarios. No podés quitarte tu propio acceso.
      </div>

      <div class="flex flex-col gap-2 sm:flex-row sm:items-end">
        <AutocompleteField
          v-model="selectedUserId"
          class="w-full sm:w-96"
          label="Buscar por nombre o DNI"
          :items="userOptions"
          labelKey="_label"
          valueKey="idPersonal"
          placeholder="Escribí nombre o DNI"
        />
        <AppButton :loading="store.loading" @click="loadUsuarios">
          Refrescar
        </AppButton>
        <button
          v-if="selectedUserId"
          @click="selectedUserId = ''"
          class="app-button-soft min-h-10 rounded-lg border px-4 py-2 text-sm font-semibold"
          type="button"
        >
          Limpiar
        </button>
      </div>

      <div v-if="store.error" role="alert" class="mt-2 flex flex-col gap-2 rounded-lg border border-error/25 bg-error-light/25 px-3 py-2 text-sm font-semibold text-error-dark sm:flex-row sm:items-center sm:justify-between">
        <span>{{ store.error }}</span>
        <button
          @click="loadUsuarios"
          class="app-button-soft min-h-9 rounded-lg border px-3 py-1.5 text-xs font-bold"
          type="button"
        >
          Reintentar
        </button>
      </div>
    </SectionCard>

    <div class="space-y-2 sm:hidden">
      <div v-if="store.loading" class="app-card rounded-xl px-3.5 py-4 text-center text-sm text-neutral-500">
        Cargando usuarios...
      </div>
      <div v-else-if="!store.error && usuariosFiltrados.length === 0" class="app-card rounded-xl px-3.5 py-4 text-center text-sm text-neutral-500">
        No se encontraron usuarios.
      </div>
      <template v-else-if="!store.error">
        <article
          v-for="usuario in pagedUsuarios"
          :key="`mobile-${usuario.idPersonal}`"
          class="app-card rounded-xl p-3.5"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="truncate text-base font-extrabold text-neutral-900">{{ usuario.nombre }}</p>
              <p class="mt-0.5 text-xs font-semibold text-neutral-500">DNI {{ usuario.dni || 'sin informar' }} · ID {{ usuario.idPersonal }}</p>
            </div>
            <span :class="usuario.activo === 1 ? 'app-state-active' : 'app-state-inactive'" class="shrink-0 rounded-full border px-2 py-1 text-xs font-bold">
              {{ usuario.activo === 1 ? 'Activo' : 'Inactivo' }}
            </span>
          </div>

          <dl class="mt-3 grid grid-cols-2 gap-2 rounded-lg border border-neutral-100 p-2.5 text-xs">
            <div>
              <dt class="font-semibold uppercase tracking-wide text-neutral-400">Encargado</dt>
              <dd class="mt-0.5 font-bold text-neutral-700">{{ usuario.encargado === 1 ? 'Sí' : 'No' }}</dd>
            </div>
            <div>
              <dt class="font-semibold uppercase tracking-wide text-neutral-400">Acceso admin</dt>
              <dd class="mt-0.5 font-bold text-neutral-700">{{ usuario.is_admin === 1 ? 'Habilitado' : 'Deshabilitado' }}</dd>
            </div>
          </dl>

          <label class="mt-3 flex min-h-10 items-center justify-between gap-3 rounded-lg border border-neutral-100 px-3 py-2 text-sm font-semibold text-neutral-700">
            <span>{{ savingUsers[usuario.idPersonal] ? 'Guardando...' : 'Permitir acceso admin' }}</span>
            <input
              type="checkbox"
              :checked="usuario.is_admin === 1"
              :disabled="isCurrentUser(usuario) || savingUsers[usuario.idPersonal]"
              @change="toggleAdmin(usuario, $event.target.checked)"
              class="h-4 w-4 accent-primary"
              :title="isCurrentUser(usuario) ? 'No podés quitarte el acceso a vos mismo' : ''"
            />
          </label>
        </article>
      </template>
    </div>

    <div v-if="!store.error" class="app-table hidden overflow-x-auto rounded-xl sm:block">
      <table class="min-w-full text-sm">
        <thead class="app-table-head sticky top-0 z-10">
          <tr>
            <th class="border-b border-neutral-200 px-3 py-2 text-left font-semibold">ID</th>
            <th class="border-b border-neutral-200 px-3 py-2 text-left font-semibold">Nombre</th>
            <th class="border-b border-neutral-200 px-3 py-2 text-left font-semibold">DNI</th>
            <th class="border-b border-neutral-200 px-3 py-2 text-left font-semibold">Activo</th>
            <th class="border-b border-neutral-200 px-3 py-2 text-left font-semibold">Encargado</th>
            <th class="border-b border-neutral-200 px-3 py-2 text-left font-semibold">Acceso Admin</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.loading">
            <td colspan="6" class="px-3 py-4 text-center text-neutral-500">Cargando usuarios...</td>
          </tr>
          <tr v-else-if="usuariosFiltrados.length === 0">
            <td colspan="6" class="px-3 py-4 text-center text-neutral-500">No se encontraron usuarios.</td>
          </tr>
          <tr v-for="usuario in pagedUsuarios" :key="usuario.idPersonal" class="app-table-row">
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.idPersonal }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.nombre }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.dni || '-' }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.activo === 1 ? 'Sí' : 'No' }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.encargado === 1 ? 'Sí' : 'No' }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">
              <label class="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  :checked="usuario.is_admin === 1"
                  :disabled="isCurrentUser(usuario) || savingUsers[usuario.idPersonal]"
                  @change="toggleAdmin(usuario, $event.target.checked)"
                  class="w-4 h-4 accent-primary"
                  :title="isCurrentUser(usuario) ? 'No podés quitarte el acceso a vos mismo' : ''"
                />
                <span class="text-xs text-neutral-500">
                  {{ savingUsers[usuario.idPersonal] ? 'Guardando...' : (usuario.is_admin === 1 ? 'Habilitado' : 'Deshabilitado') }}
                </span>
              </label>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="usuariosFiltrados.length > 0" class="app-card flex flex-col gap-3 rounded-xl px-3.5 py-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
        <p class="text-xs font-semibold text-neutral-400">
          Mostrando {{ pageStart + 1 }}-{{ pageEnd }} de {{ usuariosFiltrados.length }} usuarios
        </p>
        <label class="flex items-center gap-2 text-xs font-semibold text-neutral-500">
          Ver
          <select
            v-model.number="pageSize"
            class="app-input rounded-lg border px-2 py-1.5 text-xs font-bold focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
          </select>
          por página
        </label>
      </div>

      <div class="flex items-center justify-between gap-3 sm:justify-end">
        <button
          @click="page = Math.max(1, page - 1)"
          :disabled="page === 1 || store.loading"
          class="min-h-10 rounded-lg border border-neutral-300 px-4 py-2 text-sm font-semibold text-neutral-700 disabled:opacity-40"
          type="button"
        >
          Anterior
        </button>
        <span class="text-xs text-neutral-400">Página {{ page }} / {{ totalPages }}</span>
        <button
          @click="page = Math.min(totalPages, page + 1)"
          :disabled="page === totalPages || store.loading"
          class="min-h-10 rounded-lg border border-neutral-300 px-4 py-2 text-sm font-semibold text-neutral-700 disabled:opacity-40"
          type="button"
        >
          Siguiente
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import AutocompleteField from '@/components/AutocompleteField.vue'
import SectionCard from '@/components/SectionCard.vue'
import FeedbackMessage from '@/components/ui/FeedbackMessage.vue'
import AppButton from '@/components/ui/AppButton.vue'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'

const store = useAdminStore()
const authStore = useAuthStore()

const selectedUserId = ref('')
const savingUsers = reactive({})
const page = ref(1)
const pageSize = ref(5)
const pageSizeOptions = [5, 10, 25, 50]
const saveError = ref('')

const userOptions = computed(() => {
  return store.usuariosConfiguracion.map((usuario) => ({
    ...usuario,
    _label: [usuario.nombre, usuario.dni ? `DNI ${usuario.dni}` : '', `ID ${usuario.idPersonal}`].filter(Boolean).join(' - '),
  }))
})

const usuariosFiltrados = computed(() => {
  if (!selectedUserId.value) return store.usuariosConfiguracion
  return store.usuariosConfiguracion.filter((usuario) => Number(usuario.idPersonal) === Number(selectedUserId.value))
})

const totalPages = computed(() => Math.max(1, Math.ceil(usuariosFiltrados.value.length / pageSize.value)))
const pageStart = computed(() => (page.value - 1) * pageSize.value)
const pageEnd = computed(() => Math.min(pageStart.value + pageSize.value, usuariosFiltrados.value.length))
const pagedUsuarios = computed(() => usuariosFiltrados.value.slice(pageStart.value, pageEnd.value))

async function loadUsuarios() {
  await store.fetchUsuariosConfiguracion()
}

function isCurrentUser(usuario) {
  return authStore.user?.idPersonal === usuario.idPersonal
}

async function toggleAdmin(usuario, checked) {
  saveError.value = ''
  const oldValue = usuario.is_admin
  usuario.is_admin = checked ? 1 : 0
  savingUsers[usuario.idPersonal] = true

  try {
    const updated = await store.updateAccesoUsuario(usuario.idPersonal, checked)
    usuario.is_admin = updated.is_admin
  } catch (error) {
    usuario.is_admin = oldValue
    saveError.value = error.response?.data?.detail || 'No se pudo actualizar el acceso'
  } finally {
    savingUsers[usuario.idPersonal] = false
  }
}

watch([selectedUserId, pageSize], () => {
  page.value = 1
})

watch(totalPages, (value) => {
  if (page.value > value) page.value = value
})

onMounted(() => {
  loadUsuarios()
})
</script>
