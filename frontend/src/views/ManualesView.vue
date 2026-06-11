<template>
  <div class="min-h-[calc(100vh-8.5rem)] bg-neutral-100 px-4 py-5 pb-24 md:min-h-[calc(100vh-3.5rem)] md:px-6 md:py-6">
    <div class="mx-auto max-w-7xl space-y-4">
      <PageHeader
        title="Manuales de Usuario"
        description="Guía de uso del sistema por tipo de usuario."
      >
        <template #kicker>
          <span class="rounded-full border px-3 py-1 text-xs font-bold uppercase tracking-wide app-chip-info">
            {{ currentRoleLabel }}
          </span>
        </template>
        <template #actions>
          <AppButton variant="secondary" :disabled="loading" @click="loadManual(activeManual.id)">
            <AppIcon name="refresh" size="sm" />
            Refrescar
          </AppButton>
          <a
            :href="activeManual.pdfUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-primary px-4 text-sm font-bold text-on-primary transition-colors hover:bg-primary-dark"
          >
            <AppIcon name="download" size="sm" />
            Abrir PDF
          </a>
        </template>
      </PageHeader>

      <section class="grid gap-3 md:grid-cols-3">
        <button
          v-for="manual in manuals"
          :key="manual.id"
          type="button"
          :class="manualButtonClass(manual)"
          @click="selectManual(manual.id)"
        >
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-neutral-200 bg-neutral-50 text-primary-dark">
            <AppIcon :name="manual.icon" />
          </span>
          <span class="min-w-0 text-left">
            <span class="block text-sm font-extrabold">{{ manual.label }}</span>
            <span class="mt-0.5 block text-xs font-semibold opacity-70">{{ manual.description }}</span>
          </span>
        </button>
      </section>

      <section class="app-card overflow-hidden rounded-xl">
        <div class="flex flex-col gap-3 border-b border-neutral-100 px-4 py-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-bold uppercase tracking-wide text-neutral-400">Lectura en linea</p>
            <h2 class="mt-1 text-xl font-extrabold text-neutral-950">{{ activeManual.title }}</h2>
          </div>
          <div class="flex flex-wrap gap-2">
            <a
              :href="activeManual.sourceUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm font-bold text-neutral-700 hover:border-primary/40 hover:text-primary-dark"
            >
              <AppIcon name="view" size="sm" />
              Markdown
            </a>
            <button
              type="button"
              class="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm font-bold text-neutral-700 hover:border-primary/40 hover:text-primary-dark"
              @click="printManual"
            >
              <AppIcon name="download" size="sm" />
              Imprimir
            </button>
          </div>
        </div>

        <div v-if="loading" class="flex min-h-80 items-center justify-center text-primary">
          <AppIcon name="loading" size="xl" class="animate-spin" />
        </div>

        <div v-else-if="error" class="p-6">
          <div class="rounded-xl border border-error-light bg-error-light/30 p-4 text-sm font-semibold text-error-dark">
            {{ error }}
          </div>
        </div>

        <article
          v-else
          class="manual-content prose-safe max-w-none px-4 py-5 md:px-8 md:py-7"
          v-html="renderedManual"
        ></article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')
const activeManualId = ref('operador')
const manualMarkdown = ref('')

const manuals = [
  {
    id: 'operador',
    label: 'Operador',
    title: 'Manual de Usuario - Operador',
    description: 'Carga, pendientes, mis registros y trabajo offline.',
    icon: 'person',
    sourceUrl: '/manuales/manual-operador.md',
    pdfUrl: '/manuales/pdf/manual-operador.pdf',
  },
  {
    id: 'encargado',
    label: 'Encargado',
    title: 'Manual de Usuario - Encargado',
    description: 'Carga por operador, dashboard y pendientes por unidad.',
    icon: 'personnel',
    sourceUrl: '/manuales/manual-encargado.md',
    pdfUrl: '/manuales/pdf/manual-encargado.pdf',
  },
  {
    id: 'admin',
    label: 'Admin',
    title: 'Manual de Usuario - Admin',
    description: 'Panel admin, catalogos, accesos y asignaciones.',
    icon: 'admin',
    sourceUrl: '/manuales/manual-admin.md',
    pdfUrl: '/manuales/pdf/manual-admin.pdf',
  },
]

