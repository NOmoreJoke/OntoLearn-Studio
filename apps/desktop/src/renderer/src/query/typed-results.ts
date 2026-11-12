import { z } from 'zod'
import { validateV2 } from '../../../../../../packages/contracts/src/v2'

// Private display inputs for the received R3 source DTOs, not another bridge or
// permission issuer. The canonical source's verbatim types are checked in tests.
const scalar = z.string().refine((text) => !/[\uD800-\uDFFF]/u.test(text))
const hash = z.string().regex(/^[0-9a-f]{64}$/)
const integer = z.number().int().min(0).max(Number.MAX_SAFE_INTEGER)
const implementation = z
  .object({ executionSemanticsVersion: scalar, engineVersion: scalar, dependencyLockHash: hash })
  .strict()
const identitySchema = z
  .object({
    projectId: z.string().uuid(),
    resultId: z.string().uuid(),
    jobId: z.string().uuid(),
    inputSnapshotId: hash,
    inputProjectRevision: integer,
    scope: z.literal('asserted'),
    definitionId: scalar,
    parametersHash: hash,
    implementation,
    payloadSha256: hash,
    definitionSha256: hash,
    inputSelection: z.enum(['current', 'historical']),
    projectionVersion: z.literal(1),
    // Recognizes this source version; does not approve its production policy.
    lengthPolicyId: z.literal('query-presentation-scalars-v1'),
  })
  .strict()
type DisplayIdentity = z.infer<typeof identitySchema>
type DisplayMetadata = {
  projectId: string
  resultId: string
  jobId: string
  kind: string
  definitionId: string
  inputSnapshotId: string
  inputProjectRevision: number
  scope: string
  parametersHash: string
  dependencyVector: Record<string, number>
  implementation: z.infer<typeof implementation>
  state: 'current' | 'stale' | 'historical'
  staleReason: { code: string; dependency: string; before: number; after: number }[]
  payloadStatus: 'available' | 'evicted'
  historicalSelectionRequired: boolean
}
const cellSchema = z.union([
  z.null(),
  z.object({ kind: z.literal('iri'), iri: scalar, n3: scalar }).strict(),
  z
    .object({
      kind: z.literal('literal'),
      lexical: scalar,
      n3: scalar,
      literalType: z.discriminatedUnion('kind', [
        z.object({ kind: z.literal('plain') }).strict(),
        z.object({ kind: z.literal('language'), tag: scalar }).strict(),
        z.object({ kind: z.literal('datatype'), iri: scalar }).strict(),
      ]),
    })
    .strict(),
])
export type DisplayCell = z.infer<typeof cellSchema>
const descriptorSchema = z
  .object({
    identity: identitySchema,
    descriptorRef: z.string().uuid(),
    metadata: z.custom<DisplayMetadata>((raw) => validateV2('result', raw)),
    executedText: z
      .object({ sha256: hash, utf8Bytes: integer, unicodeScalars: integer, utf16Units: integer })
      .strict(),
    query: z.discriminatedUnion('kind', [
      z.object({ kind: z.literal('ASK'), value: z.boolean() }).strict(),
      z
        .object({
          kind: z.literal('SELECT'),
          columns: z.array(z.object({ index: integer, name: scalar }).strict()),
          rowCount: integer,
        })
        .strict(),
    ]),
  })
  .strict()
export type DisplayDescriptor = z.infer<typeof descriptorSchema>
const rowsSchema = z
  .object({
    identity: identitySchema,
    kind: z.literal('rows'),
    order: z.literal('query-index:asc'),
    rows: z.array(z.object({ index: integer, rowKey: hash, cells: z.array(cellSchema) }).strict()),
    nextCursor: z.string().uuid().nullable(),
  })
  .strict()
export type DisplayRowsPage = z.infer<typeof rowsSchema>
const textSchema = z
  .object({
    identity: identitySchema,
    kind: z.literal('text'),
    order: z.literal('utf8-byte:asc'),
    startUtf8Byte: integer,
    utf8Length: integer,
    text: scalar,
    nextCursor: z.string().uuid().nullable(),
  })
  .strict()
