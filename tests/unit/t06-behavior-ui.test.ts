import { describe, expect, it, vi } from 'vitest'
import { BehaviorController } from '../../apps/desktop/src/renderer/src/behavior/controller'
import {
  draftSchema,
  parseEvents,
  resultSchema,
  validateDraft,
  type BehaviorDraft,
  type BehaviorResult,
  type Binding,
  type Catalog,
  type Context,
  type SampleEvent,
  type SampleRequest,
} from '../../apps/desktop/src/renderer/src/behavior/model'
import {
  resultHeading,
  resultSections,
} from '../../apps/desktop/src/renderer/src/behavior/presentation'

const context: Context = {
  projectId: 'P',
  inputVersion: 'V1',
  behaviorVersion: 'B1',
  scopeId: 'isolated-1',
}
const catalog: Catalog = {
  objects: ['T1', 'W-test'],
  classes: ['TestObject', 'Notification'],
  properties: [
    { id: 'P', kind: 'single' },
    { id: 'links', kind: 'multi' },
  ],
  behaviorIds: ['saved'],
}
const draft: BehaviorDraft = {
  id: 'B',
  name: '行为',
  description: '说明',
  trigger: 'alarm',
  conditions: [
    { kind: 'equals', object: 'T1', property: 'P', value: { kind: 'boolean', value: false } },
  ],
  actions: [
    { kind: 'update', object: 'T1', property: 'P', value: { kind: 'boolean', value: true } },
    { kind: 'notify', message: '通知' },
  ],
  effect: '隔离副本产生通知',
  enabled: true,
  priority: 0,
  version: 1,
}
const events: SampleEvent[] = [
  {
    id: 'E-1',
    type: 'alarm',
    payload: '{"equipment":"T1"}',
    changes: [
      { operation: 'set', object: 'T1', property: 'P', value: { kind: 'boolean', value: false } },
    ],
  },
]
function result(binding: Binding, patch: Partial<BehaviorResult> = {}): BehaviorResult {
  const state = patch.state ?? 'candidate'
  const actionState =
    state === 'completed'
      ? 'applied'
      : ['failed', 'cancelled'].includes(state)
        ? 'rolled_back'
        : 'planned'
  const notificationState =
    state === 'completed'
      ? 'recorded'
      : ['failed', 'cancelled'].includes(state)
        ? 'discarded'
        : 'candidate'
  return {
    binding,
    runId: 'R1',
    state: 'candidate',
    committed: false,
    freshness: 'current',
    freshnessDetail: '',
    assertionVersion: 'A1',
    inferenceVersion: 'I1',
    semanticsVersion: 'E1',
    conditions: [
      { eventId: 'E-1', behaviorId: 'B', triggered: true, reason: 'T1.P=false，冻结快照条件满足' },
      { eventId: 'E-2', behaviorId: 'B', triggered: false, reason: '类型不匹配' },
    ],
    actions: [
      {
        eventId: 'E-1',
        behaviorId: 'B',
        index: 0,
        kind: 'update',
        state: actionState,
        detail: 'T1.P=true',
      },
      {
        eventId: 'E-1',
        behaviorId: 'B',
        index: 1,
        kind: 'notify',
        state: actionState,
        detail: '事件关联通知',
      },
    ],
    diff: {
      added: [{ object: 'T1', property: 'P', value: { kind: 'boolean', value: true } }],
      removed: [{ object: 'T1', property: 'P', value: { kind: 'boolean', value: false } }],
    },
    notifications: [{ eventId: 'E-1', behaviorId: 'B', message: '通知', state: notificationState }],
    error: null,
    ...patch,
  }
}
function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (error: unknown) => void
  const promise = new Promise<T>((a, b) => {
    resolve = a
    reject = b
  })
  return { promise, resolve, reject }
}
function setup(runSample?: (request: SampleRequest) => Promise<unknown>) {
  const controller = new BehaviorController(context, catalog, draft, { runSample })
  controller.editEvents(events)
  return controller
}

