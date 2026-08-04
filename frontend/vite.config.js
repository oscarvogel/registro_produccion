import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: null, // we register the SW ourselves in main.js so we
                            // can hook onNeedRefresh and force a reload when
                            // a new build ships. Otherwise the operator on the
                            // installed PWA would keep running the old bundle
                            // until they manually hard-reload.
      devOptions: { enabled: true },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      // The head tags required for installability (theme-color, iOS apple-
      // mobile-web-app-*, apple-touch-icon) live in index.html. We keep them
      // there instead of using headHTML/headMeta because the option in
      // vite-plugin-pwa 1.x is silently ignored on this project; the
      // committed index.html is the source of truth and is easier to audit.
      // The manifest stays in this config because it is the structured
      // JSON the browser reads at install time.
      manifest: {
        // `id` is required by the modern PWA spec (Chrome 96+). Without it
        // some browsers treat the app as a duplicate and skip the install
        // prompt entirely.
        id: '/',
        name: 'Registro de Producción',
        short_name: 'Producción',
        description: 'Sistema de registro de producción forestal',
        theme_color: '#143d23',
        background_color: '#f5f5f5',
        // es-AR matches the app's primary locale. Chrome uses the manifest
        // lang to decide UI strings for the install dialog.
        lang: 'es-AR',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        // skipWaiting + clientsClaim lets the new SW take control of open
        // clients immediately. main.js triggers window.location.reload() to
        // make the new assets actually run.
        skipWaiting: true,
        clientsClaim: true,
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        // Cache API responses that are catalogue data (not production submissions)
        runtimeCaching: [
          {
            urlPattern: ({ url }) =>
              /^\/api\/produccion\/(unidades-negocio|tipos-proceso-all|actas|predios|operadores|moviles|tipo-proceso|rodales|lugares-carga|asignaciones|movil-by-operador|ultima-hora-fin)/.test(url.pathname),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-catalogos',
              cacheableResponse: { statuses: [0, 200] },
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 }, // 24h
              networkTimeoutSeconds: 5,
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5174,
    watch: {
      usePolling: true,
      interval: 1000
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  test: {
    environment: 'jsdom',
    globals: true
  }
})
