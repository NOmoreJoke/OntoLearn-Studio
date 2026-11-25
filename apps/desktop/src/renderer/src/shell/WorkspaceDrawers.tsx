import type { JobView, ProgressView } from '@ontolearn/contracts'
import { ProjectCheckpointRestorePanel } from '../project/ProjectCheckpointRestorePanel'
import type { ProjectRestoreController } from '../project/restore-controller'
import { jobStatus } from '../task-presentation'

export type WorkspaceDrawersProps = {
  visible: boolean
  checkpointsOpen: boolean
  jobsOpen: boolean
  hasRecovery: boolean
  checkpointCtl?: ProjectRestoreController
  checkpointsDisabled: boolean
  destructiveBlocked: boolean
  projectId: string
  inputSnapshotId: string
  jobs: readonly JobView[]
  progress: Record<string, ProgressView>
  summaries: Record<string, string>
  connectionOffline: boolean
  controlsBusy: boolean
  onCloseCheckpoints(): void
  onCloseJobs(): void
  onRestoreTasks(): void
  onCancelJob(jobId: string): void
  onInspectOperation(job: JobView): void
  onLoadSummary(job: JobView): void
  renderJobError(job: JobView): React.ReactNode
}

export function WorkspaceDrawers({
  visible,
  checkpointsOpen,
  jobsOpen,
  hasRecovery,
  checkpointCtl,
  checkpointsDisabled,
  destructiveBlocked,
  inputSnapshotId,
  jobs,
  progress,
  summaries,
  connectionOffline,
  controlsBusy,
  onCloseCheckpoints,
  onCloseJobs,
  onRestoreTasks,
  onCancelJob,
  onInspectOperation,
  onLoadSummary,
  renderJobError,
}: WorkspaceDrawersProps) {
  if (!visible) return null
  const showCheckpoints = Boolean(checkpointCtl && (checkpointsOpen || hasRecovery))
  if (!showCheckpoints && !jobsOpen) return null

  return (
    <div className="workspace-drawers" data-testid="workspace-drawers">
      {showCheckpoints && checkpointCtl && (
        <section className="workspace-drawer-card" aria-label="检查点恢复抽屉">
          <div className="workspace-drawer-head">
            <span>整项目检查点与安全恢复</span>
            {!hasRecovery && (
              <button type="button" className="topbar-chip-btn" onClick={onCloseCheckpoints}>
                收起检查点
              </button>
            )}
          </div>
          <ProjectCheckpointRestorePanel
            controller={checkpointCtl}
            disabled={checkpointsDisabled}
            destructiveBlocked={destructiveBlocked}
          />
        </section>
      )}
      {jobsOpen && (
        <section
          className="workspace-drawer-card health-panel"
          aria-label="后台任务状态"
          data-testid="workspace-jobs-drawer"
        >
          <div className="workspace-drawer-head">
            <div>
              <h2>后台任务</h2>
              <p>窗口恢复后读取持久状态；不会重发写任务。</p>
            </div>
            <div className="workspace-drawer-actions">
              <button
                type="button"
                onClick={onRestoreTasks}
                disabled={controlsBusy || connectionOffline}
              >
                刷新任务状态
              </button>
              <button type="button" className="topbar-chip-btn" onClick={onCloseJobs}>
                收起
              </button>
            </div>
          </div>
          {jobs.length === 0 ? (
            <p className="drawer-empty">当前项目暂无后台执行记录。</p>
          ) : (
            <div className="drawer-job-list">
              {jobs.map((job) => (
                <article key={job.jobId} data-testid="durable-job" data-job-id={job.jobId}>
                  <p>
                    {connectionOffline ? '最后记录：' : ''}
                    {jobStatus(job)} · 状态版本 {job.stateVersion}
                  </p>
                  <p>
                    输入快照 {job.inputSnapshotId.slice(0, 12)} ·
                    {job.inputSnapshotId === inputSnapshotId
                      ? '当前输入'
                      : '历史输入；此任务保留原执行依据'}
                  </p>
                  {progress[job.jobId] &&
                    ['queued', 'running', 'cancelling'].includes(job.state) && (
                      <p>
                        阶段：
                        {
                          {
                            queued: '排队',
                            loading: '加载',
                            computing: '计算',
                            committing: '提交',
                            reconciling: '对账',
                          }[progress[job.jobId]!.stage]
                        }
                        {progress[job.jobId]!.total !== null
                          ? ` · ${progress[job.jobId]!.completed}/${progress[job.jobId]!.total}`
                          : ''}
                      </p>
                    )}
                  {job.error && renderJobError(job)}
                  <div className="drawer-job-buttons">
                    {['queued', 'running'].includes(job.state) && (
                      <button
                        type="button"
                        disabled={connectionOffline}
                        onClick={() => onCancelJob(job.jobId)}
                      >
                        请求取消
                      </button>
                    )}
                    <button
                      type="button"
                      disabled={connectionOffline}
                      onClick={() => onInspectOperation(job)}
                    >
                      查看提交点
                    </button>
                    {job.resultRef && (
                      <button
                        type="button"
                        disabled={connectionOffline}
                        onClick={() => onLoadSummary(job)}
                      >
                        查看运行摘要
                      </button>
                    )}
                  </div>
                  {summaries[job.jobId] && <p>{summaries[job.jobId]}</p>}
                </article>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