describe('T06 private editor structure', () => {
  it('checks the full behavior record, one group, unique IDs and safe action kinds', () => {
    expect(validateDraft(draft, catalog)).toEqual([])
    expect(validateDraft({ ...draft, id: 'saved' }, catalog)).toEqual([
      { path: 'id', message: '行为 ID 在项目中已存在' },
    ])
    expect(
      validateDraft({ ...draft, id: 'saved' }, { ...catalog, editingBehaviorId: 'saved' }),
    ).toEqual([])
    for (const field of ['id', 'name', 'description', 'trigger', 'effect'] as const)
      expect(validateDraft({ ...draft, [field]: '' }, catalog)).toContainEqual({
        path: field,
        message: '请填写完整且有效的值',
      })
    expect(draftSchema.safeParse({ ...draft, conditions: [] }).success).toBe(false)
    expect(
      draftSchema.safeParse({ ...draft, actions: [{ kind: 'email', address: 'x' }] }).success,
    ).toBe(false)
    expect(draftSchema.safeParse({ ...draft, preconditions: [] }).success).toBe(false)
    expect(draftSchema.safeParse({ ...draft, version: 0, priority: NaN }).success).toBe(false)
  })
  it('authors explicit always for X/B-a/B-b without inventing object conditions, and keeps missing conditions invalid', async () => {
    const run = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(run)
    for (const id of ['X', 'B-a', 'B-b']) {
      const always: BehaviorDraft = { ...draft, id, conditions: [{ kind: 'always' }] }
      expect(validateDraft(always, catalog)).toEqual([])
      controller.editDraft(always)
      await controller.run()
      expect(run.mock.calls.at(-1)?.[0].draft.conditions).toEqual([{ kind: 'always' }])
    }
    expect(draftSchema.safeParse({ ...draft, conditions: [] }).success).toBe(false)
    const missing: Record<string, unknown> = { ...draft }
    delete missing.conditions
    expect(draftSchema.safeParse(missing).success).toBe(false)
    expect(
      draftSchema.safeParse({ ...draft, conditions: [{ kind: 'always', object: 'dummy' }] })
        .success,
    ).toBe(false)
  })
  it('validates references and action sequence without pretending to run conflict detection', () => {
    expect(
      validateDraft(
        {
          ...draft,
          conditions: [
            { kind: 'type', object: 'T1', classId: 'TestObject' },
            { kind: 'exists', object: 'T1', property: 'P' },
          ],
          actions: [
            { kind: 'create', object: 'N1', classId: 'Notification' },
            { kind: 'relate', object: 'N1', property: 'links', target: 'T1' },
          ],
        },
        catalog,
      ),
    ).toEqual([])
    expect(
      validateDraft(
        {
          ...draft,
          actions: [
            { kind: 'update', object: 'N1', property: 'P', value: { kind: 'number', value: 1 } },
            { kind: 'create', object: 'N1', classId: 'Notification' },
          ],
        },
        catalog,
      ),
    ).toEqual([{ path: 'actions.0', message: '动作引用了未知或尚未创建的对象' }])
    expect(
      validateDraft(
        {
          ...draft,
          actions: [
            { kind: 'create', object: 'T1', classId: 'Unknown' },
            {
              kind: 'update',
              object: 'T1',
              property: 'links',
              value: { kind: 'iri', value: 'missing' },
            },
          ],
        },
        catalog,
      ),
    ).toEqual([
      { path: 'actions.0', message: '创建动作的对象 ID 已存在或重复' },
      { path: 'actions.0', message: '创建动作引用了未知类' },
      { path: 'actions.1', message: '多值关系请使用添加关系动作' },
      { path: 'actions.1', message: '属性值引用了未知对象' },
    ])
  })
  it('rejects relation append into a single-valued property while allowing explicit single IRI overwrite', () => {
    expect(
      validateDraft(
        { ...draft, actions: [{ kind: 'relate', object: 'T1', property: 'P', target: 'W-test' }] },
        catalog,
      ),
    ).toEqual([{ path: 'actions.0', message: '单值关系请使用更新属性动作' }])
    expect(
      validateDraft(
        {
          ...draft,
          actions: [
            {
              kind: 'update',
              object: 'T1',
              property: 'P',
              value: { kind: 'iri', value: 'W-test' },
            },
          ],
        },
        catalog,
      ),
    ).toEqual([])
  })
  it('retains ordered explicit event mutations and rejects duplicates/malformed or executable payloads', () => {
    expect(parseEvents(events)).toEqual({
      events: [{ ...events[0], payload: { equipment: 'T1' } }],
      issues: [],
    })
    expect(parseEvents([...events, { ...events[0], id: ' E-1 ' }]).issues).toEqual([
      { path: 'events.1', message: '本批次事件 ID 重复；重放幂等请重复运行原事件' },
    ])
    for (const payload of ['{bad', '[]', '{"x":{}}', '{"x":1e400}', '{"x":[1]}'])
      expect(parseEvents([{ ...events[0], payload }]).issues[0].path).toBe('events.0')
    expect(
      parseEvents([{ ...events[0], changes: [{ ...events[0].changes[0], object: '' }] }]).issues[0]
        .path,
    ).toBe('events.0')
    expect(parseEvents([]).issues[0].path).toBe('events')
  })
})

