/**
 * W3b S2-4: the ontology workbench offers three stable views and reports the
 * current object selection to the host.
 *
 * The actual TSX is transpiled and driven with a minimal hook harness (the
 * same technique the existing T02 page test uses): no DOM, no IPC, no engine.
 */
import { readFileSync } from 'node:fs'
import ts from 'typescript'
import { describe, expect, it, vi } from 'vitest'

type Node = {
  type: string | ((props: Record<string, unknown>) => Node)
  props: Record<string, unknown>
}

const pagePath = 'apps/desktop/src/renderer/src/ontology/OntologyPage.tsx'
const viewModelPath = 'apps/desktop/src/renderer/src/ontology/view-model.ts'

function loadModule(file: string, modules: Record<string, unknown>): Record<string, unknown> {
  const code = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      jsx: ts.JsxEmit.ReactJSX,
    },
  }).outputText
  const exported: Record<string, unknown> = {}
  new Function('require', 'exports', code)((name: string) => {
    if (!(name in modules)) throw Error(`Unexpected renderer dependency ${name}`)
    return modules[name]
  }, exported)
  return exported
}

const sameDeps = (left: unknown[], right: unknown[]) =>
  left.length === right.length && left.every((value, index) => Object.is(value, right[index]))

function harness() {
  const slots: unknown[] = []
  const effects: Array<{ deps: unknown[]; cleanup?: () => void }> = []
  const pending: Array<() => void> = []
  let cursor = 0
  const hooks = {
    useState: (initial: unknown) => {
      const index = cursor++
      if (!(index in slots))
        slots[index] = typeof initial === 'function' ? (initial as () => unknown)() : initial
      return [
        slots[index],
        (value: unknown) => {
          slots[index] =
            typeof value === 'function' ? (value as (old: unknown) => unknown)(slots[index]) : value
        },
      ]
    },
    useRef: (value: unknown) => {
      const index = cursor++
      if (!(index in slots)) slots[index] = { current: value }
      return slots[index]
    },
    useMemo: (callback: () => unknown) => callback(),
    useEffect: (callback: () => void | (() => void), deps: unknown[] = []) => {
      const index = cursor++
      const previous = effects[index]
      if (previous && sameDeps(previous.deps, deps)) return
      // React runs the previous cleanup before the next effect of the same hook.
      previous?.cleanup?.()
      effects[index] = { deps }
      pending.push(() => {
        const result = callback()
        effects[index].cleanup = typeof result === 'function' ? result : undefined
      })
    },
    useLayoutEffect: (callback: () => void | (() => void)) => {
      callback()
    },
  }
  const jsx = (type: Node['type'], props: Record<string, unknown>): Node => ({ type, props })
  const viewModel = loadModule(viewModelPath, {})
  const page = loadModule(pagePath, {
    react: hooks,
    'react/jsx-runtime': { jsx, jsxs: jsx },
    './view-model': viewModel,
    './ontology.css': {},
  })
  const view = {
    project: 'project-a',
    revision: 7,
    objects: [
      {
        iri: 'urn:Equipment',
        kind: 'class',
        identifier: 'Equipment',
        labels: [['设备', 'zh']],
        definitions: [['设备类', 'zh']],
        synonyms: [],
        examples: [],
        parents: [],
        domain: [],
        range: [],
        types: [],
      },
      {
        iri: 'urn:Pump',
        kind: 'class',
        identifier: 'Pump',
        labels: [['泵', 'zh']],
        definitions: [],
        synonyms: [],
        examples: [],
        parents: ['urn:Equipment'],
        domain: [],
        range: [],
        types: [],
      },
    ],
    triples: [{ subject: 'urn:Pump', predicate: 'urn:partOf', object: '<urn:Equipment>' }],
  }
  const selected: string[][] = []
  const props = {
    view,
    onSelectedObjectChange: (ids: string[]) => selected.push(ids),
  }
  const outer = (page.OntologyPage as (props: Record<string, unknown>) => Node)(props)
  let tree = (outer.type as (props: Record<string, unknown>) => Node)(outer.props)
  function render() {
    cursor = 0
    tree = (outer.type as (props: Record<string, unknown>) => Node)(outer.props)
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
  function button(label: string): Node {
    const matches = nodes(tree).filter(
      (node) => node.type === 'button' && text(node.props.children) === label,
    )
    expect(matches).toHaveLength(1)
    return matches[0]!
  }
  function click(label: string) {
    ;(button(label).props.onClick as () => void)()
    render()
  }
  render()
  return {
    selected,
    render,
    click,
    unmount() {
      for (const effect of effects) effect?.cleanup?.()
      effects.length = 0
    },
    nodes: () => nodes(tree),
    text: () => text(tree),
    find: (testId: string) => nodes(tree).find((node) => node.props['data-testid'] === testId),
  }
}

describe('W3b S2-4: ontology multi-view and selection reporting', () => {
  it('keeps the three view switches addressable without losing the original wording', () => {
    const page = harness()
    for (const [view, label] of [
      ['table', '表格'],
      ['tree', '类树'],
      ['graph', '局部关系图'],
    ] as const) {
      const button = page
        .nodes()
        .find((node) => node.props['data-testid'] === `ontology-view-${view}`)
      expect(button, `missing ontology-view-${view}`).toBeTruthy()
      expect(button!.type).toBe('button')
      expect(textOf(button!)).toBe(label)
    }
    const nav = page.nodes().find((node) => node.props['aria-label'] === '本体视图')
    expect(nav).toBeTruthy()
  })

  it('reports the selected object and clears it when the editor is reset', () => {
    const page = harness()
    expect(page.selected.at(-1)).toEqual([])
    page.click('查看 Equipment')
    expect(page.selected.at(-1)).toEqual(['urn:Equipment'])
    page.click('新建概念')
    expect(page.selected.at(-1)).toEqual([])
  })

  it('shows the local graph container with a stable id in the graph view', () => {
    const page = harness()
    expect(page.find('ontology-local-graph')).toBeUndefined()
    page.click('局部关系图')
    const graph = page.find('ontology-local-graph')
    expect(graph).toBeTruthy()
    expect(graph!.type).toBe('div')
  })

  it('keeps the class tree readable from the same source of truth', () => {
    const page = harness()
    page.click('类树')
    expect(page.text()).toContain('设备')
    expect(page.text()).toContain('泵')
  })

  it('never reports a selection that the user did not make', () => {
    const page = harness()
    page.click('查看 Equipment')
    expect(page.selected.filter((ids) => ids.length === 0)).toHaveLength(1)
  })

  it('retires the object selection when the ontology context is left', () => {
    const page = harness()
    page.click('查看 Equipment')
    expect(page.selected.at(-1)).toEqual(['urn:Equipment'])
    page.unmount()
    // A retired context must not keep its object selection alive in the shared
    // Agent context of the next project or generation.
    expect(page.selected.at(-1)).toEqual([])
  })
})

function textOf(node: Node): string {
  if (Array.isArray(node.props.children))
    return node.props.children
      .map((child: unknown) => (typeof child === 'string' ? child : textOf(child as Node)))
      .join('')
  return typeof node.props.children === 'string' ? node.props.children : ''
}

void vi
