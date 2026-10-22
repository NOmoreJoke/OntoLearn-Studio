import { EventEmitter } from 'node:events'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import { runInNewContext } from 'node:vm'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'

const { spawn, writeFile } = vi.hoisted(() => ({
  spawn: vi.fn(),
  writeFile: vi.fn<(...args: unknown[]) => Promise<void>>(),
}))
vi.mock('node:child_process', () => ({ spawn }))
vi.mock('node:fs/promises', () => ({ writeFile }))
import { runNativeRecovery } from '../e2e/native-driver'

const profile = resolve(tmpdir(), 'ontolearn-native-unit-profile')
const output = resolve(profile, 'native.json')
const args = [`--user-data-dir=${profile}`]
const env = { I02_NATIVE_EVIDENCE: output }
const executable = '/test-only'
const hookPath = resolve('tests/e2e/native-recovery.cjs')

beforeEach(() => {
  vi.useFakeTimers()
  spawn.mockReset()
  writeFile.mockReset().mockResolvedValue(undefined)
})

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
  vi.clearAllMocks()
})

function makeChild(closeDelay: number | null = 0) {
  const child = Object.assign(new EventEmitter(), {
    pid: 47201,
    spawnargs: [] as string[],
    stderr: Object.assign(new EventEmitter(), { destroy: vi.fn() }),
    stdout: Object.assign(new EventEmitter(), { destroy: vi.fn() }),
    exitCode: null as number | null,
    signalCode: null as NodeJS.Signals | null,
    kill: vi.fn(),
    unref: vi.fn(),
  })
  const end = (code: number | null, signal: NodeJS.Signals | null) => {
    child.exitCode = code
    child.signalCode = signal
    child.emit('exit', code, signal)
    child.emit('close', code, signal)
  }
  let closing = false
  child.kill.mockImplementation((signal: NodeJS.Signals) => {
    if (closeDelay !== null && !closing) {
      closing = true
      setTimeout(() => end(null, signal), closeDelay)
    }
    return true
  })
  spawn.mockImplementation((file: string, launchArgs: string[]) => {
    child.spawnargs = [file, ...launchArgs]
    return child
  })
  return Object.assign(child, { end })
}

type Child = ReturnType<typeof makeChild>
type Outcome = { ok: true } | { ok: false; error: unknown }

async function observe(pending: Promise<void>): Promise<Outcome> {
  try {
    await pending
    return { ok: true }
  } catch (error) {
    return { ok: false, error }
  }
}

function failure(outcome: Outcome): unknown {
  expect(outcome.ok).toBe(false)
  if (outcome.ok) throw new Error('expected failure')
  return outcome.error
}

function errors(error: unknown): unknown[] {
  return error instanceof AggregateError ? (error.errors as unknown[]).flatMap(errors) : [error]
}

function messages(error: unknown): string {
  return errors(error).map(String).join('\n')
}

interface End {
  code: number | null
  signal: string | null
  at: string
}

interface Receipt {
  pid: number
  identityVerified: boolean
  closeWithinBound: boolean
  cleanupWaitMs: number
  exit: End | null
  close: End | null
  cleanupSignals: { reason: string; skipped?: string }[]
  firstFailure: string | null
  cleanupFailures: string[]
  scope: string
}

// Read the mocked write payload, never claim a real file was persisted by a fixture.
function driverReceiptPayload(): Receipt {
  const call = writeFile.mock.calls.find(([path]) => path === `${output}.driver.json`)
  expect(call).toBeDefined()
  return JSON.parse(String(call?.[1])) as Receipt
}

function endpoint(child: Child) {
  child.stderr.emit('data', 'Debugger listening on ws://127.0.0.1:1234/test\n')
}

function silentSocket() {
  const close = vi.fn()
  class SilentSocket extends EventTarget {
    constructor() {
      super()
      queueMicrotask(() => this.dispatchEvent(new Event('open')))
    }
    send() {
      /* Deliberately no inspector response. */
    }
    close = close
  }
  vi.stubGlobal('WebSocket', SilentSocket)
  return close
}

