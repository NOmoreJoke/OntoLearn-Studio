import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import {
  applyTriageDecisions,
  classifyCandidate,
  classifyChange,
  completionClaim,
  completionClaimOutsideStatusDocument,
  dependencyChanges,
  lockMatchesManifest,
  lockVersionDelta,
  manifestNonDependencyChanges,
  semverOf,
  tautologySuspicion,
  workflowChangeKind,
  type ChangeInput,
} from '../../scripts/lib/classify.mjs'
import { parsePolicyText } from '../../scripts/lib/review-policy.mjs'

const policy = parsePolicyText(readFileSync('.github/review-policy.yml', 'utf8'), 'policy')
const encoder = new TextEncoder()
const enc = (text: string) => encoder.encode(text)

function change(partial: Partial<ChangeInput> & { path: string }): ChangeInput {
  return {
    status: 'M',
    oldMode: '100644',
    newMode: '100644',
    beforeBytes: enc('before\n'),
    afterBytes: enc('after\n'),
    gitIgnoreableWhitespace: false,
    provenFormat: { proven: false, reason: 'none' },
    ...partial,
  }
}

const plainCtx = { policy }

describe('semverOf 严格锚定（W06）', () => {
  it('接受范围前缀与精确语义化版本', () => {
    expect(semverOf('44.9.0')).toEqual({ major: 44, minor: 9, patch: 0 })
    expect(semverOf('^1.2.3')).toEqual({ major: 1, minor: 2, patch: 3 })
    expect(semverOf('~0.1.2')).toEqual({ major: 0, minor: 1, patch: 2 })
  })
  it('拒绝 workspace/tag/git/含版本号的任意字符串', () => {
    expect(semverOf('workspace:*')).toBeNull()
    expect(semverOf('next')).toBeNull()
    expect(semverOf('git+https://example.com/repo.git#v1.2.3')).toBeNull()
    expect(semverOf('electron-with-built-in-version-44.9.0')).toBeNull()
  })
})

describe('manifest 非依赖字段与依赖区（W06）', () => {
  const base = JSON.stringify({
    name: 'app',
    scripts: { build: 'vite build' },
    devDependencies: { electron: '44.9.0', typescript: '5.9.3' },
  })
  it('仅 devDependencies patch 变化时非依赖字段清单为空', () => {
    const next = JSON.stringify({
      name: 'app',
      scripts: { build: 'vite build' },
      devDependencies: { electron: '44.9.1', typescript: '5.9.3' },
    })
    expect(manifestNonDependencyChanges(base, next)).toEqual([])
    const deps = dependencyChanges(base, next) ?? []
    expect(
      deps.every((entry) => entry.bump === 'patch' && entry.section === 'devDependencies'),
    ).toBe(true)
  })
  it('依赖 patch 混入 scripts 变化时非依赖字段被检出', () => {
    const next = JSON.stringify({
      name: 'app',
      scripts: { build: 'vite build && echo packed' },
      devDependencies: { electron: '44.9.1', typescript: '5.9.3' },
    })
    expect(manifestNonDependencyChanges(base, next)).toEqual(['scripts'])
  })
})

describe('lock 差异与 manifest 一致性（W06）', () => {
  const lockBefore = JSON.stringify({
    packages: {
      '': { name: 'app', devDependencies: { electron: '44.9.0' } },
      'node_modules/electron': { version: '44.9.0' },
      'node_modules/typescript': { version: '5.9.3' },
    },
  })
  const manifestDeps = [
    { name: 'electron', section: 'devDependencies', from: '44.9.0', to: '44.9.1', bump: 'patch' },
  ]
  it('锁文件差异与 manifest bump 完全一致时通过', () => {
    const lockAfter = JSON.stringify({
      packages: {
        '': { name: 'app', devDependencies: { electron: '44.9.1' } },
        'node_modules/electron': { version: '44.9.1' },
        'node_modules/typescript': { version: '5.9.3' },
      },
    })
    const delta = lockVersionDelta(lockBefore, lockAfter)
    expect(lockMatchesManifest(delta, manifestDeps)).toBe(true)
  })
  it('锁文件夹带 manifest 之外的额外版本变化时不通过', () => {
    const lockAfter = JSON.stringify({
      packages: {
        '': { name: 'app', devDependencies: { electron: '44.9.1' } },
        'node_modules/electron': { version: '44.9.1' },
        'node_modules/typescript': { version: '5.10.0' },
      },
    })
    expect(lockMatchesManifest(lockVersionDelta(lockBefore, lockAfter), manifestDeps)).toBe(false)
  })
})

