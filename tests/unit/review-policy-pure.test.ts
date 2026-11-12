import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import {
  isStatusDocument,
  isTestCodePath,
  isTestSupportPath,
  matchPathHint,
  parsePolicyText,
  provenLineEndingOnly,
} from '../../scripts/lib/review-policy.mjs'

const policy = parsePolicyText(readFileSync('.github/review-policy.yml', 'utf8'), 'policy')

const encoder = new TextEncoder()
const bytes = (text: string) => encoder.encode(text)

describe('matchPathHint（路径提示匹配）', () => {
  it('**/*.md 匹配根级与深层 Markdown', () => {
    expect(matchPathHint('AGENTS.md', '**/*.md')).toBe(true)
    expect(matchPathHint('docs/a/b/note.md', '**/*.md')).toBe(true)
    expect(matchPathHint('src/main/index.ts', '**/*.md')).toBe(false)
  })
  it('目录前缀 + /** 只匹配目录内部', () => {
    expect(matchPathHint('apps/desktop/src/main/window.ts', 'apps/desktop/src/main/**')).toBe(true)
    expect(matchPathHint('apps/desktop/src/main.ts', 'apps/desktop/src/main/**')).toBe(false)
    expect(matchPathHint('apps/desktop/src/renderer/x.tsx', 'apps/desktop/src/main/**')).toBe(false)
  })
  it('段内 * 不跨越目录分隔符；. 为字面量', () => {
    expect(matchPathHint('apps/desktop/electron-builder.yml', '**/electron-builder.*')).toBe(true)
    expect(matchPathHint('apps/desktop/electron-buildery', '**/electron-builder.*')).toBe(false)
    expect(matchPathHint('a/b/electron-builder.json', 'a/*/electron-builder.*')).toBe(true)
    expect(matchPathHint('a/b/c/electron-builder.json', 'a/*/electron-builder.*')).toBe(false)
  })
})

describe('测试代码与支持代码路径（W08）', () => {
  it('engine tests 目录只有真正的用例文件继承例外，conftest/helper 是支持代码', () => {
    expect(isTestCodePath('packages/engine/tests/test_job_store.py')).toBe(true)
    expect(isTestCodePath('packages/engine/tests/job_store_test.py')).toBe(true)
    expect(isTestCodePath('packages/engine/tests/conftest.py')).toBe(false)
    expect(isTestCodePath('packages/engine/tests/helpers/runtime.py')).toBe(false)
    expect(isTestSupportPath('packages/engine/tests/conftest.py')).toBe(true)
  })
  it('tests 目录下 *.test.ts / *.spec.ts 是用例，夹具与配置是支持代码', () => {
    expect(isTestCodePath('tests/e2e/flow.spec.ts')).toBe(true)
    expect(isTestCodePath('tests/unit/a.test.ts')).toBe(true)
    expect(isTestCodePath('tests/fixtures/T04/fixture.json')).toBe(false)
    expect(isTestSupportPath('tests/fixtures/T04/fixture.json')).toBe(true)
  })
})

describe('provenLineEndingOnly（唯一可机器证明的非功能变更，W11 前置为修改型文本）', () => {
  it('CRLF→LF 与 LF→CRLF 规范化可证明', () => {
    expect(provenLineEndingOnly(bytes('a\r\nb\r\n'), bytes('a\nb\n')).proven).toBe(true)
    expect(provenLineEndingOnly(bytes('a\nb\n'), bytes('a\r\nb\r\n')).proven).toBe(true)
  })
  it('字符串字面量内的空格变化不可证明（即使 git diff -w 视为空白）', () => {
    expect(provenLineEndingOnly(bytes("s = 'hello world'"), bytes("s = 'helloworld'")).proven).toBe(
      false,
    )
  })
  it('Python 缩进变化不可证明', () => {
    expect(
      provenLineEndingOnly(bytes('if x:\n    return 1\n'), bytes('if x:\n  return 1\n')).proven,
    ).toBe(false)
  })
  it('注释指令空白变化（工具指令语义）不可证明', () => {
    expect(provenLineEndingOnly(bytes('#  noqa: E501'), bytes('# noqa: E501')).proven).toBe(false)
  })
  it('行尾空白与空白行增删不可证明（多行字符串/模板字面量风险）', () => {
    expect(provenLineEndingOnly(bytes('x  \ny\n'), bytes('x\ny\n')).proven).toBe(false)
    expect(provenLineEndingOnly(bytes('a\n\n\nb\n'), bytes('a\nb\n')).proven).toBe(false)
  })
  it('字符串中间的裸 CR（非行尾）不可证明', () => {
    expect(provenLineEndingOnly(bytes('a\rb\n'), bytes('ab\n')).proven).toBe(false)
  })
  it('完全相同的字节不算证明（无变更走不到分类例外）', () => {
    expect(provenLineEndingOnly(bytes('a\n'), bytes('a\n')).proven).toBe(false)
  })
})

describe('政策文件与状态文档识别', () => {
  it('政策文件是 JSON 子集且为报告模式', () => {
    expect(policy.status).toBe('adopted_report_only')
    const activation = (policy as { activation: { enforced: boolean } }).activation
    expect(activation.enforced).toBe(false)
  })
  it('状态文档识别 m0-checklist 与 status.md，普通文档不算', () => {
    expect(isStatusDocument('docs/m0-checklist.md')).toBe(true)
    expect(isStatusDocument('docs/reviews/I02/status.md')).toBe(true)
    expect(isStatusDocument('docs/verification/fr-completion.md')).toBe(false)
    expect(isStatusDocument('status.md')).toBe(false)
  })
})
