import { createHash } from 'node:crypto'
import fixtures from '../packages/contracts/v2/fixtures.json'
import { validateBusiness3 } from '../packages/contracts/src/v2'
import type { MainlineProjectReadDTO } from '../apps/desktop/src/renderer/src/query/api002-source-types'
import {
  displayDescriptor,
  displayRows,
  type DisplayDescriptor,
  type DisplayRowsPage,
} from '../apps/desktop/src/renderer/src/query/typed-results'

export const sha256 = (text: string) => createHash('sha256').update(text).digest('hex')
export const profiles = [
  { name: 'sparse-short', pageRows: 1, anchors: 1, matchingEvery: 8, literalScalars: 8 },
  { name: 'dense-page', pageRows: 32, anchors: 4, matchingEvery: 1, literalScalars: 8 },
  { name: 'wide-page', pageRows: 200, anchors: 16, matchingEvery: 2, literalScalars: 32 },
] as const
export type Profile = (typeof profiles)[number]

/** Synthetic contract-valid consumer input, never a mapping or executed query claim. */
export function graphFixture(count: number, profile: Profile, seed: number) {
  if (!Number.isInteger(count) || count < 0 || count > 4096)
    throw new Error('FACT_COUNT_OUTSIDE_READ_CONTRACT')
  if (!Number.isSafeInteger(seed) || seed < 0 || seed > 0xffffffff) throw new Error('INVALID_SEED')
  let state = seed >>> 0
  const random = () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0
    return state
  }
  const anchors = Array.from({ length: profile.anchors }, (_, i) => `urn:q3:anchor:${i}`)
  const metadata = structuredClone(
    (
      fixtures.cases.find((x) => x.name === 'response result.get')!.value as unknown as {
        result: DisplayDescriptor['metadata']
      }
    ).result,
  )
  const descriptor: DisplayDescriptor = {
    identity: {
      projectId: metadata.projectId,
      resultId: metadata.resultId,
      jobId: metadata.jobId,
      inputSnapshotId: metadata.inputSnapshotId,
      inputProjectRevision: 1,
      scope: 'asserted',
      definitionId: metadata.definitionId,
      parametersHash: metadata.parametersHash,
      implementation: metadata.implementation,
      payloadSha256: sha256('synthetic payload'),
      definitionSha256: sha256('synthetic definition'),
      inputSelection: 'current',
      projectionVersion: 1,
      lengthPolicyId: 'query-presentation-scalars-v1',
    },
    descriptorRef: '40000000-0000-4000-8000-000000000001',
    metadata,
    executedText: { sha256: sha256('text'), utf8Bytes: 4, unicodeScalars: 4, utf16Units: 4 },
    query: {
      kind: 'SELECT',
      rowCount: profile.pageRows,
      columns: anchors.map((_, index) => ({ index, name: `c${index}` })),
    },
  }
  const source: MainlineProjectReadDTO = {
    readVersion: 1,
    projectId: metadata.projectId,
    inputSnapshotId: metadata.inputSnapshotId,
    workspace: {
      workspaceVersion: 1,
      projectId: metadata.projectId,
      inputSnapshotId: metadata.inputSnapshotId,
      domainRevision: 1,
      metadataVersion: 1,
      metadata: {
        name: 'synthetic performance input',
        templateRef: null,
        archived: false,
        mode: 'guided',
        origin: 'created',
      },
      operationSequence: 1,
      checkpointRef: sha256('checkpoint'),
      draft: { editor: 'query-workspace-v1', state: 'missing' },
    },
    domain: {
      projectRevision: 1,
      dependencyVector: { 'facts:asserted': 1 },
      state: {
        definitions: [],
        mappingState: {},
        facts: Array.from({ length: count }, (_, index) => {
          const selected = index % profile.matchingEvery === 0
          const subject = selected ? anchors[random() % anchors.length] : `urn:q3:other:${index}`
          const predicate = `urn:q3:p:${index % 29}`
          const object =
            index % 5 === 4
              ? `"${'测'.repeat(profile.literalScalars)}${index}"`
              : `<urn:q3:target:${index}>`
          return {
            id: sha256(JSON.stringify([subject, predicate, object])),
            subject,
            predicate,
            object,
            owner: null,
            source_row: null,
            managed_value: null,
          }
        }),
      },
    },
  }
  const page: DisplayRowsPage = {
    identity: structuredClone(descriptor.identity),
    kind: 'rows',
    order: 'query-index:asc',
    nextCursor: null,
    rows: Array.from({ length: profile.pageRows }, (_, index) => ({
      index,
      rowKey: sha256(`synthetic-row:${seed}:${index}`),
      cells: anchors.map((_, col) => {
        const iri = anchors[(index + col) % anchors.length]
        return { kind: 'iri' as const, iri, n3: `<${iri}>` }
      }),
    })),
  }
  const requested = {
    descriptorRef: descriptor.descriptorRef,
    cursor: null,
    startIndex: 0,
    pageSize: profile.pageRows,
  }
  const sourceBytes = Buffer.byteLength(JSON.stringify(source))
  if (sourceBytes > 1572864) throw new Error('FIXTURE_EXCEEDS_READ_BYTES')
  const sourceAccepted = validateBusiness3('result_project.read', source)
  displayDescriptor(descriptor, { projectId: metadata.projectId, resultId: metadata.resultId })
  displayRows(page, descriptor, requested)
  return {
    source,
    descriptor,
    page,
    requested,
    rowKey: page.rows[0].rowKey,
    sourceBytes,
    sourceAccepted,
    inputSha256: sha256(JSON.stringify({ source, descriptor, page, requested })),
  }
}

export function summarize(values: number[]) {
  if (values.length === 0 || values.some((value) => !Number.isFinite(value) || value < 0))
    throw new Error('INVALID_SAMPLES')
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return {
    count: sorted.length,
    minMs: sorted[0],
    medianMs: sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2,
    p95Ms: sorted[Math.ceil(sorted.length * 0.95) - 1],
    maxMs: sorted[sorted.length - 1],
  }
}