describe('workflow 变更分档（W08）', () => {
  const before =
    'jobs:\n  quality:\n    steps:\n      - uses: actions/checkout@aaa111\n      - run: npm run check\n'
  it('仅 actions pin 升级（uses 行变化）视为低风险', () => {
    const after = before.replace('@aaa111', '@bbb222')
    expect(workflowChangeKind(before, after)).toBe('actions-pin-only')
  })
  it('仅新增 uses 行也是 pin 变化', () => {
    const after = before.replace(
      '      - run: npm run check',
      '      - run: npm run check\n      - uses: actions/setup-node@ccc333',
    )
    expect(workflowChangeKind(before, after)).toBe('actions-pin-only')
  })
  it('新增 if: false 或 continue-on-error 是禁用条件', () => {
    const withIfFalse = before.replace('    steps:', '    if: false\n    steps:')
    expect(workflowChangeKind(before, withIfFalse)).toBe('job-disabling-condition')
    const withContinue = before.replace('    steps:', '    continue-on-error: true\n    steps:')
    expect(workflowChangeKind(before, withContinue)).toBe('job-disabling-condition')
  })
  it('其它内容性变更是 content-change（未证明安全）', () => {
    const after = before.replace('npm run check', 'npm run lint')
    expect(workflowChangeKind(before, after)).toBe('content-change')
  })
})

describe('完成声明检测（W12）', () => {
  it('checkbox 翻转构成完成声明', () => {
    const result = completionClaim('- [ ] I01\n- [ ] I02\n', '- [ ] I01\n- [x] I02\n')
    expect(result.claimed).toBe(true)
  })
  it('状态文档新增完成措辞构成完成声明', () => {
    const result = completionClaim('# 状态\n', '# 状态\n\nI04 已完成并验收。\n')
    expect(result.claimed).toBe(true)
  })
  it('普通文档新增 FR 完成措辞触发外部完成声明（不得自动 L0）', () => {
    const result = completionClaimOutsideStatusDocument('# 验证\n', '# 验证\n\nFR-003 验收通过。\n')
    expect(result.claimed).toBe(true)
  })
  it('发布候选措辞在普通文档同样触发', () => {
    const result = completionClaimOutsideStatusDocument(
      '# 说明\n',
      '# 说明\n\n本版本为 release candidate。\n',
    )
    expect(result.claimed).toBe(true)
  })
  it('普通行编辑不触发', () => {
    const result = completionClaimOutsideStatusDocument('# 说明\n', '# 说明\n\n补充一段背景。\n')
    expect(result.claimed).toBe(false)
  })
})

describe('恒真断言嫌疑（W08）', () => {
  it('真实断言被替换为恒真断言时检出（数量不变）', () => {
    const before = "test('flow', () => {\n  expect(records.length).toBe(2)\n})\n"
    const after = "test('flow', () => {\n  expect(true).toBe(true)\n})\n"
    expect(tautologySuspicion(before, after)).toBe(true)
  })
  it('正常新增断言不触发', () => {
    const before = 'test("a", () => {\n  expect(1).toBe(1)\n})\n'
    const after = 'test("a", () => {\n  expect(1).toBe(1)\n  expect(2).toBe(2)\n})\n'
    expect(tautologySuspicion(before, after)).toBe(false)
  })
})

