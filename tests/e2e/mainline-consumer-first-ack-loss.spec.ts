import { test, expect, type ElectronApplication, type Page } from '@playwright/test'
import { resolve } from 'node:path'
import type {
  BridgeResult,
  JobView,
  MainlineProjectReadDTO,
  QueryExecutionReceiptDTO,
} from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'
import {
  observeUI,
  receiptHasOperation,
  reconciliationReady,
  updateObservationSlot,
  type UISnapshot,
} from './ui-observation'

const key = '__t01_owned_first_consumer_ack_loss_v1'
const commitChannel = 'project:changeset-commit'
const executeChannel = 'query:execute-saved'
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
const hash = /^[0-9a-f]{64}$/
type Envelope = { deliveryVersion: 1; deliveryId: string; payload: unknown }
type InventoryPage = {
  binding: { projectId: string; filter: string; order: string; listSnapshotId: string }
  jobs: JobView[]
  nextCursor: string | null
}
type Observation = {
  target: string
  commitCalls: number
  executeCalls: number
  dropped: boolean
  targetOrdinalAtDrop: number | null
  lostAckCalls: number
  request: Record<string, unknown> | null
  envelope: Envelope | null
  targetRequests: unknown[]
  targetReplies: unknown[]
  sameSenderFrame: boolean[]
}
function data<T>(response: BridgeResult<T>): T {
  if (!response.ok) throw new Error(`Actual named read refused: ${JSON.stringify(response.error)}`)
  return response.data
}
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    const encoded = JSON.stringify(value)
    if (encoded === undefined) throw new Error('Invalid independent fixture')
    return encoded
  }
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']'
  const object = value as Record<string, unknown>
  return (
    '{' +
    Object.keys(object)
      .sort()
      .map((name) => JSON.stringify(name) + ':' + canonical(object[name]))
      .join(',') +
    '}'
  )
}

