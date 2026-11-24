import { useEffect, useRef, useState } from 'react'

export type WorkspaceStatus = { dirty: boolean; unresolved: boolean }
export type ReportWorkspaceStatus = (status: WorkspaceStatus) => void

/** A mounted workspace owns its in-flight reply, even when the renderer is retired. */
export function useWorkspaceOperation(
  onStatus: ReportWorkspaceStatus | undefined,
  dirty = false,
  unresolved = false,
) {
  const mounted = useRef(true)
  const active = useRef(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(false)
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])
  useEffect(() => () => onStatus?.({ dirty: false, unresolved: false }), [onStatus])
  useEffect(() => {
    onStatus?.({ dirty, unresolved: active.current || busy || unresolved })
  }, [busy, dirty, onStatus, unresolved])

  async function perform(action: (requireCurrent: () => void) => Promise<void>) {
    if (active.current || !mounted.current) return
    active.current = true
    onStatus?.({ dirty, unresolved: true })
    setBusy(true)
    setError(false)
    const requireCurrent = () => {
      if (!mounted.current) throw new Error('WORKSPACE_RETIRED')
    }
    try {
      await action(requireCurrent)
    } catch {
      if (mounted.current) setError(true)
    } finally {
      active.current = false
      if (mounted.current) setBusy(false)
    }
  }
  return { busy, error, perform }
}
