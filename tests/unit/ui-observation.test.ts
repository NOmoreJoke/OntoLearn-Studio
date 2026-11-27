import { describe, expect, test } from 'vitest'
import type { Locator } from '@playwright/test'
import {
  DisconnectedObservationError,
  exactlyOne,
  committedReceiptOperation,
  normalizeUIText,
  observeUI,
  receiptHasOperation,
  reconciliationReady,
  snapshotElements,
  updateObservationSlot,
  validObservation,
  type UINode,
  type UISnapshot,
} from '../e2e/ui-observation'

// Isolated test-only DOM-shaped values, never Electron/product acceptance.
function button(
  text = '核对原操作与提交回执',
  attrs: Record<string, string> = {},
  options: {
    parent?: Element
    fieldset?: Element
    connected?: boolean
  } = {},
): Element {
  return {
    tagName: 'BUTTON',
    textContent: text,
    isConnected: options.connected ?? true,
    shadowRoot: null,
    parentElement: options.parent ?? null,
    parentNode: options.parent ?? null,
    hasAttribute: (key: string) => Object.hasOwn(attrs, key),
    getAttribute: (key: string) => attrs[key] ?? null,
    closest: (selector: string) =>
      selector === 'FIELDSET[DISABLED]' ? (options.fieldset ?? null) : null,
    querySelector: () => null,
    querySelectorAll: () => [],
    matches: () => false,
  } as unknown as Element
}
const targets = [{ key: 'reconcile', kind: 'button' as const, name: '核对原操作与提交回执' }]
const node = (text: string, enabled: boolean | null = null): UINode => ({
  text,
  enabled,
  value: null,
  pre: [],
  paragraphs: [],
})
const enabled = (element: Element) =>
  exactlyOne(snapshotElements([element], targets), 'reconcile')!.enabled

