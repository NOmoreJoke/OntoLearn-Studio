/** W3b S2-4: ontology import / export is all-or-nothing and never writes directly. */
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import type {
  DesktopBridge,
  OntologyTurtleExportResultDTO,
  OntologyTurtleImportCheckResultDTO,
} from '@ontolearn/contracts'

// The unit program does not include the renderer's `env.d.ts`; the same
// optional bridge declaration is repeated here so the real renderer modules
// keep their exact types under `npm run typecheck:unit`.
declare global {
  interface Window {
    ontolearn?: DesktopBridge
  }
}
import {
  ImportExportPanel,
  downloadTurtle,
  exportOutcome,
  importBaseUri,
  importOutcome,
  importPlanToChangePlan,
} from '../../apps/desktop/src/renderer/src/ontology/import-export-panel'

const exportOk: OntologyTurtleExportResultDTO = {
  status: 'ok',
  turtle: '@prefix ex: <urn:example#> .',
  tripleCount: 42,
  inputSnapshotId: 'snapshot-1',
  projectRevision: 7,
}
const exportRejected: OntologyTurtleExportResultDTO = {
  status: 'rejected',
  reasons: [
    {
      code: 'UNSUPPORTED_OWL',
      field: 'definition:urn:Equipment',
      detail: 'OWL 语义超出当前导出能力边界。',
    },
  ],
}
const importOk: OntologyTurtleImportCheckResultDTO = {
  status: 'ok',
  summary: {
    baseRevision: 7,
    inputSnapshotId: 'snapshot-1',
    tripleCount: 12,
    definitionCount: 2,
    manualFactCount: 1,
  },
  plan: {
    definitions: [
      {
        layer: 'ontology',
        id: 'urn:Equipment',
        value: {
          triples: [{ subject: 'urn:Equipment', predicate: 'rdf:type', object: 'owl:Class' }],
        },
      },
    ],
    manual: [{ id: 'f1', subject: 'urn:Pump', predicate: 'urn:partOf', object: '<urn:Equipment>' }],
  },
}
const importRejected: OntologyTurtleImportCheckResultDTO = {
  status: 'rejected',
  reasons: [
    {
      code: 'UNSUPPORTED_SHACL',
      field: 'shape:urn:Shape',
      detail: 'SHACL 形状超出当前导入能力边界。',
    },
  ],
}
const importInvalid: OntologyTurtleImportCheckResultDTO = {
  status: 'invalid',
  reasons: [{ code: 'INVALID_TURTLE', field: 'document', detail: '第 3 行缺少语句结束符。' }],
}

describe('W3b S2-4: export only ever publishes the committed state', () => {
  it('reports the committed snapshot facts for a successful export', () => {
    expect(exportOutcome(exportOk)).toEqual({
      status: 'ok',
      tripleCount: 42,
      inputSnapshotId: 'snapshot-1',
      projectRevision: 7,
    })
  })

  it('reports a whole-batch rejection instead of a partial file', () => {
    const outcome = exportOutcome(exportRejected)
    expect(outcome.status).toBe('rejected')
    expect(outcome.status === 'rejected' && outcome.reasons).toHaveLength(1)
    expect(outcome.status === 'rejected' && outcome.reasons[0]!.code).toBe('UNSUPPORTED_OWL')
  })

  it('never pretends a file was written when no DOM is available', () => {
    expect(downloadTurtle('@prefix ex: <urn:example#> .', 'ontology.ttl')).toBe(false)
  })
})

describe('W3b S2-4: import check results stay distinguishable', () => {
  it('keeps a successful check with its real summary', () => {
    const outcome = importOutcome(importOk)
    expect(outcome.status).toBe('ok')
    expect(outcome.status === 'ok' && outcome.summary.tripleCount).toBe(12)
    expect(outcome.status === 'ok' && outcome.summary.definitionCount).toBe(2)
    expect(outcome.status === 'ok' && outcome.summary.manualFactCount).toBe(1)
    expect(outcome.status === 'ok' && outcome.summary.baseRevision).toBe(7)
  })

  it('separates an out-of-boundary rejection from a syntax error', () => {
    expect(importOutcome(importRejected).status).toBe('rejected')
    expect(importOutcome(importInvalid).status).toBe('invalid')
    expect(importOutcome(importRejected)).not.toEqual(importOutcome(importInvalid))
  })

  it('carries only the supported sections into the change plan', () => {
    const plan = importPlanToChangePlan(importOk.plan)
    expect(plan.definitions).toHaveLength(1)
    expect(plan.manual).toHaveLength(1)
    expect(Object.keys(plan).sort()).toEqual(['definitions', 'manual'])
    const empty = importPlanToChangePlan({})
    expect(Object.keys(empty)).toEqual([])
  })

  it('binds the import base IRI to the selected project', () => {
    expect(importBaseUri('p1')).toBe('urn:ontolearn:project:p1')
    expect(importBaseUri(null)).toBe('urn:ontolearn:project:local')
  })
})

describe('W3b S2-4: import / export panel presentation', () => {
  const render = (projectId: string | null) =>
    renderToStaticMarkup(
      createElement(ImportExportPanel, { projectId, projectRevision: projectId ? 7 : null }),
    )

  it('states that the export contains the committed state only', () => {
    const html = render('p1')
    expect(html).toContain('data-testid="ontology-import-export"')
    expect(html).toContain('导出仅包含当前已提交态（不含未提交草稿）')
  })

  it('keeps the export and the import disabled while no project is selected', () => {
    const html = render(null)
    expect(html).toMatch(/data-testid="ontology-export-button" disabled/)
    expect(html).toMatch(/data-testid="ontology-import-file" disabled/)
    expect(html).toContain('尚未读取当前项目版本')
  })

  it('offers the export and the import for a selected project', () => {
    const html = render('p1')
    expect(html).toContain('data-testid="ontology-export-button"')
    expect(html).toContain('data-testid="ontology-import-file"')
    expect(html).not.toMatch(/data-testid="ontology-export-button" disabled/)
  })

  it('never shows a result or a commit control before a file was checked', () => {
    const html = render('p1')
    expect(html).not.toContain('data-testid="ontology-import-check-result"')
    expect(html).not.toContain('data-testid="ontology-import-commit"')
    expect(html).not.toContain('data-testid="ontology-import-rejection-')
  })
})
