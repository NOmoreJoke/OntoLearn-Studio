import { runInNewContext } from 'node:vm'
import { afterEach, expect, it, vi } from 'vitest'
import {
  i04ReadinessExpression,
  installI04NativeHook,
  type I04BootstrapDiagnostics,
} from '../e2e/i04-native-bootstrap'

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

function runtime() {
  const app = {
    commandLine: { hasSwitch: () => false },
    whenReady: () => Promise.resolve(),
    isReady: () => true,
    on: () => {},
    exit: () => {},
    quit: () => {},
    focus: () => {},
  }
  const api: { app?: Partial<typeof app>; BrowserWindow?: object } = {
    app,
    BrowserWindow: { getAllWindows: () => [] },
  }
  const req = Object.assign(
    vi.fn(() => api),
    {
      resolve: vi.fn(() => 'electron'),
      cache: { electron: {} } as Record<string, object>,
    },
  )
  const process = {
    type: 'browser',
    versions: { electron: '44.9.0' },
    getBuiltinModule: () => ({ createRequire: vi.fn(() => req) }),
  }
  return {
    app,
    api,
    req,
    process,
    evaluate: () => runInNewContext(i04ReadinessExpression('/tmp/native.cjs'), { process }),
  }
}

it('waits for real module mapping, the resolver, API members and whenReady in order', async () => {
  const r = runtime()
  delete r.req.cache.electron
  expect(r.evaluate()).toEqual({ state: 'pending', member: 'module mapping' })
  expect(r.req).not.toHaveBeenCalled()
  r.req.cache.electron = {}
  r.req.resolve.mockImplementationOnce(() => {
    throw Object.assign(new Error('not yet mapped'), { code: 'MODULE_NOT_FOUND' })
  })
  expect(r.evaluate()).toEqual({ state: 'pending', member: 'module resolver' })
  expect(r.req).not.toHaveBeenCalled()
  delete r.api.app
  expect(r.evaluate()).toEqual({ state: 'pending', member: 'app' })
  r.api.app = {}
  expect(r.evaluate()).toEqual({ state: 'pending', member: 'app.commandLine' })
  r.api.app = r.app
  let ready!: () => void
  let isReady = false
  r.app.isReady = () => isReady
  r.app.whenReady = () =>
    new Promise<void>((resolve) => {
      ready = resolve
    })
  const pending = r.evaluate()
  isReady = true
  ready()
  await expect(pending).resolves.toEqual({ state: 'ready' })
})

it('does not classify wrong mapping, wrong process, or require failures as transient', () => {
  const r = runtime()
  r.req.resolve.mockReturnValueOnce('/node_modules/electron/index.js')
  expect(r.evaluate).toThrow('unexpected Electron module mapping')
  expect(r.req).not.toHaveBeenCalled()
  r.process.type = 'renderer'
  expect(r.evaluate).toThrow('not an Electron main process')
  r.process.type = 'browser'
  r.req.mockImplementationOnce(() => {
    throw Object.assign(new Error('actual require failure'), { code: 'MODULE_NOT_FOUND' })
  })
  expect(r.evaluate).toThrow('actual require failure')
  r.req.resolve.mockImplementationOnce(() => {
    throw new Error('resolver corruption')
  })
  expect(r.evaluate).toThrow('resolver corruption')
})

it('rejects a broken whenReady contract and propagates getter failures', async () => {
  const r = runtime()
  r.app.isReady = () => false
  await expect(r.evaluate()).rejects.toThrow('inconsistent Electron readiness')
  Object.defineProperty(r.api, 'app', {
    get() {
      throw new Error('getter failure')
    },
  })
  expect(r.evaluate).toThrow('getter failure')
})

type Request = { id: number; params: { expression: string; awaitPromise?: boolean } }
function transport() {
  vi.useFakeTimers()
  const controller = new AbortController()
  const requests: Request[] = []
  const diagnostics: I04BootstrapDiagnostics = { attempts: 0, pending: [], installed: false }
  let respond: (request: Request) => void = () => {}
  class Socket extends EventTarget {
    static OPEN = 1
    readyState = 1
    listeners = new Map<string, Set<EventListenerOrEventListenerObject>>()
    override addEventListener(
      type: string,
      callback: EventListenerOrEventListenerObject | null,
      options?: boolean | AddEventListenerOptions,
    ) {
      if (callback) {
        if (!this.listeners.has(type)) this.listeners.set(type, new Set())
        this.listeners.get(type)!.add(callback)
      }
      super.addEventListener(type, callback, options)
    }
    override removeEventListener(
      type: string,
      callback: EventListenerOrEventListenerObject | null,
      options?: boolean | EventListenerOptions,
    ) {
      if (callback) this.listeners.get(type)?.delete(callback)
      super.removeEventListener(type, callback, options)
    }
    send(wire: string) {
      const request = JSON.parse(wire) as Request
      requests.push(request)
      respond(request)
    }
    reply(request: Request, result: unknown) {
      this.wire({ id: request.id, result: { result } })
    }
    wire(value: unknown) {
      this.dispatchEvent(new MessageEvent('message', { data: JSON.stringify(value) }))
    }
  }
  vi.stubGlobal('WebSocket', Socket)
  const socket = new Socket()
  return {
    socket,
    controller,
    diagnostics,
    requests,
    respond(fn: typeof respond) {
      respond = fn
    },
    start() {
      return installI04NativeHook(
        socket as unknown as WebSocket,
        '/tmp/native.cjs',
        controller.signal,
        diagnostics,
      ).then(
        () => ({ ok: true }),
        (error: unknown) => ({ error }),
      )
    },
    expectClean() {
      expect([...socket.listeners.values()].every((set) => set.size === 0)).toBe(true)
      expect(vi.getTimerCount()).toBe(0)
    },
  }
}

