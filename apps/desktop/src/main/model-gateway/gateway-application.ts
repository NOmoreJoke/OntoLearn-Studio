import { randomUUID } from 'node:crypto'
import { z } from 'zod'
import { safeError, type SafeError } from '@ontolearn/contracts'
import { EngineError } from '../engine'
import { ModelGatewayCore } from './gateway'
import { GatewayFailure, opaqueId, parse, purposeSchema, type FailureCode } from './policy'
import {
  StoredResultSource,
  sourceFailure,
  storedSelectionSchema,
  type StoredSelection,
  type StoredResultMaterial,
} from './stored-result-source'

const selectionIds = z
  .array(opaqueId)
  .min(1)
  .max(64)
  .refine((value) => new Set(value).size === value.length)
const previewInput = z.object({ configId: opaqueId, purpose: purposeSchema, selectionIds }).strict()
const startInput = previewInput.extend({ grantId: opaqueId }).strict()
type Selected = {
  materialId: string
  scopes: string[]
  leaves: string[]
  stored?: { input: StoredSelection; snapshot: StoredResultMaterial }
}
export type ApplicationOutcome =
  | { status: 'completed'; text: string }
  | { status: 'cancelled' }
  | {
      status: 'failed'
      failure:
        | { kind: 'source'; error: SafeError }
        | { kind: 'gateway'; code: Exclude<FailureCode, 'CANCELLED'> }
    }

/** Main application composition, not IPC. It has no renderer-provided source labels/text. */
export class GatewayApplication {
  private closed = false
  private readonly selected = new Map<string, Selected>()
  private readonly previews = new Set<string>()
  private readonly active = new Map<
    string,
    { controller: AbortController; references: Set<string> }
  >()
  constructor(
    private readonly core: ModelGatewayCore,
    private readonly source: StoredResultSource,
  ) {}

