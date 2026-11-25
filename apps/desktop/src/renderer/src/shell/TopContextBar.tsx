import type { WorkspaceModule } from './shell-routing'
import { stepMetaForWorkspace } from './shell-routing'

export type TopContextBarProps = {
  visible: boolean
  projectName?: string
  projectRevision: number
  projectBusy: boolean
  projectNotice: string
  workspaceModule: WorkspaceModule
  focusedTaskId?: string
  workspaceMode: 'guided' | 'assisted'
  railOpen: boolean
  checkpointsDrawerOpen: boolean
  jobsDrawerOpen: boolean
  jobCount: number
  onOpenMobileNav(): void
  onBackToProjects(): void
  onToggleCheckpointsDrawer(): void
  onToggleJobsDrawer(): void
  onToggleRail(): void
}

export function TopContextBar({
  visible,
  projectName,
  projectRevision,
  projectBusy,
  projectNotice,
  workspaceModule,
  focusedTaskId,
  workspaceMode,
  railOpen,
  checkpointsDrawerOpen,
  jobsDrawerOpen,
  jobCount,
  onOpenMobileNav,
  onBackToProjects,
  onToggleCheckpointsDrawer,
  onToggleJobsDrawer,
  onToggleRail,
}: TopContextBarProps) {
  if (!visible) return null
  const step = stepMetaForWorkspace(workspaceModule, focusedTaskId)
  const statusMessage = projectBusy ? '正在处理…' : projectNotice

  return (
    <header className="context-topbar" data-testid="context-topbar">
      <div className="context-topbar-left">
        <button
          type="button"
          className="mobile-nav-trigger"
          data-testid="mobile-nav-toggle"
          aria-label="打开导航菜单"
          onClick={onOpenMobileNav}
        >
          ☰
        </button>
        <div className="context-breadcrumb">
          <span className="context-step-pill">
            {step.num} · {step.label}
          </span>
          <strong className="context-project-name">{projectName ?? '当前项目'}</strong>
          <span className="context-version-badge" data-testid="selected-project-version">
            当前项目版本 {projectRevision}
          </span>
          <span className="context-mode-badge">
            {workspaceMode === 'assisted' ? '辅助模式' : '引导模式'}
          </span>
        </div>
      </div>

      <div className="context-topbar-actions">
        {statusMessage && (
          <div
            className="context-status-pill"
            data-testid="project-status-notice"
            role="status"
            aria-live="polite"
          >
            {statusMessage}
          </div>
        )}
        <button type="button" className="topbar-chip-btn" onClick={onBackToProjects}>
          切换项目
        </button>
        <button
          type="button"
          className="topbar-chip-btn"
          data-testid="topbar-checkpoints-toggle"
          aria-expanded={checkpointsDrawerOpen}
          onClick={onToggleCheckpointsDrawer}
        >
          检查点恢复
        </button>
        <button
          type="button"
          className="topbar-chip-btn"
          data-testid="topbar-jobs-toggle"
          aria-expanded={jobsDrawerOpen}
          onClick={onToggleJobsDrawer}
        >
          后台任务 ({jobCount})
        </button>
        <button
          type="button"
          className="topbar-rail-btn"
          data-testid="mentor-panel-toggle"
          aria-expanded={railOpen}
          onClick={onToggleRail}
        >
          {railOpen ? '收起辅助栏' : '展开导师与助手'}
        </button>
      </div>
    </header>
  )
}
