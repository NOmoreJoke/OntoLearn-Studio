import { useEffect, useState } from 'react'
import type { DesktopBridge } from '@ontolearn/contracts'
import { BehaviorWorkspace } from './BehaviorWorkspace'
import { behaviorServices, readBehaviorCatalog } from './bridge'
import type { BehaviorServices, Catalog, Context } from './model'
import type { ReportWorkspaceStatus } from '../mapping/workspace-operation'

export function ConnectedBehaviorWorkspace({
  bridge,
  projectId,
  inputSnapshotId,
  revision,
  onStatus,
  disabled,
}: {
  bridge: DesktopBridge
  projectId: string
  inputSnapshotId: string
  revision: number
  onStatus: ReportWorkspaceStatus
  disabled: boolean
}) {
  const [loaded, setLoaded] = useState<{
    catalog: Catalog
    context: Context
    services: BehaviorServices
  }>()
  const [error, setError] = useState(false)
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    if (disabled || loaded) return
    let live = true
    async function load() {
      try {
        const reply = await bridge.readProject({ editor: 'behavior' })
        if (!live) return
        if (
          !reply.ok ||
          reply.data.projectId !== projectId ||
          reply.data.inputSnapshotId !== inputSnapshotId ||
          reply.data.domain.projectRevision !== revision
        )
          throw new Error('INVALID_SNAPSHOT')
        const catalog = readBehaviorCatalog(reply.data)
        setLoaded({
          catalog,
          context: {
            projectId,
            inputVersion: inputSnapshotId,
            scopeId: crypto.randomUUID(),
            // The new editable definition starts at the editor's declared draft version.
            behaviorVersion: '1',
          },
          services: behaviorServices(bridge, catalog, revision),
        })
      } catch {
        if (live) setError(true)
      }
    }
    void load()
    return () => {
      live = false
    }
  }, [attempt, bridge, disabled, inputSnapshotId, loaded, projectId, revision])
  if (!loaded)
    return error ? (
      <p role="alert">
        无法读取此项目快照。{' '}
        <button
          onClick={() => {
            setError(false)
            setAttempt(attempt + 1)
          }}
        >
          重新读取
        </button>
      </p>
    ) : (
      <p role="status">正在读取项目快照。</p>
    )
  return (
    <fieldset disabled={disabled}>
      <BehaviorWorkspace {...loaded} connected onStatus={onStatus} />
    </fieldset>
  )
}