  private open(): void {
    if (this.closed) throw new GatewayFailure('CANCELLED')
  }
  private entries(ids: string[]): Selected[] {
    return ids.map((id) => {
      const entry = this.selected.get(id)
      if (!entry) throw new GatewayFailure('SCOPE_EXCEEDED')
      return entry
    })
  }
  async selectStoredResult(
    input: StoredSelection,
  ): Promise<{ selectionId: string; metadata: Record<string, unknown>; bodyHash: string }> {
    this.open()
    if (this.selected.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const copied = parse(storedSelectionSchema, input)
    const snapshot = await this.source.load(copied)
    this.open()
    // Recheck after await: concurrent selection must not exceed the private bound.
    if (this.selected.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const id = randomUUID(),
      scopes = [randomUUID()]
    const materialId = this.core.registerMaterial({
      projectId: this.source.projectId,
      scopes,
      kind: 'selected',
      text: snapshot.bodyText,
    })
    this.selected.set(id, { materialId, scopes, leaves: [id], stored: { input: copied, snapshot } })
    return {
      selectionId: id,
      metadata: structuredClone(snapshot.metadata),
      bodyHash: snapshot.bodyHash,
    }
  }

  // Only a trusted main tool/history/summary assembler calls this, never the public bridge.
  deriveFromMaterials(input: {
    inputs: string[]
    kind: 'tool' | 'history' | 'summary' | 'error'
    text: string
  }): string {
    this.open()
    const value = parse(
      z
        .object({
          inputs: selectionIds,
          kind: z.enum(['tool', 'history', 'summary', 'error']),
          text: z.string().max(65536),
        })
        .strict(),
      input,
    )
    if (this.selected.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const entries = this.entries(value.inputs)
    const materialId = this.core.deriveMaterial({
      projectId: this.source.projectId,
      inputs: entries.map((entry) => entry.materialId),
      kind: value.kind,
      text: value.text,
    })
    const id = randomUUID()
    this.selected.set(id, {
      materialId,
      scopes: [...new Set(entries.flatMap((entry) => entry.scopes))],
      leaves: [...new Set(entries.flatMap((entry) => entry.leaves))],
    })
    return id
  }

  private async refresh(ids: string[], signal?: AbortSignal): Promise<Selected[]> {
    this.open()
    const entries = this.entries(ids)
    const leaves = [...new Set(entries.flatMap((entry) => entry.leaves))]
    const controller = new AbortController()
    let expired = false
    const abort = () => controller.abort()
    signal?.addEventListener('abort', abort, { once: true })
    if (signal?.aborted) abort()
    const timer = setTimeout(() => {
      expired = true
      controller.abort()
    }, 5000)
    try {
      for (const leaf of leaves) {
        const original = this.selected.get(leaf)
        if (!original?.stored) throw new GatewayFailure('SCOPE_EXCEEDED')
        const latest = await this.source.load(original.stored.input, controller.signal)
        this.open()
        if (controller.signal.aborted) throw new GatewayFailure('CANCELLED')
        if (
          this.selected.get(leaf) !== original ||
          latest.bodyHash !== original.stored.snapshot.bodyHash ||
          latest.sourceFingerprint !== original.stored.snapshot.sourceFingerprint
        )
          throw new GatewayFailure('SCOPE_EXCEEDED')
      }
      if (this.entries(ids).some((entry, index) => entry !== entries[index]))
        throw new GatewayFailure('SCOPE_EXCEEDED')
      return entries
    } catch (error) {
      if (expired) throw sourceFailure('TIMEOUT', { phase: 'total' })
      throw error
    } finally {
      clearTimeout(timer)
      signal?.removeEventListener('abort', abort)
    }
  }

  async preview(
    input: z.infer<typeof previewInput>,
  ): Promise<ReturnType<ModelGatewayCore['previewAuthorization']>> {
    const value = parse(previewInput, input)
    const entries = await this.refresh(value.selectionIds)
    if (this.previews.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const preview = this.core.previewAuthorization({
      projectId: this.source.projectId,
      configId: value.configId,
      purpose: value.purpose,
      scopes: [...new Set(entries.flatMap((entry) => entry.scopes))],
    })
    this.previews.add(preview.previewId)
    return preview
  }
  // Trusted explicit user confirmation only. Reading materials never calls this automatically.
  confirm(previewId: string): string {
    this.open()
    parse(opaqueId, previewId)
    if (!this.previews.delete(previewId)) throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    return this.core.confirmAuthorization(previewId)
  }

  start(input: z.infer<typeof startInput>): {
    invocationId: string
    completion: Promise<ApplicationOutcome>
  } {
    this.open()
    const value = parse(startInput, input)
    if (this.active.size >= 4) throw new GatewayFailure('MODEL_UNAVAILABLE')
    const invocationId = randomUUID(),
      controller = new AbortController()
    const references = new Set([
      ...value.selectionIds,
      ...this.entries(value.selectionIds).flatMap((entry) => entry.leaves),
    ])
    this.active.set(invocationId, { controller, references })
    const completion = this.run(value, controller.signal).finally(() =>
      this.active.delete(invocationId),
    )
    return { invocationId, completion }
  }
  private async run(
    value: z.infer<typeof startInput>,
    signal: AbortSignal,
  ): Promise<ApplicationOutcome> {
    try {
      const entries = await this.refresh(value.selectionIds, signal)
      if (signal.aborted) return { status: 'cancelled' }
      const result = await this.core.invoke(
        {
          projectId: this.source.projectId,
          configId: value.configId,
          grantId: value.grantId,
          purpose: value.purpose,
          materials: entries.map((entry) => entry.materialId),
        },
        signal,
      )
      if (result.ok) return { status: 'completed', text: result.text }
      if (result.code === 'CANCELLED') return { status: 'cancelled' }
      return { status: 'failed', failure: { kind: 'gateway', code: result.code } }
    } catch (error) {
      if (error instanceof GatewayFailure) {
        if (error.code === 'CANCELLED') return { status: 'cancelled' }
        return { status: 'failed', failure: { kind: 'gateway', code: error.code } }
      }
      return {
        status: 'failed',
        failure: {
          kind: 'source',
          error: safeError(error instanceof EngineError ? error.error : undefined),
        },
      }
    }
  }
  cancel(invocationId: string): { requested: boolean } {
    parse(opaqueId, invocationId)
    const controller = this.active.get(invocationId)?.controller
    if (!controller || controller.signal.aborted) return { requested: false }
    controller.abort()
    return { requested: true }
  }
  releaseSelection(selectionId: string): void {
    parse(opaqueId, selectionId)
    for (const active of this.active.values())
      if (active.references.has(selectionId)) active.controller.abort()
    const entry = this.selected.get(selectionId)
    if (entry) this.core.releaseMaterial(entry.materialId)
    this.selected.delete(selectionId)
  }
  close(): void {
    if (this.closed) return
    this.closed = true
    for (const active of this.active.values()) active.controller.abort()
    this.source.close()
    this.core.closeProject(this.source.projectId)
    this.selected.clear()
    this.previews.clear()
  }
}
