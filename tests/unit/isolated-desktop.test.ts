import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const { launchMock, attachments, playtestControls } = vi.hoisted(() => ({
  launchMock: vi.fn(),
  attachments: [] as {
    name: string
    body: string | Buffer
    contentType?: string
  }[],
  playtestControls: {
    infoError: null as Error | null,
    attachShouldFail: false as boolean,
    orderLog: [] as string[],
  },
}))

vi.mock('@playwright/test', () => ({
  test: {
    info: () => {
      playtestControls.orderLog.push('info')
      if (playtestControls.infoError) throw playtestControls.infoError
      return {
        attach: async (name: string, options: { body: string | Buffer; contentType?: string }) => {
          playtestControls.orderLog.push(`attach:${name}`)
          if (playtestControls.attachShouldFail) throw new Error(`attach rejected: ${name}`)
          attachments.push({ name, body: options.body, contentType: options.contentType })
        },
      }
    },
  },
  expect: ((actual: unknown) => ({
    toBe: (expected: unknown) => {
      if (actual !== expected)
        throw new Error(`expected ${String(actual)} to be ${String(expected)}`)
    },
  })) as unknown as (typeof import('@playwright/test'))['expect'],
  _electron: { launch: launchMock },
}))

import {
  closeAndCollectLedger,
  collectTransportLedger,
  launchIsolatedDesktop,
} from '../../tests/e2e/isolated-desktop'

const originalPlatform = process.platform
const originalTmpdir = process.env.TMPDIR
let controlledRoot: string

function fakeApplication() {
  return {
    evaluate: async (fn: (arg: { app: Record<string, unknown> }) => unknown) =>
      fn({
        app: {
          getPath: () => launchUserData(),
          getAppPath: () => '/app',
          isPackaged: false,
        },
      }),
    close: vi.fn(async () => undefined),
  }
}

function launchUserData(): string {
  const call = launchMock.mock.calls.at(-1)!
  const args = (call[0] as { args?: string[] }).args ?? []
  const arg = args.find((value) => value.startsWith('--user-data-dir='))!
  return arg.slice('--user-data-dir='.length)
}

function launchEnv(): Record<string, string | undefined> {
  const call = launchMock.mock.calls.at(-1)!
  return ((call[0] as { env?: Record<string, string | undefined> }).env ?? {}) as Record<
    string,
    string | undefined
  >
}

function lastMetadata(): Record<string, unknown> {
  const entry = [...attachments].reverse().find((item) => item.name === 'engine-transport-ledger')
  return JSON.parse(entry!.body as string) as Record<string, unknown>
}

function setPlatform(value: string): void {
  Object.defineProperty(process, 'platform', { value, configurable: true })
}

/** Overrides the helper's evaluate payload (default: matching isolated app). */
function mockLaunch(options: { userData?: () => string; failEvaluate?: boolean } = {}) {
  launchMock.mockImplementationOnce(async () => ({
    evaluate: async (fn: (arg: { app: Record<string, unknown> }) => unknown) => {
      if (options.failEvaluate) throw new Error('evaluate failed')
      return fn({
        app: {
          getPath: () => options.userData?.() ?? launchUserData(),
          getAppPath: () => '/app',
          isPackaged: false,
        },
      })
    },
    close: vi.fn(async () => undefined),
  }))
}

beforeEach(async () => {
  attachments.length = 0
  playtestControls.infoError = null
  playtestControls.attachShouldFail = false
  playtestControls.orderLog.length = 0
  launchMock.mockReset()
  controlledRoot = await mkdtemp(join(tmpdir(), 'isolated-desktop-test-'))
  process.env.TMPDIR = controlledRoot
})

afterEach(async () => {
  setPlatform(originalPlatform)
  if (originalTmpdir === undefined) delete process.env.TMPDIR
  else process.env.TMPDIR = originalTmpdir
})

