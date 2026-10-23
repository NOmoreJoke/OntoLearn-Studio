import { test, expect, type Page } from '@playwright/test'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'
import type { BridgeResult, MainlineProjectReadDTO } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'

type DigestObservation = {
  algorithm: string
  preimage: string
  byteLength: number
}
type DigestGateSnapshot = {
  waiting: boolean
  released: boolean
  settled: boolean
  calls: DigestObservation[]
}
type DraftDigestGate = {
  snapshot(): DigestGateSnapshot
  release(): Promise<void>
  restore(): void
}

declare global {
  interface Window {
    __t01QueryDraftDigestGate?: DraftDigestGate
  }
}

const editor = 'query-workspace-v1'
const definitionId = 'cross_project_unfinished_draft'
const description = '仅属于项目 A：等待摘要时切换项目，不能写入项目 B。'
const sparql = 'SELECT ?unfinished WHERE {\n  # 这是未完成的工作草稿，不是正式定义\n'
// Independent literal, sorted ASCII keys. Preserve the unfinished text verbatim.
const expectedContentJson = JSON.stringify({
  definitionId,
  draft: {
    capabilityQuestion: '',
    description,
    name: '',
    scope: 'asserted',
    source: 'editor',
    sparql,
  },
  version: 1,
})
const expectedContentHash = createHash('sha256').update(expectedContentJson, 'utf8').digest('hex')

function data<T>(response: BridgeResult<T>): T {
  if (!response.ok) throw new Error(`Real named read refused: ${JSON.stringify(response.error)}`)
  return response.data
}

async function attach(name: string, value: unknown) {
  await test.info().attach(name, {
    body: JSON.stringify(value, null, 2),
    contentType: 'application/json',
  })
}

const queryPane = (page: Page) => page.getByRole('region', { name: '当前项目查询', exact: true })

async function readSelected(page: Page): Promise<MainlineProjectReadDTO> {
  // Read-only evidence through the original named bridge. No bridge write here.
  return data(
    await page.evaluate(() => {
      const bridge = window.ontolearn
      if (!bridge) throw new Error('Real preload bridge is absent')
      return bridge.readProject({ editor: 'query-workspace-v1' })
    }),
  )
}

function expectMissingBlank(value: MainlineProjectReadDTO) {
  expect(value.domain.projectRevision).toBe(0)
  expect(value.workspace.domainRevision).toBe(0)
  expect(value.workspace.draft).toEqual({ editor, state: 'missing' })
  expect(value.domain.state).toEqual({ definitions: [], facts: [], mappingState: {} })
}

async function createBlankThroughUi(page: Page, name: string) {
  const library = page.getByTestId('project-library')
  await page.getByTestId('project-name').fill(name)
  await page.getByTestId('project-create').click()
  // The distinct new list item also excludes an old same-text completion notice.
  await expect(library.locator('li').filter({ hasText: name })).toHaveCount(1)
  await expect(library.getByRole('status')).toContainText('项目已创建并打开')
  await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
  await expect(page.getByTestId('selected-project-version')).toContainText('版本 0')
}

async function readWorkspaceThroughUi(page: Page) {
  const pane = queryPane(page)
  await pane.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
  await expect(
    pane.getByText('项目与持久工作草稿已读回；工作草稿不代表正式查询定义。', { exact: true }),
  ).toBeVisible()
  await expect(pane).toContainText('工作草稿代际 0')
}

async function openThroughUi(page: Page, projectId: string) {
  await page.locator(`[data-testid="project-open"][data-project-id="${projectId}"]`).click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText('项目已打开')
  await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
  // The selected controller itself must have changed; a stale notice is insufficient.
  await expect(queryPane(page)).toContainText(projectId)
}