export type DisplayTextPage = z.infer<typeof textSchema>

function invalid(): never {
  throw new Error('query.invalidPresentation')
}
const sameImplementation = (
  a: DisplayIdentity['implementation'],
  b: DisplayIdentity['implementation'],
) =>
  a.engineVersion === b.engineVersion &&
  a.executionSemanticsVersion === b.executionSemanticsVersion &&
  a.dependencyLockHash === b.dependencyLockHash

export function sameIdentity(a: DisplayIdentity, b: DisplayIdentity): boolean {
  return (
    a.projectId === b.projectId &&
    a.resultId === b.resultId &&
    a.jobId === b.jobId &&
    a.inputSnapshotId === b.inputSnapshotId &&
    a.inputProjectRevision === b.inputProjectRevision &&
    a.scope === b.scope &&
    a.definitionId === b.definitionId &&
    a.parametersHash === b.parametersHash &&
    sameImplementation(a.implementation, b.implementation) &&
    a.payloadSha256 === b.payloadSha256 &&
    a.definitionSha256 === b.definitionSha256 &&
    a.inputSelection === b.inputSelection &&
    a.projectionVersion === b.projectionVersion &&
    a.lengthPolicyId === b.lengthPolicyId
  )
}

export function displayDescriptor(
  raw: unknown,
  expected: { projectId: string; resultId: string },
): DisplayDescriptor {
  const descriptor = descriptorSchema.parse(raw)
  const { identity, metadata, executedText, query } = descriptor
  if (
    identity.projectId !== expected.projectId ||
    identity.resultId !== expected.resultId ||
    metadata.kind !== 'query' ||
    metadata.payloadStatus !== 'available' ||
    !sameImplementation(identity.implementation, metadata.implementation) ||
    (
      [
        'projectId',
        'resultId',
        'jobId',
        'inputSnapshotId',
        'inputProjectRevision',
        'scope',
        'definitionId',
        'parametersHash',
      ] as const
    ).some((key) => identity[key] !== metadata[key]) ||
    executedText.unicodeScalars > executedText.utf16Units ||
    executedText.utf16Units > 2 * executedText.unicodeScalars ||
    executedText.utf8Bytes < executedText.unicodeScalars ||
    executedText.utf8Bytes > 4 * executedText.unicodeScalars ||
    (query.kind === 'SELECT' &&
      (new Set(query.columns.map((column) => column.name)).size !== query.columns.length ||
        query.columns.some((column, index) => column.index !== index)))
  )
    invalid()
  return structuredClone(descriptor)
}

export function displayRows(
  raw: unknown,
  descriptor: DisplayDescriptor,
  requested: { descriptorRef: string; cursor: string | null; startIndex: number; pageSize: number },
): DisplayRowsPage {
  const page = rowsSchema.parse(raw)
  const query = descriptor.query
  if (query.kind !== 'SELECT' || descriptor.metadata.payloadStatus !== 'available') return invalid()
  const { startIndex, pageSize } = requested
  const end = startIndex + page.rows.length
  if (
    requested.descriptorRef !== descriptor.descriptorRef ||
    (requested.cursor === null) !== (startIndex === 0) ||
    (page.nextCursor !== null && page.nextCursor === requested.cursor) ||
    !Number.isSafeInteger(startIndex) ||
    startIndex < 0 ||
    startIndex > query.rowCount ||
    !Number.isSafeInteger(pageSize) ||
    pageSize < 1 ||
    pageSize > 200 ||
    !sameIdentity(page.identity, descriptor.identity) ||
    page.rows.length > pageSize ||
    new Set(page.rows.map((row) => row.rowKey)).size !== page.rows.length ||
    page.rows.some(
      (row, index) => row.index !== startIndex + index || row.cells.length !== query.columns.length,
    ) ||
    end > query.rowCount ||
    (page.nextCursor !== null) !== end < query.rowCount ||
    (end < query.rowCount && page.rows.length === 0)
  )
    invalid()
  return structuredClone(page)
}