const activeManual = computed(() => manuals.find((manual) => manual.id === activeManualId.value) || manuals[0])

const currentRoleLabel = computed(() => {
  if (authStore.isAdmin) return 'Tu rol: Admin'
  if (authStore.user?.encargado === 1) return 'Tu rol: Encargado'
  return 'Tu rol: Operador'
})

const renderedManual = computed(() => renderMarkdown(manualMarkdown.value))

onMounted(() => {
  activeManualId.value = defaultManualId()
  loadManual(activeManualId.value)
})

function defaultManualId() {
  if (authStore.isAdmin) return 'admin'
  if (authStore.user?.encargado === 1) return 'encargado'
  return 'operador'
}

async function selectManual(id) {
  if (id === activeManualId.value) return
  activeManualId.value = id
  await loadManual(id)
}

async function loadManual(id) {
  const manual = manuals.find((item) => item.id === id) || manuals[0]
  loading.value = true
  error.value = ''
  try {
    const response = await fetch(manual.sourceUrl, { cache: 'no-cache' })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    manualMarkdown.value = await response.text()
  } catch {
    manualMarkdown.value = ''
    error.value = 'No se pudo cargar el manual. Intentá nuevamente o contactá al administrador.'
  } finally {
    loading.value = false
  }
}

function printManual() {
  window.print()
}

function manualButtonClass(manual) {
  return [
    'flex min-h-24 items-center gap-3 rounded-xl border px-4 py-3 transition-all text-left',
    activeManualId.value === manual.id
      ? 'border-primary/45 bg-primary-light text-primary-dark shadow-[0_0_18px_rgba(16,185,129,0.10)]'
      : 'border-neutral-200 bg-white text-neutral-800 shadow-sm hover:border-primary/40 hover:bg-neutral-50',
  ]
}

function renderMarkdown(markdown) {
  const normalized = markdown
    .replaceAll('../../frontend/public/logo-forestal.png', '/logo-forestal.png')
    .replace(/\r\n/g, '\n')

  const lines = normalized.split('\n')
  const html = []
  let paragraph = []
  let listType = ''
  let tableRows = []

  function flushParagraph() {
    if (paragraph.length === 0) return
    html.push(`<p>${inline(paragraph.join(' '))}</p>`)
    paragraph = []
  }

  function flushList() {
    if (!listType) return
    html.push(`</${listType}>`)
    listType = ''
  }

  function flushTable() {
    if (tableRows.length === 0) return
    const rows = tableRows.filter((row) => !/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(row))
    if (rows.length > 0) {
      html.push('<table>')
      rows.forEach((row, index) => {
        const cells = row.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim())
        const tag = index === 0 ? 'th' : 'td'
        html.push(`<tr>${cells.map((cell) => `<${tag}>${inline(cell)}</${tag}>`).join('')}</tr>`)
      })
      html.push('</table>')
    }
    tableRows = []
  }

  lines.forEach((line) => {
    const trimmed = line.trim()

    if (trimmed.includes('|') && /^\|?[^|]+\|/.test(trimmed)) {
      flushParagraph()
      flushList()
      tableRows.push(trimmed)
      return
    }

    flushTable()

    if (!trimmed) {
      flushParagraph()
      flushList()
      return
    }

    const allowedHtml = renderAllowedHtmlLine(trimmed)
    if (allowedHtml) {
      flushParagraph()
      flushList()
      html.push(allowedHtml)
      return
    }

    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/)
    if (heading) {
      flushParagraph()
      flushList()
      const level = heading[1].length
      html.push(`<h${level}>${inline(heading[2])}</h${level}>`)
      return
    }

    const unordered = trimmed.match(/^-\s+(.+)$/)
    if (unordered) {
      flushParagraph()
      if (listType !== 'ul') {
        flushList()
        html.push('<ul>')
        listType = 'ul'
      }
      html.push(`<li>${inline(unordered[1])}</li>`)
      return
    }

    const ordered = trimmed.match(/^\d+\.\s+(.+)$/)
    if (ordered) {
      flushParagraph()
      if (listType !== 'ol') {
        flushList()
        html.push('<ol>')
        listType = 'ol'
      }
      html.push(`<li>${inline(ordered[1])}</li>`)
      return
    }

    paragraph.push(trimmed)
  })

  flushParagraph()
  flushList()
  flushTable()

  return html.join('\n')
}

