import { createHash, randomUUID } from 'node:crypto'
import { z } from 'zod'
import { GatewayFailure, opaqueId, parse } from './policy'
import {
  StoredResultSource,
  materialCanonical,
  storedSelectionSchema,
  type StoredSelection,
  type StoredResultMaterial,
} from './stored-result-source'

const name = z.string().min(1).max(128)
const modelSchema = z
  .object({
    id: name,
    version: name,
    producerCapability: name,
    definitionId: name,
    kind: name,
    implementation: z
      .object({
        executionSemanticsVersion: name,
        engineVersion: name,
        dependencyLockHash: z.string().regex(/^[a-f0-9]{64}$/),
      })
      .strict(),
    tag: name,
    fields: z
      .array(
        z
          .object({
            key: name,
            label: name,
            index: z.number().int().min(1).max(16),
            type: z.enum(['string', 'number', 'boolean']),
            nullable: z.boolean(),
            dependsOn: z.array(name).max(16),
          })
          .strict(),
      )
      .min(1)
      .max(16),
  })
  .strict()
export type StoredFieldModel = z.infer<typeof modelSchema>
type Scalar = string | number | boolean | null
type Row = { rowId: string; ordinal: number; cells: Scalar[] }
type Model = { spec: StoredFieldModel; digest: string; dependencies: Map<string, string[]> }
type Catalog = {
  input: StoredSelection
  snapshot: StoredResultMaterial
  model: Model
  rows: Row[]
  fields: Map<string, StoredFieldModel['fields'][number]>
}
export type FieldProjection = {
  bodyText: string
  bodyHash: string
  scopes: string[]
  rowCount: number
  byteCount: number
  // Internal main-owned refresh handle. Never serialized into outgoing content.
  catalogId: string
  fieldIds: string[]
}
const hash = (value: unknown) => createHash('sha256').update(materialCanonical(value)).digest('hex')
const reject = (): never => {
  throw new GatewayFailure('SCOPE_EXCEEDED')
}
const ids = z
  .array(opaqueId)
  .min(1)
  .max(16)
  .refine((v) => new Set(v).size === v.length)

