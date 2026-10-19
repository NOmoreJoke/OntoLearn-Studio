import { defineConfig } from 'electron-vite'
import react from '@vitejs/plugin-react'
import { randomBytes } from 'node:crypto'
import { resolve } from 'node:path'

const devNonce = randomBytes(18).toString('base64')

export default defineConfig({
  main: {
    define: { __DEV_CSP_NONCE__: JSON.stringify(devNonce) },
    build: { externalizeDeps: { exclude: ['@ontolearn/contracts'] } },
  },
  preload: {},
  renderer: {
    plugins: [react()],
    html: { cspNonce: devNonce },
    server: { host: '127.0.0.1', port: 5173, strictPort: true },
    build: { rollupOptions: { input: resolve('src/renderer/index.html') } },
  },
})
