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
      devOptions: { enabled: true },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'Registro de Producción',
        short_name: 'Producción',
        description: 'Sistema de registro de producción forestal',
        theme_color: '#143d23',
        background_color: '#f5f5f5',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        // Cache API responses that are catalogue data (not production submissions)
        runtimeCaching: [
          {
            urlPattern: ({ url }) =>
              /^\/api\/produccion\/(unidades-negocio|tipos-proceso-all|actas|predios|operadores|moviles|tipo-proceso|rodales|lugares-carga|asignaciones|movil-by-operador|ultima-hora-fin)/.test(url.pathname),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-catalogos',
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
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
