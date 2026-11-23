import type { LearningOriginChoiceDTO, LearningSelectedOriginsDTO } from '@ontolearn/contracts'
import './task-origins.css'

export type TaskOriginChoices = [LearningOriginChoiceDTO | '', LearningOriginChoiceDTO | '']

const lx01People = [
  'urn:ontolearn:learning:person/L01',
  'urn:ontolearn:learning:person/L02',
] as const

const questions = {
  quality: [
    { id: 'learning-lx01-origin-l01', label: 'person/L01 a Person' },
    { id: 'learning-lx01-origin-l02', label: 'person/L02 a Person' },
  ],
  'transfer-classify': [
    { id: 'learning-transfer-origin-0', label: 'equipment/201 name "检测泵"' },
    { id: 'learning-transfer-origin-1', label: 'equipment/201 a HighRiskEquipment' },
  ],
} as const

export function selectedTaskOrigins(
  taskId: string,
  [first, second]: TaskOriginChoices,
): LearningSelectedOriginsDTO | undefined {
  if (taskId === 'quality' && (first || second)) {
    return {
      ...(first ? { [lx01People[0]]: first } : {}),
      ...(second ? { [lx01People[1]]: second } : {}),
    }
  }
  if (taskId === 'transfer-classify' && first && second) return [first, second]
  return undefined
}

export function TaskOriginSelectors({
  taskId,
  values,
  disabled,
  onChange,
}: {
  taskId: string
  values: TaskOriginChoices
  disabled: boolean
  onChange: (choices: TaskOriginChoices) => void
}) {
  if (taskId !== 'quality' && taskId !== 'transfer-classify') return null
  return (
    <fieldset className="learning-origin-selectors" disabled={disabled}>
      <legend>{taskId === 'quality' ? 'LX-01：区分人员类型的来源' : '区分两条事实的来源'}</legend>
      {questions[taskId].map(({ id, label }, index) => (
        <label key={id}>
          {label}
          <select
            data-testid={id}
            value={values[index]}
            onChange={(event) => {
              const value = event.target.value
              if (value !== '' && value !== 'asserted' && value !== 'derived') return
              onChange(index === 0 ? [value, values[1]] : [values[0], value])
            }}
          >
            <option value="">未选择</option>
            <option value="asserted">断言事实 (asserted)</option>
            <option value="derived">推导结论 (derived)</option>
          </select>
        </label>
      ))}
    </fieldset>
  )
}
