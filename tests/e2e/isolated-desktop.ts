import { _electron as electron, test, expect } from '@playwright/test'
import { mkdtemp, realpath } from 'node:fs/promises'
import { randomUUID } from 'node:crypto'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const LEDGER_FLAG = 'ONTOLEARN_E2E_TRANSPORT_LEDGER'
const LEDGER_LAUNCH_ID = 'ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID'
const LEDGER_FILE_NAME = 'engine-transport-ledger.jsonl'
const COLLECTION_CAP_BYTES = 524289

/** The real executable/main/preload stay intact; only its profile directory is isolated. */
export interface IsolatedDesktopObservation {
  /** Only an explicit request can ever enable transport observation. */
  observeTransport?: boolean
}

interface TransportIdentity {
  userData: string
  launchId: string | null
  requested: boolean
  enabled: boolean
  appPid: number | null
}

const transportIdentities = new WeakMap<object, TransportIdentity>()

function stringEnv(source: Record<string, string | undefined>): Record<string, string> {
  const env: Record<string, string> = {}
  for (const [key, value] of Object.entries(source)) {
    if (typeof value === 'string') env[key] = value
  }
  delete env[LEDGER_FLAG]
  delete env[LEDGER_LAUNCH_ID]
  return env
}

export async function launchIsolatedDesktop(
  options: NonNullable<Parameters<typeof electron.launch>[0]>,
  observation: IsolatedDesktopObservation = {},
) {
  const args = options.args ?? []
  if (args.some((arg) => arg === '--user-data-dir' || arg.startsWith('--user-data-dir=')))
    throw new Error('An existing profile argument must have one owner')
  const userData = await realpath(await mkdtemp(join(tmpdir(), 'ontolearn-e2e-profile-')))
  const launch: NonNullable<Parameters<typeof electron.launch>[0]> = {
    ...options,
    acceptDownloads: options.acceptDownloads ?? true,
    args: [...args, `--user-data-dir=${userData}`],
  }
  // Default scrub: no launch inherits the observation flag or launch identity.
  if (launch.env) {
    launch.env = stringEnv(launch.env)
  } else if (LEDGER_FLAG in process.env || LEDGER_LAUNCH_ID in process.env) {
    launch.env = stringEnv(process.env)
  }
  const requested = observation.observeTransport === true
  const packaged = Boolean(launch.env?.ONTOLEARN_PACKAGED_EXECUTABLE)
  const enabled = requested && process.platform === 'win32' && !packaged
  const launchId = enabled ? randomUUID() : null
  if (enabled) {
    const env = stringEnv(launch.env ?? process.env)
    env[LEDGER_FLAG] = '1'
    env[LEDGER_LAUNCH_ID] = launchId!
    launch.env = env
  }
  const application = await electron.launch(launch)
  transportIdentities.set(application, {
    userData,
    launchId,
    requested,
    enabled,
    appPid: null,
  })
  try {
    const actual = await application.evaluate(({ app }) => ({
      userData: app.getPath('userData'),
      sessionData: app.getPath('sessionData'),
      appPath: app.getAppPath(),
      packaged: app.isPackaged,
      pid: process.pid,
      argv: process.argv,
    }))
    expect(actual.userData).toBe(userData)
    expect(actual.sessionData).toBe(userData)
    await test.info().attach('isolated-desktop-launch', {
      body: JSON.stringify({ expectedUserData: userData, ...actual }, null, 2),
      contentType: 'application/json',
    })
    const identity = transportIdentities.get(application)
    if (identity) identity.appPid = actual.pid
    return application
  } catch (error) {
    await application.close()
    throw error
  }
}

/**
 * Best-effort bounded collection of this launch's transport ledger, called
 * after the original application.close(). Never throws (nothing here may mask
 * an existing test/close failure), never waits for a footer, reads at most
 * the ledger byte cap plus one detection byte, and attaches fixed incomplete
 * metadata instead of foreign, stale, missing, oversized or partial contents.
 */
