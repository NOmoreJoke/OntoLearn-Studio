import type { AgentDraftPlanDTO, AgentMode } from '@ontolearn/contracts'
import type { AgentContextSnapshot } from '../agent/agent-context-store'
import type { AgentAction } from '../agent/context-actions'
import { AgentPanel } from '../agent/agent-panel'
import type { QueryDraftDTO } from '../query/api002-source-types'
import type { LearningFixtureTaskId } from '../learning/content'
import type { LearningController } from '../learning/learning-controller'
import { MentorPanel } from '../learning/MentorPanel'

export type AssistantRailTab = 'mentor' | 'agent'

export type UnifiedAssistantRailProps = {
  open: boolean
  activeTab: AssistantRailTab
  onSelectTab(tab: AssistantRailTab): void
  onClose(): void
  projectId: string
  generation: number
  projectRevision: number
  inputSnapshotId: string
  learningCtl?: LearningController
  learningDisabled: boolean
  currentDomainSnapshotId?: string
  onOpenOntologyRepair(): void
  onOpenQueryWorkspace(): void
  onOpenQualityWorkspace(): void
  onOpenCheckpoints(): void
  onLoadTaskFixture(taskId: LearningFixtureTaskId): void
  taskFixture?: {
    taskId: LearningFixtureTaskId
    rows: readonly unknown[]
    approve(): void
    discard(): void
  }
  taskFixtureStatus?: string
  onResetToGBase(taskId: string): void
  refreshCheckpoints(): Promise<void>
  agentContext: AgentContextSnapshot
  modelSyncVersion: number
  onModeChange(mode: AgentMode): void | Promise<void>
  onQueryDraft(draft: QueryDraftDTO): void
  onDraftPlan(plan: AgentDraftPlanDTO): void
  onLocalAction(action: AgentAction): void | Promise<void>
}

export function UnifiedAssistantRail({
  open,
  activeTab,
  onSelectTab,
  onClose,
  projectId,
  generation,
  projectRevision,
  inputSnapshotId,
  learningCtl,
  learningDisabled,
  currentDomainSnapshotId,
  onOpenOntologyRepair,
  onOpenQueryWorkspace,
  onOpenQualityWorkspace,
  onOpenCheckpoints,
  onLoadTaskFixture,
  taskFixture,
  taskFixtureStatus,
  onResetToGBase,
  refreshCheckpoints,
  agentContext,
  modelSyncVersion,
  onModeChange,
  onQueryDraft,
  onDraftPlan,
  onLocalAction,
}: UnifiedAssistantRailProps) {
  return (
    <aside
      className="assistant-rail"
      data-testid="unified-assistant-rail"
      data-open={open ? 'true' : 'false'}
      hidden={!open}
      aria-label="课程导师与 AI 助手"
    >
      <div className="assistant-rail-bar">
        <div className="assistant-rail-tabs" role="tablist" aria-label="辅助面板切换">
          <button
            type="button"
            role="tab"
            data-testid="rail-tab-mentor"
            aria-selected={activeTab === 'mentor'}
            disabled={!learningCtl}
            onClick={() => onSelectTab('mentor')}
          >
            课程导师
          </button>
          <button
            type="button"
            role="tab"
            data-testid="rail-tab-agent"
            aria-selected={activeTab === 'agent'}
            onClick={() => onSelectTab('agent')}
          >
            AI 助手
          </button>
        </div>
        <button
          type="button"
          className="assistant-rail-close"
          aria-label="收起右侧辅助栏"
          onClick={onClose}
        >
          收起
        </button>
      </div>

      <div className="assistant-rail-body">
        {learningCtl && (
          <div
            role="tabpanel"
            aria-labelledby="rail-tab-mentor"
            hidden={!open || activeTab !== 'mentor'}
          >
            <MentorPanel
              controller={learningCtl}
              disabled={learningDisabled}
              currentDomainSnapshotId={currentDomainSnapshotId}
              onOpenOntologyRepair={onOpenOntologyRepair}
              onOpenQueryWorkspace={onOpenQueryWorkspace}
              onOpenQualityWorkspace={onOpenQualityWorkspace}
              onOpenCheckpoints={onOpenCheckpoints}
              onLoadTaskFixture={onLoadTaskFixture}
              taskFixture={taskFixture}
              taskFixtureStatus={taskFixtureStatus}
              onResetToGBase={onResetToGBase}
              refreshCheckpoints={refreshCheckpoints}
            />
          </div>
        )}
        <div
          role="tabpanel"
          aria-labelledby="rail-tab-agent"
          hidden={!open || (Boolean(learningCtl) && activeTab !== 'agent')}
        >
          <AgentPanel
            key={`${projectId}:${generation}`}
            projectId={projectId}
            projectRevision={projectRevision}
            inputSnapshotId={inputSnapshotId}
            module={agentContext.module}
            mode={agentContext.mode}
            selectedObjectIds={agentContext.selectedObjectIds}
            localActions={learningCtl ? ['hint', 'check', 'demonstrate'] : []}
            modelSyncVersion={modelSyncVersion}
            onModeChange={onModeChange}
            onQueryDraft={onQueryDraft}
            onDraftPlan={onDraftPlan}
            onLocalAction={onLocalAction}
          />
        </div>
      </div>
    </aside>
  )
}
