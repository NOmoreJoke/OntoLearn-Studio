import { useState, useSyncExternalStore } from 'react'
import type { MainlineManagementAction, MainlineManagementCatalogState } from '@ontolearn/contracts'
import { explainError } from '../task-presentation'
import { ProjectManagementController } from './management-controller'
import './project.css'

const actionLabels: Record<MainlineManagementAction['kind'], string> = {
  rename: '重命名项目',
  archive: '更改归档状态',
  'set-mode': '切换界面模式',
  'copy-current': '复制当前项目状态',
  trash: '移至回收站',
  'restore-trash': '恢复项目',
}
const filters: Array<[MainlineManagementCatalogState, string]> = [
  ['active', '使用中'],
  ['archived', '已归档'],
  ['trashed', '回收站'],
]

export function ProjectManagementPanel({
  controller,
  disabled,
  destructiveBlocked,
  openProject,
}: {
  controller: ProjectManagementController
  disabled: boolean
  destructiveBlocked: boolean
  openProject: (projectId: string) => void
}) {
  const state = useSyncExternalStore(controller.subscribe, controller.getSnapshot)
  const [name, setName] = useState('')
  const [consent, setConsent] = useState('')
  const [deleteOffer, setDeleteOffer] = useState<string>()
  const blocked =
    disabled || state.busy || !!state.pending || state.recovery.length > 0 || !state.recoveryLoaded
  const selected = state.selected
  const preview = state.preview
  const consentKey = preview ? `${preview.previewRef}:${preview.documentHash}` : ''
  return (
    <div className="project-management" data-testid="project-management">
      <div className="project-toolbar" aria-label="项目目录筛选">
        {filters.map(([filter, label]) => (
          <button
            type="button"
            key={filter}
            aria-pressed={state.filter === filter}
            disabled={blocked}
            onClick={() => void controller.refresh(filter)}
          >
            {label}
          </button>
        ))}
        <button
          type="button"
          data-testid="project-list-refresh"
          disabled={blocked}
          onClick={() => void controller.refresh()}
        >
          刷新项目列表
        </button>
      </div>
      {state.filter === 'trashed' && (
        <p>回收站保留数据和历史，不释放磁盘空间。恢复不会续跑旧任务。</p>
      )}
      {state.catalog && (
        <>
          <ul className="project-catalog">
            {state.catalog.items.map((item) => (
              <li key={item.projectId} data-project-id={item.projectId}>
                <span>
                  {item.metadata.name ?? '未命名项目'} · 版本 {item.domainRevision}
                  {item.metadata.archived ? ' · 已归档' : ''}
                </span>
                {item.lifecycle.state === 'trashed' ? (
                  <button
                    type="button"
                    data-testid="project-restore-trash"
                    data-project-id={item.projectId}
                    disabled={blocked}
                    onClick={() => void controller.preview({ kind: 'restore-trash' }, item)}
                  >
                    预览恢复
                  </button>
                ) : (
                  <button
                    type="button"
                    data-testid="project-open"
                    data-project-id={item.projectId}
                    disabled={blocked}
                    onClick={() => openProject(item.projectId)}
                  >
                    打开
                  </button>
                )}
              </li>
            ))}
          </ul>
          {state.catalog.total === 0 && <p>此目录暂无项目。</p>}
          <p>
            共 {state.catalog.total} 个项目 · 从第 {state.catalog.offset + 1} 项开始
          </p>
          {state.catalog.nextCursor && (
            <button
              type="button"
              disabled={blocked}
              onClick={() => void controller.refresh(state.filter, state.catalog!.nextCursor)}
            >
              下一页
            </button>
          )}
        </>
      )}
      {state.selectedProjectId && (
        <section aria-label="当前项目管理" className="project-settings">
          <h3>{selected?.metadata.name ?? '当前项目'}</h3>
          {selected?.metadata.archived && <p>已归档。仍可显式编辑和运行；归档只整理目录。</p>}
          <label htmlFor="project-management-name">新名称或副本名称</label>
          <input
            id="project-management-name"
            value={name}
            maxLength={4096}
            disabled={blocked}
            onChange={(event) => setName(event.target.value)}
          />
          <div className="project-toolbar">
            <button
              type="button"
              disabled={blocked || !name.trim()}
              onClick={() => void controller.preview({ kind: 'rename', name })}
            >
              预览重命名
            </button>
            <button
              type="button"
              disabled={blocked || !name.trim() || destructiveBlocked}
              onClick={() => void controller.preview({ kind: 'copy-current', name })}
            >
              预览复制当前状态
            </button>
            <button
              type="button"
              disabled={blocked || !selected}
              onClick={() =>
                void controller.preview({ kind: 'archive', archived: !selected!.metadata.archived })
              }
            >
              {selected?.metadata.archived ? '预览取消归档' : '预览归档'}
            </button>
            <button
              type="button"
              disabled={blocked || destructiveBlocked}
              onClick={() => setDeleteOffer(state.selectedProjectId)}
            >
              删除项目…
            </button>
          </div>
          <label htmlFor="project-mode">界面模式</label>
          <select
            id="project-mode"
            value={selected?.metadata.mode ?? 'guided'}
            disabled={blocked || !selected}
            onChange={(event) =>
              void controller.preview({
                kind: 'set-mode',
                mode: event.target.value as 'guided' | 'assisted',
              })
            }
          >
            <option value="guided">引导模式</option>
            <option value="assisted">辅助模式</option>
          </select>
          <p>切换只改变界面帮助的披露程度；当前编辑器、草稿和项目数据保持。</p>
          <p>完整项目导出尚待接入，查询 CSV 不等同于完整项目包。</p>
          {destructiveBlocked && <p>复制或删除前，请先保存编辑并核对未完成操作。</p>}
          {deleteOffer && deleteOffer === state.selectedProjectId && (
            <div role="dialog" aria-label="选择归档或删除" className="project-confirmation">
              <h4>建议先归档</h4>
              <p>
                归档保留项目并整理目录。移至回收站后，正常编辑和运行入口将关闭；数据和历史仍保留。
              </p>
              <button
                type="button"
                disabled={blocked}
                onClick={() => {
                  setDeleteOffer(undefined)
                  void controller.preview({ kind: 'archive', archived: true })
                }}
              >
                预览归档（推荐）
              </button>
              <button
                type="button"
                disabled={blocked || destructiveBlocked}
                onClick={() => {
                  setDeleteOffer(undefined)
                  void controller.preview({ kind: 'trash' })
                }}
              >
                仍要移至回收站：查看影响
              </button>
              <button type="button" onClick={() => setDeleteOffer(undefined)}>
                取消
              </button>
            </div>
          )}
        </section>
      )}
      {preview && (
        <section
          role="dialog"
          aria-label="项目管理确认"
          className="project-confirmation"
          data-testid="project-management-preview"
        >
          <h3>{actionLabels[preview.action.kind]}</h3>
          <p>项目：{preview.document.projectName ?? '未命名项目'}</p>
          <dl>
            <dt>名称</dt>
            <dd>
              {preview.document.beforeMetadata.name ?? '未命名'} →{' '}
              {preview.document.afterMetadata.name ?? '未命名'}
            </dd>
            <dt>归档</dt>
            <dd>
              {preview.document.beforeMetadata.archived ? '已归档' : '未归档'} →{' '}
              {preview.document.afterMetadata.archived ? '已归档' : '未归档'}
            </dd>
            <dt>模式</dt>
            <dd>
              {preview.document.beforeMetadata.mode} → {preview.document.afterMetadata.mode}
            </dd>
            <dt>版本</dt>
            <dd>
              领域 {preview.document.domainRevision} · 设置 {preview.document.metadataVersion} ·
              操作 {preview.document.operationSequence} · 生命周期{' '}
              {preview.document.lifecycleVersion}
            </dd>
            <dt>数据</dt>
            <dd>
              定义 {preview.document.counts.definitions} · 事实 {preview.document.counts.facts} ·
              墓碑 {preview.document.counts.tombstones} · 草稿 {preview.document.counts.drafts} ·
              学习记录 {preview.document.counts.learning} · 历史运行{' '}
              {preview.document.counts.historyRuns} · 活跃任务 {preview.document.counts.activeJobs}
            </dd>
          </dl>
          <h4>本次覆盖</h4>
          <ul>
            {preview.document.coverage.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
          <h4>保留或排除</h4>
          <ul>
            {preview.document.exclusions.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
          {preview.action.kind === 'trash' && (
            <p>此次是移至回收站，不会永久删除历史，也不释放磁盘空间。</p>
          )}
          {preview.action.kind === 'copy-current' && (
            <p>副本具有独立身份；源项目的运行历史不成为副本的成功记录。</p>
          )}
          <details>
            <summary>查看完整版本标识</summary>
            <p>
              模板引用：
              <code>{preview.document.beforeMetadata.templateRef ?? 'null（无模板引用）'}</code>
              {' → '}
              <code>{preview.document.afterMetadata.templateRef ?? 'null（无模板引用）'}</code>
            </p>
            <p>
              元数据来源：<code>{preview.document.beforeMetadata.origin}</code>
              {' → '}
              <code>{preview.document.afterMetadata.origin}</code>
            </p>
            <p>
              检查点：<code>{preview.document.checkpointRef}</code>
            </p>
            <p>
              确认文档：<code>{preview.documentHash}</code>
            </p>
            {preview.document.seedHash && (
              <p>
                复制输入：<code>{preview.document.seedHash}</code>
              </p>
            )}
          </details>
          <label>
            <input
              type="checkbox"
              checked={consent === consentKey}
              onChange={(event) => setConsent(event.target.checked ? consentKey : '')}
              disabled={blocked}
            />
            我已核对本次完整范围与排除项
          </label>
          <button
            type="button"
            disabled={
              blocked ||
              consent !== consentKey ||
              ((preview.action.kind === 'trash' || preview.action.kind === 'copy-current') &&
                destructiveBlocked)
            }
            onClick={() => void controller.apply()}
          >
            确认并提交项目更改
          </button>
          <button type="button" disabled={blocked} onClick={() => controller.cancelPreview()}>
            取消本次更改
          </button>
        </section>
      )}
      {!state.recoveryLoaded && (
        <section aria-label="核对管理恢复状态">
          <p>尚未确认本机是否保留待核对操作，项目修改暂不可用。</p>
          <button
            type="button"
            disabled={state.busy || disabled}
            onClick={() => void controller.initialize()}
          >
            重新读取原操作记录
          </button>
        </section>
      )}
      {state.recovery.length > 0 && (
        <section aria-label="重启后待核对的项目管理操作">
          <h3>原操作结果待核对</h3>
          <p>只查询已记录的原操作，不会重放修改或再次创建副本。</p>
          {state.recovery.map((item) => (
            <div key={item.operationId}>
              <p>
                {item.label} · <code>{item.operationId}</code>
              </p>
              <button
                type="button"
                disabled={state.busy || disabled}
                onClick={() => void controller.reconcile(item.operationId)}
              >
                核对原操作 {item.label}
              </button>
            </div>
          ))}
        </section>
      )}
      {state.pending && (
        <section aria-label="待核对的项目管理操作">
          <p>
            原操作：<code>{state.pending.operationId}</code>。尚未确认最终结果，不会自动重发。
          </p>
          <button
            type="button"
            disabled={state.busy || disabled}
            onClick={() => void controller.reconcile()}
          >
            核对原管理操作
          </button>
        </section>
      )}
      {state.receipt?.kind === 'copy-current' && (
        <button
          type="button"
          data-testid="project-open-copy"
          disabled={blocked}
          onClick={() => openProject(state.receipt!.targetProjectId)}
        >
          打开已创建的副本
        </button>
      )}
      <p data-testid="project-management-notice" aria-live="polite">
        {state.busy ? '正在处理项目管理…' : state.notice}
      </p>
      {state.error && (
        <p role="alert">
          {explainError(state.error, 'task').what} {explainError(state.error, 'task').why}（
          {state.error.code}）
        </p>
      )}
    </div>
  )
}
