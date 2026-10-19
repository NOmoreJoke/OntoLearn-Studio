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
    exitCode: null,
    kill: vi.fn(),
  })
  spawn.mockReturnValue(child)
  const pending = runNativeRecovery('/test-only', [], {})
  child.emit('error', new Error('ENOENT'))
  await expect(pending).rejects.toThrow('ENOENT')
  expect(child.kill).toHaveBeenCalledWith('SIGKILL')
})