it('waits through pending states and injects once after ready, cleaning every waiter', async () => {
  const t = transport()
  let probes = 0
  t.respond((request) =>
    t.socket.reply(
      request,
      request.params.awaitPromise
        ? {
            type: 'object',
            value: ++probes < 3 ? { state: 'pending', member: 'app' } : { state: 'ready' },
          }
        : { type: 'undefined' },
    ),
  )
  const result = t.start()
  await vi.advanceTimersByTimeAsync(200)
  expect(await result).toEqual({ ok: true })
  expect(t.requests.filter((r) => !r.params.awaitPromise)).toHaveLength(1)
  expect(t.diagnostics).toEqual({ attempts: 3, pending: ['app'], installed: true })
  t.expectClean()
})

it.each(['waiting-reply', 'polling', 'before-start', 'before-injection'])(
  'aborts at %s without a late injection or leaked wait',
  async (phase) => {
    const t = transport()
    t.respond((request) => {
      if (phase === 'polling')
        t.socket.reply(request, { type: 'object', value: { state: 'pending', member: 'app' } })
      if (phase === 'before-injection') {
        t.socket.reply(request, { type: 'object', value: { state: 'ready' } })
        t.controller.abort(new Error('child exited'))
      }
    })
    if (phase === 'before-start') t.controller.abort(new Error('child exited'))
    const result = t.start()
    await vi.advanceTimersByTimeAsync(0)
    t.controller.abort(new Error('child exited'))
    expect(await result).toHaveProperty('error')
    for (const request of [...t.requests])
      t.socket.reply(request, { type: 'object', value: { state: 'ready' } })
    await vi.advanceTimersByTimeAsync(1000)
    expect(t.requests.filter((r) => !r.params.awaitPromise)).toHaveLength(0)
    t.expectClean()
  },
)

it.each(['close', 'error', 'wrong-id', 'malformed', 'exception', 'invalid-state', 'send-throws'])(
  'fails closed on %s and removes transport listeners',
  async (mode) => {
    const t = transport()
    t.respond((request) => {
      if (mode === 'close' || mode === 'error') t.socket.dispatchEvent(new Event(mode))
      if (mode === 'wrong-id')
        t.socket.wire({ id: request.id + 1, result: { result: { type: 'undefined' } } })
      if (mode === 'malformed') t.socket.wire(null)
      if (mode === 'exception')
        t.socket.wire({ id: request.id, result: { exceptionDetails: { text: 'bad readiness' } } })
      if (mode === 'invalid-state')
        t.socket.reply(request, { type: 'object', value: { state: 'ready', extra: true } })
      if (mode === 'send-throws') throw new Error('send failure')
    })
    expect(await t.start()).toHaveProperty('error')
    expect(t.requests).toHaveLength(1)
    t.expectClean()
  },
)

it('does not retry an injected hook that throws or whose reply is lost', async () => {
  for (const lost of [false, true]) {
    const t = transport()
    t.respond((request) => {
      if (request.params.awaitPromise)
        t.socket.reply(request, { type: 'object', value: { state: 'ready' } })
      else if (!lost)
        t.socket.wire({ id: request.id, result: { exceptionDetails: { text: 'hook failed' } } })
    })
    const result = t.start()
    await vi.advanceTimersByTimeAsync(0)
    if (lost) t.controller.abort(new Error('original driver deadline'))
    expect(await result).toHaveProperty('error')
    expect(t.requests.filter((r) => !r.params.awaitPromise)).toHaveLength(1)
    expect(t.diagnostics.installed).toBe(false)
    t.expectClean()
  }
})

it('terminates permanent pending state within the attempt bound', async () => {
  const t = transport()
  t.respond((request) =>
    t.socket.reply(request, { type: 'object', value: { state: 'pending', member: 'app' } }),
  )
  const result = t.start()
  await vi.advanceTimersByTimeAsync(75000)
  expect(String(((await result) as { error: unknown }).error)).toContain('attempt limit exceeded')
  expect(t.requests).toHaveLength(750)
  t.expectClean()
})
