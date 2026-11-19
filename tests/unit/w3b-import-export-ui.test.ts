/** W3b S2-4: ontology import / export is all-or-nothing and never writes directly. */
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import ts from 'typescript'
import { describe, expect, it, vi } from 'vitest'
import * as contracts from '@ontolearn/contracts'
import type {
  ChangeSetConfirmation,
  ChangeSetManifest,
  ChangeSetPage,
  ChangeSetPreview,
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
  commitVerifiedImport,
  confirmationMatchesPreview,
  downloadTurtle,
  exportOutcome,
  importBaseUri,
  importOutcome,
  importPlanToChangePlan,
  prepareVerifiedImport,
  readFullDiffPages,
  type VerifiedImportPreview,
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

  it('keeps both controls disabled while the project version was not read yet', () => {
    const html = renderToStaticMarkup(
      createElement(ImportExportPanel, { projectId: 'p1', projectRevision: null }),
    )
    expect(html).toMatch(/data-testid="ontology-export-button" disabled/)
    expect(html).toMatch(/data-testid="ontology-import-file" disabled/)
    expect(html).toContain('尚未读取当前项目版本；导入与导出均已禁用。')
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

/* --------------------------------------------------------------------------
 * B01: the consent must bind the very difference the user actually saw.
 * ----------------------------------------------------------------------- */

const hash = (value: Uint8Array) => createHash('sha256').update(value).digest('hex')
const projectId = '00000000-0000-4000-8000-000000000001'
const previewHash = 'b'.repeat(64)
const rows = [
  {
    resource: ['fact', 'f1'],
    before: null,
    after: { subject: 'urn:Pump', predicate: 'urn:partOf', object: '<urn:Equipment>' },
  },
]

function diffFixture(): { manifest: ChangeSetManifest; page: ChangeSetPage } {
  const raw = Buffer.from(JSON.stringify(rows), 'utf8')
  const segment = {
    ordinal: 0,
    byteOffset: 0,
    rawByteLength: raw.length,
    sha256: hash(raw),
    dataBase64: raw.toString('base64'),
  }
  const manifest: ChangeSetManifest = {
    documentKind: 'diff',
    documentHash: hash(raw),
    totalBytes: raw.length,
    segmentCount: 1,
    segments: [
      {
        ordinal: segment.ordinal,
        byteOffset: segment.byteOffset,
        rawByteLength: segment.rawByteLength,
        sha256: segment.sha256,
      },
    ],
  }
  return {
    manifest,
    page: {
      projectId,
      previewHash,
      documentKind: 'diff',
      documentHash: manifest.documentHash,
      segments: [segment],
      nextCursor: '00000000-0000-4000-8000-000000000004',
      complete: true,
    },
  }
}

const { manifest, page } = diffFixture()
const previewReady: ChangeSetPreview = {
  status: 'ready',
  projectId,
  baseRevision: 7,
  previewHash,
  preparedPlanRef: 'prepared-plan-1',
  inputSnapshotId: 'snapshot-1',
  parametersHash: 'c'.repeat(64),
  intent: 'change',
  targetOperationId: null,
  summary: '导入 1 项事实',
  manifest,
}
const confirmation: ChangeSetConfirmation = {
  projectId,
  previewHash,
  preparedPlanRef: 'prepared-plan-1',
  confirmationRef: '00000000-0000-4000-8000-000000000006',
  inputSnapshotId: 'snapshot-1',
  parametersHash: 'c'.repeat(64),
}

type BridgeLog = {
  preview: number
  pages: number
  confirm: number
  commit: number
  confirmArgs: { previewHash: string; completionCursor: string } | undefined
  commitArgs: { operationId: string; confirmation: ChangeSetConfirmation } | undefined
}

function bridgeFixture(overrides: Record<string, unknown> = {}) {
  const log: BridgeLog = {
    preview: 0,
    pages: 0,
    confirm: 0,
    commit: 0,
    confirmArgs: undefined,
    commitArgs: undefined,
  }
  const bridge = {
    previewProjectChangeset: async () => {
      log.preview++
      return { ok: true as const, data: previewReady }
    },
    getProjectDiffPage: async () => {
      log.pages++
      return { ok: true as const, data: page }
    },
    confirmProjectChangeset: async (args: { previewHash: string; completionCursor: string }) => {
      log.confirm++
      log.confirmArgs = args
      return { ok: true as const, data: confirmation }
    },
    commitProjectChangeSet: async (args: {
      operationId: string
      confirmation: ChangeSetConfirmation
    }) => {
      log.commit++
      log.commitArgs = args
      return { ok: true as const, data: {} }
    },
    ...overrides,
  }
  return { bridge, log }
}

describe('W3b B01: the verified preview is the only thing the commit may act on', () => {
  it('verifies the whole diff once and keeps every identity field of that preview', async () => {
    const { bridge, log } = bridgeFixture()
    const outcome = await prepareVerifiedImport({
      bridge,
      projectId,
      baseRevision: 7,
      plan: importPlanToChangePlan(importOk.plan),
      reqSeq: 3,
      isCurrent: () => true,
    })
    expect(outcome.status).toBe('ready')
    if (outcome.status !== 'ready') return
    expect(log.preview).toBe(1)
    expect(log.pages).toBe(1)
    expect(outcome.preview.previewHash).toBe(previewHash)
    expect(outcome.preview.preparedPlanRef).toBe('prepared-plan-1')
    expect(outcome.preview.inputSnapshotId).toBe('snapshot-1')
    expect(outcome.preview.parametersHash).toBe('c'.repeat(64))
    expect(outcome.preview.baseRevision).toBe(7)
    expect(outcome.preview.reqSeq).toBe(3)
    expect(outcome.preview.rows).toEqual(rows)
    expect(outcome.preview.completionCursor).toBe(page.nextCursor)
    expect(outcome.preview.operationId).toBeTruthy()
  })

  it('commits the very preview the user checked without re-previewing or re-paging', async () => {
    const { bridge, log } = bridgeFixture()
    const prepared = await prepareVerifiedImport({
      bridge,
      projectId,
      baseRevision: 7,
      plan: importPlanToChangePlan(importOk.plan),
      reqSeq: 1,
      isCurrent: () => true,
    })
    expect(prepared.status).toBe('ready')
    if (prepared.status !== 'ready') return
    const before = log.preview + log.pages
    const outcome = await commitVerifiedImport({
      bridge,
      verified: prepared.preview,
      isCurrent: () => true,
    })
    expect(outcome.status).toBe('committed')
    // The commit never rebuilds the preview and never pages the diff again.
    expect(log.preview + log.pages).toBe(before)
    expect(log.confirm).toBe(1)
    expect(log.confirmArgs?.previewHash).toBe(previewHash)
    expect(log.confirmArgs?.completionCursor).toBe(prepared.preview.completionCursor)
    expect(log.commit).toBe(1)
    expect(log.commitArgs?.operationId).toBe(prepared.preview.operationId)
    expect(log.commitArgs?.confirmation.previewHash).toBe(previewHash)
  })

  it('refuses a confirmation that describes another identity', async () => {
    const { bridge, log } = bridgeFixture({
      confirmProjectChangeset: async () => ({
        ok: true as const,
        data: { ...confirmation, parametersHash: 'd'.repeat(64) },
      }),
    })
    const prepared = await prepareVerifiedImport({
      bridge,
      projectId,
      baseRevision: 7,
      plan: importPlanToChangePlan(importOk.plan),
      reqSeq: 1,
      isCurrent: () => true,
    })
    if (prepared.status !== 'ready') throw new Error('expected a verified preview')
    await expect(
      commitVerifiedImport({ bridge, verified: prepared.preview, isCurrent: () => true }),
    ).rejects.toThrow('INVALID_CONFIRMATION')
    expect(log.commit).toBe(0)
  })

  it('never commits an outdated request', async () => {
    const { bridge, log } = bridgeFixture()
    const prepared = await prepareVerifiedImport({
      bridge,
      projectId,
      baseRevision: 7,
      plan: importPlanToChangePlan(importOk.plan),
      reqSeq: 1,
      isCurrent: () => true,
    })
    if (prepared.status !== 'ready') throw new Error('expected a verified preview')
    const outcome = await commitVerifiedImport({
      bridge,
      verified: prepared.preview,
      isCurrent: () => false,
    })
    expect(outcome.status).toBe('stale')
    expect(log.commit).toBe(0)
  })

  it('drops a preview whose request is no longer the current one', async () => {
    const { bridge, log } = bridgeFixture()
    const outcome = await prepareVerifiedImport({
      bridge,
      projectId,
      baseRevision: 7,
      plan: importPlanToChangePlan(importOk.plan),
      reqSeq: 1,
      isCurrent: () => false,
    })
    expect(outcome.status).toBe('stale')
    expect(log.pages).toBe(0)
  })

  it('refuses a diff pagination that repeats its cursor', async () => {
    const { bridge } = bridgeFixture({
      getProjectDiffPage: async () => ({
        ok: true as const,
        data: { ...page, complete: false },
      }),
    })
    await expect(readFullDiffPages(bridge, previewHash)).rejects.toThrow('CURSOR_REPEATED')
  })

  it('compares all five identity fields of the confirmation', () => {
    const verified = {
      projectId,
      previewHash,
      preparedPlanRef: 'prepared-plan-1',
      inputSnapshotId: 'snapshot-1',
      parametersHash: 'c'.repeat(64),
    }
    expect(confirmationMatchesPreview(confirmation, verified)).toBe(true)
    for (const field of [
      'projectId',
      'previewHash',
      'preparedPlanRef',
      'inputSnapshotId',
      'parametersHash',
    ] as const)
      expect(confirmationMatchesPreview({ ...confirmation, [field]: 'other' }, verified)).toBe(
        false,
      )
  })
})

/* --------------------------------------------------------------------------
 * The rendered panel: the row by row difference must be visible before the
 * consent, and a new file must retire the previous verification.
 * ----------------------------------------------------------------------- */

type Node = { type: unknown; props: Record<string, unknown> }

function nodes(value: unknown): Node[] {
  if (Array.isArray(value)) return value.flatMap((item) => nodes(item))
  if (!value || typeof value !== 'object' || !('type' in value)) return []
  const node = value as Node
  return [node, ...nodes(node.props.children)]
}

function textOf(value: unknown): string {
  if (Array.isArray(value)) return value.map(textOf).join('')
  if (value && typeof value === 'object' && 'props' in value)
    return textOf((value as Node).props.children)
  return typeof value === 'string' || typeof value === 'number' ? String(value) : ''
}

const flush = () => new Promise((resolve) => setTimeout(resolve, 0))
// The contract verifier hashes the document with the platform digest; a few
// macrotask turns are enough for the whole chain to settle.
const flushAll = async () => {
  for (let turn = 0; turn < 12; turn++) await flush()
}

function panelHarness() {
  const slots: unknown[] = []
  const effects: Array<{ deps: unknown[] }> = []
  const pending: Array<() => void> = []
  let cursor = 0
  const sameDeps = (left: unknown[], right: unknown[]) =>
    left.length === right.length && left.every((value, index) => Object.is(value, right[index]))
  const hooks = {
    useState: (initial: unknown) => {
      const index = cursor++
      if (!(index in slots))
        slots[index] = typeof initial === 'function' ? (initial as () => unknown)() : initial
      return [
        slots[index],
        (value: unknown) => {
          slots[index] =
            typeof value === 'function' ? (value as (old: unknown) => unknown)(slots[index]) : value
        },
      ]
    },
    useRef: (value: unknown) => {
      const index = cursor++
      if (!(index in slots)) slots[index] = { current: value }
      return slots[index]
    },
    useMemo: (callback: () => unknown) => callback(),
    useCallback: (callback: unknown, deps: unknown[] = []) => {
      const index = cursor++
      const slot = slots[index] as { deps: unknown[]; value: unknown } | undefined
      if (!slot || !sameDeps(slot.deps, deps)) slots[index] = { deps, value: callback }
      return (slots[index] as { value: unknown }).value
    },
    useEffect: (callback: () => void | (() => void), deps: unknown[] = []) => {
      const index = cursor++
      const previous = effects[index]
      if (previous && sameDeps(previous.deps, deps)) return
      effects[index] = { deps }
      pending.push(() => {
        callback()
      })
    },
    useLayoutEffect: (callback: () => void | (() => void)) => {
      callback()
    },
  }
  const jsx = (type: unknown, props: Record<string, unknown>) => ({ type, props })
  const code = ts.transpileModule(
    readFileSync('apps/desktop/src/renderer/src/ontology/import-export-panel.tsx', 'utf8'),
    {
      compilerOptions: {
        target: ts.ScriptTarget.ES2022,
        module: ts.ModuleKind.CommonJS,
        jsx: ts.JsxEmit.ReactJSX,
      },
    },
  ).outputText
  const exported: Record<string, unknown> = {}
  new Function('require', 'exports', code)((name: string) => {
    if (name === 'react') return hooks
    if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx }
    if (name === '@ontolearn/contracts') return contracts
    throw Error(`Unexpected renderer dependency ${name}`)
  }, exported)
  const Component = exported.ImportExportPanel as unknown as (
    props: Record<string, unknown>,
  ) => Node
  let props: Record<string, unknown> = { projectId, projectRevision: 7 }
  let tree: Node
  function render() {
    cursor = 0
    tree = Component(props)
    for (const callback of pending.splice(0)) callback()
  }
  render()
  return {
    render,
    setProps(next: Record<string, unknown>) {
      props = { ...props, ...next }
      render()
    },
    nodes: () => nodes(tree),
    text: () => textOf(tree),
    find: (testId: string) => nodes(tree).find((node) => node.props['data-testid'] === testId),
  }
}

describe('W3b B01: the panel shows the verified difference before it asks for consent', () => {
  it('renders the row by row difference and keeps the commit disabled until consent', async () => {
    const { bridge } = bridgeFixture()
    vi.stubGlobal('window', {
      ontolearn: {
        ...bridge,
        checkProjectOntologyImport: async () => ({ ok: true as const, data: importOk }),
      },
    })
    const panel = panelHarness()
    const input = panel.find('ontology-import-file')!
    const file = { size: 32, text: async () => '@prefix ex: <urn:example#> .' } as unknown as File
    ;(input.props.onChange as (event: unknown) => void)({ target: { files: [file] } })
    await flushAll()
    panel.render()
    const preview = panel.find('ontology-import-preview')!
    ;(preview.props.onClick as () => void)()
    await flushAll()
    panel.render()
    const summary = panel.find('ontology-import-diff-summary')!
    expect(textOf(summary.props.children)).toMatch(/完整差异已核验：[1-9][0-9]* 项/)
    const detail = panel.find('ontology-import-diff-rows')!
    expect(textOf(detail.props.children)).toContain('urn:partOf')
    const commit = panel.find('ontology-import-commit')!
    expect(commit.props.disabled).toBe(true)
    const consent = panel.find('ontology-import-consent')!
    ;(consent.props.onChange as (event: unknown) => void)({ target: { checked: true } })
    panel.render()
    expect(panel.find('ontology-import-commit')!.props.disabled).toBe(false)
    vi.unstubAllGlobals()
  })

  it('retires the verified preview, the summary and the consent when a new file is checked', async () => {
    const { bridge } = bridgeFixture()
    vi.stubGlobal('window', {
      ontolearn: {
        ...bridge,
        checkProjectOntologyImport: async () => ({ ok: true as const, data: importOk }),
      },
    })
    const panel = panelHarness()
    const file = { size: 32, text: async () => '@prefix ex: <urn:example#> .' } as unknown as File
    ;(panel.find('ontology-import-file')!.props.onChange as (event: unknown) => void)({
      target: { files: [file] },
    })
    await flushAll()
    panel.render()
    ;(panel.find('ontology-import-preview')!.props.onClick as () => void)()
    await flushAll()
    panel.render()
    ;(panel.find('ontology-import-consent')!.props.onChange as (event: unknown) => void)({
      target: { checked: true },
    })
    panel.render()
    expect(panel.find('ontology-import-commit')!.props.disabled).toBe(false)
    // A second file starts a new check: the old verification is gone.
    ;(panel.find('ontology-import-file')!.props.onChange as (event: unknown) => void)({
      target: { files: [file] },
    })
    panel.render()
    expect(panel.find('ontology-import-diff-summary')).toBeUndefined()
    expect(panel.find('ontology-import-diff-rows')).toBeUndefined()
    expect(panel.find('ontology-import-commit')).toBeUndefined()
    await flushAll()
    panel.render()
    expect(panel.find('ontology-import-diff-summary')).toBeUndefined()
    expect(panel.find('ontology-import-commit')).toBeUndefined()
    vi.unstubAllGlobals()
  })

  it('retires the verified preview when the project version changes', async () => {
    const { bridge } = bridgeFixture()
    vi.stubGlobal('window', {
      ontolearn: {
        ...bridge,
        checkProjectOntologyImport: async () => ({ ok: true as const, data: importOk }),
      },
    })
    const panel = panelHarness()
    const file = { size: 32, text: async () => '@prefix ex: <urn:example#> .' } as unknown as File
    ;(panel.find('ontology-import-file')!.props.onChange as (event: unknown) => void)({
      target: { files: [file] },
    })
    await flushAll()
    panel.render()
    ;(panel.find('ontology-import-preview')!.props.onClick as () => void)()
    await flushAll()
    panel.render()
    expect(panel.find('ontology-import-diff-rows')).toBeTruthy()
    panel.setProps({ projectRevision: 8 })
    expect(panel.find('ontology-import-diff-rows')).toBeUndefined()
    expect(panel.find('ontology-import-diff-summary')).toBeUndefined()
    expect(panel.find('ontology-import-commit')).toBeUndefined()
    vi.unstubAllGlobals()
  })

  it('rejects an oversized file before it is read', async () => {
    const check = vi.fn()
    vi.stubGlobal('window', {
      ontolearn: {
        ...bridgeFixture().bridge,
        checkProjectOntologyImport: check,
      },
    })
    const panel = panelHarness()
    const file = {
      size: 2 * 1024 * 1024,
      text: async () => {
        throw new Error('the file must not be read')
      },
    } as unknown as File
    ;(panel.find('ontology-import-file')!.props.onChange as (event: unknown) => void)({
      target: { files: [file] },
    })
    await flushAll()
    panel.render()
    expect(check).not.toHaveBeenCalled()
    expect(panel.text()).toContain('文件超过可接受的大小上限')
    vi.unstubAllGlobals()
  })
})

describe('W3b R2c B01: concurrent export/import isolation and per-await ownership', () => {
  it('keeps export and import lifecycles independent when triggered concurrently', async () => {
    let resolveExport!: (value: unknown) => void
    let resolveImportCheck!: (value: unknown) => void
    const { bridge } = bridgeFixture()
    vi.stubGlobal('window', {
      ontolearn: {
        ...bridge,
        exportProjectOntology: () =>
          new Promise((resolve) => {
            resolveExport = resolve
          }),
        checkProjectOntologyImport: () =>
          new Promise((resolve) => {
            resolveImportCheck = resolve
          }),
      },
    })
    const panel = panelHarness()
    ;(panel.find('ontology-export-button')!.props.onClick as () => void)()
    panel.render()
    expect(panel.find('ontology-export-button')!.props.disabled).toBe(true)
    expect(panel.find('ontology-import-file')!.props.disabled).toBe(false)

    const file = { size: 32, text: async () => '@prefix ex: <urn:example#> .' } as unknown as File
    ;(panel.find('ontology-import-file')!.props.onChange as (event: unknown) => void)({
      target: { files: [file] },
    })
    await flush()
    panel.render()
    expect(panel.find('ontology-export-button')!.props.disabled).toBe(true)
    expect(panel.find('ontology-import-file')!.props.disabled).toBe(true)

    resolveImportCheck({ ok: true as const, data: importOk })
    await flushAll()
    panel.render()
    expect(panel.find('ontology-import-file')!.props.disabled).toBe(false)
    expect(panel.find('ontology-export-button')!.props.disabled).toBe(true)
    expect(panel.find('ontology-import-summary')).toBeTruthy()

    resolveExport({
      ok: true as const,
      data: {
        status: 'ok' as const,
        turtle: '@prefix ex: <urn:example#> .',
        tripleCount: 1,
        inputSnapshotId: 'snapshot-1',
        projectRevision: 7,
      },
    })
    await flushAll()
    panel.render()
    expect(panel.find('ontology-export-button')!.props.disabled).toBe(false)
    expect(panel.find('ontology-import-file')!.props.disabled).toBe(false)
    expect(panel.find('ontology-export-summary')).toBeTruthy()
    expect(panel.find('ontology-import-summary')).toBeTruthy()
    vi.unstubAllGlobals()
  })

  it('stops paging diff pages as soon as ownership lapses after page 1', async () => {
    let active = true
    let pageCalls = 0
    const { bridge } = bridgeFixture({
      getProjectDiffPage: async () => {
        pageCalls += 1
        active = false
        return {
          ok: true as const,
          data: {
            ...page,
            complete: false,
            nextCursor: 'cursor-page-2',
          },
        }
      },
    })
    const outcome = await prepareVerifiedImport({
      bridge,
      projectId,
      baseRevision: 7,
      plan: importPlanToChangePlan(importOk.plan),
      reqSeq: 1,
      isCurrent: () => active,
    })
    expect(outcome.status).toBe('stale')
    expect(pageCalls).toBe(1)
  })

  it('ignores a late commit receipt and skips onImported when ownership drops mid-commit', async () => {
    let stillCurrent = true
    const { bridge } = bridgeFixture({
      commitProjectChangeSet: async () => {
        stillCurrent = false
        return { ok: true as const, data: {} }
      },
    })
    const prepared = await prepareVerifiedImport({
      bridge,
      projectId,
      baseRevision: 7,
      plan: importPlanToChangePlan(importOk.plan),
      reqSeq: 1,
      isCurrent: () => true,
    })
    if (prepared.status !== 'ready') throw new Error('expected ready preview')
    const directOutcome = await commitVerifiedImport({
      bridge,
      verified: prepared.preview,
      isCurrent: () => stillCurrent,
    })
    expect(directOutcome.status).toBe('stale')

    let resolveCommit!: (value: unknown) => void
    const onImported = vi.fn()
    const { bridge: panelBridge } = bridgeFixture({
      commitProjectChangeSet: () =>
        new Promise((resolve) => {
          resolveCommit = resolve
        }),
    })
    vi.stubGlobal('window', {
      ontolearn: {
        ...panelBridge,
        checkProjectOntologyImport: async () => ({ ok: true as const, data: importOk }),
      },
    })
    try {
      const panel = panelHarness()
      panel.setProps({ projectId, projectRevision: 7, onImported })
      const file = { size: 32, text: async () => '@prefix ex: <urn:example#> .' } as unknown as File
      ;(panel.find('ontology-import-file')!.props.onChange as (event: unknown) => void)({
        target: { files: [file] },
      })
      await flushAll()
      panel.render()
      ;(panel.find('ontology-import-preview')!.props.onClick as () => void)()
      await flushAll()
      panel.render()
      ;(panel.find('ontology-import-consent')!.props.onChange as (event: unknown) => void)({
        target: { checked: true },
      })
      panel.render()
      ;(panel.find('ontology-import-commit')!.props.onClick as () => void)()
      await flush()
      panel.setProps({ projectId, projectRevision: 8, onImported })
      resolveCommit({ ok: true as const, data: {} })
      await flushAll()
      panel.render()
      expect(onImported).not.toHaveBeenCalled()
    } finally {
      vi.unstubAllGlobals()
    }
  })
})

// Keep the immutable snapshot type honest: it is the committed contract.
const _snapshotShape: VerifiedImportPreview['token'] = 'token'
void _snapshotShape
