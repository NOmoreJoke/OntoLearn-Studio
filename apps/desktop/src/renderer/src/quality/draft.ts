/** Form serialization only; authoritative definition validation stays in the engine. */
export type Pattern = {
  kind: 'type' | 'property' | 'compare'
  subject: string
  path: string
  value: string
}
export type Template = 'required' | 'datatype' | 'maxCount' | 'allowedValues' | 'numericRange'

function patternValue(row: Pattern) {
  if (row.kind === 'type') return { kind: 'type', subject: row.subject, class: row.value }
  if (row.kind === 'property')
    return { kind: 'property', subject: row.subject, path: row.path, object: row.value }
  return { kind: 'compare', left: row.subject, operator: row.path, right: row.value }
}

export function prepareEditorDraft(input: {
  kind: 'constraint' | 'rule'
  identity: string
  label: string
  revision: string
  enabled: boolean
  targetClass: string
  path: string
  template: Template
  parameter: string
  upper: string
  conditions: Pattern[]
  conclusions: Pattern[]
}): { draft: string; error: string } {
  if (!/^[1-9][0-9]*$/.test(input.revision) || Number(input.revision) > Number.MAX_SAFE_INTEGER)
    return { draft: '', error: '草稿版本须为正整数；正式版本由项目服务复验。' }
  let parameters: object = {}
  if (input.kind === 'constraint') {
    if (input.template === 'datatype') parameters = { datatype: input.parameter }
    if (input.template === 'maxCount') {
      if (!/^[0-9]+$/.test(input.parameter) || Number(input.parameter) > Number.MAX_SAFE_INTEGER)
        return { draft: '', error: '最大数量须为非负整数。' }
      parameters = { maxCount: Number(input.parameter) }
    }
    if (input.template === 'allowedValues')
      parameters = { values: input.parameter.split('\n').filter(Boolean) }
    if (input.template === 'numericRange')
      parameters = { minInclusive: input.parameter || null, maxInclusive: input.upper || null }
  }
  const common = {
    schemaVersion: 1,
    kind: input.kind,
    id: input.identity,
    revision: Number(input.revision),
    label: input.label,
    enabled: input.enabled,
  }
  const payload =
    input.kind === 'constraint'
      ? {
          ...common,
          targetClass: input.targetClass,
          path: input.path,
          template: input.template,
          parameters,
        }
      : {
          ...common,
          conditions: input.conditions.map(patternValue),
          conclusions: input.conclusions.map(patternValue),
        }
  return { draft: JSON.stringify(payload, null, 2), error: '' }
}