describe('T06 single sample result consistency', () => {
  const binding: Binding = { ...context, requestId: 'matrix' }
  const allowedActions = {
    candidate: ['planned', 'deduplicated', 'skipped'],
    completed: ['applied', 'deduplicated', 'skipped'],
    failed: ['rolled_back', 'skipped'],
    cancelled: ['rolled_back', 'skipped'],
  }
  const allowedNotifications = {
    candidate: 'candidate',
    completed: 'recorded',
    failed: 'discarded',
    cancelled: 'discarded',
  }
  it.each(['candidate', 'completed', 'failed', 'cancelled'] as const)(
    '%s accepts exactly its action/notification combinations',
    (state) => {
      for (const actionState of [
        'planned',
        'applied',
        'deduplicated',
        'rolled_back',
        'skipped',
      ] as const) {
        for (const notificationState of ['candidate', 'recorded', 'discarded'] as const) {
          const value = result(binding, {
            state,
            committed: state === 'completed',
            error: state === 'failed' ? 'execution_failed' : null,
          })
          value.actions = value.actions.map((action) => ({ ...action, state: actionState }))
          value.notifications = value.notifications.map((notification) => ({
            ...notification,
            state: notificationState,
          }))
          expect(
            resultSchema.safeParse(value).success,
            `${state}/${actionState}/${notificationState}`,
          ).toBe(
            allowedActions[state].includes(actionState) &&
              notificationState === allowedNotifications[state],
          )
        }
      }
      const noActions = result(binding, {
        state,
        committed: state === 'completed',
        error: state === 'failed' ? 'execution_failed' : null,
        actions: [],
        notifications: [],
      })
      expect(resultSchema.safeParse(noActions).success).toBe(true)
    },
  )
  it.each(['candidate', 'completed', 'failed', 'cancelled'] as const)(
    'controller rejects contradictory %s evidence without presenting success',
    async (state) => {
      const controller = setup(async (request) => {
        const value = result(request.binding, {
          state,
          committed: state === 'completed',
          error: state === 'failed' ? 'conflict' : null,
        })
        value.actions[0].state = state === 'completed' ? 'planned' : 'applied'
        return value
      })
      await controller.run()
      expect(controller.getSnapshot().result).toBeUndefined()
      expect(controller.getSnapshot().notice).toContain('已拒绝显示')
    },
  )
  it('invalid refreshed applied/recorded candidate retains the last verified result and editor', async () => {
    const run = async (request: SampleRequest) => result(request.binding)
    const refresh = async (request: Binding) => {
      const value = result(request)
      value.actions[0].state = 'applied'
      value.notifications[0].state = 'recorded'
      return value
    }
    const controller = setup(run)
    controller.configure(context, catalog, { runSample: run, refreshResult: refresh })
    await controller.run()
    const last = controller.getSnapshot().result
    controller.editDraft({ ...draft, name: '仍保留草稿' })
    await controller.refresh()
    expect(controller.getSnapshot().result).toBe(last)
    expect(controller.getSnapshot().draft.name).toBe('仍保留草稿')
    expect(controller.getSnapshot().notice).toContain('已拒绝显示')
  })
})

describe('T06 event content fidelity', () => {
  it('rejects both different same-ID __proto__ payloads instead of silently folding either into an empty object', () => {
    const inputs = ['{"__proto__":"first"}', '{"__proto__":"second"}']
    for (const payload of inputs) {
      const parsed = parseEvents([{ ...events[0], payload }])
      expect(parsed.events).toEqual([])
      expect(parsed.issues).toEqual([
        {
          path: 'events.0',
          message:
            '事件内容包含保留键（__proto__、constructor 或 prototype）；该事件整体未执行，普通字段也不会提交。原文已保留，请修正保留键后重试',
        },
      ])
    }
  })
  it('checks reserved own keys before schema normalization, including escaped keys, and preserves ordinary fields', () => {
    for (const key of ['__proto__', 'constructor', 'prototype']) {
      const payload = JSON.stringify(Object.fromEntries([[key, 'retained or rejected']]))
      expect(parseEvents([{ ...events[0], payload }]).issues[0]?.message).toContain('保留键')
    }
    expect(
      parseEvents([{ ...events[0], payload: String.raw`{"\u005f_proto__":"escaped"}` }]).issues[0]
        ?.message,
    ).toContain('保留键')
    const value = { __proto_value: 'first', Constructor: 'second', normal: null }
    expect(parseEvents([{ ...events[0], payload: JSON.stringify(value) }])).toEqual({
      events: [{ ...events[0], payload: value }],
      issues: [],
    })
  })
  it('never calls the execution callback with rejected reserved-key content', async () => {
    const run = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(run)
    for (const payload of ['{"__proto__":"first"}', '{"__proto__":"second"}']) {
      controller.editEvents([{ ...events[0], payload }])
      await controller.run()
      expect(run).not.toHaveBeenCalled()
      expect(controller.getSnapshot().issues[0]?.message).toContain('保留键')
    }
  })
})

