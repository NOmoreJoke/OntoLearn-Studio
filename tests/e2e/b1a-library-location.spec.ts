import {
  test,
  expect,
  _electron as electron,
  chromium,
  type Browser,
  type ElectronApplication,
} from '@playwright/test'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { mkdtemp, readFile, readdir, readlink, realpath } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { launchIsolatedDesktop } from './isolated-desktop'
import {
  recordB1aApplication,
  recordB1aProcessIdentities,
  closeB1aApplication,
} from './b1a-process-evidence'
const execute = promisify(execFile)

async function nativeWindow(title: string): Promise<string> {
  let found: string | undefined
  await expect
    .poll(
      async () => {
        const inventory = await execute('xdotool', [
          'search',
          '--onlyvisible',
          '--name',
          '.*',
        ]).catch(() => ({ stdout: '' }))
        const matches: string[] = []
        for (const id of inventory.stdout.trim().split('\n').filter(Boolean)) {
          const name = await execute('xdotool', ['getwindowname', id]).catch(() => ({ stdout: '' }))
          if (name.stdout.trim() === title) matches.push(id)
        }
        if (matches.length > 1) throw new Error('Ambiguous native picker window')
        found = matches[0]
        return !!found
      },
      { timeout: 10000 },
    )
    .toBe(true)
  return found!
}
async function chooseNativeDirectory(path: string, observations: unknown[]): Promise<void> {
  const id = await nativeWindow('选择空目录创建项目库')
  await execute('xdotool', ['windowactivate', '--sync', id])
  observations.push({
    id,
    title: (await execute('xdotool', ['getwindowname', id])).stdout.trim(),
    inputPath: path,
  })
  // Real GTK picker input. No replacement of dialog.showOpenDialog or its result.
  await execute('xdotool', ['key', '--clearmodifiers', 'ctrl+l'])
  await new Promise((resolve) => setTimeout(resolve, 150))
  // The trailing slash completes the location bar entry in one step. A plain
  // Return after typing does not confirm: GTK3 keeps the focused/active button
  // on _Cancel, so the second Return cancels the dialog instead.
  const dirInput = path.endsWith('/') ? path : `${path}/`
  await execute('xdotool', ['type', '--delay', '10', '--clearmodifiers', '--', dirInput])
  await new Promise((resolve) => setTimeout(resolve, 150))
  // GTK3's _Open mnemonic actually confirms the directory shown in the picker.
  await execute('xdotool', ['key', '--clearmodifiers', 'alt+o'])
}
async function logicalHash(database: string): Promise<string> {
  const python = resolve('.venv/bin/python')
  const result = await execute(
    python,
    [
      '-I',
      '-c',
      'import hashlib,sqlite3,sys; from pathlib import Path; c=sqlite3.connect(Path(sys.argv[1]).as_uri()+"?mode=ro",uri=True); c.execute("BEGIN"); print(hashlib.sha256("\\n".join(c.iterdump()).encode()).hexdigest()); c.close()',
      database,
    ],
    { timeout: 10000 },
  )
  return result.stdout.trim()
}
async function processGone(pid: number): Promise<boolean> {
  try {
    await readFile(`/proc/${pid}/cmdline`)
    return false
  } catch (cause) {
    if ((cause as NodeJS.ErrnoException).code === 'ENOENT') return true
    throw cause
  }
}

