import { createElement, Fragment, type ReactNode } from 'react'

type FactLocation = Readonly<{
  role: 'existing' | 'incoming'
  id: string
  owner: string | null
  sourceRow: string | null
  slot: Readonly<{ subject: string; predicate: string }>
}>

/** Private presentation data, validated and mapped by the caller before rendering.
 * This is not a wire DTO, parser, or engine-bound conflict lookup.
 * Declaration conflicts supply two existing records and the actual declaration;
 * other reasons supply the existing and incoming records.
 */
export type OwnershipConflictDetailViewModel = Readonly<{
  previewBaseRevision: number
  reason: 'reservedIdentity' | 'sameStatement' | 'singleSlot' | 'singleDeclaration'
  records: readonly FactLocation[]
  declaration?: Readonly<{ layer: 'ontology'; id: string; predicate: string }>
}>

const reasonLabels: Record<OwnershipConflictDetailViewModel['reason'], string> = {
  reservedIdentity: '保留身份冲突',
  sameStatement: '相同事实的来源冲突',
  singleSlot: '单值属性槽位冲突',
  singleDeclaration: '单值属性声明与现有事实冲突',
}

function originalText(value: string) {
  return createElement(
    'code',
    { style: { whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' } },
    value,
  )
}

function descriptionList(items: readonly (readonly [string, ReactNode])[]) {
  return createElement(
    'dl',
    null,
    items.map(([label, value]) =>
      createElement(
        Fragment,
        { key: label },
        createElement('dt', null, label),
        createElement('dd', null, value),
      ),
    ),
  )
}

export function OwnershipConflictDetailView({
  viewModel,
}: {
  viewModel: OwnershipConflictDetailViewModel
}) {
  const declaration = viewModel.declaration
  return createElement(
    'section',
    { 'aria-label': '首个阻断冲突定位' },
    createElement('h2', null, '首个阻断冲突定位'),
    descriptionList([
      ['预览基准修订', viewModel.previewBaseRevision],
      ['冲突原因', reasonLabels[viewModel.reason]],
    ]),
    declaration &&
      createElement(
        'section',
        { 'aria-label': '冲突声明' },
        createElement('h3', null, '冲突声明'),
        descriptionList([
          ['声明层', originalText(declaration.layer)],
          ['声明 ID', originalText(declaration.id)],
          ['声明谓词', originalText(declaration.predicate)],
        ]),
      ),
    createElement(
      'ol',
      { 'aria-label': '原始事实定位' },
      viewModel.records.map((record, index) =>
        createElement(
          'li',
          { key: index },
          createElement('h3', null, record.role === 'existing' ? '现有记录' : '传入记录'),
          descriptionList([
            ['原始 ID', originalText(record.id)],
            [
              '来源所有者（owner）',
              record.owner === null ? '人工（owner = null）' : originalText(record.owner),
            ],
            [
              '源行（sourceRow）',
              record.sourceRow === null
                ? '无源行（sourceRow = null）'
                : originalText(record.sourceRow),
            ],
            ['槽位主体（S）', originalText(record.slot.subject)],
            ['槽位谓词（P）', originalText(record.slot.predicate)],
          ]),
        ),
      ),
    ),
  )
}
