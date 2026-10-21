import { describe, expect, it } from 'vitest'
import { prepareEditorDraft } from '../../apps/desktop/src/renderer/src/quality/draft'
import {
  checkText,
  compareStatements,
  openWorldText,
  visibleObservation,
  type QualityObservation,
} from '../../apps/desktop/src/renderer/src/quality/presentation'

describe('T05 private presentation helpers (no executor)', () => {
  it('compares full statements even when row counts are the same', () => {
    expect(
      compareStatements(
        [['urn:001', 'urn:type', '<urn:Risk>']],
        [['urn:002', 'urn:type', '<urn:Risk>']],
      ),
    ).toEqual({
      missing: [['urn:001', 'urn:type', '<urn:Risk>']],
      unexpected: [['urn:002', 'urn:type', '<urn:Risk>']],
    })
  })
  it('has distinct unsupported/not-executed wording and no closed-world absence claim', () => {
    expect(checkText.unsupported).toBe('不支持')
    expect(checkText['not-executed']).toBe('未执行')
    expect(openWorldText(null)).toBe('尚未查询记录')
    expect(openWorldText(0)).toBe('未记录')
    expect(openWorldText(1)).toBe('已记录 1 条')
  })
  it('rejects late observations for a different project', () => {
    const observation = { projectId: 'old' } as QualityObservation
    expect(visibleObservation(observation, 'new')).toBeNull()
    expect(visibleObservation(observation, 'old')).toBe(observation)
    expect(visibleObservation(null, 'old')).toBeNull()
  })
})

describe('T05 editor draft regression', () => {
  const input = {
    kind: 'rule' as const,
    identity: 'r1',
    label: '测试',
    revision: '1',
    enabled: true,
    targetClass: '',
    path: '',
    template: 'maxCount' as const,
    parameter: '',
    upper: '',
    conditions: [{ kind: 'type' as const, subject: '?e', path: '', value: 'urn:Equipment' }],
    conclusions: [{ kind: 'type' as const, subject: '?e', path: '', value: 'urn:Risk' }],
  }
  it('ignores a hidden invalid constraint parameter when preparing a rule', () => {
    const result = prepareEditorDraft(input)
    expect(result.error).toBe('')
    expect(JSON.parse(result.draft)).toEqual({
      schemaVersion: 1,
      kind: 'rule',
      id: 'r1',
      label: '测试',
      revision: 1,
      enabled: true,
      conditions: [{ kind: 'type', subject: '?e', class: 'urn:Equipment' }],
      conclusions: [{ kind: 'type', subject: '?e', class: 'urn:Risk' }],
    })
    expect(prepareEditorDraft({ ...input, kind: 'constraint' }).error).toBe(
      '最大数量须为非负整数。',
    )
  })
  it('does not truncate a fractional or overflowing draft version', () => {
    for (const revision of ['1.2', '0', '-1', '2147483648']) {
      expect(prepareEditorDraft({ ...input, revision }).draft).toBe('')
    }
  })
})