export async function collectTransportLedger(application: object): Promise<void> {
  try {
    const identity = transportIdentities.get(application)
    if (!identity) {
      await attachMetadata({ status: 'not-isolated-launch', incomplete: true })
      return
    }
    if (!identity.enabled) {
      await attachMetadata({
        status: 'disabled',
        requested: identity.requested,
        platform: process.platform,
      })
      return
    }
    const file = join(identity.userData, LEDGER_FILE_NAME)
    let bytes: Buffer
    try {
      bytes = await readBounded(file)
    } catch {
      await attachMetadata({ status: 'missing', incomplete: true })
      return
    }
    if (bytes.byteLength > COLLECTION_CAP_BYTES - 1) {
      // The detection byte is not content: anything at or beyond the real
      // ledger byte cap is oversized evidence.
      await attachMetadata({ status: 'oversized', incomplete: true })
      return
    }
    const text = bytes.toString('utf8')
    const firstNewline = text.indexOf('\n')
    const firstLine = firstNewline >= 0 ? text.slice(0, firstNewline) : text
    let header: Record<string, unknown>
    try {
      header = JSON.parse(firstLine) as Record<string, unknown>
    } catch {
      await attachMetadata({ status: 'unparsable-header', incomplete: true })
      return
    }
    const headerLaunchId = typeof header.launchId === 'string' ? header.launchId : null
    const headerPid = typeof header.appPid === 'number' ? header.appPid : null
    if (
      header.kind !== 'header' ||
      headerLaunchId !== identity.launchId ||
      headerPid !== identity.appPid
    ) {
      // Exclusive create failed earlier or a foreign/stale file exists.
      await attachMetadata({
        status: 'foreign-or-stale',
        expectedLaunchId: identity.launchId,
        expectedPid: identity.appPid,
        incomplete: true,
      })
      return
    }
    // A JSONL tail without its terminating LF is an unterminated line: the
    // writer always emits one LF per record, so this shape (for example a
    // short write stopping right after the footer's closing brace) can never
    // count as a complete footer.
    const tailTerminated = text.endsWith('\n')
    const lines = tailTerminated
      ? text
          .slice(0, -1)
          .split('\n')
          .filter((line) => line.length > 0)
      : []
    const last = lines[lines.length - 1]
    let hasFooter = false
    let footerIncomplete: boolean | null = null
    let footerTruncated: boolean | null = null
    try {
      if (typeof last === 'string') {
        const parsed = JSON.parse(last) as Record<string, unknown>
        if (parsed.kind === 'footer') {
          hasFooter = true
          // Only a genuine boolean flag counts: missing, string or null flags
          // leave the corresponding semantics UNKNOWN, never "complete".
          footerIncomplete = typeof parsed.incomplete === 'boolean' ? parsed.incomplete : null
          footerTruncated = typeof parsed.truncated === 'boolean' ? parsed.truncated : null
        }
      }
    } catch {
      hasFooter = false
    }
    // A footer's existence never implies completeness. Completeness requires
    // BOTH flags to be confirmed booleans equal to false; any missing, mistyped
    // or true flag — independently per dimension — leaves incomplete/UNKNOWN.
    const complete = hasFooter && footerIncomplete === false && footerTruncated === false
    const incomplete = !complete
    await attachMetadata({
      status: 'collected',
      hasFooter,
      tailTerminated,
      footerIncomplete,
      footerTruncated,
      incomplete,
      bytes: bytes.byteLength,
      headerLaunchId,
      headerPid,
    })
    await test.info().attach('engine-transport-ledger-content', {
      body: bytes,
      contentType: 'application/octet-stream',
    })
  } catch {
    try {
      await test.info().attach('engine-transport-ledger', {
        body: JSON.stringify({ status: 'collector-failed', incomplete: true }),
        contentType: 'application/json',
      })
    } catch {
      // Observation must never mask the original test or close failure.
    }
  }
}

async function attachMetadata(metadata: Record<string, unknown>): Promise<void> {
  await test.info().attach('engine-transport-ledger', {
    body: JSON.stringify(metadata),
    contentType: 'application/json',
  })
}

/**
 * The exact close-then-collect contract used by the three T02 launch sites:
 * close exactly once, collect even when close rejects, and let the original
 * close error propagate with its original identity after the (never-throwing)
 * collector has run.
 */
export async function closeAndCollectLedger(
  application: object,
  close: () => Promise<void>,
): Promise<void> {
  try {
    await close()
  } finally {
    await collectTransportLedger(application)
  }
}

/** Reads at most the ledger cap plus one detection byte in a single open. */
async function readBounded(file: string): Promise<Buffer> {
  const { open } = await import('node:fs/promises')
  const handle = await open(file, 'r')
  try {
    const buffer = Buffer.alloc(COLLECTION_CAP_BYTES)
    const { bytesRead } = await handle.read(buffer, 0, buffer.byteLength, 0)
    return buffer.subarray(0, bytesRead)
  } finally {
    await handle.close()
  }
}
