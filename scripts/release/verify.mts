import { createHash } from 'node:crypto'
import { closeSync, constants, fstatSync, openSync, readSync, realpathSync } from 'node:fs'
import { isAbsolute, relative, resolve, sep } from 'node:path'
import { z } from 'zod'

const text = z.string().trim().min(1).max(512)
const sha = z.string().regex(/^[a-f0-9]{64}$/)
const commit = z.string().regex(/^[a-f0-9]{40}$/)
const date = z.iso.datetime({ offset: true })
const ref = z.object({ path: text, sha256: sha }).strict()
const target = z.enum(['windows11-x64', 'macos15-arm64'])
const comparisonCase = z.enum(['current-state', 'g6-conflict'])
// Adopted controller decision, not a live service claim. endpoint means the request route.
export const APPROVED_MODEL = {
  endpoint: 'https://api.deepseek.com/chat/completions',
  requestedModel: 'deepseek-v4-pro',
  decisionSha256: 'def9817dc35c11514335fce5ecf859878e00cdfccc259659edb7925fee9d84a7',
} as const
// The committed production baseline (tests/fixtures/product-baselines/manifest.json at
// version prd-v0.6-learning-1). Pinned by content hashes only - the historic git-commit
// binding was dropped so evidence mode also verifies in .git-free archives.
export const APPROVED_BASELINE = {
  sha256: '0588f5804f0b13c55ccece009b444cfd3efcc572e53067703ca8d9224f4cf8ad',
  prdSha256: '7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb',
  version: 'prd-v0.6-learning-1',
  paths: [
    'content/learning/checks.json',
    'content/learning/course.json',
    'content/learning/extensions.json',
    'content/learning/glossary.json',
    'content/learning/transfer-inputs.json',
    ...[
      'E.5.json',
      'G-base.json',
      'G-behavior.json',
      'G-map-empty.json',
      'alarms.csv',
      'cases.json',
      'conventions.json',
      'coverage.json',
      'equipment-duplicate-key.csv',
      'equipment-missing-key.csv',
      'equipment-updated.csv',
      'equipment.csv',
      'unclosed-high.rq',
    ].map((name) => `tests/fixtures/product-baselines/${name}`),
  ],
} as const
const collectorStatus = z
  .object({
    schemaVersion: z.literal(1),
    status: z.literal('complete'),
    step: z.literal('complete'),
    exitCode: z.literal(0),
  })
  .strict()
const check = z.object({ id: text, expected: ref, actual: ref }).strict()
const report = z
  .object({
    candidateSha: commit,
    baselineSha256: sha,
    artifactSha256: sha,
    testedAt: date,
    operator: text,
    environment: text,
    raw: ref,
    checks: z.array(check).min(1).max(512),
  })
  .strict()
const signature = z
  .object({
    scheme: z.enum(['authenticode', 'developer-id']),
    identity: text,
    valid: z.boolean(),
    timestamped: z.boolean(),
    hardenedRuntime: z.boolean(),
    notarized: z.boolean(),
    stapled: z.boolean(),
    report,
  })
  .strict()
const component = z.object({ name: text, version: text, license: text, notice: ref }).strict()
const artifact = z
  .object({
    target,
    appVersion: text,
    format: z.enum(['nsis', 'dmg']),
    file: ref,
    bytes: z.number().int().positive(),
    appArch: z.enum(['x64', 'arm64']),
    engineArch: z.enum(['x64', 'arm64']),
    build: z
      .object({ sourceSha: commit, nodeLock: ref, pythonLock: ref, config: ref, report })
      .strict(),
    signature,
    components: z.array(component).min(1).max(1024),
    inventory: ref,
    device: z
      .object({
        id: text,
        os: z.enum(['Windows 11', 'macOS']),
        version: text,
        build: text,
        cpu: text,
        ramGiB: z.number().positive(),
        arch: z.enum(['x64', 'arm64']),
        cleanImage: text,
        isolatedSession: text,
        nodeInstalled: z.boolean(),
        pythonInstalled: z.boolean(),
        dockerRequired: z.boolean(),
        collectorStatus: ref,
        report,
      })
      .strict(),
    download: z
      .object({ url: z.url(), audience: text, file: ref, installed: z.boolean(), report })
      .strict(),
  })
  .strict()
const participant = z
  .object({
    id: text,
    human: z.boolean(),
    developer: z.boolean(),
    ontologyNovice: z.boolean(),
    artifactSha256: sha,
    testedAt: date,
    record: ref,
    assistance: z.enum([
      'independent',
      'product-hints',
      'partial-human-help',
      'full-demo',
      'agent-full',
    ]),
    coreCompleted: z.boolean(),
    transferCompleted: z.boolean(),
    transferIndependent: z.boolean(),
    agentFullCounterexample: z.boolean(),
    agentMarkedIndependent: z.boolean(),
    blockers: z.array(text).max(128),
  })
  .strict()
