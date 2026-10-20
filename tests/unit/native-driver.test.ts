import { EventEmitter } from 'node:events'
import { afterEach, expect, it, vi } from 'vitest'
const { spawn } = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn }))
import { runNativeRecovery } from '../e2e/native-driver'

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
  vi.clearAllMocks()
})

it('rejects and cleans up a bootstrap whose socket never replies', async () => {
  vi.useFakeTimers()
  const child = Object.assign(new EventEmitter(), {
    stderr: new EventEmitter(),
    stdout: new EventEmitter(),
    exitCode: null,
    kill: vi.fn(),
  })
  spawn.mockReturnValue(child)
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
  const pending = runNativeRecovery('/test-only', [], {})
  const rejected = expect(pending).rejects.toThrow('deadline exceeded')
  child.stderr.emit('data', 'Debugger listening on ws://127.0.0.1:1234/test\n')
  await vi.advanceTimersByTimeAsync(45000)
  await rejected
  expect(child.kill).toHaveBeenCalledWith('SIGKILL')
  expect(close).toHaveBeenCalled()
})

it('fails promptly when the native executable cannot start', async () => {
  const child = Object.assign(new EventEmitter(), {
    stderr: new EventEmitter(),
    stdout: new EventEmitter(),
    exitCode: null,
    kill: vi.fn(),
  })
  spawn.mockReturnValue(child)
  const pending = runNativeRecovery('/test-only', [], {})
  child.emit('error', new Error('ENOENT'))
  await expect(pending).rejects.toThrow('ENOENT')
  expect(child.kill).toHaveBeenCalledWith('SIGKILL')
})

it('preserves bounded executable and process output diagnostics when bootstrap exits', async () => {
  const child = Object.assign(new EventEmitter(), {
    stderr: new EventEmitter(),
    stdout: new EventEmitter(),
    exitCode: 7,
    kill: vi.fn(),
  })
  spawn.mockReturnValue(child)
  const pending = runNativeRecovery('/real/electron', ['--user-data-dir=/test-profile'], {})
  child.emit('exit', 7, null)
  // Node can emit exit before remaining pipe data; close follows stdio drain.
  child.stdout.emit('data', 'launcher diagnostic')
  child.stderr.emit('data', 'x'.repeat(70000) + 'sandbox diagnostic')
  child.emit('close', 7, null)
  await expect(pending).rejects.toThrow('sandbox diagnostic')
  await expect(pending).rejects.toThrow('/real/electron')
  await expect(pending).rejects.toThrow('launcher diagnostic')
  await expect(pending).rejects.not.toThrow('x'.repeat(65537))
})
