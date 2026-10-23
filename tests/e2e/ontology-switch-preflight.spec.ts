import { test, expect, type ElectronApplication } from '@playwright/test'
import { resolve } from 'node:path'
import type { BridgeResult } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'

const instrumentationKey = '__t01_owned_ontology_preflight_delay_v1'
const watched = ['project:changeset-confirm', 'project:draft-save', 'project:changeset-commit']

function data<T>(response: BridgeResult<T>): T {
  if (!response.ok) throw new Error(`Actual bridge refused: ${JSON.stringify(response.error)}`)
  return response.data
}

async function read(page: import('@playwright/test').Page) {
  return data(
    await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology-transaction' })),
  )
}

async function installDelay(application: ElectronApplication) {
  await application.evaluate(
    ({ ipcMain }, { key, channels }) => {
      type Handler = (...args: unknown[]) => unknown
      const handlers = Reflect.get(ipcMain, '_invokeHandlers') as Map<string, Handler>
      if (!(handlers instanceof Map) || Reflect.has(globalThis, key))
        throw new Error('Owned IPC instrumentation is unavailable or already installed')
      const active = handlers.get('project:active')
      if (typeof active !== 'function') throw new Error('Original active handler is missing')
      const state = {
        held: false,
        released: false,
        actual: undefined as unknown,
        calls: [] as string[],
        release: undefined as (() => void) | undefined,
        originals: new Map<string, Handler>(),
        wrappers: new Map<string, Handler>(),
      }
      // The production handler still receives the original event and arguments.
      // Only its actual first reply is delayed, after trust checks and real work.
      const delayed: Handler = async (...args) => {
        const actual: unknown = await active(...args)
        if (!state.held) {
          state.held = true
          state.actual = actual
          await new Promise<void>((release) => {
            state.release = () => {
              state.released = true
              release()
            }
          })
        }
        return actual
      }
      state.originals.set('project:active', active)
      state.wrappers.set('project:active', delayed)
      for (const channel of channels) {
        const original = handlers.get(channel)
        if (typeof original !== 'function') throw new Error('Original write handler is missing')
        const wrapper: Handler = (...args) => {
          state.calls.push(channel)
          return original(...args)
        }
        state.originals.set(channel, original)
        state.wrappers.set(channel, wrapper)
      }
      Reflect.set(globalThis, key, state)
      for (const [channel, wrapper] of state.wrappers) handlers.set(channel, wrapper)
    },
    { key: instrumentationKey, channels: watched },
  )
}

async function inspectDelay(application: ElectronApplication) {
  return application.evaluate((_, key) => {
    const state = Reflect.get(globalThis, key) as {
      held: boolean
      released: boolean
      actual: unknown
      calls: string[]
    }
    return { held: state.held, released: state.released, actual: state.actual, calls: state.calls }
  }, instrumentationKey)
}

async function removeDelay(application: ElectronApplication) {
  await application.evaluate(({ ipcMain }, key) => {
    type Handler = (...args: unknown[]) => unknown
    const state = Reflect.get(globalThis, key) as
      | {
          originals: Map<string, Handler>
          wrappers: Map<string, Handler>
        }
      | undefined
    if (!state) return
    // Failed-test cleanup must not release a still-live A confirmation.
    // The success path releases explicitly; closing this owned app ends a held reply.
    const handlers = Reflect.get(ipcMain, '_invokeHandlers') as Map<string, Handler>
    for (const [channel, original] of state.originals) {
      if (handlers.get(channel) !== state.wrappers.get(channel))
        throw new Error('Owned handler changed while instrumented')
      handlers.set(channel, original)
    }
    Reflect.deleteProperty(globalThis, key)
  }, instrumentationKey)
}

