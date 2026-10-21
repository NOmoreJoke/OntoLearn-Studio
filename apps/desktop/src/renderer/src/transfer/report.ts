// Private T10 projection, not IPC or a replacement for the canonical project contract.
// Callers must obtain an approved, credential-free business projection before formal export.
import { z } from 'zod'
import { contentSecurityPolicy } from '../../../csp'

const text = z.string().max(16_384)
const id = z.string().min(1).max(160)
const notes = z.array(text).max(200)
const revision = z.number().int().nonnegative().safe()
const result = z
  .object({
    resultId: id,
    inputRevision: revision,
    semanticsVersion: id,
    scope: text,
    status: z.enum(['current', 'stale', 'historical', 'failed', 'cancelled']),
    statusNote: text.min(1),
    summary: text,
  })
  .strict()
const attempt = z
  .object({
    taskId: id,
    attemptId: id,
    transferTask: z.boolean(),
    operationCompleted: z.boolean(),
    hint: z.enum(['none', 'concept', 'operation', 'partial', 'full']),
    agentAssistance: z.enum(['none', 'partial', 'full']),
    check: z
      .object({
        status: z.enum(['not-run', 'passed', 'failed', 'error']),
        evidenceRef: id.nullable(),
        summary: text,
      })
      .strict(),
    stageOutcomes: notes,
  })
  .strict()
  .refine((v) => v.check.status !== 'passed' || v.check.evidenceRef !== null)

export const preparedReportSchema = z
  .object({
    projectionVersion: z.literal('t10-report-draft-1'),
    projectId: id,
    title: text.min(1),
    generatedAt: z.iso.datetime(),
    projectRevision: revision,
    goals: notes,
    competencyQuestions: notes,
    learning: z.array(attempt).max(500),
    ontologySummary: notes,
    dataSummary: notes,
    queryResults: z.array(result).max(200),
    validationResults: z.array(result).max(200),
    behaviorResults: z.array(result).max(200),
    scenarioComparisons: z.array(result).max(200),
    assumptions: notes,
    unresolved: notes,
  })
  .strict()
  .superRefine((v, ctx) => {
    const attempts = new Set<string>()
    for (const a of v.learning) {
      const key = JSON.stringify([a.taskId, a.attemptId])
      if (attempts.has(key)) ctx.addIssue({ code: 'custom', message: 'duplicate attempt' })
      attempts.add(key)
    }
    for (const r of [
      ...v.queryResults,
      ...v.validationResults,
      ...v.behaviorResults,
      ...v.scenarioComparisons,
    ]) {
      if (
        r.inputRevision > v.projectRevision ||
        (r.status === 'current' && r.inputRevision !== v.projectRevision)
      ) {
        ctx.addIssue({ code: 'custom', message: 'inconsistent result revision' })
      }
    }
  })

export type PreparedReport = z.infer<typeof preparedReportSchema>
export type LearningAttempt = PreparedReport['learning'][number]

export function learningOutcome(a: LearningAttempt): {
  label: string
  independentTransfer: boolean
} {
  if (!a.operationCompleted || a.check.status !== 'passed') {
    return { label: '尚未验证完成', independentTransfer: false }
  }
  if (a.agentAssistance === 'full') {
    return { label: 'Agent 完整辅助完成', independentTransfer: false }
  }
  if (a.hint === 'full') {
    return { label: '使用完整示范完成', independentTransfer: false }
  }
  if (a.hint !== 'none' || a.agentAssistance !== 'none') {
    return { label: '使用部分提示或 Agent 辅助完成', independentTransfer: false }
  }
  return { label: '独立完成', independentTransfer: a.transferTask }
}

export class ReportError extends Error {
  constructor() {
    super('REPORT_PROJECTION_INVALID')
  }
}

