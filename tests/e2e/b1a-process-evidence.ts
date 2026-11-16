import type { ElectronApplication } from '@playwright/test'
import { appendFile } from 'node:fs/promises'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
const execute = promisify(execFile)
const records = new WeakMap<ElectronApplication, { profile: string; pid: number }>()

/** Passive test-only evidence; never patches app relaunch, native dialogs or spawn. */
export async function recordB1aApplication(application: ElectronApplication): Promise<void> {
  if (!process.env.B1A_OWNERSHIP_MANIFEST) return
  await application.firstWindow()
  const value = await application.evaluate(({ app }) => ({
    profile: app.getPath('userData'),
    pid: process.pid,
    executable: process.execPath,
    children: (process as typeof process & { _getActiveHandles(): unknown[] })
      ._getActiveHandles()
      .filter((entry) => entry && typeof entry === 'object' && 'spawnargs' in entry)
      .map((entry) => (entry as { pid?: number }).pid)
      .filter((pid): pid is number => typeof pid === 'number'),
  }))
  records.set(application, value)
  await recordB1aProcessIdentities(value.profile, [value.pid, ...value.children], 'opened')
}
export async function recordB1aProcessIdentities(
  profile: string,
  pids: number[],
  phase: string,
): Promise<void> {
  const manifest = process.env.B1A_OWNERSHIP_MANIFEST
  if (!manifest) return
  const python = process.env.B1A_OWNER_PYTHON,
    script = process.env.B1A_OWNER_SCRIPT,
    runId = process.env.B1A_OWNER_RUN_ID
  if (!python || !script || !runId) throw new Error('Incomplete runner ownership channel')
  const evidence = await execute(python, ['-I', script, '--describe-pids', JSON.stringify(pids)], {
    timeout: 5000,
    maxBuffer: 65536,
  })
  const identities: unknown = JSON.parse(evidence.stdout)
  if (!Array.isArray(identities) || identities.length > 32)
    throw new Error('Invalid process identity evidence')
  await appendFile(manifest, JSON.stringify({ runId, profile, phase, identities }) + '\n', {
    mode: 0o600,
  })
}
export async function closeB1aApplication(application: ElectronApplication): Promise<void> {
  const record = records.get(application)
  await application.close()
  if (record) await recordB1aProcessIdentities(record.profile, [], 'closed')
}
