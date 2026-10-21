import { createHash } from 'node:crypto'
import { closeSync, openSync, readFileSync, readSync, realpathSync, statSync } from 'node:fs'
import { isAbsolute, relative, resolve, sep } from 'node:path'
import { z } from 'zod'

const text = z.string().trim().min(1).max(512)
const sha = z.string().regex(/^[a-f0-9]{64}$/)
const commit = z.string().regex(/^[a-f0-9]{40}$/)
const date = z.iso.datetime({ offset: true })
const ref = z.object({ path: text, sha256: sha }).strict()
const target = z.enum(['windows11-x64', 'macos15-arm64'])
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
        endpoint: z.literal('https://api.deepseek.com/chat/completions'),
        requestedModel: z.literal('deepseek-v4-pro'),
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
    modelMode: z.enum(['thinking', 'non-thinking']),
    evaluationSha256: sha,
    returnedModel: text,
    serviceVersion: text,
    recoverySnapshotSha256: sha,
    migrationSnapshotSha256: z.object({ 'windows11-x64': sha, 'macos15-arm64': sha }).strict(),
    previousAssets: z
      .array(z.object({ target, version: text, sourceSha: commit, sha256: sha }).strict())
      .length(2),
    expectedResults: z.record(text, sha),
    now: date,
  })
  .strict()
export type Expected = z.infer<typeof expectedSchema>
export const DEVICE_CHECKS = [
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
]
export const digest = (value: Uint8Array | string) =>
  createHash('sha256').update(value).digest('hex')

// Bound every read to a regular, nonempty file within the supplied evidence root.
function boundPath(root: string, file: z.infer<typeof ref>, limit: number): string {
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
  const info = statSync(path)
  if (!info.isFile() || info.size === 0 || info.size > limit) throw new Error('FILE_BOUNDS')
  return path
}
export function readBound(
  root: string,
  file: z.infer<typeof ref>,
  limit = 16 * 1024 * 1024,
): Buffer {
  const bytes = readFileSync(boundPath(root, file, limit))
  if (digest(bytes) !== file.sha256) throw new Error('FILE_HASH')
  return bytes
}
function verifyLargeFile(root: string, file: z.infer<typeof ref>): number {
  const path = boundPath(root, file, 8 * 1024 ** 3)
  const fd = openSync(path, 'r')
  const hash = createHash('sha256')
  let size = 0
  try {
    const buffer = Buffer.alloc(1024 * 1024)
    let length: number
    while ((length = readSync(fd, buffer)) > 0) {
      hash.update(buffer.subarray(0, length))
      size += length
      if (size > 8 * 1024 ** 3) throw new Error('FILE_BOUNDS')
    }
    if (hash.digest('hex') !== file.sha256) throw new Error('FILE_HASH')
    return size
  } finally {
    closeSync(fd)
  }
}

function installerFormat(root: string, file: z.infer<typeof ref>, mac: boolean): boolean {
  const path = boundPath(root, file, 8 * 1024 ** 3)
  const fd = openSync(path, 'r')
  try {
    const size = statSync(path).size
    const head = Buffer.alloc(64)
    if (mac) {
      return (
        size >= 512 &&
        readSync(fd, head, 0, 4, size - 512) === 4 &&
        head.subarray(0, 4).toString() === 'koly'
      )
    }
    if (readSync(fd, head, 0, 64, 0) !== 64 || head.readUInt16LE(0) !== 0x5a4d) return false
    const offset = head.readUInt32LE(0x3c)
    return (
      offset <= size - 6 &&
      readSync(fd, head, 0, 6, offset) === 6 &&
      head.readUInt32LE(0) === 0x4550 &&
      [0x14c, 0x8664].includes(head.readUInt16LE(4))
    )
  } finally {
    closeSync(fd)
  }
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
  if (!expectedSchema.safeParse(expected).success || !Number.isFinite(now))
    fail('EXPECTED_IDENTITY')
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
  const large = (r: z.infer<typeof ref>, code: string) => {
    try {
      return verifyLargeFile(root, r)
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
      if (a === undefined || b === undefined || !compareComplete(a, b)) fail(`${label}_RESULT`)
    }
  }
  if (new Set(m.artifacts.map((a) => a.target)).size !== 2) fail('TARGET_MATRIX')
  for (const a of m.artifacts) {
    const mac = a.target === 'macos15-arm64'
    const label = mac ? 'MAC' : 'WIN'
    const arch = mac ? 'arm64' : 'x64'
    const bytes = large(a.file, `${label}_ARTIFACT`)
    try {
      if (!installerFormat(root, a.file, mac)) fail(`${label}_BINARY_FORMAT`)
    } catch {
      fail(`${label}_BINARY_FORMAT`)
    }
    if (bytes !== undefined && bytes !== a.bytes) fail(`${label}_SIZE`)
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
      !compareComplete(baselineValue, json(c.expected, 'PRODUCT_FIXED_EXPECTED'))
    )
      fail('PRODUCT_EXPECTATION_BASELINE')
  }
  evidence(m.engineering, ENGINEERING_CHECKS, 'ENGINEERING')
  evidence(m.model.report, MODEL_CHECKS, 'MODEL')
  read(m.model.evaluation, 'MODEL_EVALUATION')
  if (
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
    if (
      !u.agentFullCounterexample ||
      u.agentMarkedIndependent ||
      (u.transferIndependent &&
        (!u.transferCompleted || !['independent', 'product-hints'].includes(u.assistance)))
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
    .min(1)
    .refine((items) => new Set(items.map((item) => item.id)).size === items.length)
  const snapshotSchema = z
    .object({
      format: z.literal('t11-comparison-v1'),
      projectId: text,
      sourceSnapshotId: sha,
      projectRevision: z.number().int().nonnegative(),
      facts: rows,
      definitions: rows,
      ownership: rows,
      mappingState: rows,
      queries: rows,
      results: rows,
      history: rows,
      rounds: rows,
      undo: rows,
      executionVersions: z.object({ semantics: text, engine: text, lock: text }).strict(),
    })
    .strict()
  const snapshot = (r: z.infer<typeof ref>, code: string) => {
    const value = json(r, code)
    if (!snapshotSchema.safeParse(value).success) fail(`${code}_SCHEMA`)
    return value
  }
  if (m.recovery.backup.sha256 !== expected.recoverySnapshotSha256) fail('RECOVERY_SOURCE_PIN')
  const before = snapshot(m.recovery.backup, 'RECOVERY_BACKUP')
  const after = snapshot(m.recovery.restored, 'RECOVERY_RESTORED')
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
    large(old.file, 'ROLLBACK_INSTALLER')
    try {
      if (!installerFormat(root, old.file, old.target === 'macos15-arm64'))
        fail('ROLLBACK_BINARY_FORMAT')
    } catch {
      fail('ROLLBACK_BINARY_FORMAT')
    }
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
    const a = snapshot(x.before, 'MIGRATION_BEFORE')
    const b = snapshot(x.after, 'MIGRATION_AFTER')
    if (a === undefined || b === undefined || !compareComplete(a, b)) fail('MIGRATION_DATA')
    const dest = m.artifacts.find((a) => a.target === x.to)
    evidence(x.report, MIGRATION_CHECKS, `MIGRATION_${x.from}_${x.to}`, dest?.file.sha256)
  }
  return { consistent: issues.length === 0, releaseAuthorized: false, mode: m.mode, issues }
}
