import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'

// Reviewer-local config. Never touches the reviewed vitest.config.mts or tests/unit.
export default defineConfig({
  test: {
    include: ['out/t10-review/round-1/minimax/**/*.test.ts'],
    root: fileURLToPath(new URL('../../../../', import.meta.url)),
  },
})
