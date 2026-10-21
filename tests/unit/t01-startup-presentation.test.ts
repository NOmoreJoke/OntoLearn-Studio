import { describe, expect, it } from 'vitest'
import { randomUUID } from 'node:crypto'
import {
  safeDisplayError,
  safeError,
  isTaskUpdate,
  healthSchema,
  displayHealthSchema,
} from '@ontolearn/contracts'
import { explainError } from '../../apps/desktop/src/renderer/src/task-presentation'

const format = {
  code: 'PROJECT_FORMAT_UNSUPPORTED',
  messageKey: 'project.formatUnsupported',
  params: { supportedFormats: [3] },
  retryable: false,
}
describe('finite startup presentation after authenticated main projection', () => {
  it.each(['health', 'task', 'result'] as const)(
    'preserves the complete allowed value and fixed %s copy',
    (context) => {
      expect(safeError(format).code).toBe('INTERNAL_ERROR')
      expect(safeDisplayError(format)).toEqual(format)
      expect(explainError(format, context)).toEqual({
        what: '项目格式暂不受支持。',
        why: '当前内部引擎不能打开此项目格式。',
        fix: '保留项目文件并使用兼容版本后重新检查。',
        detail: '错误代码：PROJECT_FORMAT_UNSUPPORTED。重试提示不代表允许自动重放写入。',
      })
    },
  )
  it.each([
    { ...format, path: '/private/project.sqlite' },
    { ...format, params: { supportedFormats: [4] } },
    { ...format, messageKey: 'private exception' },
    { ...format, params: { supportedFormats: [3], actual: 99 } },
    { ...format, retryable: true },
  ])('rejects extra/mutated finite values without rendering private fields', (value) => {
    expect(safeDisplayError(value).code).toBe('INTERNAL_ERROR')
    expect(JSON.stringify(explainError(value, 'health'))).not.toMatch(/private|99|4\]/)
  })
  it('uses neutral unavailable text for an engine that may never have been connected', () => {
    const text = explainError(
      { code: 'ENGINE_EXITED', messageKey: 'engine.exited', params: {}, retryable: true },
      'health',
    )
    expect(text.what).toBe('本地引擎当前不可用。')
    expect(text.what).not.toContain('已中断')
  })
  it('retains default2 health validation and only accepts complete finite display DTOs', () => {
    const value = {
      protocolVersion: 3,
      engineVersion: '0.1.0',
      status: 'ok',
      capabilities: ['health'],
    }
    expect(healthSchema.safeParse(value).success).toBe(false)
    expect(displayHealthSchema.safeParse(value).success).toBe(true)
    expect(displayHealthSchema.safeParse({ ...value, capabilities: ['arbitrary'] }).success).toBe(
      false,
    )
  })
  it('does not relax connection update binding, state or attempts', () => {
    const value = {
      kind: 'connection',
      generation: 1,
      projectId: randomUUID(),
      state: 'offline',
      attempt: 3,
      error: format,
    }
    expect(isTaskUpdate(value)).toBe(true)
    for (const change of [
      { attempt: 1 },
      { projectId: 'bad' },
      { state: 'ready' },
      { generation: -1 },
      { error: { ...format, extra: 'secret' } },
    ])
      expect(isTaskUpdate({ ...value, ...change })).toBe(false)
  })
})