function replyingSocket(
  child: Child,
  options: {
    actualPid?: number
    actualUserData?: string
    identityWriteError?: Error
    socketCloseError?: Error
    ready?: Promise<void>
  } = {},
) {
  const identityWrite = vi.fn<(path: string, data: string, flags: { flag: string }) => void>()
  identityWrite.mockImplementation(() => {
    if (options.identityWriteError) throw options.identityWriteError
  })
  const hook = vi.fn(() => setTimeout(() => child.end(0, null), 0))
  const close = vi.fn(() => {
    if (options.socketCloseError) throw options.socketCloseError
  })
  const requireMock = (name: string) => {
    if (name === 'electron')
      return {
        app: {
          whenReady: () => options.ready ?? Promise.resolve(),
          getPath: (key: string) => {
            expect(key).toBe('userData')
            return options.actualUserData ?? profile
          },
        },
      }
    if (name === 'node:fs') return { writeFileSync: identityWrite }
    if (name === hookPath) return hook()
    throw new Error(`unexpected VM module: ${name}`)
  }
  class ReplySocket extends EventTarget {
    constructor() {
      super()
      queueMicrotask(() => this.dispatchEvent(new Event('open')))
    }
    send(raw: string) {
      void (async () => {
        const request = JSON.parse(raw) as {
          id: number
          method: string
          params: { expression: string; awaitPromise?: boolean }
        }
        try {
          expect(request.method).toBe('Runtime.evaluate')
          expect(request.params.awaitPromise).toBe(true)
          // Execute only the captured identity/bootstrap expression with fake modules.
          // No real child, socket, Electron, hook, filesystem write or fault is used.
          const value = await runInNewContext(request.params.expression, {
            process: {
              pid: options.actualPid ?? child.pid,
              execPath: executable,
              getBuiltinModule: (name: string) => {
                expect(name).toBe('module')
                return { createRequire: () => requireMock }
              },
            },
          })
          this.dispatchEvent(
            new MessageEvent('message', {
              data: JSON.stringify({ id: request.id, result: { result: { value } } }),
            }),
          )
        } catch (error) {
          this.dispatchEvent(
            new MessageEvent('message', {
              data: JSON.stringify({
                id: request.id,
                result: { exceptionDetails: { text: String(error) } },
              }),
            }),
          )
        }
      })()
    }
    close = close
  }
  vi.stubGlobal('WebSocket', ReplySocket)
  return { identityWrite, hook, close }
}

it('rejects and cleans up a bootstrap whose socket never replies', async () => {
  const child = makeChild()
  const close = silentSocket()
  const pending = observe(runNativeRecovery(executable, args, env))
  endpoint(child)
  // The deadline remains 45s; allow the mocked zero-delay close to drain.
  await vi.advanceTimersByTimeAsync(45001)
  expect(messages(failure(await pending))).toContain('deadline exceeded')
  expect(child.kill).toHaveBeenCalledWith('SIGKILL')
  expect(close).toHaveBeenCalled()
  expect(driverReceiptPayload().closeWithinBound).toBe(true)
  expect(driverReceiptPayload().close?.signal).toBe('SIGKILL')
  expect(driverReceiptPayload().firstFailure).toContain('deadline exceeded')
})

it('fails promptly when the native executable cannot start', async () => {
  const child = makeChild()
  const pending = observe(runNativeRecovery(executable, args, env))
  child.emit('error', new Error('ENOENT'))
  await vi.advanceTimersByTimeAsync(1)
  expect(messages(failure(await pending))).toContain('ENOENT')
  expect(child.kill).toHaveBeenCalledWith('SIGKILL')
  expect(driverReceiptPayload().closeWithinBound).toBe(true)
  expect(vi.getTimerCount()).toBe(0)
})

it('preserves bounded executable and process output diagnostics when bootstrap exits', async () => {
  const child = makeChild()
  const pending = observe(runNativeRecovery('/real/electron', args, env))
  child.exitCode = 7
  child.emit('exit', 7, null)
  // Node can emit exit before remaining pipe data; close follows stdio drain.
  child.stdout.emit('data', 'launcher diagnostic')
  child.stderr.emit('data', 'x'.repeat(70000) + 'sandbox diagnostic')
  child.emit('close', 7, null)
  const diagnostic = messages(failure(await pending))
  expect(diagnostic).toContain('sandbox diagnostic')
  expect(diagnostic).toContain('/real/electron')
  expect(diagnostic).toContain('launcher diagnostic')
  expect(diagnostic).not.toContain('x'.repeat(65537))
  expect(driverReceiptPayload().close?.code).toBe(7)
  expect(child.kill).not.toHaveBeenCalled()
})

