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
 *
 * Every piece of UI state belongs to one exact draft identity (project,
 * operation, draft type, base revision and input snapshot). A different draft
 * retires the previous rows, the previous consent and the previous result
 * immediately, and every asynchronous answer of an outdated request is
 * discarded instead of overwriting the current view.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import {
  reassembleChangeSetDocument,
  type AgentCommitDraftResultDTO,
  type AgentDraftPlanDTO,
  type BridgeResult,
  type ChangeSetConfirmation,
  type ChangeSetPage,
  type ChangeSetPreview,
  type MainlineChangePlanDTO,
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

/** The bridge surface the draft flow really uses. */
export type DraftDiffBridge = {
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
  commitAgentDraft(args: {
    operationId: string
    draftType: AgentDraftPlanDTO['draftType']
    confirmation: ChangeSetConfirmation
    label?: string | null
  }): Promise<BridgeResult<AgentCommitDraftResultDTO>>
}

/**
 * The exact identity of one draft. Two drafts that differ in any of these
 * fields are never allowed to share UI state, consent or a commit.
 */
export function draftIdentityOf(
  plan: AgentDraftPlanDTO | undefined,
  projectId: string | null,
): string {
  if (!plan || !projectId) return ''
  return JSON.stringify([
    projectId,
    plan.operationId,
    plan.draftType,
    plan.baseRevision,
    plan.inputSnapshotId,
  ])
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
  isCurrent?: () => boolean,
): Promise<{ pages: ChangeSetPage[]; completionCursor: string; stale?: boolean }> {
  const pages: ChangeSetPage[] = []
  let cursor: string | null = null
  for (let count = 0; count < 512; count++) {
    if (isCurrent && !isCurrent()) return { pages, completionCursor: '', stale: true }
    const page: ChangeSetPage = take(
      await bridge.getProjectDiffPage({
        previewHash: preview.previewHash,
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

export type DraftPrepareResult =
  | {
      status: 'ready'
      preview: Extract<ChangeSetPreview, { status: 'ready' }>
      rows: unknown[]
      completionCursor: string
    }
  | { status: 'conflict' }
  | { status: 'stale' }
  | { status: 'failed'; code: string }

/**
 * Read the complete, verified difference of one draft. Every await is followed
 * by an ownership check: an answer of an outdated request is dropped.
 */
export async function prepareDraftDiff(args: {
  bridge: DraftDiffBridge
  plan: AgentDraftPlanDTO
  projectId: string
  isCurrent: () => boolean
}): Promise<DraftPrepareResult> {
  const { bridge, plan, projectId, isCurrent } = args
  const answer: ChangeSetPreview = take(
    await bridge.previewProjectChangeset({
      baseRevision: plan.baseRevision,
      intent: 'change',
      plan: plan.plan,
    }),
  )
  if (!isCurrent()) return { status: 'stale' }
  if (answer.projectId !== projectId) throw new Error('PROJECT_MISMATCH')
  if (answer.status === 'conflict') return { status: 'conflict' }
  if (answer.baseRevision !== plan.baseRevision) throw new Error('BASE_REVISION_MISMATCH')
  const full = await readFullDiff(bridge, answer, isCurrent)
  if (full.stale || !isCurrent()) return { status: 'stale' }
  const document = await reassembleChangeSetDocument(
    {
      projectId: answer.projectId,
      previewHash: answer.previewHash,
      manifest: answer.manifest,
    },
    full.pages,
  )
  if (!isCurrent()) return { status: 'stale' }
  return {
    status: 'ready',
    preview: answer,
    rows: document,
    completionCursor: full.completionCursor,
  }
}

export type DraftCommitResult =
  | { status: 'committed'; result: AgentCommitDraftResultDTO }
  | { status: 'stale' }
  | { status: 'failed'; code: string }

/**
 * Commit exactly the preview that was checked. The confirmation must still
 * describe the very same identity, and the write is only sent while the
 * request is still the current one.
 */
export async function commitDraftDiff(args: {
  bridge: DraftDiffBridge
  plan: AgentDraftPlanDTO
  preview: Extract<ChangeSetPreview, { status: 'ready' }>
  completionCursor: string
  label?: string
  isCurrent: () => boolean
}): Promise<DraftCommitResult> {
  const { bridge, plan, preview, completionCursor, label, isCurrent } = args
  const confirmation: ChangeSetConfirmation = take(
    await bridge.confirmProjectChangeset({
      previewHash: preview.previewHash,
      completionCursor,
    }),
  )
  if (!isCurrent()) return { status: 'stale' }
  if (
    confirmation.projectId !== preview.projectId ||
    confirmation.previewHash !== preview.previewHash ||
    confirmation.preparedPlanRef !== preview.preparedPlanRef ||
    confirmation.inputSnapshotId !== preview.inputSnapshotId ||
    confirmation.parametersHash !== preview.parametersHash
  )
    throw new Error('INVALID_CONFIRMATION')
  const committed: AgentCommitDraftResultDTO = take(
    await bridge.commitAgentDraft({
      operationId: plan.operationId,
      draftType: plan.draftType,
      confirmation,
      label: label ?? null,
    }),
  )
  if (!isCurrent()) return { status: 'stale' }
  return { status: 'committed', result: committed }
}

/** Every piece of UI state, bound to the draft identity that produced it. */
type DiffView = {
  identity: string
  boundIdentity: string
  phase: DraftDiffPhase
  preview?: Extract<ChangeSetPreview, { status: 'ready' }>
  rows: unknown[]
  completionCursor: string
  consent: boolean
  message: string
  result?: AgentCommitDraftResultDTO
}

const emptyView = (identity: string): DiffView => ({
  identity,
  boundIdentity: '',
  phase: 'idle',
  preview: undefined,
  rows: [],
  completionCursor: '',
  consent: false,
  message: '',
  result: undefined,
})

export function DraftDiffPreview(props: DraftDiffPreviewProps) {
  const { plan, projectId, label } = props
  const draftIdentity = draftIdentityOf(plan, projectId)
  const [view, setView] = useState<DiffView>(() => emptyView(draftIdentity))
  // A different draft retires the previous rows, consent and result at once.
  const current = view.identity === draftIdentity ? view : emptyView(draftIdentity)
  const live = useRef(true)
  const reqSeq = useRef(0)
  const identityRef = useRef(draftIdentity)
  useEffect(() => {
    identityRef.current = draftIdentity
  }, [draftIdentity])
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
    const mySeq = ++reqSeq.current
    const myIdentity = draftIdentity
    const isCurrent = () =>
      live.current && reqSeq.current === mySeq && identityRef.current === myIdentity
    setView({
      identity: myIdentity,
      boundIdentity: '',
      phase: 'previewing',
      preview: undefined,
      rows: [],
      completionCursor: '',
      consent: false,
      message: '',
      result: undefined,
    })
    try {
      const outcome = await prepareDraftDiff({
        bridge,
        plan,
        projectId,
        isCurrent,
      })
      if (outcome.status === 'stale' || !isCurrent()) return
      if (outcome.status === 'conflict') {
        setView((previous) =>
          previous.identity === myIdentity
            ? {
                ...previous,
                phase: 'conflict',
                message: '基准版本冲突：本次草稿不能提交，请重新生成草稿。',
              }
            : previous,
        )
        return
      }
      if (outcome.status === 'failed') {
        setView((previous) =>
          previous.identity === myIdentity
            ? {
                ...previous,
                phase: 'failed',
                message: `未能生成可核对的完整差异（${outcome.code}）；项目未被修改。`,
              }
            : previous,
        )
        onError.current?.(outcome.code)
        return
      }
      setView((previous) =>
        previous.identity === myIdentity
          ? {
              ...previous,
              boundIdentity: myIdentity,
              phase: 'ready',
              preview: outcome.preview,
              rows: outcome.rows,
              completionCursor: outcome.completionCursor,
              consent: false,
              message: '',
            }
          : previous,
      )
    } catch (cause) {
      if (!isCurrent()) return
      const code = cause instanceof Error ? cause.message : 'UNKNOWN'
      setView((previous) =>
        previous.identity === myIdentity
          ? {
              ...previous,
              phase: 'failed',
              message: `未能生成可核对的完整差异（${code}）；项目未被修改。`,
            }
          : previous,
      )
      onError.current?.(code)
    }
  }, [plan, projectId, draftIdentity])

  useEffect(() => {
    if (!plan) return
    // Deferred: the effect body itself never triggers a state update.
    const timer = setTimeout(() => void prepare(), 0)
    return () => clearTimeout(timer)
  }, [plan, prepare])

  const commit = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge || !plan || !current.preview) return
    if (!current.consent || !current.completionCursor) return
    const mySeq = ++reqSeq.current
    const myIdentity = draftIdentity
    const isCurrent = () =>
      live.current && reqSeq.current === mySeq && identityRef.current === myIdentity
    setView((previous) =>
      previous.identity === myIdentity
        ? { ...previous, phase: 'committing', message: '' }
        : previous,
    )
    try {
      const outcome = await commitDraftDiff({
        bridge,
        plan,
        preview: current.preview,
        completionCursor: current.completionCursor,
        label,
        isCurrent,
      })
      if (outcome.status === 'stale' || !isCurrent()) return
      if (outcome.status === 'failed') {
        setView((previous) =>
          previous.identity === myIdentity
            ? {
                ...previous,
                phase: 'failed',
                message: `提交未完成（${outcome.code}）；项目未被本次操作修改，请核对实际状态。`,
              }
            : previous,
        )
        onError.current?.(outcome.code)
        return
      }
      setView((previous) =>
        previous.identity === myIdentity
          ? {
              ...previous,
              phase: 'committed',
              result: outcome.result,
              message: '草稿已提交；正式保存结果以任务终态为准。',
            }
          : previous,
      )
      onCommitted.current?.(outcome.result)
    } catch (cause) {
      if (!isCurrent()) return
      const code = cause instanceof Error ? cause.message : 'UNKNOWN'
      setView((previous) =>
        previous.identity === myIdentity
          ? {
              ...previous,
              phase: 'failed',
              message: `提交未完成（${code}）；项目未被本次操作修改，请核对实际状态。`,
            }
          : previous,
      )
      onError.current?.(code)
    }
  }, [plan, current, label, draftIdentity])

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
  // Only a view that is bound to the current draft identity may be rendered.
  const bound = current.boundIdentity === draftIdentity && draftIdentity !== ''
  const blocked = current.phase === 'conflict' || current.phase === 'failed'
  const busy = current.phase === 'previewing' || current.phase === 'committing'
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
          {current.message}
        </p>
      )}
      {current.phase === 'idle' && <p role="status">正在准备完整差异…</p>}
      {current.phase === 'previewing' && <p role="status">正在读取完整差异…</p>}
      {current.phase === 'committing' && <p role="status">正在提交草稿…</p>}
      {current.phase === 'committed' && bound && (
        <p role="status" data-testid="ontology-draft-committed">
          {current.message}
          {current.result
            ? ` 操作 ${current.result.operationId} · 提交前快照 ${current.result.beforeAgentCheckpointRef}`
            : ''}
        </p>
      )}
      {current.phase === 'ready' && bound && (
        <>
          <p>全部 {current.rows.length} 项；分段顺序、长度、SHA 与完整文档已由契约校验器核验。</p>
          <pre>{JSON.stringify(current.rows, null, 2)}</pre>
          <label>
            <input
              type="checkbox"
              data-testid="ontology-draft-consent"
              checked={current.consent}
              onChange={(event) =>
                setView((previous) =>
                  previous.identity === draftIdentity
                    ? { ...previous, consent: event.target.checked }
                    : previous,
                )
              }
            />
            我已核对完整差异，确认提交此草稿
          </label>
          <button
            type="button"
            data-testid="ontology-draft-commit"
            disabled={!current.consent || !current.completionCursor}
            onClick={() => void commit()}
          >
            确认并提交 Agent 草稿
          </button>
        </>
      )}
      <button type="button" disabled={busy} onClick={() => void prepare()}>
        重新生成并核对差异
      </button>
    </section>
  )
}
