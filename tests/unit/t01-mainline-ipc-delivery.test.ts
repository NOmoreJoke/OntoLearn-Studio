/** Protocol adapter units with explicit Electron/service/receiver doubles.
 * Actual issuer accounting and OS stdio are tested in separate runtime cases.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { IpcMainInvokeEvent } from 'electron'
import type { DesktopBridge } from '@ontolearn/contracts'
import {
  registerDesktopIpc,
  type DesktopIpcDependencies,
} from '../../apps/desktop/src/main/desktop-ipc'

const electron = vi.hoisted(() => ({
  bridge: undefined as unknown,
  invoke: vi.fn(),
}))
vi.mock('electron', () => ({
  contextBridge: {
    exposeInMainWorld: (_name: string, value: unknown) => {
      electron.bridge = value
    },
  },
  ipcRenderer: { invoke: electron.invoke, on: vi.fn(), removeListener: vi.fn() },
}))

type Handler = (event: IpcMainInvokeEvent, ...args: unknown[]) => unknown
function harness(withReceiver = true) {
  const handlers = new Map<string, Handler>()
  const sender = {},
    frame = {}
  const original = { sender, senderFrame: frame } as IpcMainInvokeEvent
  let allowed = true,
    session: string | undefined = 'original-session'
  const consume = vi.fn()
  const bindings = new WeakMap<object, string | undefined>()
  const replies = {
    receive: vi.fn(async (work: () => Promise<unknown>) => {
      const originalSession = session
      const value = await work(),
        receipt = {}
      bindings.set(receipt, originalSession)
      return { value, receipt }
    }),
    binding: (receipt: object) => ({ engineSessionId: bindings.get(receipt) }),
    consume,
  }
  const payload = { ok: true as const, data: { items: [], total: 0, nextCursor: null } }
  const catalog = vi.fn(async () => payload)
  registerDesktopIpc({
    ipcMain: {
      handle: (name: string, handler: Handler) => {
        handlers.set(name, handler)
      },
    } as DesktopIpcDependencies['ipcMain'],
    trusted: () => allowed,
    tasks: {} as DesktopIpcDependencies['tasks'],
    supervisor: {
      get engineSessionId() {
        return session
      },
    } as DesktopIpcDependencies['supervisor'],
    projects: {
      getProjectCatalog: catalog,
      getOwnershipConflictDetailPage: catalog,
      queries: {},
    } as unknown as DesktopIpcDependencies['projects'],
    replies: withReceiver ? (replies as unknown as DesktopIpcDependencies['replies']) : undefined,
  })
  const invoke = (channel: string, event = original, ...args: unknown[]) =>
    handlers.get(channel)!(event, ...args)
  electron.invoke.mockImplementation((channel: string, ...args: unknown[]) =>
    invoke(channel, original, ...args),
  )
  return {
    invoke,
    original,
    consume,
    catalog,
    replies,
    payload,
    trust: (value: boolean) => {
      allowed = value
    },
    changeSession: () => {
      session = 'successor-session'
    },
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  electron.bridge = undefined
})
describe('private mainline delivery adapter', () => {
  it('ownership pages use the same exact sender/frame and missing-ACK holding', async () => {
    const h = harness()
    h.trust(false)
    expect(await h.invoke('project:ownership-detail')).toMatchObject({ ok: false })
    expect(h.catalog).not.toHaveBeenCalled()
    h.trust(true)
    const args = {
      detailRef: '00000000-0000-4000-8000-000000000001',
      documentHash: null,
      startOrdinal: 0,
      pageSize: 1,
    }
    const offered = (await h.invoke('project:ownership-detail', h.original, args)) as {
      deliveryId: string
      payload: unknown
    }
    expect(offered.payload).toBe(h.payload)
    expect(h.catalog).toHaveBeenCalledWith(args)
    expect(h.consume).not.toHaveBeenCalled()
    const wrongFrame = { ...h.original, senderFrame: {} } as IpcMainInvokeEvent
    const ack = { deliveryVersion: 1, deliveryId: offered.deliveryId }
    expect(await h.invoke('project:reply-received', wrongFrame, ack)).toMatchObject({ ok: false })
    expect(h.consume).not.toHaveBeenCalled()
    expect(await h.invoke('project:reply-received', h.original, ack)).toMatchObject({
      accepted: true,
    })
    expect(h.consume).toHaveBeenCalledTimes(1)
  })
  it('denies absent receiver or untrusted caller before business work', async () => {
    const missing = harness(false)
    expect(await missing.invoke('project:catalog')).toMatchObject({ ok: false })
    expect(missing.catalog).not.toHaveBeenCalled()
    const denied = harness()
    denied.trust(false)
    expect(await denied.invoke('project:catalog')).toMatchObject({ ok: false })
    expect(denied.replies.receive).not.toHaveBeenCalled()
    expect(denied.catalog).not.toHaveBeenCalled()
  })
  it('requires original frame, session and exact token before consumption', async () => {
    const h = harness()
    const offered = (await h.invoke('project:catalog')) as {
      deliveryVersion: 1
      deliveryId: string
      payload: unknown
    }
    expect(offered.payload).toBe(h.payload)
    expect(h.consume).not.toHaveBeenCalled()
    const ack = { deliveryVersion: 1, deliveryId: offered.deliveryId }
    const otherFrame = { ...h.original, senderFrame: {} } as IpcMainInvokeEvent
    expect(await h.invoke('project:reply-received', otherFrame, ack)).toMatchObject({ ok: false })
    expect(
      await h.invoke('project:reply-received', h.original, { ...ack, extra: true }),
    ).toMatchObject({ ok: false })
    expect(
      await h.invoke('project:reply-received', h.original, {
        ...ack,
        deliveryId: '00000000-0000-4000-8000-000000000000',
      }),
    ).toMatchObject({ ok: false })
    expect(h.consume).not.toHaveBeenCalled()
    expect(await h.invoke('project:reply-received', h.original, ack)).toEqual({
      ...ack,
      accepted: true,
    })
    expect(await h.invoke('project:reply-received', h.original, ack)).toEqual({
      ...ack,
      accepted: true,
    })
    expect(h.consume).toHaveBeenCalledTimes(1)
    h.changeSession()
    expect(await h.invoke('project:reply-received', h.original, ack)).toMatchObject({ ok: false })
    expect(h.consume).toHaveBeenCalledTimes(1)
  })
  it('keeps all sixteen unacknowledged adapter records and rejects another offer', async () => {
    const h = harness(),
      offers = []
    for (let i = 0; i < 16; i++) offers.push(await h.invoke('project:catalog'))
    expect(await h.invoke('project:catalog')).toMatchObject({ ok: false })
    expect(h.catalog).toHaveBeenCalledTimes(16)
    expect(h.consume).not.toHaveBeenCalled()
    const first = offers[0] as { deliveryId: string }
    expect(
      await h.invoke('project:reply-received', h.original, {
        deliveryVersion: 1,
        deliveryId: first.deliveryId,
      }),
    ).toHaveProperty('accepted', true)
    expect(await h.invoke('project:catalog')).toHaveProperty('deliveryVersion', 1)
  })
  it('preload returns the business shape, privately acknowledges and exposes no generic channel', async () => {
    const h = harness()
    vi.resetModules()
    await import('../../apps/desktop/src/preload/index')
    const bridge = electron.bridge as DesktopBridge
    expect(await bridge.getProjectCatalog({ pageSize: 64, cursor: null })).toEqual(h.payload)
    expect(h.consume).toHaveBeenCalledTimes(1)
    expect(Object.keys(bridge)).not.toContain('invoke')
    expect(Object.keys(bridge)).not.toContain('replyReceived')
    expect(Object.keys(bridge)).not.toContain('consume')
  })
  it('preserves an actually received known outcome when private acknowledgment fails', async () => {
    const h = harness()
    electron.invoke.mockImplementation((channel: string, ...args: unknown[]) => {
      if (channel === 'project:reply-received')
        return Promise.reject(new Error('test transport failure'))
      return h.invoke(channel, h.original, ...args)
    })
    vi.resetModules()
    await import('../../apps/desktop/src/preload/index')
    expect(
      await (electron.bridge as DesktopBridge).getProjectCatalog({ pageSize: 64, cursor: null }),
    ).toEqual(h.payload)
    expect(h.consume).not.toHaveBeenCalled()
  })
})