it.each([
  { launchArgs: [], launchEnv: env },
  { launchArgs: [...args, ...args], launchEnv: env },
  { launchArgs: args, launchEnv: {} },
  { launchArgs: args, launchEnv: { I02_NATIVE_EVIDENCE: resolve(tmpdir(), 'foreign.json') } },
])('rejects missing or conflicting own-run inputs before spawn: %j', async (input) => {
  const result = await observe(runNativeRecovery(executable, input.launchArgs, input.launchEnv))
  expect(messages(failure(result))).toContain('requires this run userData')
  expect(spawn).not.toHaveBeenCalled()
  expect(writeFile).not.toHaveBeenCalled()
})

it('records matching identity before loading the hook, then observes natural close0', async () => {
  const child = makeChild()
  const bridge = replyingSocket(child)
  const pending = observe(runNativeRecovery(executable, args, env))
  endpoint(child)
  await vi.advanceTimersByTimeAsync(1)
  expect(await pending).toEqual({ ok: true })
  expect(bridge.identityWrite).toHaveBeenCalledTimes(1)
  expect(bridge.identityWrite.mock.calls[0][0]).toBe(`${output}.identity.json`)
  expect(bridge.identityWrite.mock.calls[0][2]).toEqual({ flag: 'wx' })
  expect(JSON.parse(bridge.identityWrite.mock.calls[0][1])).toMatchObject({
    expected: { pid: child.pid, userData: profile },
    actual: { pid: child.pid, userData: profile },
    matches: true,
  })
  expect(bridge.identityWrite.mock.invocationCallOrder[0]).toBeLessThan(
    bridge.hook.mock.invocationCallOrder[0],
  )
  expect(bridge.hook).toHaveBeenCalledTimes(1)
  expect(driverReceiptPayload()).toMatchObject({
    pid: child.pid,
    identityVerified: true,
    closeWithinBound: true,
    exit: { code: 0, signal: null },
    close: { code: 0, signal: null },
    cleanupSignals: [],
    firstFailure: null,
  })
  expect(child.kill).not.toHaveBeenCalled()
  expect(child.stdout.destroy).not.toHaveBeenCalled()
  expect(child.unref).not.toHaveBeenCalled()
})

it('waits for app ready before identity persistence or hook loading', async () => {
  let ready!: () => void
  const appReady = new Promise<void>((done) => {
    ready = done
  })
  const child = makeChild()
  const bridge = replyingSocket(child, { ready: appReady })
  const pending = observe(runNativeRecovery(executable, args, env))
  endpoint(child)
  await vi.advanceTimersByTimeAsync(1)
  expect(bridge.identityWrite).not.toHaveBeenCalled()
  expect(bridge.hook).not.toHaveBeenCalled()
  ready()
  await vi.advanceTimersByTimeAsync(1)
  expect(await pending).toEqual({ ok: true })
})

it.each([{ actualUserData: resolve(profile, 'different') }, { actualPid: 47202 }])(
  'preserves mismatching actual identity and never loads the hook: %j',
  async (actual) => {
    const child = makeChild()
    const bridge = replyingSocket(child, actual)
    const pending = observe(runNativeRecovery(executable, args, env))
    endpoint(child)
    await vi.advanceTimersByTimeAsync(1)
    expect(messages(failure(await pending))).toContain('native identity mismatch')
    expect(JSON.parse(bridge.identityWrite.mock.calls[0][1]).matches).toBe(false)
    expect(bridge.hook).not.toHaveBeenCalled()
    expect(driverReceiptPayload().identityVerified).toBe(false)
  },
)

