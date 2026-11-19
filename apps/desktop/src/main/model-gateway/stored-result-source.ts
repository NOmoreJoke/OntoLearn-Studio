import { createHash } from 'node:crypto'
import { z } from 'zod'
import { safeError } from '@ontolearn/contracts'
import { validateBusiness3, validateV2, v2Registry } from '@ontolearn/contracts/v2'
import errorCatalog from '../../../../../packages/contracts/v2/errors.json'
import { EngineError, type EngineSupervisor } from '../engine'
import { GatewayFailure, opaqueId, parse } from './policy'

export function sourceFailure(
  code: keyof typeof errorCatalog.codes,
  params: Record<string, unknown> = {},
): EngineError {
  const entry = errorCatalog.codes[code]
  return new EngineError(
    safeError({ code, messageKey: entry.messageKey, params, retryable: entry.retryable }),
  )
}
// Local content comparison only. Not a Store attestation or an authorization token.
export function materialCanonical(value: unknown): string {
  if (Array.isArray(value)) return '[' + value.map(materialCanonical).join(',') + ']'
  if (value && typeof value === 'object')
    return (
      '{' +
      Object.entries(value)
        .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
        .map(([key, entry]) => JSON.stringify(key) + ':' + materialCanonical(entry))
        .join(',') +
      '}'
    )
  return JSON.stringify(value)
}
const hash = (text: string) => createHash('sha256').update(text).digest('hex')
export const storedSelectionSchema = z
  .object({ resultId: opaqueId, selection: z.enum(['current', 'historical']) })
  .strict()
export type StoredSelection = z.infer<typeof storedSelectionSchema>
type ObjectValue = Record<string, unknown>
export type StoredResultMaterial = {
  metadata: ObjectValue
  bodyText: string
  bodyHash: string
  sourceFingerprint: string
}

/** Main-only whole-result reader. Never a renderer-provided source/permission adapter. */
export class StoredResultSource {
  private closed = false
  private readonly active = new Set<AbortController>()
  constructor(
    private readonly engine: EngineSupervisor,
    readonly projectId: string,
    // The approved baseline runs only synthetic test producers. This is not public input.
    private readonly producerPolicy: 'runtime-only' | 'synthetic-test-runtime' = 'runtime-only',
  ) {
    parse(opaqueId, projectId)
  }

  close(): void {
    this.closed = true
    for (const controller of this.active) controller.abort()
  }

