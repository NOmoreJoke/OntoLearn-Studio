import { useState } from 'react'
import {
  mappingPublicIssueKeys,
  type DesktopBridge,
  type MappingDraft,
  type MappingEncoding,
  type MappingSourceSelectResultDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '@ontolearn/contracts/v2'
import {
  commitWorkspaceChange,
  prepareWorkspaceChange,
  requireWorkspaceReply,
  type WorkspaceChangePreview,
} from '../ontology/workspace-change'
import { MappingPage } from './MappingPage'
import {
  acceptPreview,
  cancelPreview,
  draftKey,
  previewHasBlockers,
  selectSource,
  updateDraft,
  type Wizard,
} from './model'
import { containsLocalPath, maskLocalPaths } from './local-text'
import { useWorkspaceOperation, type ReportWorkspaceStatus } from './workspace-operation'

type Bridge = Pick<
  DesktopBridge,
  | 'selectMappingSource'
  | 'readMappingDraft'
  | 'saveMappingDraft'
  | 'previewMapping'
  | 'prepareMappingCommit'
  | 'readProject'
  | 'previewProjectChangeset'
  | 'getProjectDiffPage'
  | 'confirmProjectChangeset'
  | 'commitProjectChangeSet'
  | 'getJob'
  | 'restoreTasks'
>

const EMPTY_DRAFT: MappingDraft = {
  identity: '',
  version: 1,
  namespace: '',
  classIri: '',
  keys: [],
  fields: [],
}
const PAGE_SIZE = 20
const deterministicCommitRejections = new Set([
  'INVALID_REQUEST',
  'INVALID_STATE',
  'METHOD_NOT_ALLOWED',
  'VERSION_INCOMPATIBLE',
  'HANDSHAKE_REQUIRED',
  'SESSION_MISMATCH',
  'PERMISSION_DENIED',
  'NOT_FOUND',
  'UNSUPPORTED_CAPABILITY',
  'QUEUE_FULL',
  'REVISION_CONFLICT',
  'OWNERSHIP_CONFLICT',
  'IDENTITY_CONFLICT',
  'STORAGE_BUSY',
  'SEMANTIC_INPUT_INVALID',
  'RESOURCE_LIMIT',
])
const issueLabels: Record<
  (typeof mappingPublicIssueKeys)[keyof typeof mappingPublicIssueKeys],
  string
> = {
  'mapping.sourceInvalid': '源文件或单元格无效',
  'mapping.sourceLimit': '源文件超出读取限制',
  'mapping.encodingUnsupported': '暂不支持此编码',
  'mapping.encodingInvalid': '数据与所选编码不匹配',
  'mapping.sourceUnsafe': '源文件含不支持的加密、宏或 XML',
  'mapping.sourceUnavailable': '源解析器当前不可用',
  'mapping.sheetInvalid': '工作表缺失或无效',
  'mapping.formulaCacheMissing': '公式缺少已保存的结果',
  'mapping.emptyKey': '业务主键为空',
  'mapping.duplicateKey': '业务主键或生成身份重复',
  'mapping.conversionFailed': '字段值转换失败',
  'mapping.referenceInvalid': '引用值无效或目标不存在',
  'mapping.issueUnknown': '存在无法分类的映射问题',
}
export function mappingEncoding(value: string): MappingEncoding {
  switch (value) {
    case 'utf-8-sig':
    case 'utf-8':
      return 'utf-8'
    case 'gb18030':
    case 'big5':
    case 'utf-16':
      return value
    default:
      throw new Error('INVALID_ENCODING')
  }
}
function safeDraft(draft: MappingDraft) {
  return !containsLocalPath(JSON.stringify(draft)) && validateBusiness3('w4.mapping.draft', draft)
}

export function MappingWorkspace({
  bridge,
  projectId,
  revision,
  inputSnapshotId,
  onStatus,
  onCommitted,
}: {
  bridge: Bridge
  projectId: string
  revision: number
  inputSnapshotId: string
  onStatus: ReportWorkspaceStatus
  onCommitted: () => Promise<void>
}) {
  const [state, setState] = useState<Wizard>({
    projectId,
    revision,
    generation: 0,
    draft: EMPTY_DRAFT,
    source: null,
    preview: null,
    confirmed: false,
  })
  const [source, setSource] = useState<MappingSourceSelectResultDTO>()
  const [draftId, setDraftId] = useState('')
  const [draftVersion, setDraftVersion] = useState<{
    id: string
    generation: number
    key: string
  }>()
  const [proposal, setProposal] = useState<{ diff: WorkspaceChangePreview; operationId: string }>()
  const [consent, setConsent] = useState(false)
  const [unknown, setUnknown] = useState(false)
  const [commitRejection, setCommitRejection] = useState<string>()
  const [draftNotice, setDraftNotice] = useState('')
  const dirty = state.draft !== EMPTY_DRAFT && draftKey(state.draft) !== draftVersion?.key
  const pendingProposal = Boolean(proposal && !commitRejection)
  const { busy, error, perform } = useWorkspaceOperation(
    onStatus,
    dirty,
    pendingProposal || unknown,
  )

  function clearProposal() {
    setProposal(undefined)
    setConsent(false)
    setCommitRejection(undefined)
  }
  function chooseSource(sheet?: string, encoding?: string) {
    void perform(async (current) => {
      clearProposal()
      setState(cancelPreview)
      const args =
        source && (sheet || encoding)
          ? {
              selectionId: source.selectionId,
              sheet: sheet ?? source.sheet,
              encoding:
                source.format === 'xlsx' ? null : mappingEncoding(encoding ?? source.encoding!),
            }
          : {}
      const next = requireWorkspaceReply(await bridge.selectMappingSource(args))
      current()
      if (
        !validateBusiness3('result_project.mapping.source.select', next) ||
        next.projectId !== projectId ||
        (args.selectionId && args.selectionId !== next.selectionId)
      )
        throw new Error('WRONG_SOURCE')
      // Sheet and column identifiers must round-trip unchanged. Unsupported host-path names
      // are rejected as a whole instead of sending redacted names back to the parser.
      if (
        [next.sheet, ...next.sheets, ...next.fields.map((field) => field.name)].some(
          containsLocalPath,
        )
      )
        throw new Error('UNSAFE_SOURCE_NAMES')
      const view = maskLocalPaths(next)
      setSource(view)
      setState((old) => selectSource(old, view))
    })
  }
  function readDraft() {
    void perform(async (current) => {
      const id = draftId.trim()
      const receipt = requireWorkspaceReply(await bridge.readMappingDraft({ mappingId: id }))
      current()
      if (
        receipt.projectId !== projectId ||
        receipt.mappingId !== id ||
        !Number.isSafeInteger(receipt.baseRevision) ||
        receipt.baseRevision < 0 ||
        receipt.baseRevision > revision ||
        (!receipt.draft && receipt.baseRevision !== revision) ||
        (receipt.draft && (receipt.draft.identity !== id || !safeDraft(receipt.draft)))
      )
        throw new Error('INVALID_DRAFT')
      const draft = receipt.draft ?? { ...EMPTY_DRAFT, identity: id }
      setDraftVersion({ id, generation: receipt.generation, key: draftKey(draft) })
      setState((old) => updateDraft(old, draft))
      clearProposal()
      setDraftNotice(
        !receipt.draft
          ? '此标识尚无保存的草稿。'
          : receipt.baseRevision < revision
            ? `已读取保存于版本 ${receipt.baseRevision} 的映射草稿（当前版本 ${revision}）；重新保存将绑定到当前版本。`
            : '已读取保存的映射草稿。',
      )
    })
  }
  function saveDraft() {
    void perform(async (current) => {
      const draft = state.draft
      if (!safeDraft(draft)) throw new Error('INVALID_DRAFT')
      const previous =
        draftVersion?.id === draft.identity
          ? draftVersion
          : requireWorkspaceReply(await bridge.readMappingDraft({ mappingId: draft.identity }))
      current()
      if (
        'mappingId' in previous &&
        (previous.projectId !== projectId ||
          previous.mappingId !== draft.identity ||
          !Number.isSafeInteger(previous.baseRevision) ||
          previous.baseRevision < 0 ||
          previous.baseRevision > revision ||
          (!previous.draft && previous.baseRevision !== revision) ||
          previous.draft)
      )
        throw new Error('LOAD_EXISTING_DRAFT')
      const operationId = crypto.randomUUID()
      const saved = requireWorkspaceReply(
        await bridge.saveMappingDraft({
          draft,
          operationId,
          baseRevision: revision,
          expectedGeneration: previous.generation,
        }),
      )
      current()
      if (
        saved.projectId !== projectId ||
        saved.operationId !== operationId ||
        saved.baseRevision !== revision ||
        saved.generation !== previous.generation + 1 ||
        draftKey(saved.draft) !== draftKey(draft)
      )
        throw new Error('WRONG_DRAFT_RECEIPT')
      setDraftVersion({ id: draft.identity, generation: saved.generation, key: draftKey(draft) })
      setDraftNotice('映射草稿已保存。')
    })
  }
  function preview(offset: number) {
    void perform(async (current) => {
      if (!source || !safeDraft(state.draft)) throw new Error('INVALID_MAPPING')
      clearProposal()
      const pending = cancelPreview(state)
      setState(pending)
      const reply = requireWorkspaceReply(
        await bridge.previewMapping({
          selectionId: source.selectionId,
          sheet: source.sheet,
          encoding: source.encoding,
          draft: pending.draft,
          page: { offset, limit: PAGE_SIZE },
        }),
      )
      current()
      if (!validateBusiness3('result_project.mapping.preview', reply))
        throw new Error('INVALID_PREVIEW')
      const view = maskLocalPaths(reply)
      const next = acceptPreview(pending, {
        ...view,
        revision: view.baseRevision,
        generation: pending.generation,
        draftKey: draftKey(pending.draft),
        issues: view.issues.map((issue) => ({
          ...issue,
          code: issueLabels[
            Object.hasOwn(mappingPublicIssueKeys, issue.code)
              ? mappingPublicIssueKeys[issue.code]
              : 'mapping.issueUnknown'
          ],
        })),
      })
      if (next === pending || reply.offset !== offset) throw new Error('STALE_PREVIEW')
      setState(next)
    })
  }
  function prepare(resultId: string) {
    void perform(async (current) => {
      const preview = state.preview
      if (
        !preview ||
        preview.resultId !== resultId ||
        previewHasBlockers(preview) ||
        !source ||
        !safeDraft(state.draft)
      )
        throw new Error('PREVIEW_REQUIRED')
      const bound = requireWorkspaceReply(await bridge.readProject({ editor: 'mapping' }))
      current()
      if (
        bound.projectId !== projectId ||
        bound.inputSnapshotId !== inputSnapshotId ||
        bound.domain.projectRevision !== revision
      )
        throw new Error('STALE_PROJECT')
      const operationId = crypto.randomUUID()
      const receipt = requireWorkspaceReply(
        await bridge.prepareMappingCommit({
          resultId,
          selectionId: source.selectionId,
          sourceFingerprint: source.fingerprint,
          baseRevision: revision,
          operationId,
        }),
      )
      current()
      if (
        receipt.projectId !== projectId ||
        receipt.resultId !== resultId ||
        receipt.plan.mappingPreparation.resultId !== resultId ||
        receipt.selectionId !== source.selectionId ||
        receipt.sourceFingerprint !== source.fingerprint ||
        receipt.baseRevision !== revision ||
        receipt.operationId !== operationId
      )
        throw new Error('WRONG_PREPARATION')
      const diff = await prepareWorkspaceChange(bridge, bound, receipt.plan, current)
      current()
      setProposal({ diff: { ...diff, rows: maskLocalPaths(diff.rows) }, operationId })
    })
  }
  function commit() {
    if (!consent || !proposal || unknown) return
    void perform(async (current) => {
      const job = await commitWorkspaceChange(
        {
          confirmProjectChangeset: (args) => bridge.confirmProjectChangeset(args),
          commitProjectChangeSet: async (args) => {
            setUnknown(true)
            const reply = await bridge.commitProjectChangeSet(args)
            current()
            if (!reply.ok && deterministicCommitRejections.has(reply.error.code)) {
              setCommitRejection(reply.error.code)
              setUnknown(false)
            }
            return reply
          },
          getJob: (jobId) => bridge.getJob(jobId),
        },
        proposal.diff,
        proposal.operationId,
        current,
      )
      current()
      await settleCommit(job.state)
    })
  }
  async function settleCommit(status: 'succeeded' | 'failed' | 'cancelled' | string) {
    if (status !== 'succeeded' && status !== 'failed' && status !== 'cancelled')
      throw new Error('CHANGESET_STATUS_UNKNOWN')
    setUnknown(false)
    clearProposal()
    setState(cancelPreview)
    if (status !== 'succeeded') throw new Error('CHANGESET_NOT_COMMITTED')
    await onCommitted()
  }
  function reconcileCommit() {
    if (!unknown || !proposal) return
    void perform(async (current) => {
      const view = requireWorkspaceReply(await bridge.restoreTasks())
      current()
      const job = view.jobs.find(
        (item) =>
          item.operationId === proposal.operationId &&
          item.projectId === projectId &&
          item.inputSnapshotId === inputSnapshotId &&
          item.capability === 'changeset.commit',
      )
      if (!job || !validateBusiness3('job', job)) throw new Error('CHANGESET_STATUS_UNKNOWN')
      await settleCommit(job.state)
    })
  }
  const locked = busy || unknown || pendingProposal

  return (
    <>
      <fieldset disabled={locked}>
        <legend>已保存的映射草稿</legend>
        <label>
          草稿标识{' '}
          <input
            value={draftId}
            onChange={(e) => {
              if (!containsLocalPath(e.target.value)) setDraftId(e.target.value)
            }}
          />
        </label>
        <button type="button" disabled={!draftId.trim()} onClick={readDraft}>
          读取草稿
        </button>
        <button type="button" disabled={!safeDraft(state.draft)} onClick={saveDraft}>
          保存草稿
        </button>
        {draftNotice && <p role="status">{draftNotice}</p>}
      </fieldset>
      <MappingPage
        state={state}
        busy={locked}
        chooser={
          source
            ? {
                format: source.format,
                sheets: source.sheets,
                onReparse: chooseSource,
                suggestions: source.suggestions,
              }
            : undefined
        }
        error={
          commitRejection && !unknown
            ? {
                summary: `映射提交被拒绝（${commitRejection}）`,
                remedy: '草稿已保留。请核对项目版本和权限，必要时修改草稿并重新预览。',
              }
            : error
              ? {
                  summary: '映射操作未完成',
                  remedy: '请核对数据源、草稿版本或已提交状态。已有草稿请先读取再编辑。',
                }
              : undefined
        }
        onDraft={(draft) => {
          if (!containsLocalPath(JSON.stringify(draft))) {
            clearProposal()
            setState((old) => updateDraft(old, draft))
          }
        }}
        onChooseSource={() => chooseSource()}
        onPreview={() => preview(0)}
        samplePage={
          state.preview
            ? {
                offset: state.preview.offset ?? 0,
                total: state.preview.totalRows ?? 0,
                limit: PAGE_SIZE,
                onPage: preview,
              }
            : undefined
        }
        onPrepareCommit={prepare}
        onConfirmation={(confirmed) => setState((old) => ({ ...old, confirmed }))}
        onCancel={() => {
          if (!locked) {
            setState(cancelPreview)
            clearProposal()
          }
        }}
      />
      {proposal && (
        <fieldset disabled={busy || unknown}>
          <legend>检查正式 ChangeSet</legend>
          <ol aria-label="已核验变更明细">
            {proposal.diff.rows.map((row, index) => (
              <li key={index}>
                <pre>{JSON.stringify(row, null, 2)}</pre>
              </li>
            ))}
          </ol>
          <label>
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
            />
            我已检查全部变更，确认提交到当前项目
          </label>
          <button type="button" disabled={!consent} onClick={commit}>
            提交映射 ChangeSet
          </button>
          <button type="button" onClick={clearProposal}>
            放弃本次 ChangeSet
          </button>
        </fieldset>
      )}
      {unknown && !busy && (
        <div role="alert">
          <p>提交结果尚待核对。请读取原操作的持久任务状态，或在人工确认项目状态后解除锁定。</p>
          <button type="button" onClick={reconcileCommit}>
            核对提交状态
          </button>
          <button
            type="button"
            onClick={() => {
              setUnknown(false)
              clearProposal()
              setState(cancelPreview)
            }}
          >
            已人工核对，解除提交锁定
          </button>
        </div>
      )}
    </>
  )
}
