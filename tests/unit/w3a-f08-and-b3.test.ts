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
            window.mountQuality = (mode) => {
              mode = mode || 'plain'
              const metadata = { state: 'stale', inputSnapshotId: snapshot, staleReasons: [
                { code: 'FACTS_CHANGED', dependency: 'facts', before: 1, after: 2 }
              ]}
              const triple = ['urn:test:pump', 'urn:test:type', '<urn:test:HighRisk>']
              const finding = {
                tier: 'violation', focusNode: 'urn:test:pump', path: 'urn:test:name',
                constraint: 'required', sourceShape: 'urn:test:shape', value: null,
                ...(mode === 'coverage' ? { definitionId: 'name-required' } : {}),
                targets: { subject: 'urn:test:pump', predicate: 'urn:test:name', object: null },
              }
              const base = {
                qualityReadVersion: 1, projectId, rules: [], constraints: [],
                reasoning: { ...metadata, derivation: { rules: [triple], rdfs: [], ruleTraces: [
                  { rule: 'R-risk', output: triple, inputs: [triple] }
                ], rdfsTraces: [], warnings: ['RULE_CHAIN_UNSUPPORTED'] }},
                validation: { ...metadata, conforms: false, findings: [finding] },
              }
              let state = base
              if (mode === 'coverage') {
                state = { ...base,
                  validation: { ...metadata, state: 'current', staleReasons: [], conforms: null,
                    scope: 'asserted', inputProjectRevision: 7,
                    checkedConstraintIds: ['name-required'],
                    unverifiedConstraintIds: ['unverified-shape'], failedConstraintIds: ['failed-shape'],
                    constraintVersions: [{ definitionId: 'name-required', version: 1 }],
                    findings: [] },
                  snapshotsAligned: false }
              }
              if (mode === 'chain') {
                state = { ...base, rules: [{ id: 'R-risk', enabled: true, revision: 3, format: 'fr505',
                  label: 'R-risk 分类',
                  conditions: [{ kind: 'type', subject: '?equipment', class: 'urn:test:Equipment' }],
                  conclusions: [{ kind: 'type', subject: '?equipment', class: 'urn:test:HighRisk' }] }] }
              }
              if (mode === 'legacy-chain') {
                state = { ...base, rules: [{ id: 'R-risk', enabled: true, revision: 1, format: 'legacy',
                  when: [
                    ['?equipment', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', '<urn:ontolearn:learning:Equipment>'],
                    ['?equipment', 'urn:ontolearn:learning:alarm', '?alarm'],
                    ['?alarm', 'urn:ontolearn:learning:level', '"High"'],
                    ['?alarm', 'urn:ontolearn:learning:status', '"Open"'],
                  ],
                  then: ['?equipment', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', '<urn:ontolearn:learning:HighRiskEquipment>'] }] }
              }
              const current = {
                ...state,
                reasoning: { ...state.reasoning, state: 'current', staleReasons: [] },
                validation: { ...state.validation, state: 'current', staleReasons: [], conforms: true, findings: [] },
              }
              const sampleResult = mode === 'sample-invalid'
                ? { valid: false, matchesExpected: false,
                    actualOutputs: [], rdfsOutputs: [], expectedOutputs: [],
                    missingOutputs: [], unexpectedOutputs: [],
                    ruleTraces: [], warnings: [],
                    diagnostics: [{ stage: 'rule', index: 0, ruleId: 'R-tag', field: 'conditions',
                      code: 'MIN_ITEMS', message: 'MIN_ITEMS：rule[0] conditions 至少 1 项' }],
                    omittedDiagnosticCount: 3 }
                : { valid: true, matchesExpected: false,
                    actualOutputs: [['urn:test:subject', 'urn:test:predicate', '<urn:test:object>']],
                    rdfsOutputs: [['urn:test:person/L02', 'urn:test:type', '<urn:test:Person>']],
                    expectedOutputs: [['urn:test:subject', 'urn:test:predicate', '<urn:test:missing>']],
                    missingOutputs: [['urn:test:subject', 'urn:test:predicate', '<urn:test:missing>']],
                    unexpectedOutputs: [['urn:test:subject', 'urn:test:predicate', '<urn:test:object>']],
                    ruleTraces: [], warnings: ['RULE_CHAIN_UNSUPPORTED:R-next'],
                    diagnostics: [{ stage: 'input', index: 0, ruleId: null, field: '2', code: 'INVALID_TERM',
                      message: 'INVALID_TERM：input[0] 2 校验失败' }] }
              render(QualityWorkspace, {
                projectId,
                onDomainSnapshotUpdated: (source) => calls.push(['snapshot', source]),
                onLocateTarget: (targets, finding) => calls.push(['locate', targets, finding.sourceShape]),
                bridge: {
                  async readProject(args) {
                    calls.push(['read', args])
                    return ok({ projectId, inputSnapshotId: snapshot, domain: { projectRevision: 2, state: { definitions: [], facts: [] } } })
                  },
                  async getProjectQualityState(args) {
                    calls.push(['quality', args])
                    if (args.ruleTest) {
                      calls.push(['sample', args.ruleTest.rules.map((rule) => rule.id), args.ruleTest.inputTriples.length])
                      return ok({ ...state, ruleTestResult: sampleResult })
                    }
                    return ok(state)
                  },
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

  it('surfaces incomplete coverage, snapshot mismatch and revision without claiming conformance', async () => {
    await page.evaluate(() =>
      (window as unknown as { mountQuality(mode?: string): void }).mountQuality('coverage'),
    )
    const coverage = page.getByTestId('quality-validation-coverage')
    await coverage.waitFor()
    const coverageText = await coverage.textContent()
    expect(coverageText).toContain('未判定为符合约束')
    expect(coverageText).toContain('未检：unverified-shape')
    expect(coverageText).toContain('失败：failed-shape')
    const mismatch = page.getByTestId('quality-snapshot-mismatch')
    await mismatch.waitFor()
    expect(await mismatch.textContent()).toContain('不同快照')
    const state = page.getByTestId('quality-validation-state')
    const stateText = await state.textContent()
    expect(stateText).toContain('范围 asserted')
    expect(stateText).toContain('rev 7')
    expect(stateText).toContain('约束版本 name-required@v1')
    expect(await state.getAttribute('data-conforms')).toBe(null)
    expect(stateText).not.toContain('· 符合约束')
  })

  it('warns live while composing a chained rule and runs FR-505 samples through the bridge', async () => {
    await page.evaluate(() =>
      (window as unknown as { mountQuality(mode?: string): void }).mountQuality('chain'),
    )
    await page.getByLabel('定义类型', { exact: true }).selectOption('rule')
    await page.getByLabel('稳定标识', { exact: true }).fill('R-next')
    const row = page
      .getByRole('group', { name: '全部满足以下条件（合取）' })
      .locator('.quality-pattern')
      .first()
    await row.getByLabel('主体变量或 IRI', { exact: true }).fill('?equipment')
    await row.getByLabel('类 IRI', { exact: true }).fill('urn:test:HighRisk')
    const warning = page.getByTestId('quality-editor-chain-warning')
    await warning.waitFor()
    const warningText = await warning.textContent()
    expect(warningText).toContain('R-risk → R-next')
    expect(warningText).not.toContain('R-next → R-next')
    // Filling a real conclusion restores the enabled draft's self chain.
    const conclusion = page
      .getByRole('group', { name: '推导一个或多个新事实' })
      .locator('.quality-pattern')
      .first()
    await conclusion.getByLabel('主体变量或 IRI', { exact: true }).fill('?equipment')
    await conclusion
      .getByLabel('类 IRI', { exact: true })
      .fill('urn:ontolearn:learning:NeedsInspection')
    expect(await warning.textContent()).toContain('R-next → R-next')

    await page.getByTestId('quality-rule-sample-tester').locator('summary').click()
    await page.getByTestId('quality-sample-preset').selectOption('rule-chain-unsupported')
    await page.getByTestId('quality-btn-run-sample').click()
    const result = page.getByTestId('quality-sample-result')
    await result.getByText('预期不一致').waitFor()
    const resultText = await result.textContent()
    expect(resultText).toContain('urn:test:object')
    expect(resultText).toContain('urn:test:missing')
    expect(resultText).toContain('INVALID_TERM')
    expect(resultText).toContain('input[0]')
    const calls = await page.evaluate(() => (window as unknown as { calls: unknown[] }).calls)
    expect(calls).toContainEqual(['sample', ['R-risk', 'R-next'], 2])
  })

  it('warns live against an imported legacy rule while composing a chained rule', async () => {
    await page.evaluate(() =>
      (window as unknown as { mountQuality(mode?: string): void }).mountQuality('legacy-chain'),
    )
    await page.getByLabel('定义类型', { exact: true }).selectOption('rule')
    await page.getByLabel('稳定标识', { exact: true }).fill('R-next')
    const row = page
      .getByRole('group', { name: '全部满足以下条件（合取）' })
      .locator('.quality-pattern')
      .first()
    await row.getByLabel('主体变量或 IRI', { exact: true }).fill('?equipment')
    await row.getByLabel('类 IRI', { exact: true }).fill('urn:ontolearn:learning:HighRiskEquipment')
    const warning = page.getByTestId('quality-editor-chain-warning')
    await warning.waitFor()
    const warningText = await warning.textContent()
    expect(warningText).toContain('R-risk → R-next')
    expect(warningText).not.toContain('R-next → R-next')
    // Filling a real conclusion restores the enabled draft's self chain.
    const conclusion = page
      .getByRole('group', { name: '推导一个或多个新事实' })
      .locator('.quality-pattern')
      .first()
    await conclusion.getByLabel('主体变量或 IRI', { exact: true }).fill('?equipment')
    await conclusion
      .getByLabel('类 IRI', { exact: true })
      .fill('urn:ontolearn:learning:NeedsInspection')
    expect(await warning.textContent()).toContain('R-next → R-next')
  })

  it('keeps an invalid sample verdict without a fake order match and reports omitted diagnostics', async () => {
    await page.evaluate(() =>
      (window as unknown as { mountQuality(mode?: string): void }).mountQuality('sample-invalid'),
    )
    await page.getByTestId('quality-rule-sample-tester').locator('summary').click()
    await page.getByTestId('quality-sample-preset').selectOption('order-independent')
    await page.getByTestId('quality-btn-run-sample').click()
    const result = page.getByTestId('quality-sample-result')
    await result.getByText('存在校验错误').waitFor()
    const omitted = page.getByTestId('quality-sample-diagnostics-omitted')
    await omitted.waitFor()
    expect(await omitted.textContent()).toContain('另有 3 条')
    expect(await result.textContent()).not.toContain('正反保存顺序对比一致')
  })

  it('rejects hollow sample rules with a front-end message before any bridge dispatch', async () => {
    await page.evaluate(() => (window as unknown as { mountQuality(): void }).mountQuality())
    await page.getByTestId('quality-rule-sample-tester').locator('summary').click()
    await page
      .getByTestId('quality-sample-rules')
      .fill(
        JSON.stringify([
          { id: 'R-empty', label: '空规则', enabled: true, conditions: [], conclusions: [] },
        ]),
      )
    await page.getByTestId('quality-btn-run-sample').click()
    const alert = page.getByRole('alert')
    await alert.waitFor()
    expect(await alert.textContent()).toBe('样本规则至少需要 1 条条件与 1 条结论。')
    const calls = await page.evaluate(() => (window as unknown as { calls: unknown[] }).calls)
    expect(calls.filter((call) => Array.isArray(call) && call[0] === 'sample')).toHaveLength(0)
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
    await page.getByText('equipment/201 name "检测泵"').waitFor()
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