export function displayText(
  raw: unknown,
  descriptor: DisplayDescriptor,
  requested: {
    descriptorRef: string
    cursor: string | null
    startUtf8Byte: number
    maxUtf8Bytes: number
  },
): DisplayTextPage {
  const page = textSchema.parse(raw)
  const { startUtf8Byte, maxUtf8Bytes } = requested
  const end = page.startUtf8Byte + page.utf8Length
  if (
    descriptor.metadata.payloadStatus !== 'available' ||
    requested.descriptorRef !== descriptor.descriptorRef ||
    (requested.cursor === null) !== (startUtf8Byte === 0) ||
    (page.nextCursor !== null && page.nextCursor === requested.cursor) ||
    !Number.isSafeInteger(startUtf8Byte) ||
    startUtf8Byte < 0 ||
    !Number.isSafeInteger(maxUtf8Bytes) ||
    maxUtf8Bytes < 4 ||
    maxUtf8Bytes > 32768 ||
    !sameIdentity(page.identity, descriptor.identity) ||
    page.startUtf8Byte !== startUtf8Byte ||
    page.utf8Length !== new TextEncoder().encode(page.text).length ||
    page.utf8Length > maxUtf8Bytes ||
    end > descriptor.executedText.utf8Bytes ||
    (page.nextCursor !== null) !== end < descriptor.executedText.utf8Bytes ||
    (end < descriptor.executedText.utf8Bytes && page.utf8Length === 0)
  )
    invalid()
  return structuredClone(page)
}

export function cellText(cell: DisplayCell): string {
  if (cell === null) return '未绑定'
  if (cell.kind === 'iri') return cell.iri
  if (cell.literalType.kind === 'language') return `${cell.lexical} @${cell.literalType.tag}`
  if (cell.literalType.kind === 'datatype') return `${cell.lexical} ^^${cell.literalType.iri}`
  return cell.lexical
}

export function currentPageCsv(
  descriptor: DisplayDescriptor,
  page: DisplayRowsPage,
  requested: { descriptorRef: string; cursor: string | null; startIndex: number; pageSize: number },
): string {
  if (descriptor.query.kind !== 'SELECT') return invalid()
  // Recheck binding/shape at the export boundary; never fetch or accumulate more rows.
  const accepted = displayRows(page, descriptor, requested)
  const escape = (value: string) => {
    const safe = /^[\s]*[=+\-@]/u.test(value) || /^[\t\r\n]/u.test(value) ? `'${value}` : value
    return `"${safe.replaceAll('"', '""')}"`
  }
  return (
    [
      descriptor.query.columns.map((column) => column.name),
      ...accepted.rows.map((row) => row.cells.map((cell) => (cell === null ? '' : cell.n3))),
    ]
      .map((row) => row.map(escape).join(','))
      .join('\r\n') + '\r\n'
  )
}

export function iriConnections(
  row: DisplayRowsPage['rows'][number],
  descriptor: DisplayDescriptor,
) {
  if (descriptor.query.kind !== 'SELECT') return []
  return row.cells.flatMap((cell, index) =>
    cell?.kind === 'iri'
      ? [
          {
            column: descriptor.query.kind === 'SELECT' ? descriptor.query.columns[index].name : '',
            iri: cell.iri,
          },
        ]
      : [],
  )
}

export function displayReadFailure(
  raw: unknown,
  expected: { projectId: string; resultId: string; descriptorRef?: string },
) {
  const failure = z
    .object({
      projectId: z.string().uuid(),
      resultId: z.string().uuid(),
      descriptorRef: z.string().uuid().nullable(),
      error: z.custom<import('../../../../../../packages/contracts/src').SafeError>((value) =>
        validateV2('error', value),
      ),
    })
    .strict()
    .parse(raw)
  if (
    failure.projectId !== expected.projectId ||
    failure.resultId !== expected.resultId ||
    (failure.error.code === 'PAYLOAD_EVICTED' &&
      failure.error.params.resultId !== expected.resultId) ||
    failure.descriptorRef !== (expected.descriptorRef ?? null)
  )
    return invalid()
  return structuredClone(failure.error)
}