describe('T06 request/refresh isolation', () => {
  it('never calls unavailable execution and reports local structure separately', async () => {
    const controller = setup()
    expect(controller.validate()).toEqual([])
    expect(controller.getSnapshot().notice).toContain(
      '真实推理、幂等与竞争检查仍由隔离执行服务完成',
    )
    await controller.run()
    expect(controller.getSnapshot().result).toBeUndefined()
    expect(controller.getSnapshot().notice).toBe('隔离执行服务未接入，不能运行样本。')
  })
  it('blocks malformed inputs and missing isolation context before calling callbacks', async () => {
    const run = vi.fn()
    const controller = setup(run)
    controller.editDraft({ ...draft, conditions: [] })
    await controller.run()
    expect(run).not.toHaveBeenCalled()
    controller.editDraft(draft)
    controller.configure({ ...context, scopeId: '' }, catalog, { runSample: run })
    await controller.run()
    expect(run).not.toHaveBeenCalled()
    expect(controller.getSnapshot().notice).toContain('隔离范围')
  })
  it('clones requests, keeps event identity for replay and does not double submit while pending', async () => {
    const gate = deferred<unknown>()
    const received: SampleRequest[] = []
    const controller = setup(async (request) => {
      received.push(request)
      return gate.promise
    })
    const first = controller.run()
    await controller.run()
    expect(received).toHaveLength(1)
    expect(received[0].events).toEqual([{ ...events[0], payload: { equipment: 'T1' } }])
    controller.editDraft({ ...draft, name: '编辑保留' })
    gate.resolve(result(received[0].binding))
    await first
    expect(controller.getSnapshot().draft.name).toBe('编辑保留')
    expect(controller.getSnapshot().resultRevision).not.toBe(controller.getSnapshot().revision)
    const second = controller.run()
    expect(received[1].events[0].id).toBe('E-1')
    expect(received[1].binding.requestId).not.toBe(received[0].binding.requestId)
    await second
    // The resolved gate still belongs to the first request: it cannot become the replay result.
    expect(controller.getSnapshot().result).toBeUndefined()
    expect(controller.getSnapshot().notice).toContain('已拒绝显示')
  })
  it.each(['projectId', 'inputVersion', 'behaviorVersion', 'scopeId'] as const)(
    'rejects late results when %s switches',
    async (field) => {
      const gate = deferred<unknown>()
      let binding!: Binding
      const run = (request: SampleRequest) => {
        binding = request.binding
        return gate.promise
      }
      const controller = setup(run)
      const pending = controller.run()
      controller.configure(
        { ...context, [field]: 'NEW' },
        catalog,
        { runSample: run },
        { ...draft, name: '新项目草稿' },
      )
      gate.resolve(result(binding))
      await pending
      expect(controller.getSnapshot().result).toBeUndefined()
      expect(controller.getSnapshot().pending).toBeUndefined()
      expect(controller.getSnapshot().draft.name).toBe(
        field === 'projectId' ? '新项目草稿' : draft.name,
      )
    },
  )
  it('rejects wrong request identity and raw evidence rather than displaying its values', async () => {
    const controller = setup(async (request) => ({
      ...result({ ...request.binding, requestId: 'wrong' }),
      evidence: { path: '/secret', value: 'sensitive' },
    }))
    await controller.run()
    expect(controller.getSnapshot().result).toBeUndefined()
    expect(controller.getSnapshot().notice).toBe('返回结果格式或项目/版本/请求不匹配，已拒绝显示。')
    expect(JSON.stringify(controller.getSnapshot())).not.toContain('sensitive')
  })
  it('callback mutation cannot alter controller binding or edited draft', async () => {
    const controller = setup(async (request) => {
      request.binding.scopeId = 'foreign'
      request.draft.name = 'mutated'
      return result(request.binding)
    })
    await controller.run()
    expect(controller.getSnapshot().draft.name).toBe(draft.name)
    expect(controller.getSnapshot().context.scopeId).toBe(context.scopeId)
    expect(controller.getSnapshot().result).toBeUndefined()
  })
  it('refreshes only the same run and preserves all local edits without rerunning events', async () => {
    const run = vi.fn(async (request: SampleRequest) => result(request.binding))
    const gate = deferred<unknown>()
    const refresh = vi.fn(() => gate.promise)
    const controller = setup(run)
    controller.configure(context, catalog, { runSample: run, refreshResult: refresh })
    await controller.run()
    const binding = controller.getSnapshot().result!.binding
    controller.editDraft({ ...draft, name: '未保存草稿' })
    controller.editEvents([{ ...events[0], id: 'E-next' }])
    const pending = controller.refresh()
    gate.resolve(result(binding, { freshness: 'stale', freshnessDetail: '行为版本已更新' }))
    await pending
    expect(run).toHaveBeenCalledTimes(1)
    expect(refresh).toHaveBeenCalledWith(binding, 'R1')
    expect(controller.getSnapshot().draft.name).toBe('未保存草稿')
    expect(controller.getSnapshot().events[0].id).toBe('E-next')
    expect(controller.getSnapshot().result?.freshness).toBe('stale')
    expect(controller.getSnapshot().resultRevision).not.toBe(controller.getSnapshot().revision)
  })
  it('rejects a refresh response from another run and preserves last verified result on failure', async () => {
    const run = async (request: SampleRequest) => result(request.binding)
    const refresh = vi.fn(async (binding: Binding) => result(binding, { runId: 'R-other' }))
    const controller = setup(run)
    controller.configure(context, catalog, { runSample: run, refreshResult: refresh })
    await controller.run()
    const old = controller.getSnapshot().result
    await controller.refresh()
    expect(controller.getSnapshot().result).toBe(old)
    expect(controller.getSnapshot().notice).toContain('已拒绝显示')
    refresh.mockRejectedValueOnce(new Error('private secret'))
    await controller.refresh()
    expect(controller.getSnapshot().result).toBe(old)
    expect(controller.getSnapshot().notice).toBe('状态刷新失败，保留最后一次已核验结果。')
  })
  it('does not convert service failure or invalid result status into success', async () => {
    const run = vi.fn(async () => {
      throw new Error('raw error /private/path')
    })
    const controller = setup(run)
    await controller.run()
    expect(controller.getSnapshot().pending).toBeUndefined()
    expect(controller.getSnapshot().notice).toBe('隔离测试调用失败，未取得成功证据。请对账后重试。')
    expect(
      resultSchema.safeParse(
        result({ ...context, requestId: 'R' }, { state: 'candidate', committed: true }),
      ).success,
    ).toBe(false)
    expect(
      resultSchema.safeParse(
        result({ ...context, requestId: 'R' }, { state: 'failed', error: null }),
      ).success,
    ).toBe(false)
  })
  it('retains real calls when callbacks disappear and releases invalidated calls without displaying them', async () => {
    const gate = deferred<unknown>()
    let binding!: Binding
    const controller = setup((request) => {
      binding = request.binding
      return gate.promise
    })
    const pending = controller.run()
    controller.configure(context, catalog, {})
    expect(controller.getSnapshot().pending?.kind).toBe('run')
    gate.resolve(result(binding))
    await pending
    expect(controller.getSnapshot().result?.binding).toEqual(binding)
    expect(controller.getSnapshot().pending).toBeUndefined()
    const nextGate = deferred<unknown>()
    controller.configure(context, catalog, {
      runSample: (request) => {
        binding = request.binding
        return nextGate.promise
      },
    })
    const next = controller.run()
    controller.invalidate()
    nextGate.resolve(result(binding))
    await next
    expect(controller.getSnapshot().result).toBeUndefined()
    expect(controller.getSnapshot().pending).toBeUndefined()
  })
})

