import { spawn } from 'node:child_process'
import { resolve as resolvePath } from 'node:path'

// Packaged Electron ignores arbitrary --require. Bootstrap a test hook through
// the MAIN inspector, then close it before any faults. No renderer CDP/loader.
export async function runNativeRecovery(
  executable: string,
  args: string[],
  env: NodeJS.ProcessEnv,
): Promise<void> {
  const child = spawn(executable, ['--inspect=0', ...args], {
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  let stderr = ''
  let socket: WebSocket | undefined
  const finished = new Promise<void>((resolve, reject) => {
    child.on('error', reject)
    child.on('exit', (code, signal) =>
      code === 0 ? resolve() : reject(new Error(`native exit ${code}/${signal}: ${stderr}`)),
    )
  })
  // Attach a rejection handler immediately while discovering the inspector URL.
  void finished.catch(() => undefined)
  let timer: ReturnType<typeof setTimeout>
  const deadline = new Promise<never>((_resolve, reject) => {
    timer = setTimeout(() => {
      child.kill('SIGKILL')
      reject(new Error('native recovery deadline exceeded'))
    }, 45000)
  })
  const exitedDuringBootstrap = finished.then(() => {
    throw new Error('native exited before bootstrap completed')
  })
  void exitedDuringBootstrap.catch(() => undefined)
  const bounded = <T>(work: Promise<T>) => Promise.race([work, exitedDuringBootstrap, deadline])
  try {
    const endpoint = await bounded(
      new Promise<string>((resolve, reject) => {
        child.stderr.on('data', (chunk) => {
          stderr += String(chunk)
          const match = stderr.match(/ws:\/\/127\.0\.0\.1:[^\s]+/)
          if (match) resolve(match[0])
        })
        child.on('error', reject)
        child.on('exit', () => reject(new Error(`native closed before inspector: ${stderr}`)))
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
              expression: `process.getBuiltinModule('module').createRequire(process.execPath)(${JSON.stringify(resolvePath('tests/e2e/native-recovery.cjs'))})`,
            },
          }),
        )
      }),
    )
    connected.close()
    await Promise.race([finished, deadline])
  } finally {
    clearTimeout(timer!)
    socket?.close()
    if (child.exitCode === null) child.kill('SIGKILL')
  }
}
