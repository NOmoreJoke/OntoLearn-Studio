import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import policyJson from '../../.github/review-policy.json'
import {
  IMMUTABLE_L2_PATTERNS,
  bumpKind,
  classifyChange,
  classifyPackageJson,
  classifyPath,
  globToRegExp,
  type ReviewPolicy,
} from '../../scripts/review-level-core.mjs'

const policy = policyJson as unknown as ReviewPolicy
const pkg = (devDependencies: Record<string, string>, extra: object = {}) =>
  JSON.stringify({ name: 'x', ...extra, devDependencies })
// 敌意策略：删除全部规则并默认 L0，模拟"策略被改写以自我降级"
const hostile: ReviewPolicy = { version: 1, defaultLevel: 'L0', rules: [] }

describe('review level glob', () => {
  it('matches ** across directories and * within one segment', () => {
    expect(globToRegExp('apps/desktop/src/main/**').test('apps/desktop/src/main/a/b.ts')).toBe(true)
    expect(globToRegExp('scripts/verify-*').test('scripts/verify-sources.mjs')).toBe(true)
    expect(globToRegExp('scripts/verify-*').test('scripts/sub/verify-x')).toBe(false)
    expect(globToRegExp('docs/verification*').test('docs/verification-2026-10-19.md')).toBe(true)
    expect(globToRegExp('packages/contracts/**').test('packages/contracts/README.md')).toBe(true)
    expect(globToRegExp('packages/contracts/**').test('packages/contracts/src/v2.ts')).toBe(true)
  })
})

describe('review level path rules', () => {
  it.each([
    ['apps/desktop/src/main/window-security.ts', 'L2'],
    ['apps/desktop/src/preload/index.ts', 'L2'],
    ['packages/contracts/src/v2.ts', 'L2'],
    ['packages/contracts/README.md', 'L2'],
    ['packages/engine/src/ontolearn_engine/storage.py', 'L2'],
    ['scripts/verify-sources.mjs', 'L2'],
    ['scripts/ci-quality-schedule.py', 'L2'],
    ['scripts/run-engine-tests.py', 'L2'],
    ['.github/review-policy.json', 'L2'],
    ['docs/process/review-policy.md', 'L2'],
    ['docs/process/review-checklist.md', 'L2'],
    ['scripts/review-level-core.mjs', 'L2'],
    ['scripts/review-level-utils.mjs', 'L2'],
    ['tests/unit/review-level.test.ts', 'L2'],
    ['.github/workflows/ci.yml', 'L2'],
    ['.github/workflows/release.yml', 'L2'],
    ['docs/prd/PRD.md', 'L2'],
    ['apps/desktop/src/renderer/App.tsx', 'L1'],
    ['tests/unit/csp.test.ts', 'L1'],
    ['packages/engine/tests/test_storage.py', 'L1'],
    ['docs/architecture/0001-desktop-framework.md', 'L1'],
    ['docs/reviews/T02/report.md', 'L0'],
    ['docs/m0-checklist.md', 'L0'],
    ['README.md', 'L0'],
    ['some/unknown/file.txt', 'L1'],
  ])('%s → %s', (path, level) => {
    expect(classifyPath(path, policy).level).toBe(level)
  })
})

