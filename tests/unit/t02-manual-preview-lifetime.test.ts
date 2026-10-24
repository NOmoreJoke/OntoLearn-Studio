/** Event/hook unit harness for the actual Page module. No React DOM, IPC or GUI proof. */
import { readFileSync } from 'node:fs'
import vm from 'node:vm'
import ts from 'typescript'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as facts from '../../apps/desktop/src/renderer/src/ontology/mainline-facts'
import {
  OntologySession,
  sourceIdentity,
} from '../../apps/desktop/src/renderer/src/ontology/mainline-session'
import { OntologyOperationBook } from '../../apps/desktop/src/renderer/src/ontology/mainline-operations'
import { projectOntology } from '../../apps/desktop/src/renderer/src/ontology/mainline-ontology'
import type {
  DomainRead,
  EditPlan,
  OntologyMainlineBridge,
} from '../../apps/desktop/src/renderer/src/ontology/mainline-api'

type Node = {
  type: string | ((props: Record<string, unknown>) => Node)
  props: Record<string, unknown>
}
type Effect = { dependencies: unknown[]; cleanup?: () => void }
const source = (): DomainRead => ({
  readVersion: 1,
  projectId: 'project-a',
  inputSnapshotId: 'a'.repeat(64),
  workspace: { draft: { state: 'missing', editor: 'ontology-transaction' } },
  domain: {
    projectRevision: 7,
    dependencyVector: { 'facts:asserted': 0 },
    state: {
      definitions: [],
      facts: [
        {
          id: 'f'.repeat(64),
          subject: 'urn:old',
          predicate: 'urn:p',
          object: '"old"',
          owner: null,
          source_row: null,
          managed_value: null,
        },
      ],
      mappingState: {},
    },
  },
})
function session() {
  let snapshot = { source: source(), phase: 'idle', stale: false, pending: undefined as unknown }
  const value = {
    getSnapshot: () => snapshot,
    subscribe: () => () => {},
    connectForPage: () => () => {},
    discardPreview: vi.fn(() => {
      snapshot = { ...snapshot, phase: 'idle' }
    }),
    read: vi.fn(async () => {}),
    prepare: vi.fn(async (plan: EditPlan) => {
      void plan
    }),
    publish: (patch: Partial<typeof snapshot>) => {
      snapshot = { ...snapshot, ...patch }
    },
    retire: () => {
      snapshot = { ...snapshot, stale: true }
    },
  }
  return value
}
function harness(initial = session()) {
  const slots: unknown[] = [],
    layout = new Map<number, Effect>(),
    passive = new Map<number, Effect>()
  let cursor = 0,
    tree: Node,
    current = initial,
    discovering = true
  const pending: Array<() => void> = []
  function effect(
    callback: () => void | (() => void),
    dependencies: unknown[] = [],
    target: Map<number, Effect>,
  ) {
    if (discovering) return
    const i = cursor++,
      previous = target.get(i)
    if (
      previous &&
      dependencies.length === previous.dependencies.length &&
      dependencies.every((v, j) => Object.is(v, previous.dependencies[j]))
    )
      return
    pending.push(() => {
      previous?.cleanup?.()
      target.set(i, { dependencies, cleanup: callback() || undefined })
    })
  }
  const hooks = {
    useState: (initialValue: unknown) => {
      const i = cursor++
      if (!(i in slots))
        slots[i] = typeof initialValue === 'function' ? initialValue() : initialValue
      return [
        slots[i],
        (value: unknown) => {
          slots[i] = typeof value === 'function' ? value(slots[i]) : value
        },
      ]
    },
    useRef: (value: unknown) => {
      const i = cursor++
      if (!(i in slots)) slots[i] = { current: value }
      return slots[i]
    },
    useMemo: (callback: () => unknown) => callback(),
    useSyncExternalStore: (_subscribe: unknown, get: () => unknown) => get(),
    useEffect: (callback: () => void | (() => void), deps: unknown[]) =>
      effect(callback, deps, passive),
    useLayoutEffect: (callback: () => void | (() => void), deps: unknown[]) =>
      effect(callback, deps, layout),
  }
  const jsx = (type: Node['type'], props: Node['props']): Node => ({ type, props })
  const marker = function OntologyPage() {
    return jsx('unused', {})
  }
  const exports: { OntologyMainlinePage?: (props: Record<string, unknown>) => Node } = {}
  const code = ts.transpileModule(
    readFileSync('apps/desktop/src/renderer/src/ontology/OntologyMainlinePage.tsx', 'utf8'),
    {
      compilerOptions: {
        target: ts.ScriptTarget.ES2022,
        module: ts.ModuleKind.CommonJS,
        jsx: ts.JsxEmit.ReactJSX,
      },
    },
  ).outputText
  vm.runInNewContext(code, {
    exports,
    Error,
    require: (name: string) => {
      if (name === 'react') return hooks
      if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx }
      if (name === './mainline-facts') return facts
      if (name === './mainline-session') return { sourceIdentity }
      if (name === './mainline-ontology') return { projectOntology }
      if (name === './OntologyPage') return { OntologyPage: marker }
      if (name.endsWith('.css')) return {}
      throw new Error(`Unexpected Page dependency: ${name}`)
    },
  })
  const outer = exports.OntologyMainlinePage!({ session: current, contextKey: 'unit' })
  const inner = (outer.type as (p: Record<string, unknown>) => Node)(outer.props)
  const editor = inner.type as (p: Record<string, unknown>) => Node
  discovering = false
  function render(next = current) {
    current = next
    cursor = 0
    tree = editor({ session: current })
    for (const callback of pending.splice(0)) callback()
  }
  function nodes(value: unknown): Node[] {
    if (Array.isArray(value)) return value.flatMap((item) => nodes(item))
    if (!value || typeof value !== 'object' || !('type' in value)) return []
    const node = value as Node
    return [node, ...nodes(node.props.children)]
  }
  function text(value: unknown): string {
    if (Array.isArray(value)) return value.map(text).join('')
    if (value && typeof value === 'object' && 'props' in value)
      return text((value as Node).props.children)
    return typeof value === 'string' || typeof value === 'number' ? String(value) : ''
  }
  const button = (name: string) => {
    const matches = nodes(tree).filter(
      (n) => n.type === 'button' && text(n.props.children) === name,
    )
    expect(matches).toHaveLength(1)
    return matches[0]!
  }
  function field(name: string, value: string) {
    const label = nodes(tree).find(
      (n) => n.type === 'label' && text(n.props.children).trim() === name,
    )
    if (!label) throw new Error(`Missing actual Page field ${name}`)
    const control = nodes(label).find((n) => n.type === 'input')!
    ;(control.props.onChange as (e: unknown) => void)({ target: { value } })
    render()
  }
  function click(name: string) {
    const target = button(name)
    ;(target.props.onClick as () => void)()
    render()
  }
  function submit() {
    const form = nodes(tree).find((n) => n.type === 'form')!
    ;(form.props.onSubmit as (e: unknown) => void)({ preventDefault() {} })
    render()
  }
  function structuralChange() {
    const node = nodes(tree).find((n) => n.type === marker)!
    ;(node.props.onDraftChange as () => void)()
    render()
  }
  function cleanupLayout() {
    for (const item of layout.values()) item.cleanup?.()
    layout.clear()
  }
  render()
  click('新建事实并读取当前基准')
  field('主体个体 IRI', 'urn:new')
  field('属性 IRI', 'urn:p')
  field('规范 RDF 对象', '"new"')
  return {
    initial,
    render,
    field,
    click,
    submit,
    structuralChange,
    cleanupLayout,
    text: () => text(tree),
    cleanupPassive: () => {
      for (const item of passive.values()) item.cleanup?.()
      passive.clear()
    },
  }
}
function digestQueue() {
  const queue: Array<{ resolve: (buffer: ArrayBuffer) => void; reject: (error: Error) => void }> =
    []
  vi.spyOn(crypto.subtle, 'digest').mockImplementation(
    () => new Promise((resolve, reject) => queue.push({ resolve, reject })),
  )
  return queue
}
const flush = async () => {
  for (let i = 0; i < 10; i++) await Promise.resolve()
}
const result = () => new Uint8Array(32).fill(1).buffer