describe('classifyChange 关键反例', () => {
  it('csp.ts 实质变更是 semantic-proof L2', () => {
    const result = classifyChange(
      change({
        path: 'apps/desktop/src/csp.ts',
        beforeBytes: enc('export const csp = "default-src \'self\'"\n'),
        afterBytes: enc('export const csp = "default-src \'self\' https:"\n'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.basis).toBe('semantic-proof')
  })
  it('engine 源码实质变更是 path-hint L2（可被可信决策定级，W09）', () => {
    const result = classifyChange(
      change({ path: 'packages/engine/src/ontolearn_engine/engine.py' }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.basis).toBe('path-hint')
  })
  it('main 文件 CRLF→LF 规范化是机器证明的 L0', () => {
    const result = classifyChange(
      change({
        path: 'apps/desktop/src/main/index.ts',
        beforeBytes: enc('console.log(1)\r\n'),
        afterBytes: enc('console.log(1)\n'),
        gitIgnoreableWhitespace: true,
        provenFormat: proven('line-ending-only(cr-removed=1,cr-added=0)'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L0')
  })
  it('main 文件缩进变化（-w 可忽略但未证明）不能 L0，按路径保守 L2', () => {
    const result = classifyChange(
      change({
        path: 'apps/desktop/src/main/index.ts',
        beforeBytes: enc('function a() {\n    return 1\n}\n'),
        afterBytes: enc('function a() {\n  return 1\n}\n'),
        gitIgnoreableWhitespace: true,
      }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.basis).toBe('path-hint')
  })
  it('模式变化（可执行位）使 CR 证明失效（W11）', () => {
    const result = classifyChange(
      change({
        path: 'apps/desktop/src/main/index.ts',
        oldMode: '100644',
        newMode: '100755',
        beforeBytes: enc('console.log(1)\r\n'),
        afterBytes: enc('console.log(1)\n'),
        gitIgnoreableWhitespace: true,
        provenFormat: proven('line-ending-only'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.reasons.join(' ')).toContain('mode-change')
  })
  it('二进制内容（含 NUL）的 CR 类字节变化不获证明（W11）', () => {
    const beforeBytes = new Uint8Array([0x61, 0x0d, 0x0a, 0x00, 0x62])
    const afterBytes = new Uint8Array([0x61, 0x0a, 0x00, 0x62])
    const result = classifyChange(
      change({
        path: 'build/binary-artifact.bin',
        beforeBytes,
        afterBytes,
        provenFormat: proven('line-ending-only'),
      }),
      plainCtx,
    )
    expect(result.level).not.toBe('L0')
  })
  it('engine/tests 新增用例在 tests-only 候选中是 L1（不被 engine 通配吞并）', () => {
    const ctx = { ...plainCtx, testsOnlyCandidate: true }
    const result = classifyChange(
      change({
        path: 'packages/engine/tests/test_query.py',
        status: 'A',
        beforeBytes: null,
        afterBytes: enc('def test_query():\n    assert q() == []\n'),
      }),
      ctx,
    )
    expect(result.level).toBe('L1')
  })
  it('conftest 修改不继承 tests-only 例外（W08）', () => {
    const ctx = { ...plainCtx, testsOnlyCandidate: true }
    const result = classifyChange(
      change({
        path: 'packages/engine/tests/conftest.py',
        beforeBytes: enc('def fixture():\n    return 1\n'),
        afterBytes: enc('def fixture():\n    return 2\n'),
      }),
      ctx,
    )
    expect(result.level).toBe('needs_triage')
  })
  it('e2e 删除断言（宣称 tests-only）转 needs_triage', () => {
    const ctx = { ...plainCtx, testsOnlyCandidate: true }
    const result = classifyChange(
      change({
        path: 'tests/e2e/flow.spec.ts',
        beforeBytes: enc(
          "test('flow', () => {\n  expect(count).toBe(3)\n  expect(state).toBe('ok')\n})\n",
        ),
        afterBytes: enc("test('flow', () => {\n  expect(count).toBe(3)\n})\n"),
      }),
      ctx,
    )
    expect(result.level).toBe('needs_triage')
  })
  it('Electron devDependency major 是 semantic-proof L2（不因 devDependencies 降级）', () => {
    const before = JSON.stringify({ devDependencies: { electron: '44.9.0' } })
    const after = JSON.stringify({ devDependencies: { electron: '45.0.0' } })
    const result = classifyChange(
      change({ path: 'package.json', beforeBytes: enc(before), afterBytes: enc(after) }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.basis).toBe('semantic-proof')
    expect(result.reasons.join(' ')).toContain('dependency-major:electron')
  })
  it('electron-builder minor 是 L1 且要求包验证', () => {
    const before = JSON.stringify({ devDependencies: { 'electron-builder': '26.15.3' } })
    const after = JSON.stringify({ devDependencies: { 'electron-builder': '26.16.0' } })
    const result = classifyChange(
      change({ path: 'package.json', beforeBytes: enc(before), afterBytes: enc(after) }),
      plainCtx,
    )
    expect(result.level).toBe('L1')
    expect(result.flags.packageValidationRequired).toBe(true)
  })
  it('devDependency patch 且无其它字段变化是 L0', () => {
    const before = JSON.stringify({
      scripts: { build: 'vite' },
      devDependencies: { typescript: '5.9.3' },
    })
    const after = JSON.stringify({
      scripts: { build: 'vite' },
      devDependencies: { typescript: '5.9.4' },
    })
    const result = classifyChange(
      change({ path: 'package.json', beforeBytes: enc(before), afterBytes: enc(after) }),
      plainCtx,
    )
    expect(result.level).toBe('L0')
  })
  it('devDependency patch 混入 scripts 变化转 needs_triage（W06）', () => {
    const before = JSON.stringify({
      scripts: { build: 'vite' },
      devDependencies: { typescript: '5.9.3' },
    })
    const after = JSON.stringify({
      scripts: { build: 'vite && node evil.js' },
      devDependencies: { typescript: '5.9.4' },
    })
    const result = classifyChange(
      change({ path: 'package.json', beforeBytes: enc(before), afterBytes: enc(after) }),
      plainCtx,
    )
    expect(result.level).toBe('needs_triage')
    expect(result.reasons.join(' ')).toContain('manifest-non-dependency-fields-changed')
  })
  it('锁文件与 manifest 一致时跟随依赖等级', () => {
    const result = classifyChange(change({ path: 'package-lock.json' }), {
      ...plainCtx,
      lockMatchesManifest: true,
      dependencyBumpLevel: 'L0',
      dependencyBumpReason: 'typescript:devDependencies:patch',
    })
    expect(result.level).toBe('L0')
  })
  it('锁文件单独变更（无 manifest 变化）转 needs_triage', () => {
    const result = classifyChange(change({ path: 'package-lock.json' }), plainCtx)
    expect(result.level).toBe('needs_triage')
  })
  it('pyproject/uv.lock 变更保守 needs_triage（W06）', () => {
    expect(classifyChange(change({ path: 'pyproject.toml' }), plainCtx).level).toBe('needs_triage')
    expect(classifyChange(change({ path: 'uv.lock' }), plainCtx).level).toBe('needs_triage')
  })
  it('状态文档 checkbox 结算是 semantic-proof L2', () => {
    const result = classifyChange(
      change({
        path: 'docs/m0-checklist.md',
        beforeBytes: enc('- [ ] I01 存储切片\n'),
        afterBytes: enc('- [x] I01 存储切片\n'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.basis).toBe('semantic-proof')
  })
  it('普通文档 FR 完成声明不得 L0，转 needs_triage（W12）', () => {
    const result = classifyChange(
      change({
        path: 'docs/verification/fr-completion.md',
        status: 'A',
        beforeBytes: null,
        afterBytes: enc('# 记录\n\nFR-003 验收通过。\n'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('needs_triage')
  })
  it('source-manifest.json 不是 L0（权威生成物）', () => {
    const result = classifyChange(change({ path: 'docs/source-manifest.json' }), plainCtx)
    expect(result.level).toBe('L1')
    expect(result.flags.requiresSourceVerification).toBe(true)
  })
  it('workflow 内容性变更转 needs_triage（不因"未匹配削弱关键词"放行）', () => {
    const result = classifyChange(
      change({
        path: '.github/workflows/ci.yml',
        beforeBytes: enc('jobs:\n  quality:\n    steps:\n      - run: npm run check\n'),
        afterBytes: enc(
          'jobs:\n  quality:\n    steps:\n      - run: npm run check\n      - run: echo done\n',
        ),
      }),
      plainCtx,
    )
    expect(result.level).toBe('needs_triage')
  })
  it('必需验证步骤被替换（check→lint）判削弱 L2', () => {
    const result = classifyChange(
      change({
        path: '.github/workflows/ci.yml',
        beforeBytes: enc('jobs:\n  quality:\n    steps:\n      - run: npm run check\n'),
        afterBytes: enc('jobs:\n  quality:\n    steps:\n      - run: npm run lint\n'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.basis).toBe('semantic-proof')
  })
  it('政策删除 L2 语义规则被检出为削弱（semantic-proof L2）', () => {
    const before = JSON.stringify({
      semantic_rules: { L2: ['a', 'b'] },
      validation: { full_ci: ['Quality'] },
    })
    const after = JSON.stringify({
      semantic_rules: { L2: ['a'] },
      validation: { full_ci: ['Quality'] },
    })
    const result = classifyChange(
      change({
        path: '.github/review-policy.yml',
        beforeBytes: enc(before),
        afterBytes: enc(after),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
    expect(result.basis).toBe('semantic-proof')
  })
  it('无提示路径 needs_triage', () => {
    expect(classifyChange(change({ path: 'unknown/random.txt' }), plainCtx).level).toBe(
      'needs_triage',
    )
  })
  it('renderer 触及 IPC 语义是 semantic-proof L2', () => {
    const result = classifyChange(
      change({
        path: 'apps/desktop/src/renderer/App.tsx',
        beforeBytes: enc('const r = await window.api.query()\n'),
        afterBytes: enc('const r = await window.api.queryAll()\n'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L2')
  })
  it('renderer 普通改动按提示 L1', () => {
    const result = classifyChange(
      change({
        path: 'apps/desktop/src/renderer/App.tsx',
        beforeBytes: enc('<main>hello</main>\n'),
        afterBytes: enc('<main>hello world</main>\n'),
      }),
      plainCtx,
    )
    expect(result.level).toBe('L1')
  })
})

describe('候选级组合与人工决策（W07/W09）', () => {
  const renderer = change({
    path: 'apps/desktop/src/renderer/App.tsx',
    beforeBytes: enc('<main>a</main>\n'),
    afterBytes: enc('<main>b</main>\n'),
  })
  const preload = change({
    path: 'apps/desktop/src/preload/bridge.ts',
    beforeBytes: enc('export const api = 1\n'),
    afterBytes: enc('export const api = 2\n'),
  })
  it('renderer+preload 跨模块强制 L2', () => {
    const result = classifyCandidate([renderer, preload], plainCtx)
    expect(result.level).toBe('L2')
    expect(result.reasons.join(' ')).toContain('cross-module-behavior')
  })
  it('path-hint L2 可被可信决策降级（非核心例外可达，W09）', () => {
    const engine = change({ path: 'packages/engine/src/ontolearn_engine/query.py' })
    let classification = applyTriageDecisions(classifyCandidate([engine], plainCtx), [], [engine], plainCtx)
    expect(classification.level).toBe('L2')
    classification = applyTriageDecisions(
      classification,
      [
        {
          paths: ['packages/engine/src/ontolearn_engine/query.py'],
          level: 'L1',
          reason: '仅查询展示层注释修正，非核心推理路径（可信人工语义裁定）',
        },
      ],
      [engine],
      plainCtx,
    )
    expect(classification.level).toBe('L1')
    expect(classification.errors ?? []).toHaveLength(0)
  })
  it('semantic-proof L2 拒绝决策降级', () => {
    const csp = change({ path: 'apps/desktop/src/csp.ts' })
    let classification = applyTriageDecisions(classifyCandidate([csp], plainCtx), [], [csp], plainCtx)
    classification = applyTriageDecisions(
      classification,
      [{ paths: ['apps/desktop/src/csp.ts'], level: 'L1', reason: '试图降级' }],
      [csp],
      plainCtx,
    )
    expect(classification.level).toBe('L2')
    expect((classification.errors ?? []).join(' ')).toContain('降级')
  })
  it('决策应用后跨模块强制规则重新生效（W07）', () => {
    let classification = applyTriageDecisions(
      classifyCandidate([renderer, preload], plainCtx),
      [],
      [renderer, preload],
      plainCtx,
    )
    classification = applyTriageDecisions(
      classification,
      [
        {
          paths: ['apps/desktop/src/preload/bridge.ts'],
          level: 'L1',
          reason: '常量重命名，无跨进程语义变化（可信裁定）',
        },
      ],
      [renderer, preload],
      plainCtx,
    )
    expect(classification.level).toBe('L2')
    expect(classification.reasons.join(' ')).toContain('cross-module-behavior')
  })
  it('非法决策等级、缺 reason、未命中路径都记录错误', () => {
    const single = change({ path: 'docs/random/note.md' })
    let classification = applyTriageDecisions(
      classifyCandidate([single], plainCtx),
      [],
      [single],
      plainCtx,
    )
    classification = applyTriageDecisions(
      classification,
      [
        { paths: ['docs/random/note.md'], level: 'L9', reason: 'x' },
        { paths: ['docs/random/note.md'], level: 'L1' },
        { paths: ['docs/missing.md'], level: 'L1', reason: 'y' },
      ],
      [single],
      plainCtx,
    )
    const joined = (classification.errors ?? []).join('\n')
    expect(joined).toContain('等级非法')
    expect(joined).toContain('缺少 reason')
    expect(joined).toContain('未命中')
  })
  it('可信声明 FR 结算强制 L2（W12）', () => {
    const doc = change({
      path: 'docs/random/notes.md',
      beforeBytes: enc('x\n'),
      afterBytes: enc('y\n'),
    })
    const result = classifyCandidate([doc], { ...plainCtx, declaration: { isFrSettlement: true } })
    expect(result.level).toBe('L2')
    expect(result.reasons.join(' ')).toContain('fr-settlement-declared')
  })
  it('needs_triage 传播到候选级且保留 provisionalLevel', () => {
    const tri = change({ path: 'unknown/random.txt' })
    const plain = change({ path: 'docs/random/note.md' })
    const result = classifyCandidate([tri, plain], plainCtx)
    expect(result.level).toBe('needs_triage')
    expect(result.provisionalLevel).toBe('L0')
  })
})

function proven(reason: string) {
  return { proven: true, reason }
}
