import { afterEach, describe, expect, it } from 'vitest'
import {
  mkdirSync,
  statSync,
  truncateSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { spawnSync } from 'node:child_process'
import {
  APPROVED_BASELINE,
  APPROVED_MODEL,
  compareComplete,
  compareProductComplete,
  comparisonSchema,
  DEVICE_CHECKS,
  digest,
  ENGINEERING_CHECKS,
  MIGRATION_CHECKS,
  MODEL_CHECKS,
  RECOVERY_CHECKS,
  verifyManifest,
  type Manifest,
  type Expected,
  type Report,
} from '../../scripts/release/verify.mjs'

const profile = JSON.parse(readFileSync('tests/fixtures/release/synthetic-profile.json', 'utf8'))
const roots: string[] = []
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})

function fixture(
  options: {
    exactPointer?: string
    replayPointer?: string
    fixedBaseline?: boolean
    packageProfile?:
      'current-only' | 'without-originals' | 'incomplete-replay' | 'zero-commit-replay'
  } = {},
) {
  const root = mkdtempSync(join(tmpdir(), 't11-release-'))
  roots.push(root)
  let n = 0
  const put = (value: unknown, path = `evidence/${++n}.json`) => {
    const content =
      typeof value === 'string' || Buffer.isBuffer(value) ? value : JSON.stringify(value)
    mkdirSync(dirname(join(root, path)), { recursive: true })
    writeFileSync(join(root, path), content)
    return { path, sha256: digest(content) }
  }
  const prdText = readFileSync('docs/prd/PRD-本体学习与落地Agent工作台.md', 'utf8')
  const prd = put(prdText, 'docs/prd/PRD-本体学习与落地Agent工作台.md')
  const p0 = [...prdText.matchAll(/^### (FR-\d+) .*【[^\n]*P0[^\n]*】/gm)].map((x) => x[1])
  const named = [
    ...prdText.slice(prdText.indexOf('### G.1')).matchAll(/^(\| ([A-Z]-\d{2}) \|.*)$/gm),
  ].map((x) => ({ id: x[2], source: x[1] }))
  const lists = prdText
    .slice(prdText.indexOf('### G.4'))
    .split('\n')
    .filter((l) => l.startsWith('- '))
    .map((l, i) => ({ id: `G-list-${String(i + 1).padStart(2, '0')}`, source: l.slice(2) }))
  const entries = [...named, ...lists]
  const coverage = put(
    { sourceSha256: prd.sha256, entries },
    'tests/fixtures/product-baselines/coverage.json',
  )
  const files: Record<string, string> = { [coverage.path]: coverage.sha256 }
  for (const name of ['G-base.json', 'G-map-empty.json', 'G-behavior.json', 'E.5.json']) {
    const r = put({ synthetic: true, name }, `tests/fixtures/product-baselines/${name}`)
    files[r.path] = r.sha256
  }
  // Synthetic pointer-shaped data exercises the T09 reference contract without duplicating its baseline.
  const exactRounds = {
    3: [
      {
        round: 1,
        created: ['SYN-W001', 'SYN-W002'],
        completed: ['SYN-W001'],
        backlog: ['SYN-W002'],
      },
    ],
    4: [
      {
        round: 1,
        created: ['SYN-W001', 'SYN-W002'],
        completed: ['SYN-W001', 'SYN-W002'],
        backlog: [],
      },
    ],
  }
  const roundsFile = put({ expected: exactRounds }, 'tests/fixtures/product-baselines/E.5.json')
  files[roundsFile.path] = roundsFile.sha256
  const pointerCases: Record<string, Record<string, unknown>> = {
    'G-list-01': {
      exactFile: 'E.5.json',
      exactPointer: options.exactPointer ?? '/expected',
      compareAllRoundFields: true,
    },
    'G-list-02': { exactFile: 'E.5.json', exactPointer: '/expected/3', crossPhaseConflict: false },
    'G-list-06': {
      replayExactFile: 'E.5.json',
      replayExactPointer: options.replayPointer ?? '/expected/3',
      duplicateOrders: [],
    },
  }
  const expandedCases: Record<string, Record<string, unknown>> = {
    'G-list-01': { exact: exactRounds, compareAllRoundFields: true },
    'G-list-02': { exact: exactRounds[3], crossPhaseConflict: false },
    'G-list-06': { replayExact: exactRounds[3], duplicateOrders: [] },
  }
  const cases = put(
    {
      fixtureVersion: 'synthetic-regression-only',
      cases: entries.map((c) => ({
        ...c,
        expected: pointerCases[c.id] ?? { id: c.id, objects: ['A01'] },
      })),
    },
    'tests/fixtures/product-baselines/cases.json',
  )
  files[cases.path] = cases.sha256
  let baseline = put(
    { version: 'synthetic-regression-only', source: prd, files },
    'tests/fixtures/product-baselines/manifest.json',
  )
  const importedExpected = new Map<string, Record<string, unknown>>()
  if (options.fixedBaseline) {
    // Always-on probe of the committed production corpus: the exact bytes on disk (no
    // .git access) must satisfy the pinned manifest hash, PRD hash and 18-file profile,
    // so the whole suite also passes in a .git-free git-archive container.
    const manifestPath = 'tests/fixtures/product-baselines/manifest.json'
    const bytes = readFileSync(manifestPath)
    expect(digest(bytes)).toBe(APPROVED_BASELINE.sha256)
    const fixed = JSON.parse(bytes.toString('utf8'))
    expect(fixed.source.sha256).toBe(APPROVED_BASELINE.prdSha256)
    const source = readFileSync(fixed.source.path)
    expect(digest(source)).toBe(APPROVED_BASELINE.prdSha256)
    put(source, fixed.source.path)
    expect(Object.keys(fixed.files)).toHaveLength(18)
    expect(Object.keys(fixed.files).sort()).toEqual([...APPROVED_BASELINE.paths].sort())
    for (const [path, hash] of Object.entries(fixed.files)) {
      expect(path.startsWith('/')).toBe(false)
      expect(path.split('/')).not.toContain('..')
      const content = readFileSync(path)
      expect(digest(content)).toBe(hash)
      put(content, path)
    }
    baseline = put(bytes, manifestPath)
    const fixedCases = JSON.parse(
      readFileSync(join(root, 'tests/fixtures/product-baselines/cases.json'), 'utf8'),
    )
    const fixedE5 = JSON.parse(
      readFileSync(join(root, 'tests/fixtures/product-baselines/E.5.json'), 'utf8'),
    )
    for (const c of fixedCases.cases) {
      const value = { ...c.expected }
      for (const prefix of ['', 'replay']) {
        const fileKey = prefix ? 'replayExactFile' : 'exactFile'
        const pointerKey = prefix ? 'replayExactPointer' : 'exactPointer'
        if (value[fileKey] !== undefined) {
          const path = `tests/fixtures/product-baselines/${value[fileKey]}`
          let expanded: unknown = JSON.parse(readFileSync(join(root, path), 'utf8'))
          for (const key of value[pointerKey].slice(1).split('/'))
            expanded = (expanded as Record<string, unknown> | undefined)?.[key]
          value[prefix ? 'replayExact' : 'exact'] = expanded
          delete value[fileKey]
          delete value[pointerKey]
        }
      }
      importedExpected.set(c.id, value)
    }
    expect(importedExpected.get('G-list-01')).toEqual({
      exact: fixedE5.expected,
      compareAllRoundFields: true,
    })
    expect(importedExpected.get('G-list-02')).toEqual({
      exact: fixedE5.expected['3'],
      crossPhaseConflict: false,
    })
    expect(importedExpected.get('G-list-06')).toMatchObject({
      replayExact: fixedE5.expected['3'],
      duplicateOrders: [],
    })
  }
  const expected: Expected = {
    candidateSha: profile.candidateSha,
    prdSha256: prd.sha256,
    baselineSha256: baseline.sha256,
    expectedResults: {},
    recoverySnapshotSha256: '0'.repeat(64),
    recoveryComparisonCase: 'g6-conflict',
    migrationComparisonCases: { 'windows11-x64': 'g6-conflict', 'macos15-arm64': 'g6-conflict' },
    migrationSnapshotSha256: { 'windows11-x64': '0'.repeat(64), 'macos15-arm64': '0'.repeat(64) },
    previousAssets: [],
    now: profile.now,
    candidateFrozenAt: profile.frozenAt,
    modelEndpoint: APPROVED_MODEL.endpoint,
    requestedModel: APPROVED_MODEL.requestedModel,
    modelDecisionSha256: APPROVED_MODEL.decisionSha256,
    modelMode: 'thinking' as const,
    evaluationSha256: '',
    returnedModel: 'synthetic-model',
    serviceVersion: 'synthetic-1',
  }
  const result = put({ ids: ['A01'], status: 'complete', provenance: ['synthetic-input'] })
  const raw = put('Synthetic command transcript; not a native/platform/signing result')
  expected.evaluationSha256 = raw.sha256
  const report = (ids: string[], artifactSha256: string): Report => ({
    candidateSha: profile.candidateSha,
    baselineSha256: baseline.sha256,
    artifactSha256,
    testedAt: profile.testedAt,
    operator: 'synthetic-runner',
    environment: 'synthetic-only',
    raw,
    checks: ids.map((id) => ({ id, expected: result, actual: result })),
  })
  const artifacts = (['windows11-x64', 'macos15-arm64'] as const).map((target) => {
    const mac = target === 'macos15-arm64'
    const binary = Buffer.alloc(512)
    if (mac) binary.write('koly', 0)
    else {
      binary.writeUInt16LE(0x5a4d, 0)
      binary.writeUInt32LE(64, 0x3c)
      binary.writeUInt32LE(0x4550, 64)
      binary.writeUInt16LE(0x14c, 68)
    }
    binary.write(`synthetic-${target}`, 128)
    const file = put(binary)

    const r = (ids: string[]) => report(ids, file.sha256)
    const collectorStatus = put({
      schemaVersion: 1,
      status: 'complete',
      step: 'complete',
      exitCode: 0,
    })
    const packageSource = put({
      packageSha256: file.sha256,
      inventory: raw,
      app: raw,
      engine: raw,
      method: 'extracted',
      provenance: raw,
    })
    const deviceReport = r(DEVICE_CHECKS)
    for (const c of deviceReport.checks) {
      if (c.id === 'collector-complete') c.expected = c.actual = collectorStatus
      if (c.id === 'installed-components-match-package') c.expected = c.actual = packageSource
    }
    return {
      target,
      appVersion: profile.version,
      format: mac ? 'dmg' : 'nsis',
      file,
      bytes: statSync(join(root, file.path)).size,
      appArch: mac ? 'arm64' : 'x64',
      engineArch: mac ? 'arm64' : 'x64',
      build: {
        sourceSha: profile.candidateSha,
        nodeLock: raw,
        pythonLock: raw,
        config: raw,
        report: r([
          'source-checkout',
          'dependency-locks',
          'app-engine-architecture',
          'embedded-components',
        ]),
      },
      signature: {
        scheme: mac ? 'developer-id' : 'authenticode',
        identity: 'SYNTHETIC-CERTIFICATE',
        valid: true,
        timestamped: true,
        hardenedRuntime: mac,
        notarized: mac,
        stapled: mac,
        report: r(
          mac
            ? ['codesign-deep-strict', 'nested-python-signatures', 'gatekeeper', 'stapler-validate']
            : ['signtool-pa-all', 'timestamp-chain', 'installed-executables'],
        ),
      },
      components: [{ name: 'synthetic-component', version: '1.0.0', license: 'MIT', notice: raw }],
      inventory: put([{ name: 'synthetic-component', version: '1.0.0' }]),
      device: {
        id: `synthetic-${target}`,
        os: mac ? 'macOS' : 'Windows 11',
        version: mac ? '15.7' : '25H2',
        build: 'synthetic-build',
        cpu: 'synthetic-cpu',
        ramGiB: 16,
        arch: mac ? 'arm64' : 'x64',
        cleanImage: 'synthetic-image',
        isolatedSession: 'synthetic-session',
        nodeInstalled: false,
        pythonInstalled: false,
        dockerRequired: false,
        collectorStatus,
        report: deviceReport,
      },
      download: {
        url: `https://example.invalid/${target}`,
        audience: 'synthetic',
        file,
        installed: true,
        report: r(['download-hash', 'download-install-start', 'audience-access']),
      },
    }
  }) as Manifest['artifacts']
  const asset = artifacts[0].file.sha256
  const comparison = JSON.parse(readFileSync('tests/fixtures/release/comparison.json', 'utf8'))
  if (options.packageProfile === 'current-only') {
    comparison.selection = {
      currentDerived: false,
      historicalRuns: false,
      rawSources: false,
      agentSessions: false,
      priorUndo: false,
    }
    comparison.derivedResults = []
    comparison.history = []
    comparison.rounds = []
    comparison.rawSources = []
    comparison.agentSessions = []
    comparison.undo = []
    comparison.dependencies = {
      mappingSources: 'missing',
      replayInputs: false,
      replayConfiguration: false,
      replaySemantics: 'missing',
    }
    comparison.capabilities = {
      restoreCurrent: true,
      rerunOriginalMapping: false,
      replaySandbox: false,
    }
  } else if (options.packageProfile === 'without-originals') {
    comparison.selection.rawSources = false
    comparison.rawSources = []
    comparison.dependencies.mappingSources = 'missing'
    comparison.capabilities.rerunOriginalMapping = false
  } else if (options.packageProfile === 'incomplete-replay') {
    comparison.dependencies.replayInputs = false
    comparison.capabilities.replaySandbox = false
  } else if (options.packageProfile === 'zero-commit-replay') {
    comparison.rounds = []
  }
  const snapshot = put(comparison)
  const m: Manifest = {
    schemaVersion: 1,
    mode: 'synthetic',
    version: profile.version,
    sourceSha: profile.candidateSha,
    candidateSha: profile.candidateSha,
    reviewedSha: profile.candidateSha,
    candidateFrozenAt: profile.frozenAt,
    prd,
    baseline,
    artifacts,
    product: {
      ...report([...p0, ...entries.map((e) => e.id)], asset),
      checks: [...p0, ...entries.map((e) => e.id)].map((id) => {
        const value = put(
          importedExpected.get(id) ??
            expandedCases[id] ??
            (entries.some((c) => c.id === id)
              ? { id, objects: ['A01'] }
              : { requirement: id, objects: ['A01'] }),
        )
        return { id, expected: value, actual: value }
      }),
    },
    model: {
      endpoint: APPROVED_MODEL.endpoint,
      decisionSha256: APPROVED_MODEL.decisionSha256,
      requestedModel: 'deepseek-v4-pro',
      returnedModel: 'synthetic-model',
      serviceVersion: 'synthetic-1',
      mode: 'thinking',
      evaluation: raw,
      fabricatedResults: 0,
      report: report(MODEL_CHECKS, asset),
    },
    users: Array.from({ length: 5 }, (_, i) => ({
      id: `SYNTHETIC-P0${i + 1}`,
      human: true,
      developer: false,
      ontologyNovice: true,
      artifactSha256: asset,
      testedAt: profile.testedAt,
      record: raw,
      assistance: 'independent',
      coreCompleted: i < 4,
      transferCompleted: true,
      transferIndependent: true,
      agentFullCounterexample: true,
      agentMarkedIndependent: false,
      blockers: [],
    })),
    reviews: [
      {
        provider: 'zcode',
        model: 'GLM-5.3',
        effort: 'highest',
        taskId: 'synthetic-zcode',
        verdict: 'pass',
        unresolved: 0,
        report: report(['full-scope', 'historical-findings-closed', 'same-candidate'], asset),
      },
      {
        provider: 'minimax',
        model: 'M3.1-Flash',
        effort: 'xhigh',
        taskId: 'synthetic-minimax',
        verdict: 'pass',
        unresolved: 0,
        report: report(['full-scope', 'historical-findings-closed', 'same-candidate'], asset),
      },
    ],
    engineering: report(ENGINEERING_CHECKS, asset),
    recovery: {
      backup: snapshot,
      restored: snapshot,
      rollbackInstallers: artifacts.map((a) => {
        const oldBytes = Buffer.from(readFileSync(join(root, a.file.path)))
        oldBytes.write('previous-version', 200)
        const oldFile = put(oldBytes)
        return {
          target: a.target,
          version: '0.0.9',
          sourceSha: '9'.repeat(40),
          file: oldFile,
          signature: {
            ...a.signature,
            report: report(
              [
                'previous-source-version',
                'previous-signature',
                'rollback-format-compatible',
                'rollback-install',
                'rollback-retain-new-version-copy',
                'rollback-refuse-incompatible-format',
              ],
              oldFile.sha256,
            ),
          },
        }
      }),
      report: report(RECOVERY_CHECKS, asset),
    },
    migration: [
      {
        from: 'windows11-x64',
        to: 'macos15-arm64',
        before: snapshot,
        after: snapshot,
        report: report(MIGRATION_CHECKS, artifacts[1].file.sha256),
      },
      {
        from: 'macos15-arm64',
        to: 'windows11-x64',
        before: snapshot,
        after: snapshot,
        report: report(MIGRATION_CHECKS, asset),
      },
    ],
  }
  expected.recoverySnapshotSha256 = snapshot.sha256
  expected.migrationSnapshotSha256 = {
    'windows11-x64': snapshot.sha256,
    'macos15-arm64': snapshot.sha256,
  }
  expected.previousAssets = m.recovery.rollbackInstallers.map((a) => ({
    target: a.target,
    version: a.version,
    sourceSha: a.sourceSha,
    sha256: a.file.sha256,
  }))
  const pin = (r: Report, label: string) => {
    for (const c of r.checks) expected.expectedResults[`${label}:${c.id}`] = c.expected.sha256
  }
  for (const a of artifacts) {
    const label = a.target === 'macos15-arm64' ? 'MAC' : 'WIN'
    pin(a.build.report, `${label}_BUILD`)
    pin(a.signature.report, `${label}_SIGN`)
    pin(a.device.report, `${label}_DEVICE`)
    pin(a.download.report, `${label}_CHANNEL`)
  }
  pin(m.product, 'PRODUCT')
  pin(m.engineering, 'ENGINEERING')
  pin(m.model.report, 'MODEL')
  pin(m.recovery.report, 'RECOVERY')
  for (const r of m.reviews) pin(r.report, `REVIEW_${r.provider}`)
  for (const a of m.recovery.rollbackInstallers) pin(a.signature.report, `ROLLBACK_${a.target}`)
  for (const x of m.migration) pin(x.report, `MIGRATION_${x.from}_${x.to}`)
  return { root, m, expected, put }
}

describe('T11 evidence consistency (all fixtures are synthetic)', () => {
  it('compares RDF facts as a full multiset, preserving values and duplicate multiplicity', () => {
    const a = { subject: 'urn:a', predicate: 'urn:p', object: '"A"' }
    const b = { subject: 'urn:b', predicate: 'urn:p', object: '"B"' }
    expect(compareProductComplete({ facts: [a, b] }, { facts: [b, a] })).toBe(true)
    expect(compareProductComplete({ facts: [a, b] }, { facts: [a, a] })).toBe(false)
    expect(compareProductComplete({ facts: [a, a] }, { facts: [a] })).toBe(false)
  })
  it('preserves event, action and round order even when nested beside unordered facts', () => {
    const before = { facts: [], events: ['E1', 'E2'], trace: ['X', 'Y'], rounds: [1, 2] }
    for (const field of ['events', 'trace', 'rounds'] as const) {
      const after = structuredClone(before)
      after[field].reverse()
      expect(compareProductComplete(before, after)).toBe(false)
    }
  })
  it('loads all committed fixed baseline bytes and fully resolves their expected pointers', () => {
    const { root, m, expected } = fixture({ fixedBaseline: true })
    expect(m.baseline.sha256).toBe(APPROVED_BASELINE.sha256)
    expect(verifyManifest(m, root, expected)).toEqual({
      consistent: true,
      releaseAuthorized: false,
      mode: 'synthetic',
      issues: [],
    })
  })
  it('accepts reordered RDF facts in a synthetic payload shaped by the fixed E.5 oracle', () => {
    const { root, m, expected, put } = fixture({ fixedBaseline: true })
    const result = m.product.checks.find((c) => c.id === 'G-list-02')!
    const actual = JSON.parse(readFileSync(join(root, result.actual.path), 'utf8'))
    expect(actual.exact).toHaveLength(4)
    actual.exact[0].facts.reverse()
    result.actual = put(actual)
    expect(verifyManifest(m, root, expected).consistent).toBe(true)
  })
  it('rejects reversed actual round order against the approved complete E.5 output', () => {
    const { root, m, expected, put } = fixture({ fixedBaseline: true })
    const result = m.product.checks.find((c) => c.id === 'G-list-02')!
    const actual = JSON.parse(readFileSync(join(root, result.actual.path), 'utf8'))
    actual.exact.reverse()
    result.actual = put(actual)
    expect(verifyManifest(m, root, expected).issues).toContain('PRODUCT_RESULT')
  })
  it('checks the complete positive fixture without granting release authority', () => {
    const { root, m, expected } = fixture()
    expect(verifyManifest(m, root, expected)).toEqual({
      consistent: true,
      releaseAuthorized: false,
      mode: 'synthetic',
      issues: [],
    })
  })
  it.each([
    'current-only',
    'without-originals',
    'incomplete-replay',
    'zero-commit-replay',
  ] as const)(
    'accepts a restorable selected package independently of rerun/replay: %s',
    (packageProfile) => {
      const { root, m, expected } = fixture({ packageProfile })
      expect(verifyManifest(m, root, expected)).toEqual({
        consistent: true,
        releaseAuthorized: false,
        mode: 'synthetic',
        issues: [],
      })
    },
  )
  it.each(['history', 'rounds', 'derivedResults', 'rawSources', 'agentSessions', 'undo'] as const)(
    'rejects carrying unselected content: %s',
    (section) => {
      const { root, m, expected, put } = fixture({ packageProfile: 'current-only' })
      const after = JSON.parse(readFileSync(join(root, m.migration[0].after.path), 'utf8'))
      after[section] = [{ id: 'unselected-row', payload: { content: 'synthetic' } }]
      m.migration[0].after = put(after)
      expect(verifyManifest(m, root, expected).issues).toContain('MIGRATION_AFTER_SCHEMA')
    },
  )
  it.each(['rerunOriginalMapping', 'replaySandbox'] as const)(
    'rejects an unsupported migration capability: %s',
    (capability) => {
      const { root, m, expected, put } = fixture({ packageProfile: 'current-only' })
      const after = JSON.parse(readFileSync(join(root, m.migration[0].after.path), 'utf8'))
      after.capabilities[capability] = true
      m.migration[0].after = put(after)
      expect(verifyManifest(m, root, expected).issues).toContain('MIGRATION_AFTER_SCHEMA')
    },
  )
  it('still rejects a missing mandatory source/ownership layer in a current-only package', () => {
    const { root, m, expected, put } = fixture({ packageProfile: 'current-only' })
    const after = JSON.parse(readFileSync(join(root, m.migration[0].after.path), 'utf8'))
    after.ownership = []
    m.migration[0].after = put(after)
    const result = verifyManifest(m, root, expected)
    expect(result.issues).toContain('MIGRATION_AFTER_SCHEMA')
    expect(result.issues).toContain('MIGRATION_DATA')
  })
  it('rejects an old comparison format instead of silently upgrading its meaning', () => {
    const { root, m, expected, put } = fixture()
    const after = JSON.parse(readFileSync(join(root, m.recovery.restored.path), 'utf8'))
    after.format = 't11-comparison-v1'
    m.recovery.restored = put(after)
    expect(verifyManifest(m, root, expected).issues).toContain('RECOVERY_RESTORED_SCHEMA')
  })
  it('requires the actual no-history restoration case in each migration direction', () => {
    const { root, m, expected } = fixture()
    m.migration[0].report.checks = m.migration[0].report.checks.filter(
      (c) => c.id !== 'restore-current-without-history',
    )
    const result = verifyManifest(m, root, expected)
    expect(result.consistent).toBe(false)
    expect(result.issues).toContain('MIGRATION_windows11-x64_macos15-arm64_COVERAGE')
  })
  it.each([{ exactPointer: '/expected/not-present' }, { replayPointer: '/expected/3/99' }])(
    'rejects unresolved fixed-baseline references %j',
    (options) => {
      const { root, m, expected } = fixture(options)
      const result = verifyManifest(m, root, expected)
      expect(result.consistent).toBe(false)
      expect(result.issues).toContain('CASE_POINTER')
      expect(result.issues).toContain('PRODUCT_EXPECTATION_BASELINE')
    },
  )
  it('rejects referenced file drift even when the direct expected/actual pair is unchanged', () => {
    const { root, m, expected } = fixture()
    writeFileSync(
      join(root, 'tests/fixtures/product-baselines/E.5.json'),
      JSON.stringify({ expected: {} }),
    )
    const result = verifyManifest(m, root, expected)
    expect(result.consistent).toBe(false)
    expect(result.issues).toContain('BASELINE_CONTENT')
    expect(result.issues).toContain('CASE_REFERENCED_FILE')
  })
  it('rejects a wrong completed object in an expanded replay result', () => {
    const { root, m, expected, put } = fixture()
    const replay = m.product.checks.find((c) => c.id === 'G-list-06')!
    const actual = JSON.parse(readFileSync(join(root, replay.actual.path), 'utf8'))
    actual.replayExact[0].completed = ['SYN-W002']
    replay.actual = put(actual)
    const result = verifyManifest(m, root, expected)
    expect(result.consistent).toBe(false)
    expect(result.issues).toContain('PRODUCT_RESULT')
  })
  it('permits empty generic query/definition layers while retaining carried facts and ownership', () => {
    const { root, m, expected, put } = fixture()
    const current = JSON.parse(readFileSync(join(root, m.recovery.backup.path), 'utf8'))
    current.comparisonCase = 'current-state'
    for (const field of ['definitions', 'mappingState', 'queries', 'results']) current[field] = []
    m.recovery.backup = m.recovery.restored = put(current)
    expected.recoverySnapshotSha256 = m.recovery.backup.sha256
    expected.recoveryComparisonCase = 'current-state'
    expect(verifyManifest(m, root, expected).issues).toEqual([])
  })
  it.each(['facts', 'ownership'])(
    'refuses a template as current recovery even with both pins updated: %s',
    (field) => {
      const { root, m, expected, put } = fixture()
      const current = JSON.parse(readFileSync(join(root, m.recovery.backup.path), 'utf8'))
      current.comparisonCase = 'current-state'
      current[field] = []
      m.recovery.backup = m.recovery.restored = put(current)
      expected.recoverySnapshotSha256 = m.recovery.backup.sha256
      expected.recoveryComparisonCase = 'current-state'
      expect(verifyManifest(m, root, expected).issues).toContain('RECOVERY_BACKUP_SCHEMA')
    },
  )
  it.each(['facts', 'definitions', 'ownership', 'mappingState', 'queries', 'results'])(
    'keeps every G.6 layer nonempty in both directions: %s',
    (field) => {
      const { root, m, expected, put } = fixture()
      for (const x of m.migration) {
        const current = JSON.parse(readFileSync(join(root, x.before.path), 'utf8'))
        current[field] = []
        x.before = x.after = put(current)
        expected.migrationSnapshotSha256[x.from] = x.before.sha256
      }
      const issues = verifyManifest(m, root, expected).issues
      expect(issues).toContain('MIGRATION_BEFORE_SCHEMA')
      expect(issues).toContain('MIGRATION_AFTER_SCHEMA')
    },
  )
  it('rejects migration case downgrade even if source snapshots and both case pins are changed', () => {
    const { root, m, expected, put } = fixture()
    const current = JSON.parse(readFileSync(join(root, m.migration[0].before.path), 'utf8'))
    current.comparisonCase = 'current-state'
    m.migration[0].before = m.migration[0].after = put(current)
    expected.migrationSnapshotSha256['windows11-x64'] = m.migration[0].before.sha256
    expect(verifyManifest(m, root, expected).issues).toContain('MIGRATION_BEFORE_CASE')
    const badFreeze = structuredClone(expected) as unknown as {
      migrationComparisonCases: Record<string, string>
    }
    badFreeze.migrationComparisonCases['windows11-x64'] = 'current-state'
    expect(verifyManifest(m, root, badFreeze as unknown as Expected).issues).toEqual([
      'EXPECTED_IDENTITY',
    ])
  })
  it.each(['t11-comparison-v2', 't11-comparison-v1'])(
    'does not convert historical comparison format %s',
    (format) => {
      const { root, m, expected, put } = fixture()
      const current = JSON.parse(readFileSync(join(root, m.recovery.backup.path), 'utf8'))
      current.format = format
      m.recovery.restored = put(current)
      expect(verifyManifest(m, root, expected).issues).toContain('RECOVERY_RESTORED_SCHEMA')
    },
  )
  it('rejects an approved-case drift between before and after even when payload is otherwise equal', () => {
    const { root, m, expected, put } = fixture()
    const current = JSON.parse(readFileSync(join(root, m.recovery.backup.path), 'utf8'))
    current.comparisonCase = 'current-state'
    m.recovery.restored = put(current)
    expect(verifyManifest(m, root, expected).issues).toEqual(
      expect.arrayContaining(['RECOVERY_RESTORED_CASE', 'RECOVERY_DATA']),
    )
  })
  it.each(['modelEndpoint', 'requestedModel', 'modelDecisionSha256'] as const)(
    'requires independent service pin %s',
    (field) => {
      const { root, m, expected } = fixture()
      const missing = { ...expected }
      delete (missing as Partial<Expected>)[field]
      expect(verifyManifest(m, root, missing).issues).toEqual(['EXPECTED_IDENTITY'])
    },
  )
  it('rejects arbitrary service tuples even if the actual and freeze agree', () => {
    const { root, m, expected } = fixture()
    m.model.endpoint = expected.modelEndpoint =
      'https://unapproved.example.invalid/chat/completions'
    m.model.requestedModel = expected.requestedModel = 'unapproved-model'
    expect(verifyManifest(m, root, expected).issues).toContain('MODEL_PROFILE_DRIFT')
  })
  it('rejects the Base URL in a field explicitly defined as the Chat Completions route', () => {
    const { root, m, expected } = fixture()
    m.model.endpoint = expected.modelEndpoint = 'https://api.deepseek.com'
    expect(verifyManifest(m, root, expected).issues).toContain('MODEL_PROFILE_DRIFT')
  })
  it.each(['pending', 'failed', 'missing', 'malformed'])(
    'rejects incomplete collector state: %s',
    (status) => {
      const { root, m, expected, put } = fixture()
      const d = m.artifacts[0].device
      if (status === 'missing') rmSync(join(root, d.collectorStatus.path))
      else
        d.collectorStatus = put(
          status === 'malformed'
            ? { status: 'complete' }
            : { schemaVersion: 1, status, step: 'signature', exitCode: 1 },
        )
      expect(verifyManifest(m, root, expected).issues).toContain('WIN_COLLECTOR_INCOMPLETE')
    },
  )
  it.each(['collector-complete', 'installed-components-match-package'])(
    'requires device evidence %s',
    (id) => {
      const { root, m, expected } = fixture()
      m.artifacts[0].device.report.checks = m.artifacts[0].device.report.checks.filter(
        (c) => c.id !== id,
      )
      expect(verifyManifest(m, root, expected).issues).toContain('WIN_DEVICE_COVERAGE')
    },
  )
  it('rejects package-source drift despite an unchanged complete marker', () => {
    const { root, m, expected, put } = fixture()
    const c = m.artifacts[0].device.report.checks.find(
      (c) => c.id === 'installed-components-match-package',
    )!
    const payload = JSON.parse(readFileSync(join(root, c.actual.path), 'utf8'))
    payload.packageSha256 = '0'.repeat(64)
    c.actual = put(payload)
    expect(verifyManifest(m, root, expected).issues).toContain('WIN_PACKAGE_SOURCE')
  })
  it.each(['rollback-retain-new-version-copy', 'rollback-refuse-incompatible-format'])(
    'requires explicit recovery and per-asset rollback evidence %s',
    (id) => {
      const { root, m, expected } = fixture()
      m.recovery.report.checks = m.recovery.report.checks.filter((c) => c.id !== id)
      m.recovery.rollbackInstallers[0].signature.report.checks =
        m.recovery.rollbackInstallers[0].signature.report.checks.filter((c) => c.id !== id)
      expect(verifyManifest(m, root, expected).issues).toEqual(
        expect.arrayContaining(['RECOVERY_COVERAGE', 'ROLLBACK_windows11-x64_COVERAGE']),
      )
    },
  )
  it('retains eight-step completion at 4/5 and rejects 3/5 or core/transfer contradictions', () => {
    const { root, m, expected } = fixture()
    expect(verifyManifest(m, root, expected).issues).toEqual([])
    m.users[3].coreCompleted = false
    expect(verifyManifest(m, root, expected).issues).toContain('USER_COMPLETION_RATE')
    m.users[0].transferCompleted = false
    expect(verifyManifest(m, root, expected).issues).toContain('USER_CORE_TRANSFER_CONTRADICTION')
  })
  it('counts product guidance for operation completion but records it separately from independence', () => {
    const { root, m, expected } = fixture()
    m.users[0].assistance = 'product-hints'
    m.users[0].transferIndependent = false
    expect(verifyManifest(m, root, expected).issues).toEqual([])
    m.users[0].transferIndependent = true
    expect(verifyManifest(m, root, expected).issues).toContain('USER_ASSISTANCE')
    m.users[0].assistance = 'agent-full'
    expect(verifyManifest(m, root, expected).issues).toContain('USER_ASSISTANCE')
  })
  it('refuses unapproved production profiles even when both manifest and freeze pin the same bytes', () => {
    const { root, m, expected } = fixture()
    m.mode = 'evidence'
    expect(verifyManifest(m, root, expected).issues).toContain('BASELINE_APPROVED_PROFILE')
  })
  it('enforces the approved 18-path production profile/version/hash independently of the freeze', () => {
    const { root, m, expected, put } = fixture({ fixedBaseline: true })
    m.mode = 'evidence'
    expect(verifyManifest(m, root, expected).issues).not.toContain('BASELINE_APPROVED_PROFILE')
    const original = JSON.parse(readFileSync(join(root, m.baseline.path), 'utf8'))
    for (const mutation of ['missing', 'extra', 'version']) {
      const value = structuredClone(original)
      if (mutation === 'missing') delete value.files['content/learning/checks.json']
      if (mutation === 'extra')
        value.files['unapproved.json'] = put('unapproved', 'unapproved.json').sha256
      if (mutation === 'version') value.version = 'unapproved-version'
      m.baseline = put(value, 'tests/fixtures/product-baselines/manifest.json')
      expected.baselineSha256 = m.baseline.sha256
      expect(verifyManifest(m, root, expected).issues).toContain('BASELINE_APPROVED_PROFILE')
    }
  })
  const negatives: [string, (m: Manifest) => void, string][] = [
    [
      'missing signature',
      (m) => {
        m.artifacts[0].signature.valid = false
      },
      'WIN_SIGNATURE',
    ],
    [
      'adhoc identity',
      (m) => {
        m.artifacts[1].signature.identity = 'adhoc'
      },
      'MAC_SIGNATURE',
    ],
    [
      'missing notarization',
      (m) => {
        m.artifacts[1].signature.stapled = false
      },
      'MAC_NOTARIZATION',
    ],
    [
      'wrong architecture',
      (m) => {
        m.artifacts[0].engineArch = 'arm64'
      },
      'WIN_ARCH',
    ],
    [
      'wrong candidate SHA',
      (m) => {
        m.reviewedSha = '2'.repeat(40)
      },
      'CANDIDATE_SHA',
    ],
    [
      'stale report SHA',
      (m) => {
        m.model.report.candidateSha = '2'.repeat(40)
      },
      'MODEL_BINDING',
    ],
    [
      'drifted artifact',
      (m) => {
        m.artifacts[0].file.sha256 = '0'.repeat(64)
      },
      'WIN_ARTIFACT',
    ],
    [
      'wrong artifact version',
      (m) => {
        m.artifacts[0].appVersion = '0.0.1'
      },
      'WIN_VERSION',
    ],
    [
      'license omitted',
      (m) => {
        m.artifacts[0].components[0].version = '2.0.0'
      },
      'WIN_LICENSE_COVERAGE',
    ],
    [
      'wrong target OS',
      (m) => {
        m.artifacts[1].device.version = '26.6.2'
      },
      'MAC_CLEAN_TARGET',
    ],
    [
      'developer dependency installed',
      (m) => {
        m.artifacts[0].device.pythonInstalled = true
      },
      'WIN_CLEAN_TARGET',
    ],
    [
      'incomplete native tests',
      (m) => {
        m.artifacts[0].device.report.checks.pop()
      },
      'WIN_DEVICE_COVERAGE',
    ],
    [
      'channel drift',
      (m) => {
        m.artifacts[0].download.file = m.artifacts[1].file
      },
      'WIN_CHANNEL_HASH',
    ],
    [
      'channel credentials',
      (m) => {
        m.artifacts[0].download.url = 'https://user:password@example.invalid/file'
      },
      'WIN_CHANNEL_URL',
    ],
    [
      'old user evidence',
      (m) => {
        m.users[0].testedAt = '2026-10-20T00:00:00+08:00'
      },
      'USER_STALE',
    ],
    [
      'old model evidence',
      (m) => {
        m.model.report.testedAt = '2026-10-20T00:00:00+08:00'
      },
      'MODEL_STALE',
    ],
    [
      'AI users',
      (m) => {
        m.users[0].human = false
      },
      'USER_ELIGIBILITY',
    ],
    [
      'developer users',
      (m) => {
        m.users[0].developer = true
      },
      'USER_ELIGIBILITY',
    ],
    [
      'duplicate users',
      (m) => {
        m.users[0].id = m.users[1].id
      },
      'USER_DUPLICATE',
    ],
    [
      'below 80%',
      (m) => {
        m.users[0].coreCompleted = false
      },
      'USER_COMPLETION_RATE',
    ],
    [
      'human help counted',
      (m) => {
        m.users[0].assistance = 'partial-human-help'
      },
      'USER_COMPLETION_RATE',
    ],
    [
      'agent transfer counted',
      (m) => {
        m.users[0].agentMarkedIndependent = true
      },
      'USER_ASSISTANCE',
    ],
    [
      'missing full-assistance negative',
      (m) => {
        m.users[0].agentFullCounterexample = false
      },
      'USER_ASSISTANCE',
    ],
    [
      'fabricated model results',
      (m) => {
        m.model.fabricatedResults = 1
      },
      'MODEL_FABRICATION',
    ],
    [
      'failed designated review',
      (m) => {
        m.reviews[0].verdict = 'fail'
      },
      'REVIEW_VERDICT',
    ],
    [
      'wrong review model',
      (m) => {
        m.reviews[0].model = 'another-model'
      },
      'REVIEW_VERDICT',
    ],
    [
      'old review evidence',
      (m) => {
        m.reviews[0].report.testedAt = '2026-10-20T00:00:00+08:00'
      },
      'REVIEW_zcode_STALE',
    ],
    [
      'missing P0 coverage',
      (m) => {
        m.product.checks.shift()
      },
      'PRODUCT_COVERAGE',
    ],
    [
      'one-way migration',
      (m) => {
        m.migration[1] = m.migration[0]
      },
      'MIGRATION_DIRECTIONS',
    ],
    [
      'duplicate targets',
      (m) => {
        m.artifacts[1] = m.artifacts[0]
      },
      'TARGET_MATRIX',
    ],
    [
      'wrong build source',
      (m) => {
        m.artifacts[0].build.sourceSha = '3'.repeat(40)
      },
      'WIN_BUILD_SHA',
    ],
  ]
  it.each(negatives)('rejects %s', (_, mutate, code) => {
    const { root, m, expected } = fixture()
    mutate(m)
    const result = verifyManifest(m, root, expected)
    expect(result.consistent).toBe(false)
    expect(result.issues).toContain(code)
  })
  it('rejects equal counts with different objects', () => {
    const { root, m, expected, put } = fixture()
    m.product.checks[0].actual = put({
      ids: ['A02'],
      status: 'complete',
      provenance: ['synthetic-input'],
    })
    expect(verifyManifest(m, root, expected).issues).toContain('PRODUCT_RESULT')
    expect(compareComplete({ a: [1, 2] }, { a: [2, 1] })).toBe(false)
    expect(compareComplete({ a: 1, b: 2 }, { b: 2, a: 1 })).toBe(true)
  })
  it('rejects lost ownership in otherwise same recovery', () => {
    const { root, m, expected, put } = fixture()
    const changed = JSON.parse(readFileSync('tests/fixtures/release/comparison.json', 'utf8'))
    changed.ownership = []
    m.recovery.restored = put(changed)
    m.migration[0].after = put(changed)
    const result = verifyManifest(m, root, expected)
    expect(result.issues).toContain('RECOVERY_DATA')
    expect(result.issues).toContain('MIGRATION_DATA')
  })
  it('rejects count-only snapshots and unavailable data', () => {
    const { root, m, expected, put } = fixture()
    m.recovery.backup = put({ count: 1 })
    m.recovery.restored = m.recovery.backup
    expect(verifyManifest(m, root, expected).issues).toContain('RECOVERY_BACKUP_SCHEMA')
    rmSync(join(root, m.recovery.backup.path))
    expect(verifyManifest(m, root, expected).issues).toContain('RECOVERY_BACKUP')
  })
  it('rejects traversal, external symlink, malformed JSON and extra keys', () => {
    const { root, m, expected } = fixture()
    m.model.evaluation.path = '../outside.json'
    expect(verifyManifest(m, root, expected).issues).toContain('MODEL_EVALUATION')
    symlinkSync('/etc/hosts', join(root, 'outside'))
    m.model.evaluation.path = 'outside'
    expect(verifyManifest(m, root, expected).issues).toContain('MODEL_EVALUATION')
    expect(verifyManifest({ ...m, publish: true }, root, expected).issues).toEqual([
      'MANIFEST_SCHEMA',
    ])
  })
  it('rejects changed pinned baselines and future reports', () => {
    const { root, m, expected } = fixture()
    expect(
      verifyManifest(m, root, { ...expected, baselineSha256: '0'.repeat(64) }).issues,
    ).toContain('BASELINE_IDENTITY')
    m.users[0].testedAt = '2026-10-26T00:00:00+08:00'
    expect(verifyManifest(m, root, expected).issues).toContain('USER_STALE')
  })
  it('rejects forged freeze time, model drift, empty snapshots and count-only fixed expectations', () => {
    const { root, m, expected, put } = fixture()
    m.candidateFrozenAt = '2020-01-01T00:00:00+08:00'
    expect(verifyManifest(m, root, expected).issues).toContain('FREEZE_IDENTITY')
    m.candidateFrozenAt = profile.frozenAt
    m.model.mode = 'non-thinking'
    expect(verifyManifest(m, root, expected).issues).toContain('MODEL_PROFILE_DRIFT')
    for (const c of m.product.checks) c.expected = c.actual = put({ count: 1 })
    expect(verifyManifest(m, root, expected).issues).toContain('PRODUCT_EXPECTATION_BASELINE')
    const snapshot = JSON.parse(readFileSync('tests/fixtures/release/comparison.json', 'utf8'))
    for (const key of Object.keys(snapshot)) if (Array.isArray(snapshot[key])) snapshot[key] = []
    snapshot.executionVersions = {}
    m.recovery.backup = m.recovery.restored = put(snapshot)
    expect(verifyManifest(m, root, expected).issues).toContain('RECOVERY_BACKUP_SCHEMA')
  })
  it('rejects unsigned-text rollback installer and incomplete transfer closure', () => {
    const { root, m, expected, put } = fixture()
    m.recovery.rollbackInstallers[0].file = put('not an installer')
    for (const u of m.users) {
      u.transferCompleted = false
      u.transferIndependent = false
    }
    const result = verifyManifest(m, root, expected)
    expect(result.issues).toContain('ROLLBACK_BINARY_FORMAT')
    expect(result.issues).toContain('USER_COMPLETION_RATE')
  })
  it('rejects arbitrary equal snapshot rows, forged FR expectations and current-asset rollback', () => {
    const { root, m, expected, put } = fixture()
    const snapshot = JSON.parse(readFileSync('tests/fixtures/release/comparison.json', 'utf8'))
    for (const key of Object.keys(snapshot))
      if (Array.isArray(snapshot[key])) snapshot[key] = [{ a: null, b: null }]
    m.recovery.backup = m.recovery.restored = put(snapshot)
    m.migration[0].before = m.migration[0].after = m.recovery.backup
    for (const c of m.product.checks.filter((c) => c.id.startsWith('FR-')))
      c.expected = c.actual = put({ count: 1 })
    m.recovery.rollbackInstallers[0].file = m.artifacts[0].file
    const result = verifyManifest(m, root, expected)
    expect(result.issues).toContain('RECOVERY_SOURCE_PIN')
    expect(result.issues).toContain('RECOVERY_BACKUP_SCHEMA')
    expect(result.issues).toContain('MIGRATION_SOURCE_PIN')
    expect(result.issues).toContain('PRODUCT_EXPECTATION_PIN')
    expect(result.issues).toContain('ROLLBACK_IDENTITY_PIN')
  })
  it('reports a missing migration destination explicitly after duplicate-target rejection', () => {
    const { root, m, expected } = fixture()
    m.artifacts[1] = m.artifacts[0]
    expect(verifyManifest(m, root, expected).issues).toEqual(
      expect.arrayContaining(['TARGET_MATRIX', 'MIGRATION_DESTINATION']),
    )
  })
  it('CLI replaces forged freeze.now with the current local clock', () => {
    const { root, m, expected } = fixture()
    m.users[0].testedAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    writeFileSync(join(root, 'manifest.json'), JSON.stringify(m))
    writeFileSync(
      join(root, 'freeze.json'),
      JSON.stringify({ ...expected, now: '2099-12-31T00:00:00Z' }),
    )
    const run = spawnSync(
      process.execPath,
      [
        'scripts/release/verify-release.mjs',
        join(root, 'manifest.json'),
        root,
        join(root, 'freeze.json'),
      ],
      { encoding: 'utf8' },
    )
    expect(run.status).toBe(1)
    expect(run.stderr).toBe('')
    expect(JSON.parse(run.stdout).issues).toContain('USER_STALE')
  })
  it.each([
    { label: 'no arguments', args: [] },
    { label: 'missing arguments', args: ['sensitive-only'] },
    { label: 'an empty required argument', args: ['manifest.json', '', 'freeze.json'] },
    { label: 'extra arguments', args: ['one', 'two', 'three', 'sensitive-extra'] },
  ])('CLI refuses $label with fixed usage and no path disclosure', ({ args }) => {
    const run = spawnSync(process.execPath, ['scripts/release/verify-release.mjs', ...args], {
      encoding: 'utf8',
    })
    expect(run.status).toBe(2)
    expect(run.stdout).toBe('')
    expect(run.stderr).toBe(
      'Usage: node scripts/release/verify-release.mjs MANIFEST EVIDENCE_ROOT TRUSTED_FREEZE.json\n',
    )
  })
  it.each([
    { name: 'manifest', failure: 'missing' },
    { name: 'freeze', failure: 'missing' },
    { name: 'manifest', failure: 'malformed' },
    { name: 'freeze', failure: 'malformed' },
  ])('CLI rejects $failure $name with the whole fixed error surface', ({ name, failure }) => {
    const { root, m, expected } = fixture()
    const paths = { manifest: join(root, 'manifest.json'), freeze: join(root, 'freeze.json') }
    writeFileSync(paths.manifest, JSON.stringify(m))
    writeFileSync(paths.freeze, JSON.stringify(expected))
    const selected = name as keyof typeof paths
    if (failure === 'missing') paths[selected] = join(root, 'sensitive-missing.json')
    else writeFileSync(paths[selected], 'sensitive invalid contents')
    const run = spawnSync(
      process.execPath,
      ['scripts/release/verify-release.mjs', paths.manifest, root, paths.freeze],
      { encoding: 'utf8' },
    )
    expect(run.status).toBe(2)
    expect(run.stdout).toBe('')
    expect(run.stderr).toBe('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID\n')
  })
  it.each(['manifest', 'freeze'])(
    'CLI rejects oversized %s with fixed stderr before parse',
    (name) => {
      const { root, m, expected } = fixture()
      writeFileSync(join(root, 'manifest.json'), JSON.stringify(m))
      writeFileSync(join(root, 'freeze.json'), JSON.stringify(expected))
      truncateSync(join(root, `${name}.json`), 16 * 1024 * 1024 + 1)
      const run = spawnSync(
        process.execPath,
        [
          'scripts/release/verify-release.mjs',
          join(root, 'manifest.json'),
          root,
          join(root, 'freeze.json'),
        ],
        { encoding: 'utf8' },
      )
      expect(run.status).toBe(2)
      expect(run.stdout).toBe('')
      expect(run.stderr).toBe('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID\n')
    },
  )
  it.each(['manifest', 'freeze'])(
    'CLI preserves the schema failure contract for %s without printing input data',
    (name) => {
      const { root, m, expected } = fixture()
      const manifest = join(root, 'manifest.json')
      const freeze = join(root, 'freeze.json')
      writeFileSync(manifest, JSON.stringify(m))
      writeFileSync(freeze, JSON.stringify(expected))
      writeFileSync(join(root, `${name}.json`), JSON.stringify({ sensitive: 'invalid schema' }))
      const run = spawnSync(
        process.execPath,
        ['scripts/release/verify-release.mjs', manifest, root, freeze],
        { encoding: 'utf8' },
      )
      if (name === 'freeze') {
        expect(run.status).toBe(2)
        expect(run.stdout).toBe('')
        expect(run.stderr).toBe('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID\n')
      } else {
        expect(run.status).toBe(1)
        expect(run.stderr).toBe('')
        expect(JSON.parse(run.stdout)).toEqual({
          consistent: false,
          releaseAuthorized: false,
          mode: 'invalid',
          issues: ['MANIFEST_SCHEMA'],
        })
      }
    },
  )
  it('CLI fails closed for synthetic and malformed inputs without printing contents', () => {
    const { root, m, expected } = fixture()
    const path = join(root, 'manifest.json')
    writeFileSync(path, JSON.stringify(m))
    const { now: _now, ...pins } = expected
    void _now
    writeFileSync(join(root, 'freeze.json'), JSON.stringify(pins))
    const args = ['scripts/release/verify-release.mjs', path, root, join(root, 'freeze.json')]
    const run = spawnSync(process.execPath, args, { encoding: 'utf8' })
    expect(run.status).toBe(1)
    expect(run.stderr).toBe('')
    expect(JSON.parse(run.stdout).releaseAuthorized).toBe(false)
    writeFileSync(path, 'sensitive invalid contents')
    const bad = spawnSync(process.execPath, args, { encoding: 'utf8' })
    expect(bad.status).toBe(2)
    expect(bad.stdout).toBe('')
    expect(bad.stderr).toBe('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID\n')
  })
  it('CLI reports an actual implementation import failure without a stack or path', () => {
    const { root } = fixture()
    const cli = join(root, 'isolated-cli.mjs')
    writeFileSync(cli, readFileSync('scripts/release/verify-release.mjs'))
    const run = spawnSync(process.execPath, [cli, 'missing.json', root, 'missing-freeze.json'], {
      encoding: 'utf8',
    })
    expect(run.status).toBe(2)
    expect(run.stdout).toBe('')
    expect(run.stderr).toBe('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID\n')
  })
  it.each(['24.0.0', '24.2.9', '23.9.0', '25.0.0'])(
    'CLI rejects simulated unsupported Node %s before loading TypeScript',
    (version) => {
      const { root } = fixture()
      const cli = join(root, 'isolated-cli.mjs')
      const preload = join(root, 'runtime-version.mjs')
      writeFileSync(cli, readFileSync('scripts/release/verify-release.mjs'))
      writeFileSync(
        preload,
        `Object.defineProperty(process.versions, 'node', { value: ${JSON.stringify(version)} })`,
      )
      const run = spawnSync(
        process.execPath,
        ['--import', pathToFileURL(preload).href, cli, 'missing.json', root, 'missing-freeze.json'],
        { encoding: 'utf8' },
      )
      expect(run.status).toBe(2)
      expect(run.stdout).toBe('')
      expect(run.stderr).toBe('UNSUPPORTED_NODE_RUNTIME\n')
    },
  )
  it('CLI preserves an independent runtime warning while failing a real input read', () => {
    const { root } = fixture()
    const preload = join(root, 'runtime-warning.mjs')
    writeFileSync(
      preload,
      "process.emitWarning('T11 controlled diagnostic', { code: 'T11_TEST_WARNING' })",
    )
    const run = spawnSync(
      process.execPath,
      [
        '--import',
        pathToFileURL(preload).href,
        'scripts/release/verify-release.mjs',
        join(root, 'missing.json'),
        root,
        join(root, 'missing-freeze.json'),
      ],
      { encoding: 'utf8' },
    )
    expect(run.status).toBe(2)
    expect(run.stdout).toBe('')
    expect(run.stderr).toContain('[T11_TEST_WARNING]')
    expect(run.stderr).toContain('T11 controlled diagnostic')
    expect(run.stderr).toContain('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID\n')
    expect(run.stderr).not.toContain('MODULE_TYPELESS_PACKAGE_JSON')
  })
})

describe('Stage 0 packaging configuration invariants (apps/desktop)', () => {
  const builder = readFileSync('apps/desktop/electron-builder.yml', 'utf8')
  const desktop = JSON.parse(readFileSync('apps/desktop/package.json', 'utf8'))
  const section = (name: string): string => {
    const start = builder.indexOf(`\n${name}:\n`)
    if (start === -1) throw new Error(`missing electron-builder section ${name}`)
    const rest = builder.slice(start + 1)
    const body = rest.slice(rest.indexOf('\n') + 1)
    const next = body.search(/^[\w-]+:\s*$/m)
    return next === -1 ? rest : rest.slice(0, rest.length - body.length + next)
  }
  it('makes release signing mandatory and keeps the official mac identity enabled', () => {
    expect(builder).toContain('forceCodeSigning: true')
    const mac = section('mac')
    expect(mac).toContain('hardenedRuntime: true')
    expect(mac).toContain('notarize: true')
    expect(mac).toContain('- target: dmg')
    expect(mac).toContain('- arm64')
    // mac.identity must not be disabled (identity: null) in the official release config.
    expect(mac).not.toContain('identity')
  })
  it('signs the Windows executable and builds nsis/x64', () => {
    const win = section('win')
    expect(win).toContain('signAndEditExecutable: true')
    expect(win).toContain('signExecutable: true')
    expect(win).toContain('- target: nsis')
    expect(win).toContain('- x64')
  })
  it('carries exactly six extraResources including the FR003 bundle and Electron licenses', () => {
    const extra = section('extraResources')
    expect((extra.match(/- from:/g) ?? []).length).toBe(6)
    expect(extra).toContain('fr003-bundle-v2')
    expect(extra).toContain('to: licenses/electron/LICENSE')
    expect(extra).toContain('to: licenses/electron/LICENSES.chromium.html')
    expect(extra).toContain('to: engine')
    expect(extra).toContain('to: contracts/v2')
    expect(extra).toContain('to: examples/equipment-maintenance')
    expect(extra).toContain('to: licenses')
  })
  it('contains zero hardcoded certificate identities, passwords or secrets', () => {
    const forbidden =
      /^\s*[\w-]*(?:password|secret|certificate|api[-_]?key|identity|csc)[\w-]*\s*:/i
    for (const line of builder.split('\n')) expect(line).not.toMatch(forbidden)
  })
  it('separates the unsigned directory pre-verification build from the signed release builds', () => {
    const dir = desktop.scripts['package:dir']
    expect(dir).toContain('-c.forceCodeSigning=false')
    expect(dir).toContain('-c.mac.identity=null')
    expect(dir).toContain('-c.mac.hardenedRuntime=false')
    expect(dir).toContain('-c.mac.notarize=false')
    expect(dir).toContain('-c.win.signExecutable=false')
    expect(desktop.scripts['package:release:mac']).toContain('dmg')
    expect(desktop.scripts['package:release:mac']).toContain('arm64')
    expect(desktop.scripts['package:release:win']).toContain('nsis')
    expect(desktop.scripts['package:release:win']).toContain('x64')
    expect(desktop.scripts['package:release:mac']).not.toMatch(/-c\./)
    expect(desktop.scripts['package:release:win']).not.toMatch(/-c\./)
  })
})

describe('T10 to t11-comparison-v3 projection mapping (project-t10-comparison.py)', () => {
  // The exact honest mapping the read-only projector emits for a full T10 package:
  // carried layers only (facts/definitions/ownership/mappingState/history/agentSessions),
  // never-carried layers empty (queries/results/rounds/rawSources/undo/derivedResults) and
  // v1 portability claims mirrored from transfer/service.py (no rerun, no replay).
  const projection = {
    format: 't11-comparison-v3',
    comparisonCase: 'current-state',
    projectId: 't10-package',
    sourceSnapshotId: 'a'.repeat(64),
    projectRevision: 3,
    selection: {
      currentDerived: false,
      historicalRuns: true,
      rawSources: false,
      agentSessions: true,
      priorUndo: false,
    },
    capabilities: { restoreCurrent: true, rerunOriginalMapping: false, replaySandbox: false },
    dependencies: {
      mappingSources: 'missing',
      replayInputs: false,
      replayConfiguration: false,
      replaySemantics: 'missing',
    },
    facts: [
      {
        id: 'b'.repeat(64),
        payload: { subject: 'urn:x:equipment/001', predicate: 'urn:x:name', object: '"泵站A"' },
      },
    ],
    definitions: [
      { id: 'G', payload: { layer: 'ontology', definition: { triples: [], references: [] } } },
    ],
    ownership: [
      {
        id: 'b'.repeat(64),
        payload: {
          fact: 'b'.repeat(64),
          owner: 'equip-map',
          row: 0,
          managedValue: '"C"',
        },
      },
    ],
    mappingState: [
      { id: 'equip-map', payload: { mapping: 'equip-map', generatedVersion: 1, stale: [] } },
    ],
    queries: [],
    results: [],
    derivedResults: [],
    history: [
      {
        id: 'history-1',
        payload: { sequence: 1, operationId: 'op-1', operationKind: 'application' },
      },
    ],
    rounds: [],
    rawSources: [],
    agentSessions: [
      {
        id: 'attempt-1',
        payload: {
          attempt: 'attempt-1',
          recordVersion: 1,
          course: '检修',
          task: 'transfer-repair',
          record: { taskId: 'transfer-repair', operationComplete: true },
        },
      },
    ],
    undo: [],
    executionVersions: {
      semantics: 'application-state-v1',
      engine: 'db-format-v3',
      lock: 'checkpoint-schema-v1',
    },
  }
  it('accepts the projector mapping through the exported comparisonSchema', () => {
    expect(comparisonSchema.safeParse(projection).success).toBe(true)
  })
  it('refuses a template projection instead of weakening the restoreCurrent contract', () => {
    const template = structuredClone(projection)
    template.capabilities.restoreCurrent = false
    template.facts = []
    template.ownership = []
    expect(comparisonSchema.safeParse(template).success).toBe(false)
  })
  it('refuses history rows when historicalRuns was not selected', () => {
    const unselected = structuredClone(projection)
    unselected.selection.historicalRuns = false
    expect(comparisonSchema.safeParse(unselected).success).toBe(false)
  })
  it('refuses an honest v1 projection that lies about rerunOriginalMapping', () => {
    const lying = structuredClone(projection)
    lying.capabilities.rerunOriginalMapping = true
    expect(comparisonSchema.safeParse(lying).success).toBe(false)
  })
  it('refuses a replay capability without portable scenario inputs', () => {
    const lying = structuredClone(projection)
    lying.capabilities.replaySandbox = true
    expect(comparisonSchema.safeParse(lying).success).toBe(false)
  })
  it('refuses g6-conflict for a projection whose queries/results layers can never be carried', () => {
    const g6 = structuredClone(projection)
    g6.comparisonCase = 'g6-conflict'
    expect(comparisonSchema.safeParse(g6).success).toBe(false)
  })
})