describe('isolated desktop launch observation wiring', () => {
  it('scrubs inherited ledger keys from every default launch', async () => {
    launchMock.mockImplementationOnce(fakeApplication)
    const application = await launchIsolatedDesktop({
      env: {
        ONTOLEARN_E2E_TRANSPORT_LEDGER: '1',
        ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID: '1a2b3c4d-0000-0000-0000-000000000000',
        OTHER: 'kept',
      },
    })
    const env = launchEnv()
    expect(env.ONTOLEARN_E2E_TRANSPORT_LEDGER).toBeUndefined()
    expect(env.ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID).toBeUndefined()
    expect(env.OTHER).toBe('kept')
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({ status: 'disabled', requested: false })
  })

  it('enables observation only for an explicit Windows unpackaged request', async () => {
    setPlatform('win32')
    launchMock.mockImplementationOnce(fakeApplication)
    const application = await launchIsolatedDesktop({ env: {} }, { observeTransport: true })
    const env = launchEnv()
    expect(env.ONTOLEARN_E2E_TRANSPORT_LEDGER).toBe('1')
    expect(env.ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/,
    )
    void application
  })

  it('stays disabled on macOS, Linux and packaged launches', async () => {
    for (const [platform, env] of [
      ['darwin', {}],
      ['linux', {}],
      ['win32', { ONTOLEARN_PACKAGED_EXECUTABLE: '/some/packaged/app' }],
    ] as const) {
      setPlatform(platform)
      launchMock.mockImplementationOnce(fakeApplication)
      const application = await launchIsolatedDesktop(
        { env: { ...env } },
        { observeTransport: true },
      )
      const launch = launchEnv()
      expect(launch.ONTOLEARN_E2E_TRANSPORT_LEDGER).toBeUndefined()
      await collectTransportLedger(application)
      const metadata = lastMetadata()
      expect(metadata).toMatchObject({ status: 'disabled', requested: true })
    }
  })

  it('creates a unique profile and launch identity per launch', async () => {
    setPlatform('win32')
    launchMock.mockImplementationOnce(fakeApplication)
    const first = await launchIsolatedDesktop({}, { observeTransport: true })
    const firstDir = launchUserData()
    const firstId = launchEnv().ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID
    launchMock.mockImplementationOnce(fakeApplication)
    const second = await launchIsolatedDesktop({}, { observeTransport: true })
    void first
    const secondCall = launchMock.mock.calls.at(-1)!
    const secondDir = (
      (secondCall[0] as { args: string[] }).args.find((value) =>
        value.startsWith('--user-data-dir='),
      ) as string
    ).slice('--user-data-dir='.length)
    const secondId = ((secondCall[0] as { env: Record<string, string> }).env ?? {})
      .ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID
    expect(firstDir).not.toBe(secondDir)
    expect(firstId).not.toBe(secondId)
    void second
  })

  it('preserves the original startup failure path: close once, rethrow first', async () => {
    mockLaunch({ failEvaluate: true })
    await expect(launchIsolatedDesktop({}, { observeTransport: true })).rejects.toMatchObject({
      message: 'evaluate failed',
    })
    const application = await launchMock.mock.results[0]!.value
    expect(application.close).toHaveBeenCalledTimes(1)
  })
})