describe('T06 cancellation reconciliation', () => {
  it('requires real cancellation confirmation and rejects the later run completion', async () => {
    const gate = deferred<unknown>()
    const cancelGate = deferred<unknown>()
    let binding!: Binding
    const run = (request: SampleRequest) => {
      binding = request.binding
      return gate.promise
    }
    const cancel = vi.fn(() => cancelGate.promise)
    const controller = setup(run)
    controller.configure(context, catalog, { runSample: run, cancelSample: cancel })
    const pending = controller.run()
    controller.editDraft({ ...draft, name: '取消时继续编辑' })
    const cancellation = controller.cancel()
    expect(controller.getSnapshot().result).toBeUndefined()
    expect(controller.getSnapshot().cancelling).toBe(true)
    expect(controller.getSnapshot().notice).toContain('尚未视为已取消')
    cancelGate.resolve(result(binding, { state: 'cancelled' }))
    await cancellation
    expect(controller.getSnapshot().result?.state).toBe('cancelled')
    expect(controller.getSnapshot().resultRevision).not.toBe(controller.getSnapshot().revision)
    gate.resolve(result(binding, { state: 'completed', committed: true }))
    await pending
    expect(controller.getSnapshot().result?.state).toBe('cancelled')
    expect(controller.getSnapshot().pending).toBeUndefined()
  })
  it('keeps running when cancellation fails and handles completion winning the race', async () => {
    const gate = deferred<unknown>()
    const cancelGate = deferred<unknown>()
    let binding!: Binding
    const run = (request: SampleRequest) => {
      binding = request.binding
      return gate.promise
    }
    const controller = setup(run)
    controller.configure(context, catalog, {
      runSample: run,
      cancelSample: () => cancelGate.promise,
    })
    const pending = controller.run()
    const cancelling = controller.cancel()
    gate.resolve(result(binding, { state: 'completed', committed: true }))
    await pending
    cancelGate.reject(new Error('private cancellation exception'))
    await cancelling
    expect(controller.getSnapshot().result?.state).toBe('completed')
    expect(controller.getSnapshot().notice).toBe('')
  })
  it('ignores absent cancel service and does not treat an acknowledgement as a cancelled terminal result', async () => {
    const gate = deferred<unknown>()
    let binding!: Binding
    const run = (request: SampleRequest) => {
      binding = request.binding
      return gate.promise
    }
    const controller = setup(run)
    const pending = controller.run()
    await controller.cancel()
    expect(controller.getSnapshot().cancelling).toBe(false)
    controller.configure(context, catalog, {
      runSample: run,
      cancelSample: async () => ({ accepted: true }),
    })
    const restarted = controller.run()
    await controller.cancel()
    expect(controller.getSnapshot().notice).toContain('取消尚未得到有效收尾确认')
    expect(controller.getSnapshot().pending?.kind).toBe('run')
    gate.resolve(result(binding))
    await Promise.all([pending, restarted])
  })
})

