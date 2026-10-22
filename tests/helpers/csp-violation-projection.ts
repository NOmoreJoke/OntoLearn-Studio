export interface CspViolation {
  directive: string
  disposition: string
  blocked: string
}

export type CspViolationTuple = readonly [
  directive: string,
  disposition: string,
  blockedClass: string,
]

function blockedClass(blocked: string, receiverOrigin: string): string {
  if (blocked === 'inline') return 'inline'
  try {
    if (new URL(blocked).origin === receiverOrigin) return 'probe-origin'
  } catch {
    // Keep malformed and non-URL values as unexpected evidence below.
  }
  return `unexpected:${JSON.stringify(blocked)}`
}

/** Pure test oracle; callers supply an independent expected set, never a product policy. */
export function compareCspViolations(
  violations: readonly CspViolation[],
  receiver: string,
  expected: readonly CspViolationTuple[],
) {
  const receiverOrigin = new URL(receiver).origin
  if (receiverOrigin === 'null') throw new Error('INVALID_CSP_PROBE_ORIGIN')
  const raw = violations.map((violation) => ({ ...violation }))
  const counts = new Map<string, { tuple: CspViolationTuple; count: number }>()
  for (const violation of raw) {
    const tuple: CspViolationTuple = [
      violation.directive,
      violation.disposition,
      blockedClass(violation.blocked, receiverOrigin),
    ]
    const key = JSON.stringify(tuple)
    const previous = counts.get(key)
    if (previous) previous.count += 1
    else counts.set(key, { tuple, count: 1 })
  }
  const expectedByKey = new Map<string, CspViolationTuple>()
  for (const tuple of expected) {
    const key = JSON.stringify(tuple)
    if (expectedByKey.has(key)) throw new Error('DUPLICATE_EXPECTED_CSP_TUPLE')
    expectedByKey.set(key, tuple)
  }
  const missing = [...expectedByKey].filter(([key]) => !counts.has(key)).map(([, tuple]) => tuple)
  const extra = [...counts]
    .filter(([key]) => !expectedByKey.has(key))
    .map(([, value]) => value.tuple)
  return {
    raw,
    counts: [...counts.values()],
    missing,
    extra,
    matches: missing.length === 0 && extra.length === 0,
  }
}
