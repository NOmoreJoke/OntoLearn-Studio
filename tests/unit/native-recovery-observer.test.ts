import { EventEmitter } from 'node:events'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { runInNewContext } from 'node:vm'
import { expect, it, vi } from 'vitest'

const source = readFileSync(resolve('tests/e2e/native-recovery.cjs'), 'utf8')
const fault = 'for (;;) {}'
function setup(
  options: {
    observerThrows?: boolean
    observerOverCap?: boolean
    recordThrows?: boolean
    writeError?: Error
  } = {},
) {
  const timers: { work: () => void; delay: number }[] = []
  const writes: string[] = []
  const inputs: unknown[] = []
  const scripts: string[] = []
  const app = Object.assign(new EventEmitter(), {
    isPackaged: false,
    commandLine: { hasSwitch: () => false },
    focus: vi.fn(),
    exit: vi.fn(),
  })
  const dialog = {
    showMessageBox: async (...args: unknown[]) => {
      void args
      return { response: 1 }
    },
  }
  const inspector = { close: vi.fn(), url: () => undefined }
  let rejectFault: (error: Error) => void = () => {}
  let scriptError: Error | undefined
  let inputError: Error | undefined
  let windowSequence = 0
  class Window extends EventEmitter {
    id = ++windowSequence
    destroyed = false
    diagnosticReadsThrow = false
    contents = Object.assign(new EventEmitter(), {
      id: this.id + 100,
      isDestroyed: () => this.destroyed,
      isLoadingMainFrame: () => false,
      forcefullyCrashRenderer: vi.fn(() =>
        this.contents.emit('render-process-gone', {}, { reason: 'killed' }),
      ),
      executeJavaScript: vi.fn((script: string) => {
        scripts.push(script)
        if (script === fault)
          return new Promise((_resolve, reject) => {
            rejectFault = reject
          })
        if (scriptError) return Promise.reject(scriptError)
        return Promise.resolve(
          script === 'window.ontolearn.getEngineHealth()'
            ? { ok: true }
            : { status: '尚未检查', bridge: 'function' },
        )
      }),
      sendInputEvent: vi.fn((input: unknown) => {
        inputs.push(input)
        if (inputError) throw inputError
      }),
    })
    get webContents() {
      if (this.diagnosticReadsThrow) throw new Error('private diagnostic getter failure')
      return this.contents
    }
    isDestroyed() {
      if (this.diagnosticReadsThrow) throw new Error('private destroyed read failure')
      return this.destroyed
    }
    isVisible() {
      if (this.diagnosticReadsThrow) throw new Error('private visible read failure')
      if (this.destroyed) throw new Error('destroyed visible read')
      return true
    }
    isFocused() {
      if (this.diagnosticReadsThrow) throw new Error('private focused read failure')
      if (this.destroyed) throw new Error('destroyed focused read')
      return true
    }
    show = vi.fn()
    focus = vi.fn()
  }
  runInNewContext(source, {
    require(name: string) {
      if (name === 'electron') return { app, dialog, BrowserWindow: { getAllWindows: () => [] } }
      if (name === 'node:inspector') return inspector
      if (name === 'node:fs')
        return {
          writeFileSync(_path: string, data: string) {
            if (options.writeError) throw options.writeError
            writes.push(data)
          },
        }
      throw new Error(`Unexpected module ${name}`)
    },
    process: { versions: { electron: 'synthetic' }, env: { I02_NATIVE_EVIDENCE: '/synthetic' } },
    Number: options.recordThrows
      ? {
          isInteger() {
            throw new Error('observer record failure')
          },
        }
      : Number,
    Buffer: {
      byteLength(value: string, encoding: BufferEncoding) {
        if (options.observerThrows) throw new Error('observer serialization failure')
        if (options.observerOverCap) return 4097
        return Buffer.byteLength(value, encoding)
      },
    },
    setTimeout(work: () => void, delay: number) {
      timers.push({ work, delay })
      return { unref() {} }
    },
  })
  const timer = (delay: number) => {
    const found = timers.filter((item) => item.delay === delay)
    expect(found).toHaveLength(1)
    return found[0].work
  }
  timer(150)()
  return {
    app,
    dialog,
    inputs,
    scripts,
    timers,
    timer,
    writes,
    rejectFault: (error: Error) => rejectFault(error),
    failScript: (error: Error) => (scriptError = error),
    failInput: (error: Error) => (inputError = error),
    window() {
      const window = new Window()
      app.emit('browser-window-created', {}, window)
      window.contents.emit('did-finish-load')
      return window
    },
    saved: () => JSON.parse(writes.at(-1)!),
  }
}
async function settle() {
  for (let i = 0; i < 8; i++) await Promise.resolve()
}
async function secondWindow(options: Parameters<typeof setup>[0] = {}) {
  const h = setup(options)
  const first = h.window()
  await settle()
  const second = h.window()
  await settle()
  return { ...h, first, second }
}

