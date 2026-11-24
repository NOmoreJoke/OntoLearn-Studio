import { errorText } from './presentation'
import {
  bindingSchema,
  draftSchema,
  emptyDraft,
  parseEvents,
  resultSchema,
  sameContext,
  validateDraft,
  type BehaviorDraft,
  type BehaviorResult,
  type BehaviorServices,
  type Binding,
  type Catalog,
  type Context,
  type Issue,
  type SampleEvent,
  type SampleRequest,
} from './model'

export interface WorkspaceState {
  context: Context
  draft: BehaviorDraft
  events: SampleEvent[]
  revision: number
  resultRevision?: number
  result?: BehaviorResult
  pending?: { kind: 'run' | 'refresh'; binding: Binding; revision: number }
  cancelling: boolean
  issues: Issue[]
  notice: string
}
interface Operation {
  // Object identity is the lifecycle token, independent of the display epoch.
  key: string
  view: NonNullable<WorkspaceState['pending']>
  epoch: number
  cancelAttempt?: object
}
function contextKey(context: Context): string {
  return JSON.stringify([
    context.projectId,
    context.inputVersion,
    context.behaviorVersion,
    context.scopeId,
  ])
}
export class BehaviorController {
  private listeners = new Set<() => void>()
  private epoch = 0
  // Only live component calls; no persisted jobs, timeout release or second Store authority.
  private operations = new Map<string, Operation>()
  private services: BehaviorServices
  private catalog: Catalog
  private state: WorkspaceState
  constructor(
    context: Context,
    catalog: Catalog,
    draft: BehaviorDraft = emptyDraft(),
    services: BehaviorServices = {},
  ) {
    this.services = services
    this.catalog = catalog
    this.state = {
      context: { ...context },
      draft: structuredClone(draft),
      events: [{ id: '', type: '', payload: '{}', changes: [] }],
      revision: 0,
      cancelling: false,
      issues: [],
      notice: '',
    }
  }
  getSnapshot = (): WorkspaceState => this.state
  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }
  private publish(patch: Partial<WorkspaceState>) {
    this.state = { ...this.state, ...patch }
    this.listeners.forEach((listener) => listener())
  }
  configure(
    context: Context,
    catalog: Catalog,
    services: BehaviorServices,
    initialDraft?: BehaviorDraft,
  ) {
    const changed = !sameContext(context, this.state.context)
    this.catalog = catalog
    // Inline callbacks may change on every host render. Identity is not an input version.
    // Calls already made retain their own Promise; only future calls use these functions.
    this.services = services
    if (changed) {
      this.epoch++
      const sameProject = context.projectId === this.state.context.projectId
      const operation = this.operations.get(contextKey(context))
      this.publish({
        context: { ...context },
        draft: sameProject ? this.state.draft : structuredClone(initialDraft ?? emptyDraft()),
        events: sameProject
          ? this.state.events
          : [{ id: '', type: '', payload: '{}', changes: [] }],
        revision: this.state.revision + 1,
        result: undefined,
        resultRevision: undefined,
        pending: operation?.view,
        cancelling: Boolean(operation?.cancelAttempt),
        issues: [],
        notice: operation
          ? '该输入的原请求仍在收尾；旧结果不会覆盖当前视图，请等待或请求取消。'
          : '输入上下文已切换；原请求结果不会覆盖当前视图。',
      })
    }
  }
  invalidate() {
    this.epoch++
    this.publish({ result: undefined, resultRevision: undefined })
  }
  editDraft(draft: BehaviorDraft) {
    this.publish({
      draft: structuredClone(draft),
      revision: this.state.revision + 1,
      issues: [],
      notice: '',
    })
  }
  editEvents(events: SampleEvent[]) {
    this.publish({
      events: structuredClone(events),
      revision: this.state.revision + 1,
      issues: [],
      notice: '',
    })
  }
  validate(): Issue[] {
    const issues = [
      ...validateDraft(this.state.draft, this.catalog),
      ...parseEvents(this.state.events).issues,
    ]
    this.publish({
      issues,
      notice: issues.length
        ? '请修复本地结构问题。'
        : '本地结构检查通过；真实推理、幂等与竞争检查仍由隔离执行服务完成。',
    })
    return issues
  }
  private currentOperation(): Operation | undefined {
    return this.operations.get(contextKey(this.state.context))
  }
  private begin(kind: 'run' | 'refresh', binding: Binding, revision: number): Operation {
    const operation: Operation = {
      key: contextKey(binding),
      view: { kind, binding, revision },
      epoch: ++this.epoch,
    }
    this.operations.set(operation.key, operation)
    this.publish({ pending: operation.view, cancelling: false })
    return operation
  }
  private owns(operation: Operation): boolean {
    return this.operations.get(operation.key) === operation
  }
  private visible(operation: Operation): boolean {
    return this.owns(operation) && sameContext(operation.view.binding, this.state.context)
  }
  private accepts(operation: Operation): boolean {
    return this.visible(operation) && operation.epoch === this.epoch
  }
  private finish(
    operation: Operation,
    invalidatedNotice = '原请求已收尾；旧输入结果未作为当前结果展示。',
  ) {
    if (!this.owns(operation)) return
    this.operations.delete(operation.key)
    if (sameContext(operation.view.binding, this.state.context)) {
      this.publish({
        pending: undefined,
        cancelling: false,
        ...(operation.epoch !== this.epoch ? { notice: invalidatedNotice } : {}),
      })
    }
  }
  async run() {
    if (this.currentOperation()) return
    const service = this.services.runSample
    if (!service) {
      this.publish({ notice: '隔离执行服务未接入，不能运行样本。' })
      return
    }
    if (!bindingSchema.safeParse({ ...this.state.context, requestId: 'validation' }).success) {
      this.publish({ notice: '缺少有效项目、输入版本或隔离范围，不能运行样本。' })
      return
    }
    if (this.validate().length) return
    let request: SampleRequest
    try {
      request = {
        binding: { ...this.state.context, requestId: crypto.randomUUID() },
        draft: draftSchema.parse(this.state.draft),
        events: parseEvents(this.state.events).events,
      }
    } catch {
      this.publish({ notice: '无法建立隔离测试请求；尚未调用执行服务，请检查运行环境后重试。' })
      return
    }
    const operation = this.begin('run', request.binding, this.state.revision)
    this.publish({
      result: undefined,
      resultRevision: undefined,
      notice: '正在请求隔离样本测试；正式项目数据不属于此请求范围。',
    })
    try {
      this.receive(await service(structuredClone(request)), operation)
    } catch (error) {
      if (this.accepts(operation)) {
        const known =
          error instanceof Error && 'code' in error && typeof error.code === 'string'
            ? (error.code as keyof typeof errorText)
            : undefined
        this.publish({
          notice:
            known && Object.hasOwn(errorText, known)
              ? errorText[known]
              : '隔离测试调用失败，未取得成功证据。请对账后重试。',
        })
      }
    } finally {
      this.finish(operation)
    }
  }
  private receive(value: unknown, operation: Operation, runId?: string) {
    if (!this.accepts(operation)) return
    const binding = operation.view.binding
    const parsed = resultSchema.safeParse(value)
    if (
      !parsed.success ||
      !sameContext(parsed.data.binding, binding) ||
      parsed.data.binding.requestId !== binding.requestId ||
      (runId !== undefined && parsed.data.runId !== runId)
    ) {
      this.publish({ notice: '返回结果格式或项目/版本/请求不匹配，已拒绝显示。' })
      return
    }
    this.publish({ result: parsed.data, resultRevision: operation.view.revision, notice: '' })
  }
  async refresh() {
    const result = this.state.result
    const service = this.services.refreshResult
    if (this.currentOperation() || !result || !service) return
    const operation = this.begin(
      'refresh',
      result.binding,
      this.state.resultRevision ?? this.state.revision,
    )
    this.publish({ notice: '正在读取此运行的状态；不会重发事件或覆盖编辑草稿。' })
    try {
      this.receive(
        await service(structuredClone(result.binding), result.runId),
        operation,
        result.runId,
      )
    } catch {
      if (this.accepts(operation))
        this.publish({ notice: '状态刷新失败，保留最后一次已核验结果。' })
    } finally {
      this.finish(operation)
    }
  }
  async cancel() {
    const service = this.services.cancelSample
    if (!service) return
    let operation = this.currentOperation()
    const result = this.state.result
    const reconcileCandidate =
      !operation && result?.state === 'candidate' && result.freshness === 'current'
    if (reconcileCandidate && result)
      operation = this.begin(
        'run',
        result.binding,
        this.state.resultRevision ?? this.state.revision,
      )
    if (!operation || operation.view.kind !== 'run' || operation.cancelAttempt) return
    const ownedOperation = operation
    const attempt = {}
    operation.cancelAttempt = attempt
    const ownsAttempt = () => this.owns(ownedOperation) && ownedOperation.cancelAttempt === attempt
    this.publish({ cancelling: true, notice: '已请求取消，等待服务确认收尾；尚未视为已取消。' })
    try {
      const value = await service(structuredClone(operation.view.binding))
      if (!ownsAttempt()) return
      const parsed = resultSchema.safeParse(value)
      const binding = operation.view.binding
      if (
        !parsed.success ||
        parsed.data.state !== 'cancelled' ||
        !sameContext(parsed.data.binding, binding) ||
        parsed.data.binding.requestId !== binding.requestId
      ) {
        if (this.visible(operation))
          this.publish({ notice: '取消尚未得到有效收尾确认，原请求继续等待。' })
        return
      }
      this.receive(parsed.data, operation)
      this.finish(operation, '原请求已确认取消；旧输入结果未作为当前结果展示。')
    } catch {
      if (ownsAttempt() && this.visible(operation))
        this.publish({ notice: '取消调用失败；运行状态未确认。' })
    } finally {
      if (ownsAttempt()) {
        operation.cancelAttempt = undefined
        if (reconcileCandidate) this.finish(operation)
        else if (this.visible(operation)) this.publish({ cancelling: false })
      }
    }
  }
}