describe('review level dependency rules', () => {
  it('classifies semver bumps only for single simple specs', () => {
    expect(bumpKind('5.9.3', '7.0.2')).toBe('major')
    expect(bumpKind('26.15.3', '26.18.0')).toBe('minor')
    expect(bumpKind('^8.71.2', '^8.71.3')).toBe('patch')
    expect(bumpKind('0.3.0', '0.4.0')).toBe('major')
    expect(bumpKind('latest', '1.0.0')).toBe('unknown')
    expect(bumpKind('1.0.0', '1.0.0')).toBe('none')
    expect(bumpKind(' 1.0.0 ', '1.0.0')).toBe('none')
  })

  it('treats ranges, wildcards, prefixes and exotic specs as unknown', () => {
    expect(bumpKind('44.9.0', '44.9.0 || 45.0.0')).toBe('unknown')
    expect(bumpKind('^1.0.0 || ^2.0.0', '^1.0.0 || ^3.0.0')).toBe('unknown')
    expect(bumpKind('>=1.0.0 <2.0.0', '>=1.0.0 <1.0.0')).toBe('unknown')
    expect(bumpKind('1.0.0 - 2.0.0', '1.0.0')).toBe('unknown')
    expect(bumpKind('1.x', '2.x')).toBe('unknown')
    expect(bumpKind('*', '^1.0.0')).toBe('unknown')
    expect(bumpKind('1.0.0-rc.1', '1.0.0')).toBe('unknown')
    expect(bumpKind('1.0.0+build', '1.0.0')).toBe('unknown')
    expect(bumpKind('44.9.0', 'latest')).toBe('unknown')
    expect(bumpKind('44.9.0', 'next')).toBe('unknown')
    expect(bumpKind('file:../x', '^1.0.0')).toBe('unknown')
    expect(bumpKind('workspace:*', '^1.0.0')).toBe('unknown')
    expect(bumpKind('https://x/y-1.0.0.tgz', '^1.0.0')).toBe('unknown')
    // 区间前缀改变不得判 none
    expect(bumpKind('1.0.0', '^1.0.0')).toBe('unknown')
    expect(bumpKind('^1.0.0', '~1.0.0')).toBe('unknown')
  })

  it.each([
    [{ typescript: '5.9.3' }, { typescript: '7.0.2' }, 'L2'],
    [{ electron: '44.9.0' }, { electron: '45.0.0' }, 'L2'],
    [{ 'electron-builder': '26.15.3' }, { 'electron-builder': '26.18.0' }, 'L1'],
    [{ 'typescript-eslint': '8.71.2' }, { 'typescript-eslint': '8.72.0' }, 'L1'],
    [{ 'typescript-eslint': '8.71.2' }, { 'typescript-eslint': '8.71.3' }, 'L0'],
    [{ globals: '16.0.0' }, { globals: '17.0.0' }, 'L1'],
  ])('%o → %o = %s', (from, to, level) => {
    expect(classifyPackageJson(pkg(from), pkg(to), policy).level).toBe(level)
  })

  it('treats runtime dependency changes and script edits conservatively', () => {
    const a = JSON.stringify({ dependencies: { n3: '1.17.0' } })
    const b = JSON.stringify({ dependencies: { n3: '2.0.0' } })
    expect(classifyPackageJson(a, b, policy).level).toBe('L2')
    expect(classifyPackageJson(pkg({}), pkg({}, { scripts: { x: 'y' } }), policy).level).toBe('L1')
  })

  it('escalates unparsable specs of critical or runtime deps to L2', () => {
    // 关键依赖：区间放宽 / 浮动 tag
    expect(
      classifyPackageJson(
        pkg({ electron: '44.9.0' }),
        pkg({ electron: '44.9.0 || 45.0.0' }),
        policy,
      ).level,
    ).toBe('L2')
    expect(
      classifyPackageJson(pkg({ electron: '44.9.0' }), pkg({ electron: 'latest' }), policy).level,
    ).toBe('L2')
    // 运行时依赖：区间边界变化
    const runtime = (from: string, to: string): [string, string] => [
      JSON.stringify({ dependencies: { x: from } }),
      JSON.stringify({ dependencies: { x: to } }),
    ]
    expect(
      classifyPackageJson(...runtime('^1.0.0 || ^2.0.0', '^1.0.0 || ^3.0.0'), policy).level,
    ).toBe('L2')
    expect(classifyPackageJson(...runtime('>=1.0.0 <2.0.0', '>=1.0.0 <1.0.0'), policy).level).toBe(
      'L2',
    )
    expect(classifyPackageJson(...runtime('1.0.0', '^1.0.0'), policy).level).toBe('L2')
    // 非关键开发依赖的不可解析 spec 仍为 L1
    expect(
      classifyPackageJson(pkg({ leftpad: '^1 || ^2' }), pkg({ leftpad: '^1 || ^3' }), policy).level,
    ).toBe('L1')
  })

  it('treats optional/peer/overrides/resolutions as runtime semantics', () => {
    const opt = (v: string) => JSON.stringify({ optionalDependencies: { 'left-pad': v } })
    expect(classifyPackageJson(opt('1.0.0'), opt('2.0.0'), policy).level).toBe('L2')
    expect(
      classifyPackageJson('{}', JSON.stringify({ optionalDependencies: { x: '1.0.0' } }), policy)
        .level,
    ).toBe('L2')
    const peer = (v: string) => JSON.stringify({ peerDependencies: { react: v } })
    expect(classifyPackageJson(peer('^18.0.0'), peer('^19.0.0'), policy).level).toBe('L2')
    const override = (v: string) => JSON.stringify({ overrides: { 'global-agent': v } })
    expect(classifyPackageJson(override('4.1.3'), override('5.0.0'), policy).level).toBe('L2')
    expect(
      classifyPackageJson(
        JSON.stringify({ resolutions: { x: '^1.0.0' } }),
        JSON.stringify({ resolutions: { x: '^2.0.0' } }),
        policy,
      ).level,
    ).toBe('L2')
  })

  it('ignores pure key reordering in package.json', () => {
    const original = JSON.stringify({ name: 'x', version: '1.0.0', scripts: { a: 'x', b: 'y' } })
    const reordered = JSON.stringify({ scripts: { b: 'y', a: 'x' }, version: '1.0.0', name: 'x' })
    expect(classifyPackageJson(original, reordered, policy).level).toBe('L0')
    const depsReordered = JSON.stringify({ name: 'x', devDependencies: { a: '1.0.0' } })
    const depsOriginal = JSON.stringify({ devDependencies: { a: '1.0.0' }, name: 'x' })
    expect(classifyPackageJson(depsOriginal, depsReordered, policy).level).toBe('L0')
  })

  it('fails closed on missing or broken package.json text', () => {
    expect(() => classifyPackageJson('{', '{}', policy)).toThrow()
    expect(() => classifyPackageJson(undefined as unknown as string, '{}', policy)).toThrow()
    expect(() => classifyPackageJson('{}', undefined as unknown as string, policy)).toThrow()
    expect(() => classifyPackageJson(null, null, policy)).toThrow()
    expect(() => classifyPackageJson('[]', '{}', policy)).toThrow()
    expect(() => classifyPackageJson('"text"', '{}', policy)).toThrow()
    expect(() => classifyPackageJson('null', '{}', policy)).toThrow()
    expect(() => classifyChange([{ path: 'package.json' }], policy)).toThrow()
  })
})

