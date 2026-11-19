import { createHash } from 'node:crypto'
import { isValidElement, type ReactElement } from 'react'
import { describe, expect, it, vi, afterEach } from 'vitest'
import type {
  ChangeSetManifest,
  ChangeSetPage,
  ChangeSetPreview,
  DesktopBridge,
  HtmlReportPrepareResultDTO,
  JobView,
  MainlineProjectReadDTO,
  MappingBridge,
  MappingDraft,
  MappingPreviewResultDTO,
  MappingSourceSelectResultDTO,
  PackageExportCheckResultDTO,
  PackageImportCheckResultDTO,
  ScenarioBridge,
  ScenarioReadResultDTO,
  ScenarioRunResultDTO,
  ScenarioSummaryDTO,
  TaskUpdate,
  TaskView,
  TransferBridge,
  TransferPublicationReceiptDTO,
} from '@ontolearn/contracts'
import { App } from '../../apps/desktop/src/renderer/src/App'
import { agentContextStore } from '../../apps/desktop/src/renderer/src/agent/agent-context-store'
import { toAgentModule } from '../../apps/desktop/src/renderer/src/agent/context-actions'
import { ConnectedBehaviorWorkspace } from '../../apps/desktop/src/renderer/src/behavior/ConnectedBehaviorWorkspace'
import { BehaviorWorkspace } from '../../apps/desktop/src/renderer/src/behavior/BehaviorWorkspace'
import { MappingPage } from '../../apps/desktop/src/renderer/src/mapping/MappingPage'
import { MappingWorkspace } from '../../apps/desktop/src/renderer/src/mapping/MappingWorkspace'
import { ConnectedScenarioWorkspace } from '../../apps/desktop/src/renderer/src/scenario/ConnectedScenarioWorkspace'
import { ScenarioPage } from '../../apps/desktop/src/renderer/src/scenario/ScenarioPage'
import { TransferPanel } from '../../apps/desktop/src/renderer/src/transfer/TransferPanel'
import {
  PublicationReceipt,
  TransferWorkspace,
} from '../../apps/desktop/src/renderer/src/transfer/TransferWorkspace'
import { LibraryLocationPanel } from '../../apps/desktop/src/renderer/src/project/LibraryLocationPanel'
import fixtures from '../../packages/contracts/v2/fixtures.json'

// Run actual component bodies and event callbacks without a browser or desktop focus.
const react = vi.hoisted(() => ({ hooks: {} as Record<string, (...args: never[]) => unknown> }))
vi.mock('react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react')>()
  return {
    ...actual,
    useState: (...args: never[]) => react.hooks.useState(...args),
    useMemo: (...args: never[]) => react.hooks.useMemo(...args),
    useEffect: (...args: never[]) => react.hooks.useEffect(...args),
    useRef: (...args: never[]) => react.hooks.useRef(...args),
    useCallback: (...args: never[]) => react.hooks.useCallback(...args),
    useSyncExternalStore: (...args: never[]) => react.hooks.useSyncExternalStore(...args),
    useId: () => 'w4-test',
  }
})

type Element = ReactElement<Record<string, unknown>>
const same = (a: unknown[], b: unknown[]) =>
  a.length === b.length && a.every((item, i) => Object.is(item, b[i]))