describe('isolated desktop ledger collection', () => {
  async function observedLaunch() {
    setPlatform('win32')
    launchMock.mockImplementationOnce(fakeApplication)
    const application = await launchIsolatedDesktop({}, { observeTransport: true })
    const userData = launchUserData()
    const launchId = launchEnv().ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID!
    return { application, userData, launchId }
  }

  function headerLine(launchId: string): string {
    return JSON.stringify({
      kind: 'header',
      schema: 1,
      owner: 'owner',
      launchId,
      appPid: process.pid,
      platform: 'win32',
      seq: 1,
      monotonicMs: 0,
    })
  }

  function footerLine(overrides: Record<string, unknown> = {}): string {
    return JSON.stringify({
      kind: 'footer',
      stopRequested: true,
      childrenOpenCount: 0,
      childrenOverflow: false,
      recordsWritten: 1,
      bytesWritten: 100,
      droppedQueue: 0,
      overflow: 0,
      writeErrors: 0,
      recordErrors: 0,
      truncated: false,
      incomplete: false,
      seq: 2,
      monotonicMs: 1,
      ...overrides,
    })
  }

  it('reports a missing file as incomplete and never throws', async () => {
    const { application } = await observedLaunch()
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({ status: 'missing', incomplete: true })
  })

  it('collects matching current-launch evidence with a complete footer', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n${footerLine()}\n`,
      'utf8',
    )
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({
      status: 'collected',
      hasFooter: true,
      incomplete: false,
      headerLaunchId: launchId,
      headerPid: process.pid,
    })
    expect(attachments.some((item) => item.name === 'engine-transport-ledger-content')).toBe(true)
  })

  it('keeps the footer incomplete semantics instead of trusting its existence', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n${footerLine({ incomplete: true, truncated: true })}\n`,
      'utf8',
    )
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({
      status: 'collected',
      hasFooter: true,
      footerIncomplete: true,
      footerTruncated: true,
      incomplete: true,
    })
  })

  it('marks the evidence incomplete when only truncated is unknown or mistyped', async () => {
    const cases: Array<[string, Record<string, unknown>]> = [
      ['missing', { truncated: undefined }],
      ['string', { truncated: 'false' }],
      ['null', { truncated: null }],
    ]
    for (const [label, overrides] of cases) {
      const { application, userData, launchId } = await observedLaunch()
      await writeFile(
        join(userData, 'engine-transport-ledger.jsonl'),
        `${headerLine(launchId)}\n${footerLine({ incomplete: false, ...overrides })}\n`,
        'utf8',
      )
      await collectTransportLedger(application)
      const metadata = lastMetadata()
      expect(metadata, label).toMatchObject({
        status: 'collected',
        hasFooter: true,
        incomplete: true,
      })
    }
  })

  it('marks the evidence incomplete when only incomplete is unknown or mistyped', async () => {
    const cases: Array<[string, Record<string, unknown>]> = [
      ['missing', { incomplete: undefined }],
      ['string', { incomplete: 'false' }],
      ['null', { incomplete: null }],
    ]
    for (const [label, overrides] of cases) {
      const { application, userData, launchId } = await observedLaunch()
      await writeFile(
        join(userData, 'engine-transport-ledger.jsonl'),
        `${headerLine(launchId)}\n${footerLine({ truncated: false, ...overrides })}\n`,
        'utf8',
      )
      await collectTransportLedger(application)
      const metadata = lastMetadata()
      expect(metadata, label).toMatchObject({
        status: 'collected',
        hasFooter: true,
        incomplete: true,
      })
    }
  })

  it('accepts completeness only with both flags confirmed false', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n${footerLine({ incomplete: false, truncated: false })}\n`,
      'utf8',
    )
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({
      status: 'collected',
      hasFooter: true,
      footerIncomplete: false,
      footerTruncated: false,
      incomplete: false,
    })
  })

  it('treats a footer missing only its terminating LF as unterminated', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n${footerLine({ incomplete: false, truncated: false })}`,
      'utf8',
    )
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({
      status: 'collected',
      hasFooter: false,
      tailTerminated: false,
      incomplete: true,
    })
  })

  it('never attaches a foreign or stale file as current contents', async () => {
    const { application, userData } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine('00000000-0000-4000-8000-0000000000ff')}\n${footerLine()}\n`,
      'utf8',
    )
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({ status: 'foreign-or-stale', incomplete: true })
    expect(attachments.some((item) => item.name === 'engine-transport-ledger-content')).toBe(false)
  })

  it('treats a partial tail without footer as incomplete', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n{"kind":"resp`,
      'utf8',
    )
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({ status: 'collected', hasFooter: false, incomplete: true })
  })

  it('rejects an unparsable header without attaching contents', async () => {
    const { application, userData } = await observedLaunch()
    await writeFile(join(userData, 'engine-transport-ledger.jsonl'), 'not-json\n', 'utf8')
    await collectTransportLedger(application)
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({ status: 'unparsable-header', incomplete: true })
  })

  it('reads at most the ledger cap plus one detection byte', async () => {
    const { application, userData, launchId } = await observedLaunch()
    const file = join(userData, 'engine-transport-ledger.jsonl')
    await writeFile(file, `${headerLine(launchId)}\n${footerLine()}\n`, 'utf8')
    // At exactly the cap the evidence is collected; one extra byte is oversized.
    const exact = Buffer.concat([
      Buffer.from(`${headerLine(launchId)}\n`, 'utf8'),
      Buffer.alloc(524288 - headerLine(launchId).length - 1),
    ])
    await writeFile(file, exact)
    await collectTransportLedger(application)
    let metadata = lastMetadata()
    expect(metadata.status).toBe('collected')
    attachments.length = 0
    await writeFile(file, Buffer.concat([exact, Buffer.alloc(1)]))
    await collectTransportLedger(application)
    metadata = lastMetadata()
    expect(metadata).toMatchObject({ status: 'oversized', incomplete: true })
    expect(attachments.some((item) => item.name === 'engine-transport-ledger-content')).toBe(false)
  })

  it('never masks failures when test.info() itself throws', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n${footerLine()}\n`,
      'utf8',
    )
    playtestControls.infoError = new Error('info unavailable')
    await expect(collectTransportLedger(application)).resolves.toBeUndefined()
    playtestControls.infoError = null
  })

  it('swallows a total attachment failure without throwing', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n${footerLine()}\n`,
      'utf8',
    )
    playtestControls.attachShouldFail = true
    await expect(collectTransportLedger(application)).resolves.toBeUndefined()
    playtestControls.attachShouldFail = false
  })

  it('returns the exact closeError reference and collects only after close', async () => {
    const { application, userData, launchId } = await observedLaunch()
    await writeFile(
      join(userData, 'engine-transport-ledger.jsonl'),
      `${headerLine(launchId)}\n${footerLine()}\n`,
      'utf8',
    )
    const closeError = new Error('close rejected')
    let closeCalls = 0
    // Only the close/collect sequence under observation is ordered here.
    playtestControls.orderLog.length = 0
    const error = await closeAndCollectLedger(application, async () => {
      closeCalls += 1
      playtestControls.orderLog.push('close')
      throw closeError
    }).then(
      () => null,
      (cause: unknown) => cause,
    )
    expect(closeCalls).toBe(1)
    // The identical reference propagates, not a same-message clone.
    expect(error).toBe(closeError)
    // Real collector entry points run strictly after the single close.
    // The frozen collector enters info once per attachment: metadata first,
    // then content. Close precedes every collector entry.
    expect(playtestControls.orderLog).toEqual([
      'close',
      'info',
      'attach:engine-transport-ledger',
      'info',
      'attach:engine-transport-ledger-content',
    ])
    expect(attachments.some((item) => item.name === 'engine-transport-ledger')).toBe(true)
  })

  it('keeps the original closeError priority when collection also fails', async () => {
    const { application } = await observedLaunch()
    const closeError = new Error('close rejected first')
    const error = await closeAndCollectLedger(application, async () => {
      playtestControls.orderLog.push('close')
      throw closeError
    }).then(
      () => null,
      (cause: unknown) => cause,
    )
    expect(error).toBe(closeError)
    // A collector whose info entry throws must never mask the close error.
    playtestControls.infoError = new Error('info broken')
    const errorWithBrokenInfo = await closeAndCollectLedger(application, async () => {
      throw closeError
    }).then(
      () => null,
      (cause: unknown) => cause,
    )
    expect(errorWithBrokenInfo).toBe(closeError)
    playtestControls.infoError = null
    playtestControls.attachShouldFail = true
    const errorWithBrokenAttach = await closeAndCollectLedger(application, async () => {
      throw closeError
    }).then(
      () => null,
      (cause: unknown) => cause,
    )
    expect(errorWithBrokenAttach).toBe(closeError)
    playtestControls.attachShouldFail = false
  })

  it('reports non-isolated applications and never masks failures', async () => {
    await collectTransportLedger({})
    const metadata = lastMetadata()
    expect(metadata).toMatchObject({ status: 'not-isolated-launch', incomplete: true })
  })
})
