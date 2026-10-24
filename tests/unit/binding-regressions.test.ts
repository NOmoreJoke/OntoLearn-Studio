import { describe, it, expect } from 'vitest'
import { acceptsJobEvent, type EventBinding } from '../../packages/contracts/src/v2'
import corpus from '../../packages/contracts/v2/binding-regressions.json'

describe('R2-F1 trusted binding regressions (public wire unchanged)', () => {
  for (const entry of corpus.cases) {
    it(entry.name, () => {
      expect(acceptsJobEvent(entry.value, entry.binding as unknown as EventBinding)).toBe(
        entry.valid,
      )
    })
  }
})
