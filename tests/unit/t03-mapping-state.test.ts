import { describe, expect, it } from 'vitest'
import {
  acceptPreview,
  canConfirm,
  cancelPreview,
  currentPreview,
  draftKey,
  mappingDraftValid,
  selectSource,
  updateDraft,
} from '../../apps/desktop/src/renderer/src/mapping/model'
import type { PreviewView, Wizard } from '../../apps/desktop/src/renderer/src/mapping/model'

const initial: Wizard = {
  projectId: 'P',
  revision: 1,
  generation: 0,
  source: {
    selectionId: 'opaque',
    fingerprint: 'source-1',
    sheet: 'CSV',
    encoding: 'utf-8-sig',
    totalRows: 2,
    fields: [
      { name: 'id', observedTypes: ['string'], samples: ['001', '002'] },
      { name: 'name', observedTypes: ['string'], samples: ['泵站A', '泵站B'] },
    ],
  },
  draft: {
    identity: 'M',
    version: 1,
    namespace: 'urn:e/',
    classIri: 'urn:Equipment',
    keys: ['id'],
    fields: [
      {
        column: 'name',
        predicate: 'urn:name',
        kind: 'string',
        trim: false,
        empty: 'omit',
        referenceNamespace: '',
        referenceColumns: [],
      },
    ],
  },
  preview: null,
  confirmed: false,
}
const preview: PreviewView = {
  resultId: 'result',
  projectId: 'P',
  revision: 1,
  sourceFingerprint: 'source-1',
  selectionId: 'opaque',
  sheet: 'CSV',
  encoding: 'utf-8-sig',
  generation: 0,
  draftKey: draftKey(initial.draft),
  rows: [],
  added: [],
  removed: [],
  modified: [],
  identitiesAdded: [],
  identitiesRemoved: [],
  issues: [],
  conflicts: [],
}

describe('T03 private wizard state', () => {
  it('requires fresh preview and explicit confirmation', () => {
    expect(mappingDraftValid(initial)).toBe(true)
    expect(canConfirm(initial)).toBe(false)
    const ready = acceptPreview(initial, preview)
    expect(currentPreview(ready)).toBe(true)
    expect(canConfirm(ready)).toBe(false)
    expect(canConfirm({ ...ready, confirmed: true })).toBe(true)
  })
  it('rejects late results for another project, source, revision or draft', () => {
    for (const change of [
      { projectId: 'other' },
      { revision: 0 },
      { sourceFingerprint: 'old' },
      { draftKey: 'old' },
    ])
      expect(acceptPreview(initial, { ...preview, ...change })).toBe(initial)
  })
  it('draft/source changes invalidate preview and confirmation without discarding unrelated fields', () => {
    const ready = { ...acceptPreview(initial, preview), confirmed: true }
    const changed = updateDraft(ready, { ...ready.draft, namespace: 'urn:new/' })
    expect(changed.preview).toBeNull()
    expect(changed.confirmed).toBe(false)
    const selected = selectSource(ready, {
      ...initial.source!,
      fields: [initial.source!.fields[0]],
      fingerprint: 'new',
    })
    expect(selected.draft.keys).toEqual(['id'])
    expect(selected.draft.fields).toEqual([])
    expect(selected.preview).toBeNull()
    expect(selected.confirmed).toBe(false)
  })
  it('never allows commit for conversion errors or ownership/manual conflict', () => {
    const ready = { ...acceptPreview(initial, preview), confirmed: true }
    expect(
      canConfirm({
        ...ready,
        preview: {
          ...preview,
          issues: [{ code: 'EMPTY_KEY', sheet: 'CSV', row: 2, column: 1, field: 'id' }],
        },
      }),
    ).toBe(false)
    expect(
      canConfirm({
        ...ready,
        preview: {
          ...preview,
          conflicts: [
            {
              code: 'MANUAL_DRIFT',
              subject: 'urn:e/001',
              predicate: 'urn:name',
              current: 'manual',
              source: 'new',
              managed: 'old',
              owner: 'M',
              sourceRow: '2',
            },
          ],
        },
      }),
    ).toBe(false)
    expect(canConfirm({ ...ready, revision: 2 })).toBe(false)
  })
  it('requires key selection and disallows empty literals in typed values', () => {
    expect(mappingDraftValid({ ...initial, draft: { ...initial.draft, keys: [] } })).toBe(false)
    expect(
      mappingDraftValid({
        ...initial,
        draft: {
          ...initial.draft,
          fields: [{ ...initial.draft.fields[0], kind: 'integer', empty: 'literal' }],
        },
      }),
    ).toBe(false)
  })
})

describe('T03 selection lifecycle', () => {
  it('rejects late previews after same-file worksheet, encoding or selection changes', () => {
    for (const change of [
      { sheet: 'sheet-B' },
      { encoding: 'gb18030' },
      { selectionId: 'new-pick' },
    ]) {
      const selected = selectSource(initial, { ...initial.source!, ...change })
      expect(acceptPreview(selected, preview)).toBe(selected)
      expect(canConfirm({ ...selected, preview, confirmed: true })).toBe(false)
    }
  })
  it('cancellation invalidates an outstanding result even with unchanged inputs', () => {
    const cancelled = cancelPreview(initial)
    expect(acceptPreview(cancelled, preview)).toBe(cancelled)
    expect(cancelled.generation).toBe(1)
    const fresh = { ...preview, generation: cancelled.generation }
    expect(currentPreview(acceptPreview(cancelled, fresh))).toBe(true)
  })
  it('changing a draft then restoring identical values does not revive the old result', () => {
    const changed = updateDraft(initial, { ...initial.draft, namespace: 'urn:changed/' })
    const restored = updateDraft(changed, initial.draft)
    expect(acceptPreview(restored, preview)).toBe(restored)
    expect(restored.draft).toEqual(initial.draft)
    expect(restored.generation).toBe(2)
  })
})
