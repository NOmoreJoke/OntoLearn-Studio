/**
 * Ontology import / export panel.
 *
 * Export only ever emits the **committed** project state. Import is a two
 * step, all-or-nothing flow: the host first *checks* the Turtle file, and a
 * successful check only produces a plan. The plan is then committed through
 * the existing ChangeSet chain (preview → full diff → confirm → commit), so a
 * rejected or invalid file can never leave the project half written.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  BridgeResult,
  ChangeSetConfirmation,
  ChangeSetPage,
  ChangeSetPreview,
  MainlineChangePlanDTO,
  OntologyTurtleExportResultDTO,
  OntologyTurtleImportCheckResultDTO,
  OntologyTurtleImportPlanDTO,
  OntologyTurtleImportSummaryDTO,
  OntologyTurtleRejectionItem,
} from '@ontolearn/contracts'
import { reassembleChangeSetDocument } from '@ontolearn/contracts'

export type ImportExportPanelProps = {
  /** The selected project; import and export are bound to it. */
  projectId: string | null
  /** Current committed project revision, used as the change base. */
  projectRevision: number | null
  /** Called after a successful commit so the host can re-read the project. */
  onImported?: (operationId: string) => void
  onError?: (message: string) => void
}

type ImportStatus = 'idle' | 'checking' | 'ok' | 'rejected' | 'error'

/** The host contract limits the checked Turtle text to 262144 characters. */
export const MAX_IMPORT_TEXT_LENGTH = 262144
/** Upper bound checked *before* the file is read into memory. */
export const MAX_IMPORT_FILE_BYTES = 1024 * 1024

const take = <T,>(reply: { ok: true; data: T } | { ok: false; error: { code: string } }): T => {
  if (!reply.ok) throw new Error(reply.error.code)
  return reply.data
}

/**
 * The immutable, already verified import snapshot.
 *
 * It is produced exactly once, is rendered row by row to the user, and is the
 * only object the commit path is allowed to act on. The commit never rebuilds
 * a preview and never pages the diff again.
 */
export type VerifiedImportPreview = {
  /** Unique identity of this verified snapshot. */
  token: string
  /** The monotonic request sequence that produced it. */
  reqSeq: number
  projectId: string
  baseRevision: number
  previewHash: string
  inputSnapshotId: string
  preparedPlanRef: string
  parametersHash: string
  completionCursor: string
  summary: string
  rows: unknown[]
  operationId: string
}