// This is deliberately a real-native opt-in lane, like I04_NATIVE_ISOLATED. A
// skipped run is not native acceptance, and Linux evidence is not Mac/Windows evidence.
test('B1a real native picker, actual relaunch and a second restart preserve separate libraries', async () => {
  test.skip(
    process.platform !== 'linux' || process.env.B1A_NATIVE_ISOLATED !== '1',
    'Requires a dedicated Linux display with openbox and xdotool; never substitutes a mocked picker.',
  )
  test.setTimeout(120000)
  if (!process.env.B1A_OWNERSHIP_MANIFEST)
    throw new Error(
      'Run native relaunch through the B1a packaged runner so detached process cleanup is owned.',
    )
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  // Pin GTK3's button mnemonics to the stable _Cancel/_Open set regardless of
  // the host locale. LC_ALL would override LC_MESSAGES in the child process,
  // so it is removed to guarantee LC_MESSAGES actually takes effect.
  delete env.LC_ALL
  env.LC_MESSAGES = 'C.UTF-8'
  const options = {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  }
  const targetDirectory = await realpath(await mkdtemp(join(tmpdir(), 'b1a-native-target-')))
  const observations: unknown[] = []
  let application: ElectronApplication | undefined = await launchIsolatedDesktop(options)
  await recordB1aApplication(application)
  let connected: Browser | undefined
  let restartedPid: number | undefined
  try {
    let page = await application.firstWindow()
    await page.getByTestId('project-name').fill('原库保留项目')
    await page.getByTestId('project-create').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
    )
    const launch = await application.evaluate(({ app }) => ({
      userData: app.getPath('userData'),
      pid: process.pid,
      children: (process as typeof process & { _getActiveHandles(): unknown[] })
        ._getActiveHandles()
        .filter((value) => value && typeof value === 'object' && 'spawnargs' in value)
        .map((value) => {
          const child = value as { pid?: number; spawnargs: string[] }
          return { pid: child.pid, spawnargs: child.spawnargs }
        }),
    }))
    const oldEngines = launch.children.filter((child) =>
      child.spawnargs.includes('--t01-internal-profile=business3'),
    )
    expect(oldEngines.length).toBeGreaterThan(0)
    const original = join(launch.userData, 'engine.sqlite')
    const originalHash = await logicalHash(original)
    const originalLocation = await page.evaluate(() => window.ontolearn!.getLibraryLocation())
    expect(originalLocation.ok).toBe(true)
    // A fresh schema2 start must not create a pointless migration backup.
    expect(
      (await readdir(launch.userData)).filter((name) => name.startsWith('.t01-backup-')),
    ).toEqual([])
    const location = page.getByRole('region', { name: '项目库位置', exact: true })
    await location.getByRole('button', { name: '选择空目录建立项目库', exact: true }).click()
    const cancelledPicker = await nativeWindow('选择空目录创建项目库')
    await execute('xdotool', ['windowactivate', '--sync', cancelledPicker])
    await execute('xdotool', ['key', '--clearmodifiers', 'Escape'])
    await expect(
      location.getByRole('button', { name: '选择空目录建立项目库', exact: true }),
    ).toBeEnabled()
    expect(await page.evaluate(() => window.ontolearn!.getLibraryLocation())).toEqual(
      originalLocation,
    )
    await location.getByRole('button', { name: '选择空目录建立项目库', exact: true }).click()
    await chooseNativeDirectory(targetDirectory, observations)
    const confirm = page.getByRole('dialog', { name: '确认切换项目库', exact: true })
    await expect(confirm).toContainText(targetDirectory)
    const oldPortFile = await readFile(join(launch.userData, 'DevToolsActivePort'), 'utf8')
    const exited = application.waitForEvent('close')
    await confirm.getByRole('button', { name: '确认并重启到此项目库', exact: true }).click()
    await exited
    application = undefined
    await expect
      .poll(
        async () => {
          const current = await readFile(join(launch.userData, 'DevToolsActivePort'), 'utf8').catch(
            () => '',
          )
          return current.length > 0 && current !== oldPortFile
        },
        { timeout: 20000 },
      )
      .toBe(true)
    const [port] = (await readFile(join(launch.userData, 'DevToolsActivePort'), 'utf8'))
      .trim()
      .split('\n')
    connected = await chromium.connectOverCDP(`http://127.0.0.1:${port}`)
    await expect.poll(() => connected!.contexts()[0]?.pages().length ?? 0).toBeGreaterThan(0)
    page = connected.contexts()[0]!.pages()[0]!
    await expect(page.getByTestId('library-location')).toContainText(targetDirectory)
    const singleton = await readlink(join(launch.userData, 'SingletonLock'))
    restartedPid = Number(singleton.slice(singleton.lastIndexOf('-') + 1))
    await recordB1aProcessIdentities(launch.userData, [restartedPid], 'relaunched')
    expect(
      Number.isSafeInteger(restartedPid) && restartedPid > 0 && restartedPid !== launch.pid,
    ).toBe(true)
    for (const old of oldEngines) {
      expect(old.pid).toBeGreaterThan(0)
      await expect.poll(() => processGone(old.pid!), { timeout: 5000 }).toBe(true)
    }
    expect(await logicalHash(original)).toBe(originalHash)
    await page.getByTestId('project-name').fill('目标库独立项目')
    await page.getByTestId('project-create').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
    )
    const target = await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology' }))
    expect(target.ok && target.data.workspace.metadata.name).toBe('目标库独立项目')
    const mainWindow = await nativeWindow('OntoLearn Studio')
    await execute('xdotool', ['windowactivate', '--sync', mainWindow])
    await execute('xdotool', ['key', '--clearmodifiers', 'alt+F4'])
    await expect.poll(() => processGone(restartedPid!), { timeout: 10000 }).toBe(true)
    await connected.close()
    connected = undefined
    restartedPid = undefined
    application = await electron.launch({
      ...options,
      args: [...options.args, `--user-data-dir=${launch.userData}`],
    })
    await recordB1aApplication(application)
    page = await application.firstWindow()
    await expect(page.getByTestId('library-location')).toContainText(targetDirectory)
    await page.getByTestId('project-list-refresh').click()
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    const catalog = await page.evaluate(() =>
      window.ontolearn!.getProjectCatalog({ pageSize: 64, cursor: null }),
    )
    expect(catalog.ok && catalog.data.items.map((item) => item.metadata.name)).toEqual([
      '目标库独立项目',
    ])
    expect(await logicalHash(original)).toBe(originalHash)
    await test.info().attach('b1a-real-native-picker-relaunch', {
      body: JSON.stringify(
        {
          launch,
          observations,
          originalHash,
          targetDirectory,
          target,
          catalog,
          boundary:
            'Actual Linux native picker and app.relaunch; original runtime/main/preload/engine. No native Mac/Windows claim.',
        },
        null,
        2,
      ),
      contentType: 'application/json',
    })
  } finally {
    if (application) await closeB1aApplication(application)
    await connected?.close().catch(() => {})
    // The runner closes any remaining detached process through its verified
    // ownership handles. This test never signals a potentially recycled PID.
  }
})