export const manifestSchema = z
  .object({
    schemaVersion: z.literal(1),
    mode: z.enum(['evidence', 'synthetic']),
    version: z.string().regex(/^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?$/),
    sourceSha: commit,
    candidateSha: commit,
    reviewedSha: commit,
    candidateFrozenAt: date,
    prd: ref,
    baseline: ref,
    artifacts: z.array(artifact).length(2),
    product: report,
    model: z
      .object({
        endpoint: z.url(),
        requestedModel: text,
        decisionSha256: sha,
        returnedModel: text,
        serviceVersion: text,
        mode: z.enum(['thinking', 'non-thinking']),
        evaluation: ref,
        fabricatedResults: z.number().int().nonnegative(),
        report,
      })
      .strict(),
    users: z.array(participant).min(5).max(100),
    reviews: z
      .array(
        z
          .object({
            provider: z.enum(['zcode', 'minimax']),
            model: text,
            effort: text,
            taskId: text,
            verdict: z.enum(['pass', 'fail', 'unverifiable']),
            unresolved: z.number().int().nonnegative(),
            report,
          })
          .strict(),
      )
      .length(2),
    engineering: report,
    recovery: z
      .object({
        backup: ref,
        restored: ref,
        rollbackInstallers: z
          .array(
            z
              .object({
                target,
                version: text,
                sourceSha: commit,
                file: ref,
                signature,
              })
              .strict(),
          )
          .length(2),
        report,
      })
      .strict(),
    migration: z
      .array(z.object({ from: target, to: target, before: ref, after: ref, report }).strict())
      .length(2),
  })
  .strict()
export type Manifest = z.infer<typeof manifestSchema>
export type Report = z.infer<typeof report>
export type Verification = {
  consistent: boolean
  releaseAuthorized: false
  mode: string
  issues: string[]
}
export const expectedSchema = z
  .object({
    candidateSha: commit,
    prdSha256: sha,
    baselineSha256: sha,
    candidateFrozenAt: date,
    modelEndpoint: z.url(),
    requestedModel: text,
    modelDecisionSha256: sha,
    modelMode: z.enum(['thinking', 'non-thinking']),
    evaluationSha256: sha,
    returnedModel: text,
    serviceVersion: text,
    recoverySnapshotSha256: sha,
    recoveryComparisonCase: comparisonCase,
    migrationComparisonCases: z
      .object({
        'windows11-x64': z.literal('g6-conflict'),
        'macos15-arm64': z.literal('g6-conflict'),
      })
      .strict(),
    migrationSnapshotSha256: z.object({ 'windows11-x64': sha, 'macos15-arm64': sha }).strict(),
    previousAssets: z
      .array(z.object({ target, version: text, sourceSha: commit, sha256: sha }).strict())
      .length(2),
    expectedResults: z.record(text, sha),
    now: date,
  })
  .strict()
export type Expected = z.infer<typeof expectedSchema>
const row = z
  .object({
    id: text,
    payload: z
      .record(text, z.unknown())
      .refine((value) => Object.keys(value).length > 0 && !('count' in value)),
  })
  .strict()
const rows = z
  .array(row)
  .refine((items) => new Set(items.map((item) => item.id)).size === items.length)
// The strict t11-comparison-v3 snapshot contract (selection-comparison-v3). Exported so
// the read-only T10 projector and cross-language tests validate the exact same shape.
export const comparisonSchema = z
  .object({
    format: z.literal('t11-comparison-v3'),
    comparisonCase,
    projectId: text,
    sourceSnapshotId: sha,
    projectRevision: z.number().int().nonnegative(),
    selection: z
      .object({
        currentDerived: z.boolean(),
        historicalRuns: z.boolean(),
        rawSources: z.boolean(),
        agentSessions: z.boolean(),
        priorUndo: z.boolean(),
      })
      .strict(),
    capabilities: z
      .object({
        restoreCurrent: z.literal(true),
        rerunOriginalMapping: z.boolean(),
        replaySandbox: z.boolean(),
      })
      .strict(),
    dependencies: z
      .object({
        mappingSources: z.enum(['embedded', 'missing']),
        replayInputs: z.boolean(),
        replayConfiguration: z.boolean(),
        replaySemantics: z.enum(['supported', 'missing', 'unsupported']),
      })
      .strict(),
    facts: rows,
    definitions: rows,
    ownership: rows,
    mappingState: rows,
    queries: rows,
    results: rows,
    derivedResults: rows,
    history: rows,
    rounds: rows,
    rawSources: rows,
    agentSessions: rows,
    undo: rows,
    executionVersions: z.object({ semantics: text, engine: text, lock: text }).strict(),
  })
  .strict()
  .superRefine((value, ctx) => {
    const reject = (message: string) => ctx.addIssue({ code: 'custom', message })
    // PRD G.6 template boundary remains mandatory, including generic recovery.
    if (!value.facts.length || !value.ownership.length) reject('TEMPLATE_NOT_RESTORABLE')
    if (
      value.comparisonCase === 'g6-conflict' &&
      ['facts', 'definitions', 'ownership', 'mappingState', 'queries', 'results'].some(
        (key) => !value[key as 'facts'].length,
      )
    )
      reject('G6_REQUIRED_LAYER')
    if (
      (!value.selection.currentDerived && value.derivedResults.length > 0) ||
      (!value.selection.historicalRuns && (value.history.length > 0 || value.rounds.length > 0)) ||
      (!value.selection.rawSources && value.rawSources.length > 0) ||
      (!value.selection.agentSessions && value.agentSessions.length > 0) ||
      (!value.selection.priorUndo && value.undo.length > 0)
    )
      reject('UNSELECTED_CONTENT')
    const canRerun =
      value.selection.rawSources &&
      value.rawSources.length > 0 &&
      value.dependencies.mappingSources === 'embedded'
    if (
      (value.dependencies.mappingSources === 'embedded' && !canRerun) ||
      value.capabilities.rerunOriginalMapping !== canRerun
    )
      reject('MAPPING_CAPABILITY')
    const canReplay =
      value.selection.historicalRuns &&
      value.history.length > 0 &&
      value.dependencies.replayInputs &&
      value.dependencies.replayConfiguration &&
      value.dependencies.replaySemantics === 'supported'
    if (value.capabilities.replaySandbox !== canReplay) reject('REPLAY_CAPABILITY')
  })
