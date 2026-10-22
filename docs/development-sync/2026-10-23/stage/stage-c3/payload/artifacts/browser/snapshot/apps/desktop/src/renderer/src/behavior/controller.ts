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
export class BehaviorController {
  private listeners = new Set<() => void>()
  private epoch = 0
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
    const serviceChanged =
      services.runSample !== this.services.runSample ||
      services.refreshResult !== this.services.refreshResult ||
      services.cancelSample !== this.services.cancelSample
    this.catalog = catalog
    this.services = services
    if (changed) {
      this.epoch++
      const sameProject = context.projectId === this.state.context.projectId
      this.publish({
        context: { ...context },
        draft: sameProject ? this.state.draft : structuredClone(initialDraft ?? emptyDraft()),
        events: sameProject
          ? this.state.events
          : [{ id: '', type: '', payload: '{}', changes: [] }],
        revision: this.state.revision + 1,
        result: undefined,
        resultRevision: undefined,
        pending: undefined,
        cancelling: false,
        issues: [],
        notice: '输入上下文已切换；原请求结果不会覆盖当前视图。',
      })
    } else if (serviceChanged) {
      this.invalidate()
      this.publish({
        pending: undefined,
        cancelling: false,
        notice: '能力连接已变化，请核对后重新运行。',
      })
    }
  }
  invalidate() {
    this.epoch++
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
  async run() {
    if (this.state.pending) return
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
    const binding = { ...this.state.context, requestId: `behavior-ui-${crypto.randomUUID()}` }
    const request: SampleRequest = {
      binding,
      draft: draftSchema.parse(this.state.draft),
      events: parseEvents(this.state.events).events,
    }
    const revision = this.state.revision
    const epoch = ++this.epoch
    this.publish({
      pending: { kind: 'run', binding, revision },
      result: undefined,
      resultRevision: undefined,
      notice: '正在请求隔离样本测试；正式项目数据不属于此请求范围。',
    })
    try {
      this.receive(await service(structuredClone(request)), binding, revision, epoch)
    } catch {
      if (this.accepts(binding, epoch))
        this.publish({ notice: '隔离测试调用失败，未取得成功证据。请对账后重试。' })
    } finally {
      if (this.accepts(binding, epoch)) this.publish({ pending: undefined, cancelling: false })
    }
  }
  private accepts(binding: Binding, epoch: number): boolean {
    return (
      epoch === this.epoch &&
      sameContext(binding, this.state.context) &&
      this.state.pending?.binding.requestId === binding.requestId
    )
  }
  private receive(
    value: unknown,
    binding: Binding,
    revision: number,
    epoch: number,
    runId?: string,
  ) {
    if (!this.accepts(binding, epoch)) return
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
    this.publish({ result: parsed.data, resultRevision: revision, notice: '' })
  }
  async refresh() {
    const result = this.state.result
    const service = this.services.refreshResult
    if (this.state.pending || !result || !service) return
    const binding = result.binding
    const epoch = ++this.epoch
    const revision = this.state.resultRevision ?? this.state.revision
    this.publish({
      pending: { kind: 'refresh', binding, revision },
      notice: '正在读取此运行的状态；不会重发事件或覆盖编辑草稿。',
    })
    try {
      this.receive(
        await service(structuredClone(binding), result.runId),
        binding,
        revision,
        epoch,
        result.runId,
      )
    } catch {
      if (this.accepts(binding, epoch))
        this.publish({ notice: '状态刷新失败，保留最后一次已核验结果。' })
    } finally {
      if (this.accepts(binding, epoch)) this.publish({ pending: undefined })
    }
  }
  async cancel() {
    const pending = this.state.pending
    const service = this.services.cancelSample
    if (!pending || pending.kind !== 'run' || this.state.cancelling || !service) return
    const epoch = this.epoch
    this.publish({ cancelling: true, notice: '已请求取消，等待服务确认收尾；尚未视为已取消。' })
    try {
      const result = await service(structuredClone(pending.binding))
      if (!this.accepts(pending.binding, epoch)) return
      const parsed = resultSchema.safeParse(result)
      if (!parsed.success || parsed.data.state !== 'cancelled') {
        this.publish({ notice: '取消尚未得到有效收尾确认，原请求继续等待。' })
        return
      }
      this.receive(result, pending.binding, pending.revision, epoch)
      if (
        sameContext(parsed.data.binding, pending.binding) &&
        parsed.data.binding.requestId === pending.binding.requestId
      ) {
        this.epoch++
        this.publish({ pending: undefined, cancelling: false })
      }
    } catch {
      if (this.accepts(pending.binding, epoch))
        this.publish({ notice: '取消调用失败；运行状态未确认。' })
    } finally {
      if (this.accepts(pending.binding, epoch)) this.publish({ cancelling: false })
    }
  }
}