async function installFirstAckLoss(application: ElectronApplication, target: string) {
  await application.evaluate(
    ({ ipcMain }, config) => {
      type Handler = (...args: unknown[]) => unknown
      const handlers = Reflect.get(ipcMain, '_invokeHandlers') as Map<string, Handler>
      if (!(handlers instanceof Map) || Reflect.has(globalThis, config.key))
        throw new Error('Owned registered-handler instrumentation unavailable or already installed')
      const state = {
        target: config.target,
        commitCalls: 0,
        executeCalls: 0,
        dropped: false,
        targetOrdinalAtDrop: null as number | null,
        lostAckCalls: 0,
        request: null as Record<string, unknown> | null,
        envelope: null as { deliveryVersion: 1; deliveryId: string; payload: unknown } | null,
        targetRequests: [] as unknown[],
        targetReplies: [] as unknown[],
        sameSenderFrame: [] as boolean[],
        sender: undefined as object | undefined,
        frame: undefined as object | undefined,
        originals: new Map<string, Handler>(),
        wrappers: new Map<string, Handler>(),
      }
      for (const channel of [config.commit, config.execute, 'project:reply-received']) {
        const original = handlers.get(channel)
        if (typeof original !== 'function') throw new Error('Production registered handler missing')
        const wrapped: Handler = async (...args) => {
          if (channel === config.commit) state.commitCalls++
          if (channel === config.execute) state.executeCalls++
          if (channel === config.target) {
            const event = args[0] as { sender: object; senderFrame: object }
            state.sender ??= event.sender
            state.frame ??= event.senderFrame
            state.sameSenderFrame.push(
              event.sender === state.sender && event.senderFrame === state.frame,
            )
            state.targetRequests.push(structuredClone(args[1]))
          }
          if (channel === 'project:reply-received') {
            const ack = args[1]
            if (
              ack &&
              typeof ack === 'object' &&
              'deliveryId' in ack &&
              ack.deliveryId === state.envelope?.deliveryId
            )
              state.lostAckCalls++
          }
          // Original event/senderFrame/args/trust/issuer/Job/worker stay untouched.
          const actual: unknown = await original(...args)
          if (channel === config.target) state.targetReplies.push(actual)
          if (channel === config.target && !state.dropped) {
            if (
              !actual ||
              typeof actual !== 'object' ||
              !('deliveryVersion' in actual) ||
              actual.deliveryVersion !== 1 ||
              !('deliveryId' in actual) ||
              typeof actual.deliveryId !== 'string' ||
              !('payload' in actual) ||
              !actual.payload ||
              typeof actual.payload !== 'object' ||
              !('ok' in actual.payload) ||
              actual.payload.ok !== true
            )
              throw new Error('First original target did not return a successful real delivery')
            const request = args[1]
            if (!request || typeof request !== 'object' || Array.isArray(request))
              throw new Error('Original named request is missing')
            // Synchronous observation then throw IMMEDIATELY at first real return.
            // There is no terminal wait, extra Job lookup, event suppression or forged reply.
            state.request = structuredClone(request) as Record<string, unknown>
            state.envelope = actual as { deliveryVersion: 1; deliveryId: string; payload: unknown }
            state.targetOrdinalAtDrop =
              channel === config.commit ? state.commitCalls : state.executeCalls
            state.dropped = true
            throw new Error('T01_OWNED_FIRST_CONSUMER_ACK_LOST')
          }
          return actual
        }
        state.originals.set(channel, original)
        state.wrappers.set(channel, wrapped)
      }
      Reflect.set(globalThis, config.key, state)
      for (const [channel, wrapped] of state.wrappers) handlers.set(channel, wrapped)
    },
    { key, target, commit: commitChannel, execute: executeChannel },
  )
}
async function inspect(application: ElectronApplication): Promise<Observation> {
  return application.evaluate((_, name) => {
    const state = Reflect.get(globalThis, name) as Observation
    return {
      target: state.target,
      commitCalls: state.commitCalls,
      executeCalls: state.executeCalls,
      dropped: state.dropped,
      targetOrdinalAtDrop: state.targetOrdinalAtDrop,
      lostAckCalls: state.lostAckCalls,
      request: state.request,
      envelope: state.envelope,
      targetRequests: state.targetRequests,
      targetReplies: state.targetReplies,
      sameSenderFrame: state.sameSenderFrame,
    }
  }, key)
}
async function removeFault(application: ElectronApplication) {
  await application.evaluate(({ ipcMain }, name) => {
    type Handler = (...args: unknown[]) => unknown
    const state = Reflect.get(globalThis, name) as
      | {
          originals: Map<string, Handler>
          wrappers: Map<string, Handler>
        }
      | undefined
    if (!state) return
    const handlers = Reflect.get(ipcMain, '_invokeHandlers') as Map<string, Handler>
    for (const [channel, original] of state.originals) {
      if (handlers.get(channel) !== state.wrappers.get(channel))
        throw new Error('Registered handler changed during owned instrumentation')
      handlers.set(channel, original)
    }
    // Restores instrumentation only. Does NOT ACK/consume/delete the production lost lease.
    Reflect.deleteProperty(globalThis, name)
  }, key)
}
async function launch() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  return launchIsolatedDesktop({
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  })
}
async function create(page: Page, example: boolean): Promise<MainlineProjectReadDTO> {
  await page.getByTestId('project-name').fill(example ? 'Query 首受理ACK丢失' : '本体首受理ACK丢失')
  await page.getByTestId(example ? 'project-create-example' : 'project-create').click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
    '项目已创建并打开',
  )
  await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
  return data(
    await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology-transaction' })),
  )
}
async function read(page: Page) {
  return data(
    await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology-transaction' })),
  )
}
async function allJobs(page: Page, projectId: string): Promise<JobView[]> {
  let listSnapshotId: string | null = null
  let cursor: string | null = null
  const seen = new Set<string>()
  const jobs: JobView[] = []
  for (let index = 0; index < 32; index++) {
    const raw: InventoryPage = data(
      await page.evaluate((args) => window.ontolearn!.listJobs(args), {
        filter: 'all' as const,
        pageSize: 100,
        listSnapshotId,
        cursor,
      }),
    ) as InventoryPage
    expect(raw.binding.projectId).toBe(projectId)
    expect(raw.binding.filter).toBe('all')
    expect(raw.binding.order).toBe('createdAtMs+jobId:asc')
    expect(raw.binding.listSnapshotId).toMatch(uuid)
    listSnapshotId ??= raw.binding.listSnapshotId
    expect(raw.binding.listSnapshotId).toBe(listSnapshotId)
    for (const job of raw.jobs) {
      expect(job.projectId).toBe(projectId)
      expect(jobs.some((old) => old.jobId === job.jobId)).toBe(false)
      const previous = jobs.at(-1)
      if (previous) {
        const before = previous.createdAtMs as number
        const after = job.createdAtMs as number
        expect(after > before || (after === before && job.jobId > previous.jobId)).toBe(true)
      }
      jobs.push(job)
    }
    if (raw.nextCursor === null) return jobs
    expect(seen.has(raw.nextCursor)).toBe(false)
    seen.add(raw.nextCursor)
    cursor = raw.nextCursor
  }
  throw new Error('Bounded all-state fixed Job inventory did not finish')
}

