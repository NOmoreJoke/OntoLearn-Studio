import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import {
  escapeReportText,
  learningOutcome,
  parsePreparedReport,
  renderPreparedReport,
} from '../../apps/desktop/src/renderer/src/transfer/report'

const fixture = (name: string) =>
  JSON.parse(readFileSync(new URL(`../fixtures/transfer/${name}`, import.meta.url), 'utf8'))
const input = () => parsePreparedReport(fixture('report-input.json'))
const attacks: string[] = fixture('malicious-texts.json')

describe('T10 safe offline prepared report', () => {
  it('includes every required section, provenance, status and per-attempt learning evidence', () => {
    const html = renderPreparedReport(input())
    for (const expected of [
      '项目目标',
      '能力问题',
      '任务完成及提示使用',
      '本体概况',
      '数据概况',
      '查询结果及版本',
      '验证结果及版本',
      '行为摘要',
      '场景对比',
      '主要假设',
      '待解决问题',
      '项目版本 7',
      '输入版本 6',
      '执行语义 synthetic-semantics-1',
      '已过期',
      '历史',
      '失败',
      'attempt-1',
      'synthetic-check-1',
      '独立迁移成功：是',
      '尚未接入正式项目与学习证据',
    ])
      expect(html).toContain(expected)
    expect(html).not.toMatch(/<(script|style|img|link|iframe|object|a)\b/i)
    expect(html).toContain('Content-Security-Policy')
    expect(html).toContain('connect-src &#39;none&#39;')
  })

  for (const [index, attack] of attacks.entries()) {
    it(`escapes malicious text #${index} at every dynamic text location`, () => {
      const report = input()
      report.title = attack
      report.goals =
        report.competencyQuestions =
        report.ontologySummary =
        report.dataSummary =
        report.assumptions =
        report.unresolved =
          [attack]
      const a = report.learning[0]
      a.taskId = a.attemptId = a.check.summary = a.check.evidenceRef = attack
      a.stageOutcomes = [attack]
      for (const results of [
        report.queryResults,
        report.validationResults,
        report.behaviorResults,
        report.scenarioComparisons,
      ]) {
        for (const r of results)
          r.resultId = r.scope = r.statusNote = r.summary = r.semanticsVersion = attack
      }
      const html = renderPreparedReport(report)
      expect(html).toContain(escapeReportText(attack))
      expect(html).not.toMatch(/<(script|style|img|link|iframe|object|svg|a)\b/i)
      expect(html).not.toContain('</title><script>')
    })
  }

  it('preserves Chinese, literal markup, quotes, ampersand and LF without double decoding', () => {
    const report = input()
    report.goals = ['<b>设备A</b>\n中文“引号” \'单\' "双" & &lt;img&gt;']
    const html = renderPreparedReport(report)
    expect(html).toContain(
      '&lt;b&gt;设备A&lt;/b&gt;\n中文“引号” &#39;单&#39; &quot;双&quot; &amp; &amp;lt;img&amp;gt;',
    )
  })

  it('rejects extra credential/config/session fields instead of dumping arbitrary objects', () => {
    for (const key of [
      'apiKey',
      'password',
      'token',
      'vault',
      'audit',
      'agentSessions',
      'sendAuthorization',
    ]) {
      expect(() => renderPreparedReport({ ...input(), [key]: 'synthetic-secret' })).toThrow(
        /^REPORT_PROJECTION_INVALID$/,
      )
      const report = input()
      Object.assign(report.learning[0].check, { [key]: 'synthetic-secret' })
      expect(() => renderPreparedReport(report)).toThrow(/^REPORT_PROJECTION_INVALID$/)
    }
  })

  it('rejects duplicate attempts, unsupported version, invalid evidence and contradictory current state', () => {
    const duplicate = input()
    duplicate.learning.push(duplicate.learning[0])
    expect(() => renderPreparedReport(duplicate)).toThrow('REPORT_PROJECTION_INVALID')
    expect(() => renderPreparedReport({ ...input(), projectionVersion: 3 })).toThrow(
      'REPORT_PROJECTION_INVALID',
    )
    const noEvidence = input()
    noEvidence.learning[0].check.evidenceRef = null
    expect(() => renderPreparedReport(noEvidence)).toThrow('REPORT_PROJECTION_INVALID')
    const old = input()
    old.queryResults[0].inputRevision = 6
    expect(() => renderPreparedReport(old)).toThrow('REPORT_PROJECTION_INVALID')
  })

  it('does not convert clicks, failure or full assistance to independent mastery', () => {
    const base = input().learning[0]
    const cases = [
      [{ ...base, operationCompleted: false }, '尚未验证完成'],
      [{ ...base, check: { ...base.check, status: 'failed' as const } }, '尚未验证完成'],
      [{ ...base, hint: 'concept' as const }, '使用部分提示或 Agent 辅助完成'],
      [{ ...base, hint: 'full' as const }, '使用完整示范完成'],
      [{ ...base, agentAssistance: 'partial' as const }, '使用部分提示或 Agent 辅助完成'],
      [{ ...base, agentAssistance: 'full' as const }, 'Agent 完整辅助完成'],
    ] as const
    for (const [attempt, label] of cases) {
      expect(learningOutcome(attempt)).toEqual({ label, independentTransfer: false })
      const report = input()
      report.learning = [attempt]
      expect(renderPreparedReport(report)).toContain('独立迁移成功：否')
    }
    const report = input()
    report.learning.push({ ...base, attemptId: 'attempt-2', agentAssistance: 'full' })
    const html = renderPreparedReport(report)
    expect(html).toContain('attempt-1｜独立完成')
    expect(html).toContain('attempt-2｜Agent 完整辅助完成')
  })

  it('bounds total text, object count, cycles and accessors without exposing diagnostics', () => {
    const report = input()
    report.goals = Array(200).fill('x'.repeat(16_384))
    expect(() => renderPreparedReport(report)).toThrow(/^REPORT_PROJECTION_INVALID$/)
    const cycle: Record<string, unknown> = {}
    cycle.self = cycle
    expect(() => renderPreparedReport(cycle)).toThrow(/^REPORT_PROJECTION_INVALID$/)
    let invoked = false
    const getter = Object.defineProperty({}, 'apiKey', {
      get() {
        invoked = true
        return 'synthetic-secret'
      },
    })
    expect(() => renderPreparedReport(getter)).toThrow(/^REPORT_PROJECTION_INVALID$/)
    expect(invoked).toBe(false)
    const arrayGetter = input()
    arrayGetter.goals = Object.defineProperty([], '0', {
      get() {
        invoked = true
        throw new Error('synthetic-sensitive-diagnostic')
      },
    })
    expect(() => renderPreparedReport(arrayGetter)).toThrow(/^REPORT_PROJECTION_INVALID$/)
    expect(invoked).toBe(false)
    const inherited = Object.create(Array.prototype)
    Object.defineProperty(inherited, '0', {
      get() {
        invoked = true
        throw new Error('synthetic-inherited-diagnostic')
      },
    })
    const inheritedArray = input()
    inheritedArray.goals = Object.setPrototypeOf(new Array(1), inherited)
    expect(() => renderPreparedReport(inheritedArray)).toThrow(/^REPORT_PROJECTION_INVALID$/)
    expect(invoked).toBe(false)
    const sparse = input()
    sparse.goals = new Array(1)
    expect(() => renderPreparedReport(sparse)).toThrow(/^REPORT_PROJECTION_INVALID$/)
  })
})
