import type { HealthResult, LearningTaskStateDTO } from '@ontolearn/contracts'
import {
  COURSE_NAV_STEPS,
  isCourseNavStepActive,
  stepCourseStatus,
  type CourseNavStep,
  type PrimaryView,
  type WorkspaceModule,
} from './shell-routing'

export type SidebarNavProps = {
  primaryView: PrimaryView
  hasProject: boolean
  workspaceModule: WorkspaceModule
  focusedTaskId?: string
  workspaceControlsDisabled: boolean
  qualityStepDisabled: boolean
  learningTasks?: readonly LearningTaskStateDTO[]
  currentDomainSnapshotId?: string
  learningSnapshotRef?: string
  engineHealth?: HealthResult
  connectionOffline: boolean
  mobileOpen: boolean
  onCloseMobile(): void
  onSelectPrimaryView(view: PrimaryView): void
  onSelectStep(step: CourseNavStep): void
}

export function SidebarNav({
  primaryView,
  hasProject,
  workspaceModule,
  focusedTaskId,
  workspaceControlsDisabled,
  qualityStepDisabled,
  learningTasks,
  currentDomainSnapshotId,
  learningSnapshotRef,
  engineHealth,
  connectionOffline,
  mobileOpen,
  onCloseMobile,
  onSelectPrimaryView,
  onSelectStep,
}: SidebarNavProps) {
  const engineState = connectionOffline
    ? 'offline'
    : engineHealth
      ? engineHealth.ok
        ? 'ok'
        : 'error'
      : 'idle'

  const foundationDisabled = connectionOffline || (hasProject && workspaceControlsDisabled)

  return (
    <>
      {mobileOpen && (
        <div className="sidebar-backdrop" aria-hidden="true" onClick={() => onCloseMobile()} />
      )}
      <aside
        className="sidebar"
        data-mobile-open={mobileOpen ? 'true' : 'false'}
        aria-label="主导航栏"
      >
        <div className="sidebar-top">
          <div className="wordmark">
            <span className="brand-mark" aria-hidden="true">
              O
            </span>
            <strong>
              OntoLearn<span>STUDIO</span>
            </strong>
          </div>
          <button
            type="button"
            className="sidebar-close-btn"
            aria-label="关闭导航菜单"
            onClick={() => onCloseMobile()}
          >
            ✕
          </button>
        </div>
        <div className="side-label">本体学习与落地工作台</div>
        <nav aria-label="工作台导航">
          <div className="nav-group-label" aria-hidden="true">
            门户与路线
          </div>
          <a
            href="#overview"
            data-testid="nav-project-library"
            aria-current={primaryView === 'projects' ? 'page' : undefined}
            onClick={() => {
              onSelectPrimaryView('projects')
              onCloseMobile()
            }}
          >
            <span className="nav-item-label">项目工作台</span>
            <span aria-hidden="true">↗</span>
          </a>
          <a
            href="#learning-center"
            data-testid="nav-learning-center"
            aria-current={primaryView === 'learning' ? 'page' : undefined}
            onClick={() => {
              onSelectPrimaryView('learning')
              onCloseMobile()
            }}
          >
            <span className="nav-item-label">学习路线图</span>
            <span aria-hidden="true">08</span>
          </a>
          <a
            href="#model-settings"
            data-testid="nav-model-settings"
            aria-current={primaryView === 'settings' ? 'page' : undefined}
            onClick={(event) => {
              event.preventDefault()
              onSelectPrimaryView('settings')
              onCloseMobile()
            }}
          >
            模型设置
          </a>

          {hasProject ? (
            <>
              <div className="nav-group-label" aria-hidden="true">
                核心工作台 · 00–08
              </div>
              <a
                href="#foundation-sandbox"
                data-testid="nav-step-00"
                aria-current={primaryView === 'foundation' ? 'page' : undefined}
                aria-disabled={foundationDisabled}
                onClick={(event) => {
                  event.preventDefault()
                  if (foundationDisabled) return
                  onSelectPrimaryView('foundation')
                  onCloseMobile()
                }}
              >
                <span className="nav-step-main">
                  <span className="nav-step-num" aria-hidden="true">
                    00
                  </span>
                  <span className="nav-item-label">三元组与概念沙盒</span>
                </span>
              </a>
              {COURSE_NAV_STEPS.map((step) => {
                const disabled =
                  step.module === 'quality' ? qualityStepDisabled : workspaceControlsDisabled
                const active = isCourseNavStepActive(
                  step,
                  primaryView,
                  workspaceModule,
                  focusedTaskId,
                )
                const status = stepCourseStatus(
                  step,
                  learningTasks,
                  currentDomainSnapshotId,
                  learningSnapshotRef,
                )
                return (
                  <a
                    key={step.id}
                    href={step.href}
                    data-testid={`nav-step-${step.num}`}
                    aria-current={active ? 'page' : undefined}
                    aria-disabled={disabled}
                    aria-description={
                      status ? `第 ${step.num} 步，${status.text}` : `第 ${step.num} 步`
                    }
                    onClick={(event) => {
                      event.preventDefault()
                      if (disabled) return
                      onSelectStep(step)
                      onCloseMobile()
                    }}
                  >
                    <span className="nav-step-main">
                      <span className="nav-step-num" aria-hidden="true">
                        {step.num}
                      </span>
                      <span className="nav-item-label">{step.label}</span>
                    </span>
                    {status && (
                      <span className={`nav-step-badge is-${status.tone}`} aria-hidden="true">
                        {status.text}
                      </span>
                    )}
                  </a>
                )
              })}
            </>
          ) : (
            <>
              <div className="nav-group-label" aria-hidden="true">
                零代码概念预热 · 00
              </div>
              <a
                href="#foundation-sandbox"
                data-testid="nav-step-00"
                aria-current={primaryView === 'foundation' ? 'page' : undefined}
                aria-disabled={foundationDisabled}
                onClick={(event) => {
                  event.preventDefault()
                  if (foundationDisabled) return
                  onSelectPrimaryView('foundation')
                  onCloseMobile()
                }}
              >
                <span className="nav-step-main">
                  <span className="nav-step-num" aria-hidden="true">
                    00
                  </span>
                  <span className="nav-item-label">三元组与概念沙盒</span>
                </span>
              </a>
              <p className="nav-locked-hint">打开或创建项目后解锁 01–08 实操工作台。</p>
            </>
          )}
        </nav>

        <button
          type="button"
          className="sidebar-note sidebar-engine-btn"
          data-engine-state={engineState}
          onClick={() => {
            onSelectPrimaryView('projects')
            onCloseMobile()
          }}
        >
          <span className="sidebar-engine-head">
            <span className="status-dot" aria-hidden="true" />
            <span>
              {engineState === 'offline'
                ? '引擎已离线 · 点击对账'
                : engineState === 'error'
                  ? '引擎检查异常'
                  : engineState === 'ok' && engineHealth?.ok
                    ? `本地引擎 v${engineHealth.data.engineVersion}`
                    : '本地优先'}
            </span>
          </span>
          <span className="sidebar-engine-sub">
            无需配置模型 API，所有操作均先预览 Diff 后提交。
          </span>
        </button>
      </aside>
    </>
  )
}