export const DEVICE_CHECKS = [
  'collector-complete',
  'installed-components-match-package',
  'install',
  'first-start',
  'offline-core',
  'credential-roundtrip',
  'credential-unavailable',
  'credential-corrupt',
  'credential-restart',
  'credential-signed-upgrade',
  'crash-mapping',
  'crash-changeset',
  'crash-sandbox',
  'unresponsive-recovery',
  'storage-failure',
  'cancel-zero-commit',
  'cancel-after-round',
  'response-lost',
  'upgrade',
  'uninstall-retain-data',
  'reinstall-restore',
  'authorized-directories-only',
  'no-network-listener',
  'no-model-call-local',
  'no-secrets-export-log',
  'html-no-execution',
]
export const ENGINEERING_CHECKS = [
  'check',
  'sources',
  'target-e2e',
  'package-samples',
  'ci',
  'remote-candidate',
  'capacity-approved-criteria',
  'capacity-measured',
  'semantic-matrix-C',
  'invalidation-D',
  'execution-E',
  'authorization-F',
  'prd-10',
  'prd-11',
  'prd-12',
]
export const MODEL_CHECKS = [
  'connection',
  'structured-output',
  'tool-roundtrip',
  'bad-output-rejected',
  'cancel-timeout',
  'no-fabrication',
  'tool-failure',
  'stale-results',
  'no-evidence',
  'final-field-authorization',
  'endpoint-change',
  'prompt-injection',
  'offline-fallback',
]
export const RECOVERY_CHECKS = [
  'backup-readable',
  'restore-complete',
  'rollback-format-compatible',
  'rollback-install',
  'rollback-retain-new-version-copy',
  'rollback-refuse-incompatible-format',
  'no-uncommitted-data',
  'no-auto-write-replay',
]
export const MIGRATION_CHECKS = [
  'asserted-facts',
  'definitions',
  'queries-results',
  'sources-ownership',
  'manual-conflicts',
  'relink-rerun-conflict',
  'continue-edit-query-undo',
  'history-rounds',
  'replay-versions',
  'missing-originals-warning',
  'template-not-restorable',
  'selected-only-no-credentials',
  'restore-current-without-history',
  'restore-without-originals',
  'rerun-after-relink',
  'replay-complete-inputs',
  'incomplete-replay-not-promised',
  'unselected-history-excluded',
  'unselected-derived-excluded',
  'unselected-session-excluded',
  'unselected-undo-excluded',
  'replay-zero-commit-inputs',
]
export const digest = (value: Uint8Array | string) =>
  createHash('sha256').update(value).digest('hex')

// Resolve containment first. Ancestor directories must remain trusted and stable while reading.
function boundPath(root: string, file: z.infer<typeof ref>): string {
  if (
    isAbsolute(file.path) ||
    file.path.includes('\\') ||
    file.path.split('/').some((p) => p === '..' || p === '.')
  )
    throw new Error('UNSAFE_PATH')
  const base = realpathSync(root)
  const path = realpathSync(resolve(base, file.path))
  const rel = relative(base, path)
  if (!rel || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel))
    throw new Error('UNSAFE_PATH')
  return path
}