/** Finite, trusted-main policy over actual validated Store rows; no arbitrary provenance inference. */
export class StoredFieldProjector {
  private closed = false
  private readonly models: Model[]
  private readonly catalogs = new Map<string, Catalog>()
  private readonly scopes = new Map<string, string>()
  constructor(
    private readonly source: StoredResultSource,
    models: StoredFieldModel[] = [],
  ) {
    this.models = parse(z.array(modelSchema).max(32), models).map((spec) => {
      const keys = new Set(spec.fields.map((f) => f.key))
      const indices = new Set(spec.fields.map((f) => f.index))
      if (
        keys.size !== spec.fields.length ||
        indices.size !== keys.size ||
        spec.fields.some(
          (f) => f.index > keys.size || new Set(f.dependsOn).size !== f.dependsOn.length,
        )
      )
        reject()
      const dependencies = new Map<string, string[]>()
      const visit = (key: string, path: Set<string>): string[] => {
        if (path.has(key) || !keys.has(key)) return reject()
        const known = dependencies.get(key)
        if (known) return known
        const field = spec.fields.find((f) => f.key === key)!
        const result = [
          ...new Set(
            field.dependsOn.flatMap((dep) => [dep, ...visit(dep, new Set([...path, key]))]),
          ),
        ].sort()
        dependencies.set(key, result)
        return result
      }
      for (const key of keys) visit(key, new Set())
      // zod parsed/copies input; freeze every externally shaped policy object as well.
      for (const field of spec.fields) {
        Object.freeze(field.dependsOn)
        Object.freeze(field)
      }
      Object.freeze(spec.fields)
      Object.freeze(spec.implementation)
      Object.freeze(spec)
      return { spec, digest: hash(spec), dependencies }
    })
  }
  private open(): void {
    if (this.closed) throw new GatewayFailure('CANCELLED')
  }
  private decode(snapshot: StoredResultMaterial): { model: Model; rows: Row[] } {
    const body = JSON.parse(snapshot.bodyText) as { source: Record<string, unknown>; rows: Row[] }
    // Producer identity is validated by StoredResultSource, not selected by a data-controlled tag.
    const matches = this.models.filter(
      ({ spec }) =>
        spec.producerCapability === body.source.producerCapability &&
        spec.definitionId === snapshot.metadata.definitionId &&
        spec.kind === snapshot.metadata.kind &&
        materialCanonical(spec.implementation) ===
          materialCanonical(snapshot.metadata.implementation),
    )
    if (matches.length !== 1) return reject()
    const model = matches[0]
    for (const row of body.rows) {
      if (row.cells.length !== model.spec.fields.length + 1 || row.cells[0] !== model.spec.tag)
        reject()
      for (const field of model.spec.fields) {
        const value = row.cells[field.index]
        if (value === null ? !field.nullable : typeof value !== field.type) reject()
      }
    }
    return { model, rows: body.rows }
  }
  async catalog(input: StoredSelection): Promise<{
    catalogId: string
    metadata: Record<string, unknown>
    fields: {
      fieldId: string
      label: string
      type: string
      nullable: boolean
      requires: string[]
    }[]
  }> {
    this.open()
    if (this.catalogs.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const copied = parse(storedSelectionSchema, input)
    const snapshot = await this.source.load(copied)
    this.open()
    if (this.catalogs.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const { model, rows } = this.decode(snapshot)
    const fields = new Map(model.spec.fields.map((f) => [randomUUID(), f]))
    const catalogId = randomUUID()
    this.catalogs.set(catalogId, { input: copied, snapshot, model, rows, fields })
    return {
      catalogId,
      metadata: structuredClone(snapshot.metadata),
      fields: [...fields].map(([fieldId, field]) => ({
        fieldId,
        label: field.label,
        type: field.type,
        nullable: field.nullable,
        requires: model.dependencies
          .get(field.key)!
          .map((key) => [...fields].find(([, f]) => f.key === key)![0]),
      })),
    }
  }
  private async fresh(catalogId: string, signal?: AbortSignal): Promise<Catalog> {
    this.open()
    const catalog = this.catalogs.get(catalogId)
    if (!catalog) return reject()
    const latest = await this.source.load(catalog.input, signal)
    this.open()
    if (
      this.catalogs.get(catalogId) !== catalog ||
      latest.bodyHash !== catalog.snapshot.bodyHash ||
      latest.sourceFingerprint !== catalog.snapshot.sourceFingerprint
    )
      return reject()
    return catalog
  }
  async select(input: { catalogId: string; fieldIds: string[] }): Promise<FieldProjection> {
    const value = parse(z.object({ catalogId: opaqueId, fieldIds: ids }).strict(), input)
    const catalog = await this.fresh(value.catalogId)
    const fields = value.fieldIds
      .map((id) => catalog.fields.get(id) ?? reject())
      .sort((a, b) => a.index - b.index)
    const keys = new Set(fields.map((f) => f.key))
    if (fields.some((f) => catalog.model.dependencies.get(f.key)!.some((dep) => !keys.has(dep))))
      return reject()
    const metadata = catalog.snapshot.metadata
    const scopeKeys = fields.map((field) =>
      hash({
        domain: 'i06-stored-field-v1',
        projectId: this.source.projectId,
        definitionId: metadata.definitionId,
        producerCapability: catalog.model.spec.producerCapability,
        kind: metadata.kind,
        inputSnapshotId: metadata.inputSnapshotId,
        parametersHash: metadata.parametersHash,
        scope: metadata.scope,
        dependencyVector: metadata.dependencyVector,
        definitionSetDigests: metadata.definitionSetDigests,
        implementation: metadata.implementation,
        modelDigest: catalog.model.digest,
        field,
        dependencies: catalog.model.dependencies.get(field.key)!.map((key) => {
          const dep = catalog.model.spec.fields.find((f) => f.key === key)!
          return {
            field: dep,
            values: catalog.rows.map((row) => [row.rowId, row.ordinal, row.cells[dep.index]]),
          }
        }),
        values: catalog.rows.map((row) => [row.rowId, row.ordinal, row.cells[field.index]]),
      }),
    )
    if (this.scopes.size + new Set(scopeKeys.filter((key) => !this.scopes.has(key))).size > 2048)
      throw new GatewayFailure('INVALID_INPUT')
    const scopes = scopeKeys.map((key) => {
      const id = this.scopes.get(key) ?? randomUUID()
      this.scopes.set(key, id)
      return id
    })
    // Explicit allowlist: never spread full metadata, input parameters/hash or unselected fields.
    const bodyText = materialCanonical({
      source: {
        projectId: this.source.projectId,
        resultId: metadata.resultId,
        jobId: metadata.jobId,
        selection: catalog.input.selection,
        stateAtRead: metadata.state,
        stateMeaning: 'observed-at-read; immutable-selected-result; not-live-current-lease',
        modelId: catalog.model.spec.id,
        modelVersion: catalog.model.spec.version,
      },
      fields: fields.map((f) => ({
        key: f.key,
        label: f.label,
        type: f.type,
        nullable: f.nullable,
      })),
      rows: catalog.rows.map((row, index) => ({
        // Source row identifiers/ordinals can themselves encode unselected data.
        // Use only a projection-local dense position in outgoing content.
        ordinal: index,
        cells: fields.map((f) => row.cells[f.index]),
      })),
    })
    if (Buffer.byteLength(bodyText) > 65536) throw new GatewayFailure('INVALID_INPUT')
    return {
      bodyText,
      bodyHash: createHash('sha256').update(bodyText).digest('hex'),
      scopes,
      rowCount: catalog.rows.length,
      byteCount: Buffer.byteLength(bodyText),
      catalogId: value.catalogId,
      fieldIds: [...value.fieldIds],
    }
  }
  async refresh(projection: FieldProjection, signal?: AbortSignal): Promise<void> {
    await this.fresh(projection.catalogId, signal)
  }
  releaseCatalog(catalogId: string): void {
    this.catalogs.delete(parse(opaqueId, catalogId))
  }
  close(): void {
    this.closed = true
    this.catalogs.clear()
    this.scopes.clear()
  }
}
