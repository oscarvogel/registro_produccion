<template>
  <div class="space-y-3">
    <SectionCard title="Configuracion de Acceso">
      <div class="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-900 mb-3">
        Desde aqui se puede habilitar o deshabilitar acceso admin a otros usuarios. No podes quitarte tu propio acceso.
      </div>

      <div class="flex flex-col gap-2 sm:flex-row sm:items-end">
        <AutocompleteField
          v-model="selectedUserId"
          class="w-full sm:w-96"
          label="Buscar por nombre o DNI"
          :items="userOptions"
          labelKey="_label"
          valueKey="idPersonal"
          placeholder="Escribi nombre o DNI"
        />
        <button
          @click="loadUsuarios"
          class="h-12 px-4 rounded-xl bg-primary-dark text-white font-semibold hover:bg-primary transition-colors"
          type="button"
        >
          Refrescar
        </button>
        <button
          v-if="selectedUserId"
          @click="selectedUserId = ''"
          class="h-12 px-4 rounded-xl border border-neutral-300 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
          type="button"
        >
          Limpiar
        </button>
      </div>

      <p v-if="store.error" class="text-sm text-red-700 mt-2">{{ store.error }}</p>
    </SectionCard>

    <div class="overflow-x-auto rounded-xl border border-neutral-200 bg-white">
      <table class="min-w-full text-sm">
        <thead class="bg-neutral-50 text-neutral-600">
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
          <tr v-for="usuario in pagedUsuarios" :key="usuario.idPersonal" class="hover:bg-neutral-50/70">
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.idPersonal }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.nombre }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.dni || '-' }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.activo === 1 ? 'Si' : 'No' }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">{{ usuario.encargado === 1 ? 'Si' : 'No' }}</td>
            <td class="border-b border-neutral-100 px-3 py-2">
              <label class="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  :checked="usuario.is_admin === 1"
                  :disabled="isCurrentUser(usuario) || savingUsers[usuario.idPersonal]"
                  @change="toggleAdmin(usuario, $event.target.checked)"
                  class="w-4 h-4 accent-primary"
                  :title="isCurrentUser(usuario) ? 'No podes quitarte el acceso a vos mismo' : ''"
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

    <div v-if="usuariosFiltrados.length > 0" class="flex flex-col gap-3 rounded-xl border border-neutral-200 bg-white px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
        <p class="text-xs font-semibold text-neutral-400">
          Mostrando {{ pageStart + 1 }}-{{ pageEnd }} de {{ usuariosFiltrados.length }} usuarios
        </p>
        <label class="flex items-center gap-2 text-xs font-semibold text-neutral-500">
          Ver
          <select
            v-model.number="pageSize"
            class="rounded-lg border border-neutral-200 bg-white px-2 py-1.5 text-xs font-bold text-neutral-700 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
          </select>
          por pagina
        </label>
      </div>

      <div class="flex items-center justify-between gap-3 sm:justify-end">
        <button
          @click="page = Math.max(1, page - 1)"
          :disabled="page === 1 || store.loading"
          class="px-4 py-2 rounded-lg border border-neutral-300 text-sm font-semibold text-neutral-700 disabled:opacity-40"
          type="button"
        >
          Anterior
        </button>
        <span class="text-xs text-neutral-400">Pagina {{ page }} / {{ totalPages }}</span>
        <button
          @click="page = Math.min(totalPages, page + 1)"
          :disabled="page === totalPages || store.loading"
          class="px-4 py-2 rounded-lg border border-neutral-300 text-sm font-semibold text-neutral-700 disabled:opacity-40"
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
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'

const store = useAdminStore()
const authStore = useAuthStore()

const selectedUserId = ref('')
const savingUsers = reactive({})
const page = ref(1)
const pageSize = ref(5)
const pageSizeOptions = [5, 10, 25, 50]

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
  const oldValue = usuario.is_admin
  usuario.is_admin = checked ? 1 : 0
  savingUsers[usuario.idPersonal] = true

  try {
    const updated = await store.updateAccesoUsuario(usuario.idPersonal, checked)
    usuario.is_admin = updated.is_admin
  } catch (error) {
    usuario.is_admin = oldValue
    alert(error.response?.data?.detail || 'No se pudo actualizar el acceso')
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