// No-follow protects the resolved leaf; nonblocking permits rejecting FIFOs without blocking.
// Neither protects concurrently replaced ancestors. One fd supplies size, bytes, hash and format.
function withFile<T>(path: string, limit: number, consume: (fd: number, size: number) => T): T {
  const fd = openSync(
    path,
    constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0),
  )
  try {
    const before = fstatSync(fd)
    if (!before.isFile() || before.size < 1 || before.size > limit) throw new Error('FILE_BOUNDS')
    const result = consume(fd, before.size)
    const extra = Buffer.alloc(1)
    if (readSync(fd, extra, 0, 1, before.size) !== 0) throw new Error('FILE_CHANGED')
    const after = fstatSync(fd)
    if (
      !after.isFile() ||
      after.size !== before.size ||
      after.ino !== before.ino ||
      after.dev !== before.dev ||
      after.mtimeMs !== before.mtimeMs ||
      after.ctimeMs !== before.ctimeMs
    )
      throw new Error('FILE_CHANGED')
    return result
  } finally {
    closeSync(fd)
  }
}
function readExact(fd: number, buffer: Buffer, position: number): void {
  let offset = 0
  while (offset < buffer.length) {
    const count = readSync(fd, buffer, offset, buffer.length - offset, position + offset)
    if (count === 0) throw new Error('FILE_SHORT_READ')
    offset += count
  }
}
function readSmallFile(path: string, limit: number): Buffer {
  return withFile(path, limit, (fd, size) => {
    const bytes = Buffer.alloc(size)
    readExact(fd, bytes, 0)
    return bytes
  })
}
export function readJsonFile(path: string): unknown {
  // Limit is enforced before allocation and JSON.parse, including the CLI's trusted freeze.
  return JSON.parse(readSmallFile(path, 16 * 1024 * 1024).toString('utf8'))
}
export function readBound(
  root: string,
  file: z.infer<typeof ref>,
  limit = 16 * 1024 * 1024,
): Buffer {
  const bytes = readSmallFile(boundPath(root, file), limit)
  if (digest(bytes) !== file.sha256) throw new Error('FILE_HASH')
  return bytes
}
function installerFormat(fd: number, size: number, mac: boolean): boolean {
  if (mac) {
    if (size < 512) return false
    const tail = Buffer.alloc(4)
    readExact(fd, tail, size - 512)
    return tail.toString() === 'koly'
  }
  if (size < 64) return false
  const head = Buffer.alloc(64)
  readExact(fd, head, 0)
  if (head.readUInt16LE(0) !== 0x5a4d) return false
  const offset = head.readUInt32LE(0x3c)
  if (offset < 64 || offset > size - 6) return false
  const pe = Buffer.alloc(6)
  readExact(fd, pe, offset)
  return pe.readUInt32LE(0) === 0x4550 && [0x14c, 0x8664].includes(pe.readUInt16LE(4))
}
export function verifyLargeFile(
  root: string,
  file: z.infer<typeof ref>,
  mac?: boolean,
): { size: number; format: boolean } {
  return withFile(boundPath(root, file), 8 * 1024 ** 3, (fd, size) => {
    const hash = createHash('sha256')
    const buffer = Buffer.alloc(Math.min(size, 1024 * 1024))
    for (let position = 0; position < size;) {
      const part = buffer.subarray(0, Math.min(buffer.length, size - position))
      readExact(fd, part, position)
      hash.update(part)
      position += part.length
    }
    if (hash.digest('hex') !== file.sha256) throw new Error('FILE_HASH')
    return { size, format: mac === undefined || installerFormat(fd, size, mac) }
  })
}

