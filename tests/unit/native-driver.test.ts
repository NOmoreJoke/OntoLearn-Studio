import { EventEmitter } from 'node:events'
import { resolve } from 'node:path'
import { runInNewContext } from 'node:vm'
import { afterEach, expect, it, vi } from 'vitest'
const { spawn } = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn }))
import { runNativeRecovery } from '../e2e/native-driver'

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
  vi.clearAllMocks()
})

type Request = {
  id: number
  method: string
  params: {
    expression: string
    awaitPromise?: boolean
    returnByValue?: boolean
  }
}
function setup() {
  vi.useFakeTimers()
  const child = Object.assign(new EventEmitter(), {
    stderr: new EventEmitter(),
    stdout: new EventEmitter(),
    exitCode: null as number | null,
    signalCode: null as string | null,
    kill: vi.fn(),
  })
  spawn.mockReturnValue(child)
  const requests: Request[] = []
  let respond: (request: Request) => void = () => {}
  class InspectorSocket extends EventTarget {
    static OPEN = 1
    static instance: InspectorSocket
    readyState = 0
    listeners = new Map<string, Set<EventListenerOrEventListenerObject>>()
    constructor() {
      super()
      InspectorSocket.instance = this
      queueMicrotask(() => {
        this.readyState = 1
        this.dispatchEvent(new Event('open'))
      })
    }
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
    send = vi.fn((wire: string) => {
      const request = JSON.parse(wire) as Request
      requests.push(request)
      respond(request)
    })
    reply(request: Request, result: unknown) {
      this.dispatchEvent(
        new MessageEvent('message', {
          data: JSON.stringify({ id: request.id, result: { result } }),
        }),
      )
    }
    close = vi.fn(() => {
      this.readyState = 3
      this.dispatchEvent(new Event('close'))
    })
  }
  vi.stubGlobal('WebSocket', InspectorSocket)
  return {
    child,
    requests,
    get socket() {
      return InspectorSocket.instance
    },
    respond(work: (request: Request) => void) {
      respond = work
    },
    start() {
      const result = runNativeRecovery(
        '/real/electron',
        ['--user-data-dir=/test-profile'],
        {},
      ).then(
        () => ({ ok: true as const }),
        (error: unknown) => ({ error }),
      )
      child.stderr.emit('data', 'Debugger listening on ws://127.0.0.1:1234/test\n')
      return result
    },
    finish(code = 0) {
      child.exitCode = code
      child.emit('exit', code, null)
      child.emit('close', code, null)
    },
    expectClean() {
      const socket = InspectorSocket.instance
      expect([...socket.listeners.values()].every((listeners) => listeners.size === 0)).toBe(true)
      expect(child.stderr.listenerCount('data')).toBe(0)
      expect(vi.getTimerCount()).toBe(0)
    },
  }
}
function realm() {
  const state = { mapped: true, wrongMapping: false, missingAPI: false }
  const app = {
    isPackaged: false,
    whenReady: vi.fn(async () => {}),
    isReady: vi.fn(() => true),
    on: vi.fn(),
    exit: vi.fn(),
    focus: vi.fn(),
    commandLine: { hasSwitch: vi.fn() },
  }
  const load = vi.fn(() =>
    state.missingAPI
      ? {}
      : {
          app,
          dialog: { showMessageBox: vi.fn() },
          BrowserWindow: { getAllWindows: vi.fn() },
        },
  )
  const fromHelper = Object.assign(load, {
    cache: {} as Record<string, unknown>,
    resolve: vi.fn(() => (state.wrongMapping ? '/npm/electron/index.js' : 'electron')),
  })
  return {
    state,
    app,
    load,
    async evaluate(expression: string) {
      fromHelper.cache = state.mapped ? { electron: {} } : {}
      return await runInNewContext(expression, {
        process: {
          getBuiltinModule: () => ({ createRequire: () => fromHelper }),
          type: 'browser',
          versions: { electron: '44.9.0' },
        },
      })
    },
  }
}
function connect(h: ReturnType<typeof setup>, r: ReturnType<typeof realm>) {
  h.respond((request) => {
    if (!request.params.returnByValue) {
      h.socket.reply(request, { type: 'object', objectId: 'original-helper' })
      return
    }
    void r.evaluate(request.params.expression).then(
      (value) => h.socket.reply(request, { type: 'object', value }),
      (error: unknown) =>
        h.socket.dispatchEvent(
          new MessageEvent('message', {
            data: JSON.stringify({
              id: request.id,
              result: { exceptionDetails: { text: String(error) } },
            }),
          }),
        ),
    )
  })
}
const helperRequests = (h: ReturnType<typeof setup>) =>
  h.requests.filter((r) => !r.params.returnByValue)

