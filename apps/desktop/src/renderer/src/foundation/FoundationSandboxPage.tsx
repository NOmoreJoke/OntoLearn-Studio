import { useState } from 'react'
import {
  FOUNDATION_MICRO_STEPS,
  type FoundationMicroStepId,
} from '../learning/scenarios/retail-membership-orders'
import { ExcelTripleBuilder } from './ExcelTripleBuilder'
import { LiveTripleMiniGraph } from './LiveTripleMiniGraph'
import { PrdConceptClinic } from './PrdConceptClinic'
import {
  INITIAL_STEP_TRIPLE,
  REIFIED_SO101_TRIPLES,
  type SandboxMode,
  type SandboxTriple,
} from './foundation-types'
import './foundation.css'

export type FoundationSandboxPageProps = {
  activeStep: FoundationMicroStepId
  hasProject: boolean
  onSelectStep(stepId: FoundationMicroStepId): void
  onApplyDraftToOntology(triples: readonly SandboxTriple[]): void
}

export function FoundationSandboxPage({
  activeStep,
  hasProject,
  onSelectStep,
  onApplyDraftToOntology,
}: FoundationSandboxPageProps) {
  const stepMeta =
    FOUNDATION_MICRO_STEPS.find((s) => s.id === activeStep) ?? FOUNDATION_MICRO_STEPS[0]!
  const [modeOverride, setModeOverride] = useState<Record<string, SandboxMode>>({})
  const [triples, setTriples] = useState<SandboxTriple[]>(() => [INITIAL_STEP_TRIPLE[activeStep]])
  const [completedSteps, setCompletedSteps] = useState<Record<string, boolean>>({})
  const [reified, setReified] = useState(false)

  const currentMode: SandboxMode = modeOverride[activeStep] ?? stepMeta.recommendedMode
  const completedCount = FOUNDATION_MICRO_STEPS.filter((s) => completedSteps[s.id]).length

  function addTripleAndComplete(triple: SandboxTriple) {
    setTriples((prev) => (prev.some((item) => item.id === triple.id) ? prev : [...prev, triple]))
    setCompletedSteps((prev) => ({ ...prev, [activeStep]: true }))
  }

  function handleStepSwitch(nextStepId: FoundationMicroStepId) {
    onSelectStep(nextStepId)
    const preset = INITIAL_STEP_TRIPLE[nextStepId]
    setTriples((prev) => (prev.some((item) => item.id === preset.id) ? prev : [...prev, preset]))
  }

  function handleReifyOrderModel() {
    setReified(true)
    setTriples((prev) => {
      const existing = new Set(prev.map((t) => t.id))
      return [...prev, ...REIFIED_SO101_TRIPLES.filter((t) => !existing.has(t.id))]
    })
    setCompletedSteps((prev) => ({ ...prev, 'step-05': true }))
  }

  return (
    <section
      className="foundation-sandbox-page"
      data-testid="foundation-sandbox-page"
      aria-label="00 三元组与概念沙盒"
    >
      <header className="foundation-hero">
        <div>
          <p className="foundation-eyebrow">ZERO-CODE SANDBOX · 00 底层本体概念预热</p>
          <h1>{stepMeta.title}</h1>
          <p className="foundation-subtitle">{stepMeta.conceptSummary}</p>
        </div>
        <div className="foundation-hero-meta">
          <span className="foundation-scale-pill">知味茶饮 · 微缩沙盒 10 行</span>
          <span className="foundation-progress-pill" data-testid="foundation-progress-pill">
            已练通 {completedCount} / {FOUNDATION_MICRO_STEPS.length} 步
          </span>
          <button
            type="button"
            className="foundation-clear-btn"
            data-testid="sandbox-clear-graph"
            onClick={() => setTriples([])}
          >
            清空图谱画布
          </button>
        </div>
      </header>

      <nav className="foundation-stepper" aria-label="六步底层元概念关卡">
        {FOUNDATION_MICRO_STEPS.map((step) => {
          const isCurrent = step.id === activeStep
          const isDone = Boolean(completedSteps[step.id])
          return (
            <button
              key={step.id}
              type="button"
              className={`foundation-step-tab${isCurrent ? ' is-current' : ''}${isDone ? ' is-done' : ''}`}
              data-testid="foundation-step-tab"
              data-step-id={step.id}
              aria-current={isCurrent ? 'step' : undefined}
              onClick={() => handleStepSwitch(step.id)}
            >
              <span className="step-tab-num">
                {isDone ? '✓ ' : ''}
                {step.num}
              </span>
              <span className="step-tab-title">{step.title.split('（')[0]}</span>
            </button>
          )
        })}
      </nav>

      <div className="foundation-mode-bar">
        <div className="foundation-mode-toggle" role="group" aria-label="沙盒练习模式切换">
          <button
            type="button"
            data-testid="foundation-mode-excel"
            aria-pressed={currentMode === 'excel'}
            onClick={() => setModeOverride((prev) => ({ ...prev, [activeStep]: 'excel' }))}
          >
            Excel 拆积木沙盒
          </button>
          <button
            type="button"
            data-testid="foundation-mode-clinic"
            aria-pressed={currentMode === 'clinic'}
            onClick={() => setModeOverride((prev) => ({ ...prev, [activeStep]: 'clinic' }))}
          >
            PRD 圈词与坏模型诊所
          </button>
        </div>
        <span className="foundation-goal-chip">本步目标：{stepMeta.targetOutcome}</span>
      </div>

      <div className="foundation-main-split">
        <div className="foundation-builder-column">
          {currentMode === 'excel' ? (
            <ExcelTripleBuilder
              key={`${activeStep}:${stepMeta.defaultTable}`}
              activeStep={activeStep}
              defaultTable={stepMeta.defaultTable}
              onAddTriple={addTripleAndComplete}
            />
          ) : (
            <PrdConceptClinic
              hasProject={hasProject}
              reified={reified}
              onReifyOrderModel={handleReifyOrderModel}
              onApplyDraftToOntology={onApplyDraftToOntology}
            />
          )}
        </div>

        <LiveTripleMiniGraph
          triples={triples}
          onRemoveTriple={(id) => setTriples((prev) => prev.filter((item) => item.id !== id))}
        />
      </div>
    </section>
  )
}