describe('pure test observation regression, not product evidence', () => {
  test('removed button is an immediate incomplete snapshot until the same operation receipt appears', () => {
    const pending: UISnapshot = { receipt: [], reconcile: [node('button', false)] }
    const removed: UISnapshot = { receipt: [], reconcile: [] }
    const succeeded: UISnapshot = {
      receipt: [node('操作 original-operation，提交版本 1。')],
      reconcile: [],
    }
    expect(reconciliationReady(pending)).toBe(false)
    expect(reconciliationReady(removed)).toBe(false)
    expect(receiptHasOperation(removed, 'original-operation')).toBe(false)
    expect(reconciliationReady(succeeded)).toBe(true)
    expect(receiptHasOperation(succeeded, 'original-operation')).toBe(true)
    expect(receiptHasOperation(succeeded, 'different-operation')).toBe(false)
    expect(() =>
      receiptHasOperation(
        { ...succeeded, receipt: [...succeeded.receipt!, ...succeeded.receipt!] },
        'original-operation',
      ),
    ).toThrow('Duplicate')
    expect(reconciliationReady({ receipt: [], reconcile: [node('button', true)] })).toBe(true)
  })

  test('native disabled and nearest disabled fieldset keep first legend exemption', () => {
    const blocked = { querySelector: () => null } as unknown as Element
    const firstLegend = { contains: () => true } as unknown as Element
    const exempt = { querySelector: () => firstLegend } as unknown as Element
    expect(enabled(button())).toBe(true)
    expect(enabled(button(undefined, { disabled: '', 'aria-disabled': 'false' }))).toBe(false)
    expect(enabled(button(undefined, {}, { fieldset: blocked }))).toBe(false)
    expect(enabled(button(undefined, {}, { fieldset: exempt }))).toBe(true)
  })

  test('nearest explicit ARIA true/false follows Playwright case folding without trimming', () => {
    const parent = button(undefined, { 'aria-disabled': 'true' })
    expect(enabled(button(undefined, {}, { parent }))).toBe(false)
    expect(enabled(button(undefined, { 'aria-disabled': 'FALSE' }, { parent }))).toBe(true)
    expect(enabled(button(undefined, { 'aria-disabled': ' true ' }))).toBe(true)
    expect(enabled(button(undefined, { 'aria-disabled': 'TRUE' }))).toBe(false)
    const host = button(undefined, { 'aria-disabled': 'true' })
    const inShadow = button()
    Reflect.set(inShadow, 'parentNode', { nodeType: 11, host })
    expect(enabled(inShadow)).toBe(false)
  })

  test('duplicate exact matches and unsupported markup fail closed', () => {
    const actual = button()
    expect(() => snapshotElements([actual, actual], targets)).toThrow('Duplicate')
    expect(() => snapshotElements([button('other name')], targets)).toThrow('Ambiguous')
    expect(() =>
      snapshotElements([button(undefined, { 'aria-label': 'override' })], targets),
    ).toThrow('override')
    expect(() => snapshotElements([button(undefined, {}, { connected: false })], targets)).toThrow(
      'Unsupported',
    )
    const shadow = button()
    Reflect.set(shadow, 'shadowRoot', {})
    expect(() => snapshotElements([shadow], targets)).toThrow('Unsupported')
  })

  test('disconnected rounds are typed incomplete and never record completion', async () => {
    // The accepted shape is exactly the proven Playwright wrapper from the
    // CI46 Windows report.json failure: first line = optional report/evaluator
    // prefixes + browser error, stack strictly after the newline.
    const ci46Original =
      'Error: locator.evaluateAll: Error: Unsupported UI observation markup: disconnected\n' +
      '    at snapshotElements (...'
    for (const message of [
      ci46Original,
      'locator.evaluateAll: Error: Unsupported UI observation markup: disconnected\n' +
        '    at snapshotElements (<anonymous>:1:11)',
      'Error: Unsupported UI observation markup: disconnected',
      'Unsupported UI observation markup: disconnected',
    ]) {
      const locator = {
        evaluateAll: async () => {
          throw new Error(message)
        },
      } as unknown as Locator
      const completed: UISnapshot[] = []
      await expect(
        observeUI(locator, targets, (snapshot) => completed.push(snapshot)),
      ).rejects.toBeInstanceOf(DisconnectedObservationError)
      expect(completed).toEqual([])
    }
    const bare = {
      evaluateAll: async () => {
        throw new Error('Unsupported UI observation markup: disconnected')
      },
    } as unknown as Locator
    await expect(observeUI(bare, targets, () => {})).rejects.toThrow(
      /^Unsupported UI observation markup: disconnected$/,
    )
  })

  test('only the exact disconnected outcome is retryable; other errors stay fatal', async () => {
    for (const message of [
      // Unrelated failure whose diagnostic merely mentions the reason token.
      'Error: locator.evaluateAll: Error: unrelated failure; diagnostic mentions ' +
        'Unsupported UI observation markup: disconnected',
      // Reason with trailing explanation on the same line, or arbitrary
      // preceding text: outside the proven wrapper, therefore fatal.
      'Unsupported UI observation markup: disconnected; extra explanation',
      'preceding text Unsupported UI observation markup: disconnected',
      'Error: locator.evaluateAll: Error: Unsupported UI observation markup: aria-labelledby',
      'Unsupported UI observation markup: special-descendant',
      'Error: locator.evaluateAll: Error: Unsupported UI observation markup: disconnectedX',
      'Ambiguous or unsupported UI observation target',
      'Target closed',
    ]) {
      const locator = {
        evaluateAll: async () => {
          throw new Error(message)
        },
      } as unknown as Locator
      const completed: UISnapshot[] = []
      await expect(
        observeUI(locator, targets, (snapshot) => completed.push(snapshot)),
      ).rejects.toThrow(message.split('\n')[0]!.slice(0, 120))
      expect(completed).toEqual([])
      await expect(validObservation(() => observeUI(locator, targets, () => {}))).rejects.toThrow(
        message.split('\n')[0]!.slice(0, 120),
      )
    }
  })

  test('validObservation passes successful rounds through and maps only disconnected to incomplete', async () => {
    const snapshot: UISnapshot = { reconcile: [node('button', true)] }
    const ok = { evaluateAll: async () => snapshot } as unknown as Locator
    let rounds = 0
    const observe = () =>
      observeUI(
        {
          evaluateAll: async () => {
            rounds += 1
            if (rounds === 1) throw new Error('Unsupported UI observation markup: disconnected')
            return snapshot
          },
        } as unknown as Locator,
        targets,
        () => {},
      )
    expect(await validObservation(observe)).toBeUndefined()
    expect(await validObservation(observe)).toEqual(snapshot)
    expect(await validObservation(() => observeUI(ok, targets, () => {}))).toEqual(snapshot)
  })

  test('unsupported markup names only the first matched guard and never touches later ones', () => {
    // Every later guard is either a throwing sentinel or a different-reason trap,
    // so each exact message also proves evaluation stopped at the first match.
    const later = () => {
      throw new Error('later guard accessed')
    }
    const disconnected = {
      ...button(undefined, { 'aria-labelledby': 'label' }, { connected: false }),
      closest: later,
      matches: later,
      querySelector: later,
      querySelectorAll: later,
      shadowRoot: {},
    } as unknown as Element
    expect(() => snapshotElements([disconnected], targets)).toThrow(
      /^Unsupported UI observation markup: disconnected$/,
    )
    const labelled = {
      ...button(undefined, { 'aria-labelledby': 'label' }),
      closest: later,
      matches: later,
      querySelector: later,
      querySelectorAll: later,
      shadowRoot: {},
    } as unknown as Element
    expect(() => snapshotElements([labelled], targets)).toThrow(
      /^Unsupported UI observation markup: aria-labelledby$/,
    )
    const inHead = {
      ...button(),
      closest: (selector: string) => (selector === 'head' ? ({} as Element) : null),
      matches: later,
      querySelector: later,
      querySelectorAll: later,
      shadowRoot: {},
    } as unknown as Element
    expect(() => snapshotElements([inHead], targets)).toThrow(
      /^Unsupported UI observation markup: head-ancestor$/,
    )
    const specialSelf = {
      ...button(),
      matches: () => true,
      querySelector: later,
      querySelectorAll: later,
      shadowRoot: {},
    } as unknown as Element
    expect(() => snapshotElements([specialSelf], targets)).toThrow(
      /^Unsupported UI observation markup: special-self$/,
    )
    const specialDescendant = {
      ...button(),
      querySelector: () => ({}) as Element,
      querySelectorAll: later,
      shadowRoot: {},
    } as unknown as Element
    expect(() => snapshotElements([specialDescendant], targets)).toThrow(
      /^Unsupported UI observation markup: special-descendant$/,
    )
    const shadowSelf = {
      ...button(),
      shadowRoot: {},
      querySelectorAll: later,
    } as unknown as Element
    expect(() => snapshotElements([shadowSelf], targets)).toThrow(
      /^Unsupported UI observation markup: shadow-self$/,
    )
    const shadowDescendant = {
      ...button(),
      querySelectorAll: () => [{ shadowRoot: {} }] as unknown as Element[],
    } as unknown as Element
    expect(() => snapshotElements([shadowDescendant], targets)).toThrow(
      /^Unsupported UI observation markup: shadow-descendant$/,
    )
  })

  test('normalized text and unnormalized complete input values remain separate', () => {
    expect(normalizeUIText('  操作\u200b未能\u00ad完成：\n INVALID_REQUEST。 ')).toBe(
      '操作未能完成： INVALID_REQUEST。',
    )
    const raw = '  "泵站A"@zh\n' + '9'.repeat(4301)
    const input = {
      ...button(),
      tagName: 'INPUT',
      textContent: '',
      value: raw,
      labels: [{ textContent: '规范 RDF 对象' }],
    } as unknown as Element
    const actual = exactlyOne(
      snapshotElements([input], [{ key: 'object', kind: 'textbox', name: '规范 RDF 对象' }]),
      'object',
    )!
    expect(actual.value).toBe(raw)
    expect(actual.value).not.toBe(normalizeUIText(raw))
    expect(actual.enabled).toBeNull()
  })

  test('receipt keeps first paragraph identity, exact read version and no pending together', () => {
    const id = 'ded30765-ee2f-402b-98dd-7bc32d50ddeb'
    const pattern = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    const receipt = {
      ...node('untruncated'),
      paragraphs: [`操作 ${id}，提交版本 20。`, '当前已读版本 20。'],
    }
    expect(committedReceiptOperation({ receipt: [receipt], pending: [] }, 20, pattern)).toBe(id)
    expect(
      committedReceiptOperation({ receipt: [receipt], pending: [node('succeeded')] }, 20, pattern),
    ).toBeUndefined()
    expect(
      committedReceiptOperation(
        {
          receipt: [{ ...receipt, paragraphs: ['unrelated', ...receipt.paragraphs] }],
          pending: [],
        },
        20,
        pattern,
      ),
    ).toBeUndefined()
    expect(
      committedReceiptOperation(
        {
          receipt: [{ ...receipt, paragraphs: [receipt.paragraphs[0]!, '当前已读版本 19。'] }],
          pending: [],
        },
        20,
        pattern,
      ),
    ).toBeUndefined()
    expect(() =>
      committedReceiptOperation({ receipt: [receipt, receipt], pending: [] }, 20, pattern),
    ).toThrow('Duplicate')
  })

  test('one bounded slot is updated before failure and preserves other annotations', () => {
    const annotations = [{ type: 'unrelated', description: 'keep' }]
    const full = 'x'.repeat(100000)
    for (let index = 0; index < 1000; index++)
      updateObservationSlot(annotations, 'owned', `stage${index}`, { index, text: full })
    expect(annotations).toHaveLength(2)
    expect(annotations[0]).toEqual({ type: 'unrelated', description: 'keep' })
    const saved = annotations.find(
      (item) => item.type === 'owned-last-completed-observation',
    )!.description!
    expect(Buffer.byteLength(saved)).toBeLessThanOrEqual(16384)
    expect(JSON.parse(saved)).toMatchObject({
      stage: 'stage999',
      observed: { index: 999, text: { originalUTF16Units: 100000, truncated: true } },
    })
    expect(full).toHaveLength(100000)
    updateObservationSlot(
      annotations,
      'owned',
      'large structure',
      Array.from({ length: 2000 }, (_, index) => ({ index, value: 'a'.repeat(300) })),
    )
    const capped = annotations[1]!.description!
    expect(Buffer.byteLength(capped)).toBeLessThanOrEqual(16384)
    expect(JSON.parse(capped).truncated).toBe(true)
  })
})