function inline(value) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

function renderAllowedHtmlLine(value) {
  if (value === '</div>') return '</div>'

  const div = value.match(/^<div\s+class="(cover|page-break|warning|note)">$/)
  if (div) return `<div class="${div[1]}">`

  const img = value.match(/^<img\s+src="([^"]+)"\s+alt="([^"]*)"\s*\/?>$/)
  if (!img) return ''

  const normalizedSrc = img[1].replace('../../frontend/public/logo-forestal.png', '/logo-forestal.png')
  if (!isSafeImageSrc(normalizedSrc)) return ''

  return `<img src="${escapeHtml(normalizedSrc)}" alt="${escapeHtml(img[2])}">`
}

function isSafeImageSrc(value) {
  return value.startsWith('/') && !value.startsWith('//') && !/[<>"']/g.test(value)
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}
</script>

<style scoped>
.manual-content :deep(.cover) {
  align-items: center;
  background: var(--app-surface-muted);
  border: 1px solid var(--app-border);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  margin-bottom: 2rem;
  padding: 2rem;
  text-align: center;
}

.manual-content :deep(.cover img) {
  height: auto;
  margin-bottom: 1rem;
  max-width: 11rem;
}

.manual-content :deep(.cover h1) {
  color: var(--app-text);
  font-size: 2rem;
  font-weight: 900;
  line-height: 1.05;
  margin: 0;
}

.manual-content :deep(.subtitle) {
  color: var(--color-primary-dark);
  font-size: 1.1rem;
  font-weight: 800;
  margin-top: 0.35rem;
}

.manual-content :deep(.meta) {
  color: var(--app-text-muted);
  font-size: 0.85rem;
  margin-top: 0.75rem;
}

.manual-content :deep(.page-break) {
  display: none;
}

.manual-content :deep(h1) {
  color: var(--app-text);
  font-size: 1.8rem;
  font-weight: 900;
  line-height: 1.15;
  margin: 0 0 1rem;
}

.manual-content :deep(h2) {
  border-bottom: 1px solid var(--app-border);
  color: var(--color-primary-dark);
  font-size: 1.35rem;
  font-weight: 900;
  margin: 2rem 0 0.75rem;
  padding-bottom: 0.4rem;
}

.manual-content :deep(h3) {
  color: var(--app-text);
  font-size: 1.05rem;
  font-weight: 900;
  margin: 1.35rem 0 0.5rem;
}

.manual-content :deep(p) {
  color: var(--app-text-muted);
  line-height: 1.65;
  margin: 0 0 0.9rem;
}

.manual-content :deep(ul),
.manual-content :deep(ol) {
  color: var(--app-text-muted);
  line-height: 1.65;
  margin: 0 0 1rem 1.25rem;
}

.manual-content :deep(li) {
  margin: 0.18rem 0;
}

.manual-content :deep(table) {
  border-collapse: collapse;
  margin: 1rem 0 1.25rem;
  width: 100%;
}

.manual-content :deep(th),
.manual-content :deep(td) {
  border: 1px solid var(--app-border);
  padding: 0.65rem 0.75rem;
  text-align: left;
  vertical-align: top;
}

.manual-content :deep(th) {
  background: var(--app-surface-muted);
  color: var(--color-primary-dark);
  font-size: 0.8rem;
  font-weight: 900;
  text-transform: uppercase;
}

.manual-content :deep(code) {
  background: var(--app-surface-muted);
  border: 1px solid var(--app-border);
  border-radius: 0.3rem;
  color: var(--color-primary-dark);
  font-size: 0.86em;
  padding: 0.08rem 0.28rem;
}

.manual-content :deep(.warning),
.manual-content :deep(.note) {
  border-left: 4px solid var(--color-primary);
  border-radius: 0.5rem;
  margin: 1rem 0;
  padding: 0.9rem 1rem;
}

.manual-content :deep(.warning) {
  background: var(--color-idle-bg);
  border-left-color: var(--color-warning-dark);
}

.manual-content :deep(.note) {
  background: var(--color-active-bg);
}

@media print {
  .manual-content {
    padding: 0 !important;
  }
}
</style>
