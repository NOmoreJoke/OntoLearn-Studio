import { randomUUID } from 'node:crypto'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import type { BridgeResult } from '@ontolearn/contracts'
import { chromium, type Browser, type Page } from '@playwright/test'
import { build } from 'vite'
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest'
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import {
  buildLearningFixturePlan,
  commitLearningTaskFixture,
  prepareLearningTaskFixture,
} from '../../apps/desktop/src/renderer/src/learning/task-fixture'
import {
  entityEditPlan,
  projectOntology,
} from '../../apps/desktop/src/renderer/src/ontology/mainline-ontology'
import {
  prepareWorkspaceChange,
  requireWorkspaceReply,
} from '../../apps/desktop/src/renderer/src/ontology/workspace-change'
import { sourceText } from '../../apps/desktop/src/renderer/src/query/QueryResultPanel'

function samples() {
  let seed = 0xf08
  const next = () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0
    return seed >>> 16
  }
  const alphabet = ['a', 'Z', '中', '字', '🌱', '🙂']
  return [
    0,
    1,
    255,
    256,
    257,
    511,
    ...Array.from({ length: 128 }, () => 257 + (next() % 340)),
    ...Array.from({ length: 128 }, () => next() % 257),
  ].map((length) => Array.from({ length }, () => alphabet[next() % alphabet.length]))
}

it('F08 truncates mixed Unicode text at the codepoint boundary', () => {
  for (const points of samples()) {
    const expected = points.length > 256 ? points.slice(0, 256).join('') + '…' : points.join('')
    const actual = sourceText(points.join(''))
    expect(actual).toBe(expected)
    expect(actual).not.toMatch(/[\uD800-\uDFFF]/u)
  }
})

it('commits editable declarations for LX-01 and both transfer fixtures through the real engine', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'w3a-learning-fixtures-'))
  const supervisor = new EngineSupervisor(
    { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: resolve('.') },
    {
      profile: 'business3',
      dataPath: join(directory, 'owned.sqlite'),
      exampleRoot: resolve(
        'build/release-resources/fr003-bundle-v2/examples/equipment-maintenance/loader',
      ),
    },
  )
  const tasks = new TaskService(supervisor)
  const projects = new ProjectMainlineService(supervisor, tasks, () => tasks.attachView(() => {}))
  const replies = supervisor.mainlineReplyReceiver()
  const receive = async <T>(work: () => Promise<BridgeResult<T>>): Promise<BridgeResult<T>> => {
    const { value, receipt } = await replies.receive(work)
    replies.consume(receipt)
    return value
  }
  const bridge = {
    readProject: (args: { editor: string }) => receive(() => projects.readProject(args)),
    previewProjectChangeset: (args: Parameters<typeof projects.previewProjectChangeset>[0]) =>
      receive(() => projects.previewProjectChangeset(args)),
    getProjectDiffPage: (args: Parameters<typeof projects.getProjectDiffPage>[0]) =>
      receive(() => projects.getProjectDiffPage(args)),
    confirmProjectChangeset: (args: Parameters<typeof projects.confirmProjectChangeset>[0]) =>
      receive(() => projects.confirmProjectChangeset(args)),
    commitProjectChangeSet: (args: Parameters<typeof projects.commitProjectChangeSet>[0]) =>
      receive(() => projects.commitProjectChangeSet(args)),
    getJob: (id: string) => tasks.getJob(id),
  }
  const requireCurrent = () => {}
  const read = async () => requireWorkspaceReply(await bridge.readProject({ editor: 'quality' }))
  const commit = async (proposal: Awaited<ReturnType<typeof prepareWorkspaceChange>>) => {
    const job = await commitLearningTaskFixture(bridge, proposal, randomUUID(), requireCurrent)
    expect(job.state, JSON.stringify(job.error)).toBe('succeeded')
  }
  const iri = 'urn:ontolearn:learning:'
  const transferEntities = [
    'Alarm',
    'Equipment',
    'HighRiskEquipment',
    'WorkOrder',
    'alarm',
    'eventOrder',
    'level',
    'name',
    'status',
    'workOrderStatus',
  ]

  try {
    for (const [task, identifiers] of [
      ['quality', ['Person', 'assignedTo']],
      ['transfer-repair', transferEntities],
      ['transfer-classify', transferEntities],
    ] as const) {
      const operationId = randomUUID()
      const result =
        task === 'quality'
          ? await receive(() =>
              projects.createExampleProject({
                exampleCreateRequestVersion: 1,
                operationId,
                name: 'LX-01 fixture test',
                exampleId: 'equipment-maintenance',
                inputDigest: '52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e',
              }),
            )
          : await receive(() =>
              projects.createBlankProject({
                requestVersion: 1,
                operationId,
                name: task,
                initialization: { kind: 'blank' },
              }),
            )
      const { projectId } = requireWorkspaceReply<{ projectId: string }>(result)
      requireWorkspaceReply(await receive(() => projects.openProject({ projectId })))
      const proposal = await prepareLearningTaskFixture(bridge, projectId, task, requireCurrent)
      expect(proposal, task).toBeDefined()
      await commit(proposal!)

      const source = await read()
      const projection = projectOntology(source)
      const fixture = projection.homes.find(({ id }) =>
        task === 'quality' ? id.startsWith('learning-lx01.') : id === `${task}.ontology`,
      )
      expect(fixture?.value.entityMetadata).toEqual({
        entityMetadataVersion: 1,
        entities: Object.fromEntries(
          identifiers.map((identifier) => [
            iri + identifier,
            { identifier, labels: [], definitions: [], synonyms: [], examples: [] },
          ]),
        ),
      })
      if (task !== 'quality') continue

      await expect(buildLearningFixturePlan(source, task)).resolves.toBeUndefined()
      const assignedTo = projection.view.objects.find((entity) => entity.iri === iri + 'assignedTo')
      expect(assignedTo).toMatchObject({ kind: 'objectProperty', identifier: 'assignedTo' })
      const axioms = { domain: [iri + 'Equipment'], range: [iri + 'Person'] }
      const edit = entityEditPlan(projection, {
        action: 'edit',
        object: { ...assignedTo!, ...axioms },
      })
      await commit(await prepareWorkspaceChange(bridge, source, edit, requireCurrent))
      const readback = projectOntology(await read())
      expect(
        readback.view.objects.find((entity) => entity.iri === iri + 'assignedTo'),
      ).toMatchObject({ identifier: 'assignedTo', ...axioms })
      expect(readback.metadataHomes.get(iri + 'Person')).toEqual(
        readback.metadataHomes.get(iri + 'assignedTo'),
      )
    }
  } finally {
    projects.dispose()
    tasks.dispose()
    await supervisor.stopAndWait()
    await rm(directory, { recursive: true, force: true })
  }
}, 30_000)