it('retains original successful fields, three windows, fault, inputs and timers without diagnostics', async () => {
  const h = await secondWindow()
  await h.dialog.showMessageBox(h.first, {})
  h.timer(250)()
  h.second.emit('unresponsive')
  await h.dialog.showMessageBox(h.second, {})
  h.window()
  await settle()
  const data = h.saved()
  expect(data.result).toBe('PASS')
  expect(data.windows).toBe(3)
  expect(data.events).toEqual(['killed', 'unresponsive'])
  expect(data.prompts).toHaveLength(2)
  expect(data.health).toHaveLength(3)
  expect(data).not.toHaveProperty('failureObservation')
  expect(data).not.toHaveProperty('error')
  expect(h.app.exit.mock.calls).toEqual([[0]])
  expect(h.timers.map((item) => item.delay)).toEqual([40000, 150, 250])
  expect(h.scripts).toHaveLength(7)
  expect(h.scripts.filter((script) => script === fault)).toHaveLength(1)
  expect(h.inputs).toEqual([
    { type: 'mouseDown', x: 400, y: 400, button: 'left', clickCount: 1 },
    { type: 'mouseUp', x: 400, y: 400, button: 'left', clickCount: 1 },
  ])
})

it('caps passive records and scalars after repeated events, without claiming execution ACKs', async () => {
  const h = await secondWindow()
  h.second.id = Number.MAX_SAFE_INTEGER
  h.second.contents.id = Infinity
  for (let i = 0; i < 2000; i++) h.second.emit('unresponsive')
  h.timer(250)()
  h.timer(40000)()
  const data = h.saved()
  const observation = data.failureObservation
  expect(data.error).toBe('native recovery timeout')
  expect(h.app.exit.mock.calls).toEqual([[1]])
  expect(
    Buffer.byteLength(JSON.stringify({ failureObservation: observation }, null, 2), 'utf8'),
  ).toBeLessThanOrEqual(4096)
  expect(observation.records).toHaveLength(16)
  expect(observation.overwritten).toBeGreaterThan(0)
  expect(observation.counts).toHaveLength(16)
  expect(observation.counts[4]).toBe(2000)
  expect(observation.records.every((row: number[]) => row.length === 8)).toBe(true)
  expect(
    observation.records
      .flat()
      .every((value: number) => Number.isInteger(value) && value >= -1 && value <= 2147483647),
  ).toBe(true)
  expect(observation.records.at(-1).slice(2, 4)).toEqual([-1, -1])
  expect(observation.rendererLoopStarted).toBe('UNKNOWN')
  expect(observation.productHandlerEntered).toBe('UNKNOWN')
  expect(observation.counts[7]).toBe(1) // A Promise returned, not a renderer start ACK.
  expect(observation.counts[11]).toBe(1)
  expect(observation.counts[13]).toBe(1)
})

