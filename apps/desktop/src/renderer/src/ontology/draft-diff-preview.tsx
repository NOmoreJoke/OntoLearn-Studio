/**
 * Agent draft diff preview.
 *
 * The Agent never writes project data by itself. This view only:
 *  1. asks the host to preview the frozen change plan (`previewProjectChangeset`),
 *  2. reads the *complete* diff document and re-verifies it with the canonical
 *     contract verifier (`reassembleChangeSetDocument`),
 *  3. and — only after an explicit human confirmation — commits through
 *     `commitAgentDraft`, which takes the `before-agent` snapshot first.
 *
 * Nothing here is a second writer: no direct ontology write, no partial
 * import, and no commit while the base revision conflicts.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import {
  reassembleChangeSetDocument,
  type AgentCommitDraftResultDTO,
  type AgentDraftPlanDTO,
  type ChangeSetPage,
  type ChangeSetPreview,
} from '@ontolearn/contracts'

export type DraftDiffPhase =
  'idle' | 'previewing' | 'ready' | 'conflict' | 'committing' | 'committed' | 'failed'

export type DraftDiffPreviewProps = {
  /** The host-built plan. `undefined` renders the empty state. */
  plan?: AgentDraftPlanDTO
  /** Project the plan belongs to; a mismatch blocks everything. */
  projectId: string | null
  /** Optional human label recorded with the commit. */
  label?: string
  onCommitted?: (result: AgentCommitDraftResultDTO) => void
  onError?: (message: string) => void
}

const take = <T,>(reply: { ok: true; data: T } | { ok: false; error: { code: string } }): T => {
  if (!reply.ok) throw new Error(reply.error.code)
  return reply.data
}

export async function readFullDiff(
  bridge: {
    getProjectDiffPage(args: {
      previewHash: string
      documentKind: 'diff' | 'undo-impact'
      pageSize: number
      cursor: string | null
    }): Promise<{ ok: true; data: ChangeSetPage } | { ok: false; error: { code: string } }>
  },
  preview: { projectId: string; previewHash: string; manifest: { segmentCount: number } },
): Promise<{ pages: ChangeSetPage[]; completionCursor: string }> {
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
    if (page.complete) return { pages, completionCursor: page.nextCursor }
    cursor = page.nextCursor
  }
  throw new Error('DIFF_INCOMPLETE')
}