describe.skipIf(process.env.T09_HEADLESS_UI !== '1')('W3a headless component interactions', () => {
  let browser: Browser
  let page: Page
  let script: string
  const errors: string[] = []
  beforeAll(async () => {
    const renderer = resolve('apps/desktop/src/renderer/src')
    const entry = '\0w3a-component-entry'
    const compiled = await build({
      configFile: false,
      logLevel: 'error',
      oxc: { jsx: { runtime: 'automatic', development: false } },
      plugins: [
        {
          name: 'w3a-headless-components',
          resolveId(id) {
            if (id === 'w3a-component-entry' || id === resolve('w3a-component-entry')) return entry
          },
          load(id) {
            if (id !== entry) return
            return `
            import React from 'react'
            import { createRoot } from 'react-dom/client'
            import { flushSync } from 'react-dom'
            import { TruncatedSourceText } from ${JSON.stringify(renderer + '/query/QueryResultPanel.tsx')}
            import { QualityWorkspace } from ${JSON.stringify(renderer + '/quality/QualityWorkspace.tsx')}
            import { MentorPanel } from ${JSON.stringify(renderer + '/learning/MentorPanel.tsx')}
            import { LearningController } from ${JSON.stringify(renderer + '/learning/learning-controller.ts')}
            const root = createRoot(document.getElementById('root'))
            const render = (component, props) => flushSync(() => root.render(React.createElement(component, props)))
            const projectId = 'a0000000-0000-4000-8000-000000000001'
            const snapshot = 'a'.repeat(64)
            const ok = (data) => ({ ok: true, data })
            window.calls = []
            window.mountSource = value => render(TruncatedSourceText, { value })
            window.clickSourceToggle = button => flushSync(() => button.click())
            window.mountQuality = () => {
              const metadata = { state: 'stale', inputSnapshotId: snapshot, staleReasons: [
                { code: 'FACTS_CHANGED', dependency: 'facts', before: 1, after: 2 }
              ]}
              const triple = ['urn:test:pump', 'urn:test:type', '<urn:test:HighRisk>']
              const finding = {
                tier: 'violation', focusNode: 'urn:test:pump', path: 'urn:test:name',
                constraint: 'required', sourceShape: 'urn:test:shape', value: null,
                targets: { subject: 'urn:test:pump', predicate: 'urn:test:name', object: null },
              }
              const state = {
                qualityReadVersion: 1, projectId, rules: [], constraints: [],
                reasoning: { ...metadata, derivation: { rules: [triple], rdfs: [], ruleTraces: [
                  { rule: 'R-risk', output: triple, inputs: [triple] }
                ], rdfsTraces: [], warnings: ['RULE_CHAIN_UNSUPPORTED'] }},
                validation: { ...metadata, conforms: false, findings: [finding] },
              }
              const current = {
                ...state,
                reasoning: { ...state.reasoning, state: 'current', staleReasons: [] },
                validation: { ...state.validation, state: 'current', staleReasons: [], conforms: true, findings: [] },
              }
              render(QualityWorkspace, {
                projectId,
                onDomainSnapshotUpdated: (source) => calls.push(['snapshot', source]),
                onLocateTarget: (targets, finding) => calls.push(['locate', targets, finding.sourceShape]),
                bridge: {
                  async readProject(args) {
                    calls.push(['read', args])
                    return ok({ projectId, inputSnapshotId: snapshot, domain: { projectRevision: 2, state: { definitions: [], facts: [] } } })
                  },
                  async getProjectQualityState(args) { calls.push(['quality', args]); return ok(state) },
                  async runProjectQualityCheck(args) {
                    calls.push(['check', args.validationScope])
                    return ok({ projectId, qualityState: current,
                      reasoningJob: { state: 'succeeded' }, validationJobs: [{ state: 'succeeded' }] })
                  },
                },
              })
            }
            window.mountMentor = async () => {
              const task = (taskId) => ({
                taskId, checkStatus: 'not-checked', operationComplete: false, maxHintLevel: 0,
                assistance: 'independent', instructions: '操作', completionCondition: '完成条件',
                steps: [], inputVersion: '1', attemptId: 'attempt', checkAvailability: { available: true },
                revealedHints: [], commonErrors: [], knowledgePoints: [], readings: [],
              })
              const controller = new LearningController({
                async getProjectLearningState() { return ok({
                  projectId, domainSnapshotRef: snapshot, domainRevision: 1,
                  courseMeta: { firstTask: 'quality' },
                  tasks: ['quality', 'transfer-classify'].map(task),
                  observations: [], readings: [], glossary: [], flashcards: [],
                }) },
                async checkLearningTask(args) {
                  calls.push(['origins', args.selectedOrigins])
                  return { ok: false, error: { code: 'INVALID_STATE', messageKey: 'task.invalid', retryable: false, params: {} } }
                },
              })
              await controller.selectAndRefresh(projectId)
              controller.focusTask('quality')
              window.focusTask = taskId => controller.focusTask(taskId)
              render(MentorPanel, {
                controller, disabled: false, onOpenOntologyRepair() {},
                onOpenQualityWorkspace() { calls.push(['navigate', 'quality']) },
                refreshCheckpoints: async () => {},
              })
            }
          `
          },
        },
      ],
      define: { 'process.env.NODE_ENV': JSON.stringify('production') },
      build: {
        write: false,
        lib: { entry: 'w3a-component-entry', formats: ['iife'], name: 'W3aHarness' },
      },
    })
    const outputs = Array.isArray(compiled) ? compiled : [compiled]
    script = outputs
      .flatMap((output) => ('output' in output ? output.output : []))
      .filter((output) => output.type === 'chunk')
      .map((output) => output.code)
      .join('\n')
    expect(script).toBeTruthy()
    browser = await chromium.launch({
      headless: true,
      chromiumSandbox: true,
      ignoreDefaultArgs: ['--disable-hang-monitor', '--use-mock-keychain'],
    })
  }, 30_000)

  beforeEach(async () => {
    errors.length = 0
    page = await browser.newPage()
    page.setDefaultTimeout(3500)
    page.on('pageerror', (error) => errors.push(error.message))
    await page.route('**/*', (route) => route.abort())
    // A fulfilled secure origin supplies the same Crypto API as Electron.
    await page.route('https://w3a.test/', (route) =>
      route.fulfill({
        contentType: 'text/html',
        body: '<!doctype html><html lang="zh-CN"><div id="root"></div></html>',
      }),
    )
    await page.goto('https://w3a.test/')
    await page.addScriptTag({ content: script })
  })
  afterEach(async () => {
    await page?.close()
    expect(errors).toEqual([])
  })
  afterAll(async () => {
    await browser?.close()
  })

  it('round-trips expansion in the DOM for 128+ mixed Unicode inputs', async () => {
    const mismatches = await page.evaluate((cases) => {
      const browser = window as unknown as {
        mountSource(value: string): void
        clickSourceToggle(button: HTMLButtonElement): void
      }
      const root = document.getElementById('root')!
      const errors = []
      for (const [index, points] of cases.entries()) {
        const text = points.join('')
        browser.mountSource(text)
        const code = root.querySelector('code')!
        const toggle = root.querySelector('button')
        if (points.length <= 256) {
          if (code.textContent !== text || toggle) errors.push([index, 'short'])
          continue
        }
        const excerpt = points.slice(0, 256).join('') + '…'
        if (code.textContent !== excerpt || toggle?.getAttribute('aria-expanded') !== 'false') {
          errors.push([index, 'collapsed'])
          continue
        }
        browser.clickSourceToggle(toggle)
        if (code.textContent !== text || toggle.textContent !== '收起全文')
          errors.push([index, 'expanded'])
        browser.clickSourceToggle(toggle)
        if (code.textContent !== excerpt || toggle.textContent !== '展开全文')
          errors.push([index, 'recollapsed'])
      }
      return errors
    }, samples())
    expect(mismatches).toEqual([])
  })

  it('renders stale reasons and traces, locates a finding, and refreshes after a check', async () => {
    await page.evaluate(() => (window as unknown as { mountQuality(): void }).mountQuality())
    const check = page.getByTestId('quality-btn-run-check')
    await page
      .getByTestId('quality-stale-reasons')
      .getByText(/FACTS_CHANGED/)
      .first()
      .waitFor()
    await page.getByTestId('quality-rule-traces').getByText('R-risk', { exact: true }).waitFor()
    await page.getByText(/不支持规则链。规则输出/).waitFor()
    await page.getByRole('button', { name: '定位' }).click()
    await check.click()
    await page.getByText('检查已完成。').waitFor()
    expect(await page.getByTestId('quality-validation-state').getAttribute('data-conforms')).toBe(
      'true',
    )
    expect(await page.getByTestId('quality-stale-reasons').count()).toBe(0)
    const calls = await page.evaluate(() => (window as unknown as { calls: unknown[] }).calls)
    expect(calls).toContainEqual([
      'locate',
      { subject: 'urn:test:pump', predicate: 'urn:test:name', object: null },
      'urn:test:shape',
    ])
    expect(calls).toContainEqual(['check', 'asserted+derived'])
    expect(calls.filter((call) => Array.isArray(call) && call[0] === 'snapshot')).toHaveLength(2)
  })

  it('forwards temporary LX-01 and transfer selections through the Mentor controller', async () => {
    await page.evaluate(() => (window as unknown as { mountMentor(): Promise<void> }).mountMentor())
    const check = page.getByTestId('mentor-btn-check')
    await page.getByTestId('learning-open-quality-workspace').click()
    await page.getByTestId('learning-lx01-origin-l02').selectOption('derived')
    await check.click()
    const focus = (id: string) =>
      page.evaluate(
        (taskId) => (window as unknown as { focusTask(id: string): void }).focusTask(taskId),
        id,
      )
    await focus('transfer-classify')
    const first = page.getByTestId('learning-transfer-origin-0')
    expect(await first.inputValue()).toBe('')
    await first.selectOption('asserted')
    await page.getByTestId('learning-transfer-origin-1').selectOption('derived')
    await check.click()
    await focus('quality')
    expect(await page.getByTestId('learning-lx01-origin-l02').inputValue()).toBe('')
    const calls = await page.evaluate(() => (window as unknown as { calls: unknown[] }).calls)
    expect(calls).toEqual([
      ['navigate', 'quality'],
      ['origins', { 'urn:ontolearn:learning:person/L02': 'derived' }],
      ['origins', ['asserted', 'derived']],
    ])
  })
})
