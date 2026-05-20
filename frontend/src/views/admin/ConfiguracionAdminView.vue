<template>
  <div class="space-y-4">
    <SectionCard title="Configuracion de Acceso">
      <div class="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-900 mb-3">
        El acceso inicial fue otorgado al usuario ID 951. Desde aqui se puede habilitar o deshabilitar acceso admin a otros usuarios.
      </div>

      <div class="flex flex-wrap gap-2 items-end">
        <InputField v-model="buscar" label="Buscar por nombre o DNI" placeholder="Ej: Juan o 30123456" />
        <button
          @click="loadUsuarios"
          class="h-12 px-4 rounded-xl bg-primary-dark text-white font-semibold hover:bg-primary transition-colors"
        >
          Buscar
        </button>
      </div>

      <p v-if="store.error" class="text-sm text-red-700 mt-2">{{ store.error }}</p>
    </SectionCard>

    <div class="bg-white border border-neutral-200 rounded-2xl overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="bg-neutral-50 text-neutral-600">
          <tr>
            <th class="text-left px-3 py-2.5 font-semibold border-b border-neutral-200">ID</th>
            <th class="text-left px-3 py-2.5 font-semibold border-b border-neutral-200">Nombre</th>
            <th class="text-left px-3 py-2.5 font-semibold border-b border-neutral-200">DNI</th>
            <th class="text-left px-3 py-2.5 font-semibold border-b border-neutral-200">Activo</th>
            <th class="text-left px-3 py-2.5 font-semibold border-b border-neutral-200">Encargado</th>
            <th class="text-left px-3 py-2.5 font-semibold border-b border-neutral-200">Acceso Admin</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.loading">
            <td colspan="6" class="px-3 py-8 text-center text-neutral-500">Cargando usuarios...</td>
          </tr>
          <tr v-else-if="store.usuariosConfiguracion.length === 0">
            <td colspan="6" class="px-3 py-8 text-center text-neutral-500">No se encontraron usuarios.</td>
          </tr>
          <tr v-for="usuario in store.usuariosConfiguracion" :key="usuario.idPersonal" class="hover:bg-neutral-50/70">
            <td class="px-3 py-2.5 border-b border-neutral-100">{{ usuario.idPersonal }}</td>
            <td class="px-3 py-2.5 border-b border-neutral-100">{{ usuario.nombre }}</td>
            <td class="px-3 py-2.5 border-b border-neutral-100">{{ usuario.dni || '-' }}</td>
            <td class="px-3 py-2.5 border-b border-neutral-100">{{ usuario.activo === 1 ? 'Si' : 'No' }}</td>
            <td class="px-3 py-2.5 border-b border-neutral-100">{{ usuario.encargado === 1 ? 'Si' : 'No' }}</td>
            <td class="px-3 py-2.5 border-b border-neutral-100">
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
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import InputField from '@/components/InputField.vue'
import SectionCard from '@/components/SectionCard.vue'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'

const store = useAdminStore()
const authStore = useAuthStore()

const buscar = ref('')
const savingUsers = reactive({})

async function loadUsuarios() {
  await store.fetchUsuariosConfiguracion(buscar.value)
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

onMounted(() => {
  loadUsuarios()
})
</script>