describe('review level change summary', () => {
  it('takes the highest file level and lets lockfiles follow manifests', () => {
    const patch = classifyChange(
      [
        {
          path: 'package.json',
          base: pkg({ 'typescript-eslint': '8.71.2' }),
          head: pkg({ 'typescript-eslint': '8.71.3' }),
        },
        { path: 'package-lock.json' },
        { path: 'docs/reviews/x.md' },
      ],
      policy,
    )
    expect(patch.level).toBe('L0')
    expect(classifyChange([{ path: 'package-lock.json' }], policy).level).toBe('L1')
    expect(
      classifyChange([{ path: 'README.md' }, { path: 'apps/desktop/src/main/index.ts' }], policy)
        .level,
    ).toBe('L2')
  })

  it('classifies Python manifests conservatively as L2 and uv.lock accordingly', () => {
    expect(classifyChange([{ path: 'pyproject.toml' }], policy).level).toBe('L2')
    expect(classifyChange([{ path: 'packages/engine/pyproject.toml' }], policy).level).toBe('L2')
    expect(classifyChange([{ path: 'uv.lock' }], policy).level).toBe('L1')
    const withManifest = classifyChange(
      [{ path: 'packages/engine/pyproject.toml' }, { path: 'uv.lock' }],
      policy,
    )
    expect(withManifest.level).toBe('L2')
    expect(withManifest.files.find((f) => f.path === 'uv.lock')?.level).toBe('L0')
  })
})

describe('immutable L2 floor and trusted base policy', () => {
  const floorPaths = [
    '.github/review-policy.json',
    'docs/process/review-policy.md',
    'docs/process/review-checklist.md',
    'scripts/review-level.mjs',
    'scripts/review-level-core.mjs',
    'scripts/review-level-utils.mjs',
    'tests/unit/review-level.test.ts',
    '.github/workflows/ci.yml',
    'scripts/ci-quality-schedule.py',
    'scripts/run-engine-tests.py',
    'scripts/verify-sources.mjs',
    'scripts/i04_matrix_evidence.py',
    'docs/source-manifest.json',
    'packages/contracts/README.md',
    'docs/prd/PRD.md',
  ]

  it.each(floorPaths)('%s stays L2 even under a hostile policy', (path) => {
    expect(classifyChange([{ path }], hostile).level).toBe('L2')
  })

  it('keeps unprotected paths at the hostile level but elevates them via base policy', () => {
    // 敌意策略确实会降级普通路径（证明上面的 L2 来自硬底线/基线，而非默认值）
    expect(classifyChange([{ path: 'docs/reviews/x.md' }], hostile).level).toBe('L0')
    expect(classifyChange([{ path: 'apps/desktop/src/main/index.ts' }], hostile).level).toBe('L0')
    // basePolicy（可信基线）存在时每个文件取 max(head, base)
    expect(
      classifyChange([{ path: 'apps/desktop/src/main/index.ts' }], hostile, policy).level,
    ).toBe('L2')
    const mixed = classifyChange(
      [{ path: 'docs/reviews/x.md' }, { path: 'scripts/review-level.mjs' }],
      hostile,
      policy,
    )
    expect(mixed.level).toBe('L2')
  })

  it('blocks self-downgrade by deleting or rewriting rule 0', () => {
    const noRuleZero: ReviewPolicy = {
      ...policy,
      rules: policy.rules.filter((r) => !r.paths.includes('.github/review-policy.json')),
    }
    // 仅 head 策略删掉自保护规则：硬底线兜底
    expect(classifyChange([{ path: '.github/review-policy.json' }], noRuleZero).level).toBe('L2')
    // head 策略删除规则且基线策略仍在：取 max
    expect(classifyChange([{ path: '.github/review-policy.json' }], noRuleZero, policy).level).toBe(
      'L2',
    )
    // 策略文件在 head 被删除（规则失效）时同样不可降级
    expect(classifyChange([{ path: '.github/review-policy.json' }], hostile, null).level).toBe('L2')
  })

  it('exposes the immutable floor patterns', () => {
    expect(IMMUTABLE_L2_PATTERNS).toContain('.github/review-policy.json')
    expect(IMMUTABLE_L2_PATTERNS).toContain('scripts/review-level*')
    expect(IMMUTABLE_L2_PATTERNS).toContain('tests/unit/review-level*.test.ts')
    expect(IMMUTABLE_L2_PATTERNS).toContain('.github/workflows/**')
    expect(IMMUTABLE_L2_PATTERNS).toContain('packages/contracts/**')
    expect(IMMUTABLE_L2_PATTERNS).toContain('docs/prd/**')
  })
})

