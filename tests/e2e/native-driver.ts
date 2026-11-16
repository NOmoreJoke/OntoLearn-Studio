import { spawn } from 'node:child_process'
import { resolve as resolvePath } from 'node:path'

// Synchronize the bootstrap precondition; CI41's specific timing cause is unproven.
// The original helper still closes MAIN inspector before faults, with no renderer CDP.
export async function runNativeRecovery(
  executable: string,
  args: string[],
  env: NodeJS.ProcessEnv,
): Promise<void> {
  const expiresAt = performance.now() + 45000
  const child = spawn(executable, ['--inspect=0', ...args], {
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  let stderr = ''
  let stdout = ''
  let socket: WebSocket | undefined
  let cleanupSocket = () => {}
  let terminal: Error | undefined
  let childExited = false
  let bootstrapComplete = false
  let readinessAttempts = 0
  // Bounded diagnostics for pending API members: at most the guarded member
  // count, each a short literal name; nothing else about the API is dumped.
  const pendingMembers: string[] = []
  let resolverPending = false
  let sequence = 0
  const cancellations = new Set<(reason: Error) => void>()
  const diagnostics = () =>
    JSON.stringify({
      executable,
      args,
      exitCode: child.exitCode,
      signalCode: child.signalCode,
      readinessAttempts,
      pendingMembers,
      resolverPending,
      bootstrapComplete,
      stderr,
      stdout,
    })
  const stop = (reason: Error) => {
    terminal ??= reason
    for (const cancel of [...cancellations]) cancel(terminal)
  }
  // A race alone does not cancel an outstanding listener or polling timer.
  const waitFor = <T>(
    setup: (
      resolve: (value: T) => void,
      reject: (error: unknown) => void,
      cleanup: (work: () => void) => void,
    ) => void,
  ): Promise<T> =>
    new Promise((resolve, reject) => {
      if (terminal) return reject(terminal)
      let settled = false
      const cleanups: (() => void)[] = []
      const settle = (work: () => void) => {
        if (settled) return
        settled = true
        cancellations.delete(cancel)
        for (const cleanup of cleanups) cleanup()
        work()
      }
      const cancel = (error: unknown) => settle(() => reject(error))
      cancellations.add(cancel)
      try {
        setup(
          (value) => settle(() => resolve(value)),
          cancel,
          (work) => cleanups.push(work),
        )
      } catch (error) {
        cancel(error)
      }
    })
  const assertActive = (connected?: WebSocket) => {
    if (performance.now() >= expiresAt)
      stop(new Error(`native recovery deadline exceeded: ${diagnostics()}`))
    if (childExited || child.exitCode !== null || child.signalCode != null)
      stop(new Error(`native exited before bootstrap completed: ${diagnostics()}`))
    if (connected && connected.readyState !== WebSocket.OPEN)
      stop(new Error('native inspector is not open'))
    if (terminal) throw terminal
  }
  const collectStdout = (chunk: unknown) => {
    stdout = (stdout + String(chunk)).slice(-65536)
  }
  const collectStderr = (chunk: unknown) => {
    stderr = (stderr + String(chunk)).slice(-65536)
  }
  child.stdout.on('data', collectStdout)
  child.stderr.on('data', collectStderr)
  const onExit = () => {
    childExited = true
    if (!bootstrapComplete) stop(new Error('native exited before bootstrap completed'))
  }
  child.on('exit', onExit)
  const finished = new Promise<void>((resolve, reject) => {
    child.once('error', (error) => {
      stop(error)
      reject(error)
    })
    child.once('close', (code, signal) => {
      if (!bootstrapComplete)
        stop(new Error(`native exited before bootstrap completed: ${diagnostics()}`))
      if (code === 0) resolve()
      else reject(new Error(`native exit ${code}/${signal}: ${diagnostics()}`))
    })
  })
  void finished.catch(() => undefined)
  let onStdioClose!: () => void
  const stdioClosed = new Promise<void>((resolve) => {
    onStdioClose = resolve
    child.once('close', onStdioClose)
  })
  let timer: ReturnType<typeof setTimeout>
  const deadline = new Promise<never>((_resolve, reject) => {
    timer = setTimeout(
      () => {
        const error = new Error(`native recovery deadline exceeded: ${diagnostics()}`)
        stop(error)
        child.kill('SIGKILL')
        reject(error)
      },
      Math.max(0, expiresAt - performance.now()),
    )
  })
  const exitedDuringBootstrap = finished.then(() => {
    throw new Error(`native exited before bootstrap completed: ${diagnostics()}`)
  })
  void exitedDuringBootstrap.catch(() => undefined)
  const bounded = <T>(work: Promise<T>) => Promise.race([work, exitedDuringBootstrap, deadline])
  try {
    const endpoint = await bounded(
      waitFor<string>((resolve, _reject, cleanup) => {
        const onData = () => {
          const match = stderr.match(/ws:\/\/127\.0\.0\.1:[^\s]+/)
          if (match) resolve(match[0])
        }
        child.stderr.on('data', onData)
        cleanup(() => child.stderr.off('data', onData))
        onData()
      }),
    )
    assertActive()
    socket = new WebSocket(endpoint)
    const connected = socket
    const onSocketClose = () => {
      if (!bootstrapComplete) stop(new Error('native inspector closed before bootstrap complete'))
    }
    const onSocketError = () => stop(new Error('native inspector connection failed'))
    connected.addEventListener('close', onSocketClose)
    connected.addEventListener('error', onSocketError)
    cleanupSocket = () => {
      connected.removeEventListener('close', onSocketClose)
      connected.removeEventListener('error', onSocketError)
    }
    await bounded(
      waitFor<void>((resolve, reject, cleanup) => {
        const open = () => resolve()
        const close = () => reject(new Error('native inspector closed before open'))
        const error = () => reject(new Error('native inspector connection failed'))
        connected.addEventListener('open', open)
        connected.addEventListener('close', close)
        connected.addEventListener('error', error)
        cleanup(() => {
          connected.removeEventListener('open', open)
          connected.removeEventListener('close', close)
          connected.removeEventListener('error', error)
        })
        if (connected.readyState === WebSocket.OPEN) resolve()
      }),
    )
    const evaluate = (expression: string, readiness = false) => {
      assertActive(connected)
      const id = ++sequence
      return bounded(
        waitFor<Record<string, unknown>>((resolve, reject, cleanup) => {
          const close = () => reject(new Error('native inspector closed before bootstrap reply'))
          const error = () => reject(new Error('native inspector connection failed'))
          const message = (event: MessageEvent) => {
            try {
              const reply = JSON.parse(String(event.data))
              if (!reply || typeof reply !== 'object' || Array.isArray(reply))
                throw new Error('invalid native inspector response')
              if (reply.id === undefined && typeof reply.method === 'string') return
              if (reply.id !== id) throw new Error('unexpected native inspector response ID')
              if (reply.error || reply.result?.exceptionDetails)
                throw new Error(JSON.stringify(reply))
              if (!reply.result?.result || typeof reply.result.result.type !== 'string')
                throw new Error('invalid native inspector evaluation result')
              resolve(reply.result.result)
            } catch (error) {
              reject(error)
            }
          }
          connected.addEventListener('message', message)
          connected.addEventListener('close', close)
          connected.addEventListener('error', error)
          cleanup(() => {
            connected.removeEventListener('message', message)
            connected.removeEventListener('close', close)
            connected.removeEventListener('error', error)
          })
          // Check again at the actual send boundary, not just before Promise creation.
          assertActive(connected)
          connected.send(
            JSON.stringify({
              id,
              method: 'Runtime.evaluate',
              params: {
                expression,
                ...(readiness ? { awaitPromise: true, returnByValue: true } : {}),
              },
            }),
          )
        }),
      )
    }
    const helper = JSON.stringify(resolvePath('tests/e2e/native-recovery.cjs'))
    // Electron44.9 common/init installs this cache key and canonical resolver.
    // Never require an unmapped npm shim, clear cache, or replace the resolver.
    // In Electron 44.9's browser_init, makeElectronModule('electron') writes
    // Module._cache['electron'] several statements before Module._resolveFilename
    // is replaced with the canonical one, so an evaluate landing in that window
    // sees fromHelper.resolve('electron') throw MODULE_NOT_FOUND or resolve the
    // on-disk npm shim even though the cache key exists. Both shapes are
    // re-polled as resolver-pending inside the original 45s/450-attempt bounds,
    // and fromHelper('electron') is never called before resolve returns the
    // canonical 'electron' specifier, so no unmapped npm shim is ever loaded.
    // CI46 (Windows) proved only that the combined main-API guard failed on
    // the first reply (missing member UNKNOWN; its stack overlapped
    // browser_init/Object.app). That members may merely be late to install is
    // the working hypothesis behind the strategy below, not a proven cause:
    // an unsatisfied member is reported by name and re-polled inside the
    // original 45s/450-attempt bounds instead of failing immediately.
    // Permanent absence still fails at those bounds with the member named.
    // Wait for the first usable BrowserWindow (visible, main frame finished
    // loading, and where getOSProcessId is a function an OS PID above zero, so
    // the Windows ChildProcessLauncher has finished PostLaunchOnClientThread
    // and renderer termination will not be silently dropped while IsStarting()
    // is still true) plus a 400ms win32 settle window.
    const readiness = `(() => {
      const previousStackLimit = Error.stackTraceLimit;
      let stack = '';
      try {
        Error.stackTraceLimit = Math.max(
          typeof previousStackLimit === 'number' ? previousStackLimit : 10,
          64,
        );
        stack = String(new Error().stack ?? '');
      } finally {
        Error.stackTraceLimit = previousStackLimit;
      }
      if (stack.includes('electron/js2c/'))
        return { state: 'api-pending', pending: 'browser_init' };
      const fromHelper = process.getBuiltinModule('module').createRequire(${helper});
      if (!Object.prototype.hasOwnProperty.call(fromHelper.cache, 'electron'))
        return { state: 'mapping-pending' };
      let resolved;
      try {
        resolved = fromHelper.resolve('electron');
      } catch (error) {
        if (error && typeof error === 'object' && error.code === 'MODULE_NOT_FOUND')
          return { state: 'resolver-pending' };
        throw error;
      }
      if (resolved !== 'electron')
        return { state: 'resolver-pending' };
      if (process.type !== 'browser' || !process.versions.electron)
        throw new Error('bootstrap is not an Electron main process');
      const api = fromHelper('electron');
      if (!api || typeof api !== 'object') throw new Error('missing Electron API object');
      const { app, dialog, BrowserWindow } = api;
      const members = [
        ['app', () => !!app],
        ['app.isPackaged', () => typeof app.isPackaged === 'boolean'],
        ['app.whenReady', () => typeof app.whenReady === 'function'],
        ['app.isReady', () => typeof app.isReady === 'function'],
        ['app.on', () => typeof app.on === 'function'],
        ['app.exit', () => typeof app.exit === 'function'],
        ['app.focus', () => typeof app.focus === 'function'],
        ['app.commandLine', () => !!app.commandLine],
        ['app.commandLine.hasSwitch', () => typeof app.commandLine.hasSwitch === 'function'],
        ['dialog', () => !!dialog],
        ['dialog.showMessageBox', () => typeof dialog.showMessageBox === 'function'],
        ['BrowserWindow', () => !!BrowserWindow],
        ['BrowserWindow.getAllWindows', () => typeof BrowserWindow.getAllWindows === 'function'],
      ];
      for (const [member, installed] of members)
        if (!installed()) return { state: 'api-pending', pending: member };
      return app.whenReady().then(() => {
        if (app.isReady() !== true) throw new Error('inconsistent Electron readiness');
        const windows = BrowserWindow.getAllWindows();
        const primary =
          windows && typeof windows.length === 'number' && windows.length > 0
            ? windows[0]
            : undefined;
        const windowReady =
          !!primary &&
          (typeof primary.isDestroyed !== 'function' || !primary.isDestroyed()) &&
          (typeof primary.isVisible !== 'function' || primary.isVisible() === true) &&
          (!primary.webContents ||
            ((typeof primary.webContents.isDestroyed !== 'function' ||
              !primary.webContents.isDestroyed()) &&
              (typeof primary.webContents.isLoadingMainFrame !== 'function' ||
                primary.webContents.isLoadingMainFrame() === false) &&
              (typeof primary.webContents.getOSProcessId !== 'function' ||
                primary.webContents.getOSProcessId() > 0)));
        if (!windowReady) {
          delete globalThis.__i02FirstWindowReadyAt;
          return { state: 'api-pending', pending: 'BrowserWindow.firstWindow' };
        }
        if (process.platform === 'win32') {
          const now = Date.now();
          if (typeof globalThis.__i02FirstWindowReadyAt !== 'number') {
            globalThis.__i02FirstWindowReadyAt = now;
          }
          if (now - globalThis.__i02FirstWindowReadyAt < 400) {
            return { state: 'api-pending', pending: 'BrowserWindow.firstWindowSettle' };
          }
        }
        delete globalThis.__i02FirstWindowReadyAt;
        return { state: 'ready' };
      });
    })()`
    let ready = false
    for (readinessAttempts = 1; readinessAttempts <= 450; readinessAttempts++) {
      const result = await evaluate(readiness, true)
      const value = result.value as Record<string, unknown> | null | undefined
      if (
        result.type !== 'object' ||
        !value ||
        typeof value !== 'object' ||
        Array.isArray(value) ||
        typeof value.state !== 'string'
      )
        throw new Error('invalid native readiness state')
      if (value.state === 'ready') {
        if (Object.keys(value).length !== 1) throw new Error('invalid native readiness state')
        resolverPending = false
        ready = true
        break
      }
      if (value.state === 'mapping-pending') {
        if (Object.keys(value).length !== 1) throw new Error('invalid native readiness state')
      } else if (value.state === 'resolver-pending') {
        if (Object.keys(value).length !== 1) throw new Error('invalid native readiness state')
        resolverPending = true
      } else if (value.state === 'api-pending') {
        if (
          Object.keys(value).length !== 2 ||
          typeof value.pending !== 'string' ||
          !value.pending ||
          value.pending.length > 64
        )
          throw new Error('invalid native readiness state')
        if (pendingMembers.length < 32 && !pendingMembers.includes(value.pending))
          pendingMembers.push(value.pending)
        resolverPending = false
      } else throw new Error('unknown native readiness state')
      if (readinessAttempts === 450) break
      assertActive(connected)
      await bounded(
        waitFor<void>((resolve, _reject, cleanup) => {
          const pollTimer = setTimeout(resolve, 100)
          cleanup(() => clearTimeout(pollTimer))
        }),
      )
    }
    if (!ready)
      throw new Error(
        pendingMembers.length
          ? `Electron main API readiness bounds exceeded; unsatisfied members (first-seen order): ${pendingMembers.join(', ')}; ${diagnostics()}`
          : resolverPending
            ? `unexpected Electron module mapping: ${diagnostics()}`
            : 'Electron mapping readiness attempt limit exceeded',
      )
    // Original target/expression, sent once; failures never retry the helper.
    await evaluate(`process.getBuiltinModule('module').createRequire(process.execPath)(${helper})`)
    bootstrapComplete = true
    connected.close()
    await Promise.race([finished, deadline])
  } catch (error) {
    if (childExited) {
      // Stop sends immediately, but exit can precede the final pipe data/close.
      // Drain only inside the same original deadline; never restart its budget.
      const drain = await Promise.race([
        stdioClosed.then(() => ({ closed: true })),
        deadline.then(undefined, (reason: unknown) => ({ deadlineError: String(reason) })),
      ])
      throw new Error(
        `${String(error)}: ${diagnostics()}${'deadlineError' in drain ? `; stdio drain: ${drain.deadlineError}` : ''}`,
        { cause: error },
      )
    }
    throw error
  } finally {
    stop(new Error('native recovery cleanup'))
    clearTimeout(timer!)
    cleanupSocket()
    socket?.close()
    child.off('exit', onExit)
    child.off('close', onStdioClose)
    child.stdout.off('data', collectStdout)
    child.stderr.off('data', collectStderr)
    if (child.exitCode === null) child.kill('SIGKILL')
  }
}