describe('T06 complete evidence presentation', () => {
  it('shows exact trigger reasons, action sequence, before/after Diff and all notifications', () => {
    const value = result({ ...context, requestId: 'req' })
    expect(resultSections(value)).toEqual({
      conditions: [
        'E-1 / B · 触发 · T1.P=false，冻结快照条件满足',
        'E-2 / B · 未触发 · 类型不匹配',
      ],
      actions: [
        'E-1 / B · 动作 1 · 更新属性 · 计划 · T1.P=true',
        'E-1 / B · 动作 2 · 通知记录 · 计划 · 事件关联通知',
      ],
      added: ['T1 · P · true'],
      removed: ['T1 · P · false'],
      notifications: ['E-1 / B · 候选 · 通知'],
    })
    expect(resultHeading(value)).toBe('候选计划 · 尚未提交 / 当前输入')
    expect(
      resultHeading({ ...value, state: 'failed', error: 'conflict', freshness: 'historical' }),
    ).toBe('运行失败 · 本轮未提交 / 历史结果')
    expect(
      resultHeading({
        ...value,
        state: 'cancelled',
        freshness: 'stale',
        freshnessDetail: '上游改变',
      }),
    ).toBe('运行已取消 · 本轮未提交 / 已过期')
    expect(resultHeading({ ...value, state: 'completed', committed: true })).toBe(
      '隔离副本已提交 / 当前输入',
    )
  })
})