test('actual ontology consumer reconciles first lost commit ACK without another submit', async () => {
  test.setTimeout(60000)
  const application = await launch()
  let instrumented = false
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  const observed = (value: unknown) => {
    evidence.lastCompletedObservation = JSON.parse(
      updateObservationSlot(test.info().annotations, 'first-ack-loss', stage, {
        operationId: evidence.operationId,
        jobId: evidence.jobId,
        value,
      }),
    )
  }
  try {
    const page = await application.firstWindow()
    const initial = await create(page, false)
    evidence.initial = initial
    observed({ projectId: initial.projectId, inputSnapshotId: initial.inputSnapshotId })
    expect(initial.domain.projectRevision).toBe(0)
    expect(initial.domain.state).toEqual({ definitions: [], facts: [], mappingState: {} })
    expect(await allJobs(page, initial.projectId)).toEqual([])
    await page.getByRole('link', { name: '本体构建', exact: true }).click()
    const panel = page.getByRole('region', { name: '本体项目编辑', exact: true })
    // No manual read/retry: this waits for the real initial owned-session auto-read.
    await expect(panel.getByRole('region', { name: '本体编辑表单', exact: true })).toBeVisible()
    await expect(panel.getByRole('alert')).toHaveCount(0)
    await panel.getByRole('button', { name: '新建概念', exact: true }).click()
    const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
    const iri = 'urn:t01:ack-loss:Asset'
    await form.getByLabel('稳定 IRI', { exact: true }).fill(iri)
    await form.getByLabel('英文标识', { exact: true }).fill('AckLostAsset')
    await form.getByRole('button', { name: '预览定义修改', exact: true }).click()
    const diff = panel.getByRole('region', { name: '完整事务差异', exact: true })
    await expect(diff).toBeVisible()
    const document: unknown = JSON.parse((await diff.locator('pre').textContent()) ?? 'null')
    evidence.fullDiff = document
    observed({ completeDiff: document })
    expect(document).toHaveLength(1)
    const home = (document as Array<{ resource: unknown[] }>)[0]?.resource[2]
    expect(home).toEqual(expect.stringMatching(/^t02-[0-9a-f-]{36}$/))
    if (typeof home !== 'string') throw new Error('Actual Diff home identity missing')
    expect(document).toEqual([
      {
        resource: ['definition', 'ontology', home],
        before: null,
        after: {
          layer: 'ontology',
          id: home,
          payload: canonical({
            triples: [
              {
                subject: iri,
                predicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                object: '<http://www.w3.org/2000/01/rdf-schema#Class>',
              },
            ],
            entityMetadata: {
              entityMetadataVersion: 1,
              entities: {
                [iri]: {
                  identifier: 'AckLostAsset',
                  labels: [],
                  definitions: [],
                  synonyms: [],
                  examples: [],
                },
              },
            },
          }),
        },
      },
    ])
    await installFirstAckLoss(application, commitChannel)
    instrumented = true
    stage = 'original commit handler accepts; first consumer reply throws'
    await diff.getByRole('button', { name: '我已核对完整差异，确认提交', exact: true }).click()
    await expect.poll(async () => (await inspect(application)).dropped).toBe(true)
    const lost = await inspect(application)
    evidence.firstDroppedDelivery = lost
    expect(lost.targetOrdinalAtDrop).toBe(1)
    expect(lost.lostAckCalls).toBe(0)
    expect(lost.commitCalls).toBe(1)
    expect(lost.executeCalls).toBe(0)
    if (!lost.envelope || !lost.request) throw new Error('Original first delivery was not recorded')
    const accepted = data(lost.envelope.payload as BridgeResult<JobView>)
    const operationId = lost.request.operationId
    expect(typeof operationId).toBe('string')
    if (typeof operationId !== 'string') throw new Error('Original operation missing')
    expect(operationId).toMatch(uuid)
    evidence.operationId = operationId
    evidence.jobId = accepted.jobId
    observed({ operationId, accepted })
    expect(accepted).toMatchObject({
      projectId: initial.projectId,
      operationId,
      capability: 'changeset.commit',
      inputSnapshotId: initial.inputSnapshotId,
    })
    expect(lost.request).toMatchObject({
      operationId,
      confirmation: {
        projectId: initial.projectId,
        inputSnapshotId: initial.inputSnapshotId,
      },
    })
    const pending = panel.getByRole('region', { name: '原操作状态', exact: true })
    const receipt = panel.getByRole('region', { name: '已提交回执', exact: true })
    await expect
      .poll(async () => {
        if (await pending.count())
          return (await pending.textContent())?.includes(operationId) ?? false
        if (await receipt.count())
          return (await receipt.textContent())?.includes(operationId) ?? false
        return false
      })
      .toBe(true)
    const observedPending = (await pending.count()) > 0
    if (observedPending) {
      await expect(pending.locator('code')).toHaveText(operationId)
      await expect(
        pending.getByRole('button', { name: '核对原操作与提交回执', exact: true }),
      ).toBeEnabled()
    }
    stage = 'real UI reads original operation and complete Job; no commit replay'
    const reconcile = pending.getByRole('button', { name: '核对原操作与提交回执', exact: true })
    const reconciliation = () =>
      observeUI(
        receipt.or(reconcile),
        [
          { key: 'receipt', kind: 'region', name: '已提交回执' },
          { key: 'reconcile', kind: 'button', name: '核对原操作与提交回执' },
        ],
        observed,
      )
    let reads = 0
    await expect
      .poll(
        async () => {
          if (receiptHasOperation(await reconciliation(), operationId)) return true
          if (++reads > 12)
            throw new Error('Bounded original-operation UI reconciliation exhausted')
          await expect(reconcile).toBeEnabled()
          await reconcile.click()
          let completed: UISnapshot = {}
          await expect
            .poll(
              async () => {
                completed = await reconciliation()
                return reconciliationReady(completed)
              },
              { intervals: [100], timeout: 5000 },
            )
            .toBe(true)
          return receiptHasOperation(completed, operationId)
        },
        { timeout: 5000 },
      )
      .toBe(true)
    await expect(receipt).toContainText('当前已读版本 1。')
    await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled()
    const marker = data(
      await page.evaluate((id) => window.ontolearn!.getOperation(id), operationId),
    )
    evidence.marker = marker
    observed({ marker })
    const job = data(await page.evaluate((id) => window.ontolearn!.getJob(id), accepted.jobId))
    evidence.job = job
    observed({ marker, job })
    const after = await read(page)
    evidence.after = after
    observed({
      projectId: after.projectId,
      projectRevision: after.domain.projectRevision,
      inputSnapshotId: after.inputSnapshotId,
    })
    expect(marker).toEqual({
      projectId: initial.projectId,
      operationId,
      jobId: accepted.jobId,
      projectRevision: 1,
      beforeSnapshotId: initial.inputSnapshotId,
      afterSnapshotId: after.inputSnapshotId,
      planHash: expect.stringMatching(hash),
    })
    if (!marker) throw new Error('Original successful operation marker missing')
    expect(job).toMatchObject({
      ...accepted,
      state: 'succeeded',
      error: null,
      stateVersion: expect.any(Number),
      updatedAtMs: expect.any(Number),
      finishedAtMs: expect.any(Number),
      resultRef: {
        resultId: expect.stringMatching(uuid),
        inputSnapshotId: initial.inputSnapshotId,
      },
      commitProgress: {
        mode: 'atomic',
        operationId,
        marker: {
          projectRevision: 1,
          beforeSnapshotId: initial.inputSnapshotId,
          afterSnapshotId: after.inputSnapshotId,
          planHash: marker.planHash,
        },
      },
    })
    expect(job.input).toEqual(accepted.input)
    expect(job.implementation).toEqual(accepted.implementation)
    expect(job.limits).toEqual(accepted.limits)
    expect(job.confirmationRef).toBe(accepted.confirmationRef)
    expect(job.stateVersion).toBeGreaterThanOrEqual(accepted.stateVersion)
    expect(after.domain.projectRevision).toBe(1)
    expect(after.domain.state.facts).toEqual(initial.domain.state.facts)
    expect(after.domain.state.mappingState).toEqual(initial.domain.state.mappingState)
    const expectedRows = document as Array<{ after: unknown }>
    expect(after.domain.state.definitions).toEqual([expectedRows[0]!.after])
    const inventory = await allJobs(page, initial.projectId)
    expect(inventory).toEqual([job])
    const final = await inspect(application)
    expect(final.commitCalls).toBe(1)
    expect(final.executeCalls).toBe(0)
    expect(final.lostAckCalls).toBe(0)
    expect(final.request).toEqual(lost.request)
    evidence.initial = initial
    evidence.fullDiff = document
    evidence.firstDroppedDelivery = lost
    evidence.observedPending = observedPending
    evidence.job = job
    evidence.marker = marker
    evidence.after = after
    evidence.allStateInventory = inventory
    evidence.final = final
    stage = 'completed'
  } finally {
    try {
      if (instrumented) await removeFault(application)
    } finally {
      try {
        await test.info().attach('ontology-first-consumer-ack-loss', {
          body: JSON.stringify({ stage, ...evidence }, null, 2),
          contentType: 'application/json',
        })
      } finally {
        await application.close()
      }
    }
  }
})

