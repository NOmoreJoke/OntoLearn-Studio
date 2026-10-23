import { _electron as electron, test, expect } from '@playwright/test'
import { mkdtemp } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

/** The real executable/main/preload stay intact; only its profile directory is isolated. */
export async function launchIsolatedDesktop(
  options: NonNullable<Parameters<typeof electron.launch>[0]>,
) {
  const args = options.args ?? []
  if (args.some((arg) => arg === '--user-data-dir' || arg.startsWith('--user-data-dir=')))
    throw new Error('An existing profile argument must have one owner')
  const userData = await mkdtemp(join(tmpdir(), 'ontolearn-e2e-profile-'))
  const application = await electron.launch({
    ...options,
    acceptDownloads: options.acceptDownloads ?? true,
    args: [...args, `--user-data-dir=${userData}`],
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
    return application
  } catch (error) {
    await application.close()
    throw error
  }
}
