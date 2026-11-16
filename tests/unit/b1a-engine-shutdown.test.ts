import { afterEach, describe, expect, it, vi } from 'vitest'
import { EventEmitter } from 'node:events'
import { PassThrough } from 'node:stream'
import { fileURLToPath } from 'node:url'

const processDouble = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn: processDouble.spawn }))
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'
class Child extends EventEmitter {
  stdin = new PassThrough()
  stdout = new PassThrough()
  stderr = new PassThrough()
  exitCode = null
  signalCode = null
  kill = vi.fn(() => true)
}
const active: EngineSupervisor[] = []
const root = fileURLToPath(new URL('../..', import.meta.url))
function supervisor(): EngineSupervisor {
  const value = new EngineSupervisor(
    { packaged: false, appPath: root + '/apps/desktop', resourcesPath: '' },
    { startupMs: 10000 },
  )
  active.push(value)
  return value
}
afterEach(() => {
  for (const value of active.splice(0)) value.stop()
  vi.useRealTimers()
  vi.resetAllMocks()
})
describe('B1a actual child-close barrier', () => {
  it('does not resolve for a starting child until close, even when stop already retired its session', async () => {
    const child = new Child()
    processDouble.spawn.mockReturnValue(child)
    const value = supervisor(),
      startup = value.health().catch(() => null)
    await Promise.resolve()
    value.stop()
    let complete = false
    const barrier = value.stopAndWait(1000).then(() => {
      complete = true
    })
    await Promise.resolve()
    await Promise.resolve()
    expect(child.kill).toHaveBeenCalledOnce()
    expect(complete).toBe(false)
    child.emit('exit', 0, null)
    await Promise.resolve()
    expect(complete).toBe(false)
    child.emit('close', 0, null)
    await barrier
    await startup
    await expect(value.health()).rejects.toThrow()
    expect(processDouble.spawn).toHaveBeenCalledOnce()
  })
  it('retains close responsibility after timeout and permits only a later proven close', async () => {
    vi.useFakeTimers()
    const child = new Child()
    processDouble.spawn.mockReturnValue(child)
    const value = supervisor(),
      startup = value.health().catch(() => null)
    await Promise.resolve()
    const first = value.stopAndWait(20)
    const rejected = expect(first).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
    await vi.advanceTimersByTimeAsync(20)
    await rejected
    let complete = false
    const second = value.stopAndWait(100).then(() => {
      complete = true
    })
    await vi.advanceTimersByTimeAsync(10)
    expect(complete).toBe(false)
    child.emit('close', 0, null)
    await second
    await startup
  })
  it('waits for both retired and replacement startup generations', async () => {
    vi.useFakeTimers()
    const old = new Child(),
      next = new Child()
    processDouble.spawn.mockReturnValueOnce(old).mockReturnValueOnce(next)
    const value = supervisor(),
      first = value.health().catch(() => null)
    await Promise.resolve()
    old.emit('error', new Error('startup failure'))
    await first
    const second = value.health().catch(() => null)
    await vi.advanceTimersByTimeAsync(100)
    expect(processDouble.spawn).toHaveBeenCalledTimes(2)
    let complete = false
    const barrier = value.stopAndWait(1000).then(() => {
      complete = true
    })
    next.emit('close', 0, null)
    await vi.advanceTimersByTimeAsync(10)
    expect(complete).toBe(false)
    old.emit('close', 0, null)
    await barrier
    await second
  })
  it('fences a start waiting in retry backoff before a replacement can spawn', async () => {
    vi.useFakeTimers()
    const old = new Child()
    processDouble.spawn.mockReturnValue(old)
    const value = supervisor(),
      first = value.health().catch(() => null)
    await Promise.resolve()
    old.emit('close', 1, null)
    await first
    const next = value.health().catch(() => null),
      barrier = value.stopAndWait(1000)
    await vi.advanceTimersByTimeAsync(100)
    await barrier
    await next
    expect(processDouble.spawn).toHaveBeenCalledOnce()
  })
  it('awaits a real child close after ignored termination requires forceful shutdown', async () => {
    const actual = await vi.importActual<typeof import('node:child_process')>('node:child_process')
    let spawned: ReturnType<typeof actual.spawn> | undefined
    processDouble.spawn.mockImplementation((...args: Parameters<typeof actual.spawn>) => {
      spawned = actual.spawn(...args)
      return spawned
    })
    const value = new EngineSupervisor(
      { packaged: false, appPath: root + '/apps/desktop', resourcesPath: '' },
      {
        startupMs: 10000,
        command: {
          command: process.execPath,
          args: [
            '-e',
            "process.on('SIGTERM',()=>{});process.stderr.write('ready');setInterval(()=>{},1000)",
          ],
        },
      },
    )
    active.push(value)
    const startup = value.health().catch(() => null)
    await Promise.resolve()
    await new Promise<void>((resolve, reject) => {
      spawned!.stderr!.once('data', () => resolve())
      spawned!.once('error', reject)
    })
    let observedClose = false
    spawned!.once('close', () => {
      observedClose = true
    })
    await value.stopAndWait(5000)
    await startup
    expect(observedClose).toBe(true)
    if (process.platform !== 'win32') expect(spawned!.signalCode).toBe('SIGKILL')
  })
  it('excludes only the current receiver while preserving other unacknowledged replies', async () => {
    const value = new EngineSupervisor(
      { packaged: false, appPath: root + '/apps/desktop', resourcesPath: '' },
      { profile: 'business3' },
    )
    active.push(value)
    const receiver = value.mainlineReplyReceiver()
    const first = await receiver.receive(async () => {
      expect(value.hasUnresolvedResponsibility).toBe(true)
      expect(value.hasOtherMainlineResponsibility).toBe(false)
      return null
    })
    expect(value.hasOtherMainlineResponsibility).toBe(true)
    const second = await receiver.receive(async () => {
      expect(value.hasOtherMainlineResponsibility).toBe(true)
      receiver.consume(first.receipt)
      expect(value.hasOtherMainlineResponsibility).toBe(false)
      expect(value.hasUnresolvedResponsibility).toBe(true)
      return null
    })
    expect(value.hasOtherMainlineResponsibility).toBe(true)
    receiver.consume(second.receipt)
    expect(value.hasUnresolvedResponsibility).toBe(false)
    expect(value.hasOtherMainlineResponsibility).toBe(false)
  })
  it('does not exclude an older UNKNOWN delivery inside a later receiver', async () => {
    const value = new EngineSupervisor(
      { packaged: false, appPath: root + '/apps/desktop', resourcesPath: '' },
      { profile: 'business3' },
    )
    active.push(value)
    const receiver = value.mainlineReplyReceiver()
    await expect(
      receiver.receive(async () => {
        throw new Error('unknown callback outcome')
      }),
    ).rejects.toThrow('unknown callback outcome')
    const next = await receiver.receive(async () => {
      expect(value.hasOtherMainlineResponsibility).toBe(true)
      return null
    })
    receiver.consume(next.receipt)
    expect(value.hasOtherMainlineResponsibility).toBe(true)
    expect(value.hasUnresolvedResponsibility).toBe(true)
  })
})
