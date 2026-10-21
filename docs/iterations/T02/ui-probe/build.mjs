import { build } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'node:url'
await build({
  root: fileURLToPath(new URL('.', import.meta.url)),
  configFile: false,
  base: './',
  plugins: [react()],
  build: { outDir: 'out', emptyOutDir: true },
})