export function DraftDiffPreview(props: DraftDiffPreviewProps) {
  const { plan, projectId, label } = props
  const [phase, setPhase] = useState<DraftDiffPhase>('idle')
  const [preview, setPreview] = useState<ChangeSetPreview>()
  const [rows, setRows] = useState<unknown[]>([])
  const [completionCursor, setCompletionCursor] = useState('')
  const [consent, setConsent] = useState(false)
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<AgentCommitDraftResultDTO>()
  const live = useRef(true)
  const operationId = plan?.operationId
  // Callbacks are read through a ref so a new parent render never restarts
  // the preview/diff read.
  const onError = useRef(props.onError)
  const onCommitted = useRef(props.onCommitted)
  useEffect(() => {
    onError.current = props.onError
    onCommitted.current = props.onCommitted
  })

  useEffect(() => {
    live.current = true
    return () => {
      live.current = false
    }
  }, [])

  const prepare = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge || !plan || !projectId) return
    setPhase('previewing')
    setMessage('')
    setConsent(false)
    setRows([])
    setResult(undefined)
    try {
      const answer = take(
        await bridge.previewProjectChangeset({
          baseRevision: plan.baseRevision,
          intent: 'change',
          plan: plan.plan,
        }),
      )
      if (!live.current) return
      if (answer.projectId !== projectId) {
        setPhase('failed')
        setMessage('预览所属项目与当前项目不一致；不能据此提交。')
        return
      }
      if (answer.status === 'conflict') {
        setPreview(answer)
        setPhase('conflict')
        setMessage('基准版本冲突：本次草稿不能提交，请重新生成草稿。')
        return
      }
      if (answer.baseRevision !== plan.baseRevision) {
        setPhase('failed')
        setMessage('预览基准与草稿基准不一致；不能据此提交。')
        return
      }
      const full = await readFullDiff(bridge, answer)
      if (!live.current) return
      const document = await reassembleChangeSetDocument(
        {
          projectId: answer.projectId,
          previewHash: answer.previewHash,
          manifest: answer.manifest,
        },
        full.pages,
      )
      if (!live.current) return
      setPreview(answer)
      setRows(document)
      setCompletionCursor(full.completionCursor)
      setPhase('ready')
    } catch (cause) {
      if (!live.current) return
      setPhase('failed')
      const code = cause instanceof Error ? cause.message : 'UNKNOWN'
      setMessage(`未能生成可核对的完整差异（${code}）；项目未被修改。`)
      onError.current?.(code)
    }
  }, [plan, projectId])

  useEffect(() => {
    if (!operationId) return
    // Deferred: the effect body itself never triggers a state update.
    const timer = setTimeout(() => void prepare(), 0)
    return () => clearTimeout(timer)
  }, [operationId, prepare])

  const commit = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge || !plan || !preview || preview.status !== 'ready') return
    if (!consent || !completionCursor) return
    setPhase('committing')
    setMessage('')
    try {
      const confirmation = take(
        await bridge.confirmProjectChangeset({
          previewHash: preview.previewHash,
          completionCursor,
        }),
      )
      if (
        confirmation.projectId !== preview.projectId ||
        confirmation.previewHash !== preview.previewHash ||
        confirmation.preparedPlanRef !== preview.preparedPlanRef ||
        confirmation.inputSnapshotId !== preview.inputSnapshotId ||
        confirmation.parametersHash !== preview.parametersHash
      )
        throw new Error('INVALID_CONFIRMATION')
      const committed = take(
        await bridge.commitAgentDraft({
          operationId: plan.operationId,
          draftType: plan.draftType,
          confirmation,
          label: label ?? null,
        }),
      )
      if (!live.current) return
      setResult(committed)
      setPhase('committed')
      setMessage('草稿已提交；正式保存结果以任务终态为准。')
      onCommitted.current?.(committed)
    } catch (cause) {
      if (!live.current) return
      setPhase('failed')
      const code = cause instanceof Error ? cause.message : 'UNKNOWN'
      setMessage(`提交未完成（${code}）；项目未被本次操作修改，请核对实际状态。`)
      onError.current?.(code)
    }
  }, [plan, preview, consent, completionCursor, label])

  if (!plan) {
    return (
      <section
        className="ontology-draft-diff"
        data-testid="ontology-draft-diff"
        aria-label="Agent 草稿差异"
      >
        <p>尚无 Agent 草稿差异可核对。</p>
      </section>
    )
  }
  const blocked = phase === 'conflict' || phase === 'failed'
  return (
    <section
      className="ontology-draft-diff"
      data-testid="ontology-draft-diff"
      aria-label="Agent 草稿差异"
    >
      <h2>Agent 草稿差异 · 尚未提交</h2>
      <p data-testid="ontology-draft-summary">{plan.summary}</p>
      <p>
        基准版本 {plan.baseRevision} · 输入快照 {plan.inputSnapshotId} · 类型 {plan.draftType}
      </p>
      {blocked && (
        <p role="alert" data-testid="ontology-draft-blocked">
          {message}
        </p>
      )}
      {phase === 'idle' && <p role="status">正在准备完整差异…</p>}
      {phase === 'previewing' && <p role="status">正在读取完整差异…</p>}
      {phase === 'committing' && <p role="status">正在提交草稿…</p>}
      {phase === 'committed' && (
        <p role="status" data-testid="ontology-draft-committed">
          {message}
          {result
            ? ` 操作 ${result.operationId} · 提交前快照 ${result.beforeAgentCheckpointRef}`
            : ''}
        </p>
      )}
      {phase === 'ready' && (
        <>
          <p>全部 {rows.length} 项；分段顺序、长度、SHA 与完整文档已由契约校验器核验。</p>
          <pre>{JSON.stringify(rows, null, 2)}</pre>
          <label>
            <input
              type="checkbox"
              data-testid="ontology-draft-consent"
              checked={consent}
              onChange={(event) => setConsent(event.target.checked)}
            />
            我已核对完整差异，确认提交此草稿
          </label>
          <button
            type="button"
            data-testid="ontology-draft-commit"
            disabled={!consent || !completionCursor}
            onClick={() => void commit()}
          >
            确认并提交 Agent 草稿
          </button>
        </>
      )}
      <button type="button" disabled={phase === 'committing'} onClick={() => void prepare()}>
        重新生成并核对差异
      </button>
    </section>
  )
}
