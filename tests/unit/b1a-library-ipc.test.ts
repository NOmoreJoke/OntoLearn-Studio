/** IPC adapter tests: Electron events are doubles; actual picker is a separate native E2E. */
import { EventEmitter } from 'node:events'
import { describe, expect, it, vi } from 'vitest'
import type { IpcMainInvokeEvent } from 'electron'
import {
  registerDesktopIpc,
  type DesktopIpcDependencies,
} from '../../apps/desktop/src/main/desktop-ipc'

type Handler = (event: IpcMainInvokeEvent, ...args: unknown[]) => Promise<unknown>
function harness() {
  const handlers = new Map<string, Handler>()
  const sender = new EventEmitter(),
    frame = {}
  const event = { sender, senderFrame: frame } as unknown as IpcMainInvokeEvent
  let trusted = true
  const permission = { ok: false }
  const library = {
    switching: false,
    getLocation: vi.fn(() => ({ ok: true, data: {} })),
    choose: vi.fn(async () => ({ ok: true, data: null })),
    reportWorkspace: vi.fn(() => ({ ok: true, data: null })),
    switchLocation: vi.fn(async () => ({ ok: true, data: { restartRequested: true } })),
    invalidateDocument: vi.fn(),
  }
  const catalog = vi.fn(async () => ({ ok: true, data: [] }))
  const cancel = vi.fn(async () => permission)
  const consume = vi.fn()
  const projects = { getProjectCatalog: catalog, managementBlocked: false, queries: {} }
  registerDesktopIpc({
    ipcMain: {
      handle: (channel: string, handler: Handler) => {
        handlers.set(channel, handler)
      },
    } as DesktopIpcDependencies['ipcMain'],
    trusted: () => trusted,
    tasks: { cancelJob: cancel } as unknown as DesktopIpcDependencies['tasks'],
    supervisor: { engineSessionId: 'same-session' } as DesktopIpcDependencies['supervisor'],
    projects: projects as unknown as DesktopIpcDependencies['projects'],
    library: library as unknown as DesktopIpcDependencies['library'],
    replies: {
      receive: async (work: () => Promise<unknown>) => ({ value: await work(), receipt: {} }),
      binding: () => ({ engineSessionId: 'same-session' }),
      consume,
    } as unknown as DesktopIpcDependencies['replies'],
  })
  return {
    handlers,
    event,
    sender,
    library,
    projects,
    catalog,
    cancel,
    consume,
    trust: (value: boolean) => {
      trusted = value
    },
  }
}

describe('B1a native location IPC binding', () => {
  it('uses an app-owned document identity and invalidates it for navigation, replacement frame and destruction', async () => {
    const h = harness()
    const args = { documentNonce: 'renderer nonce', generation: 1, dirty: false, unresolved: false }
    await h.handlers.get('library:workspace')!(h.event, args)
    const first = h.library.reportWorkspace.mock.calls[0] as unknown as [unknown, object]
    expect(first[0]).toBe(args)
    expect(first[1]).not.toBe(args)
    await h.handlers.get('library:switch')!(h.event, { choiceRef: 'opaque' })
    expect((h.library.switchLocation.mock.calls[0] as unknown as [unknown, object])[1]).toBe(
      first[1],
    )
    h.sender.emit('did-start-navigation', {}, 'file:///same#anchor', true, true)
    expect(h.library.invalidateDocument).not.toHaveBeenCalled()
    h.sender.emit('did-start-navigation', {}, 'file:///next', false, true)
    expect(h.library.invalidateDocument).toHaveBeenCalledWith(first[1])
    await h.handlers.get('library:workspace')!(h.event, args)
    const second = (h.library.reportWorkspace.mock.calls[1] as unknown as [unknown, object])[1]
    expect(second).not.toBe(first[1])
    await h.handlers.get('library:workspace')!(
      { ...h.event, senderFrame: {} } as IpcMainInvokeEvent,
      args,
    )
    expect(h.library.invalidateDocument).toHaveBeenLastCalledWith(second)
    const third = (h.library.reportWorkspace.mock.calls[2] as unknown as [unknown, object])[1]
    h.sender.emit('destroyed')
    expect(h.library.invalidateDocument).toHaveBeenLastCalledWith(third)
  })
  it('denies untrusted native calls, fences new operations while switching, and still consumes the original receipt', async () => {
    const h = harness()
    h.trust(false)
    expect(await h.handlers.get('library:choose')!(h.event, { intent: 'open' })).toMatchObject({
      ok: false,
    })
    expect(h.library.choose).not.toHaveBeenCalled()
    h.trust(true)
    const delivery = (await h.handlers.get('project:catalog')!(h.event, {})) as {
      deliveryId: string
    }
    h.library.switching = true
    expect(await h.handlers.get('project:catalog')!(h.event, {})).toMatchObject({ ok: false })
    expect(h.catalog).toHaveBeenCalledTimes(1)
    expect(await h.handlers.get('job:cancel')!(h.event, 'job')).toMatchObject({ ok: false })
    expect(h.cancel).not.toHaveBeenCalled()
    expect(
      await h.handlers.get('project:reply-received')!(h.event, {
        deliveryVersion: 1,
        deliveryId: delivery.deliveryId,
      }),
    ).toMatchObject({ accepted: true })
    expect(h.consume).toHaveBeenCalledOnce()
  })
})
