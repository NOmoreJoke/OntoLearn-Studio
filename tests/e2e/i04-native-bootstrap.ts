// I04's native hook must run once, only after Electron's MAIN API is installed.
// Its caller owns the original 75s budget and aborts on child termination/cleanup.
export interface I04BootstrapDiagnostics {
  attempts: number
  pending: string[]
  installed: boolean
}

export function i04ReadinessExpression(hook: string): string {
  return `(() => {
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
      return { state: 'pending', member: 'browser_init' };
    const req = process.getBuiltinModule('module').createRequire(${JSON.stringify(hook)});
    if (!Object.prototype.hasOwnProperty.call(req.cache, 'electron'))
      return { state: 'pending', member: 'module mapping' };
    let resolved;
    try { resolved = req.resolve('electron'); }
    catch (error) {
      if (error?.code === 'MODULE_NOT_FOUND') return { state: 'pending', member: 'module resolver' };
      throw error;
    }
    if (resolved !== 'electron') throw new Error('unexpected Electron module mapping');
    if (process.type !== 'browser' || !process.versions.electron)
      throw new Error('bootstrap is not an Electron main process');
    const api = req('electron');
    if (!api || typeof api !== 'object') throw new Error('missing Electron API object');
    const { app, BrowserWindow } = api;
    const members = [
      ['app', () => !!app],
      ['app.commandLine', () => !!app.commandLine],
      ['app.commandLine.hasSwitch', () => typeof app.commandLine.hasSwitch === 'function'],
      ['app.whenReady', () => typeof app.whenReady === 'function'],
      ['app.isReady', () => typeof app.isReady === 'function'],
      ['app.on', () => typeof app.on === 'function'],
      ['app.exit', () => typeof app.exit === 'function'],
      ['app.quit', () => typeof app.quit === 'function'],
      ['app.focus', () => typeof app.focus === 'function'],
      ['BrowserWindow', () => !!BrowserWindow],
      ['BrowserWindow.getAllWindows', () => typeof BrowserWindow.getAllWindows === 'function'],
    ];
    for (const [member, installed] of members)
      if (!installed()) return { state: 'pending', member };
    return app.whenReady().then(() => {
      if (app.isReady() !== true) throw new Error('inconsistent Electron readiness');
      return { state: 'ready' };
    });
  })()`
}

export async function installI04NativeHook(
  socket: WebSocket,
  hook: string,
  signal: AbortSignal,
  diagnostics: I04BootstrapDiagnostics,
): Promise<void> {
  let sequence = 0
  const assertActive = () => {
    signal.throwIfAborted()
    if (socket.readyState !== WebSocket.OPEN) throw new Error('native main inspector is not open')
  }
  const waitFor = <T>(
    setup: (resolve: (value: T) => void, reject: (error: unknown) => void) => () => void,
  ) =>
    new Promise<T>((resolve, reject) => {
      assertActive()
      let cleanup = () => {}
      let settled = false
      const finish = (work: () => void) => {
        if (settled) return
        settled = true
        signal.removeEventListener('abort', abort)
        cleanup()
        work()
      }
      const abort = () => finish(() => reject(signal.reason))
      signal.addEventListener('abort', abort, { once: true })
      try {
        cleanup = setup(
          (value) => finish(() => resolve(value)),
          (error) => finish(() => reject(error)),
        )
        // A synchronous send failure or test transport reply may already settle.
        if (settled) cleanup()
      } catch (error) {
        finish(() => reject(error))
      }
    })
  const evaluate = (expression: string, readiness: boolean) =>
    waitFor<Record<string, unknown>>((resolve, reject) => {
      const id = ++sequence
      const close = () => reject(new Error('native inspector closed before bootstrap reply'))
      const error = () => reject(new Error('native inspector connection failed'))
      const message = (event: MessageEvent) => {
        try {
          const reply = JSON.parse(String(event.data))
          if (!reply || typeof reply !== 'object' || Array.isArray(reply))
            throw new Error('invalid native inspector response')
          if (reply.id === undefined && typeof reply.method === 'string') return
          if (reply.id !== id) throw new Error('unexpected native inspector response ID')
          if (reply.error || reply.result?.exceptionDetails) throw new Error(JSON.stringify(reply))
          if (!reply.result?.result || typeof reply.result.result.type !== 'string')
            throw new Error('invalid native inspector evaluation result')
          resolve(reply.result.result)
        } catch (reason) {
          reject(reason)
        }
      }
      socket.addEventListener('message', message)
      socket.addEventListener('close', close)
      socket.addEventListener('error', error)
      const cleanup = () => {
        socket.removeEventListener('message', message)
        socket.removeEventListener('close', close)
        socket.removeEventListener('error', error)
      }
      try {
        assertActive()
        socket.send(
          JSON.stringify({
            id,
            method: 'Runtime.evaluate',
            params: {
              expression,
              ...(readiness ? { awaitPromise: true, returnByValue: true } : {}),
            },
          }),
        )
      } catch (reason) {
        cleanup()
        reject(reason)
      }
      return cleanup
    })
  for (let attempt = 1; attempt <= 750; attempt++) {
    diagnostics.attempts = attempt
    const result = await evaluate(i04ReadinessExpression(hook), true)
    const value = result.value as Record<string, unknown> | undefined
    if (result.type !== 'object' || !value || typeof value !== 'object' || Array.isArray(value))
      throw new Error('invalid native readiness state')
    if (value.state === 'ready' && Object.keys(value).length === 1) {
      // Exactly one injection. Never retry the hook after exceptions or lost replies.
      await evaluate(
        `process.getBuiltinModule('module').createRequire(process.execPath)(${JSON.stringify(hook)})`,
        false,
      )
      diagnostics.installed = true
      return
    }
    if (
      value.state !== 'pending' ||
      Object.keys(value).length !== 2 ||
      typeof value.member !== 'string' ||
      !value.member ||
      value.member.length > 64
    )
      throw new Error('invalid native readiness state')
    if (diagnostics.pending.length < 32 && !diagnostics.pending.includes(value.member))
      diagnostics.pending.push(value.member)
    if (attempt === 750) break
    await waitFor<void>((resolve) => {
      const timer = setTimeout(resolve, 100)
      return () => clearTimeout(timer)
    })
  }
  throw new Error(`native readiness attempt limit exceeded: ${JSON.stringify(diagnostics)}`)
}
