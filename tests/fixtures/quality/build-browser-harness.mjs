/** Build only: never starts a browser, server, Electron or a product process. */
import { build } from 'vite'
import react from '@vitejs/plugin-react'
import { mkdir, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { resolve } from 'node:path'

const root = fileURLToPath(new URL('../../../', import.meta.url))
const output = resolve(root, 'out/t05-headless-ui')
await build({
  configFile: false,
  root,
  plugins: [react()],
  define: { 'process.env.NODE_ENV': JSON.stringify('production') },
  build: {
    outDir: output,
    emptyOutDir: false,
    lib: {
      entry: resolve(root, 'tests/fixtures/quality/browser-harness.tsx'),
      name: 'T05Harness',
      formats: ['iife'],
      fileName: () => 'harness.js',
    },
  },
})
await mkdir(output, { recursive: true })
await writeFile(
  resolve(output, 'index.html'),
  '<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><title>T05 private component harness</title><link rel="stylesheet" href="ontolearn-studio.css"><div id="root"></div><script src="harness.js"></script></html>',
)