describe('review level CLI', () => {
  const ROOT = fileURLToPath(new URL('../..', import.meta.url))
  const run = (...cliArgs: string[]) => {
    try {
      const stdout = execFileSync(process.execPath, ['scripts/review-level.mjs', ...cliArgs], {
        cwd: ROOT,
        encoding: 'utf8',
      })
      return { status: 0, stdout, stderr: '' }
    } catch (e) {
      const err = e as { status?: number; stdout?: string; stderr?: string }
      return {
        status: err.status ?? 1,
        stdout: err.stdout ?? '',
        stderr: err.stderr ?? '',
      }
    }
  }

  it('emits binding and mechanical evidence in --json mode', () => {
    const { status, stdout } = run('origin/develop', 'HEAD', '--json')
    expect(status).toBe(0)
    const out = JSON.parse(stdout)
    expect(out.base).toBe('origin/develop')
    expect(out.head).toBe('HEAD')
    expect(out.baseSha).toMatch(/^[0-9a-f]{40}$/)
    expect(out.headSha).toMatch(/^[0-9a-f]{40}$/)
    expect(out.mergeBase).toMatch(/^[0-9a-f]{40}$/)
    expect(out.baseTree).toMatch(/^[0-9a-f]{40}$/)
    expect(out.headTree).toMatch(/^[0-9a-f]{40}$/)
    expect(out.level).toBe('L2')
    expect(out.mechanical.ok).toBe(true)
    expect(out.mechanical.changedFileDigests.length).toBeGreaterThan(0)
    for (const digest of out.mechanical.changedFileDigests) {
      expect(digest.status).toMatch(/^[ADMT]$/)
      if (digest.status === 'D') {
        expect(digest.bytes).toBeNull()
        expect(digest.sha256).toBeNull()
      } else {
        expect(digest.sha256).toMatch(/^[0-9a-f]{64}$/)
      }
    }
    expect(out.mechanical.sourceManifest.ok).toBe(true)
    expect(out.mechanical.sourceManifest.checkedCount).toBeGreaterThan(0)
    expect(out.mechanical.sourceManifest.mismatches).toEqual([])
  })

  it('rejects unknown options and more than two positional args with exit code 2', () => {
    expect(run('--nope').status).toBe(2)
    expect(run('a', 'b', 'c').status).toBe(2)
    expect(run('origin/develop', 'HEAD', '--json', 'extra').status).toBe(2)
  })

  it('fails with a readable error for invalid refs', () => {
    const r = run('no-such-ref', 'HEAD')
    expect(r.status).not.toBe(0)
    expect(r.stderr).toContain('no-such-ref')
    expect(r.stderr).not.toContain('at ')
  })
})

describe('review checklist integrity', () => {
  const checklist = readFileSync(
    new URL('../../docs/process/review-checklist.md', import.meta.url),
    'utf8',
  )
  const body = checklist.slice(checklist.indexOf('## 一、'))
  const items = [...body.matchAll(/^> (.+)$/gm)].map((m) => m[1])
  const fixture = readFileSync(
    new URL('./review-level-checklist-fixture.txt', import.meta.url),
    'utf8',
  )
    .split('\n')
    .filter(Boolean)

  it('keeps all 160 English items verbatim, matching the reviewed version as a set', () => {
    expect(items).toHaveLength(160)
    expect(new Set(items).size).toBe(160)
    expect(fixture).toHaveLength(160)
    expect([...items].sort()).toEqual([...fixture].sort())
  })

  it('keeps section counts at 37 / 84 / 39', () => {
    const count = (s: string) => [...s.matchAll(/^> /gm)].length
    const core = body.slice(0, body.indexOf('## 二、'))
    const modules = body.slice(body.indexOf('## 二、'), body.indexOf('## 三、'))
    const nonApplicable = body.slice(body.indexOf('## 三、'))
    expect(count(core)).toBe(37)
    expect(count(modules)).toBe(84)
    expect(count(nonApplicable)).toBe(39)
  })
})
