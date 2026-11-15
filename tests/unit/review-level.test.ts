import { describe, expect, it } from 'vitest'
import policyJson from '../../.github/review-policy.json'
import {
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

describe('review level glob', () => {
  it('matches ** across directories and * within one segment', () => {
    expect(globToRegExp('apps/desktop/src/main/**').test('apps/desktop/src/main/a/b.ts')).toBe(true)
    expect(globToRegExp('scripts/verify-*').test('scripts/verify-sources.mjs')).toBe(true)
    expect(globToRegExp('scripts/verify-*').test('scripts/sub/verify-x')).toBe(false)
    expect(globToRegExp('docs/verification*').test('docs/verification-2026-10-19.md')).toBe(true)
  })
})

describe('review level path rules', () => {
  it.each([
    ['apps/desktop/src/main/window-security.ts', 'L2'],
    ['apps/desktop/src/preload/index.ts', 'L2'],
    ['packages/contracts/src/v2.ts', 'L2'],
    ['packages/engine/src/ontolearn_engine/storage.py', 'L2'],
    ['scripts/verify-sources.mjs', 'L2'],
    ['.github/review-policy.json', 'L2'],
    ['docs/process/review-checklist.md', 'L2'],
    ['scripts/review-level-core.mjs', 'L2'],
    ['docs/prd/PRD.md', 'L2'],
    ['apps/desktop/src/renderer/App.tsx', 'L1'],
    ['tests/unit/csp.test.ts', 'L1'],
    ['packages/engine/tests/test_storage.py', 'L1'],
    ['.github/workflows/ci.yml', 'L1'],
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
  it('classifies semver bumps', () => {
    expect(bumpKind('5.9.3', '7.0.2')).toBe('major')
    expect(bumpKind('26.15.3', '26.18.0')).toBe('minor')
    expect(bumpKind('^8.71.2', '^8.71.3')).toBe('patch')
    expect(bumpKind('0.3.0', '0.4.0')).toBe('major')
    expect(bumpKind('latest', '1.0.0')).toBe('unknown')
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
    expect(classifyPackageJson('{', '{}', policy).level).toBe('L1')
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
})