describe('T06 live operation ownership under host callback churn', () => {
  it('retains an in-flight run across repeated inline callback replacements and only then admits its successor', async () => {
    const gate = deferred<unknown>()
    const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => gate.promise)
    const runB = vi.fn(async (request: SampleRequest) => result(request.binding))
    const refreshB = vi.fn()
    const controller = setup(runA)
    const first = controller.run()
    const pending = controller.getSnapshot().pending
    for (let index = 0; index < 4; index++) {
      controller.configure(context, catalog, {
        runSample: (request) => runB(request),
        refreshResult: () => refreshB(),
      })
      await controller.run()
      await controller.refresh()
      expect(controller.getSnapshot().pending).toBe(pending)
    }
    expect(runA).toHaveBeenCalledTimes(1)
    expect(runB).not.toHaveBeenCalled()
    expect(refreshB).not.toHaveBeenCalled()
    gate.resolve(result(runA.mock.calls[0][0].binding))
    await first
    expect(controller.getSnapshot().pending).toBeUndefined()
    expect(controller.getSnapshot().result?.binding).toEqual(runA.mock.calls[0][0].binding)
    await controller.run()
    expect(runB).toHaveBeenCalledTimes(1)
    expect(controller.getSnapshot().result?.binding).toEqual(runB.mock.calls[0][0].binding)
  })
  it('keeps the pending call when capability availability disappears, and releases it on real rejection', async () => {
    const gate = deferred<unknown>()
    const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => gate.promise)
    const runB = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(runA)
    const first = controller.run()
    controller.configure(context, catalog, {})
    await controller.run()
    expect(runA).toHaveBeenCalledTimes(1)
    expect(controller.getSnapshot().pending?.kind).toBe('run')
    gate.reject(new Error('private old call failure'))
    await first
    expect(controller.getSnapshot().pending).toBeUndefined()
    expect(controller.getSnapshot().notice).toBe('隔离测试调用失败，未取得成功证据。请对账后重试。')
    controller.configure(context, catalog, { runSample: (request) => runB(request) })
    await controller.run()
    expect(runB).toHaveBeenCalledTimes(1)
    expect(controller.getSnapshot().result?.binding).toEqual(runB.mock.calls[0][0].binding)
  })
  it('display invalidation blocks reentry until settlement and does not strand a hidden operation', async () => {
    const gate = deferred<unknown>()
    const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => gate.promise)
    const runB = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(runA)
    const first = controller.run()
    controller.invalidate()
    controller.configure(context, catalog, { runSample: (request) => runB(request) })
    await controller.run()
    expect(runB).not.toHaveBeenCalled()
    expect(controller.getSnapshot().pending?.kind).toBe('run')
    gate.resolve(result(runA.mock.calls[0][0].binding))
    await first
    expect(controller.getSnapshot().result).toBeUndefined()
    expect(controller.getSnapshot().pending).toBeUndefined()
    expect(controller.getSnapshot().notice).toContain('旧输入结果未作为当前结果展示')
    await controller.run()
    expect(runB).toHaveBeenCalledTimes(1)
  })
  it.each(['projectId', 'inputVersion', 'behaviorVersion', 'scopeId'] as const)(
    'old %s finally cannot clear a successor pending in a new context',
    async (field) => {
      const firstGate = deferred<unknown>()
      const secondGate = deferred<unknown>()
      const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => firstGate.promise)
      const runB = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => secondGate.promise)
      const controller = setup(runA)
      const first = controller.run()
      controller.configure({ ...context, [field]: 'NEW' }, catalog, { runSample: runB }, draft)
      if (field === 'projectId') controller.editEvents(events)
      const second = controller.run()
      const successor = controller.getSnapshot().pending
      expect(successor?.binding).toEqual(runB.mock.calls[0][0].binding)
      firstGate.resolve(result(runA.mock.calls[0][0].binding))
      await first
      expect(controller.getSnapshot().pending).toBe(successor)
      expect(controller.getSnapshot().result).toBeUndefined()
      secondGate.resolve(result(runB.mock.calls[0][0].binding))
      await second
      expect(controller.getSnapshot().result?.binding).toEqual(runB.mock.calls[0][0].binding)
      expect(controller.getSnapshot().pending).toBeUndefined()
    },
  )
  it('does not overwrite a finished successor when the old context returns last', async () => {
    const gate = deferred<unknown>()
    const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => gate.promise)
    const runB = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(runA)
    const first = controller.run()
    controller.configure({ ...context, inputVersion: 'V2' }, catalog, { runSample: runB })
    await controller.run()
    const latest = controller.getSnapshot().result
    gate.resolve(result(runA.mock.calls[0][0].binding))
    await first
    expect(controller.getSnapshot().result).toBe(latest)
    expect(controller.getSnapshot().notice).toBe('')
  })
  it('projects the real pending when switching away and back to the same context', async () => {
    const gate = deferred<unknown>()
    const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => gate.promise)
    const runB = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(runA)
    const first = controller.run()
    const original = controller.getSnapshot().pending
    controller.configure({ ...context, inputVersion: 'V2' }, catalog, { runSample: runB })
    controller.configure(context, catalog, { runSample: (request) => runB(request) })
    expect(controller.getSnapshot().pending).toBe(original)
    await controller.run()
    expect(runB).not.toHaveBeenCalled()
    gate.resolve(result(runA.mock.calls[0][0].binding))
    await first
    expect(controller.getSnapshot().result).toBeUndefined()
    expect(controller.getSnapshot().pending).toBeUndefined()
    await controller.run()
    expect(runB).toHaveBeenCalledTimes(1)
  })
  it('retains a real refresh across callback churn without rerunning events or losing editor contents', async () => {
    const gate = deferred<unknown>()
    const run = vi.fn(async (request: SampleRequest) => result(request.binding))
    const refreshA = vi.fn<(binding: Binding, runId: string) => Promise<unknown>>(
      () => gate.promise,
    )
    const refreshB = vi.fn()
    const controller = setup(run)
    controller.configure(context, catalog, { runSample: run, refreshResult: refreshA })
    await controller.run()
    const binding = controller.getSnapshot().result!.binding
    const refreshing = controller.refresh()
    controller.editDraft({ ...draft, name: '宿主重绘保留草稿' })
    controller.configure(context, catalog, {
      runSample: (request) => run(request),
      refreshResult: () => refreshB(),
    })
    await controller.run()
    await controller.refresh()
    expect(run).toHaveBeenCalledTimes(1)
    expect(refreshB).not.toHaveBeenCalled()
    gate.resolve(result(binding, { freshness: 'stale', freshnessDetail: '实际版本已变化' }))
    await refreshing
    expect(refreshA).toHaveBeenCalledWith(binding, 'R1')
    expect(controller.getSnapshot().pending).toBeUndefined()
    expect(controller.getSnapshot().result?.freshness).toBe('stale')
    expect(controller.getSnapshot().draft.name).toBe('宿主重绘保留草稿')
  })
  it('a genuinely cancelled run may have a late Promise; its finally cannot clear the next cancellation', async () => {
    const runGateA = deferred<unknown>()
    const cancelGateA = deferred<unknown>()
    const runGateB = deferred<unknown>()
    const cancelGateB = deferred<unknown>()
    const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => runGateA.promise)
    const runB = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => runGateB.promise)
    const cancelA = vi.fn<(binding: Binding) => Promise<unknown>>(() => cancelGateA.promise)
    const cancelB = vi.fn<(binding: Binding) => Promise<unknown>>(() => cancelGateB.promise)
    const controller = setup(runA)
    controller.configure(context, catalog, { runSample: runA, cancelSample: cancelA })
    const first = controller.run()
    const cancellingFirst = controller.cancel()
    controller.configure(context, catalog, {
      runSample: (request) => runB(request),
      cancelSample: (binding) => cancelB(binding),
    })
    await controller.run()
    await controller.cancel()
    expect(runB).not.toHaveBeenCalled()
    expect(cancelB).not.toHaveBeenCalled()
    expect(controller.getSnapshot().cancelling).toBe(true)
    cancelGateA.resolve(result(runA.mock.calls[0][0].binding, { state: 'cancelled' }))
    await cancellingFirst
    expect(controller.getSnapshot().pending).toBeUndefined()
    const second = controller.run()
    const cancellingSecond = controller.cancel()
    const nextPending = controller.getSnapshot().pending
    runGateA.resolve(result(runA.mock.calls[0][0].binding))
    await first
    expect(controller.getSnapshot().pending).toBe(nextPending)
    expect(controller.getSnapshot().cancelling).toBe(true)
    cancelGateB.resolve(result(runB.mock.calls[0][0].binding, { state: 'cancelled' }))
    await cancellingSecond
    runGateB.resolve(result(runB.mock.calls[0][0].binding))
    await second
    expect(controller.getSnapshot().result?.state).toBe('cancelled')
    expect(controller.getSnapshot().result?.binding).toEqual(runB.mock.calls[0][0].binding)
  })
  it('late cancellation failure after completion cannot overwrite a successor notice or pending', async () => {
    const runGateA = deferred<unknown>()
    const cancelGateA = deferred<unknown>()
    const runGateB = deferred<unknown>()
    const runA = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => runGateA.promise)
    const runB = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => runGateB.promise)
    const controller = setup(runA)
    controller.configure(context, catalog, {
      runSample: runA,
      cancelSample: () => cancelGateA.promise,
    })
    const first = controller.run()
    const cancelling = controller.cancel()
    runGateA.resolve(result(runA.mock.calls[0][0].binding))
    await first
    controller.configure(context, catalog, { runSample: runB })
    const second = controller.run()
    const pending = controller.getSnapshot().pending
    const notice = controller.getSnapshot().notice
    cancelGateA.reject(new Error('late private cancellation failure'))
    await cancelling
    expect(controller.getSnapshot().pending).toBe(pending)
    expect(controller.getSnapshot().notice).toBe(notice)
    runGateB.resolve(result(runB.mock.calls[0][0].binding))
    await second
  })
  it.each(['projectId', 'inputVersion', 'behaviorVersion', 'scopeId', 'requestId'] as const)(
    'mismatched cancellation %s keeps the real run and gives cancellation-specific guidance',
    async (field) => {
      const gate = deferred<unknown>()
      const run = vi.fn<(request: SampleRequest) => Promise<unknown>>(() => gate.promise)
      const controller = setup(run)
      controller.configure(context, catalog, {
        runSample: run,
        cancelSample: async (binding) =>
          result({ ...binding, [field]: 'foreign' }, { state: 'cancelled' }),
      })
      const pending = controller.run()
      await controller.cancel()
      expect(controller.getSnapshot().pending?.binding).toEqual(run.mock.calls[0][0].binding)
      expect(controller.getSnapshot().cancelling).toBe(false)
      expect(controller.getSnapshot().notice).toBe('取消尚未得到有效收尾确认，原请求继续等待。')
      gate.resolve(result(run.mock.calls[0][0].binding))
      await pending
      expect(controller.getSnapshot().result?.state).toBe('candidate')
    },
  )
  it('request identity creation failure is safely reported before a call or pending is started', async () => {
    const run = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(run)
    const uuid = vi.spyOn(crypto, 'randomUUID').mockImplementation(() => {
      throw new Error('private identity failure')
    })
    try {
      await controller.run()
      expect(run).not.toHaveBeenCalled()
      expect(controller.getSnapshot().pending).toBeUndefined()
      expect(controller.getSnapshot().notice).toBe(
        '无法建立隔离测试请求；尚未调用执行服务，请检查运行环境后重试。',
      )
    } finally {
      uuid.mockRestore()
    }
    await controller.run()
    expect(run).toHaveBeenCalledTimes(1)
  })
  it('mixed reserved-key events retain their exact editor text and reject the whole event until explicitly corrected', async () => {
    const run = vi.fn(async (request: SampleRequest) => result(request.binding))
    const controller = setup(run)
    const payload = '{"equipment":"T1","level":"high","__proto__":"x"}'
    controller.editEvents([{ ...events[0], payload }])
    await controller.run()
    expect(run).not.toHaveBeenCalled()
    expect(controller.getSnapshot().events[0].payload).toBe(payload)
    expect(controller.getSnapshot().issues[0].message).toContain(
      '该事件整体未执行，普通字段也不会提交',
    )
    controller.editEvents([{ ...events[0], payload: '{"equipment":"T1","level":"high"}' }])
    await controller.run()
    expect(run).toHaveBeenCalledTimes(1)
    expect(run.mock.calls[0][0].events[0].payload).toEqual({ equipment: 'T1', level: 'high' })
  })
})