async function installFirstDigestGate(page: Page) {
  await page.evaluate(() => {
    if ('__t01QueryDraftDigestGate' in window) throw new Error('Digest gate already exists')
    const subtle = window.crypto.subtle
    const original = subtle.digest
    const ownDescriptor = Object.getOwnPropertyDescriptor(subtle, 'digest')
    const calls: DigestObservation[] = []
    let waiting = false
    let released = false
    let settled = false
    let releaseWait: (() => void) | undefined
    let first: Promise<ArrayBuffer> | undefined
    const waitForRelease = new Promise<void>((resolveWait) => {
      releaseWait = resolveWait
    })
    const instrumented: SubtleCrypto['digest'] = (algorithm, input) => {
      const bytes =
        input instanceof ArrayBuffer
          ? new Uint8Array(input)
          : new Uint8Array(input.buffer, input.byteOffset, input.byteLength)
      calls.push({
        algorithm: typeof algorithm === 'string' ? algorithm : algorithm.name,
        byteLength: bytes.byteLength,
        preimage: new TextDecoder('utf-8').decode(bytes),
      })
      if (calls.length !== 1) return original.call(subtle, algorithm, input)
      waiting = true
      // The original algorithm, BufferSource object, receiver and native implementation
      // are retained. Only scheduling of the first call changes; no synthetic digest.
      first = waitForRelease
        .then(() => original.call(subtle, algorithm, input))
        .finally(() => {
          settled = true
        })
      return first
    }
    Object.defineProperty(subtle, 'digest', {
      configurable: true,
      writable: true,
      value: instrumented,
    })
    window.__t01QueryDraftDigestGate = {
      snapshot: () => ({
        waiting,
        released,
        settled,
        calls: calls.map((call) => ({ ...call })),
      }),
      release: async () => {
        if (!waiting || !first || !releaseWait) throw new Error('No actual digest is pending')
        if (released) throw new Error('Original digest already released')
        released = true
        releaseWait()
        await first
      },
      restore: () => {
        // Restore instrumentation only. Never replay a suspended save during cleanup.
        if (ownDescriptor) Object.defineProperty(subtle, 'digest', ownDescriptor)
        else Reflect.deleteProperty(subtle, 'digest')
        delete window.__t01QueryDraftDigestGate
      },
    }
  })
}

async function digestSnapshot(page: Page) {
  return page.evaluate(() => {
    const gate = window.__t01QueryDraftDigestGate
    if (!gate) throw new Error('Digest gate is absent')
    return gate.snapshot()
  })
}