it('rejects and cleans up a bootstrap whose socket never replies, ignoring a late ready', async () => {
  const h = setup()
  const result = h.start()
  await vi.advanceTimersByTimeAsync(45000)
  expect(await result).toMatchObject({
    error: expect.objectContaining({ message: expect.stringContaining('deadline exceeded') }),
  })
  expect(h.requests).toHaveLength(1)
  h.socket.reply(h.requests[0]!, { type: 'object', value: { state: 'ready' } })
  await vi.advanceTimersByTimeAsync(1000)
  expect(helperRequests(h)).toHaveLength(0)
  expect(h.child.kill).toHaveBeenCalledWith('SIGKILL')
  h.expectClean()
})

it('fails promptly when the native executable cannot start', async () => {
  const h = setup()
  const pending = runNativeRecovery('/test-only', [], {})
  const rejected = expect(pending).rejects.toThrow('ENOENT')
  h.child.emit('error', new Error('ENOENT'))
  await rejected
  expect(h.child.kill).toHaveBeenCalledWith('SIGKILL')
  expect(vi.getTimerCount()).toBe(0)
})

it('preserves bounded executable and drained process output diagnostics when bootstrap exits', async () => {
  const h = setup()
  const pending = runNativeRecovery('/real/electron', ['--user-data-dir=/test-profile'], {})
  h.child.exitCode = 7
  h.child.emit('exit', 7, null)
  const rejected = expect(pending).rejects.toThrow('sandbox diagnostic')
  await vi.advanceTimersByTimeAsync(0)
  setTimeout(() => {
    h.child.stdout.emit('data', 'launcher diagnostic')
    h.child.stderr.emit('data', 'x'.repeat(70000) + 'sandbox diagnostic')
    h.child.emit('close', 7, null)
  }, 100)
  await vi.advanceTimersByTimeAsync(100)
  await rejected
  await expect(pending).rejects.toThrow('sandbox diagnostic')
  await expect(pending).rejects.toThrow('/real/electron')
  await expect(pending).rejects.toThrow('launcher diagnostic')
  await expect(pending).rejects.not.toThrow('x'.repeat(65537))
  expect(vi.getTimerCount()).toBe(0)
})

it('bounds pipe draining after exit by the original deadline and sends no later helper', async () => {
  const h = setup()
  const result = h.start()
  await vi.advanceTimersByTimeAsync(1000)
  h.child.exitCode = 7
  h.child.emit('exit', 7, null)
  await vi.advanceTimersByTimeAsync(0)
  h.socket.reply(h.requests[0]!, { type: 'object', value: { state: 'ready' } })
  await vi.advanceTimersByTimeAsync(44000)
  expect(await result).toMatchObject({
    error: expect.objectContaining({ message: expect.stringContaining('stdio drain:') }),
  })
  expect(h.requests).toHaveLength(1)
  expect(helperRequests(h)).toHaveLength(0)
  h.expectClean()
})

it('waits for mapping without loading a shim, then checks real readiness and loads the original helper once', async () => {
  const h = setup(),
    r = realm()
  r.state.mapped = false
  connect(h, r)
  const result = h.start()
  await vi.advanceTimersByTimeAsync(0)
  expect(h.requests).toHaveLength(1)
  expect(r.load).not.toHaveBeenCalled()
  expect(r.app.whenReady).not.toHaveBeenCalled()
  r.state.mapped = true
  await vi.advanceTimersByTimeAsync(100)
  expect(h.requests.map((request) => request.id)).toEqual([1, 2, 3])
  expect(h.requests[0]!.params).toMatchObject({ awaitPromise: true, returnByValue: true })
  expect(r.app.whenReady).toHaveBeenCalledOnce()
  expect(r.app.isReady).toHaveBeenCalledOnce()
  expect(r.app.focus).not.toHaveBeenCalled()
  expect(r.app.exit).not.toHaveBeenCalled()
  expect(r.app.commandLine.hasSwitch).not.toHaveBeenCalled()
  expect(helperRequests(h).map((request) => request.params.expression)).toEqual([
    `process.getBuiltinModule('module').createRequire(process.execPath)(${JSON.stringify(resolve('tests/e2e/native-recovery.cjs'))})`,
  ])
  h.finish()
  expect(await result).toEqual({ ok: true })
  h.expectClean()
})

