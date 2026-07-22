import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import {
  renderManualMarkdown,
  renderAllowedHtmlLine,
  isSafeImageSrc,
  escapeHtml,
} from './manualRenderer.js'

const here = dirname(fileURLToPath(import.meta.url))
const manualsDir = resolve(here, '../../public/manuales')

describe('manualRenderer - escapeHtml', () => {
  it('escapes all HTML-significant characters', () => {
    expect(escapeHtml('<h1>Hola "Mundo" & \'ok\'</h1>'))
      .toBe('&lt;h1&gt;Hola &quot;Mundo&quot; &amp; &#039;ok&#039;&lt;/h1&gt;')
  })

  it('handles empty string and number values', () => {
    expect(escapeHtml('')).toBe('')
    expect(escapeHtml(42)).toBe('42')
  })
})

describe('manualRenderer - isSafeImageSrc', () => {
  it('accepts local absolute paths', () => {
    expect(isSafeImageSrc('/logo-forestal.png')).toBe(true)
    expect(isSafeImageSrc('/assets/x.png')).toBe(true)
  })

  it('rejects relative, scheme-relative, remote or malformed srcs', () => {
    expect(isSafeImageSrc('//evil.com/x.png')).toBe(false)
    expect(isSafeImageSrc('https://evil.com/x.png')).toBe(false)
    expect(isSafeImageSrc('javascript:alert(1)')).toBe(false)
    expect(isSafeImageSrc('"><script>')).toBe(false)
    expect(isSafeImageSrc('logo.png')).toBe(false)
  })
})

describe('manualRenderer - renderAllowedHtmlLine (the bug from issue #28)', () => {
  it('renders the cover opening div', () => {
    expect(renderAllowedHtmlLine('<div class="cover">')).toBe('<div class="cover">')
  })

  it('renders the cover closing div', () => {
    expect(renderAllowedHtmlLine('</div>')).toBe('</div>')
  })

  it('renders the page-break div (was appearing as raw text in the bug report)', () => {
    expect(renderAllowedHtmlLine('<div class="page-break"></div>'))
      .toBe('<div class="page-break"></div>')
  })

  it('renders the h1 inside the cover (was appearing as raw text in the bug report)', () => {
    expect(renderAllowedHtmlLine('<h1>Manual de Usuario</h1>'))
      .toBe('<h1>Manual de Usuario</h1>')
  })

  it('renders the subtitle div (was appearing as raw text in the bug report)', () => {
    expect(renderAllowedHtmlLine('<div class="subtitle">Admin</div>'))
      .toBe('<div class="subtitle">Admin</div>')
  })

  it('renders the meta paragraph with inline <br>', () => {
    expect(renderAllowedHtmlLine('<p class="meta">Line 1<br>Line 2</p>'))
      .toBe('<p class="meta">Line 1<br>Line 2</p>')
  })

  it('normalizes the local logo src to /logo-forestal.png', () => {
    expect(renderAllowedHtmlLine('<img src="../../frontend/public/logo-forestal.png" alt="Logo">'))
      .toBe('<img src="/logo-forestal.png" alt="Logo">')
  })

  it('rejects remote / unsafe image srcs', () => {
    expect(renderAllowedHtmlLine('<img src="https://evil.com/x.png" alt="x">')).toBe('')
  })

  it('returns empty for non-whitelisted HTML so it falls through to paragraph rendering', () => {
    expect(renderAllowedHtmlLine('<script>alert(1)</script>')).toBe('')
    expect(renderAllowedHtmlLine('<unknown-tag>x</unknown-tag>')).toBe('')
  })
})

describe('manualRenderer - renderManualMarkdown (full pipeline)', () => {
  it('renders the cover + page-break block without leaking raw tags', () => {
    const md = `<div class="cover">
  <img src="../../frontend/public/logo-forestal.png" alt="Logo Forestal">
  <h1>Manual de Usuario</h1>
  <div class="subtitle">Admin</div>
  <p class="meta">Sistema Registro Producción Forestal<br>Versión documental: Junio 2026</p>
</div>

<div class="page-break"></div>

# Manual de Usuario - Admin
`
    const out = renderManualMarkdown(md)

    expect(out).toContain('<div class="cover">')
    expect(out).toContain('<img src="/logo-forestal.png" alt="Logo Forestal">')
    expect(out).toContain('<h1>Manual de Usuario</h1>')
    expect(out).toContain('<div class="subtitle">Admin</div>')
    expect(out).toContain('<p class="meta">')
    expect(out).toContain('<div class="page-break"></div>')

    expect(out).not.toContain('&lt;h1&gt;')
    expect(out).not.toContain('&lt;div class="cover"&gt;')
    expect(out).not.toContain('&lt;div class="page-break"&gt;')
    expect(out).not.toContain('&lt;div class="subtitle"&gt;')
  })

  it('escapes inline <unknown> tags inside paragraphs', () => {
    const md = 'Linea con <desconocido> adentro\n'
    const out = renderManualMarkdown(md)
    expect(out).toContain('&lt;desconocido&gt;')
  })

  it('renders markdown headings, lists, tables and inline code/bold', () => {
    const md = `## Seccion

- item **uno**
- item \`dos\`

1. primero
2. segundo

| col | val |
| --- | --- |
| a | 1 |
`
    const out = renderManualMarkdown(md)
    expect(out).toContain('<h2>Seccion</h2>')
    expect(out).toContain('<li>item <strong>uno</strong></li>')
    expect(out).toContain('<li>item <code>dos</code></li>')
    expect(out).toContain('<ol>')
    expect(out).toContain('<th>col</th>')
  })

  it('handles CRLF line endings', () => {
    const md = '<div class="cover">\r\n  <h1>X</h1>\r\n</div>\r\n'
    const out = renderManualMarkdown(md)
    expect(out).toContain('<div class="cover">')
    expect(out).toContain('<h1>X</h1>')
    expect(out).toContain('</div>')
  })

  it('returns empty string for empty or null input', () => {
    expect(renderManualMarkdown('')).toBe('')
    expect(renderManualMarkdown(null)).toBe('')
    expect(renderManualMarkdown(undefined)).toBe('')
  })

  it('renders all three real manuals without leaking raw HTML tags', () => {
    for (const name of ['manual-admin.md', 'manual-encargado.md', 'manual-operador.md']) {
      const md = readFileSync(resolve(manualsDir, name), 'utf8')
      const out = renderManualMarkdown(md)

      // No raw tag fragments should appear as escaped entities
      expect(out, `${name}: must not contain escaped <h1> tags`).not.toMatch(/&lt;h[1-4]&gt;/)
      expect(out, `${name}: must not contain escaped <div class="cover">`).not.toMatch(/&lt;div class="cover"&gt;/)
      expect(out, `${name}: must not contain escaped <div class="page-break">`).not.toMatch(/&lt;div class="page-break"&gt;/)
      expect(out, `${name}: must not contain escaped <div class="subtitle">`).not.toMatch(/&lt;div class="subtitle"&gt;/)
      expect(out, `${name}: must not contain escaped <p class="meta">`).not.toMatch(/&lt;p class="meta"&gt;/)

      // The legitimate rendered forms should be present
      expect(out, `${name}: should contain cover div`).toContain('<div class="cover">')
      expect(out, `${name}: should contain page-break div`).toContain('<div class="page-break"></div>')
    }
  })
})