test('actual query consumer recovers first lost ACK with the exact same intent and one Job', async () => {
  test.setTimeout(60000)
  const application = await launch()
  let instrumented = false
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  try {
    const page = await application.firstWindow()
    const initial = await create(page, true)
    expect(initial.domain.projectRevision).toBe(1)
    expect(await allJobs(page, initial.projectId)).toEqual([])
    await page.getByRole('link', { name: '本体查询', exact: true }).click()
    const workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
    const notice = workspace.locator('p[role="status"][aria-live="polite"]')
    await workspace.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
    await expect(notice).toHaveText('项目与持久工作草稿已读回；工作草稿不代表正式查询定义。')
    await workspace
      .getByRole('combobox', { name: '已提交查询', exact: true })
      .selectOption('unclosed-high')
    await workspace
      .getByLabel('我已保留当前编辑，允许重新载入或新建替换它', { exact: true })
      .check()
    await expect(
      workspace.getByRole('button', { name: '按所选当前/历史输入载入定义', exact: true }),
    ).toBeEnabled()
    await workspace
      .getByRole('button', { name: '按所选当前/历史输入载入定义', exact: true })
      .click()
    await expect(notice).toHaveText('已载入真实受管定义；后续编辑需先正式提交。')
    const sparql =
      'PREFIX l: <urn:ontolearn:learning:>\n' +
      'SELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . ' +
      '?alarm l:level "High" ; l:status "Open" . } ORDER BY ?alarm'
    const visibleDraft = {
      name: '未关闭的高等级告警',
      description: '设备运维示例查询',
      sparql,
      scope: 'asserted',
      capabilityQuestion: '哪些高等级告警尚未关闭？',
      source: 'template',
    }
    await expect(workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
      sparql,
    )
    const viewBefore = data(await page.evaluate(() => window.ontolearn!.restoreTasks()))
    expect(viewBefore.project?.projectId).toBe(initial.projectId)
    expect(viewBefore.project?.inputSnapshotId).toBe(initial.inputSnapshotId)
    await installFirstAckLoss(application, executeChannel)
    instrumented = true
    stage = 'first original execute return immediately throws, before consumer sees receipt'
    await workspace
      .getByRole('button', { name: '执行已载入且未改变的受管定义', exact: true })
      .click()
    await expect.poll(async () => (await inspect(application)).dropped).toBe(true)
    const lost = await inspect(application)
    expect(lost.targetOrdinalAtDrop).toBe(1)
    expect(lost.commitCalls).toBe(0)
    expect(lost.executeCalls).toBe(1)
    expect(lost.lostAckCalls).toBe(0)
    if (!lost.envelope || !lost.request) throw new Error('First real execute envelope missing')
    const first = data(lost.envelope.payload as BridgeResult<QueryExecutionReceiptDTO>)
    const operationId = first.operationId
    expect(operationId).toMatch(uuid)
    const original = first.acceptedJob
    expect(lost.request).toEqual({
      operationId,
      loadRef: expect.stringMatching(uuid),
      visibleDraft,
      selection: { kind: 'current' },
    })
    expect(original).toMatchObject({
      projectId: initial.projectId,
      operationId,
      capability: 'query.execute',
      inputSnapshotId: initial.inputSnapshotId,
      confirmationRef: null,
    })
    const pending = workspace.locator('p').filter({ hasText: '保留原 execute 操作：' })
    await expect(pending.locator('code')).toHaveText(operationId)
    const retry = workspace.getByRole('button', { name: '以原 intent 重取受理', exact: true })
    await expect(retry).toBeEnabled()
    await expect(workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
      sparql,
    )
    // No tab, project, generation, loadRef, session or operation change occurs.
    // Existing service e.accepted is reused; this is a second IPC, not a new Job.
    stage = 'same-view existing retry returns original accepted receipt'
    await retry.click()
    const task = workspace.getByRole('region', { name: '真实查询或提交任务', exact: true })
    await expect(task.locator('code')).toHaveText(original.jobId)
    await expect(pending).toHaveCount(0)
    const retried = await inspect(application)
    expect(retried.executeCalls).toBe(2)
    expect(retried.commitCalls).toBe(0)
    expect(retried.targetRequests).toEqual([lost.request, lost.request])
    expect(retried.sameSenderFrame).toEqual([true, true])
    expect(retried.targetReplies).toHaveLength(2)
    const secondEnvelope = retried.targetReplies[1] as Envelope
    expect(secondEnvelope.deliveryVersion).toBe(1)
    expect(secondEnvelope.deliveryId).toMatch(uuid)
    expect(secondEnvelope.deliveryId).not.toBe(lost.envelope.deliveryId)
    const second = data(secondEnvelope.payload as BridgeResult<QueryExecutionReceiptDTO>)
    expect(second.operationId).toBe(operationId)
    expect(second.acceptedJob).toEqual(original)
    expect(retried.lostAckCalls).toBe(0)
    const viewAfterRetry = data(await page.evaluate(() => window.ontolearn!.restoreTasks()))
    expect(viewAfterRetry.generation).toBe(viewBefore.generation)
    expect(viewAfterRetry.project).toEqual(viewBefore.project)
    stage = 'UI refreshes original Job and fixed result without another execute'
    const refresh = task.getByRole('button', { name: '刷新任务、原操作与固定结果', exact: true })
    let reads = 0
    await expect
      .poll(async () => {
        if (++reads > 12) throw new Error('Bounded original-Job UI refresh exhausted')
        await expect(refresh).toBeEnabled()
        await refresh.click()
        await expect(refresh).toBeEnabled()
        return (await task.textContent())?.includes('：succeeded；') ?? false
      })
      .toBe(true)
    await expect(notice).toHaveText('已取得真实结果描述；按固定引用分别读取文本与结果页。')
    const lane = workspace.getByRole('region', { name: '本次执行结果', exact: true })
    const result = lane.getByRole('region', { name: '查询结果', exact: true })
    await expect(result).toContainText('完整结果共 1 行')
    await lane.getByRole('button', { name: '读取 SELECT 结果第一页', exact: true }).click()
    const table = result.getByRole('table')
    await expect(table.getByRole('columnheader')).toHaveText(['alarm'])
    await expect(table.locator('tbody tr')).toHaveCount(1)
    await expect(table.locator('tbody td > span')).toHaveText(['urn:ontolearn:learning:alarm/A01'])
    await table.getByText('RDF 原文', { exact: true }).click()
    await expect(table.locator('tbody code')).toHaveText('<urn:ontolearn:learning:alarm/A01>')
    await expect(
      lane.getByRole('button', { name: '读取 SELECT 结果第一页', exact: true }),
    ).toBeEnabled()
    await lane.getByRole('button', { name: '读取执行文本第一页', exact: true }).click()
    await result.getByText('本次实际执行的 SPARQL', { exact: true }).click()
    await expect(result.locator('pre')).toHaveText(sparql)
    await expect(
      lane.getByRole('button', { name: '读取执行文本第一页', exact: true }),
    ).toBeEnabled()
    const job = data(await page.evaluate((id) => window.ontolearn!.getJob(id), original.jobId))
    expect(job).toMatchObject({
      projectId: initial.projectId,
      operationId,
      jobId: original.jobId,
      capability: 'query.execute',
      state: 'succeeded',
      error: null,
      inputSnapshotId: initial.inputSnapshotId,
      confirmationRef: null,
    })
    for (const field of [
      'input',
      'parametersHash',
      'implementation',
      'limits',
      'scope',
      'createdAtMs',
      'dependencyVector',
      'definitionSetDigests',
      'confirmationRef',
    ] as const)
      expect(job[field]).toEqual(original[field])
    expect(job.stateVersion).toBeGreaterThanOrEqual(original.stateVersion)
    expect(job.resultRef).toEqual({
      resultId: expect.stringMatching(uuid),
      inputSnapshotId: initial.inputSnapshotId,
    })
    expect(job.commitProgress).toEqual({ mode: 'none' })
    // Null is the query's no-domain-marker shape, not proof of a negative ACK.
    expect(
      data(await page.evaluate((id) => window.ontolearn!.getOperation(id), operationId)),
    ).toBeNull()
    const inventory = await allJobs(page, initial.projectId)
    expect(inventory).toEqual([job])
    const after = await read(page)
    expect(after.domain).toEqual(initial.domain)
    expect(after.inputSnapshotId).toBe(initial.inputSnapshotId)
    const final = await inspect(application)
    expect(final.executeCalls).toBe(2)
    expect(final.commitCalls).toBe(0)
    expect(final.targetRequests).toEqual([lost.request, lost.request])
    expect(final.lostAckCalls).toBe(0)
    evidence.initial = initial
    evidence.firstDroppedDelivery = lost
    evidence.sameIntentRetry = retried
    evidence.viewBefore = viewBefore
    evidence.viewAfterRetry = viewAfterRetry
    evidence.job = job
    evidence.after = after
    evidence.allStateInventory = inventory
    evidence.final = final
    stage = 'completed'
  } finally {
    try {
      if (instrumented) await removeFault(application)
    } finally {
      try {
        await test.info().attach('query-first-consumer-ack-loss', {
          body: JSON.stringify({ stage, ...evidence }, null, 2),
          contentType: 'application/json',
        })
      } finally {
        await application.close()
      }
    }
  }
})
