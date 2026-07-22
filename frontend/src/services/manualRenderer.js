/**
 * Minimal Markdown -> HTML renderer for the user manuals in
 * `frontend/public/manuales/*.md`.
 *
 * Supports:
 *   - ATX headings (#, ##, ###, ####)
 *   - Unordered (- ) and ordered (1. ) lists
 *   - Pipe tables
 *   - Inline `code` and **bold**
 *   - A small whitelist of explicit HTML blocks (div.cover, div.page-break,
 *     div.subtitle, h1-h4, p.meta, img with local src)
 *
 * The whitelist lets the manual files use a cover page and page breaks
 * without exposing arbitrary HTML.
 *
 * Everything else is HTML-escaped so that no Markdown source can leak
 * raw tags into the rendered view.
 */

const HTML_WHITELIST_TAGS = new Set(['div', 'h1', 'h2', 'h3', 'h4', 'p', 'img'])

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function inline(value) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

function isSafeImageSrc(value) {
  return value.startsWith('/') && !value.startsWith('//') && !/[<>"']/g.test(value)
}

/**
 * Try to render a single line as a whitelisted HTML block. Returns the
 * HTML string when the line matches a known shape, or an empty string
 * when the line should be processed as regular Markdown.
 */
function renderAllowedHtmlLine(value) {
  if (value === '</div>') return '</div>'

  const pageBreak = value.match(/^<div\s+class="page-break"\s*>\s*<\/div>$/)
  if (pageBreak) return '<div class="page-break"></div>'

  const div = value.match(/^<div\s+class="(cover|page-break|warning|note)">$/)
  if (div) return `<div class="${div[1]}">`

  const subtitle = value.match(/^<div\s+class="subtitle"\s*>(.+)<\/div>$/)
  if (subtitle) return `<div class="subtitle">${inline(subtitle[1])}</div>`

  const heading = value.match(/^<h([1-4])>(.+)<\/h\1>$/)
  if (heading) return `<h${heading[1]}>${inline(heading[2])}</h${heading[1]}>`

  const meta = value.match(/^<p\s+class="meta"\s*>(.+)<\/p>$/)
  if (meta) {
    const parts = meta[1].split(/<br\s*\/?>/i).map((part) => inline(part))
    return `<p class="meta">${parts.join('<br>')}</p>`
  }

  const img = value.match(/^<img\s+src="([^"]+)"\s+alt="([^"]*)"\s*\/?>$/)
  if (!img) return ''

  const normalizedSrc = img[1].replace('../../frontend/public/logo-forestal.png', '/logo-forestal.png')
  if (!isSafeImageSrc(normalizedSrc)) return ''

  return `<img src="${escapeHtml(normalizedSrc)}" alt="${escapeHtml(img[2])}">`
}

/**
 * Render a manual Markdown source as an HTML string safe to bind via v-html.
 * Any HTML tag not in `HTML_WHITELIST_TAGS` is escaped.
 */
export function renderManualMarkdown(markdown) {
  if (!markdown) return ''

  const normalized = String(markdown)
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

  for (const rawLine of lines) {
    const trimmed = rawLine.trim()

    if (trimmed.includes('|') && /^\|?[^|]+\|/.test(trimmed)) {
      flushParagraph()
      flushList()
      tableRows.push(trimmed)
      continue
    }

    flushTable()

    if (!trimmed) {
      flushParagraph()
      flushList()
      continue
    }

    const allowedHtml = renderAllowedHtmlLine(trimmed)
    if (allowedHtml) {
      flushParagraph()
      flushList()
      html.push(allowedHtml)
      continue
    }

    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/)
    if (heading) {
      flushParagraph()
      flushList()
      const level = heading[1].length
      html.push(`<h${level}>${inline(heading[2])}</h${level}>`)
      continue
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
      continue
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
      continue
    }

    paragraph.push(trimmed)
  }

  flushParagraph()
  flushList()
  flushTable()

  return html.join('\n')
}

export { escapeHtml, inline, isSafeImageSrc, renderAllowedHtmlLine, HTML_WHITELIST_TAGS }
