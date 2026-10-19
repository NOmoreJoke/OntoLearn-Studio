import { spawn } from 'node:child_process'
import { resolve, join } from 'node:path'
import { healthSchema, type EngineHealth } from '@ontolearn/contracts'

export interface EngineLocation {
  packaged: boolean
  appPath: string
  resourcesPath: string
}

export function getEngineCommand(location: EngineLocation): { command: string; args: string[] } {
  const executable = process.platform === 'win32' ? 'ontolearn-engine.exe' : 'ontolearn-engine'
  if (location.packaged) {
    return { command: join(location.resourcesPath, 'engine', executable), args: [] }
  }
  const root = resolve(location.appPath, '../..')
  const python =
    process.platform === 'win32'
      ? join(root, '.venv', 'Scripts', 'python.exe')
      : join(root, '.venv', 'bin', 'python')
  return { command: python, args: ['-I', '-m', 'ontolearn_engine'] }
}

// 当前健康探针采用单请求子进程；持久任务队列/取消在 M1 另行设计。
export function readEngineHealth(location: EngineLocation): Promise<EngineHealth> {
  return new Promise((resolveHealth, reject) => {
    const { command, args } = getEngineCommand(location)
    const child = spawn(command, args, {
      shell: false,
      windowsHide: true,
      stdio: ['pipe', 'pipe', 'ignore'],
    })
    let output = ''
    let settled = false
    const finish = (error?: Error, value?: EngineHealth): void => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      child.kill()
      if (error) reject(error)
      else resolveHealth(value!)
    }
    const timer = setTimeout(() => finish(new Error('ENGINE_TIMEOUT')), 5000)
    child.once('error', () => finish(new Error('ENGINE_UNAVAILABLE')))
    child.stdin.on('error', () => finish(new Error('ENGINE_UNAVAILABLE')))
    child.stdout.setEncoding('utf8')
    child.stdout.on('data', (chunk: string) => {
      output += chunk
      if (Buffer.byteLength(output) > 65536) finish(new Error('ENGINE_RESPONSE_LIMIT'))
    })
    child.once('close', (code) => {
      if (settled) return
      try {
        const response = JSON.parse(output.trim())
        if (code !== 0 || response.id !== 'health' || response.ok !== true) throw new Error()
        finish(undefined, healthSchema.parse(response.result))
      } catch {
        finish(new Error('ENGINE_PROTOCOL_ERROR'))
      }
    })
    child.stdin.end(JSON.stringify({ id: 'health', method: 'health', protocolVersion: 1 }) + '\n')
  })
}
