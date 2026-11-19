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

const take = <T,>(reply: { ok: true; data: T } | { ok: false; error: { code: string } }): T => {
  if (!reply.ok) throw new Error(reply.error.code)
  return reply.data
}

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

export function ImportExportPanel(props: ImportExportPanelProps) {
  const { projectId, projectRevision } = props
  const [exported, setExported] = useState<OntologyTurtleExportResultDTO>()
  const [exporting, setExporting] = useState(false)
  const [importStatus, setImportStatus] = useState<ImportStatus>('idle')
  const [importResult, setImportResult] = useState<OntologyTurtleImportCheckResultDTO>()
  const [importing, setImporting] = useState(false)
  const [diffSummary, setDiffSummary] = useState('')
  const [message, setMessage] = useState('')
  const [plan, setPlan] = useState<MainlineChangePlanDTO>()
  const [consent, setConsent] = useState(false)
  const live = useRef(true)
  useEffect(() => {
    live.current = true
    return () => {
      live.current = false
    }
  }, [])

  const runExport = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    setExporting(true)
    setMessage('')
    try {
      const result = take(await bridge.exportProjectOntology({}))
      if (!live.current) return
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
      if (!live.current) return
      setMessage(
        `导出未完成（${cause instanceof Error ? cause.message : 'UNKNOWN'}）；项目未被修改。`,
      )
      props.onError?.(cause instanceof Error ? cause.message : 'UNKNOWN')
    } finally {
      if (live.current) setExporting(false)
    }
  }, [projectId, props])

  const runImportCheck = useCallback(
    async (file: File) => {
      const bridge = window.ontolearn
      if (!bridge) return
      setImporting(true)
      setImportStatus('checking')
      setImportResult(undefined)
      setPlan(undefined)
      setConsent(false)
      setDiffSummary('')
      setMessage('')
      try {
        const turtleText = await file.text()
        const result = take(
          await bridge.checkProjectOntologyImport({
            baseUri: importBaseUri(projectId),
            turtleText,
            format: 'turtle',
          }),
        )
        if (!live.current) return
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
        if (!live.current) return
        setImportStatus('error')
        setMessage(
          `导入检查未完成（${cause instanceof Error ? cause.message : 'UNKNOWN'}）；原文件与当前项目保持不变。`,
        )
      } finally {
        if (live.current) setImporting(false)
      }
    },
    [projectId],
  )

  const previewImport = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge || !importResult || importResult.status !== 'ok') return
    setImporting(true)
    setMessage('')
    try {
      const changePlan: MainlineChangePlanDTO = {}
      if (importResult.plan.definitions) changePlan.definitions = importResult.plan.definitions
      if (importResult.plan.manual) changePlan.manual = importResult.plan.manual
      setPlan(changePlan)
      const preview: ChangeSetPreview = take(
        await bridge.previewProjectChangeset({
          baseRevision: importResult.summary.baseRevision,
          intent: 'change',
          plan: changePlan,
        }),
      )
      if (preview.status === 'conflict') {
        setMessage('基准版本冲突：本次导入不能提交，请重新读取项目后再试。')
        return
      }
      const pages: ChangeSetPage[] = []
      let cursor: string | null = null
      for (let count = 0; count < 512; count++) {
        const page: ChangeSetPage = take(
          await bridge.getProjectDiffPage({
            previewHash: preview.previewHash,
            documentKind: 'diff',
            pageSize: 16,
            cursor,
          }),
        )
        if (!page.complete && pages.some((old) => old.nextCursor === page.nextCursor))
          throw new Error('CURSOR_REPEATED')
        pages.push(page)
        if (page.complete) break
        cursor = page.nextCursor
      }
      const last = pages.at(-1)
      if (!last?.complete) throw new Error('DIFF_INCOMPLETE')
      const document = await reassembleChangeSetDocument(
        {
          projectId: preview.projectId,
          previewHash: preview.previewHash,
          manifest: preview.manifest,
        },
        pages,
      )
      setDiffSummary(
        `完整差异已核验：${document.length} 项；摘要 ${preview.summary}。确认前不会写入任何数据。`,
      )
      setMessage('')
    } catch (cause) {
      setMessage(
        `无法生成完整差异（${cause instanceof Error ? cause.message : 'UNKNOWN'}）；项目未被修改。`,
      )
      props.onError?.(cause instanceof Error ? cause.message : 'UNKNOWN')
    } finally {
      if (live.current) setImporting(false)
    }
  }, [importResult, props])

  const commitImport = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge || !importResult || importResult.status !== 'ok' || !plan || !consent) return
    setImporting(true)
    try {
      const preview: ChangeSetPreview = take(
        await bridge.previewProjectChangeset({
          baseRevision: importResult.summary.baseRevision,
          intent: 'change',
          plan,
        }),
      )
      if (preview.status === 'conflict') {
        setMessage('基准版本冲突：本次导入不能提交，请重新读取项目后再试。')
        return
      }
      const pages: ChangeSetPage[] = []
      let cursor: string | null = null
      for (let count = 0; count < 512; count++) {
        const page: ChangeSetPage = take(
          await bridge.getProjectDiffPage({
            previewHash: preview.previewHash,
            documentKind: 'diff',
            pageSize: 16,
            cursor,
          }),
        )
        pages.push(page)
        if (page.complete) break
        cursor = page.nextCursor
      }
      const last = pages.at(-1)
      if (!last?.complete) throw new Error('DIFF_INCOMPLETE')
      const confirmation = take(
        await bridge.confirmProjectChangeset({
          previewHash: preview.previewHash,
          completionCursor: last.nextCursor,
        }),
      )
      const operationId = crypto.randomUUID()
      take(await bridge.commitProjectChangeSet({ operationId, confirmation }))
      setMessage('导入已提交；正式保存结果以任务终态为准。')
      props.onImported?.(operationId)
    } catch (cause) {
      setMessage(
        `导入未完成（${cause instanceof Error ? cause.message : 'UNKNOWN'}）；项目未被本次操作修改。`,
      )
      props.onError?.(cause instanceof Error ? cause.message : 'UNKNOWN')
    } finally {
      if (live.current) setImporting(false)
    }
  }, [importResult, plan, consent, props])

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
        disabled={exporting || !projectId}
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
          disabled={importing || !projectId}
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
          {diffSummary && <p data-testid="ontology-import-diff-summary">{diffSummary}</p>}
          {diffSummary && (
            <>
              <label>
                <input
                  type="checkbox"
                  data-testid="ontology-import-consent"
                  checked={consent}
                  onChange={(event) => setConsent(event.target.checked)}
                />
                我已核对完整差异，确认导入本次变更
              </label>
              <button
                type="button"
                data-testid="ontology-import-commit"
                disabled={importing || !consent}
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
