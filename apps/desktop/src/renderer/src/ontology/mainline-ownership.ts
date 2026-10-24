import { reassembleOwnershipDetail, type OwnershipDetailPage } from '@ontolearn/contracts'
import { matchesOwnershipDetail } from '@ontolearn/contracts/v2'
import type { OntologyMainlineBridge } from './mainline-api'
import type { OwnershipConflictDetailViewModel } from './OwnershipConflictDetailView'

const invalid = (): never => {
  throw new Error('INVALID_OWNERSHIP_DETAIL')
}

/** Read-only consumer. Canonical page/document validation and byte assembly stay
 * in the public contract; this adapter binds the preview revision and maps roles.
 */
export async function readOwnershipConflictDetail(
  bridge: Pick<OntologyMainlineBridge, 'getOwnershipConflictDetailPage'>,
  binding: Readonly<{ projectId: string; detailRef: string; sourceBaseRevision: number }>,
  requireCurrent: () => void,
): Promise<OwnershipConflictDetailViewModel> {
  const pages: OwnershipDetailPage[] = []
  let startOrdinal = 0
  let documentHash: string | null = null
  for (let count = 0; count < 512; count++) {
    requireCurrent()
    const args =
      documentHash === null
        ? {
            detailRef: binding.detailRef,
            documentHash: null,
            startOrdinal: 0 as const,
            pageSize: 64,
          }
        : { detailRef: binding.detailRef, documentHash, startOrdinal, pageSize: 64 }
    const result = await bridge.getOwnershipConflictDetailPage(args)
    requireCurrent()
    if (!result.ok) return invalid()
    const page = structuredClone(result.data)
    if (!matchesOwnershipDetail({ ...args, projectId: binding.projectId }, page)) return invalid()
    const first = pages[0]
    if (
      first &&
      (page.manifest.totalBytes !== first.manifest.totalBytes ||
        page.manifest.segmentCount !== first.manifest.segmentCount)
    )
      return invalid()
    pages.push(page)
    if (page.complete) {
      requireCurrent()
      const document = await reassembleOwnershipDetail(
        { projectId: binding.projectId, detailRef: binding.detailRef },
        pages,
      )
      requireCurrent()
      if (document.sourceBaseRevision !== binding.sourceBaseRevision) return invalid()
      return document.reason === 'singleDeclaration'
        ? {
            previewBaseRevision: document.sourceBaseRevision,
            reason: document.reason,
            declaration: { ...document.declaration },
            records: document.existing.map((record) => ({
              ...record,
              role: 'existing',
              slot: { ...document.slot },
            })),
          }
        : {
            previewBaseRevision: document.sourceBaseRevision,
            reason: document.reason,
            records: [
              { ...document.existing, role: 'existing', slot: { ...document.existing.slot } },
              { ...document.incoming, role: 'incoming', slot: { ...document.incoming.slot } },
            ],
          }
    }
    if (page.nextOrdinal === null || page.nextOrdinal <= startOrdinal) return invalid()
    startOrdinal = page.nextOrdinal
    documentHash = pages[0]!.manifest.documentHash
  }
  return invalid()
}
