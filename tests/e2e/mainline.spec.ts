import { test, expect, _electron as electron, type ElectronApplication } from '@playwright/test'
import { resolve } from 'node:path'
import { randomUUID } from 'node:crypto'
import type { BridgeResult } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'

function data<T>(value: BridgeResult<T>): T {
  if (!value.ok) throw new Error(`Real named bridge refused: ${JSON.stringify(value.error)}`)
  return value.data
}

test('real UI creates blank and fixed example projects; its named bridge draft survives restart', async () => {
  test.setTimeout(60000)
  const env = { ...process.env }
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  const options = {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  }
  let application: ElectronApplication | undefined = await launchIsolatedDesktop(options)
  try {
    let page = await application.firstWindow()
    const library = page.getByTestId('project-library')
    await page.getByTestId('project-name').fill('Electron 空白项目')
    await page.getByTestId('project-create').click()
    await expect(library.getByRole('status')).toContainText('项目已创建并打开')
    await expect(page.getByTestId('selected-project-version')).toContainText('版本 0')
    const blank = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology' })),
    )
    expect(blank.domain.state).toEqual({ definitions: [], facts: [], mappingState: {} })

    await page.getByTestId('project-name').fill('Electron 运维示例')
    await page.getByTestId('project-create-example').click()
    await expect(page.getByTestId('selected-project-version')).toContainText('版本 1')
    await expect(library.getByRole('status')).toContainText('项目已创建并打开')
    const initial = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology' })),
    )
    expect(initial.workspace.metadata.name).toBe('Electron 运维示例')
    expect(initial.domain.state.definitions.filter((d) => d.layer === 'ontology')).toHaveLength(10)
    expect(initial.domain.state.facts).toContainEqual(
      expect.objectContaining({
        subject: 'urn:ontolearn:learning:equipment/001',
        predicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
        object: '<urn:ontolearn:learning:Equipment>',
        owner: null,
        source_row: null,
        managed_value: null,
      }),
    )
    const query = initial.domain.state.definitions.find((d) => d.layer === 'query')
    expect(query?.id).toBe('unclosed-high')
    expect(JSON.parse(query!.payload).text).toBe(
      'PREFIX l: <urn:ontolearn:learning:>\nSELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . ?alarm l:level "High" ; l:status "Open" . } ORDER BY ?alarm',
    )
    // Exercise actual main/preload private ACK consumption beyond its finite16 window.
    for (let index = 0; index < 24; index++) {
      const current = data(
        await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology' })),
      )
      expect(current.domain).toEqual(initial.domain)
    }
    const contentJson = '{"note":"真实 Electron 草稿","version":1}'
    const draft = data(
      await page.evaluate((args) => window.ontolearn!.saveProjectDraft(args), {
        operationId: randomUUID(),
        editor: 'ontology',
        expectedGeneration: 0,
        boundDomainRevision: 1,
        contentJson,
      }),
    )
    expect(draft.generation).toBe(1)
    const launch = await application.evaluate(({ app }) => ({
      userData: app.getPath('userData'),
      resourcesPath: process.resourcesPath,
      appPath: app.getAppPath(),
      packaged: app.isPackaged,
      pid: process.pid,
      children: (process as typeof process & { _getActiveHandles(): unknown[] })
        ._getActiveHandles()
        .filter((value) => value && typeof value === 'object' && 'spawnargs' in value)
        .map((value) => {
          const child = value as { pid?: number; spawnfile: string; spawnargs: string[] }
          return { pid: child.pid, spawnfile: child.spawnfile, spawnargs: child.spawnargs }
        }),
    }))
    const engine = launch.children.find((child) =>
      child.spawnargs.includes('--t01-internal-profile=business3'),
    )
    expect(engine).toBeDefined()
    expect(
      engine!.spawnargs.filter((arg) => arg.startsWith('--t11-internal-example-root=')),
    ).toHaveLength(1)
    expect(engine!.pid).toBeGreaterThan(0)
    if (!launch.packaged)
      expect(engine!.spawnargs).toContain(resolve('packages/engine/entrypoint.py'))
    await page.screenshot({ path: test.info().outputPath('mainline-created.png') })
    await application.close()
    application = undefined
    // Reuse only this test's already-owned profile. The executable and main entry stay original.
    application = await electron.launch({
      ...options,
      args: [...options.args, `--user-data-dir=${launch.userData}`],
    })
    expect(await application.evaluate(({ app }) => app.getPath('userData'))).toBe(launch.userData)
    page = await application.firstWindow()
    await page.getByTestId('project-list-refresh').click()
    // A click ends before its async UI request. Observe completion before the
    // independent catalog read; the receiver admits only one computation at a time.
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await expect(page.getByTestId('project-open')).toHaveCount(2)
    const catalog = data(
      await page.evaluate(() =>
        window.ontolearn!.getProjectCatalog({ pageSize: 64, cursor: null }),
      ),
    )
    expect(catalog.items.map((item) => item.metadata.name).sort()).toEqual(
      ['Electron 空白项目', 'Electron 运维示例'].sort(),
    )
    await page
      .locator(`[data-testid="project-open"][data-project-id="${initial.projectId}"]`)
      .click()
    await expect(page.getByTestId('selected-project-version')).toContainText('版本 1')
    const reopened = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology' })),
    )
    expect(reopened.domain).toEqual(initial.domain)
    expect(reopened.workspace.draft).toMatchObject({
      state: 'present',
      generation: 1,
      boundDomainRevision: 1,
      contentJson,
    })
    await test.info().attach('actual-mainline-create-restart', {
      body: JSON.stringify(
        {
          launch,
          blankProjectId: blank.projectId,
          initial,
          draft,
          reopened,
          boundary:
            'Creation/open use real UI; draft/read use the real named renderer bridge. Ontology/query page editing and formal M Job are separate acceptance.',
        },
        null,
        2,
      ),
      contentType: 'application/json',
    })
  } finally {
    await application?.close()
  }
})