it('never loads the hook when identity persistence fails', async () => {
  const child = makeChild()
  const bridge = replyingSocket(child, { identityWriteError: new Error('identity receipt EACCES') })
  const pending = observe(runNativeRecovery(executable, args, env))
  endpoint(child)
  await vi.advanceTimersByTimeAsync(1)
  expect(messages(failure(await pending))).toContain('identity receipt EACCES')
  expect(bridge.hook).not.toHaveBeenCalled()
  expect(driverReceiptPayload().identityVerified).toBe(false)
})

it('retains the 45s first failure when direct-child close arrives within the 5s cleanup wait', async () => {
  const child = makeChild(4999)
  silentSocket()
  const pending = observe(runNativeRecovery(executable, args, env))
  let completed = false
  void pending.then(() => {
    completed = true
  })
  endpoint(child)
  await vi.advanceTimersByTimeAsync(45000)
  expect(completed).toBe(false)
  await vi.advanceTimersByTimeAsync(4999)
  expect(messages(failure(await pending))).toContain('deadline exceeded')
  expect(driverReceiptPayload().closeWithinBound).toBe(true)
  expect(driverReceiptPayload().cleanupWaitMs).toBe(5000)
  expect(driverReceiptPayload().close?.signal).toBe('SIGKILL')
})

it('fails after the 5s close wait without calling the original PID or descendants settled', async () => {
  const child = makeChild(null)
  silentSocket()
  const pending = observe(runNativeRecovery(executable, args, env))
  let completed = false
  void pending.then(() => {
    completed = true
  })
  endpoint(child)
  await vi.advanceTimersByTimeAsync(45000)
  await vi.advanceTimersByTimeAsync(4999)
  expect(completed).toBe(false)
  await vi.advanceTimersByTimeAsync(1)
  const diagnostic = messages(failure(await pending))
  expect(diagnostic).toContain('deadline exceeded')
  expect(diagnostic).toContain('child close unresolved')
  expect(driverReceiptPayload()).toMatchObject({
    pid: child.pid,
    closeWithinBound: false,
    close: null,
  })
  expect(driverReceiptPayload().scope).toContain('descendant settlement is not proven')
  expect(child.stdout.destroy).toHaveBeenCalledTimes(1)
  expect(child.stderr.destroy).toHaveBeenCalledTimes(1)
  expect(child.unref).toHaveBeenCalledTimes(1)
})

it('does not signal an original PID whose exit was observed while close is unresolved', async () => {
  const child = makeChild(null)
  const pending = observe(runNativeRecovery(executable, args, env))
  child.exitCode = 7
  child.emit('exit', 7, null)
  child.emit('error', new Error('bootstrap transport failure'))
  await vi.advanceTimersByTimeAsync(5000)
  expect(messages(failure(await pending))).toContain('bootstrap transport failure')
  expect(child.kill).not.toHaveBeenCalled()
  expect(driverReceiptPayload().cleanupSignals[0].skipped).toContain(
    'exit or close already observed',
  )
  expect(driverReceiptPayload().closeWithinBound).toBe(false)
})

it('keeps first failure, socket error and unresolved close when final receipt writing also fails', async () => {
  const child = makeChild(null)
  const socketError = new Error('socket-close failed')
  const receiptError = new Error('terminal receipt EIO')
  const bridge = replyingSocket(child, {
    actualUserData: resolve(profile, 'mismatch'),
    socketCloseError: socketError,
  })
  writeFile.mockRejectedValueOnce(receiptError)
  const pending = observe(runNativeRecovery(executable, args, env))
  endpoint(child)
  await vi.advanceTimersByTimeAsync(1)
  await vi.advanceTimersByTimeAsync(5000)
  const error = failure(await pending)
  expect(error).toBeInstanceOf(AggregateError)
  expect(errors(error)).toContain(socketError)
  expect(errors(error)).toContain(receiptError)
  expect(messages(error)).toContain('native identity mismatch')
  expect(messages(error)).toContain('child close unresolved')
  expect(bridge.hook).not.toHaveBeenCalled()
  // This is the attempted write payload; the mocked write rejected.
  expect(driverReceiptPayload().cleanupFailures.join('\n')).toContain('socket-close failed')
  expect(driverReceiptPayload().closeWithinBound).toBe(false)
})
