/** Pure cross-workspace domain-snapshot selection (unit-testable, no React). */

/** One workspace-side observation of the project's committed domain identity. */
export type DomainSnapshotCandidate = {
  projectId?: string
  snapshotId?: string
  revision?: number
}

/** The freshest domain snapshot of the open project, by real projectRevision.
 *  Workspaces cache their own last read (ontology session, query read, project
 *  open, learning read); switching between them must never let an older cached
 *  snapshot win over a newer committed one and falsely project "stale".
 *  Candidates from other projects and entries without a real revision or
 *  snapshot id never qualify. */
export function pickLatestDomainSnapshotId(
  activeProjectId: string | undefined,
  candidates: ReadonlyArray<DomainSnapshotCandidate | undefined>,
): string | undefined {
  if (!activeProjectId) return undefined
  let best: { snapshotId: string; revision: number } | undefined
  for (const candidate of candidates) {
    if (
      !candidate ||
      candidate.projectId !== activeProjectId ||
      typeof candidate.revision !== 'number' ||
      !candidate.snapshotId
    )
      continue
    if (!best || candidate.revision > best.revision)
      best = { snapshotId: candidate.snapshotId, revision: candidate.revision }
  }
  return best?.snapshotId
}