afterEach(() => vi.restoreAllMocks())
describe('actual Page manual preview async lifetime (instrumented hook/event unit only)', () => {
  it('prepares the latest unchanged tuple exactly once after digest completion', async () => {
    const q = digestQueue(),
      h = harness()
    h.submit()
    expect(h.initial.prepare).not.toHaveBeenCalled()
    expect(q).toHaveLength(1)
    q[0]!.resolve(result())
    await flush()
    expect(h.initial.prepare).toHaveBeenCalledExactlyOnceWith({
      manual: [{ id: '01'.repeat(32), subject: 'urn:new', predicate: 'urn:p', object: '"new"' }],
    })
  })
  it.each([
    'input ABA',
    'reset',
    'load fact',
    'structural draft',
    'read',
    'source ABA',
    'project switch',
    'reading',
    'layout reattach',
    'pending',
    'retire',
    'layout detach',
    'session replacement',
  ])('refuses late hash after %s', async (change) => {
    const q = digestQueue(),
      h = harness()
    h.submit()
    expect(q).toHaveLength(1)
    if (change === 'input ABA') {
      h.field('规范 RDF 对象', '"changed"')
      h.field('规范 RDF 对象', '"new"')
    }
    if (change === 'reset') h.click('新建事实并读取当前基准')
    if (change === 'load fact') h.click('载入事实')
    if (change === 'structural draft') h.structuralChange()
    if (change === 'read') h.click('读取当前项目')
    if (change === 'source ABA') {
      const original = h.initial.getSnapshot().source
      h.initial.publish({ source: { ...original, inputSnapshotId: 'b'.repeat(64) } })
      h.initial.publish({ source: structuredClone(original) })
    }
    if (change === 'project switch') {
      const original = h.initial.getSnapshot().source
      h.initial.publish({ source: { ...original, projectId: 'project-b' } })
    }
    if (change === 'reading') h.initial.publish({ phase: 'reading' })
    if (change === 'layout reattach') {
      h.cleanupLayout()
      h.render()
    }
    if (change === 'pending') h.initial.publish({ pending: { operationId: 'owned-operation' } })
    if (change === 'retire') h.initial.retire()
    if (change === 'layout detach') h.cleanupLayout() // Deliberately before passive detach/dispose.
    const replacement = session()
    if (change === 'session replacement') h.render(replacement)
    q[0]!.resolve(result())
    await flush()
    expect(h.initial.prepare).not.toHaveBeenCalled()
    expect(replacement.prepare).not.toHaveBeenCalled()
  })
  it('supersedes older preview even when tuple is identical', async () => {
    const q = digestQueue(),
      h = harness()
    h.submit()
    h.submit()
    expect(q).toHaveLength(2)
    q[0]!.resolve(result())
    await flush()
    expect(h.initial.prepare).not.toHaveBeenCalled()
    q[1]!.resolve(result())
    await flush()
    expect(h.initial.prepare).toHaveBeenCalledTimes(1)
  })
  it('does not surface an obsolete hash rejection on the new draft', async () => {
    const q = digestQueue(),
      h = harness()
    h.submit()
    expect(q).toHaveLength(1)
    h.field('规范 RDF 对象', '"changed"')
    q[0]!.reject(new Error('OLD_HASH_FAILURE'))
    await flush()
    h.render()
    expect(h.initial.prepare).not.toHaveBeenCalled()
    expect(h.text()).not.toContain('无法预览')
  })
  it.each(['retire', 'layout detach before ordinary dispose'])(
    'blocks old hash with the actual Session lifecycle: %s',
    async (change) => {
      const bridge = {
        readProject: vi.fn(async () => ({ ok: true, data: source() })),
        onTaskUpdate: vi.fn(() => () => {}),
        getActiveProject: vi.fn(),
        previewProjectChangeset: vi.fn(),
      }
      const real = new OntologySession(
        bridge as unknown as OntologyMainlineBridge,
        new OntologyOperationBook(),
      )
      real.connect()
      await real.read()
      const prepare = vi.spyOn(real, 'prepare')
      const q = digestQueue(),
        h = harness(real as unknown as ReturnType<typeof session>)
      h.submit()
      expect(q).toHaveLength(1)
      try {
        if (change === 'retire') real.retire()
        else {
          h.cleanupLayout()
          const snapshot = real.getSnapshot()
          real.dispose() // Unlike retire, this does not publish a new snapshot.
          expect(real.getSnapshot()).toBe(snapshot)
        }
        q[0]!.resolve(result())
        await flush()
        expect(prepare).not.toHaveBeenCalled()
        expect(bridge.getActiveProject).not.toHaveBeenCalled()
        expect(bridge.previewProjectChangeset).not.toHaveBeenCalled()
      } finally {
        real.dispose()
        h.cleanupLayout()
      }
    },
  )
  it('renders a current digest error while ignoring one from a detached attachment', async () => {
    const q = digestQueue(),
      h = harness()
    h.submit()
    expect(q).toHaveLength(1)
    q[0]!.reject(new Error('CURRENT_HASH_FAILURE'))
    await flush()
    h.render()
    expect(h.text()).toContain('无法预览')
    h.field('规范 RDF 对象', '"newer"')
    h.submit()
    expect(q).toHaveLength(2)
    h.cleanupLayout()
    h.render() // A fresh attachment must not revive the old request.
    q[1]!.reject(new Error('OLD_ATTACHMENT_FAILURE'))
    await flush()
    h.render()
    expect(h.initial.prepare).not.toHaveBeenCalled()
    expect(h.text()).not.toContain('无法预览')
  })
  it('does not adopt a newer draft generation changed by a synchronous discard subscriber', async () => {
    const q = digestQueue(),
      h = harness()
    const discard = h.initial.discardPreview.getMockImplementation()!
    h.initial.discardPreview.mockImplementationOnce(() => {
      discard()
      h.field('规范 RDF 对象', '"subscriber changed"')
    })
    h.submit()
    await flush()
    expect(q).toHaveLength(0)
    expect(h.initial.prepare).not.toHaveBeenCalled()
  })
})
