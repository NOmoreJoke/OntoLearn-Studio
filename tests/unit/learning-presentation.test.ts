import { describe, expect, it } from 'vitest'
import {
  offlineCourse,
  offlineGlossary,
} from '../../apps/desktop/src/renderer/src/learning/content'
import {
  checkStatusLabels,
  recordLabel,
  observeRecord,
  observeRecords,
  contextKey,
  projectionRecord,
  sameContext,
  searchGlossary,
  statusLabel,
  validFeedback,
  validRecord,
} from '../../apps/desktop/src/renderer/src/learning/presentation'
import type {
  CheckStatus,
  LearningRecordView,
  TaskContext,
} from '../../apps/desktop/src/renderer/src/learning/types'

const context: TaskContext = {
  projectId: 'project-1',
  taskId: 'transfer-repair',
  attemptId: 'attempt-1',
  inputVersion: 'input-1',
}
function record(changes: Partial<LearningRecordView> = {}): LearningRecordView {
  return {
    context,
    recordVersion: 1,
    maxHintLevel: 0,
    assistance: 'independent',
    operationComplete: true,
    independentTransferSuccess: true,
    checkStatus: 'passed',
    evidenceIds: ['actual-result-ref'],
    ...changes,
  }
}

describe('learning UI trusted projections', () => {
  it('has all offline lessons, hints and required glossary explanations', () => {
    expect(offlineCourse.tasks.slice(0, 6).map((task) => task.module)).toEqual([
      '本体构建',
      '数据映射',
      '本体查询',
      '质量与推理',
      '行为定义',
      '沙盘预测',
    ])
    expect(offlineCourse.tasks.filter((task) => task.transfer).map((task) => task.id)).toEqual([
      'transfer-repair',
      'transfer-classify',
    ])
    for (const task of offlineCourse.tasks) {
      expect(task.hints.map((hint) => hint.level)).toEqual([1, 2, 3, 4])
      expect(task.completionCondition).not.toBe('')
    }
    for (const term of ['开放世界假设', '定义域', '值域']) {
      const entry = offlineGlossary.find((item) => item.term === term)!
      expect([entry.plain, entry.example, entry.technical].every(Boolean)).toBe(true)
    }
  })
  it.each(['projectId', 'taskId', 'attemptId', 'inputVersion'] as const)(
    'rejects a different %s',
    (field) => {
      const wrong = { ...context, [field]: 'different' }
      expect(sameContext(context, wrong)).toBe(false)
      expect(validRecord(record({ context: wrong }), context)).toBe(false)
    },
  )
  it.each([
    { maxHintLevel: 1 },
    { maxHintLevel: 4, assistance: 'partial-hints' as const },
    { evidenceIds: [] },
    { checkStatus: 'stale' as const },
    { checkStatus: 'failed' as const },
    { recordVersion: -1 },
    { maxHintLevel: 5 },
  ])('does not count contradictory or missing evidence as complete: %j', (changes) => {
    expect(validRecord(record(changes), context)).toBe(false)
  })
  it('separates assisted operation completion from independent transfer', () => {
    const assisted = record({
      maxHintLevel: 4,
      assistance: 'agent-full-assistance',
      independentTransferSuccess: false,
    })
    expect(validRecord(assisted, context)).toBe(true)
    expect(recordLabel(assisted)).toBe('使用 Agent 完整辅助')
    expect(validRecord({ ...assisted, independentTransferSuccess: true }, context)).toBe(false)
  })
  it('rejects old record versions and lowered assistance even on the same input', () => {
    const previous = record({
      recordVersion: 4,
      maxHintLevel: 4,
      assistance: 'agent-full-assistance',
      independentTransferSuccess: false,
    })
    const feedback = {
      context,
      record: record(),
      completed: ['完成'],
      repairs: [],
      suggestions: [],
      knowledgePoints: [],
    }
    expect(validFeedback(feedback, context, 4, previous)).toBe(false)
    expect(
      validFeedback(
        {
          ...feedback,
          record: { ...previous, recordVersion: 5, assistance: 'full-demonstration' },
        },
        context,
        4,
        previous,
      ),
    ).toBe(false)
    expect(
      validFeedback(
        { ...feedback, record: { ...previous, recordVersion: 5 } },
        context,
        4,
        previous,
      ),
    ).toBe(true)
  })
  it('never describes stale input as current completion', () => {
    expect(
      recordLabel(
        record({
          operationComplete: false,
          independentTransferSuccess: false,
          checkStatus: 'stale',
        }),
      ),
    ).toBe('结果已过期 · 请重新检查')
  })
  it('retains assistance floors across newer, older and same-version conflicting updates', () => {
    const assisted = record({
      recordVersion: 4,
      maxHintLevel: 4,
      assistance: 'agent-full-assistance',
      independentTransferSuccess: false,
    })
    let projected = observeRecord(undefined, assisted)
    projected = observeRecord(projected, record({ recordVersion: 5 }))
    expect(projectionRecord(projected, context)).toBeUndefined()
    expect(projected.floor.maxHintLevel).toBe(4)
    projected = observeRecord(projected, { ...assisted, recordVersion: 6 })
    expect(projectionRecord(projected, context)).toEqual({ ...assisted, recordVersion: 6 })
    projected = observeRecord(projected, {
      ...assisted,
      recordVersion: 6,
      evidenceIds: ['different'],
    })
    expect(projectionRecord(projected, context)).toBeUndefined()
    projected = observeRecord(projected, { ...assisted, recordVersion: 7 })
    expect(projectionRecord(projected, context)?.recordVersion).toBe(7)
    const earlierAssistance = observeRecord(
      observeRecord(undefined, record({ recordVersion: 9 })),
      assisted,
    )
    expect(projectionRecord(earlierAssistance, context)).toBeUndefined()
  })
  it('invalidates an old pass when a newer owner record is contradictory', () => {
    const old = record()
    let records = observeRecords({}, [old])
    records = observeRecords(records, [record({ recordVersion: 2, maxHintLevel: 4 })])
    expect(projectionRecord(records[contextKey(context)], context)).toBeUndefined()
    records = observeRecords(records, [
      record({
        recordVersion: 3,
        maxHintLevel: 4,
        assistance: 'full-demonstration',
        independentTransferSuccess: false,
      }),
    ])
    expect(
      projectionRecord(records[contextKey(context)], context)?.independentTransferSuccess,
    ).toBe(false)
  })
  it('blocks invalid owner values without poisoning recoverable assistance floors', () => {
    let projected = observeRecord(undefined, record())
    projected = observeRecord(projected, record({ recordVersion: 2, maxHintLevel: 5 }))
    expect(projectionRecord(projected, context)).toBeUndefined()
    expect(projected.floor.maxHintLevel).toBe(0)
    projected = observeRecord(
      projected,
      record({
        recordVersion: 3,
        maxHintLevel: 4,
        assistance: 'full-demonstration',
        independentTransferSuccess: false,
      }),
    )
    expect(projectionRecord(projected, context)?.maxHintLevel).toBe(4)
  })

  it('ships the offline-course-2 content with five mounted readings', () => {
    expect(offlineCourse.version).toBe('offline-course-2')
    expect(offlineCourse.firstTask).toBe('business-ontology')
    expect(offlineCourse.tasks).toHaveLength(9)
    const mounted = offlineCourse.tasks.flatMap((task) =>
      (task.readings ?? []).map((reading) => ({
        task: task.id,
        id: reading.id,
        optional: reading.optional,
      })),
    )
    expect(mounted).toEqual([
      { task: 'business-ontology', id: 'business-question', optional: false },
      { task: 'mapping', id: 'mapping-diff-read', optional: false },
      { task: 'query', id: 'query-scope-read', optional: false },
      { task: 'behavior', id: 'behavior-conflict-read', optional: false },
      { task: 'scenario', id: 'scenario-read', optional: true },
    ])
    const ids = mounted.map((item) => item.id)
    expect(new Set(ids).size).toBe(ids.length)
    for (const task of offlineCourse.tasks) {
      // Reading material is mounted, never inlined into the task itself.
      expect(task.readings?.length ?? 0).toBeGreaterThanOrEqual(0)
      for (const reading of task.readings ?? []) {
        expect(reading.content.length).toBeGreaterThan(0)
        expect(reading.sourceRef.length).toBeGreaterThan(0)
        for (const item of reading.selfAssessment ?? []) {
          expect(item.options.map((option) => option.id)).toContain(item.answerKey)
        }
      }
    }
    const business = offlineCourse.tasks.find((task) => task.id === 'business-ontology')!
    expect(business.steps?.[0]).toMatchObject({
      index: 0,
      scored: false,
      readingRef: 'business-question',
    })
    expect(business.hints[0].text).toContain('类回答是哪一类，个体回答是哪一个')
    expect(business.commonErrors.join('\n')).toContain('把具体人员建成类')
  })

  it('keeps the glossary at glossary-2 with boundary and alias on every entry', () => {
    expect(offlineGlossary).toHaveLength(27)
    for (const entry of offlineGlossary) {
      expect(entry.boundary.trim().length).toBeGreaterThan(0)
      expect(entry.aliases.length).toBeGreaterThan(0)
      expect(entry.example).not.toContain('equipmentA')
    }
    const identity = offlineGlossary.find((entry) => entry.term === 'IRI / 稳定身份')!
    expect(identity.aliases).toEqual(['主键', 'Primary Key', 'PK'])
    expect(identity.boundary).toContain('Palantir 主键 ≠ 本软件 IRI')
  })

  it.each(['主键', 'Primary Key', 'PK', ' primary   key '])(
    'reaches the identity term through the local alias search: %s',
    (query) => {
      const matches = searchGlossary(offlineGlossary, query)
      expect(matches[0].entry.term).toBe('IRI / 稳定身份')
      expect(matches[0].entry.boundary).toContain('Palantir 主键 ≠ 本软件 IRI')
      expect(searchGlossary(offlineGlossary, '')).toEqual([])
      expect(searchGlossary(offlineGlossary, '这个词不存在于术语表')).toEqual([])
    },
  )

  it('maps every check status to a text label instead of colour alone', () => {
    const expected: Record<CheckStatus, string> = {
      'not-checked': '待检查',
      passed: '已通过',
      'needs-repair': '需要修复',
      stale: '已过期',
      failed: '检查失败 / 已取消',
      'pending-dependency': '依赖未就绪',
      'rerun-required': '已过期 / 需重跑',
      'missing-evidence': '检查失败',
      'tool-not-successful': '检查失败',
    }
    expect(checkStatusLabels).toEqual(expected)
    expect(statusLabel(undefined)).toBe('待检查')
    expect(
      statusLabel(
        record({
          operationComplete: false,
          independentTransferSuccess: false,
          checkStatus: 'failed',
        }),
      ),
    ).toBe('检查失败 / 已取消')
    expect(
      statusLabel(
        record({
          operationComplete: false,
          independentTransferSuccess: false,
          checkStatus: 'rerun-required',
        }),
      ),
    ).toBe('已过期 / 需重跑')
  })
})
