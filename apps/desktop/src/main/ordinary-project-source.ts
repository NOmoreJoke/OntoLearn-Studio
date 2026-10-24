import { randomUUID } from 'node:crypto'
import { safeError, type BridgeResult, type ProjectView } from '@ontolearn/contracts'
import { validateV2 } from '../../../../packages/contracts/src/v2'
import {
  EngineError,
  OrdinaryLibraryTransport,
  type EngineSupervisor,
  type OrdinaryRetentionAccount,
} from './engine'

export type OrdinaryOwner = Readonly<{ ownerId: string }>
export type OrdinaryChoice = Readonly<{ projectId: string }>
export type OrdinaryCurrent = Readonly<{
  owner: OrdinaryOwner
  supervisor: EngineSupervisor
  engineSessionId: string
  selectionSeq: number
  project: ProjectView
}> | null
interface IssuedChoice {
  ref: string
  session: string
  menuSeq: number
}
interface Action {
  id: string
  seq: number
  session: string
  state: 'ACTION' | 'VERIFIED' | 'SELECTED' | 'UNKNOWN'
  project?: ProjectView
  leaseRef?: string
  release?: Promise<void>
  bytes: number
  objects: number
  verifiedBytes?: number
  verifiedObjects?: number
}
const denied = {
  code: 'PERMISSION_DENIED',
  messageKey: 'permission.denied',
  params: {},
  retryable: false,
}
const invalidState = {
  code: 'INVALID_STATE',
  messageKey: 'protocol.invalidState',
  params: {},
  retryable: false,
}
function failure(error: typeof denied): EngineError {
  return new EngineError(error)
}
function frozenProject(value: unknown): ProjectView {
  if (!validateV2('result_project.get', value)) throw failure(invalidState)
  const project = value as ProjectView
  return Object.freeze({
    ...project,
    dependencyVector: Object.freeze({ ...project.dependencyVector }),
  })
}
function charge(project: ProjectView): { bytes: number; objects: number } {
  // Include the private transport's second retained copy in this same main-side book.
  const entries = Object.entries(project.dependencyVector)
  const bytes =
    4096 +
    8 *
      (project.projectId.length +
        project.inputSnapshotId.length +
        entries.reduce((n, [key]) => n + Buffer.byteLength(key, 'utf8') * 2 + 96, 0))
  return { bytes, objects: 128 + 8 * entries.length }
}

/** Main-only source. A DTO/string cannot replace the runtime-branded injected transport.
 * Production presently supplies null: neither userData, a menu click nor ownerId issues a read grant.
 */
