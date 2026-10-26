import type { Locator } from '@playwright/test'

export type UITarget = {
  key: string
  kind: 'region' | 'button' | 'textbox' | 'alert'
  name?: string
}
export type UINode = {
  text: string
  value: string | null
  enabled: boolean | null
  pre: string[]
  paragraphs: string[]
}
export type UISnapshot = Record<string, UINode[]>

/** Only observes elements already selected by public, exact Playwright role locators.
 * Supports this fixture's native light-DOM markup, failing closed for overrides.
 * No waits, business calls, DOM mutation, cached reads or truncated assertion data.
 */
export function snapshotElements(nodes: Element[], targets: UITarget[]): UISnapshot {
  const normalize = (value: string) =>
    value
      .replace(/[\u200b\u00ad]/g, '')
      .trim()
      .replace(/\s+/g, ' ')
  const result: UISnapshot = Object.fromEntries(targets.map(({ key }) => [key, []]))
  for (const node of nodes) {
    const tag = node.tagName.toLowerCase()
    const special =
      'script,noscript,style,input[type="submit"],input[type="button"],input[type="reset"]'
    if (
      !node.isConnected ||
      node.hasAttribute('aria-labelledby') ||
      node.closest('head') ||
      node.matches(special) ||
      node.querySelector(special) ||
      node.shadowRoot ||
      Array.from(node.querySelectorAll('*')).some((child) => child.shadowRoot)
    )
      throw new Error('Unsupported UI observation markup')
    const matches = targets.filter((target) => {
      if (target.kind === 'region')
        return tag === 'section' && node.getAttribute('aria-label') === target.name
      if (target.kind === 'alert') return node.getAttribute('role') === 'alert'
      if (target.kind === 'button')
        return tag === 'button' && normalize(node.textContent ?? '') === target.name
      if (tag !== 'input' && tag !== 'textarea') return false
      const labels = Array.from((node as HTMLInputElement).labels ?? [])
      return normalize(labels.map((label) => label.textContent ?? '').join(' ')) === target.name
    })
    if (matches.length !== 1) throw new Error('Ambiguous or unsupported UI observation target')
    const target = matches[0]!
    const native = target.kind === 'button' || target.kind === 'textbox'
    if (native && (node.hasAttribute('role') || node.hasAttribute('aria-label')))
      throw new Error('Native UI observation role/name override')
    // Playwright1.64.1 injected native BUTTON rule (local coreBundle injected
    // getAriaDisabled/isNativelyDisabled): native disabled OR nearest fieldset,
    // then nearest explicit aria true/false through parents/shadow hosts.
    let enabled: boolean | null = null
    if (target.kind === 'button') {
      const fieldset = node.closest('FIELDSET[DISABLED]')
      const legend = fieldset?.querySelector(':scope > LEGEND')
      enabled = !(
        node.hasAttribute('disabled') ||
        (fieldset && (!legend || !legend.contains(node)))
      )
      if (enabled) {
        for (let ancestor: Element | null = node; ancestor;) {
          const value = (ancestor.getAttribute('aria-disabled') || '').toLowerCase()
          if (value === 'true' || value === 'false') {
            enabled = value === 'false'
            break
          }
          const parent: ParentNode | null = ancestor.parentNode
          ancestor =
            ancestor.parentElement ??
            (parent?.nodeType === 11 && 'host' in parent ? (parent as ShadowRoot).host : null)
        }
      }
    }
    if (result[target.key]!.length) throw new Error('Duplicate strict UI observation target')
    const pre =
      target.kind === 'region'
        ? Array.from(node.querySelectorAll('pre'), (pre) => pre.textContent ?? '')
        : []
    if (pre.length > 1) throw new Error('Duplicate strict Diff pre target')
    result[target.key]!.push({
      text: node.textContent ?? '',
      value: target.kind === 'textbox' ? (node as HTMLInputElement).value : null,
      enabled,
      pre,
      paragraphs:
        target.kind === 'region'
          ? Array.from(node.querySelectorAll('p'), (p) => p.textContent ?? '')
          : [],
    })
  }
  return result
}

export async function observeUI(
  locator: Locator,
  targets: UITarget[],
  completed: (snapshot: UISnapshot) => void,
): Promise<UISnapshot> {
  const snapshot = await locator.evaluateAll(snapshotElements, targets)
  completed(snapshot)
  return snapshot
}

export function normalizeUIText(value: string): string {
  return value
    .replace(/[\u200b\u00ad]/g, '')
    .trim()
    .replace(/\s+/g, ' ')
}

export function exactlyOne(snapshot: UISnapshot, key: string): UINode | undefined {
  if ((snapshot[key]?.length ?? 0) > 1) throw new Error('Duplicate strict UI observation target')
  return snapshot[key]?.length === 1 ? snapshot[key]![0] : undefined
}

export function committedReceiptOperation(
  snapshot: UISnapshot,
  revision: number,
  uuidPattern: string,
): string | undefined {
  const receipt = exactlyOne(snapshot, 'receipt')
  if (!receipt || snapshot.pending?.length !== 0) return undefined
  // Preserve the original receipt.locator('p').first() identity source; do not
  // search later paragraphs for a convenient matching operation.
  const identity = normalizeUIText(receipt.paragraphs[0] ?? '').match(
    new RegExp(`^操作 (${uuidPattern})，提交版本 ${revision}。$`),
  )
  if (
    !identity ||
    receipt.paragraphs.filter((text) => normalizeUIText(text) === `当前已读版本 ${revision}。`)
      .length !== 1
  )
    return undefined
  return identity[1]
}

export function receiptHasOperation(snapshot: UISnapshot, operationId: string): boolean {
  const receipt = exactlyOne(snapshot, 'receipt')
  return !!receipt && receipt.text.includes(operationId)
}

export function reconciliationReady(snapshot: UISnapshot): boolean {
  return !!exactlyOne(snapshot, 'receipt') || exactlyOne(snapshot, 'reconcile')?.enabled === true
}

/** One task-owned slot, synchronously replaced after completed observations.
 * Only this diagnostic copy is bounded; assertion snapshots stay complete.
 * Normal timeout reports may retain it. Worker termination/cancellation may not.
 */
export function updateObservationSlot(
  annotations: Array<{ type: string; description?: string }>,
  scope: string,
  stage: string,
  observed: unknown,
) {
  const type = `${scope}-last-completed-observation`
  const text = JSON.stringify(
    {
      stage,
      at: new Date().toISOString(),
      monotonicMs: performance.now(),
      observed,
      boundary:
        'Earlier completed observation, not authoritative final business state; worker termination may lose this record.',
    },
    (_key, value: unknown) =>
      typeof value === 'string' && value.length > 4096
        ? { utf16Prefix: value.slice(0, 4096), originalUTF16Units: value.length, truncated: true }
        : value,
  )
  const description =
    Buffer.byteLength(text) <= 16384
      ? text
      : JSON.stringify({
          stage,
          at: new Date().toISOString(),
          monotonicMs: performance.now(),
          truncated: true,
          originalBytes: Buffer.byteLength(text),
          utf8PrefixBase64: Buffer.from(text).subarray(0, 11000).toString('base64'),
          boundary: 'Bounded earlier observation prefix only, not final business state.',
        })
  const slot = annotations.find((annotation) => annotation.type === type)
  if (slot) slot.description = description
  else annotations.push({ type, description })
  return description
}
