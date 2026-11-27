import {
  reassembleChangeSetDocument,
  type BridgeResult,
  type ChangeSetPage,
  type ChangeSetPreview,
  type DesktopBridge,
  type JobView,
  type MainlineChangePlanDTO,
  type MainlineProjectReadDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '@ontolearn/contracts/v2'

type ReadyChangeSet = Extract<ChangeSetPreview, { status: 'ready' }>

export type WorkspaceChangePreview = {
  preview: ReadyChangeSet
  rows: unknown[]
  completionCursor: string
}

export function requireWorkspaceReply<T>(response: BridgeResult<T>): T {
  if (!response.ok) throw new Error(response.error.code)
  return response.data
}

export async function prepareWorkspaceChange(
  bridge: Pick<DesktopBridge, 'previewProjectChangeset' | 'getProjectDiffPage'>,
  source: MainlineProjectReadDTO,
  plan: MainlineChangePlanDTO,
  requireCurrent: () => void,
): Promise<WorkspaceChangePreview> {
  requireCurrent()
  const preview = requireWorkspaceReply(
    await bridge.previewProjectChangeset({
      baseRevision: source.domain.projectRevision,
      intent: 'change',
      plan,
    }),
  )
  requireCurrent()
  if (
    preview.status !== 'ready' ||
    preview.intent !== 'change' ||
    preview.targetOperationId !== null ||
    preview.projectId !== source.projectId ||
    preview.inputSnapshotId !== source.inputSnapshotId ||
    preview.baseRevision !== source.domain.projectRevision ||
    preview.manifest.documentKind !== 'diff'
  )
    throw new Error('INVALID_PREVIEW')

  const pages: ChangeSetPage[] = []
  let cursor: string | null = null
  for (let index = 0; index < preview.manifest.segmentCount; index++) {
    const page: ChangeSetPage = requireWorkspaceReply(
      await bridge.getProjectDiffPage({
        previewHash: preview.previewHash,
        documentKind: 'diff',
        pageSize: 32,
        cursor,
      }),
    )
    requireCurrent()
    pages.push(page)
    if (page.complete) {
      const rows = await reassembleChangeSetDocument(preview, pages)
      requireCurrent()
      return { preview, rows, completionCursor: page.nextCursor }
    }
    if (pages.slice(0, -1).some((part) => part.nextCursor === page.nextCursor))
      throw new Error('INVALID_CHANGESET_DOCUMENT')
    cursor = page.nextCursor
  }
  throw new Error('DIFF_INCOMPLETE')
}

export async function commitWorkspaceChange(
  bridge: Pick<DesktopBridge, 'confirmProjectChangeset' | 'commitProjectChangeSet' | 'getJob'>,
  proposal: WorkspaceChangePreview,
  operationId: string,
  requireCurrent: () => void,
): Promise<JobView> {
  requireCurrent()
  const { preview, completionCursor } = proposal
  const confirmation = requireWorkspaceReply(
    await bridge.confirmProjectChangeset({ previewHash: preview.previewHash, completionCursor }),
  )
  requireCurrent()
  if (
    confirmation.projectId !== preview.projectId ||
    confirmation.previewHash !== preview.previewHash ||
    confirmation.preparedPlanRef !== preview.preparedPlanRef ||
    confirmation.inputSnapshotId !== preview.inputSnapshotId ||
    confirmation.parametersHash !== preview.parametersHash
  )
    throw new Error('INVALID_CONFIRMATION')

  let job = requireWorkspaceReply(
    await bridge.commitProjectChangeSet({ operationId, confirmation }),
  )
  const jobId = job.jobId
  const deadline = performance.now() + 30_000
  do {
    requireCurrent()
    if (
      !validateBusiness3('job', job) ||
      job.jobId !== jobId ||
      job.projectId !== preview.projectId ||
      job.operationId !== operationId ||
      job.inputSnapshotId !== preview.inputSnapshotId ||
      job.capability !== 'changeset.commit'
    )
      throw new Error('INVALID_JOB')
    if (job.state === 'succeeded' || job.state === 'failed' || job.state === 'cancelled') return job
    await new Promise<void>((resolve) => setTimeout(resolve, 125))
    requireCurrent()
    job = requireWorkspaceReply(await bridge.getJob(jobId))
  } while (performance.now() < deadline)
  throw new Error('CHANGESET_STATUS_UNKNOWN')
}