test('hash-pending A draft cannot cross into B; original operation retries only in retained A', async () => {
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
  let page: Page | undefined
  try {
    page = await application.firstWindow()
    await createBlankThroughUi(page, '摘要切换边界项目 A')
    await readWorkspaceThroughUi(page)
    const aBefore = await readSelected(page)
    expectMissingBlank(aBefore)

    const aPane = queryPane(page)
    await aPane.getByLabel('项目内查询标识', { exact: true }).fill(definitionId)
    await aPane.getByLabel('说明', { exact: true }).fill(description)
    await aPane.getByLabel('可见 SPARQL', { exact: true }).fill(sparql)
    await expect(aPane.getByLabel('名称', { exact: true })).toHaveValue('')
    await installFirstDigestGate(page)
    await aPane.getByRole('button', { name: '保存工作草稿（不提交正式定义）', exact: true }).click()
    await page.waitForFunction(() => window.__t01QueryDraftDigestGate?.snapshot().waiting === true)
    const pending = aPane.locator('p').filter({ hasText: '保留原 draft 操作：' })
    await expect(pending).toHaveCount(1)
    const operationId = (await pending.locator('code').innerText()).trim()
    expect(operationId).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/,
    )
    const held = await digestSnapshot(page)
    expect(held).toEqual({
      waiting: true,
      released: false,
      settled: false,
      calls: [
        {
          algorithm: 'SHA-256',
          preimage: expectedContentJson,
          byteLength: Buffer.byteLength(expectedContentJson, 'utf8'),
        },
      ],
    })
    await attach('01-A-before-first-write-hash-pending', { aBefore, operationId, held })

    // Create/open B through App while the original A digest is still suspended.
    // Both projects have revision 0 and a missing generation-0 draft, so the old
    // continuation would satisfy B's CAS instead of being harmlessly rejected.
    await createBlankThroughUi(page, '摘要切换边界项目 B')
    await readWorkspaceThroughUi(page)
    const bBefore = await readSelected(page)
    expect(bBefore.projectId).not.toBe(aBefore.projectId)
    expectMissingBlank(bBefore)
    expect((await digestSnapshot(page)).released).toBe(false)
    await attach('02-B-selected-before-release', bBefore)

    await page.evaluate(async () => {
      const gate = window.__t01QueryDraftDigestGate
      if (!gate) throw new Error('Digest gate is absent')
      await gate.release()
      // Let the original awaiting controller continuation run before the read probe.
      await new Promise<void>((resolveTurn) => setTimeout(resolveTurn, 0))
    })
    const bAfterRelease = await readSelected(page)
    await attach('03-B-after-original-A-digest', { bBefore, bAfterRelease })
    expect(bAfterRelease).toEqual(bBefore)
    expectMissingBlank(bAfterRelease)
    await expect(queryPane(page).getByLabel('说明', { exact: true })).toHaveValue('')
    await expect(queryPane(page).getByLabel('可见 SPARQL', { exact: true })).toHaveValue('')

    // Retained A controller, not a newly loaded controller or a reconstructed request.
    await openThroughUi(page, aBefore.projectId)
    const retainedA = queryPane(page)
    await expect(retainedA.getByLabel('项目内查询标识', { exact: true })).toHaveValue(definitionId)
    await expect(retainedA.getByRole('textbox', { name: '说明', exact: true })).toHaveValue(
      description,
    )
    await expect(retainedA.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
      sparql,
    )
    await expect(retainedA.getByLabel('名称', { exact: true })).toHaveValue('')
    await expect(
      retainedA.locator('p').filter({ hasText: '保留原 draft 操作：' }).locator('code'),
    ).toHaveText(operationId)
    const retry = retainedA.getByRole('button', {
      name: '以原 operation 和原参数重试草稿保存',
      exact: true,
    })
    await expect(retry).toBeEnabled()
    const aBeforeRetry = await readSelected(page)
    await attach('04-retained-A-before-explicit-original-operation-retry', aBeforeRetry)
    expect(aBeforeRetry).toEqual(aBefore)
    expectMissingBlank(aBeforeRetry)

    await retry.click()
    await expect(
      retainedA.getByText('工作草稿已持久化；正式定义尚未提交。', { exact: true }),
    ).toBeVisible()
    const receipt = retainedA.locator('p').filter({ hasText: '工作草稿持久回执：operation' })
    await expect(receipt.locator('code')).toHaveText(operationId)
    await expect(receipt).toContainText('generation 1')
    const aAfter = await readSelected(page)
    expect(aAfter.projectId).toBe(aBefore.projectId)
    expect(aAfter.domain).toEqual(aBefore.domain)
    expect(aAfter.workspace.operationSequence).toBe(aBefore.workspace.operationSequence + 1)
    expect(aAfter.workspace.checkpointRef).not.toBe(aBefore.workspace.checkpointRef)
    expect(aAfter.workspace.draft).toEqual({
      editor,
      state: 'present',
      generation: 1,
      present: true,
      boundDomainRevision: 0,
      contentHash: expectedContentHash,
      contentJson: expectedContentJson,
    })
    // A second actual read is inert; no extra UI save/new operation is generated.
    expect(await readSelected(page)).toEqual(aAfter)
    expect(aAfter.domain.state.definitions).toEqual([])

    const receiptUi = await receipt.innerText()
    await openThroughUi(page, bBefore.projectId)
    const bFinal = await readSelected(page)
    expect(bFinal).toEqual(bBefore)
    expectMissingBlank(bFinal)
    const digest = await digestSnapshot(page)
    expect(digest.settled).toBe(true)
    expect(digest.calls).toEqual([held.calls[0], held.calls[0]])
    await attach('05-original-operation-persisted-once-only-in-A', {
      operationId,
      receiptUi,
      aAfter,
      bFinal,
      digest,
      limits: 'UI writes only; named read probes; no raw IPC request-count claim',
    })
  } finally {
    try {
      if (page && !page.isClosed()) {
        await page.evaluate(() => window.__t01QueryDraftDigestGate?.restore())
      }
    } finally {
      await application.close()
    }
  }
})
