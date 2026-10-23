import type { OntologyMainlineBridge, Preview } from './mainline-api'

const invalid = (): never => {
  throw new Error('INVALID_CHANGESET_DOCUMENT')
}
const sha256 = async (bytes: Uint8Array) =>
  Array.from(
    new Uint8Array(await crypto.subtle.digest('SHA-256', Uint8Array.from(bytes))),
    (byte) => byte.toString(16).padStart(2, '0'),
  ).join('')

/** Check the actual bridge's complete frozen document before enabling confirmation.
 * Cursor authority and canonical wire validation stay in the approved main/preload.
 * This consumer additionally checks byte continuity, order, all hashes and UTF-8.
 */
export async function readFullDiff(
  bridge: OntologyMainlineBridge,
  supplied: Preview,
  requireCurrent: () => void,
): Promise<{ rows: unknown[]; completionCursor: string }> {
  const preview = structuredClone(supplied)
  const manifest = preview.manifest
  if (
    !Number.isSafeInteger(manifest.totalBytes) ||
    manifest.totalBytes < 0 ||
    manifest.totalBytes > 16 * 1024 * 1024 ||
    !Number.isSafeInteger(manifest.segmentCount) ||
    manifest.segmentCount < 1 ||
    manifest.segmentCount > 512 ||
    manifest.segments.length !== manifest.segmentCount
  )
    return invalid()
  let offset = 0
  for (const [index, segment] of manifest.segments.entries()) {
    if (
      segment.ordinal !== index ||
      segment.byteOffset !== offset ||
      !Number.isSafeInteger(segment.rawByteLength) ||
      segment.rawByteLength < 1 ||
      segment.rawByteLength > 32768
    )
      return invalid()
    offset += segment.rawByteLength
  }
  if (offset !== manifest.totalBytes) return invalid()
  const bytes = new Uint8Array(manifest.totalBytes)
  const cursors = new Set<string>()
  let cursor: string | null = null
  let ordinal = 0
  for (let count = 0; count < 512; count++) {
    requireCurrent()
    const result = await bridge.getProjectDiffPage({
      previewHash: preview.previewHash,
      documentKind: manifest.documentKind,
      pageSize: 32,
      cursor,
    })
    requireCurrent()
    if (!result.ok) throw new Error(result.error.code)
    const page = result.data
    if (
      page.projectId !== preview.projectId ||
      page.previewHash !== preview.previewHash ||
      page.documentKind !== manifest.documentKind ||
      page.documentHash !== manifest.documentHash ||
      !page.nextCursor ||
      cursors.has(page.nextCursor) ||
      (!page.complete && page.segments.length === 0)
    )
      return invalid()
    cursors.add(page.nextCursor)
    for (const part of page.segments) {
      const expected = manifest.segments[ordinal]
      if (
        !expected ||
        part.ordinal !== expected.ordinal ||
        part.byteOffset !== expected.byteOffset ||
        part.rawByteLength !== expected.rawByteLength ||
        part.sha256 !== expected.sha256 ||
        part.dataBase64.length > 43692
      )
        return invalid()
      let binary: string
      try {
        binary = atob(part.dataBase64)
      } catch {
        return invalid()
      }
      if (btoa(binary) !== part.dataBase64 || binary.length !== part.rawByteLength) return invalid()
      const value = Uint8Array.from(binary, (character) => character.charCodeAt(0))
      if ((await sha256(value)) !== part.sha256) return invalid()
      requireCurrent()
      bytes.set(value, part.byteOffset)
      ordinal++
    }
    if (page.complete !== (ordinal === manifest.segmentCount)) return invalid()
    if (page.complete) {
      if ((await sha256(bytes)) !== manifest.documentHash) return invalid()
      requireCurrent()
      let rows: unknown
      try {
        rows = JSON.parse(new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes))
      } catch {
        return invalid()
      }
      const valid = (value: unknown): boolean => {
        if (typeof value === 'number') return Number.isFinite(value)
        if (typeof value === 'string')
          return [...value].every((c) => {
            const code = c.codePointAt(0)!
            return code < 0xd800 || code > 0xdfff
          })
        if (Array.isArray(value)) return value.every(valid)
        if (value && typeof value === 'object')
          return Object.entries(value).every(([key, item]) => valid(key) && valid(item))
        return value === null || typeof value === 'boolean'
      }
      if (!Array.isArray(rows) || !valid(rows)) return invalid()
      return { rows, completionCursor: page.nextCursor }
    }
    cursor = page.nextCursor
  }
  return invalid()
}
