import { createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { flushSync } from 'react-dom'
import {
  AgentSidebar,
  type AgentSidebarProps,
} from '../../../apps/desktop/src/renderer/src/agent/AgentSidebar'

// Test-only browser surface. No main runtime imports, Buffer shim, transport or domain service.
type Event = Record<string, unknown> & { id: number; kind: string }
type Options = Partial<AgentSidebarProps> & {
  deferred?: boolean
  tools?: boolean
  handlers?: boolean
}
const initialContext: AgentSidebarProps['context'] = {
  projectId: 'p1',
  projectRevision: 1,
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  module: 'query',
  mode: 'tutor',
  selectedObjectIds: ['001', '002'],
}
const container = document.getElementById('root')!
let root: Root = createRoot(container)
let props: AgentSidebarProps
let events: Event[] = []
let nextId = 0
let deferred = false
let tools = false
const pending = new Map<number, { resolve: () => void; reject: (error: Error) => void }>()
const host = window as unknown as {
  t08Node: (kind: 'submit' | 'cancel', question?: string) => Promise<void>
  t08: {
    reset: (options?: Options) => void
    update: (patch: Partial<AgentSidebarProps>) => void
    events: () => Event[]
    settle: (id: number, success: boolean) => void
  }
}
function record(kind: string, details: Record<string, unknown> = {}) {
  const id = ++nextId
  events.push({ id, kind, context: structuredClone(props.context), ...details })
  return id
}
function operation(kind: string, details: Record<string, unknown> = {}) {
  const id = record(kind, details)
  return deferred
    ? new Promise<void>((resolve, reject) => pending.set(id, { resolve, reject }))
    : Promise.resolve()
}
function render() {
  flushSync(() => root.render(createElement(AgentSidebar, props)))
}
host.t08 = {
  reset(options = {}) {
    for (const value of pending.values()) value.resolve()
    pending.clear()
    root.unmount()
    root = createRoot(container)
    events = []
    nextId = 0
    const { deferred: wait = false, tools: toolMode = false, handlers = true, ...patch } = options
    deferred = wait
    tools = toolMode
    props = {
      context: structuredClone(initialContext),
      state: null,
      privacy: 'minimum',
      modelReady: true,
      localActions: ['hint'],
      ...(handlers
        ? {
            onAction: (action, target, assistance) =>
              operation('action', { action, target, assistance }),
            onSubmit: (question) => {
              if (!tools) return operation('submit', { question })
              record('submit', { question })
              return host.t08Node('submit', question)
            },
            onCancel: () => {
              record('cancel')
              if (tools) void host.t08Node('cancel').catch(() => record('binding-error'))
            },
            onRetry: () => operation('retry'),
            onPreviewDraft: (receipt) => {
              record('preview', { receipt: structuredClone(receipt) })
              if (receipt.outcome.kind === 'draft')
                receipt.outcome.detail = 'mutated callback clone'
            },
          }
        : {}),
      ...patch,
    }
    render()
  },
  update(patch) {
    props = { ...props, ...patch }
    render()
  },
  events: () => structuredClone(events),
  settle(id, success) {
    const value = pending.get(id)
    if (!value) throw Error('unknown fixture operation')
    pending.delete(id)
    if (success) value.resolve()
    else value.reject(Error('private-path/private-cell must never reach UI'))
  },
}
host.t08.reset()
