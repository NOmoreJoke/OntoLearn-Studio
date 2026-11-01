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
    // Same predicates, order and short-circuit as the original single guard;
    // the first true condition stops evaluation and names itself only.
    let unsupportedReason: string | undefined
    if (!node.isConnected) unsupportedReason = 'disconnected'
    else if (node.hasAttribute('aria-labelledby')) unsupportedReason = 'aria-labelledby'
    else if (node.closest('head')) unsupportedReason = 'head-ancestor'
    else if (node.matches(special)) unsupportedReason = 'special-self'
    else if (node.querySelector(special)) unsupportedReason = 'special-descendant'
    else if (node.shadowRoot) unsupportedReason = 'shadow-self'
    else if (Array.from(node.querySelectorAll('*')).some((child) => child.shadowRoot))
      unsupportedReason = 'shadow-descendant'
    if (unsupportedReason !== undefined)
      throw new Error(`Unsupported UI observation markup: ${unsupportedReason}`)
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

/** The single retryable observation outcome: a node already selected by the
 * public locator got disconnected between selection and read (Playwright
 * evaluates the query and the snapshot in separate awaits). The class cannot
 * cross the browser boundary, so observeUI re-raises it Node-side; every
 * other markup reason stays a fatal plain Error with its original message. */
export class DisconnectedObservationError extends Error {
  constructor() {
    super('Unsupported UI observation markup: disconnected')
    this.name = 'DisconnectedObservationError'
  }
}

// Playwright wraps browser-side evaluation errors before they reach Node,
// and reports prepend their own prefix; the CI46 Windows failure
// (report.json errors[].message) is exactly:
//   Error: locator.evaluateAll: Error: Unsupported UI observation markup:
//   disconnected\n    at snapshotElements …
// Classification accepts only that proven wrapper shape: the message's FIRST
// line, after stripping the optional report/evaluator prefixes, must equal
// the browser error exactly, with any stack strictly after the newline.
// Arbitrary preceding text, trailing explanation on the same line, other
// markup reasons, browser-closed and unknown errors all stay fatal; this is
// never a substring/includes match.
const DISCONNECTED_PREFIXES = ['Error: ', 'locator.evaluateAll: '] as const

export function isDisconnectedMarkup(error: unknown): boolean {
  if (!(error instanceof Error)) return false
  let line = error.message.split('\n', 1)[0] ?? ''
  for (const prefix of DISCONNECTED_PREFIXES) {
    if (line.startsWith(prefix)) line = line.slice(prefix.length)
  }
  return (
    line === 'Error: Unsupported UI observation markup: disconnected' ||
    line === 'Unsupported UI observation markup: disconnected'
  )
}

export async function observeUI(
  locator: Locator,
  targets: UITarget[],
  completed: (snapshot: UISnapshot) => void,
): Promise<UISnapshot> {
  let snapshot: UISnapshot
  try {
    snapshot = await locator.evaluateAll(snapshotElements, targets)
  } catch (error) {
    if (isDisconnectedMarkup(error)) throw new DisconnectedObservationError()
    throw error
  }
  completed(snapshot)
  return snapshot
}

/** One observation round under the caller's original poll deadline: the
 * identified disconnected outcome means "no valid snapshot this round"
 * (undefined) and the caller's own poll re-observes fresh nodes. Incomplete
 * rounds never invoke completed, count as success, or reuse an old snapshot;
 * every other error stays fatal. */
export async function validObservation<T>(observe: () => Promise<T>): Promise<T | undefined> {
  try {
    return await observe()
  } catch (error) {
    if (error instanceof DisconnectedObservationError) return undefined
    throw error
  }
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
