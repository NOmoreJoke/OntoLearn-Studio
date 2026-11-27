/** Private component harness. Synthetic observations are display inputs, never engine evidence. */
import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import { QualityWorkspace } from '../../../apps/desktop/src/renderer/src/quality/QualityWorkspace'
import type { QualityObservation } from '../../../apps/desktop/src/renderer/src/quality/presentation'

const observation: QualityObservation = {
  projectId: 'project-a',
  inputSnapshotId: 'synthetic-snapshot',
  inputVersion: 7,
  constraintVersion: 'constraint-v2',
  ruleVersion: 'rule-v3',
  executionSemanticsVersion: 'synthetic-display-only',
  dataScope: 'asserted',
  includesDerived: false,
  resultState: 'stale',
  staleReasons: ['facts.changed'],
  checks: [
    { category: 'parse', state: 'passed', detail: 'synthetic parse display' },
    { category: 'shacl', state: 'failed', detail: 'synthetic report display' },
    { category: 'rules', state: 'unsupported', detail: 'synthetic unsupported display' },
    { category: 'reasoning', state: 'not-executed', detail: 'synthetic unexecuted display' },
  ],
  findings: [
    {
      id: 'synthetic-finding',
      severity: 'repair',
      message: 'SYNTHETIC FINDING: missing name',
      target: { kind: 'constraint', id: 'name-required' },
    },
  ],
  expected: [['urn:001', 'urn:type', '<urn:Risk>']],
  actual: [['urn:002', 'urn:type', '<urn:Risk>']],
  difference: null,
  trace: [],
}

function Harness() {
  const [projectId, setProjectId] = useState('project-a')
  const [showObservation, setShowObservation] = useState(false)
  const [located, setLocated] = useState('')
  return (
    <>
      <h1>T05 component harness: synthetic props only</h1>
      <label htmlFor="harness-project">Harness project</label>
      <select
        id="harness-project"
        value={projectId}
        onChange={(event) => setProjectId(event.target.value)}
      >
        <option value="project-a">Project A</option>
        <option value="project-b">Project B</option>
      </select>
      <button type="button" onClick={() => setShowObservation(!showObservation)}>
        Toggle synthetic observation for A
      </button>
      <p role="status">Harness location: {located || '(none)'}</p>
      <QualityWorkspace
        projectId={projectId}
        observation={showObservation ? observation : null}
        onLocate={(target) => setLocated(`${projectId}/${target.kind}/${target.id}`)}
      />
    </>
  )
}

createRoot(document.getElementById('root')!).render(<Harness />)