function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`
  if (value && typeof value === 'object')
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${JSON.stringify(k)}:${canonical(v)}`)
      .join(',')}}`
  return JSON.stringify(value)
}
export function compareComplete(expected: unknown, actual: unknown): boolean {
  // Object key order is irrelevant. Arrays must already be normalized by the owning domain adapter.
  return canonical(expected) === canonical(actual)
}

export function compareProductComplete(expected: unknown, actual: unknown): boolean {
  const rdfFields = new Set(['facts', 'assertedFacts', 'inferred', 'addedTriples', 'inputs'])
  const isTriple = (value: unknown) =>
    value !== null &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    Object.keys(value).length === 3 &&
    ['subject', 'predicate', 'object'].every(
      (key) => typeof (value as Record<string, unknown>)[key] === 'string',
    )
  const normalise = (value: unknown, field = ''): unknown => {
    if (Array.isArray(value)) {
      const items = value.map((item) => normalise(item))
      // Only RDF triple collections are unordered. Preserve duplicates and every other order.
      return rdfFields.has(field) && items.every(isTriple)
        ? items.sort((a, b) => canonical(a).localeCompare(canonical(b)))
        : items
    }
    if (value !== null && typeof value === 'object')
      return Object.fromEntries(
        Object.entries(value).map(([key, item]) => [key, normalise(item, key)]),
      )
    return value
  }
  return compareComplete(normalise(expected), normalise(actual))
}

/** Evidence consistency only. Provenance/identities and real operation require independent approval. */
export function verifyManifest(input: unknown, root: string, expected: Expected): Verification {
  const issues: string[] = []
  const fail = (code: string) => {
    if (!issues.includes(code)) issues.push(code)
  }
  const parsed = manifestSchema.safeParse(input)
  if (!parsed.success)
    return {
      consistent: false,
      releaseAuthorized: false,
      mode: 'invalid',
      issues: ['MANIFEST_SCHEMA'],
    }
  const m = parsed.data
  if (!expectedSchema.safeParse(expected).success)
    return {
      consistent: false,
      releaseAuthorized: false,
      mode: m.mode,
      issues: ['EXPECTED_IDENTITY'],
    }
  const now = Date.parse(expected.now)
  if (!Number.isFinite(now)) fail('EXPECTED_IDENTITY')
  if ([m.sourceSha, m.candidateSha, m.reviewedSha].some((s) => s !== expected.candidateSha))
    fail('CANDIDATE_SHA')
  if (m.prd.sha256 !== expected.prdSha256 || m.baseline.sha256 !== expected.baselineSha256)
    fail('BASELINE_IDENTITY')
  if (m.candidateFrozenAt !== expected.candidateFrozenAt) fail('FREEZE_IDENTITY')
  const frozen = Date.parse(expected.candidateFrozenAt)
  if (frozen > now) fail('FUTURE_FREEZE')
  const read = (r: z.infer<typeof ref>, code: string, limit?: number): Buffer | undefined => {
    try {
      return readBound(root, r, limit)
    } catch {
      fail(code)
      return undefined
    }
  }
  const large = (r: z.infer<typeof ref>, code: string, mac?: boolean) => {
    try {
      return verifyLargeFile(root, r, mac)
    } catch {
      fail(code)
      return undefined
    }
  }
  const json = (r: z.infer<typeof ref>, code: string): unknown => {
    try {
      const b = read(r, code)
      return b ? JSON.parse(b.toString('utf8')) : undefined
    } catch {
      fail(code)
      return undefined
    }
  }
  const fresh = (when: string, code: string) => {
    const at = Date.parse(when)
    if (at < frozen || at > now) fail(code)
  }
  const prd = read(m.prd, 'PRD_FILE')?.toString('utf8') ?? ''
  const p0 = [...prd.matchAll(/^### (FR-\d+) .*【[^\n]*P0[^\n]*】/gm)].map((x) => x[1])
  if (p0.length !== 57 || new Set(p0).size !== p0.length) fail('PRD_SCOPE')
  const baselineSchema = z
    .object({ version: text, source: ref, files: z.record(text, sha) })
    .strict()
  const baseline = baselineSchema.safeParse(json(m.baseline, 'BASELINE_FILE'))
  let fixedCases: string[] = []
  const fixedExpected = new Map<string, unknown>()
  if (!baseline.success) fail('BASELINE_SCHEMA')
  else {
    if (
      m.mode === 'evidence' &&
      (m.baseline.path !== 'tests/fixtures/product-baselines/manifest.json' ||
        m.baseline.sha256 !== APPROVED_BASELINE.sha256 ||
        m.prd.sha256 !== APPROVED_BASELINE.prdSha256 ||
        baseline.data.version !== APPROVED_BASELINE.version ||
        !compareComplete(
          Object.keys(baseline.data.files).sort(),
          [...APPROVED_BASELINE.paths].sort(),
        ))
    )
      fail('BASELINE_APPROVED_PROFILE')
    if (baseline.data.source.sha256 !== m.prd.sha256) fail('BASELINE_PRD')
    read(baseline.data.source, 'BASELINE_SOURCE')
    for (const [path, sha256] of Object.entries(baseline.data.files))
      read({ path, sha256 }, 'BASELINE_CONTENT')
    const coveragePath = 'tests/fixtures/product-baselines/coverage.json'
    const coverageHash = baseline.data.files[coveragePath]
    const coverageSchema = z
      .object({
        sourceSha256: sha,
        entries: z.array(z.object({ id: text, source: text }).strict()).length(50),
      })
      .strict()
    const coverage = coverageHash
      ? coverageSchema.safeParse(
          json({ path: coveragePath, sha256: coverageHash }, 'COVERAGE_FILE'),
        )
      : undefined
    if (!coverage?.success) fail('COVERAGE_SCHEMA')
    else {
      fixedCases = coverage.data.entries.map((c) => c.id)
      const named = [...prd.slice(prd.indexOf('### G.1')).matchAll(/^\| ([A-Z]-\d{2}) \|/gm)].map(
        (x) => x[1],
      )
      const lists = [...prd.slice(prd.indexOf('### G.4')).split('\n')]
        .filter((l) => l.startsWith('- '))
        .map((l) => l.slice(2))
      const tableRows = new Map(
        [...prd.slice(prd.indexOf('### G.1')).matchAll(/^(\| ([A-Z]-\d{2}) \|.*)$/gm)].map((x) => [
          x[2],
          x[1],
        ]),
      )
      const sourceById = new Map([
        ...tableRows,
        ...lists.map((line, i) => [`G-list-${String(i + 1).padStart(2, '0')}`, line] as const),
      ])
      if (coverage.data.entries.some((c) => sourceById.get(c.id) !== c.source))
        fail('COVERAGE_SOURCE')
      const expectedEntries = [
        ...named,
        ...lists.map((_, i) => `G-list-${String(i + 1).padStart(2, '0')}`),
      ]
      if (
        !compareComplete([...fixedCases].sort(), expectedEntries.sort()) ||
        coverage.data.sourceSha256 !== m.prd.sha256 ||
        coverage.data.entries.some((c) => !prd.includes(c.source))
      )
        fail('COVERAGE_PRD')
    }
    const casesPath = 'tests/fixtures/product-baselines/cases.json'
    const casesHash = baseline.data.files[casesPath]
    const casesSchema = z
      .object({ fixtureVersion: text, cases: z.array(z.record(text, z.unknown())).length(50) })
      .strict()
    const cases = casesHash
      ? casesSchema.safeParse(json({ path: casesPath, sha256: casesHash }, 'CASES_FILE'))
      : undefined
    if (!cases?.success) fail('CASES_SCHEMA')
    else
      for (const c of cases.data.cases) {
        if (
          typeof c.id !== 'string' ||
          !fixedCases.includes(c.id) ||
          fixedExpected.has(c.id) ||
          !c.expected ||
          typeof c.expected !== 'object' ||
          Array.isArray(c.expected)
        ) {
          fail('CASE_IDENTITY')
          continue
        }
        const value = { ...c.expected } as Record<string, unknown>
        for (const prefix of ['', 'replay']) {
          const fileKey = prefix ? 'replayExactFile' : 'exactFile'
          const pointerKey = prefix ? 'replayExactPointer' : 'exactPointer'
          if (value[fileKey] !== undefined) {
            const name = value[fileKey],
              pointer = value[pointerKey]
            const path = `tests/fixtures/product-baselines/${name}`
            const hash = baseline.data.files[path]
            if (
              typeof name !== 'string' ||
              typeof pointer !== 'string' ||
              !pointer.startsWith('/') ||
              !hash
            ) {
              fail('CASE_POINTER')
              continue
            }
            let expanded = json({ path, sha256: hash }, 'CASE_REFERENCED_FILE')
            for (const key of pointer.slice(1).split('/')) {
              if (!expanded || typeof expanded !== 'object' || !Object.hasOwn(expanded, key)) {
                expanded = undefined
                break
              }
              expanded = (expanded as Record<string, unknown>)[key]
            }
            if (expanded === undefined) fail('CASE_POINTER')
            else value[prefix ? 'replayExact' : 'exact'] = expanded
            delete value[fileKey]
            delete value[pointerKey]
          }
        }
        fixedExpected.set(c.id, value)
      }
    for (const needed of [
      'G-base.json',
      'G-map-empty.json',
      'G-behavior.json',
      'E.5.json',
      'cases.json',
    ]) {
      if (!baseline.data.files[`tests/fixtures/product-baselines/${needed}`])
        fail('BASELINE_REQUIRED_FILE')
    }
  }
  const evidence = (r: Report, required: string[], label: string, hash?: string) => {
    if (
      r.candidateSha !== m.candidateSha ||
      r.baselineSha256 !== m.baseline.sha256 ||
      (hash !== undefined && r.artifactSha256 !== hash)
    )
      fail(`${label}_BINDING`)
    fresh(r.testedAt, `${label}_STALE`)
    read(r.raw, `${label}_RAW`)
    const ids = r.checks.map((c) => c.id)
    if (new Set(ids).size !== ids.length || required.some((id) => !ids.includes(id)))
      fail(`${label}_COVERAGE`)
    for (const c of r.checks) {
      if (expected.expectedResults[`${label}:${c.id}`] !== c.expected.sha256)
        fail(`${label}_EXPECTATION_PIN`)
      const a = json(c.expected, `${label}_EXPECTED`)
      const b = json(c.actual, `${label}_ACTUAL`)
      if (
        a === undefined ||
        b === undefined ||
        !(label === 'PRODUCT' ? compareProductComplete(a, b) : compareComplete(a, b))
      )
        fail(`${label}_RESULT`)
    }
  }
  if (new Set(m.artifacts.map((a) => a.target)).size !== 2) fail('TARGET_MATRIX')
  for (const a of m.artifacts) {
    const mac = a.target === 'macos15-arm64'
    const label = mac ? 'MAC' : 'WIN'
    const arch = mac ? 'arm64' : 'x64'
    const binary = large(a.file, `${label}_ARTIFACT`, mac)
    if (binary && !binary.format) fail(`${label}_BINARY_FORMAT`)
    if (binary && binary.size !== a.bytes) fail(`${label}_SIZE`)
    if (a.appArch !== arch || a.engineArch !== arch || a.device.arch !== arch) fail(`${label}_ARCH`)
    if (a.appVersion !== m.version) fail(`${label}_VERSION`)
    if (a.format !== (mac ? 'dmg' : 'nsis')) fail(`${label}_FORMAT`)
    if (a.build.sourceSha !== m.sourceSha) fail(`${label}_BUILD_SHA`)
    for (const r of [a.build.nodeLock, a.build.pythonLock, a.build.config])
      read(r, `${label}_BUILD_INPUT`)
    evidence(
      a.build.report,
      ['source-checkout', 'dependency-locks', 'app-engine-architecture', 'embedded-components'],
      `${label}_BUILD`,
      a.file.sha256,
    )
    if (
      !a.signature.valid ||
      !a.signature.timestamped ||
      a.signature.scheme !== (mac ? 'developer-id' : 'authenticode') ||
      /adhoc|ad.hoc|unsigned|none/i.test(a.signature.identity)
    )
      fail(`${label}_SIGNATURE`)
    if (mac && (!a.signature.hardenedRuntime || !a.signature.notarized || !a.signature.stapled))
      fail('MAC_NOTARIZATION')
    evidence(
      a.signature.report,
      mac
        ? ['codesign-deep-strict', 'nested-python-signatures', 'gatekeeper', 'stapler-validate']
        : ['signtool-pa-all', 'timestamp-chain', 'installed-executables'],
      `${label}_SIGN`,
      a.file.sha256,
    )
    const inventorySchema = z.array(z.object({ name: text, version: text }).strict()).min(1)
    const inventory = inventorySchema.safeParse(json(a.inventory, `${label}_INVENTORY`))
    const names = a.components.map((c) => `${c.name}@${c.version}`)
    if (
      !inventory.success ||
      new Set(names).size !== names.length ||
      !compareComplete(
        [...names].sort(),
        inventory.data.map((c) => `${c.name}@${c.version}`).sort(),
      )
    )
      fail(`${label}_LICENSE_COVERAGE`)
    for (const c of a.components) read(c.notice, `${label}_LICENSE_FILE`)
    const d = a.device
    if (
      d.os !== (mac ? 'macOS' : 'Windows 11') ||
      !(mac ? /^15\.\d+(?:\.\d+)?$/ : /^\d{2}H[12]$/).test(d.version) ||
      d.nodeInstalled ||
      d.pythonInstalled ||
      d.dockerRequired
    )
      fail(`${label}_CLEAN_TARGET`)
    if (!collectorStatus.safeParse(json(d.collectorStatus, `${label}_COLLECTOR_STATUS`)).success)
      fail(`${label}_COLLECTOR_INCOMPLETE`)
    const complete = d.report.checks.find((c) => c.id === 'collector-complete')
    if (!complete || complete.actual.sha256 !== d.collectorStatus.sha256)
      fail(`${label}_COLLECTOR_BINDING`)
    const samePackage = d.report.checks.find((c) => c.id === 'installed-components-match-package')
    const installedSchema = z
      .object({
        packageSha256: sha,
        inventory: ref,
        app: ref,
        engine: ref,
        method: z.enum(['installed', 'extracted']),
        provenance: ref,
      })
      .strict()
    const installed =
      samePackage && installedSchema.safeParse(json(samePackage.actual, `${label}_PACKAGE_SOURCE`))
    if (!installed || !installed.success || installed.data.packageSha256 !== a.file.sha256)
      fail(`${label}_PACKAGE_SOURCE`)
    else {
      // This binds the declared bytes, not the truth of the installation/extraction transcript.
      read(installed.data.inventory, `${label}_PACKAGE_INVENTORY`)
      read(installed.data.provenance, `${label}_PACKAGE_PROVENANCE`)
      large(installed.data.app, `${label}_INSTALLED_APP`)
      large(installed.data.engine, `${label}_INSTALLED_ENGINE`)
    }
    evidence(d.report, DEVICE_CHECKS, `${label}_DEVICE`, a.file.sha256)
    const url = new URL(a.download.url)
    if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash)
      fail(`${label}_CHANNEL_URL`)
    large(a.download.file, `${label}_DOWNLOAD`)
    if (a.download.file.sha256 !== a.file.sha256 || !a.download.installed)
      fail(`${label}_CHANNEL_HASH`)
    evidence(
      a.download.report,
      ['download-hash', 'download-install-start', 'audience-access'],
      `${label}_CHANNEL`,
      a.file.sha256,
    )
  }
  if (new Set(m.artifacts.map((a) => a.device.id)).size !== 2) fail('DISTINCT_DEVICES')
  // Product/engineering reports cover the full candidate; artifact hash must identify one actual release asset.
  const assets = new Set(m.artifacts.map((a) => a.file.sha256))
  for (const [r, label] of [
    [m.product, 'PRODUCT'],
    [m.model.report, 'MODEL'],
    [m.engineering, 'ENGINEERING'],
    [m.recovery.report, 'RECOVERY'],
  ] as const)
    if (!assets.has(r.artifactSha256)) fail(`${label}_ASSET`)
  evidence(m.product, [...p0, ...fixedCases], 'PRODUCT')
  for (const id of fixedCases) {
    const c = m.product.checks.find((c) => c.id === id)
    const baselineValue = fixedExpected.get(id)
    if (
      !c ||
      baselineValue === undefined ||
      !compareProductComplete(baselineValue, json(c.expected, 'PRODUCT_FIXED_EXPECTED'))
    )
      fail('PRODUCT_EXPECTATION_BASELINE')
  }
  evidence(m.engineering, ENGINEERING_CHECKS, 'ENGINEERING')
  evidence(m.model.report, MODEL_CHECKS, 'MODEL')
  read(m.model.evaluation, 'MODEL_EVALUATION')
  if (
    m.model.endpoint !== APPROVED_MODEL.endpoint ||
    m.model.requestedModel !== APPROVED_MODEL.requestedModel ||
    m.model.decisionSha256 !== APPROVED_MODEL.decisionSha256 ||
    expected.modelEndpoint !== APPROVED_MODEL.endpoint ||
    expected.requestedModel !== APPROVED_MODEL.requestedModel ||
    expected.modelDecisionSha256 !== APPROVED_MODEL.decisionSha256 ||
    m.model.endpoint !== expected.modelEndpoint ||
    m.model.requestedModel !== expected.requestedModel ||
    m.model.decisionSha256 !== expected.modelDecisionSha256 ||
    m.model.mode !== expected.modelMode ||
    m.model.returnedModel !== expected.returnedModel ||
    m.model.serviceVersion !== expected.serviceVersion ||
    m.model.evaluation.sha256 !== expected.evaluationSha256
  )
    fail('MODEL_PROFILE_DRIFT')
  if (m.model.fabricatedResults !== 0) fail('MODEL_FABRICATION')
  for (const provider of ['zcode', 'minimax']) {
    const r = m.reviews.find((r) => r.provider === provider)
    if (!r) {
      fail('REVIEW_PAIR')
      continue
    }
    if (
      r.model !== (provider === 'zcode' ? 'GLM-5.3' : 'M3.1-Flash') ||
      r.effort !== (provider === 'zcode' ? 'highest' : 'xhigh') ||
      r.verdict !== 'pass' ||
      r.unresolved !== 0
    )
      fail('REVIEW_VERDICT')
    if (!assets.has(r.report.artifactSha256)) fail('REVIEW_ASSET')
    evidence(
      r.report,
      ['full-scope', 'historical-findings-closed', 'same-candidate'],
      `REVIEW_${provider}`,
    )
  }
  if (new Set(m.reviews.map((r) => r.taskId)).size !== 2) fail('REVIEW_TASKS')
  let successes = 0
  if (new Set(m.users.map((u) => u.id)).size !== m.users.length) fail('USER_DUPLICATE')
  for (const u of m.users) {
    read(u.record, 'USER_RECORD')
    fresh(u.testedAt, 'USER_STALE')
    if (!u.human || u.developer || !u.ontologyNovice || !assets.has(u.artifactSha256))
      fail('USER_ELIGIBILITY')
    if (u.blockers.length) fail('USER_BLOCKER')
    if (u.coreCompleted && !u.transferCompleted) fail('USER_CORE_TRANSFER_CONTRADICTION')
    if (
      !u.agentFullCounterexample ||
      u.agentMarkedIndependent ||
      (u.transferIndependent && (!u.transferCompleted || u.assistance !== 'independent'))
    )
      fail('USER_ASSISTANCE')
    if (
      u.coreCompleted &&
      u.transferCompleted &&
      ['independent', 'product-hints'].includes(u.assistance)
    )
      successes++
  }
  if (successes / m.users.length < 0.8) fail('USER_COMPLETION_RATE')
  const snapshot = (
    r: z.infer<typeof ref>,
    code: string,
    requiredCase: z.infer<typeof comparisonCase>,
  ) => {
    const value = json(r, code)
    const parsed = comparisonSchema.safeParse(value)
    if (!parsed.success) fail(`${code}_SCHEMA`)
    else if (parsed.data.comparisonCase !== requiredCase) fail(`${code}_CASE`)
    return value
  }
  if (m.recovery.backup.sha256 !== expected.recoverySnapshotSha256) fail('RECOVERY_SOURCE_PIN')
  const before = snapshot(m.recovery.backup, 'RECOVERY_BACKUP', expected.recoveryComparisonCase)
  const after = snapshot(m.recovery.restored, 'RECOVERY_RESTORED', expected.recoveryComparisonCase)
  if (before === undefined || after === undefined || !compareComplete(before, after))
    fail('RECOVERY_DATA')
  if (new Set(m.recovery.rollbackInstallers.map((a) => a.target)).size !== 2)
    fail('ROLLBACK_TARGETS')
  for (const old of m.recovery.rollbackInstallers) {
    const pin = expected.previousAssets.find((a) => a.target === old.target)
    if (
      !pin ||
      pin.version !== old.version ||
      pin.sourceSha !== old.sourceSha ||
      pin.sha256 !== old.file.sha256 ||
      m.artifacts.some((a) => a.file.sha256 === old.file.sha256)
    )
      fail('ROLLBACK_IDENTITY_PIN')
    const binary = large(old.file, 'ROLLBACK_INSTALLER', old.target === 'macos15-arm64')
    if (binary && !binary.format) fail('ROLLBACK_BINARY_FORMAT')
    if (
      old.version === m.version ||
      old.sourceSha === m.candidateSha ||
      !old.signature.valid ||
      !old.signature.timestamped ||
      old.signature.scheme !== (old.target === 'macos15-arm64' ? 'developer-id' : 'authenticode') ||
      /adhoc|ad.hoc|unsigned|none/i.test(old.signature.identity)
    )
      fail('ROLLBACK_SIGNATURE')
    if (
      old.target === 'macos15-arm64' &&
      (!old.signature.notarized || !old.signature.stapled || !old.signature.hardenedRuntime)
    )
      fail('ROLLBACK_NOTARIZATION')
    evidence(
      old.signature.report,
      [
        'previous-source-version',
        'previous-signature',
        'rollback-format-compatible',
        'rollback-install',
        'rollback-retain-new-version-copy',
        'rollback-refuse-incompatible-format',
      ],
      `ROLLBACK_${old.target}`,
      old.file.sha256,
    )
  }
  evidence(m.recovery.report, RECOVERY_CHECKS, 'RECOVERY')
  const directions = m.migration.map((x) => `${x.from}:${x.to}`)
  if (
    !directions.includes('windows11-x64:macos15-arm64') ||
    !directions.includes('macos15-arm64:windows11-x64')
  )
    fail('MIGRATION_DIRECTIONS')
  for (const x of m.migration) {
    if (x.before.sha256 !== expected.migrationSnapshotSha256[x.from]) fail('MIGRATION_SOURCE_PIN')
    const a = snapshot(x.before, 'MIGRATION_BEFORE', expected.migrationComparisonCases[x.from])
    const b = snapshot(x.after, 'MIGRATION_AFTER', expected.migrationComparisonCases[x.from])
    if (a === undefined || b === undefined || !compareComplete(a, b)) fail('MIGRATION_DATA')
    const dest = m.artifacts.find((a) => a.target === x.to)
    if (!dest) {
      fail('MIGRATION_DESTINATION')
      continue
    }
    evidence(x.report, MIGRATION_CHECKS, `MIGRATION_${x.from}_${x.to}`, dest.file.sha256)
  }
  return { consistent: issues.length === 0, releaseAuthorized: false, mode: m.mode, issues }
}