function tree(value: unknown): Element[] {
  if (Array.isArray(value)) return value.flatMap(tree)
  if (!isValidElement<Record<string, unknown>>(value)) return []
  return [
    value,
    ...tree(value.props.children),
    ...tree(value.props.connected),
    ...(typeof value.props.connected === 'object' && value.props.connected !== null
      ? tree((value.props.connected as { listControls?: unknown }).listControls).concat(
          tree((value.props.connected as { runContent?: unknown }).runContent),
        )
      : []),
  ]
}
function plain(value: unknown): string {
  if (Array.isArray(value)) return value.map(plain).join('')
  if (isValidElement<Record<string, unknown>>(value)) return plain(value.props.children)
  return typeof value === 'string' || typeof value === 'number' ? String(value) : ''
}
function harness<Props>(component: (props: Props) => unknown, props: Props) {
  let index = 0
  const cells: unknown[] = []
  const effects = new Map<number, () => void>()
  const pending: (() => void)[] = []
  let root: unknown
  function memo<T>(compute: () => T, deps: unknown[]): T {
    const slot = index++
    const cached = cells[slot] as { value: T; deps: unknown[] } | undefined
    if (cached && same(cached.deps, deps)) return cached.value
    const value = compute()
    cells[slot] = { value, deps }
    return value
  }
  const hooks = {
    useState<T>(initial: T | (() => T)) {
      const slot = index++
      if (!(slot in cells))
        cells[slot] = typeof initial === 'function' ? (initial as () => T)() : initial
      return [
        cells[slot],
        (value: T | ((previous: T) => T)) => {
          cells[slot] =
            typeof value === 'function' ? (value as (previous: T) => T)(cells[slot] as T) : value
        },
      ]
    },
    useRef<T>(value: T) {
      return memo(() => ({ current: value }), [])
    },
    useMemo: memo,
    useCallback<T>(value: T, deps: unknown[]) {
      return memo(() => value, deps)
    },
    useEffect(effect: () => void | (() => void), deps: unknown[] = []) {
      const slot = index++
      const previous = cells[slot] as unknown[] | undefined
      if (previous && same(previous, deps)) return
      cells[slot] = deps
      pending.push(() => {
        effects.get(slot)?.()
        const dispose = effect()
        if (dispose) effects.set(slot, dispose)
        else effects.delete(slot)
      })
    },
    useSyncExternalStore(_: unknown, snapshot: () => unknown) {
      return snapshot()
    },
  }
  function render() {
    index = 0
    react.hooks = hooks
    root = component(props)
    pending.splice(0).forEach((task) => task())
    return root
  }
  function find(predicate: (node: Element) => boolean) {
    return tree(render()).find(predicate)
  }
  function button(label: string) {
    const node = find(
      (element) => element.type === 'button' && plain(element.props.children) === label,
    )
    if (!node) throw new Error(`Missing button: ${label}`)
    return node
  }
  return {
    render,
    find,
    button,
    click(label: string) {
      const node = button(label)
      expect(node.props.disabled).not.toBe(true)
      ;(node.props.onClick as () => void)()
    },
    unmount() {
      effects.forEach((dispose) => dispose())
      effects.clear()
    },
  }
}

const projectId = '00000000-0000-4000-8000-000000000001'
const selectionId = '00000000-0000-4000-8000-000000000001'
const newProjectId = '00000000-0000-4000-8000-000000000003'
const otherId = '00000000-0000-4000-8000-000000000004'
const inputSnapshotId = 'a'.repeat(64)
const props = { projectId, revision: 0, inputSnapshotId, disabled: false, onStatus: vi.fn() }
const ok = <T>(data: T) => ({ ok: true as const, data })
const err = {
  ok: false as const,
  error: { code: 'INTERNAL_ERROR', messageKey: 'engine.internal', params: {}, retryable: false },
}
const path = '/Users/example/private.csv'

function fixture<T>(method: string): T {
  const entry = fixtures.business3.responses.find(
    ({ name }) => name === `W4 ${method} valid binding`,
  )
  if (!entry || !('result' in entry.response)) throw new Error(`No frozen fixture for ${method}`)
  return structuredClone(entry.response.result) as T
}
function propsOf<Props>(value: Element | undefined) {
  if (!value) throw new Error('Component unavailable')
  return value.props as Props
}
function fieldChange(node: Element | undefined, value: string | boolean) {
  if (!node) throw new Error('Field unavailable')
  ;(
    node.props.onChange as (event: {
      target: { value: string | boolean; checked: boolean }
    }) => void
  )({
    target: { value, checked: value === true },
  })
}