/** The bridge surface the import flow really uses. */
export type ImportBridge = {
  previewProjectChangeset(args: {
    baseRevision: number
    intent: 'change'
    plan: MainlineChangePlanDTO
  }): Promise<BridgeResult<ChangeSetPreview>>
  getProjectDiffPage(args: {
    previewHash: string
    documentKind: 'diff' | 'undo-impact'
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<ChangeSetPage>>
  confirmProjectChangeset(args: {
    previewHash: string
    completionCursor: string
  }): Promise<BridgeResult<ChangeSetConfirmation>>
  commitProjectChangeSet(args: {
    operationId: string
    confirmation: ChangeSetConfirmation
  }): Promise<BridgeResult<unknown>>
}

/** The verified preview, its summary and the human consent, bound to one identity. */
type VerifiedState = {
  identity: string
  preview?: VerifiedImportPreview
  consent: boolean
  summary: string
}

const emptyVerified = (identity: string): VerifiedState => ({
  identity,
  preview: undefined,
  consent: false,
  summary: '',
})

/** Base IRI used when checking an imported Turtle document. */
export function importBaseUri(projectId: string | null): string {
  return projectId ? `urn:ontolearn:project:${projectId}` : 'urn:ontolearn:project:local'
}

/**
 * Turn a checked import plan into the change plan of the existing ChangeSet
 * chain. Only the two supported sections are carried over; nothing else is
 * invented and no direct write path exists.
 */
export function importPlanToChangePlan(plan: OntologyTurtleImportPlanDTO): MainlineChangePlanDTO {
  const changePlan: MainlineChangePlanDTO = {}
  if (plan.definitions) changePlan.definitions = plan.definitions
  if (plan.manual) changePlan.manual = plan.manual
  return changePlan
}

/** The export view model: a committed snapshot, or a whole-batch rejection. */
export function exportOutcome(
  result: OntologyTurtleExportResultDTO,
):
  | { status: 'ok'; tripleCount: number; inputSnapshotId: string; projectRevision: number }
  | { status: 'rejected'; reasons: OntologyTurtleRejectionItem[] } {
  return result.status === 'ok'
    ? {
        status: 'ok',
        tripleCount: result.tripleCount,
        inputSnapshotId: result.inputSnapshotId,
        projectRevision: result.projectRevision,
      }
    : { status: 'rejected', reasons: result.reasons }
}

/**
 * The import view model. `rejected` (outside the capability boundary) and
 * `invalid` (syntax / format error) stay distinguishable.
 */
export function importOutcome(
  result: OntologyTurtleImportCheckResultDTO,
):
  | { status: 'ok'; summary: OntologyTurtleImportSummaryDTO }
  | { status: 'rejected'; reasons: OntologyTurtleRejectionItem[] }
  | { status: 'invalid'; reasons: OntologyTurtleRejectionItem[] } {
  if (result.status === 'ok') return { status: 'ok', summary: result.summary }
  return { status: result.status, reasons: result.reasons }
}

/**
 * Trigger a browser download for the exported Turtle text.
 * Returns `false` when no DOM is available so callers can still report the
 * verified summary without pretending a file was written.
 */
export function downloadTurtle(text: string, filename: string): boolean {
  if (typeof document === 'undefined' || typeof URL.createObjectURL !== 'function') return false
  const blob = new Blob([text], { type: 'text/turtle;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.rel = 'noopener'
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
  return true
}

/**
 * Read the complete diff document exactly once.
 * A repeated cursor is a hard failure: the pagination must never loop.
 */
export async function readFullDiffPages(
  bridge: Pick<ImportBridge, 'getProjectDiffPage'>,
  previewHash: string,
  isCurrent?: () => boolean,
): Promise<{ pages: ChangeSetPage[]; completionCursor: string; stale?: boolean }> {
  const pages: ChangeSetPage[] = []
  let cursor: string | null = null
  for (let count = 0; count < 512; count++) {
    if (isCurrent && !isCurrent()) return { pages, completionCursor: '', stale: true }
    const page: ChangeSetPage = take(
      await bridge.getProjectDiffPage({
        previewHash,
        documentKind: 'diff',
        pageSize: 16,
        cursor,
      }),
    )
    if (isCurrent && !isCurrent()) return { pages, completionCursor: '', stale: true }
    if (!page.complete && pages.some((old) => old.nextCursor === page.nextCursor))
      throw new Error('CURSOR_REPEATED')
    pages.push(page)
    if (page.complete) return { pages, completionCursor: page.nextCursor }
    cursor = page.nextCursor
  }
  throw new Error('DIFF_INCOMPLETE')
}

/**
 * The confirmation must still describe the very preview the user checked:
 * project, preview hash, prepared plan, input snapshot and parameter hash.
 */
export function confirmationMatchesPreview(
  confirmation: ChangeSetConfirmation,
  preview: {
    projectId: string
    previewHash: string
    preparedPlanRef: string
    inputSnapshotId: string
    parametersHash: string
  },
): boolean {
  return (
    confirmation.projectId === preview.projectId &&
    confirmation.previewHash === preview.previewHash &&
    confirmation.preparedPlanRef === preview.preparedPlanRef &&
    confirmation.inputSnapshotId === preview.inputSnapshotId &&
    confirmation.parametersHash === preview.parametersHash
  )
}

export type ImportPrepareResult =
  | { status: 'ready'; preview: VerifiedImportPreview }
  | { status: 'conflict' }
  | { status: 'stale' }
  | { status: 'failed'; code: string }

/**
 * Build the verified snapshot: preview once, read the whole diff once, and
 * re-verify the document with the canonical contract verifier.
 */
export async function prepareVerifiedImport(args: {
  bridge: ImportBridge
  projectId: string
  baseRevision: number
  plan: MainlineChangePlanDTO
  reqSeq: number
  isCurrent: () => boolean
}): Promise<ImportPrepareResult> {
  const { bridge, projectId, baseRevision, plan, reqSeq, isCurrent } = args
  const preview: ChangeSetPreview = take(
    await bridge.previewProjectChangeset({ baseRevision, intent: 'change', plan }),
  )
  if (!isCurrent()) return { status: 'stale' }
  if (preview.status === 'conflict') return { status: 'conflict' }
  if (preview.projectId !== projectId) throw new Error('PROJECT_MISMATCH')
  const full = await readFullDiffPages(bridge, preview.previewHash, isCurrent)
  if (full.stale || !isCurrent()) return { status: 'stale' }
  const document = await reassembleChangeSetDocument(
    {
      projectId: preview.projectId,
      previewHash: preview.previewHash,
      manifest: preview.manifest,
    },
    full.pages,
  )
  if (!isCurrent()) return { status: 'stale' }
  return {
    status: 'ready',
    preview: {
      token: crypto.randomUUID(),
      reqSeq,
      projectId: preview.projectId,
      baseRevision: preview.baseRevision,
      previewHash: preview.previewHash,
      inputSnapshotId: preview.inputSnapshotId,
      preparedPlanRef: preview.preparedPlanRef,
      parametersHash: preview.parametersHash,
      completionCursor: full.completionCursor,
      summary: preview.summary,
      rows: document,
      operationId: crypto.randomUUID(),
    },
  }
}

export type ImportCommitResult =
  | { status: 'committed'; operationId: string }
  | { status: 'stale' }
  | { status: 'failed'; code: string }

/**
 * Commit exactly the snapshot the user checked. The preview is never rebuilt
 * and the diff is never paged again; a confirmation that describes another
 * identity is refused.
 */
export async function commitVerifiedImport(args: {
  bridge: ImportBridge
  verified: VerifiedImportPreview
  isCurrent: () => boolean
}): Promise<ImportCommitResult> {
  const { bridge, verified, isCurrent } = args
  const confirmation: ChangeSetConfirmation = take(
    await bridge.confirmProjectChangeset({
      previewHash: verified.previewHash,
      completionCursor: verified.completionCursor,
    }),
  )
  if (!isCurrent()) return { status: 'stale' }
  if (!confirmationMatchesPreview(confirmation, verified)) throw new Error('INVALID_CONFIRMATION')
  take(await bridge.commitProjectChangeSet({ operationId: verified.operationId, confirmation }))
  if (!isCurrent()) return { status: 'stale' }
  return { status: 'committed', operationId: verified.operationId }
}

export function ImportExportPanel(props: ImportExportPanelProps) {
  const { projectId, projectRevision } = props
  const [exported, setExported] = useState<OntologyTurtleExportResultDTO>()
  const [exporting, setExporting] = useState(false)
  const [importStatus, setImportStatus] = useState<ImportStatus>('idle')
  const [importResult, setImportResult] = useState<OntologyTurtleImportCheckResultDTO>()
  const [importing, setImporting] = useState(false)
  const [message, setMessage] = useState('')
  const live = useRef(true)
  const exportSeq = useRef(0)
  const importSeq = useRef(0)
  // The verified preview, its summary and the human consent always belong to
  // one project generation; a change of identity retires all three at once.
  const identity = `${projectId ?? ''}:${projectRevision ?? ''}`
  const identityRef = useRef(identity)
  useEffect(() => {
    if (identityRef.current !== identity) {
      identityRef.current = identity
      exportSeq.current += 1
      importSeq.current += 1
      setExporting(false)
      setImporting(false)
    }
  }, [identity])
  const [verifiedState, setVerifiedState] = useState<VerifiedState>(() => emptyVerified(identity))
  const verified = verifiedState.identity === identity ? verifiedState : emptyVerified(identity)
  useEffect(() => {
    live.current = true
    return () => {
      live.current = false
    }
  }, [])

  const isExportCurrent = useCallback((mySeq: number, myIdentity: string) => {
    return live.current && exportSeq.current === mySeq && identityRef.current === myIdentity
  }, [])

  const isImportCurrent = useCallback((mySeq: number, myIdentity: string) => {
    return live.current && importSeq.current === mySeq && identityRef.current === myIdentity
  }, [])

  const runExport = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    const mySeq = ++exportSeq.current
    const myIdentity = identity
    setExporting(true)
    setMessage('')
    try {
      const result = take(await bridge.exportProjectOntology({}))
      if (!isExportCurrent(mySeq, myIdentity)) return
      setExported(result)
      if (result.status === 'ok') {
        const downloaded = downloadTurtle(
          result.turtle,
          `ontology-${projectId ?? 'project'}-r${result.projectRevision}.ttl`,
        )
        setMessage(
          downloaded
            ? `已导出已提交态：${result.tripleCount} 条三元组，快照 ${result.inputSnapshotId}，版本 ${result.projectRevision}。`
            : `已生成已提交态：${result.tripleCount} 条三元组，快照 ${result.inputSnapshotId}，版本 ${result.projectRevision}。当前环境无法触发文件下载。`,
        )
      } else {
        setMessage(`导出被拒绝；未生成任何文件，项目未被修改。`)
      }
    } catch (cause) {
      if (!isExportCurrent(mySeq, myIdentity)) return
      setMessage(
        `导出未完成（${cause instanceof Error ? cause.message : 'UNKNOWN'}）；项目未被修改。`,
      )
      props.onError?.(cause instanceof Error ? cause.message : 'UNKNOWN')
    } finally {
      if (isExportCurrent(mySeq, myIdentity)) setExporting(false)
    }
  }, [projectId, identity, isExportCurrent, props])

  const runImportCheck = useCallback(
    async (file: File) => {
      const bridge = window.ontolearn
      if (!bridge) return
      const mySeq = ++importSeq.current
      const myIdentity = identity
      setImporting(true)
      setImportStatus('checking')
      setImportResult(undefined)
      // A new file retires the previous verified preview, summary and consent.
      setVerifiedState(emptyVerified(myIdentity))
      setMessage('')
      try {
        if (projectRevision === null) throw new Error('PROJECT_VERSION_UNAVAILABLE')
        if (file.size > MAX_IMPORT_FILE_BYTES) throw new Error('FILE_TOO_LARGE')
        const turtleText = await file.text()
        if (!isImportCurrent(mySeq, myIdentity)) return
        if (turtleText.length > MAX_IMPORT_TEXT_LENGTH) throw new Error('FILE_TOO_LARGE')
        const result = take(
          await bridge.checkProjectOntologyImport({
            baseUri: importBaseUri(projectId),
            turtleText,
            format: 'turtle',
          }),
        )
        if (!isImportCurrent(mySeq, myIdentity)) return
        setImportResult(result)
        setImportStatus(
          result.status === 'ok' ? 'ok' : result.status === 'rejected' ? 'rejected' : 'error',
        )
        if (result.status === 'ok')
          setMessage(
            `检查通过：${result.summary.tripleCount} 条三元组，${result.summary.definitionCount} 项定义，${result.summary.manualFactCount} 条手工事实，基准版本 ${result.summary.baseRevision}。尚未写入项目。`,
          )
        else if (result.status === 'rejected')
          setMessage('超出本能力边界，原文件与当前项目保持不变。')
        else setMessage('文件语法或格式错误，原文件与当前项目保持不变。')
      } catch (cause) {
        if (!isImportCurrent(mySeq, myIdentity)) return
        setImportStatus('error')
        const code = cause instanceof Error ? cause.message : 'UNKNOWN'
        setMessage(
          code === 'FILE_TOO_LARGE'
            ? '文件超过可接受的大小上限；原文件与当前项目保持不变。'
            : code === 'PROJECT_VERSION_UNAVAILABLE'
              ? '尚未读取当前项目版本；请先读取项目再导入。'
              : `导入检查未完成（${code}）；原文件与当前项目保持不变。`,
        )
      } finally {
        if (isImportCurrent(mySeq, myIdentity)) setImporting(false)
      }
    },
    [projectId, projectRevision, identity, isImportCurrent],
  )

  const previewImport = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge || !importResult || importResult.status !== 'ok') return
    const mySeq = ++importSeq.current
    const myIdentity = identity
    setImporting(true)
    setMessage('')
    // A new preview invalidates the previous snapshot and the previous consent.
    setVerifiedState(emptyVerified(myIdentity))
    try {
      const outcome = await prepareVerifiedImport({
        bridge,
        projectId: projectId ?? '',
        baseRevision: importResult.summary.baseRevision,
        plan: importPlanToChangePlan(importResult.plan),
        reqSeq: mySeq,
        isCurrent: () => isImportCurrent(mySeq, myIdentity),
      })
      if (outcome.status === 'stale' || !isImportCurrent(mySeq, myIdentity)) return
      if (outcome.status === 'conflict') {
        setMessage('基准版本冲突：本次导入不能提交，请重新读取项目后再试。')
        return
      }
      if (outcome.status === 'failed') {
        setMessage(`无法生成完整差异（${outcome.code}）；项目未被修改。`)
        return
      }
      setVerifiedState({
        identity: myIdentity,
        preview: outcome.preview,
        consent: false,
        summary: `完整差异已核验：${outcome.preview.rows.length} 项；摘要 ${outcome.preview.summary}。确认前不会写入任何数据。`,
      })
    } catch (cause) {
      if (!isImportCurrent(mySeq, myIdentity)) return
      const code = cause instanceof Error ? cause.message : 'UNKNOWN'
      setMessage(`无法生成完整差异（${code}）；项目未被修改。`)
      props.onError?.(code)
    } finally {
      if (isImportCurrent(mySeq, myIdentity)) setImporting(false)
    }
  }, [importResult, projectId, identity, isImportCurrent, props])

  const commitImport = useCallback(async () => {
    const bridge = window.ontolearn
    const verifiedPreview = verified.preview
    if (!bridge || !verifiedPreview || !verified.consent) return
    const mySeq = ++importSeq.current
    const myIdentity = identity
    setImporting(true)
    try {
      const outcome = await commitVerifiedImport({
        bridge,
        verified: verifiedPreview,
        isCurrent: () => isImportCurrent(mySeq, myIdentity),
      })
      if (outcome.status === 'stale' || !isImportCurrent(mySeq, myIdentity)) return
      if (outcome.status === 'failed') {
        setMessage(`导入未完成（${outcome.code}）；项目未被本次操作修改。`)
        props.onError?.(outcome.code)
        return
      }
      setMessage('导入已提交；正式保存结果以任务终态为准。')
      props.onImported?.(outcome.operationId)
    } catch (cause) {
      if (!isImportCurrent(mySeq, myIdentity)) return
      const code = cause instanceof Error ? cause.message : 'UNKNOWN'
      setMessage(`导入未完成（${code}）；项目未被本次操作修改。`)
      props.onError?.(code)
    } finally {
      if (isImportCurrent(mySeq, myIdentity)) setImporting(false)
    }
  }, [verified, identity, isImportCurrent, props])

  const exportRejections = exported ? exportOutcome(exported) : undefined
  const importView = importResult ? importOutcome(importResult) : undefined
  const importRejections = importView && importView.status !== 'ok' ? importView.reasons : []
  return (
    <section
      className="ontology-import-export"
      data-testid="ontology-import-export"
      aria-label="本体导入导出"
    >
      <h2>导入 / 导出</h2>
      <p>
        导出仅包含当前已提交态（不含未提交草稿）。导入先做完整检查，确认后才进入既有预览、差异、确认与提交流程。
      </p>
      <button
        type="button"
        data-testid="ontology-export-button"
        disabled={exporting || !projectId || projectRevision === null}
        onClick={() => void runExport()}
      >
        导出已提交态本体（Turtle）
      </button>
      {exported?.status === 'ok' && (
        <p data-testid="ontology-export-summary">
          {exported.tripleCount} 条三元组 · 快照 {exported.inputSnapshotId} · 版本{' '}
          {exported.projectRevision}
        </p>
      )}
      {exportRejections?.status === 'rejected' && (
        <div data-testid="ontology-export-rejections">
          <p role="alert">导出被整批拒绝；未生成任何文件，项目未被修改。</p>
          <ul>
            {exportRejections.reasons.map((reason, index) => (
              <li
                key={`${reason.code}:${index}`}
                data-testid={`ontology-export-rejection-${reason.code}`}
              >
                {reason.code} · {reason.field} · {reason.detail}
              </li>
            ))}
          </ul>
        </div>
      )}
      <label>
        选择 Turtle 文件
        <input
          type="file"
          accept=".ttl,text/turtle"
          data-testid="ontology-import-file"
          disabled={importing || !projectId || projectRevision === null}
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) void runImportCheck(file)
          }}
        />
      </label>
      {importStatus !== 'idle' && importStatus !== 'checking' && (
        <div
          data-testid="ontology-import-check-result"
          data-status={importStatus}
          data-ontology-status={importView?.status ?? 'error'}
        >
          {importView?.status === 'ok' && (
            <p data-testid="ontology-import-summary">
              {importView.summary.tripleCount} 条三元组 · {importView.summary.definitionCount}{' '}
              项定义 · {importView.summary.manualFactCount} 条手工事实 · 基准版本{' '}
              {importView.summary.baseRevision} · 快照 {importView.summary.inputSnapshotId}
            </p>
          )}
          {importView && importView.status !== 'ok' && (
            <ul>
              {importRejections.map((reason, index) => (
                <li
                  key={`${reason.code}:${index}`}
                  data-testid={`ontology-import-rejection-${reason.code}`}
                >
                  {reason.code} · {reason.field} · {reason.detail}
                </li>
              ))}
            </ul>
          )}
          {importView?.status === 'rejected' && (
            <p role="status">超出本能力边界；原文件与当前项目保持不变。</p>
          )}
          {importView?.status === 'invalid' && (
            <p role="alert">文件语法或格式错误（与超出能力边界不同）；原文件与当前项目保持不变。</p>
          )}
        </div>
      )}
      {message && (
        <p role="status" data-testid="ontology-import-export-message">
          {message}
        </p>
      )}
      {importResult?.status === 'ok' && (
        <>
          <button
            type="button"
            data-testid="ontology-import-preview"
            disabled={importing}
            onClick={() => void previewImport()}
          >
            预览变更并确认提交
          </button>
          {verified.summary && <p data-testid="ontology-import-diff-summary">{verified.summary}</p>}
          {verified.preview && (
            <>
              <p>以下为本次已核验的完整差异明细（逐行）：</p>
              <pre data-testid="ontology-import-diff-rows">
                {JSON.stringify(verified.preview.rows, null, 2)}
              </pre>
            </>
          )}
          {verified.preview && (
            <>
              <label>
                <input
                  type="checkbox"
                  data-testid="ontology-import-consent"
                  checked={verified.consent}
                  onChange={(event) =>
                    setVerifiedState((previous) =>
                      previous.identity === identity
                        ? { ...previous, consent: event.target.checked }
                        : previous,
                    )
                  }
                />
                我已核对完整差异，确认导入本次变更
              </label>
              <button
                type="button"
                data-testid="ontology-import-commit"
                disabled={importing || !verified.consent}
                onClick={() => void commitImport()}
              >
                确认并提交导入
              </button>
            </>
          )}
        </>
      )}
      {projectRevision === null && <p role="status">尚未读取当前项目版本；导入与导出均已禁用。</p>}
    </section>
  )
}
