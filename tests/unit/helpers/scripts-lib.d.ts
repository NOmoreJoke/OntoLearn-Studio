// 纯函数测试对 scripts/lib/*.mjs 的最小类型声明。
// 运行时由 vitest 加载真实 .mjs 模块；此文件只满足 tsc 的模块解析。
declare module '*/lib/review-policy.mjs' {
  export function matchPathHint(path: string, pattern: string): boolean
  export function hintsFor(
    path: string,
    policy: { path_hints: Record<string, string[]> },
  ): Record<string, string[]>
  export function highestHint(
    path: string,
    policy: { path_hints: Record<string, string[]> },
  ): 'L2' | 'L1' | 'L0' | null
  export function isGovernancePath(
    path: string,
    policy: { path_hints: Record<string, string[]> },
  ): boolean
  export function isTestCodePath(path: string): boolean
  export function isTestSupportPath(path: string): boolean
  export function isStatusDocument(path: string): boolean
  export function provenLineEndingOnly(
    before: Uint8Array,
    after: Uint8Array,
  ): { proven: boolean; reason: string }
  export function parsePolicyText(text: string, sourceLabel: string): Record<string, unknown>
  export function sha256Hex(data: Uint8Array | string): string
}

declare module '*/lib/classify.mjs' {
  export interface ChangeInput {
    path: string
    status: string
    oldMode?: string
    newMode?: string
    beforeBytes: Uint8Array | null
    afterBytes: Uint8Array | null
    gitIgnoreableWhitespace?: boolean
    provenFormat?: { proven: boolean; reason: string }
  }
  export interface ChangeClassification {
    path: string
    status: string
    level: string
    basis: string
    reasons: string[]
    flags: Record<string, boolean>
  }
  export function semverOf(spec: unknown): { major: number; minor: number; patch: number } | null
  export function dependencyChanges(
    beforeText: string | null,
    afterText: string | null,
  ): Array<Record<string, string>> | null
  export function manifestNonDependencyChanges(
    beforeText: string | null,
    afterText: string | null,
  ): string[] | null
  export function lockVersionDelta(
    beforeText: string | null,
    afterText: string | null,
  ): {
    added: string[]
    removed: string[]
    changed: Array<{ name: string; from: string; to: string }>
  } | null
  export function lockMatchesManifest(
    lockDelta: {
      added: string[]
      removed: string[]
      changed: Array<{ name: string; from: string; to: string }>
    } | null,
    depChanges: Array<Record<string, string>> | null,
  ): boolean
  export function completionClaim(
    beforeText: string | null,
    afterText: string | null,
  ): { claimed: boolean; evidence?: string }
  export function completionClaimOutsideStatusDocument(
    beforeText: string | null,
    afterText: string | null,
  ): { claimed: boolean; evidence?: string }
  export function tautologySuspicion(beforeText: string | null, afterText: string | null): boolean
  export function workflowChangeKind(beforeText: string | null, afterText: string | null): string
  export function gateWeakening(
    path: string,
    beforeText: string | null,
    afterText: string | null,
  ): { weakened: boolean; evidence?: string; unparseable?: boolean }
  export function classifyChange(
    change: ChangeInput,
    ctx: Record<string, unknown>,
  ): ChangeClassification
  export function classifyCandidate(
    changes: ChangeInput[],
    ctx: Record<string, unknown>,
  ): {
    level: string
    provisionalLevel: string | null
    reasons: string[]
    perChange: ChangeClassification[]
    flags: Record<string, boolean>
    pendingTriage: ChangeClassification[]
    pendingSemanticReview: ChangeClassification[]
  }
  export function applyTriageDecisions(
    classification: Record<string, unknown>,
    decisions: Array<Record<string, unknown>>,
    changes: ChangeInput[],
    ctx: Record<string, unknown>,
  ): {
    level: string
    provisionalLevel: string | null
    reasons: string[]
    perChange: ChangeClassification[]
    pendingTriage: ChangeClassification[]
    errors?: string[]
    [key: string]: unknown
  }
}

declare module '*/lib/range-diff.mjs' {
  export function parseRangeDiff(rawOutput: string): {
    status: string
    patchUnchanged: boolean | null
    entries: Array<Record<string, unknown>>
    reason?: string
  }
  export function parseConflictsEvidence(doc: Record<string, unknown> | null): {
    status: string
    reason?: string
    source?: string
    count?: number
    paths?: string[]
  }
}

declare module '*/lib/checklist.mjs' {
  export const ANCHOR_SOURCE_SHA256: string
  export function extractOriginalEntries(originalBytes: Uint8Array): string[]
  export function verifySourceChecklist(
    originalBytes: Uint8Array,
    indexBytes: Uint8Array,
  ): {
    status: string
    errors: string[]
    checks: Array<{ name: string; expected: unknown; actual: unknown; pass: boolean }>
    summary: {
      sourceSha256: string
      total: number
      checkItems: number
      roleAppendixItems: number
    } | null
  }
}

declare module '*/lib/ci-reception.mjs' {
  export function sha256Hex(data: Uint8Array | string): string
  export function parseKnownOptions(
    argvList: string[],
    spec: Record<string, string>,
  ): { parsed: Record<string, string>; errors: string[] }
  export function receiveCiFinalState(input: Record<string, unknown>): {
    status: string
    evidenceSource?: string
    checks: Array<{ name: string; expected: unknown; actual: unknown; pass: boolean }>
    errors: string[]
    note?: string
  }
}