function mappingDiff() {
  const raw = Buffer.from(
    JSON.stringify([{ resource: ['fact', 'f1'], before: null, after: { subject: 'urn:Pump' } }]),
  )
  const sha256 = createHash('sha256').update(raw).digest('hex')
  const metadata = { ordinal: 0, byteOffset: 0, rawByteLength: raw.length, sha256 }
  const manifest: ChangeSetManifest = {
    documentKind: 'diff',
    totalBytes: raw.length,
    segmentCount: 1,
    documentHash: sha256,
    segments: [metadata],
  }
  const previewHash = 'b'.repeat(64)
  const preview: Extract<ChangeSetPreview, { status: 'ready' }> = {
    projectId,
    previewHash,
    baseRevision: 0,
    inputSnapshotId,
    intent: 'change',
    targetOperationId: null,
    manifest,
    parametersHash: 'c'.repeat(64),
    status: 'ready',
    preparedPlanRef: 'd'.repeat(64),
    summary: '新增设备事实',
  }
  const page: ChangeSetPage = {
    projectId,
    previewHash,
    documentKind: 'diff',
    documentHash: sha256,
    complete: true,
    nextCursor: otherId,
    segments: [{ ...metadata, dataBase64: raw.toString('base64') }],
  }
  return { preview, page }
}
const draft: MappingDraft = {
  identity: 'equipment',
  version: 1,
  namespace: 'urn:sample:/',
  classIri: 'urn:Equipment',
  keys: ['id'],
  fields: [],
}
const read: MainlineProjectReadDTO = {
  readVersion: 1,
  workspace: {
    workspaceVersion: 1,
    projectId,
    inputSnapshotId,
    domainRevision: 0,
    metadataVersion: 1,
    operationSequence: 1,
    checkpointRef: inputSnapshotId,
    metadata: {
      name: '运维',
      mode: 'guided',
      archived: false,
      origin: 'created',
      templateRef: null,
    },
    draft: { editor: 'behavior', state: 'missing' },
  },
  projectId,
  inputSnapshotId,
  domain: {
    projectRevision: 0,
    state: { definitions: [], facts: [], mappingState: {} },
    dependencyVector: {},
  },
}