export class OrdinaryProjectSource {
  readonly #transport: OrdinaryLibraryTransport | null
  readonly #owner: OrdinaryOwner | null
  readonly #retention: OrdinaryRetentionAccount | undefined
  #current: OrdinaryCurrent = null
  #revision = 0
  #sequence = 0
  #menuSeq = 0
  #disposed = false
  #choices = new Map<OrdinaryChoice, IssuedChoice>()
  #actions = new Map<number, Action>()
  #selected: Action | undefined
  #listeners = new Map<object, (value: OrdinaryCurrent, revision: number) => void>()
  #connectionRelease: (() => void) | undefined
  #choiceBytes = 4096
  #choiceObjects = 32
  constructor(transport: OrdinaryLibraryTransport | null) {
    this.#transport = OrdinaryLibraryTransport.owns(transport) ? transport : null
    this.#owner = this.#transport ? Object.freeze({ ownerId: this.#transport.ownerId }) : null
    if (this.#transport && this.#owner) {
      this.#retention = this.#transport.claimSource(this.#owner)
      const original = this.#transport
      this.#connectionRelease = original.observe((state) => {
        if (
          state.state === 'disconnected' ||
          (this.#current && state.engineSessionId !== this.#current.engineSessionId)
        ) {
          this.#fence()
          // Cleanup remains owned and session-pinned. A failure is retained as UNKNOWN.
          void this.#cleanup().catch(() => {})
        }
      })
      // Subscription precedes the initial session read; absence issues no grant.
      void original.engineSessionId
    }
  }
  hasTransport(transport: OrdinaryLibraryTransport | null): boolean {
    return this.#transport === transport
  }
  get available(): boolean {
    return !this.#disposed && this.#transport !== null
  }
  current(): OrdinaryCurrent {
    return this.#current
  }
  observe(listener: (value: OrdinaryCurrent, revision: number) => void): () => void {
    if (this.#disposed || this.#listeners.size >= 8) throw failure(invalidState)
    const registration = Object.freeze({})
    this.#listeners.set(registration, listener)
    try {
      listener(this.#current, this.#revision)
    } catch (cause) {
      this.#listeners.delete(registration)
      throw cause
    }
    return () => {
      this.#listeners.delete(registration)
    }
  }
  #notify(): void {
    for (const listener of this.#listeners.values()) {
      try {
        listener(this.#current, this.#revision)
      } catch {
        /* isolate each consumer */
      }
    }
  }
  #fence(): void {
    if (this.#sequence >= Number.MAX_SAFE_INTEGER) throw failure(invalidState)
    this.#sequence++
    this.#current = null
    this.#revision++
    this.#notify()
  }
  #room(extra: { bytes: number; objects: number }, replacing?: Action): void {
    const records = [...this.#actions.values(), ...(this.#selected ? [this.#selected] : [])].filter(
      (action) => action !== replacing,
    )
    const bytes = this.#choiceBytes + extra.bytes + records.reduce((n, a) => n + a.bytes, 0)
    const objects = this.#choiceObjects + extra.objects + records.reduce((n, a) => n + a.objects, 0)
    if (bytes > 262144 || objects > 4096) throw failure(invalidState)
    this.#retention?.reserve(bytes, objects)
  }
  #live(action: Action): boolean {
    return (
      !this.#disposed &&
      this.#transport !== null &&
      this.#owner !== null &&
      this.#sequence === action.seq &&
      this.#actions.get(action.seq) === action &&
      this.#transport.engineSessionId === action.session
    )
  }
  async choices(): Promise<ReadonlyArray<OrdinaryChoice>> {
    const transport = this.#transport
    if (this.#disposed || !transport || !this.#owner) throw failure(denied)
    if (this.#menuSeq >= Number.MAX_SAFE_INTEGER) throw failure(invalidState)
    const menuSeq = ++this.#menuSeq
    const result = await transport.request({ op: 'choices', ownerId: this.#owner.ownerId, menuSeq })
    if (
      this.#disposed ||
      menuSeq !== this.#menuSeq ||
      !transport.engineSessionId ||
      !validateV2('result_ordinary.library', result)
    )
      throw failure(denied)
    const data = result as {
      op: string
      ownerId: string
      menuSeq: number
      choices: Array<{ choiceRef: string; projectId: string }>
    }
    if (
      data.op !== 'choices' ||
      data.ownerId !== this.#owner.ownerId ||
      data.menuSeq !== menuSeq ||
      new Set(data.choices.map((c) => c.choiceRef)).size !== data.choices.length ||
      new Set(data.choices.map((c) => c.projectId)).size !== data.choices.length
    )
      throw failure(invalidState)
    const bytes = 4096 + data.choices.length * 1024,
      objects = 32 + data.choices.length * 16
    // Charge the old/new overlap before allocating/replacing issued handles.
    this.#room({ bytes, objects })
    this.#choiceBytes = bytes
    this.#choiceObjects = objects
    const issued = new Map<OrdinaryChoice, IssuedChoice>()
    for (const row of data.choices) {
      const choice = Object.freeze({ projectId: row.projectId })
      issued.set(choice, { ref: row.choiceRef, session: transport.engineSessionId, menuSeq })
    }
    this.#choices = issued
    return Object.freeze([...issued.keys()])
  }
  open(choice: OrdinaryChoice): Promise<BridgeResult<ProjectView>> {
    const issued = this.#choices.get(choice),
      transport = this.#transport,
      owner = this.#owner
    if (
      this.#disposed ||
      !issued ||
      !transport ||
      !owner ||
      issued.menuSeq !== this.#menuSeq ||
      issued.session !== transport.engineSessionId
    )
      return Promise.resolve({ ok: false, error: safeError(denied) })
    // Slot exhaustion does not discard UNKNOWN, the selected reference or an old action.
    if (this.#actions.size >= 2)
      return Promise.resolve({ ok: false, error: safeError(invalidState) })
    try {
      this.#room({ bytes: 2048, objects: 32 })
    } catch (cause) {
      return Promise.resolve({ ok: false, error: safeError((cause as EngineError).error) })
    }
    this.#fence()
    const action: Action = {
      id: randomUUID(),
      seq: this.#sequence,
      session: issued.session,
      state: 'ACTION',
      bytes: 2048,
      objects: 32,
    }
    this.#actions.set(action.seq, action)
    return this.#open(action, choice, issued)
  }
  async #open(
    action: Action,
    choice: OrdinaryChoice,
    issued: IssuedChoice,
  ): Promise<BridgeResult<ProjectView>> {
    const transport = this.#transport!,
      owner = this.#owner!
    try {
      await this.#cleanup(action)
      if (!this.#live(action)) throw failure(denied)
      const result = await transport.request({
        op: 'acquire',
        ownerId: owner.ownerId,
        actionId: action.id,
        actionSeq: action.seq,
        choiceRef: issued.ref,
      })
      if (!this.#live(action) || !validateV2('result_ordinary.library', result))
        throw failure(denied)
      const data = result as {
        op: string
        ownerId: string
        actionId: string
        actionSeq: number
        leaseRef: string
        project: ProjectView
      }
      if (
        data.op !== 'acquire' ||
        data.ownerId !== owner.ownerId ||
        data.actionId !== action.id ||
        data.actionSeq !== action.seq ||
        data.project.projectId !== choice.projectId
      )
        throw failure(invalidState)
      const cost = charge(data.project)
      this.#room(cost, action)
      action.project = frozenProject(data.project)
      action.leaseRef = data.leaseRef
      action.bytes = cost.bytes
      action.objects = cost.objects
      action.verifiedBytes = cost.bytes
      action.verifiedObjects = cost.objects
      action.state = 'VERIFIED'
      if (!this.#live(action)) throw failure(denied)
      const committed = await transport.request({
        op: 'commit',
        ownerId: owner.ownerId,
        actionId: action.id,
        actionSeq: action.seq,
        leaseRef: action.leaseRef,
      })
      if (!this.#live(action) || !validateV2('result_ordinary.library', committed))
        throw failure(denied)
      const ack = committed as typeof data
      if (
        ack.op !== 'commit' ||
        ack.ownerId !== owner.ownerId ||
        ack.actionId !== action.id ||
        ack.actionSeq !== action.seq ||
        ack.leaseRef !== action.leaseRef ||
        !sameProject(ack.project, action.project)
      )
        throw failure(invalidState)
      // Final ACK fence and publication share this stack; no consumer is called before publication.
      if (!this.#live(action)) throw failure(denied)
      action.state = 'SELECTED'
      this.#actions.delete(action.seq)
      this.#selected = action
      this.#current = Object.freeze({
        owner,
        supervisor: transport.supervisor,
        engineSessionId: action.session,
        selectionSeq: action.seq,
        project: action.project,
      })
      this.#revision++
      this.#notify()
      return { ok: true, data: action.project }
    } catch (cause) {
      // Preserve the first failure. A failed release is still an owned UNKNOWN record.
      try {
        await this.#release(action)
      } catch {
        /* retain responsibility */
      }
      return { ok: false, error: safeError(cause instanceof EngineError ? cause.error : undefined) }
    }
  }
  async #release(action: Action): Promise<void> {
    if (action.release) return action.release
    const transport = this.#transport,
      owner = this.#owner
    if (!transport || !owner) throw failure(denied)
    action.state = 'UNKNOWN'
    action.release = (async () => {
      const result = await transport.request({
        op: 'release',
        ownerId: owner.ownerId,
        actionId: action.id,
        actionSeq: action.seq,
      })
      if (!validateV2('result_ordinary.library', result)) throw failure(invalidState)
      const data = result as { op: string; ownerId: string; actionId: string; actionSeq: number }
      if (
        data.op !== 'release' ||
        data.ownerId !== owner.ownerId ||
        data.actionId !== action.id ||
        data.actionSeq !== action.seq
      )
        throw failure(invalidState)
      if (this.#actions.get(action.seq) === action) this.#actions.delete(action.seq)
      if (this.#selected === action) this.#selected = undefined
    })()
    try {
      await action.release
    } finally {
      action.release = undefined
    }
  }
  async #cleanup(except?: Action): Promise<void> {
    const records = [...this.#actions.values(), ...(this.#selected ? [this.#selected] : [])].filter(
      (a) => a !== except,
    )
    const results = await Promise.allSettled(records.map((action) => this.#release(action)))
    const failed = results.find((result) => result.status === 'rejected')
    if (failed?.status === 'rejected') throw failed.reason
  }
  closeSelection(): Promise<void> {
    this.#fence()
    return this.#cleanup()
  }
  createBlank: (intent: unknown) => never = () => {
    throw failure(invalidState)
  }
  dispose(): Promise<void> {
    if (!this.#disposed) {
      this.#fence()
      this.#disposed = true
      this.#connectionRelease?.()
      this.#listeners.clear()
      this.#choices.clear()
    }
    return this.#cleanup()
  }
  /** Only TaskService's authenticated readback stream may advance this same selected context. */
  observeProject(
    project: ProjectView,
    supervisor: EngineSupervisor,
    engineSessionId: string,
  ): void {
    const current = this.#current,
      selected = this.#selected
    if (
      !current ||
      !selected ||
      supervisor !== current.supervisor ||
      engineSessionId !== current.engineSessionId ||
      project.projectId !== current.project.projectId
    )
      return
    if (
      !validateV2('result_project.get', project) ||
      project.projectRevision < current.project.projectRevision
    )
      throw failure(invalidState)
    if (sameProject(project, current.project)) return
    if (project.projectRevision === current.project.projectRevision) throw failure(invalidState)
    const projectionCost = charge(project)
    // The original verified lease/transport copy remains retained for exact retries.
    const cost = {
      bytes: projectionCost.bytes + (selected.verifiedBytes ?? 0),
      objects: projectionCost.objects + (selected.verifiedObjects ?? 0),
    }
    this.#room(cost, selected)
    selected.project = frozenProject(project)
    selected.bytes = cost.bytes
    selected.objects = cost.objects
    this.#current = Object.freeze({ ...current, project: selected.project })
    this.#revision++
    this.#notify()
  }
}
function sameProject(a: ProjectView, b: ProjectView): boolean {
  return (
    a.projectId === b.projectId &&
    a.projectRevision === b.projectRevision &&
    a.inputSnapshotId === b.inputSnapshotId &&
    a.formatVersion === b.formatVersion &&
    JSON.stringify(Object.entries(a.dependencyVector).sort()) ===
      JSON.stringify(Object.entries(b.dependencyVector).sort())
  )
}
