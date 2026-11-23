import { useState, useSyncExternalStore } from 'react'
import type { ProjectCheckpointReason } from '@ontolearn/contracts'
import { explainError } from '../task-presentation'
import { ProjectRestoreController } from './restore-controller'
import './project.css'

const reasonLabels: Record<ProjectCheckpointReason, string> = {
  genesis: '初始状态',
  manual: '手动检查点',
  'before-run': '运行前快照',
  'guided-stage': '引导阶段完成',
  'before-agent': 'Agent 修改前',
  restore: '恢复操作',
  operation: '常规操作',
}

/** Whole-project checkpoint list and explicit segmented restore confirmation. */
export function ProjectCheckpointRestorePanel({
  controller,
  disabled,
  destructiveBlocked,
}: {
  controller: ProjectRestoreController
  disabled: boolean
  /** 未保存编辑或未完成操作时，恢复确认与执行必须先被用户收口，防止静默丢失。 */
  destructiveBlocked: boolean
}) {
  // getServerSnapshot keeps this panel renderable outside a live DOM subscription.
  const state = useSyncExternalStore(
    controller.subscribe,
    controller.getSnapshot,
    controller.getSnapshot,
  )
  const [label, setLabel] = useState('')
  // Typed consent is scoped to one preview (previewRef + documentHash). A new
  // preview, a cancelled preview or a different checkpoint must never reuse the
  // previous "恢复" input.
  const [consent, setConsent] = useState({ key: '', text: '' })
  const noProject = !state.selectedProjectId
  const blocked =
    disabled || state.busy || state.recovery.length > 0 || !state.recoveryLoaded || noProject
  const preview = state.preview
  const document = state.document
  const consentKey = preview ? `${preview.previewRef}:${preview.documentHash}` : ''
  const consentText = consent.key === consentKey ? consent.text : ''
  return (
    <div className="project-checkpoints" data-testid="project-checkpoints">
      <h3>检查点与整项目恢复</h3>
      <p>
        检查点覆盖元数据、草稿与学习当前状态；历史运行、审计与操作证物始终保留。
        整项目恢复与“撤销一次修改”是两个不同操作。
      </p>
      {noProject && (
        <p data-testid="checkpoint-no-project">
          尚未打开项目：请先在上方打开或创建项目，再使用检查点与整项目恢复。
        </p>
      )}
      {state.recovery.length > 0 && (
        <div role="alert" data-testid="restore-recovery">
          <p>存在结果未确认的恢复操作。请先核对原操作，勿重复提交。</p>
          {state.recovery.map((item) => (
            <button
              type="button"
              key={item.operationId}
              data-testid="restore-reconcile"
              disabled={state.busy}
              onClick={() => void controller.reconcile()}
            >
              核对原恢复操作
            </button>
          ))}
        </div>
      )}
      <div className="project-toolbar">
        <label>
          检查点备注
          <input
            data-testid="checkpoint-create-label"
            value={label}
            maxLength={256}
            disabled={blocked}
            onChange={(event) => setLabel(event.target.value)}
            placeholder="例如：导入映射之前"
          />
        </label>
        <button
          type="button"
          data-testid="checkpoint-create"
          disabled={blocked}
          onClick={() => void controller.createCheckpoint(label)}
        >
          创建手动检查点
        </button>
        <button
          type="button"
          data-testid="checkpoint-list-refresh"
          disabled={blocked}
          onClick={() => void controller.refresh()}
        >
          刷新检查点
        </button>
      </div>
      {state.list && (
        <ul className="checkpoint-catalog" data-testid="checkpoint-list">
          {state.list.items.map((item) => (
            <li key={item.checkpointRef} data-checkpoint-ref={item.checkpointRef}>
              <span data-testid="checkpoint-item-summary">
                #{item.operationSequence} · {reasonLabels[item.reason]}
                {item.label ? `「${item.label}」` : ''} · 域修订 {item.domainRevision} · 应用序号{' '}
                {item.operationSequence}
                {item.isCurrent ? ' · 当前' : ''}
              </span>
              <span className="checkpoint-counts">
                定义 {item.counts.definitions} · 事实 {item.counts.facts} · 草稿{' '}
                {item.counts.drafts}
              </span>
              <button
                type="button"
                data-testid="checkpoint-restore-preview"
                data-checkpoint-ref={item.checkpointRef}
                disabled={blocked || item.isCurrent}
                onClick={() => void controller.previewRestore(item.checkpointRef)}
              >
                预览恢复快照
              </button>
            </li>
          ))}
        </ul>
      )}
      {state.list?.nextCursor && (
        <button
          type="button"
          data-testid="checkpoint-list-next"
          disabled={blocked}
          onClick={() => void controller.refresh(state.list!.nextCursor)}
        >
          下一页检查点
        </button>
      )}
      {preview && document && (
        <div className="restore-preview" data-testid="restore-preview">
          <h4>
            恢复到 #{preview.targetOperationSequence}（域修订 {preview.targetDomainRevision}）
          </h4>
          <p data-testid="restore-impact-meta">
            {document.domainWillRestore
              ? `将恢复本体/事实到目标快照（当前域修订 ${document.current.domainRevision} → 目标 ${document.target.domainRevision}），受影响的结果会标记过期。`
              : '目标检查点与当前领域内容相同，不会触发领域恢复。'}
            {` 元数据将恢复为「${document.metadata.after.name ?? '未命名'}」，模式 ${document.metadata.after.mode}。`}
            {` 覆盖后续操作 ${preview.interveningOperationCount} 项。`}
          </p>
          <p className="checkpoint-counts">
            覆盖范围：{document.coverage.join('、')}。保留不变：{document.preserved.join('、')}。
          </p>
          {document.domainDiff.length > 0 && (
            <details data-testid="restore-impact-domain">
              <summary>领域差异（{document.domainDiff.length} 项）</summary>
              <ul>
                {document.domainDiff.map((item, index) => (
                  <li key={index}>{item.resource.join(' / ')}</li>
                ))}
              </ul>
            </details>
          )}
          <details data-testid="restore-impact-app">
            <summary>元数据 / 草稿 / 学习状态差异</summary>
            <ul>
              <li>
                名称：{String(document.metadata.before.name ?? '未命名')} →{' '}
                {String(document.metadata.after.name ?? '未命名')}
              </li>
              {document.drafts.map((draft) => (
                <li key={draft.editor}>
                  草稿 {draft.editor}：{draft.after ? '恢复内容' : '恢复为空'}
                </li>
              ))}
              {document.learning.map((record) => (
                <li key={record.attempt}>
                  学习 {record.attempt}：
                  {record.withdrawnByRestore ? '标记为本次恢复撤回（保留记录）' : '恢复进度'}
                </li>
              ))}
            </ul>
          </details>
          <details data-testid="restore-impact-ops" open>
            <summary>将被覆盖的后续操作（{document.interveningOperations.length} 项）</summary>
            <ul>
              {document.interveningOperations.map((operation) => (
                <li key={operation.operationId}>
                  #{operation.sequence} · {operation.operationKind} · {operation.changeType}
                </li>
              ))}
            </ul>
          </details>
          <p data-testid="restore-read-progress" data-complete={document ? 'true' : 'false'}>
            影响文档 {preview.manifest.totalBytes} 字节，已完整读取 {state.readSegmentHashes.length}
            /{preview.manifest.segmentCount} 段。
          </p>
          {!state.confirmation && (
            <>
              {destructiveBlocked && (
                <p data-testid="restore-destructive-blocked">
                  存在未保存编辑或未完成操作；恢复会覆盖后续修改。请先保存并核对，再确认恢复。
                </p>
              )}
              <button
                type="button"
                data-testid="restore-confirm"
                disabled={
                  blocked ||
                  destructiveBlocked ||
                  state.readSegmentHashes.length < preview.manifest.segmentCount
                }
                onClick={() => void controller.confirmRestore()}
              >
                我已完整阅读影响，确认恢复
              </button>{' '}
              <button
                type="button"
                data-testid="restore-cancel"
                disabled={state.busy}
                onClick={() => controller.cancelPreview()}
              >
                取消
              </button>
            </>
          )}
          {state.confirmation && (
            <>
              <p>已确认。输入“恢复”以执行整项目恢复（不可与撤销单次修改混淆）。</p>
              <input
                data-testid="restore-consent"
                value={consentText}
                disabled={state.busy}
                onChange={(event) => setConsent({ key: consentKey, text: event.target.value })}
                placeholder="恢复"
                aria-label="恢复确认输入"
              />
              <button
                type="button"
                data-testid="restore-apply"
                disabled={blocked || destructiveBlocked || consentText !== '恢复'}
                onClick={() => void controller.applyRestore()}
              >
                执行整项目恢复
              </button>{' '}
              <button
                type="button"
                data-testid="restore-cancel"
                disabled={state.busy}
                onClick={() => controller.cancelPreview()}
              >
                取消
              </button>
            </>
          )}
        </div>
      )}
      {state.notice && (
        // No role="status" here: this panel lives inside the project-library
        // section, whose own single live region must stay the only status role
        // for that scope. aria-live keeps the announcement without breaking
        // the enclosing role="status" structure.
        <p data-testid="checkpoint-notice" aria-live="polite">
          {state.notice}
        </p>
      )}
      {state.error && (
        <div role="alert" data-testid="checkpoint-error">
          {explainError(state.error, 'task').what} {explainError(state.error, 'task').why}
          {state.error.code === 'REVISION_CONFLICT' && ' 版本已变化：请刷新检查点后重新预览。'}
        </div>
      )}
      {state.list && state.list.items.length === 0 && <p>暂无检查点。</p>}
    </div>
  )
}