describe('W4 connected mapping workspace', () => {
  it('reparses the opaque selection, saves optimistically, renders conflict and issue evidence and submits the verified ChangeSet', async () => {
    const csv: MappingSourceSelectResultDTO = {
      projectId,
      selectionId,
      fingerprint: inputSnapshotId,
      format: 'csv',
      sheets: ['CSV'],
      sheet: 'CSV',
      encoding: 'utf-8',
      totalRows: 20,
      fields: [{ name: 'id', observedTypes: ['string'], samples: ['001', path] }],
      suggestions: [
        { column: 'id', predicate: 'urn:id', basis: 'exact-field-name', samples: ['001'] },
      ],
    }
    const xlsx: MappingSourceSelectResultDTO = {
      ...csv,
      format: 'xlsx',
      sheets: ['设备', '备件'],
      sheet: '设备',
      encoding: null,
    }
    const { preview, page } = mappingDiff()
    const previewFixture = fixture<MappingPreviewResultDTO>('project.mapping.preview')
    const selectMappingSource = vi
      .fn<MappingBridge['selectMappingSource']>()
      .mockResolvedValueOnce(ok(csv))
      .mockResolvedValueOnce(ok({ ...csv, encoding: 'big5' }))
      .mockResolvedValueOnce(ok(csv))
      .mockResolvedValueOnce(ok(xlsx))
      .mockResolvedValueOnce(ok({ ...xlsx, sheet: '备件' }))
    const previewMapping = vi
      .fn<MappingBridge['previewMapping']>()
      .mockImplementation(async ({ sheet, encoding }) =>
        ok({ ...previewFixture, sheet, encoding, totalRows: 20, identitiesAdded: ['urn:Pump'] }),
      )
    previewMapping.mockImplementationOnce(async ({ sheet, encoding }) =>
      ok({
        ...previewFixture,
        sheet,
        encoding,
        totalRows: 20,
        issues: [
          {
            code: 'EMPTY_KEY',
            messageKey: 'mapping.emptyKey',
            sheet,
            row: 3,
            column: 2,
            field: 'id',
          },
        ],
        conflicts: [
          {
            code: 'MANUAL_DRIFT',
            current: '手工值',
            source: '源值',
            managed: '旧值',
            owner: 'equipment',
            sourceRow: 'row-3',
            subject: 'urn:Pump',
            predicate: 'urn:id',
          },
        ],
      }),
    )
    const commitProjectChangeSet = vi.fn<DesktopBridge['commitProjectChangeSet']>(
      async ({ operationId }) => {
        const job = structuredClone(
          fixtures.cases.find(({ name }) => name === 'atomic succeeded committed')!.value,
        ) as JobView
        return ok({
          ...job,
          capability: 'changeset.commit',
          operationId,
          commitProgress: { ...(job.commitProgress as object), operationId },
        } as JobView)
      },
    )
    const bridge: Parameters<typeof MappingWorkspace>[0]['bridge'] = {
      selectMappingSource,
      readMappingDraft: vi.fn(async ({ mappingId }) =>
        ok({ projectId, mappingId, generation: 3, baseRevision: 0, draft }),
      ),
      saveMappingDraft: vi.fn(async (args) =>
        ok({
          projectId,
          operationId: args.operationId,
          generation: 4,
          baseRevision: 0,
          draft: args.draft,
        }),
      ),
      previewMapping,
      prepareMappingCommit: vi.fn(async (args) =>
        ok({
          ...args,
          projectId,
          plan: {
            mappingPreparation: { resultId: args.resultId, preparationRef: inputSnapshotId },
          },
        }),
      ),
      readProject: vi.fn(async () => ok(read)),
      previewProjectChangeset: vi.fn(async () => ok(preview)),
      getProjectDiffPage: vi.fn(async () => ok(page)),
      confirmProjectChangeset: vi.fn(async () =>
        ok({
          projectId,
          previewHash: preview.previewHash,
          preparedPlanRef: preview.preparedPlanRef,
          inputSnapshotId,
          parametersHash: preview.parametersHash,
          confirmationRef: otherId,
        }),
      ),
      commitProjectChangeSet,
      getJob: vi.fn(),
      restoreTasks: vi.fn(),
    }
    const onCommitted = vi.fn(async () => {})
    const h = harness(MappingWorkspace, { ...props, bridge, onCommitted })
    const mapping = () =>
      propsOf<Parameters<typeof MappingPage>[0]>(h.find((node) => node.type === MappingPage))
    mapping().onChooseSource!('utf-8-sig')
    await vi.waitFor(() => expect(mapping().state.source?.encoding).toBe('utf-8'))
    expect(selectMappingSource).toHaveBeenNthCalledWith(1, {})
    expect(JSON.stringify(mapping().state.source)).not.toContain(path)
    mapping().chooser!.onReparse(undefined, 'big5')
    await vi.waitFor(() => expect(mapping().state.source?.encoding).toBe('big5'))
    mapping().chooser!.onReparse(undefined, 'utf-8-sig')
    await vi.waitFor(() => expect(mapping().state.source?.encoding).toBe('utf-8'))
    expect(selectMappingSource).toHaveBeenNthCalledWith(3, {
      selectionId,
      sheet: 'CSV',
      encoding: 'utf-8',
    })
    mapping().onChooseSource!('utf-8')
    await vi.waitFor(() => expect(mapping().state.source?.sheet).toBe('设备'))
    mapping().chooser!.onReparse('备件')
    await vi.waitFor(() => expect(mapping().state.source?.sheet).toBe('备件'))
    expect(selectMappingSource).toHaveBeenNthCalledWith(5, {
      selectionId,
      sheet: '备件',
      encoding: null,
    })
    fieldChange(
      h.find((node) => node.type === 'input' && node.props.value === ''),
      'equipment',
    )
    h.click('读取草稿')
    await vi.waitFor(() => expect(mapping().state.draft).toEqual(draft))
    mapping().onDraft({ ...draft, version: 2 })
    h.click('保存草稿')
    await vi.waitFor(() =>
      expect(bridge.saveMappingDraft).toHaveBeenCalledWith(
        expect.objectContaining({ expectedGeneration: 3, draft: { ...draft, version: 2 } }),
      ),
    )
    await vi.waitFor(() => expect(mapping().busy).toBe(false))
    mapping().onPreview!()
    await vi.waitFor(() => expect(mapping().state.preview?.issues[0]?.code).toBe('业务主键为空'))
    const pageUi = harness(MappingPage, mapping())
    const text = plain(pageUi.render())
    expect(text).toContain('手工值')
    expect(text).toContain('row-3')
    expect(text).toContain('备件 第 3 行、第 2 列（id')
    expect(pageUi.button('检查正式变更').props.disabled).toBe(true)
    mapping().onPreview!()
    await vi.waitFor(() => expect(mapping().state.preview?.conflicts).toEqual([]))
    mapping().onPrepareCommit!(previewFixture.resultId)
    await vi.waitFor(() => expect(h.button('提交映射 ChangeSet').props.disabled).toBe(true))
    expect(bridge.confirmProjectChangeset).not.toHaveBeenCalled()
    expect(bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(bridge.previewProjectChangeset).toHaveBeenCalledWith(
      expect.objectContaining({
        intent: 'change',
        plan: {
          mappingPreparation: {
            resultId: previewFixture.resultId,
            preparationRef: inputSnapshotId,
          },
        },
      }),
    )
    const confirm = h.find((node) => node.type === 'input' && node.props.type === 'checkbox')
    fieldChange(confirm, true)
    h.click('提交映射 ChangeSet')
    await vi.waitFor(() => expect(onCommitted).toHaveBeenCalledOnce())
    expect(bridge.getProjectDiffPage).toHaveBeenCalledWith(
      expect.objectContaining({ previewHash: preview.previewHash, cursor: null }),
    )
  })
})

describe('W4 connected transfer workspace', () => {
  function transferBridge() {
    const exportCheck = fixture<PackageExportCheckResultDTO>(
      'project.transfer.package.export.check',
    )
    const importCheck = fixture<PackageImportCheckResultDTO>(
      'project.transfer.package.import.check',
    )
    let report = fixture<HtmlReportPrepareResultDTO>('project.transfer.report.prepare')
    report = {
      ...report,
      credentialScan: { version: 1, status: 'redacted' },
      report: {
        ...report.report,
        title: '<b>设备</b>',
        goals: [path, '建立设备体系'],
        learning: [
          {
            taskId: 'transfer',
            attemptId: 'attempt-1',
            transferTask: true,
            operationCompleted: true,
            hint: 'none',
            agentAssistance: 'none',
            check: { status: 'passed', evidenceRef: 'evidence-1', summary: '校验通过' },
            stageOutcomes: ['通过'],
            independentTransferSuccess: true,
          },
        ],
      },
    }
    const publication: TransferPublicationReceiptDTO = {
      state: 'publication-unconfirmed',
      sha256: inputSnapshotId,
      byteLength: 12,
      cleanup: 'pending',
    }
    return {
      selectTransferFile: vi.fn<TransferBridge['selectTransferFile']>(async ({ purpose }) =>
        ok(
          purpose === 'report-html'
            ? { projectId, selectionId, purpose, extension: '.html' }
            : { projectId, selectionId, purpose, extension: '.ontolearn.zip' },
        ),
      ),
      checkProjectPackageExport: vi.fn<TransferBridge['checkProjectPackageExport']>(async (args) =>
        ok({
          ...exportCheck,
          ...args,
          manifest: {
            ...exportCheck.manifest,
            kind: args.kind,
            options: args.options,
            files:
              args.kind === 'full'
                ? exportCheck.manifest.files
                : exportCheck.manifest.files.slice(0, 1),
          },
          portability: { ...exportCheck.portability, restoreCurrent: args.kind === 'full' },
        }),
      ),
      exportProjectPackage: vi.fn<TransferBridge['exportProjectPackage']>(async (args) =>
        ok({ projectId, ...args, kind: 'template', publication }),
      ),
      checkProjectPackageImport: vi
        .fn<TransferBridge['checkProjectPackageImport']>()
        .mockResolvedValueOnce(
          ok({
            projectId,
            selectionId,
            expectedKind: 'full',
            status: 'rejected',
            reason: 'reader-too-old',
          }),
        )
        .mockResolvedValueOnce(ok(importCheck)),
      importProjectPackage: vi
        .fn<TransferBridge['importProjectPackage']>(async (args) =>
          ok({
            ...args,
            projectId,
            kind: args.expectedKind,
            importedProjectId: newProjectId,
            conflictPolicy: exportCheck.conflictPolicy,
          }),
        )
        .mockImplementation(async ({ expectedKind, ...args }) =>
          ok({
            ...args,
            projectId,
            kind: expectedKind,
            importedProjectId: newProjectId,
            conflictPolicy: exportCheck.conflictPolicy,
          }),
        ),
      prepareProjectHtmlReport: vi.fn<TransferBridge['prepareProjectHtmlReport']>(async () =>
        ok(report),
      ),
      exportProjectHtmlReport: vi.fn<TransferBridge['exportProjectHtmlReport']>(async (args) =>
        ok({
          ...args,
          projectId,
          credentialScan: report.credentialScan,
          format: 'html',
          publication: {
            state: 'published',
            cleanup: 'complete',
            durability: 'confirmed',
            sha256: inputSnapshotId,
            byteLength: 12,
            postPublicationError: false,
          },
        }),
      ),
    } satisfies TransferBridge
  }
  it('checks scope and manifest before writes, blocks an unconfirmed retry and uses the checked package and report references', async () => {
    const bridge = transferBridge()
    const onImported = vi.fn(async () => {})
    const h = harness(TransferWorkspace, { ...props, bridge, onImported })
    const container = () =>
      propsOf<Parameters<typeof TransferPanel>[0]>(h.find((node) => node.type === TransferPanel))
    expect(
      tree(container().connected)
        .filter((node) => node.type === 'input' && node.props.type === 'checkbox')
        .map((node) => node.props.checked),
    ).toEqual([false, false, false, false])
    h.click('选择目标并检查项目包')
    await vi.waitFor(() =>
      expect(
        h.find((node) => node.type === 'button' && plain(node.props.children) === '确认导出项目包'),
      ).toBeDefined(),
    )
    expect(bridge.checkProjectPackageExport).toHaveBeenCalledWith({
      baseRevision: 0,
      kind: 'full',
      selectionId,
      options: { agentSessions: false, rawSources: false, derived: false, history: false },
    })
    fieldChange(
      h.find((node) => node.type === 'select'),
      'template',
    )
    expect(
      h.find((node) => node.type === 'button' && plain(node.props.children) === '确认导出项目包'),
    ).toBeUndefined()
    h.click('选择目标并检查项目包')
    await vi.waitFor(() =>
      expect(
        h.find((node) => node.type === 'button' && plain(node.props.children) === '确认导出项目包'),
      ).toBeDefined(),
    )
    h.click('确认导出项目包')
    await vi.waitFor(() =>
      expect(h.find((node) => node.type === PublicationReceipt)?.props.value).toMatchObject({
        state: 'publication-unconfirmed',
      }),
    )
    expect(
      tree(container().connected)
        .filter((node) => node.type === 'fieldset')
        .every((node) => node.props.disabled),
    ).toBe(true)
    h.click('已人工核对，解除写入锁定')
    h.click('选择并检查待导入项目包')
    await vi.waitFor(() => expect(plain(container().connected)).toContain('reader-too-old'))
    expect(bridge.importProjectPackage).not.toHaveBeenCalled()
    h.click('选择并检查待导入项目包')
    await vi.waitFor(() =>
      expect(
        h.find(
          (node) => node.type === 'button' && plain(node.props.children) === '确认导入为新项目',
        ),
      ).toBeDefined(),
    )
    h.click('确认导入为新项目')
    await vi.waitFor(() => expect(plain(container().connected)).toContain(newProjectId))
    expect(bridge.importProjectPackage).toHaveBeenCalledWith(
      expect.objectContaining({
        selectionId,
        expectedKind: 'full',
        packageSha256: inputSnapshotId,
      }),
    )
    expect(onImported).toHaveBeenCalledOnce()
    h.click('准备并预览 HTML 报告')
    await vi.waitFor(() =>
      expect(
        h.find(
          (node) =>
            node.type === 'button' && plain(node.props.children) === '选择目标并导出 HTML 报告',
        ),
      ).toBeDefined(),
    )
    const reportNode = tree(container().connected).find(
      (node) => typeof node.type === 'function' && node.type.name === 'ReportPreview',
    )!
    const reportUi = (reportNode.type as (value: typeof reportNode.props) => Element)(
      reportNode.props,
    )
    expect(plain(reportUi)).toContain('<b>设备</b>')
    expect(plain(reportUi)).toContain('独立迁移通过')
    expect(plain(reportUi)).toContain('redacted')
    expect(plain(reportUi)).not.toContain(path)
    expect(
      tree(reportUi).some(
        (node) =>
          node.type === 'b' || node.type === 'iframe' || 'dangerouslySetInnerHTML' in node.props,
      ),
    ).toBe(false)
    h.click('选择目标并导出 HTML 报告')
    await vi.waitFor(() =>
      expect(h.find((node) => node.type === PublicationReceipt)?.props.value).toMatchObject({
        state: 'published',
      }),
    )
    expect(bridge.exportProjectHtmlReport).toHaveBeenCalledWith(
      expect.objectContaining({ selectionId, reportRef: inputSnapshotId, baseRevision: 0 }),
    )
  })
  it.each([
    [{ state: 'cancelled', cleanup: 'complete' }, '已取消写入'],
    [{ state: 'failed', cleanup: 'complete', code: 'target-exists' }, '目标已存在'],
  ] satisfies Array<[TransferPublicationReceiptDTO, string]>)(
    'shows the persisted receipt %j',
    (value, label) => {
      expect(plain(PublicationReceipt({ value }))).toContain(label)
    },
  )
})

describe('W4 scenario and behavior rendering', () => {
  it('reads a selected scenario and its persisted run, then exposes committed round evidence', async () => {
    const started = fixture<ScenarioRunResultDTO>('project.scenario.run')
    const scenario: ScenarioSummaryDTO = fixture<{ scenario: ScenarioSummaryDTO }>(
      'project.scenario.create',
    ).scenario
    const detail: ScenarioReadResultDTO = {
      projectId,
      scenario,
      runs: [{ runId: started.run.runId, status: 'queued', lastCommittedRound: 0 }],
    }
    const bridge: ScenarioBridge = {
      listScenarios: vi.fn(async () => ok({ projectId, items: [scenario], nextCursor: otherId })),
      readScenario: vi.fn(async () => ok(detail)),
      readScenarioRun: vi.fn(async () => ok({ projectId, run: started.run })),
      createScenario: vi.fn(),
      copyScenario: vi.fn(),
      cancelScenarioRun: vi.fn(),
      startScenarioRun: vi.fn(),
      resumeScenarioRun: vi.fn(),
      compareScenarioRuns: vi.fn(),
      deleteScenarioRun: vi.fn(),
      restoreScenarioBaseline: vi.fn(),
    }
    const h = harness(ConnectedScenarioWorkspace, { ...props, bridge })
    const page = () =>
      propsOf<Parameters<typeof ScenarioPage>[0]>(h.find((node) => node.type === ScenarioPage))
    await vi.waitFor(() => expect(page().scenarios).toHaveLength(1))
    page().connected!.onSelect(scenario.identity.scenarioId)
    await vi.waitFor(() => expect(plain(page().connected!.runContent)).toContain('刷新运行列表'))
    h.click(`读取运行 ${started.run.runId} · queued · 已提交 0 轮`)
    await vi.waitFor(() => expect(h.button('请求取消运行').props.disabled).toBe(false))
    expect(h.button('从最后提交检查点显式续跑').props.disabled).toBe(true)
    expect(h.button('加入运行对比').props.disabled).toBe(true)
    expect(bridge.readScenarioRun).toHaveBeenCalledWith({
      runId: started.run.runId,
      scenarioId: scenario.identity.scenarioId,
      roundOffset: 0,
      limit: 5,
    })
  })

  it('binds the behavior editor to an actual snapshot and opens versioned event controls', async () => {
    const bridge = { readProject: vi.fn(async () => ok(read)) } as unknown as DesktopBridge
    const h = harness(ConnectedBehaviorWorkspace, { ...props, bridge })
    const editor = () =>
      propsOf<Parameters<typeof BehaviorWorkspace>[0]>(
        h.find((node) => node.type === BehaviorWorkspace),
      )
    await vi.waitFor(() => expect(h.find((node) => node.type === BehaviorWorkspace)).toBeDefined())
    expect(editor().context).toMatchObject({ projectId, inputVersion: inputSnapshotId })
    expect(bridge.readProject).toHaveBeenCalledWith({ editor: 'behavior' })
    const workspace = harness(BehaviorWorkspace, editor())
    expect(workspace.find((node) => node.props.label === '触发事件 ID（可选）')).toBeDefined()
    expect(workspace.find((node) => node.props.label === '事件版本')).toBeDefined()
  })
})

describe('W4 App workspace navigation', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    agentContextStore.setModule('query')
  })
  const view: TaskView = {
    generation: 2,
    project: {
      projectId,
      inputSnapshotId,
      projectRevision: 0,
      dependencyVector: {},
      formatVersion: 3,
    },
    jobs: [],
  }
  function appBridge(extra: Record<string, unknown> = {}) {
    const listeners = new Set<(event: TaskUpdate) => void>()
    const bridge = {
      restoreTasks: vi.fn(async () => ok(view)),
      onTaskUpdate: (listener: (event: TaskUpdate) => void) => {
        listeners.add(listener)
        return () => listeners.delete(listener)
      },
      getLibraryLocation: vi.fn(),
      ...extra,
    }
    vi.stubGlobal('window', {
      ontolearn: bridge,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      confirm: () => true,
    })
    return (event: TaskUpdate) => listeners.forEach((listener) => listener(event))
  }

  it('switches all tabs, publishes the valid Agent module, and guards the workbench on freeze and disconnect', async () => {
    const emit = appBridge()
    const h = harness(App, undefined)
    const anchor = (module: string) => h.find((node) => node.props.href === `#${module}-workspace`)
    await vi.waitFor(() => expect(anchor('mapping')).toBeDefined())
    expect(h.find((node) => node.props.id === 'query-workspace')).toBeDefined()
    for (const module of ['mapping', 'behavior', 'scenario', 'transfer'] as const) {
      const link = anchor(module)!
      ;(link.props.onClick as (event: unknown) => void)({ preventDefault() {} })
      expect(anchor(module)?.props['aria-current']).toBe('page')
      expect(h.find((node) => node.props.id === `${module}-workspace`)?.key).toContain(
        inputSnapshotId,
      )
      expect(agentContextStore.getSnapshot().module).toBe(toAgentModule(module))
    }
    expect(toAgentModule('transfer')).toBe('learn')
    const library = propsOf<Parameters<typeof LibraryLocationPanel>[0]>(
      h.find((node) => node.type === LibraryLocationPanel),
    )
    library.freeze(true)
    expect(anchor('mapping')?.props['aria-disabled']).toBe(true)
    expect(h.find((node) => node.props.className === 'workspace-freeze')?.props.disabled).toBe(true)
    library.freeze(false)
    emit({
      kind: 'connection',
      generation: 3,
      projectId,
      error: err.error,
      state: 'offline',
      attempt: 3,
    })
    expect(anchor('mapping')?.props['aria-disabled']).toBe(true)
    expect(h.find((node) => node.props.id === 'transfer-workspace')).toBeUndefined()
    h.unmount()
  })

  it('keeps every new link disabled when management recovery cannot be confirmed', async () => {
    appBridge({
      getProjectManagementState: vi.fn(async () => err),
      getPendingProjectManagementOperations: vi.fn(async () => err),
      getProjectManagementCatalog: vi.fn(async () => err),
    })
    const h = harness(App, undefined)
    const anchors = () =>
      tree(h.render()).filter((node) =>
        [
          '#mapping-workspace',
          '#behavior-workspace',
          '#scenario-workspace',
          '#transfer-workspace',
        ].includes(String(node.props.href)),
      )
    await vi.waitFor(() => expect(anchors()).toHaveLength(4))
    expect(anchors().every((node) => node.props['aria-disabled'] === true)).toBe(true)
    expect(h.find((node) => node.props.className === 'workspace-freeze')?.props.disabled).toBe(true)
    h.unmount()
  })
})
