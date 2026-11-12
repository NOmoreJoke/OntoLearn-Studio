import { describe, expect, it } from 'vitest'
import { parseConflictsEvidence, parseRangeDiff } from '../../scripts/lib/range-diff.mjs'

describe('parseRangeDiff（W02：exit 0 不代表补丁一致）', () => {
  it('全部等号判 unchanged', () => {
    const raw = [
      '1:  f614874c5e0e = 1:  9a1b2c3d4e5f feat: first change',
      '2:  abc123def456 = 2:  fed654cba321 fix: second change',
    ].join('\n')
    const parsed = parseRangeDiff(raw)
    expect(parsed.status).toBe('unchanged')
    expect(parsed.patchUnchanged).toBe(true)
  })
  it('等号 + 单侧新增（-: >）必须判 changed（原实现误判 unchanged 的核心反例）', () => {
    const raw = [
      '1:  f614874c5e0e = 1:  9a1b2c3d4e5f feat: first change',
      '-:  ------------ > 2:  fed1234abc567 feat: sneaky extra commit',
    ].join('\n')
    const parsed = parseRangeDiff(raw)
    expect(parsed.status).toBe('changed')
    expect(parsed.patchUnchanged).toBe(false)
  })
  it('单侧删除（< -:）判 changed', () => {
    const raw = [
      '1:  f614874c5e0e = 1:  9a1b2c3d4e5f feat: first',
      '2:  abc123def456 < -:  ------------ dropped commit',
    ].join('\n')
    const parsed = parseRangeDiff(raw)
    expect(parsed.status).toBe('changed')
  })
  it('修改条目（!）判 changed', () => {
    const raw = ['1:  f614874c5e0e ! 1:  9a1b2c3d4e5f feat: modified change'].join('\n')
    const parsed = parseRangeDiff(raw)
    expect(parsed.status).toBe('changed')
    expect(parsed.patchUnchanged).toBe(false)
  })
  it('无法识别的条目行判 unknown，不得推定相等', () => {
    const raw = ['1:  f614874c5e0e = 1:  9a1b2c3d4e5f ok', '2:  weird ~ 3:  entry broken'].join(
      '\n',
    )
    const parsed = parseRangeDiff(raw)
    expect(parsed.status).toBe('unknown')
    expect(parsed.patchUnchanged).toBeNull()
  })
  it('空输出判 unknown', () => {
    const parsed = parseRangeDiff('')
    expect(parsed.status).toBe('unknown')
  })
})

describe('parseConflictsEvidence（冲突只认附带证据，W02）', () => {
  it('schema 完整且 count=0 给出 none-proven', () => {
    const parsed = parseConflictsEvidence({
      schemaVersion: 1,
      producedBy: 'git-rebase-output',
      conflictCount: 0,
      conflictPaths: [],
    })
    expect(parsed.status).toBe('none-proven-by-attached-evidence')
  })
  it('有冲突时如实列出', () => {
    const parsed = parseConflictsEvidence({
      schemaVersion: 1,
      producedBy: 'git-rebase-output',
      conflictCount: 1,
      conflictPaths: ['packages/contracts/index.ts'],
    })
    expect(parsed.status).toBe('present')
    expect(parsed.paths).toEqual(['packages/contracts/index.ts'])
  })
  it('count 与 paths 不一致判 unknown', () => {
    const parsed = parseConflictsEvidence({
      schemaVersion: 1,
      producedBy: 'x',
      conflictCount: 0,
      conflictPaths: ['a.ts'],
    })
    expect(parsed.status).toBe('unknown')
  })
  it('缺 producedBy/schema 判 unknown', () => {
    expect(parseConflictsEvidence(null).status).toBe('unknown')
    expect(parseConflictsEvidence({ conflictCount: 0, conflictPaths: [] }).status).toBe('unknown')
  })
})
