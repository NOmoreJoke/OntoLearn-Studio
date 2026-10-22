import { spawn } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import { dirname, isAbsolute, resolve as resolvePath } from 'node:path'

// Packaged Electron ignores arbitrary --require. Bootstrap a test hook through
// the MAIN inspector, then close it before any faults. No renderer CDP/loader.
export async function runNativeRecovery(
  executable: string,
  args: string[],
  env: NodeJS.ProcessEnv,
): Promise<void> {
  const userDataArgs = args.filter((arg) => arg.startsWith('--user-data-dir='))
  const expectedUserData = userDataArgs[0]?.slice('--user-data-dir='.length)
  const evidencePath = env.I02_NATIVE_EVIDENCE
  if (
    userDataArgs.length !== 1 ||
    !expectedUserData ||
    !isAbsolute(expectedUserData) ||
    resolvePath(expectedUserData) !== expectedUserData ||
    !evidencePath ||
    !isAbsolute(evidencePath) ||
    dirname(evidencePath) !== expectedUserData
  )
    throw new Error('native recovery requires this run userData and evidence directory')
  const identityPath = `${evidencePath}.identity.json`
  const child = spawn(executable, ['--inspect=0', ...args], {
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  type End = { code: number | null; signal: NodeJS.Signals | null; at: string }
  let exited: End | undefined
  let closed: End | undefined
  const closeObserved = new Promise<void>((done) =>
    child.once('close', (code, signal) => {
      closed = { code, signal, at: new Date().toISOString() }
      done()
    }),
  )
  child.once('exit', (code, signal) => {
    exited = { code, signal, at: new Date().toISOString() }
  })
  const cleanupSignals: {
    at: string
    reason: string
    sent?: boolean
    error?: string
    skipped?: string
  }[] = []
  const requestKill = (reason: string) => {
    const attempt: (typeof cleanupSignals)[number] = { at: new Date().toISOString(), reason }
    cleanupSignals.push(attempt)
    if (exited || closed) {
      attempt.skipped = 'original exit or close already observed'
      return
    }
    try {
      attempt.sent = child.kill('SIGKILL')
    } catch (error) {
      attempt.error = String(error)
    }
  }
  let stderr = ''
  let stdout = ''
  const diagnostics = () =>
    JSON.stringify({
      executable,
      args,
      pid: child.pid,
      expectedUserData,
      exitCode: child.exitCode,
      signalCode: child.signalCode,
      stderr,
      stdout,
    })
  child.stdout.on('data', (chunk) => {
    stdout = (stdout + String(chunk)).slice(-65536)
  })
  let socket: WebSocket | undefined
  const finished = new Promise<void>((resolve, reject) => {
    child.on('error', reject)
    child.on('close', (code, signal) =>
      code === 0 ? resolve() : reject(new Error(`native exit ${code}/${signal}: ${diagnostics()}`)),
    )
  })
  // Attach a rejection handler immediately while discovering the inspector URL.
  void finished.catch(() => undefined)
  let timer: ReturnType<typeof setTimeout>
  const deadline = new Promise<never>((_resolve, reject) => {
    timer = setTimeout(() => {
      requestKill('active-deadline')
      reject(new Error(`native recovery deadline exceeded: ${diagnostics()}`))
    }, 45000)
  })
  const exitedDuringBootstrap = finished.then(() => {
    throw new Error(`native exited before bootstrap completed: ${diagnostics()}`)
  })
  void exitedDuringBootstrap.catch(() => undefined)
  const bounded = <T>(work: Promise<T>) => Promise.race([work, exitedDuringBootstrap, deadline])
  let firstFailure: unknown
  let hasFirstFailure = false
  const cleanupFailures: unknown[] = []
  let identityVerified = false
  try {
    const endpoint = await bounded(
      new Promise<string>((resolve, reject) => {
        child.stderr.on('data', (chunk) => {
          stderr = (stderr + String(chunk)).slice(-65536)
          const match = stderr.match(/ws:\/\/127\.0\.0\.1:[^\s]+/)
          if (match) resolve(match[0])
        })
        child.on('error', reject)
        child.on('close', () =>
          reject(new Error(`native closed before inspector: ${diagnostics()}`)),
        )
      }),
    )
    socket = new WebSocket(endpoint)
    const connected = socket
    await bounded(
      new Promise<void>((resolve, reject) => {
        connected.addEventListener('open', () => resolve(), { once: true })
        connected.addEventListener(
          'close',
          () => reject(new Error('native inspector closed before open')),
          { once: true },
        )
        connected.addEventListener(
          'error',
          () => reject(new Error('native inspector connection failed')),
          { once: true },
        )
      }),
    )
    await bounded(
      new Promise<void>((resolve, reject) => {
        connected.addEventListener(
          'close',
          () => reject(new Error('native inspector closed before bootstrap reply')),
          { once: true },
        )
        connected.addEventListener('message', (event) => {
          const message = JSON.parse(String(event.data))
          if (message.id !== 1) return
          if (message.error || message.result?.exceptionDetails)
            reject(new Error(JSON.stringify(message)))
          else resolve()
        })
        connected.send(
          JSON.stringify({
            id: 1,
            method: 'Runtime.evaluate',
            params: {
              awaitPromise: true,
              expression: `(async () => {
                const r = process.getBuiltinModule('module').createRequire(process.execPath);
                const { app } = r('electron');
                await app.whenReady();
                const actual = { pid: process.pid, userData: app.getPath('userData') };
                const expected = { pid: ${JSON.stringify(child.pid)}, userData: ${JSON.stringify(expectedUserData)} };
                const matches = actual.pid === expected.pid && actual.userData === expected.userData;
                r('node:fs').writeFileSync(${JSON.stringify(identityPath)}, JSON.stringify({
                  at: new Date().toISOString(), expected, actual, matches
                }, null, 2) + '\\n', { flag: 'wx' });
                if (!matches) throw new Error('native identity mismatch; fault hook not loaded');
                r(${JSON.stringify(resolvePath('tests/e2e/native-recovery.cjs'))});
                return true;
              })()`,
            },
          }),
        )
      }),
    )
    identityVerified = true
    connected.close()
    await Promise.race([finished, deadline])
  } catch (error) {
    firstFailure = error
    hasFirstFailure = true
  } finally {
    clearTimeout(timer!)
    try {
      socket?.close()
    } catch (error) {
      cleanupFailures.push(error)
    }
    let cleanupTimer: ReturnType<typeof setTimeout> | undefined
    let closeWithinBound = Boolean(closed)
    try {
      if (!closed && child.pid) requestKill('finally')
      closeWithinBound = closed
        ? true
        : await Promise.race([
            closeObserved.then(() => true),
            new Promise<boolean>((done) => {
              cleanupTimer = setTimeout(() => done(false), 5000)
            }),
          ])
    } catch (error) {
      cleanupFailures.push(error)
    } finally {
      if (cleanupTimer) clearTimeout(cleanupTimer)
    }
    if (!closeWithinBound)
      cleanupFailures.push(new Error(`native child close unresolved: ${diagnostics()}`))
    try {
      await writeFile(
        `${evidencePath}.driver.json`,
        JSON.stringify(
          {
            pid: child.pid ?? null,
            executable,
            args: child.spawnargs,
            expectedUserData,
            identityPath,
            identityVerified,
            exit: exited ?? null,
            close: closed ?? null,
            cleanupSignals,
            cleanupWaitMs: 5000,
            closeWithinBound,
            firstFailure: hasFirstFailure ? String(firstFailure) : null,
            cleanupFailures: cleanupFailures.map(String),
            scope: 'direct owned child only; descendant settlement is not proven here',
          },
          null,
          2,
        ) + '\n',
        { flag: 'wx' },
      )
    } catch (error) {
      cleanupFailures.push(error)
    } finally {
      if (!closed) {
        // Preserve the unresolved PID; release only this runner's pipe/watch handles.
        child.stdout.destroy()
        child.stderr.destroy()
        child.unref()
      }
    }
  }
  if (cleanupFailures.length)
    throw new AggregateError(
      hasFirstFailure ? [firstFailure, ...cleanupFailures] : cleanupFailures,
      hasFirstFailure ? 'native failure and cleanup failure' : 'native cleanup failure',
    )
  if (hasFirstFailure) throw firstFailure
}