test('ontology real preflight reply cannot start A writes after the UI selects same-revision B', async () => {
  test.setTimeout(60000)
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  const application = await launchIsolatedDesktop({
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  })
  let instrumented = false
  const evidence: Record<string, unknown> = {
    boundary:
      'Real original IPC reply delay and pass-through call observation; no forged response or authority. This schedule alone does not prove the narrower pre-React-cleanup microtask gap.',
  }
  try {
    const page = await application.firstWindow()
    const library = page.getByTestId('project-library')
    async function create(name: string) {
      await page.getByTestId('project-name').fill(name)
      await page.getByTestId('project-create').click()
      await expect(library.getByRole('status')).toContainText('项目已创建并打开')
      await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
      const source = await read(page)
      expect(source.domain.projectRevision).toBe(0)
      expect(source.domain.state).toEqual({ definitions: [], facts: [], mappingState: {} })
      expect(source.workspace.draft.state).toBe('missing')
      return source
    }
    const b = await create('T02 延迟预检 B')
    const a = await create('T02 延迟预检 A')
    expect(a.projectId).not.toBe(b.projectId)
    expect(a.domain.projectRevision).toBe(b.domain.projectRevision)
    await page.getByRole('link', { name: '本体构建', exact: true }).click()
    const ontology = page.getByRole('region', { name: '本体项目编辑', exact: true })
    await expect(ontology.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled()
    await expect(ontology).toContainText('项目版本 0')
    await expect(ontology.getByRole('alert')).toHaveCount(0)
    await ontology.getByRole('button', { name: '新建概念', exact: true }).click()
    const form = ontology.getByRole('region', { name: '本体编辑表单', exact: true })
    await form.getByLabel('稳定 IRI', { exact: true }).fill('urn:t01:delayed-preflight:A')
    await form.getByLabel('英文标识', { exact: true }).fill('DelayedA')
    await form.getByRole('button', { name: '预览定义修改', exact: true }).click()
    const diff = ontology.getByRole('region', { name: '完整事务差异', exact: true })
    await expect(diff).toBeVisible()
    const confirm = diff.getByRole('button', { name: '我已核对完整差异，确认提交', exact: true })
    await expect(confirm).toBeEnabled()
    const beforeA = await read(page)
    expect(beforeA.domain).toEqual(a.domain)
    expect(beforeA.workspace.draft).toEqual(a.workspace.draft)

    await installDelay(application)
    instrumented = true
    await confirm.click()
    await expect.poll(async () => (await inspectDelay(application)).held).toBe(true)
    const held = await inspectDelay(application)
    expect(held.released).toBe(false)
    expect(held.calls).toEqual([])
    expect(held.actual).toMatchObject({ ok: true, data: { projectId: a.projectId } })
    evidence.held = held

    await page.locator(`[data-testid="project-open"][data-project-id="${b.projectId}"]`).click()
    await expect(library.getByRole('status')).toContainText('项目已打开')
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await page.getByRole('link', { name: '本体构建', exact: true }).click()
    await expect(ontology).toContainText('项目版本 0')
    await expect(ontology.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled()
    await expect(ontology.getByRole('alert')).toHaveCount(0)
    const selectedB = await read(page)
    expect(selectedB.projectId).toBe(b.projectId)
    expect(selectedB.domain).toEqual(b.domain)
    expect(selectedB.workspace.draft).toEqual(b.workspace.draft)
    await expect(page.getByRole('region', { name: '完整事务差异', exact: true })).toHaveCount(0)
    await application.evaluate((_, key) => {
      const state = Reflect.get(globalThis, key) as { release?: () => void }
      if (!state.release) throw new Error('Actual original reply has not been held')
      state.release()
    }, instrumentationKey)
    // An actual named round trip lets the renderer consume the released reply.
    expect(data(await page.evaluate(() => window.ontolearn!.getActiveProject()))?.projectId).toBe(
      b.projectId,
    )
    await application.evaluate(() => new Promise<void>((done) => setImmediate(done)))
    const afterB = await read(page)
    expect(afterB.domain).toEqual(b.domain)
    expect(afterB.workspace.draft).toEqual(b.workspace.draft)
    const observed = await inspectDelay(application)
    expect(observed.released).toBe(true)
    expect(observed.calls).toEqual([])
    evidence.afterRelease = observed
    evidence.beforeA = beforeA
    evidence.beforeB = b
    evidence.afterB = afterB
    await removeDelay(application)
    instrumented = false

    await page.locator(`[data-testid="project-open"][data-project-id="${a.projectId}"]`).click()
    await expect(library.getByRole('status')).toContainText('项目已打开')
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await page.getByRole('link', { name: '本体构建', exact: true }).click()
    await expect(ontology).toContainText('项目版本 0')
    await expect(ontology.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled()
    await expect(ontology.getByRole('alert')).toHaveCount(0)
    const afterA = await read(page)
    expect(afterA.domain).toEqual(a.domain)
    expect(afterA.workspace.draft).toEqual(a.workspace.draft)
    const tasks = data(await page.evaluate(() => window.ontolearn!.restoreTasks()))
    expect(tasks.project?.projectId).toBe(a.projectId)
    expect(tasks.jobs).toEqual([])
    evidence.afterA = afterA
    evidence.tasks = tasks
    await page.screenshot({ path: test.info().outputPath('ontology-preflight-after-switch.png') })
  } finally {
    try {
      if (instrumented) await removeDelay(application)
    } finally {
      try {
        await test.info().attach('ontology-original-preflight-evidence', {
          body: JSON.stringify(evidence, null, 2),
          contentType: 'application/json',
        })
      } finally {
        await application.close()
      }
    }
  }
})