  async load(input: StoredSelection, signal?: AbortSignal): Promise<StoredResultMaterial> {
    const selection = parse(storedSelectionSchema, input)
    if (this.closed || signal?.aborted) throw new GatewayFailure('CANCELLED')
    if (this.active.size >= 4) throw sourceFailure('RESOURCE_LIMIT', { resource: 'memory' })
    const controller = new AbortController()
    this.active.add(controller)
    let expired = false
    const abort = () => controller.abort()
    signal?.addEventListener('abort', abort, { once: true })
    const timer = setTimeout(() => {
      expired = true
      controller.abort()
    }, 5000)
    const check = () => {
      if (controller.signal.aborted || this.closed) {
        if (expired) throw sourceFailure('TIMEOUT', { phase: 'total' })
        throw new GatewayFailure('CANCELLED')
      }
    }
    let session: string | undefined
    const request = async (
      method: string,
      params: ObjectValue,
      schema: string,
    ): Promise<ObjectValue> => {
      check()
      const value = await new Promise<unknown>((resolve, reject) => {
        const cancelled = () => {
          try {
            check()
          } catch (error) {
            reject(error)
          }
        }
        controller.signal.addEventListener('abort', cancelled, { once: true })
        this.engine
          .request(method, params)
          .then(resolve, reject)
          .finally(() => {
            controller.signal.removeEventListener('abort', cancelled)
          })
          .catch(() => {})
        if (controller.signal.aborted) cancelled()
      })
      check()
      const currentSession = this.engine.engineSessionId
      if (!currentSession || (session !== undefined && currentSession !== session))
        throw sourceFailure('SESSION_MISMATCH')
      session = currentSession
      const validate = this.engine.profile === 'business3' ? validateBusiness3 : validateV2
      if (!validate(schema, value)) throw sourceFailure('INVALID_STATE')
      return structuredClone(value as ObjectValue)
    }
    try {
      const project = await request(
        'project.get',
        { projectId: this.projectId },
        'result_project.get',
      )
      if (project.projectId !== this.projectId) throw sourceFailure('PERMISSION_DENIED')
      const resultParams = { projectId: this.projectId, resultId: selection.resultId }
      const metadata = await request('result.get', resultParams, 'result')
      if (metadata.projectId !== this.projectId || metadata.resultId !== selection.resultId)
        throw sourceFailure('PERMISSION_DENIED')
      if (metadata.payloadStatus !== 'available')
        throw sourceFailure('PAYLOAD_EVICTED', { resultId: selection.resultId })
      if (
        (metadata.state !== 'current') !== metadata.historicalSelectionRequired ||
        (metadata.state === 'stale') !== (metadata.staleReason as unknown[]).length > 0 ||
        Number(metadata.inputProjectRevision) > Number(project.projectRevision) ||
        (selection.selection === 'current' && metadata.state !== 'current')
      )
        throw sourceFailure('INVALID_STATE')
      const jobParams = { projectId: this.projectId, jobId: metadata.jobId }
      const job = await request('job.get', jobParams, 'job')
      const input_ = job.input as ObjectValue
      const resultRef = job.resultRef as ObjectValue | null
      if (
        job.projectId !== this.projectId ||
        job.jobId !== metadata.jobId ||
        job.state !== 'succeeded' ||
        !resultRef ||
        resultRef.resultId !== selection.resultId ||
        resultRef.inputSnapshotId !== metadata.inputSnapshotId ||
        input_.definitionId !== metadata.definitionId ||
        ['inputSnapshotId', 'parametersHash', 'scope'].some(
          (key) => input_[key] !== metadata[key],
        ) ||
        [
          'inputSnapshotId',
          'parametersHash',
          'scope',
          'dependencyVector',
          'definitionSetDigests',
          'implementation',
        ].some((key) => materialCanonical(job[key]) !== materialCanonical(metadata[key]))
      )
        throw sourceFailure('INVALID_STATE')
      const producer = String(job.capability)
      const capability = v2Registry.capabilities[producer as keyof typeof v2Registry.capabilities]
      // Business3 installs the named query/quality and ChangeSet runtimes on top
      // of the legacy registry. Accept results from those exact producers only.
      const business3Producer =
        this.engine.profile === 'business3' &&
        (producer === 'query.execute' ||
          (v2Registry.projectQuality.chainCapabilities as string[]).includes(producer) ||
          Object.hasOwn(
            v2Registry.foundationProfiles.business3.capabilityImplementations,
            producer,
          ))
      const legacyAssertedQuery =
        producer === 'query.execute' &&
        metadata.scope === 'asserted' &&
        capability?.implementation === 'runtime-asserted-only'
      if (
        !capability ||
        (capability.implementation !== 'runtime' &&
          !business3Producer &&
          !legacyAssertedQuery &&
          !(
            this.producerPolicy === 'synthetic-test-runtime' &&
            capability.implementation === 'test-runtime'
          ))
      )
        throw sourceFailure('UNSUPPORTED_CAPABILITY')
      const expectedKind: Record<string, string> = {
        'test.read': 'test',
        'test.atomic': 'receipt',
        'test.rounds': 'scenario',
        'query.execute': 'query',
        'reasoning.execute': 'reasoning',
        'validation.execute': 'validation',
        'mapping.commit': 'receipt',
        'changeset.commit': 'receipt',
        'behavior.test': 'behavior',
        'scenario.run': 'scenario',
      }
      if (expectedKind[String(job.capability)] !== metadata.kind)
        throw sourceFailure('INVALID_STATE')
      const binding = {
        ...resultParams,
        inputSnapshotId: metadata.inputSnapshotId,
        scope: metadata.scope,
        parametersHash: metadata.parametersHash,
        order: 'ordinal+rowId:asc',
      }
      const rows: ObjectValue[] = [],
        ids = new Set<string>(),
        cursors = new Set<string>()
      let cursor: string | null = null
      let rowBytes = 0
      for (let pageNumber = 0; ; pageNumber++) {
        if (pageNumber >= 64) throw sourceFailure('RESOURCE_LIMIT', { resource: 'page' })
        const page = await request('result.page', { binding, pageSize: 64, cursor }, 'page')
        if (materialCanonical(page.binding) !== materialCanonical(binding))
          throw sourceFailure('CURSOR_MISMATCH')
        const incoming = page.rows as ObjectValue[]
        if (page.nextCursor && incoming.length === 0) throw sourceFailure('INVALID_STATE')
        for (const row of incoming) {
          const previous = rows.at(-1)
          if (
            ids.has(String(row.rowId)) ||
            (previous &&
              (Number(row.ordinal) < Number(previous.ordinal) ||
                (row.ordinal === previous.ordinal && String(row.rowId) <= String(previous.rowId))))
          )
            throw sourceFailure('INVALID_STATE')
          ids.add(String(row.rowId))
          rows.push(row)
          rowBytes += Buffer.byteLength(materialCanonical(row))
          if (rows.length > 1024 || rowBytes > 65536)
            throw sourceFailure('RESOURCE_LIMIT', { resource: 'memory' })
        }
        cursor = page.nextCursor as string | null
        if (cursor === null) break
        if (cursors.has(cursor)) throw sourceFailure('CURSOR_MISMATCH')
        cursors.add(cursor)
      }
      const latest = await request('result.get', resultParams, 'result')
      const latestJob = await request('job.get', jobParams, 'job')
      if (
        materialCanonical(latest) !== materialCanonical(metadata) ||
        materialCanonical(latestJob) !== materialCanonical(job)
      )
        throw sourceFailure('INVALID_STATE')
      const bodyText = materialCanonical({
        source: {
          ...metadata,
          selection: selection.selection,
          producerCapability: job.capability,
          stateMeaning: 'observed-at-read; immutable-selected-result; not-live-current-lease',
        },
        rows,
      })
      if (Buffer.byteLength(bodyText) > 65536)
        throw sourceFailure('RESOURCE_LIMIT', { resource: 'memory' })
      check()
      return {
        metadata: structuredClone(metadata),
        bodyText,
        bodyHash: hash(bodyText),
        sourceFingerprint: hash(materialCanonical({ metadata, job, bodyHash: hash(bodyText) })),
      }
    } finally {
      clearTimeout(timer)
      signal?.removeEventListener('abort', abort)
      this.active.delete(controller)
    }
  }
}