// Defensive output budget, not a measured product-capacity claim. Fixed-depth schemas
// still permit large products of list sizes; reject before Zod cloning or HTML joining.
function checkBudget(value: unknown): void {
  const pending = [value]
  let nodes = 0
  let characters = 0
  while (pending.length) {
    if (++nodes > 20_000) throw new ReportError()
    const next = pending.pop()
    if (typeof next === 'string') characters += next.length
    else if (next !== null && typeof next === 'object') {
      const array = Array.isArray(next)
      const prototype = Object.getPrototypeOf(next)
      if (
        array ? prototype !== Array.prototype : prototype !== Object.prototype && prototype !== null
      ) {
        throw new ReportError()
      }
      if (array && next.length > 500) throw new ReportError()
      const descriptors = Object.getOwnPropertyDescriptors(next)
      if (Object.keys(descriptors).length > (array ? 501 : 40)) throw new ReportError()
      if (array) {
        for (let i = 0; i < next.length; i++) {
          if (!Object.hasOwn(descriptors, String(i))) throw new ReportError()
        }
      }
      for (const [key, descriptor] of Object.entries(descriptors)) {
        if (!('value' in descriptor)) throw new ReportError()
        characters += key.length
        pending.push(descriptor.value)
      }
    }
    if (characters > 1_048_576) throw new ReportError()
  }
}

export function parsePreparedReport(value: unknown): PreparedReport {
  try {
    checkBudget(value)
    const parsed = preparedReportSchema.safeParse(value)
    if (!parsed.success) throw new ReportError()
    return parsed.data
  } catch {
    throw new ReportError() // Never expose source values, accessors or Zod diagnostics.
  }
}

// Every dynamic string occurs only in HTML text, never markup/URL/style/script contexts.
export function escapeReportText(value: string): string {
  return value.replace(/[&<>"']/g, (c) => {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!
  })
}

const pre = (value: string) => `<pre>${escapeReportText(value)}</pre>`
const section = (title: string, values: string[]) =>
  `<section><h2>${title}</h2>${values.length ? values.map(pre).join('') : '<p>未记录</p>'}</section>`
const statusLabels = {
  current: '当前',
  stale: '已过期',
  historical: '历史',
  failed: '失败',
  cancelled: '已取消',
}
const hintLabels = {
  none: '无提示',
  concept: '概念提示',
  operation: '操作提示',
  partial: '部分示范',
  full: '完整示范',
}
const assistanceLabels = { none: '无', partial: '部分', full: '完整代做' }
const checkLabels = { 'not-run': '未检查', passed: '通过', failed: '未通过', error: '检查错误' }

export function renderPreparedReport(value: unknown): string {
  const report = parsePreparedReport(value)
  const resultSection = (title: string, results: PreparedReport['queryResults']) =>
    section(
      title,
      results.map(
        (r) =>
          `结果 ${r.resultId}｜${statusLabels[r.status]}\n输入版本 ${r.inputRevision}｜执行语义 ${r.semanticsVersion}\n范围：${r.scope}\n状态说明：${r.statusNote}\n${r.summary}`,
      ),
    )
  const learning = report.learning.map((a) => {
    const outcome = learningOutcome(a)
    return [
      `任务 ${a.taskId}｜尝试 ${a.attemptId}｜${outcome.label}`,
      `操作完成：${a.operationCompleted ? '是' : '否'}｜提示：${hintLabels[a.hint]}｜Agent 辅助：${assistanceLabels[a.agentAssistance]}`,
      `检查：${checkLabels[a.check.status]}｜证据：${a.check.evidenceRef ?? '未记录'}`,
      `独立迁移成功：${outcome.independentTransfer ? '是' : '否'}`,
      a.check.summary,
      ...a.stageOutcomes,
    ].join('\n')
  })
  // Uses the existing CSP authority. No scripts, styles, links, fonts or remote resources.
  return [
    '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
    `<meta http-equiv="Content-Security-Policy" content="${escapeReportText(contentSecurityPolicy())}">`,
    `<title>${escapeReportText(report.title)}</title></head><body>`,
    '<p>内部投影预验报告：尚未接入正式项目与学习证据，不作为产品验收结论。</p>',
    `<h1>${escapeReportText(report.title)}</h1>`,
    pre(
      `项目 ${report.projectId}｜项目版本 ${report.projectRevision}｜生成时间 ${report.generatedAt}`,
    ),
    section('项目目标', report.goals),
    section('能力问题', report.competencyQuestions),
    section('任务完成及提示使用', learning),
    section('本体概况', report.ontologySummary),
    section('数据概况', report.dataSummary),
    resultSection('查询结果及版本', report.queryResults),
    resultSection('验证结果及版本', report.validationResults),
    resultSection('行为摘要', report.behaviorResults),
    resultSection('场景对比', report.scenarioComparisons),
    section('主要假设', report.assumptions),
    section('待解决问题', report.unresolved),
    '</body></html>',
  ].join('\n')
}