it.each(['wrongMapping', 'missingAPI'] as const)(
  'fails immediately on %s with no helper or retry',
  async (kind) => {
    const h = setup(),
      r = realm()
    r.state[kind] = true
    connect(h, r)
    const result = h.start()
    await vi.advanceTimersByTimeAsync(0)
    expect(await result).toMatchObject({
      error: expect.objectContaining({
        message: expect.stringContaining(
          kind === 'wrongMapping'
            ? 'unexpected Electron module mapping'
            : 'missing required Electron main API',
        ),
      }),
    })
    await vi.advanceTimersByTimeAsync(1000)
    expect(h.requests).toHaveLength(1)
    expect(helperRequests(h)).toHaveLength(0)
    expect(r.load).toHaveBeenCalledTimes(kind === 'wrongMapping' ? 0 : 1)
    h.expectClean()
  },
)

it('keeps a stalled app.whenReady inside the original deadline and sends no helper after late fulfillment', async () => {
  const h = setup(),
    r = realm()
  let ready!: () => void
  r.app.whenReady.mockImplementation(
    () =>
      new Promise<void>((resolve) => {
        ready = resolve
      }),
  )
  connect(h, r)
  const result = h.start()
  await vi.advanceTimersByTimeAsync(0)
  expect(r.app.whenReady).toHaveBeenCalledOnce()
  await vi.advanceTimersByTimeAsync(45000)
  expect(await result).toMatchObject({
    error: expect.objectContaining({ message: expect.stringContaining('deadline exceeded') }),
  })
  ready()
  await vi.advanceTimersByTimeAsync(1000)
  expect(h.requests).toHaveLength(1)
  expect(helperRequests(h)).toHaveLength(0)
  h.expectClean()
})

it.each(['exit', 'close', 'error'] as const)(
  'cancels a pending mapping poll on %s without any later send',
  async (kind) => {
    const h = setup(),
      r = realm()
    r.state.mapped = false
    connect(h, r)
    const result = h.start()
    await vi.advanceTimersByTimeAsync(0)
    if (kind === 'exit') h.finish(7)
    else if (kind === 'close') h.socket.close()
    else h.socket.dispatchEvent(new Event('error'))
    await vi.advanceTimersByTimeAsync(0)
    expect(await result).toHaveProperty('error')
    r.state.mapped = true
    await vi.advanceTimersByTimeAsync(1000)
    expect(h.requests).toHaveLength(1)
    expect(helperRequests(h)).toHaveLength(0)
    h.expectClean()
  },
)

it('checks the absolute cutoff again before helper send even if the deadline timer has not fired', async () => {
  const h = setup()
  const began = performance.now()
  h.respond((request) => {
    h.socket.reply(request, { type: 'object', value: { state: 'ready' } })
    vi.spyOn(performance, 'now').mockReturnValue(began + 45000)
  })
  const result = h.start()
  await vi.advanceTimersByTimeAsync(0)
  expect(await result).toMatchObject({
    error: expect.objectContaining({ message: expect.stringContaining('deadline exceeded') }),
  })
  expect(h.requests).toHaveLength(1)
  expect(helperRequests(h)).toHaveLength(0)
  h.expectClean()
})

it.each(['invalid-json', 'send-throw', 'unknown-state', 'helper-error'] as const)(
  'fails on %s and clears the outstanding request without retrying',
  async (kind) => {
    const h = setup()
    h.respond((request) => {
      if (kind === 'send-throw') throw new Error('send failed')
      if (kind === 'invalid-json') {
        h.socket.dispatchEvent(new MessageEvent('message', { data: '{broken' }))
      } else if (kind === 'unknown-state') {
        h.socket.reply(request, { type: 'object', value: { state: 'unexpected' } })
      } else if (request.params.returnByValue) {
        h.socket.reply(request, { type: 'object', value: { state: 'ready' } })
      } else {
        h.socket.dispatchEvent(
          new MessageEvent('message', {
            data: JSON.stringify({
              id: request.id,
              result: { exceptionDetails: { text: 'original helper failure' } },
            }),
          }),
        )
      }
    })
    const result = h.start()
    await vi.advanceTimersByTimeAsync(0)
    expect(await result).toHaveProperty('error')
    await vi.advanceTimersByTimeAsync(1000)
    expect(helperRequests(h)).toHaveLength(kind === 'helper-error' ? 1 : 0)
    expect(h.requests).toHaveLength(kind === 'helper-error' ? 2 : 1)
    h.expectClean()
  },
)
