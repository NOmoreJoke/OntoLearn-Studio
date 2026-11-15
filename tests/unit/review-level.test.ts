import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import policyJson from '../../.github/review-policy.json'
import {
  IMMUTABLE_L2_PATTERNS,
  bumpKind,
  classifyChange,
  classifyPackageJson,
  classifyPath,
  globToRegExp,
  validateSourceManifest,
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

describe('canonical repo path guard', () => {
  it.each([
    ['./.github/review-policy.json', '前导 ./'],
    ['/etc/passwd', '前导 /'],
    ['scripts\\review-level.mjs', '反斜杠'],
    ['', '空路径'],
    ['a/../b', '.. 段'],
    ['a/./b', '. 段'],
    ['a//b', '空段'],
    ['a/', '尾部斜杠'],
  ])('rejects non-canonical path %s（%s）', (path) => {
    expect(() => classifyPath(path, policy)).toThrow(/Fail-Closed/)
  })

  it('fails closed inside classifyChange as well', () => {
    expect(() => classifyChange([{ path: '../evil.ts' }], policy)).toThrow(/Fail-Closed/)
    expect(() =>
      classifyChange(
        [{ path: 'package.json', base: '{}', head: '{}' }, { path: './uv.lock' }],
        policy,
      ),
    ).toThrow(/Fail-Closed/)
    // 合法相对路径不受影响
    expect(classifyChange([{ path: 'a/b.ts' }], policy).level).toBe('L1')
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
    ['tests/unit/review-level-checklist-fixture.txt', 'L2'],
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

  it('refuses to stringify non-string specs (nested objects, null, undefined)', () => {
    // 嵌套 overrides 对象：禁止 String() 后把两侧都变 "[object Object]" 误判为无变化
    expect(
      bumpKind({ bar: '1.0.0' } as unknown as string, { bar: '2.0.0' } as unknown as string),
    ).toBe('unknown')
    expect(bumpKind(null as unknown as string, '1.0.0')).toBe('unknown')
    expect(bumpKind('1.0.0', undefined as unknown as string)).toBe('unknown')
    expect(bumpKind(['1.0.0'] as unknown as string, ['2.0.0'] as unknown as string)).toBe('unknown')
  })

  it('classifies nested overrides/resolutions object specs recursively and conservatively', () => {
    const nested = (v: string) => JSON.stringify({ overrides: { foo: { bar: v } } })
    // 子条目主版本变化 → L2（Codex R2 反例：原实现误判 L0）
    expect(classifyPackageJson(nested('1.0.0'), nested('2.0.0'), policy).level).toBe('L2')
    // 子条目 0.x 次版本 → L2
    expect(classifyPackageJson(nested('0.3.0'), nested('0.4.0'), policy).level).toBe('L2')
    // 子条目不可解析 spec → L2
    expect(classifyPackageJson(nested('latest'), nested('2.0.0'), policy).level).toBe('L2')
    // 子条目次/补丁版本 → L1（runtime 语义）
    expect(classifyPackageJson(nested('1.0.0'), nested('1.0.1'), policy).level).toBe('L1')
    expect(classifyPackageJson(nested('1.0.0'), nested('1.1.0'), policy).level).toBe('L1')
    // 嵌套键新增/删除（结构变化）→ L2
    expect(
      classifyPackageJson(
        JSON.stringify({ overrides: { foo: { bar: '1.0.0' } } }),
        JSON.stringify({ overrides: { foo: { bar: '1.0.0', baz: '2.0.0' } } }),
        policy,
      ).level,
    ).toBe('L2')
    expect(
      classifyPackageJson(
        JSON.stringify({ overrides: { foo: { bar: '1.0.0', baz: '2.0.0' } } }),
        JSON.stringify({ overrides: { foo: { bar: '1.0.0' } } }),
        policy,
      ).level,
    ).toBe('L2')
    // 对象 → 标量类型切换 → L2
    expect(
      classifyPackageJson(
        JSON.stringify({ overrides: { foo: { bar: '1.0.0' } } }),
        JSON.stringify({ overrides: { foo: '2.0.0' } }),
        policy,
      ).level,
    ).toBe('L2')
    // 嵌套对象纯 key 重排 → 无变化 L0
    expect(
      classifyPackageJson(
        JSON.stringify({ overrides: { foo: { bar: '1.0.0', baz: '2.0.0' } } }),
        JSON.stringify({ overrides: { foo: { baz: '2.0.0', bar: '1.0.0' } } }),
        policy,
      ).level,
    ).toBe('L0')
    // resolutions 同样处理
    const res = (v: string) => JSON.stringify({ resolutions: { foo: { bar: v } } })
    expect(classifyPackageJson(res('1.0.0'), res('2.0.0'), policy).level).toBe('L2')
    expect(
      classifyPackageJson(
        JSON.stringify({ resolutions: { foo: { bar: '1.0.0', baz: '2.0.0' } } }),
        JSON.stringify({ resolutions: { foo: { baz: '2.0.0', bar: '1.0.0' } } }),
        policy,
      ).level,
    ).toBe('L0')
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

  it('never lets a foreign-ecosystem manifest downgrade an unrelated lockfile', () => {
    // Codex R2 反例：package.json 开发依赖 patch 曾把独立改动的 uv.lock 降为 L0
    const npmPatchPlusUv = classifyChange(
      [
        {
          path: 'package.json',
          base: pkg({ foo: '1.0.0' }),
          head: pkg({ foo: '1.0.1' }),
        },
        { path: 'uv.lock' },
      ],
      policy,
    )
    expect(npmPatchPlusUv.files.find((f) => f.path === 'uv.lock')?.level).toBe('L1')
    expect(npmPatchPlusUv.level).toBe('L1')
    // 反向：Python 清单变化不降级 npm 锁文件
    const pyPlusNpmLock = classifyChange(
      [{ path: 'pyproject.toml' }, { path: 'package-lock.json' }],
      policy,
    )
    expect(pyPlusNpmLock.files.find((f) => f.path === 'package-lock.json')?.level).toBe('L1')
    // uv.lock 只有随 pyproject.toml 系清单时才判 L0
    const pyPlusUv = classifyChange([{ path: 'pyproject.toml' }, { path: 'uv.lock' }], policy)
    expect(pyPlusUv.files.find((f) => f.path === 'uv.lock')?.level).toBe('L0')
    expect(pyPlusUv.level).toBe('L2')
    // npm 锁文件仍随 npm 清单
    const npmFollows = classifyChange(
      [
        {
          path: 'package.json',
          base: pkg({ 'typescript-eslint': '8.71.2' }),
          head: pkg({ 'typescript-eslint': '8.71.3' }),
        },
        { path: 'package-lock.json' },
      ],
      policy,
    )
    expect(npmFollows.files.find((f) => f.path === 'package-lock.json')?.level).toBe('L0')
  })

  it('falls back to ecosystem suffix grouping for lockfiles without explicit groups', () => {
    // 未声明 lockfileGroups 时按生态文件名兜底：npm 系只随 package.json 系清单
    const pnpmPolicy: ReviewPolicy = {
      ...policy,
      dependencies: { manifests: ['package.json'], lockfiles: ['pnpm-lock.yaml'], critical: [] },
    }
    const follows = classifyChange(
      [
        {
          path: 'package.json',
          base: pkg({ foo: '1.0.0' }),
          head: pkg({ foo: '1.0.1' }),
        },
        { path: 'pnpm-lock.yaml' },
      ],
      pnpmPolicy,
    )
    expect(follows.files.find((f) => f.path === 'pnpm-lock.yaml')?.level).toBe('L0')
    // uv 生态兜底：uv.lock 只随 pyproject.toml，npm 清单无法降级它
    const uvPolicy: ReviewPolicy = {
      ...policy,
      dependencies: {
        manifests: ['package.json', 'pyproject.toml'],
        lockfiles: ['uv.lock'],
        critical: [],
      },
    }
    const npmOnly = classifyChange(
      [
        {
          path: 'package.json',
          base: pkg({ foo: '1.0.0' }),
          head: pkg({ foo: '1.0.1' }),
        },
        { path: 'uv.lock' },
      ],
      uvPolicy,
    )
    expect(npmOnly.files.find((f) => f.path === 'uv.lock')?.level).toBe('L1')
    const pyOnly = classifyChange([{ path: 'pyproject.toml' }, { path: 'uv.lock' }], uvPolicy)
    expect(pyOnly.files.find((f) => f.path === 'uv.lock')?.level).toBe('L0')
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
    'tests/unit/review-level-checklist-fixture.txt',
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

  it('keeps the checklist fixture at L2 even when a hostile policy targets it for downgrade', () => {
    const fixtureHostile: ReviewPolicy = {
      version: 1,
      defaultLevel: 'L0',
      rules: [
        {
          level: 'L0',
          reason: '敌意策略试图将清单 fixture 降为 L0',
          paths: ['tests/unit/review-level-checklist-fixture.txt'],
        },
      ],
    }
    expect(
      classifyChange([{ path: 'tests/unit/review-level-checklist-fixture.txt' }], fixtureHostile)
        .level,
    ).toBe('L2')
  })

  it('exposes the immutable floor patterns', () => {
    expect(IMMUTABLE_L2_PATTERNS).toContain('.github/review-policy.json')
    expect(IMMUTABLE_L2_PATTERNS).toContain('scripts/review-level*')
    expect(IMMUTABLE_L2_PATTERNS).toContain('tests/unit/review-level*')
    expect(IMMUTABLE_L2_PATTERNS).toContain('.github/workflows/**')
    expect(IMMUTABLE_L2_PATTERNS).toContain('packages/contracts/**')
    expect(IMMUTABLE_L2_PATTERNS).toContain('docs/prd/**')
  })
})

describe('source manifest evidence schema validation', () => {
  const sha = 'a'.repeat(64)

  it('accepts a well-formed manifest with hex digests', () => {
    const valid = {
      files: [
        { path: 'scripts/a.py', sha256: sha },
        { path: 'b.ts', sha256: 'B'.repeat(64) },
      ],
    }
    expect(validateSourceManifest(valid).files).toHaveLength(2)
  })

  it.each([
    ['空对象 {}', {}],
    ['files 缺失', { entries: [] }],
    ['files 空数组', { files: [] }],
    ['null', null],
    ['数组', []],
    ['字符串', 'x'],
    ['entry 非对象', { files: ['a'] }],
    ['entry null', { files: [null] }],
    ['path 为空', { files: [{ path: '', sha256: sha }] }],
    ['path 非法（../）', { files: [{ path: '../a', sha256: sha }] }],
    ['path 非法（前导 /）', { files: [{ path: '/a', sha256: sha }] }],
    ['sha 长度不足', { files: [{ path: 'a', sha256: 'abc123' }] }],
    ['sha 非十六进制', { files: [{ path: 'a', sha256: 'z'.repeat(64) }] }],
    ['sha 缺失', { files: [{ path: 'a' }] }],
  ])('fails closed on %s', (_label, manifest) => {
    expect(() => validateSourceManifest(manifest)).toThrow(/Fail-Closed/)
  })
})

describe('review level CLI', () => {
  const ROOT = fileURLToPath(new URL('../..', import.meta.url))
  // 共享隔离环境构建器：先按大小写无关剔除全部 GIT_* 变量（拦截 Windows/大小写混合的
  // Git_Dir、git_work_tree、Git_Index_File 等），再显式注入测试隔离 Git 配置（空的
  // global/system 配置 + 禁用系统配置 + 禁用终端提示），防止宿主 worktree/hook/全局配置
  // 泄漏进临时仓库，保证 CLI 与其内部 git 调用只作用于 tempRepo。
  const buildIsolatedGitEnv = (
    sourceEnv: NodeJS.ProcessEnv,
    emptyGitConfigPath: string,
  ): NodeJS.ProcessEnv => ({
    ...Object.fromEntries(
      Object.entries(sourceEnv).filter(([key]) => !key.toUpperCase().startsWith('GIT_')),
    ),
    GIT_CONFIG_GLOBAL: emptyGitConfigPath,
    GIT_CONFIG_SYSTEM: emptyGitConfigPath,
    GIT_CONFIG_NOSYSTEM: '1',
    GIT_TERMINAL_PROMPT: '0',
  })
  let fixtureRoot = ''
  let tempRepo = ''
  let emptyGitConfig = ''
  let emptyHooksDir = ''
  let isolatedEnv: NodeJS.ProcessEnv = {}
  let baseSha = ''
  let baseTree = ''
  let l1Sha = ''
  let l1Tree = ''
  let l2PolicySha = ''
  let l2PolicyTree = ''

  const git = (...args: string[]) =>
    execFileSync('git', args, { cwd: tempRepo, env: isolatedEnv, encoding: 'utf8' })
  const run = (...cliArgs: string[]) => {
    try {
      const stdout = execFileSync(
        process.execPath,
        [resolve(ROOT, 'scripts/review-level.mjs'), ...cliArgs],
        { cwd: tempRepo, env: isolatedEnv, encoding: 'utf8' },
      )
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
  const writeUnder =
    (repoRoot: string) =>
    (relPath: string, content: string): void => {
      const target = join(repoRoot, relPath)
      mkdirSync(join(target, '..'), { recursive: true })
      writeFileSync(target, content)
    }

  beforeAll(() => {
    // 夹具根目录统一收纳临时仓库/空配置/空 hooks，afterAll 一次性清理
    fixtureRoot = mkdtempSync(join(tmpdir(), 'review-level-cli-'))
    tempRepo = join(fixtureRoot, 'repo')
    mkdirSync(tempRepo, { recursive: true })
    emptyGitConfig = join(fixtureRoot, 'empty.gitconfig')
    writeFileSync(emptyGitConfig, '')
    emptyHooksDir = join(fixtureRoot, 'empty-hooks')
    mkdirSync(emptyHooksDir, { recursive: true })
    isolatedEnv = buildIsolatedGitEnv(process.env, emptyGitConfig)
    // --template= 禁用宿主 init.templateDir，避免宿主模板（含 hooks 样例）复制进临时仓库
    git('init', '--template=')
    git('config', 'user.name', 'test')
    git('config', 'user.email', 'test@example.com')
    git('config', 'commit.gpgsign', 'false')
    git('config', 'core.hooksPath', emptyHooksDir)
    git('config', 'core.autocrlf', 'false')
    const write = writeUnder(tempRepo)

    // base：真实策略文件 + manifest 覆盖的 README/docs/guide.md + 待删除文件 + 与内容一致的 source-manifest
    write(
      '.github/review-policy.json',
      readFileSync(resolve(ROOT, '.github/review-policy.json'), 'utf8'),
    )
    write('README.md', 'hello\n')
    write('docs/guide.md', 'guide\n')
    write('obsolete.txt', 'remove-me\n')
    write(
      'docs/source-manifest.json',
      `${JSON.stringify(
        {
          version: 1,
          files: [
            { path: 'README.md', sha256: createHash('sha256').update('hello\n').digest('hex') },
            { path: 'docs/guide.md', sha256: createHash('sha256').update('guide\n').digest('hex') },
          ],
        },
        null,
        2,
      )}\n`,
    )
    git('add', '.')
    git('commit', '-m', 'base')
    baseSha = git('rev-parse', 'HEAD').trim()
    baseTree = git('rev-parse', 'HEAD^{tree}').trim()
    // 即使 CI 浅克隆（fetch-depth: 1）也能解析默认 origin/develop 基线
    git('update-ref', 'refs/remotes/origin/develop', baseSha)

    // L1：非策略的渲染层前端变更
    write('apps/desktop/src/renderer/src/App.tsx', 'export const App = () => null\n')
    git('add', '.')
    git('commit', '-m', 'l1 frontend')
    l1Sha = git('rev-parse', 'HEAD').trim()
    l1Tree = git('rev-parse', 'HEAD^{tree}').trim()

    // L2（HEAD）：覆盖删除分支（status === 'D'）与策略文档路径（POLICY_OR_CLASSIFIER_PATHS 与 L2 硬底线）
    git('rm', 'obsolete.txt')
    write('docs/process/review-policy.md', '# Review Policy\n')
    git('add', '.')
    git('commit', '-m', 'l2 policy')
    l2PolicySha = git('rev-parse', 'HEAD').trim()
    l2PolicyTree = git('rev-parse', 'HEAD^{tree}').trim()
  })

  afterAll(() => {
    // maxRetries/retryDelay 兼顾 Windows 上文件句柄延迟释放导致的清理失败
    rmSync(fixtureRoot, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 })
  })

  it('emits L0 with empty mechanical evidence for identical refs', () => {
    const { status, stdout } = run(baseSha, baseSha, '--json')
    expect(status).toBe(0)
    const out = JSON.parse(stdout)
    expect(out.level).toBe('L0')
    expect(out.mechanical.ok).toBe(true)
    expect(out.mechanical.changedFileDigests).toEqual([])
    expect(out.selfCheck.policyOrClassifierTouched).toBe(false)
    // 精确 SHA/tree 断言：同一 ref 两侧的 SHA 与 tree 必须逐位等于夹具提交
    expect(out.baseSha).toBe(baseSha)
    expect(out.headSha).toBe(baseSha)
    expect(out.mergeBase).toBe(baseSha)
    expect(out.baseTree).toBe(baseTree)
    expect(out.headTree).toBe(baseTree)
  })

  it('emits L1 with per-file digests for non-policy frontend change', () => {
    const { status, stdout } = run(baseSha, l1Sha, '--json')
    expect(status).toBe(0)
    const out = JSON.parse(stdout)
    expect(out.level).toBe('L1')
    expect(out.mechanical.ok).toBe(true)
    expect(out.selfCheck.policyOrClassifierTouched).toBe(false)
    // 精确 SHA/tree 断言：基线即 base 提交，head 即 l1 提交
    expect(out.baseSha).toBe(baseSha)
    expect(out.headSha).toBe(l1Sha)
    expect(out.mergeBase).toBe(baseSha)
    expect(out.baseTree).toBe(baseTree)
    expect(out.headTree).toBe(l1Tree)
    let sawAppTsx = false
    for (const digest of out.mechanical.changedFileDigests) {
      expect(digest.status).toMatch(/^[ADMT]$/)
      if (digest.path !== 'apps/desktop/src/renderer/src/App.tsx') continue
      sawAppTsx = true
      expect(digest.status).toBe('A')
      expect(digest.sha256).toMatch(/^[0-9a-f]{64}$/)
    }
    expect(sawAppTsx).toBe(true)
  })

  it('defaults to origin/develop..HEAD and emits binding and mechanical evidence in --json mode', () => {
    const { status, stdout } = run('--json')
    expect(status).toBe(0)
    const out = JSON.parse(stdout)
    expect(out.base).toBe('origin/develop')
    expect(out.head).toBe('HEAD')
    expect(out.baseSha).toMatch(/^[0-9a-f]{40}$/)
    expect(out.headSha).toMatch(/^[0-9a-f]{40}$/)
    expect(out.mergeBase).toMatch(/^[0-9a-f]{40}$/)
    expect(out.baseTree).toMatch(/^[0-9a-f]{40}$/)
    expect(out.headTree).toMatch(/^[0-9a-f]{40}$/)
    // 精确 SHA/tree 断言：origin/develop 即 base 提交，HEAD 即 l2 提交
    expect(out.baseSha).toBe(baseSha)
    expect(out.headSha).toBe(l2PolicySha)
    expect(out.mergeBase).toBe(baseSha)
    expect(out.baseTree).toBe(baseTree)
    expect(out.headTree).toBe(l2PolicyTree)
    expect(out.level).toBe('L2')
    expect(out.mechanical.ok).toBe(true)
    expect(out.mechanical.sourceManifest.ok).toBe(true)
    // manifest 覆盖 README.md 与 docs/guide.md 两条受控文件，覆盖多条目循环
    expect(out.mechanical.sourceManifest.checkedCount).toBe(2)
    expect(out.mechanical.sourceManifest.mismatches).toEqual([])
    let sawDelete = false
    let sawNonDelete = false
    for (const digest of out.mechanical.changedFileDigests) {
      expect(digest.status).toMatch(/^[ADMT]$/)
      if (digest.status === 'D') {
        sawDelete = true
        expect(digest.bytes).toBeNull()
        expect(digest.sha256).toBeNull()
      } else {
        sawNonDelete = true
        expect(digest.sha256).toMatch(/^[0-9a-f]{64}$/)
      }
    }
    expect(sawDelete).toBe(true)
    expect(sawNonDelete).toBe(true)
    // 自检元信息：本候选触及策略/分级器路径 → G0 后必须以可信基线脚本执行分级
    expect(out.selfCheck.policyOrClassifierTouched).toBe(true)
    expect(out.selfCheck.trustedBaselineRule).toBe('run_from_trusted_base_after_g0')
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

  it('stays hermetic against hostile mixed-case GIT_* vars and a rejecting global hooks config', () => {
    // 动态隔离回归：宿主环境携带大小写混合 GIT_* 变量（Git_Dir/git_work_tree/Git_Index_File）
    // 与恶意 GIT_CONFIG_GLOBAL（拒绝型 pre-commit hook + 敌意 user 配置）时，隔离器必须
    // 剥离全部污染项，夹具提交（敌意 hook 未执行）与 CLI L0 输出均成功且 SHA 精确等于子仓库提交。
    const hostileRoot = mkdtempSync(join(tmpdir(), 'review-level-cli-hostile-'))
    try {
      const hostileRepo = join(hostileRoot, 'repo')
      mkdirSync(hostileRepo, { recursive: true })
      const rejectHooksDir = join(hostileRoot, 'reject-hooks')
      mkdirSync(rejectHooksDir, { recursive: true })
      // 拒绝型 pre-commit hook：一旦敌意全局配置泄漏，任何提交都会被其以非零码拒绝
      const preCommit = join(rejectHooksDir, 'pre-commit')
      writeFileSync(preCommit, '#!/bin/sh\nexit 1\n')
      if (process.platform !== 'win32') chmodSync(preCommit, 0o755)
      const hostileGitConfig = join(hostileRoot, 'hostile.gitconfig')
      writeFileSync(
        hostileGitConfig,
        `[user]\n\tname = hostile-ignored\n[core]\n\thooksPath = ${rejectHooksDir}\n`,
      )
      const hostileHostEnv: NodeJS.ProcessEnv = {
        ...process.env,
        Git_Dir: '/nonexistent/hostile-git-dir',
        git_work_tree: '/nonexistent/hostile-work-tree',
        Git_Index_File: '/nonexistent/hostile-index',
        GIT_CONFIG_GLOBAL: hostileGitConfig,
      }
      const hostileEnv = buildIsolatedGitEnv(hostileHostEnv, emptyGitConfig)
      // 构建器必须剥离大小写混合变量并覆盖恶意全局配置
      expect(hostileEnv.Git_Dir).toBeUndefined()
      expect(hostileEnv.git_work_tree).toBeUndefined()
      expect(hostileEnv.Git_Index_File).toBeUndefined()
      expect(hostileEnv.GIT_CONFIG_GLOBAL).toBe(emptyGitConfig)
      const hostileGit = (...args: string[]) =>
        execFileSync('git', args, { cwd: hostileRepo, env: hostileEnv, encoding: 'utf8' })
      const hostileRun = (...cliArgs: string[]) => {
        try {
          const stdout = execFileSync(
            process.execPath,
            [resolve(ROOT, 'scripts/review-level.mjs'), ...cliArgs],
            { cwd: hostileRepo, env: hostileEnv, encoding: 'utf8' },
          )
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
      hostileGit('init', '--template=')
      hostileGit('config', 'user.name', 'test')
      hostileGit('config', 'user.email', 'test@example.com')
      hostileGit('config', 'commit.gpgsign', 'false')
      // 故意不设置本地 core.hooksPath：若敌意 GIT_CONFIG_GLOBAL 泄漏，上面的 pre-commit
      // 将接管提交并退出非零，hostileGit('commit') 会直接抛错使本用例失败
      const write = writeUnder(hostileRepo)
      write(
        '.github/review-policy.json',
        readFileSync(resolve(ROOT, '.github/review-policy.json'), 'utf8'),
      )
      write('README.md', 'hello\n')
      write(
        'docs/source-manifest.json',
        `${JSON.stringify(
          {
            version: 1,
            files: [
              { path: 'README.md', sha256: createHash('sha256').update('hello\n').digest('hex') },
            ],
          },
          null,
          2,
        )}\n`,
      )
      hostileGit('add', '.')
      hostileGit('commit', '-m', 'hostile base')
      const hostileSha = hostileGit('rev-parse', 'HEAD').trim()
      const { status, stdout } = hostileRun(hostileSha, hostileSha, '--json')
      expect(status).toBe(0)
      const out = JSON.parse(stdout)
      expect(out.level).toBe('L0')
      expect(out.baseSha).toBe(hostileSha)
      expect(out.headSha).toBe(hostileSha)
    } finally {
      rmSync(hostileRoot, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 })
    }
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