it.each(['throwing', 'destroyed'])(
  'preserves watchdog save/exit with %s diagnostic reads',
  async (kind) => {
    const h = await secondWindow()
    if (kind === 'throwing') h.second.diagnosticReadsThrow = true
    else h.second.destroyed = true
    h.timer(40000)()
    const data = h.saved()
    expect(data.error).toBe('native recovery timeout')
    expect(h.app.exit.mock.calls).toEqual([[1]])
    expect(data.failureObservation.records.at(-1).slice(5, 7)).toEqual([-1, -1])
    expect(JSON.stringify(data.failureObservation)).not.toContain('private')
    if (kind === 'throwing') expect(data.failureObservation.readErrors).toBeGreaterThan(0)
  },
)

it('does not let observer serialization failure skip the original write and exit', async () => {
  const h = await secondWindow({ observerThrows: true })
  h.timer(40000)()
  expect(h.saved().error).toBe('native recovery timeout')
  expect(h.saved()).not.toHaveProperty('failureObservation')
  expect(h.app.exit.mock.calls).toEqual([[1]])
})

it('uses a bounded fixed fallback when the diagnostic byte measurement exceeds its cap', async () => {
  const h = await secondWindow({ observerOverCap: true })
  h.timer(40000)()
  expect(h.saved().failureObservation).toEqual({
    schema: 'c1-native-passive-v1',
    limitBytes: 4096,
    unavailable: 'byte-cap',
    rendererLoopStarted: 'UNKNOWN',
    productHandlerEntered: 'UNKNOWN',
  })
  expect(Buffer.byteLength(JSON.stringify(h.saved().failureObservation))).toBeLessThan(4096)
  expect(h.saved().error).toBe('native recovery timeout')
  expect(h.app.exit.mock.calls).toEqual([[1]])
})

it('isolates an outer record failure while preserving the original watchdog write and exit', async () => {
  const h = await secondWindow({ recordThrows: true })
  h.timer(40000)()
  expect(h.saved().error).toBe('native recovery timeout')
  expect(h.saved().failureObservation.records).toEqual([])
  expect(h.saved().failureObservation.rendererLoopStarted).toBe('UNKNOWN')
  expect(h.app.exit.mock.calls).toEqual([[1]])
})

it('preserves the original write exception identity rather than substituting diagnostics or exit', () => {
  const failure = new Error('original native evidence write failure')
  const h = setup({ observerThrows: true, writeError: failure })
  let caught: unknown
  try {
    h.timer(40000)()
  } catch (error) {
    caught = error
  }
  expect(caught).toBe(failure)
  expect(h.app.exit).not.toHaveBeenCalled()
})

it.each([false, true])(
  'preserves original rejected fault handling with destroyed=%s',
  async (destroyed) => {
    const h = await secondWindow()
    const failure = new Error('original fault rejection')
    h.second.destroyed = destroyed
    h.rejectFault(failure)
    await settle()
    if (destroyed) {
      expect(h.writes).toHaveLength(0)
      h.timer(40000)()
      expect(h.saved().hangScriptDisposed).toBe(String(failure))
      expect(h.saved().error).toBe('native recovery timeout')
    } else expect(h.saved().error).toBe(String(failure))
    expect(h.saved().failureObservation.counts[8]).toBe(1)
    expect(h.app.exit.mock.calls).toEqual([[1]])
  },
)

it('does not swallow an original synchronous input exception or issue the second input', async () => {
  const h = await secondWindow()
  const failure = new Error('original input failure')
  h.failInput(failure)
  let caught: unknown
  try {
    h.timer(250)()
  } catch (error) {
    caught = error
  }
  expect(caught).toBe(failure)
  expect(h.inputs).toHaveLength(1)
  expect(h.writes).toHaveLength(0)
  h.timer(40000)()
  const counts = h.saved().failureObservation.counts
  expect(counts[10]).toBe(1)
  expect(counts[11]).toBe(0)
  expect(counts[12]).toBe(0)
})

it('retains original drive failure formatting and save/exit', async () => {
  const h = setup()
  const failure = new Error('original initial state read failure')
  h.failScript(failure)
  h.window()
  await settle()
  expect(h.saved().error).toBe(String(failure))
  expect(h.app.exit.mock.calls).toEqual([[1]])
  expect(h.saved().failureObservation.counts[14]).toBe(1)
})
