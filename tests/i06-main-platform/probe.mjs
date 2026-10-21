import assert from 'node:assert/strict'
import { execFileSync, spawn } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { copyFileSync, mkdirSync, readdirSync, writeFileSync } from 'node:fs'
import { mkdir, readFile, writeFile, readdir, chmod, stat } from 'node:fs/promises'
import https from 'node:https'
import path from 'node:path'
import { expect } from '@playwright/test'
import { launchActualElectron } from './electron-driver.mjs'

const root = '/workspace'
const output = '/probe-data/main-platform'
const secret = 'I06_MAIN_SYNTHETIC_SECRET_' + randomUUID()
const responseMarker = 'I06_RESPONSE_PRIVATE_MARKER_' + randomUUID()
const responseText = `<script>window.I06_BAD_EXECUTION=true</script> ${responseMarker}`
assert.notEqual(
  process.env.NODE_TLS_REJECT_UNAUTHORIZED,
  '0',
  'TLS_VERIFICATION_MUST_REMAIN_ENABLED',
)
const cases = []
const received = []
const applications = new Map()
const sockets = new Set()
let hold = false
let requestError = false
let nextReceiverId = 0
const server = https.createServer(
  {
    key: await readFile('/probe-data/certificates/server.key'),
    cert: await readFile('/probe-data/certificates/server.pem'),
  },
  async (request, response) => {
    const chunks = []
    for await (const chunk of request) chunks.push(chunk)
    const body = Buffer.concat(chunks)
    // Headers are checked in memory only, never written to any artifact.
    if (request.headers.authorization !== 'Bearer ' + secret || request.method !== 'POST')
      requestError = true
    const index = nextReceiverId++
    await writeFile(path.join(output, `receiver-${index}.body`), body)
    const record = {
      index,
      path: request.url,
      byteCount: body.length,
      sha256: createHash('sha256').update(body).digest('hex'),
      body,
      response,
    }
    received.push(record)
    response.setHeader('Content-Type', 'text/plain; charset=utf-8')
    if (!hold) response.end(responseText)
  },
)
server.on('connection', (socket) => {
  sockets.add(socket)
  socket.on('close', () => sockets.delete(socket))
})
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
const endpoint = `https://127.0.0.1:${server.address().port}/v1/chat/completions`
const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds))
async function until(check, code, timeout = 15000) {
  const deadline = Date.now() + timeout
  do {
    const result = await check()
    if (result) return result
    await wait(40)
  } while (Date.now() < deadline)
  throw new Error(code)
}
async function saveCase(name, details = {}) {
  cases.push({ name, result: 'passed', ...details })
  await writeFile(path.join(output, 'cases.json'), JSON.stringify(cases, null, 2) + '\n')
}
function checkPublicBodies(expectedResultId) {
  for (const record of received) {
    const body = record.body.toString('utf8')
    for (const marker of [
      'PRIVATE_VALUE_SENTINEL',
      'PRIVATE_DERIVED_SENTINEL',
      'PRIVATE_LABEL_SENTINEL',
      'PRIVATE_DERIVED_LABEL_SENTINEL',
      'I06_FINITE_FIELDS',
      secret,
      '854736291',
    ])
      assert.equal(body.includes(marker), false, 'UNSELECTED_BYTES_EGRESS')
    const request = JSON.parse(body)
    assert.deepEqual(Object.keys(request).sort(), ['model', 'parts'])
    assert.equal(request.model, 'synthetic-model')
    assert.equal(request.parts.length, 1)
    assert.deepEqual(Object.keys(request.parts[0]).sort(), ['kind', 'text'])
    assert.equal(request.parts[0].kind, 'selected')
    const projection = JSON.parse(request.parts[0].text)
    assert.deepEqual(Object.keys(projection).sort(), ['fields', 'rows', 'source'])
    assert.deepEqual(projection.fields, [
      { key: 'public', label: 'Public label', type: 'string', nullable: false },
    ])
    assert.deepEqual(
      projection.rows,
      [0, 1, 2].map((ordinal) => ({ ordinal, cells: [`PUBLIC_VALUE_${ordinal}`] })),
    )
    assert.equal(projection.source.resultId, expectedResultId)
    assert.equal(projection.source.selection, 'current')
    assert.equal(projection.source.modelId, 'i06-finite-probe')
    assert.equal(projection.source.modelVersion, 'v1')
    assert.deepEqual(Object.keys(projection.source).sort(), [
      'jobId',
      'modelId',
      'modelVersion',
      'projectId',
      'resultId',
      'selection',
      'stateAtRead',
      'stateMeaning',
    ])
  }
}
async function bridge(page, method, params = {}) {
  return page.evaluate(async ({ method, params }) => window.ontolearn[method](params), {
    method,
    params,
  })
}
async function data(page, method, params = {}) {
  const result = await bridge(page, method, params)
  if (!result.ok) throw new Error('BRIDGE_REJECTED_' + method + '_' + result.error.code)
  assert.equal(JSON.stringify(result).includes(secret), false, 'SECRET_RETURNED')
  return result.data
}
async function status(page) {
  return data(page, 'getModelAccessStatus')
}
async function launch(
  name,
  fixture,
  profile = name,
  backend = 'gnome-libsecret',
  environment = {},
) {
  const userData = path.join('/probe-data/profiles', profile)
  await mkdir(userData, { recursive: true, mode: 0o700 })
  const env = { ...process.env, ...environment }
  delete env.ELECTRON_RUN_AS_NODE
  if (fixture) env.I04_TEST_FIXTURE = fixture
  else delete env.I04_TEST_FIXTURE
  const productLogs = []
  const application = await launchActualElectron({
    args: [
      path.join(root, 'apps/desktop'),
      `--password-store=${backend}`,
      `--user-data-dir=${userData}`,
      ...(fixture ? [`--i04-test-fixture=${fixture}`] : []),
    ],
    cwd: path.join(root, 'apps/desktop'),
    env,
    onLog: (bytes) => productLogs.push(Buffer.from(bytes)),
  }).catch(async (error) => {
    await writeFile(path.join(output, name + '.product.log'), Buffer.concat(productLogs))
    throw error
  })
  const rendererLogs = []
  const close = async () => {
    try {
      await application.close()
    } finally {
      applications.delete(application)
      await writeFile(path.join(output, name + '.product.log'), Buffer.concat(productLogs))
      await writeFile(path.join(output, name + '.renderer.log'), rendererLogs.join('\n'))
    }
  }
  applications.set(application, close)
  const page = await application.firstWindow()
  page.on('console', (message) => rendererLogs.push(message.text()))
  const runtime = await application.evaluate(({ app, safeStorage, BrowserWindow }) => {
    const preferences = BrowserWindow.getAllWindows()[0].webContents.getLastWebPreferences()
    const encryptionAvailable = safeStorage.isEncryptionAvailable()
    const backend = safeStorage.getSelectedStorageBackend()
    const fs = process.getBuiltinModule('fs')
    const mainPid = process.pid
    const rendererPid = BrowserWindow.getAllWindows()[0].webContents.getOSProcessId()
    const proc = (pid) => {
      const raw = fs.readFileSync(`/proc/${pid}/status`, 'utf8')
      const names = [
        'Uid',
        'Gid',
        'NSpid',
        'NoNewPrivs',
        'Seccomp',
        'Seccomp_filters',
        'CapEff',
        'CapBnd',
      ]
      return Object.fromEntries(
        raw
          .split('\n')
          .map((line) => line.split(/:\s*/))
          .filter(([name]) => names.includes(name)),
      )
    }
    return {
      electron: process.versions.electron,
      node: process.versions.node,
      type: process.type,
      ready: app.isReady(),
      packaged: app.isPackaged,
      appPath: app.getAppPath(),
      userData: app.getPath('userData'),
      backend,
      encryptionAvailable,
      passwordStoreSwitch: app.commandLine.getSwitchValue('password-store'),
      mockKeychainSwitch: app.commandLine.hasSwitch('use-mock-keychain'),
      disabledHangMonitorSwitch: app.commandLine.hasSwitch('disable-hang-monitor'),
      noSandboxSwitch: app.commandLine.hasSwitch('no-sandbox'),
      argv: process.argv,
      execArgv: process.execArgv,
      uid: process.getuid(),
      mainPid,
      rendererPid,
      mainProc: proc(mainPid),
      rendererProc: proc(rendererPid),
      preferences: {
        sandbox: preferences.sandbox,
        contextIsolation: preferences.contextIsolation,
        nodeIntegration: preferences.nodeIntegration,
      },
    }
  })
  assert.equal(runtime.electron, '44.9.0')
  assert.equal(runtime.type, 'browser')
  assert.equal(runtime.ready, true)
  assert.equal(runtime.userData, userData)
  assert.equal(runtime.mockKeychainSwitch, false)
  assert.equal(runtime.disabledHangMonitorSwitch, false)
  assert.equal(runtime.passwordStoreSwitch, backend)
  assert.equal(runtime.noSandboxSwitch, false)
  assert.equal(runtime.uid, 1106)
  assert.equal(runtime.rendererProc.NoNewPrivs, '1')
  assert.equal(runtime.rendererProc.Seccomp, '2')
  assert.equal(
    Number(runtime.rendererProc.Seccomp_filters) > Number(runtime.mainProc.Seccomp_filters),
    true,
    'RENDERER_REQUIRES_OWN_SECCOMP_FILTER',
  )
  await writeFile(
    path.join(output, name + '-runtime.json'),
    JSON.stringify(runtime, null, 2) + '\n',
  )
  await expect(page.getByRole('heading', { name: '解释选中的结果' })).toBeVisible()
  // Project restoration replaces the no-project panel. Wait for that actual UI commit.
  if (fixture) await expect(page.getByRole('region', { name: '后台任务状态' })).toBeVisible()
  return {
    application,
    page,
    userData,
    runtime,
    close,
  }
}
function prepare(name, mode) {
  const directory = path.join('/probe-data/fixtures', name)
  try {
    execFileSync(
      path.join(root, '.venv/bin/python'),
      ['-I', path.join(root, 'tests/i06-main-platform/fixture.py'), directory, mode],
      { cwd: root, timeout: 40000, stdio: ['ignore', 'ignore', 'pipe'] },
    )
  } catch (error) {
    writeFileSync(path.join(output, name + '.prepare.log'), error.stderr ?? String(error))
    throw error
  }
  const capture = path.join(output, 'fixture-captures', name)
  mkdirSync(capture, { recursive: true })
  for (const file of readdirSync(directory).filter(
    (name) => name.endsWith('.json') || name.endsWith('.log'),
  ))
    copyFileSync(path.join(directory, file), path.join(capture, file))
  return directory
}
async function configureUI(page) {
  await page.getByText('模型接收配置与凭据', { exact: true }).click()
  await page.locator('input[name="displayName"]').fill('I06 synthetic receiver')
  await page.locator('input[name="endpoint"]').fill(endpoint)
  await page.locator('input[name="model"]').fill('synthetic-model')
  await page.getByRole('button', { name: '保存配置', exact: true }).click()
  await until(async () => (await status(page)).configurations.length === 1, 'CONFIGURE_FAILED')
  await page.getByLabel('API 凭据', { exact: true }).fill(secret)
  await page.getByRole('button', { name: '安全保存凭据', exact: true }).click()
  await until(
    async () => (await status(page)).configurations[0]?.credentialState === 'configured',
    'CREDENTIAL_STORE_FAILED',
  )
  assert.equal(await page.getByLabel('API 凭据', { exact: true }).inputValue(), '')
  assert.equal((await page.locator('body').textContent()).includes(secret), false)
  return (await status(page)).configurations[0]
}
async function selectPublicUI(page, resultId) {
  const choice = page.locator('.model-result-choice').filter({ hasText: resultId })
  await choice.getByRole('button', { name: '读取可选字段', exact: true }).click()
  await expect(page.getByRole('group', { name: '有限字段目录' })).toBeVisible()
  const checkbox = page.getByRole('checkbox', { name: 'Public label · string', exact: true })
  await expect(checkbox).not.toBeChecked()
  await checkbox.check()
  await page.getByRole('button', { name: '选中这些字段', exact: true }).click()
  await until(
    async () => (await status(page)).selections[0]?.metadata.resultId === resultId,
    'PUBLIC_SELECTION_FAILED',
  )
  const selection = (await status(page)).selections[0]
  assert.equal(selection.kind, 'fields')
  assert.equal(selection.fields.length, 1)
  assert.equal(selection.fields[0].label, 'Public label')
  return selection
}
async function previewUI(page, reusable = false) {
  await page.getByRole('button', { name: '预览外发范围', exact: true }).click()
  const preview = page.getByLabel('模型外发授权预览', { exact: true })
  await expect(preview).toBeVisible()
  await expect(preview).toContainText(endpoint)
  await expect(preview).toContainText('Public label')
  if (reusable)
    await expect(
      preview.getByRole('button', { name: '发送解释请求（复用已有授权）', exact: true }),
    ).toBeVisible()
  else await preview.getByRole('button', { name: '明确授权上述范围', exact: true }).click()
  await expect(preview.getByRole('button', { name: /^发送解释请求/ })).toBeEnabled()
  return preview
}
async function captureSelection(page, name) {
  const current = await status(page)
  const selection = current.selections[0]
  const sourceMetadata = await data(page, 'getResult', selection.metadata.resultId)
  const sourcePage = await data(page, 'getResultPage', {
    resultId: selection.metadata.resultId,
    pageSize: 200,
    cursor: null,
  })
  const authorization = await data(page, 'previewModelExplanation', {
    contextId: current.contextId,
    configurationId: current.configurations[0].configurationId,
    selectionIds: [selection.selectionId],
  })
  assert.equal(authorization.authorization.state, 'reusable')
  await writeFile(
    path.join(output, name + '.json'),
    JSON.stringify({ sourceMetadata, sourcePage, selected: selection, authorization }, null, 2) +
      '\n',
  )
  return { selection, grantId: authorization.authorization.grantId }
}
async function invocation(page, id) {
  const state = await status(page)
  return data(page, 'getModelExplanationOutcome', { contextId: state.contextId, invocationId: id })
}
async function expectDenied(page, method, params, codes) {
  const result = await bridge(page, method, params)
  if (method === 'startModelExplanation' && result.ok) {
    const outcome = await until(async () => {
      const value = await invocation(page, result.data.invocationId)
      return value.state === 'failed' || value.state === 'completed' || value.state === 'cancelled'
        ? value
        : false
    }, 'EXPECTED_ASYNC_DENIAL')
    assert.equal(outcome.state, 'failed')
    assert.ok(codes.includes(outcome.error.code), 'UNEXPECTED_ASYNC_FIXED_ERROR')
    return outcome.error
  }
  assert.equal(result.ok, false)
  assert.ok(codes.includes(result.error.code), 'UNEXPECTED_FIXED_ERROR')
  return result.error
}

async function checkProfileLock(app, fixture) {
  const before = await status(app.page)
  const windows = await app.application.evaluate(({ BrowserWindow }) =>
    BrowserWindow.getAllWindows().map((window) => window.id),
  )
  const count = received.length
  const child = spawn(
    '/workspace/node_modules/electron/dist/electron',
    [
      '/workspace/apps/desktop',
      '--password-store=gnome-libsecret',
      `--user-data-dir=${app.userData}`,
      `--i04-test-fixture=${fixture}`,
    ],
    {
      cwd: '/workspace/apps/desktop',
      env: { ...process.env, I04_TEST_FIXTURE: fixture },
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  )
  const logs = []
  child.stdout.on('data', (bytes) => logs.push(Buffer.from(bytes)))
  child.stderr.on('data', (bytes) => logs.push(Buffer.from(bytes)))
  const exit = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      child.kill('SIGTERM')
      reject(new Error('SECOND_PROFILE_INSTANCE_DID_NOT_EXIT'))
    }, 10000)
    child.once('error', (error) => {
      clearTimeout(timer)
      reject(error)
    })
    child.once('close', (code, signal) => {
      clearTimeout(timer)
      resolve({ code, signal })
    })
  })
  await writeFile(path.join(output, 'second-same-profile.product.log'), Buffer.concat(logs))
  assert.equal(exit.code, 0)
  assert.equal(exit.signal, null)
  assert.deepEqual(await status(app.page), before)
  assert.deepEqual(
    await app.application.evaluate(({ BrowserWindow }) =>
      BrowserWindow.getAllWindows().map((window) => window.id),
    ),
    windows,
  )
  assert.equal(received.length, count)
  await saveCase(
    'actual-second-same-profile-process-exits-original-window-ledger-receiver-unchanged',
  )
}

try {
  const noProject = await launch('no-project')
  await until(
    async () => (await status(noProject.page)).availability === 'unavailable',
    'NO_PROJECT_STATUS',
  )
  const empty = await status(noProject.page)
  assert.equal(empty.contextId, null)
  assert.equal(empty.projectId, null)
  assert.equal(empty.privacy, 'local')
  await expect(noProject.page.getByLabel('项目模型隐私模式', { exact: true })).toBeDisabled()
  assert.equal(received.length, 0)
  await noProject.close()
  await saveCase('default-local-no-project-disabled')

  const fixture = prepare('fields', 'fields')
  const evidence = JSON.parse(await readFile(path.join(fixture, 'fixture-evidence.json'), 'utf8'))
  const firstResult = evidence.firstJob.resultRef.resultId
  let app = await launch('settings', path.join(fixture, 'fixture.json'), 'secure')
  await until(async () => (await status(app.page)).availability === 'ready', 'PROJECT_READY')
  assert.equal(app.runtime.backend, 'gnome_libsecret')
  assert.equal(app.runtime.encryptionAvailable, true)
  const configuration = await configureUI(app.page)
  await expect(app.page.getByRole('button', { name: '预览外发范围', exact: true })).toBeDisabled()
  assert.equal(received.length, 0)
  await app.close()
  await saveCase('explicit-settings-actual-libsecret-no-secret-readback', {
    backend: 'gnome_libsecret',
  })

  app = await launch('restored-field-rounds', path.join(fixture, 'second-fixture.json'), 'secure')
  await until(async () => (await status(app.page)).availability === 'ready', 'RESTORE_READY')
  let current = await status(app.page)
  assert.equal(current.configurations[0].configurationId, configuration.configurationId)
  assert.equal(current.configurations[0].credentialState, 'configured')
  assert.equal(current.privacy, 'local')
  assert.equal(current.invocations.length, 0)
  await app.page.getByLabel('项目模型隐私模式', { exact: true }).selectOption('minimal')
  await selectPublicUI(app.page, firstResult)
  await previewUI(app.page)
  const firstFieldProof = await captureSelection(app.page, 'a03-first-selected-and-source')
  assert.equal(
    (await data(app.page, 'restoreTasks')).jobs.some(
      (job) => job.jobId !== evidence.firstJob.jobId && job.state === 'succeeded',
    ),
    false,
    'SECOND_WORKER_COMPLETED_BEFORE_FIRST_AUTHORIZATION',
  )
  await saveCase('first-real-worker-public-field-authorized-before-second-completes')
  const children = JSON.parse(
    execFileSync(
      '/workspace/.venv/bin/python',
      [
        '-I',
        '/workspace/tests/i06-main-platform/process-environment.py',
        String(app.application.process().pid),
      ],
      { encoding: 'utf8' },
    ),
  )
  assert.deepEqual(children.map((child) => child.role).sort(), ['coordinator', 'worker'])
  assert.equal(
    children.every(
      (child) =>
        child.pythonIsOwnVenv &&
        child.secretPrefixAbsent &&
        child.nodeExtraCAAbsent &&
        child.proxyVariablesAbsent,
    ),
    true,
  )
  await writeFile(
    path.join(output, 'actual-engine-worker-environments.json'),
    JSON.stringify(children, null, 2) + '\n',
  )
  await saveCase('actual-running-coordinator-and-worker-environments-exclude-key-ca-proxy')
  const secondJob = await until(
    async () => {
      const view = await data(app.page, 'restoreTasks')
      return view.jobs.find(
        (job) => job.jobId !== evidence.firstJob.jobId && job.state === 'succeeded',
      )
    },
    'SECOND_REAL_WORKER_FAILED',
    25000,
  )
  await app.page.getByRole('button', { name: '刷新任务状态', exact: true }).click()
  await selectPublicUI(app.page, secondJob.resultRef.resultId)
  const reusable = await previewUI(app.page, true)
  const secondFieldProof = await captureSelection(app.page, 'a03-second-selected-and-source')
  assert.equal(secondFieldProof.grantId, firstFieldProof.grantId)
  assert.notEqual(secondFieldProof.selection.catalogId, firstFieldProof.selection.catalogId)
  assert.notEqual(
    secondFieldProof.selection.metadata.resultId,
    firstFieldProof.selection.metadata.resultId,
  )
  assert.equal(received.length, 0)
  await reusable.getByRole('button', { name: '发送解释请求（复用已有授权）', exact: true }).click()
  await until(() => received.length === 1, 'FIRST_HTTPS_POST')
  current = await status(app.page)
  const firstInvocation = current.invocations[0].invocationId
  await until(
    async () => (await invocation(app.page, firstInvocation)).state === 'completed',
    'COMPLETE_RESPONSE',
  )
  await expect(app.page.locator('.model-outcome pre')).toHaveText(responseText)
  assert.equal(await app.page.evaluate(() => Boolean(window.I06_BAD_EXECUTION)), false)
  const body = received[0].body.toString('utf8')
  assert.equal(body.includes('PUBLIC_VALUE_0'), true)
  for (const marker of [
    'PRIVATE_VALUE_SENTINEL',
    'PRIVATE_DERIVED_SENTINEL',
    'PRIVATE_LABEL_SENTINEL',
    'PRIVATE_DERIVED_LABEL_SENTINEL',
    'I06_FINITE_FIELDS',
    secret,
  ])
    assert.equal(body.includes(marker), false, 'UNSELECTED_BYTES_EGRESS')
  await app.page.screenshot({
    path: path.join(output, 'completed-public-field.png'),
    fullPage: true,
  })
  await saveCase('actual-ui-second-worker-reuses-public-grant-https-selected-bytes-only', {
    firstJobId: evidence.firstJob.jobId,
    secondJobId: secondJob.jobId,
    receiverIndex: 0,
  })

  const beforeReload = await status(app.page)
  await app.page.reload()
  await expect(app.page.getByRole('heading', { name: '解释选中的结果' })).toBeVisible()
  await until(
    async () => (await status(app.page)).invocations.length === beforeReload.invocations.length,
    'RELOAD_LEDGER',
  )
  const afterReload = await status(app.page)
  assert.equal(afterReload.contextId, beforeReload.contextId)
  assert.deepEqual(afterReload.invocations, beforeReload.invocations)
  await wait(1800)
  assert.equal(received.length, 1)
  await saveCase('window-reload-read-only-main-ledger-no-repost')
  await checkProfileLock(app, path.join(fixture, 'second-fixture.json'))

  const healthBefore = await data(app.page, 'getEngineHealth')
  assert.equal(
    await app.page.evaluate(
      () =>
        'invoke' in window.ontolearn ||
        'request' in window.ontolearn ||
        'getModelCredential' in window.ontolearn,
    ),
    false,
  )
  for (let index = 0; index < 3; index++) await status(app.page)
  const healthAfter = await data(app.page, 'getEngineHealth')
  assert.deepEqual(healthAfter, healthBefore)
  await saveCase('main-named-model-calls-leave-real-engine-healthy')

  // Two explicit starts share authorization but have independent invocations and cancellation.
  current = await status(app.page)
  const p = await data(app.page, 'previewModelExplanation', {
    contextId: current.contextId,
    configurationId: configuration.configurationId,
    selectionIds: current.selections.map((value) => value.selectionId),
  })
  assert.equal(p.authorization.state, 'reusable')
  const start = {
    contextId: current.contextId,
    configurationId: configuration.configurationId,
    grantId: p.authorization.grantId,
    selectionIds: current.selections.map((value) => value.selectionId),
  }
  hold = true
  const a = await data(app.page, 'startModelExplanation', start)
  const b = await data(app.page, 'startModelExplanation', start)
  await until(() => received.length === 3, 'TWO_PENDING_HTTPS_POSTS')
  await until(async () => (await app.page.locator('.model-outcome').count()) >= 3, 'PENDING_UI')
  await app.page
    .locator('.model-outcome')
    .filter({ hasText: a.invocationId })
    .getByRole('button', { name: '取消此请求', exact: true })
    .click()
  await until(
    async () => (await invocation(app.page, a.invocationId)).state === 'cancelled',
    'TARGET_CANCEL',
  )
  assert.equal((await invocation(app.page, b.invocationId)).state, 'running')
  for (const record of received.slice(1))
    if (!record.response.destroyed) record.response.end(responseText)
  hold = false
  await until(
    async () => (await invocation(app.page, b.invocationId)).state === 'completed',
    'UNRELATED_COMPLETE',
  )
  await saveCase('targeted-ui-cancel-other-invocation-completes', {
    cancelled: a.invocationId,
    completed: b.invocationId,
  })

  await app.page.getByLabel('项目模型隐私模式', { exact: true }).selectOption('local')
  await until(async () => (await status(app.page)).privacy === 'local', 'LOCAL_TOGGLE')
  await expectDenied(app.page, 'startModelExplanation', start, [
    'GATEWAY_LOCAL_ONLY',
    'GATEWAY_AUTHORIZATION_REQUIRED',
  ])
  await app.page.getByLabel('项目模型隐私模式', { exact: true }).selectOption('minimal')
  await until(async () => (await status(app.page)).privacy === 'minimal', 'MINIMAL_TOGGLE')
  await expectDenied(app.page, 'startModelExplanation', start, ['GATEWAY_AUTHORIZATION_REQUIRED'])
  assert.equal(received.length, 3)
  await saveCase('privacy-local-and-back-does-not-revive-old-grant')

  const freshPreview = await data(app.page, 'previewModelExplanation', {
    contextId: current.contextId,
    configurationId: configuration.configurationId,
    selectionIds: start.selectionIds,
  })
  const freshGrant = await data(app.page, 'confirmModelAuthorization', {
    contextId: current.contextId,
    previewId: freshPreview.previewId,
  })
  const freshStart = { ...start, grantId: freshGrant.grantId }
  const auditPath = path.join(app.userData, 'model-gateway-private-v1/audit')
  await chmod(auditPath, 0o500)
  const blocked = await data(app.page, 'startModelExplanation', freshStart)
  await until(
    async () => (await invocation(app.page, blocked.invocationId)).state === 'failed',
    'AUDIT_DENIAL',
  )
  const failed = await invocation(app.page, blocked.invocationId)
  assert.equal(failed.error.code, 'GATEWAY_AUDIT_UNAVAILABLE')
  assert.equal(received.length, 3)
  assert.equal(
    (await data(app.page, 'restoreTasks')).jobs.some(
      (job) => job.jobId === secondJob.jobId && job.state === 'succeeded',
    ),
    true,
  )
  await expect(app.page.getByRole('heading', { name: '解释选中的结果' })).toBeVisible()
  await chmod(auditPath, 0o700)
  await saveCase('actual-audit-permission-failure-blocks-post-local-window-readable')

  const other = await data(app.page, 'configureModel', {
    contextId: current.contextId,
    configurationId: null,
    configurationVersion: null,
    displayName: 'independent synthetic configuration',
    endpoint,
    model: 'synthetic-other',
  })
  const otherCredential = await data(app.page, 'storeModelCredential', {
    contextId: current.contextId,
    configurationId: other.configurationId,
    configurationVersion: other.configurationVersion,
    secret,
  })
  assert.equal(otherCredential.credentialState, 'configured')
  await expectDenied(
    app.page,
    'startModelExplanation',
    { ...freshStart, configurationId: other.configurationId },
    ['GATEWAY_AUTHORIZATION_REQUIRED', 'GATEWAY_CONFIGURATION_CHANGED'],
  )
  assert.equal(received.length, 3)
  await saveCase('configuration-identity-switch-cannot-use-another-grant')

  await app.page.getByText('模型接收配置与凭据', { exact: true }).click()
  const configSelect = app.page.getByLabel('模型配置', { exact: true })
  await until(
    async () => (await configSelect.locator('option').count()) === 3,
    'UI_SECOND_CONFIGURATION_NOT_RESTORED',
  )
  await configSelect.selectOption(configuration.configurationId)
  await app.page.getByLabel('API 凭据', { exact: true }).fill(secret)
  await configSelect.selectOption(other.configurationId)
  await expect(app.page.getByLabel('API 凭据', { exact: true })).toHaveValue('')
  await configSelect.selectOption('')
  await app.page.locator('input[name="displayName"]').fill('Unsaved synthetic draft')
  await app.page.locator('input[name="endpoint"]').fill(endpoint)
  await app.page.locator('input[name="model"]').fill('unsaved-draft')
  await data(app.page, 'configureModel', {
    contextId: current.contextId,
    configurationId: null,
    configurationVersion: null,
    displayName: 'Poll-observable synthetic addition',
    endpoint,
    model: 'poll-marker',
  })
  // This option can only appear through the real periodic status refresh; no refresh click.
  await expect(
    configSelect.locator('option').filter({ hasText: 'Poll-observable synthetic addition' }),
  ).toHaveCount(1, { timeout: 5000 })
  await expect(configSelect).toHaveValue('')
  await expect(app.page.locator('input[name="displayName"]')).toHaveValue('Unsaved synthetic draft')
  await expect(app.page.locator('input[name="endpoint"]')).toHaveValue(endpoint)
  await expect(app.page.locator('input[name="model"]')).toHaveValue('unsaved-draft')
  await configSelect.selectOption(configuration.configurationId)
  await saveCase('actual-ui-config-switch-clears-password-new-configuration-draft-survives-poll')

  const nowConfiguration = (await status(app.page)).configurations.find(
    (value) => value.configurationId === configuration.configurationId,
  )
  await app.page.getByLabel('API 凭据', { exact: true }).fill(secret)
  const changed = await data(app.page, 'configureModel', {
    contextId: current.contextId,
    configurationId: nowConfiguration.configurationId,
    configurationVersion: nowConfiguration.configurationVersion,
    displayName: nowConfiguration.displayName,
    endpoint: endpoint + '/changed',
    model: nowConfiguration.model,
  })
  assert.equal(changed.credentialState, 'missing')
  assert.notEqual(changed.configurationVersion, nowConfiguration.configurationVersion)
  await expect(app.page.getByLabel('API 凭据', { exact: true })).toHaveValue('', { timeout: 5000 })
  await saveCase('actual-ui-configuration-version-change-remounts-empty-password')
  await expectDenied(app.page, 'startModelExplanation', freshStart, [
    'GATEWAY_CREDENTIAL_UNAVAILABLE',
    'GATEWAY_AUTHORIZATION_REQUIRED',
    'GATEWAY_CONFIGURATION_CHANGED',
  ])
  const restored = await data(app.page, 'configureModel', {
    contextId: current.contextId,
    configurationId: changed.configurationId,
    configurationVersion: changed.configurationVersion,
    displayName: changed.displayName,
    endpoint,
    model: changed.model,
  })
  assert.equal(restored.credentialState, 'missing')
  await expectDenied(
    app.page,
    'storeModelCredential',
    {
      contextId: current.contextId,
      configurationId: restored.configurationId,
      configurationVersion: nowConfiguration.configurationVersion,
      secret,
    },
    ['GATEWAY_CONFIGURATION_CHANGED'],
  )
  const oldChoice = app.page.locator('.model-result-choice').filter({ hasText: firstResult })
  await oldChoice.getByRole('button', { name: '选中当前整份结果', exact: true }).click()
  await expect(app.page.locator('.model-panel > [role="alert"]')).toContainText('INVALID_STATE')
  await oldChoice.getByRole('button', { name: '明确选中此历史版本', exact: true }).click()
  const historical = await until(async () => {
    const selection = (await status(app.page)).selections[0]
    return selection?.kind === 'whole-result' && selection.selection === 'historical'
      ? selection
      : false
  }, 'EXPLICIT_HISTORY_SELECTION')
  assert.equal(historical.metadata.resultId, firstResult)
  assert.equal(historical.metadata.state, 'historical')
  assert.equal(historical.metadata.historicalSelectionRequired, true)
  assert.equal(historical.rowCount, 3)
  const newChoice = app.page
    .locator('.model-result-choice')
    .filter({ hasText: secondJob.resultRef.resultId })
  await newChoice.getByRole('button', { name: '选中当前整份结果', exact: true }).click()
  const whole = await until(async () => {
    const selection = (await status(app.page)).selections[0]
    return selection?.kind === 'whole-result' && selection.selection === 'current'
      ? selection
      : false
  }, 'EXPLICIT_CURRENT_SELECTION')
  assert.equal(whole.metadata.resultId, secondJob.resultRef.resultId)
  assert.equal(whole.metadata.state, 'current')
  assert.equal(whole.metadata.historicalSelectionRequired, false)
  assert.equal(whole.rowCount, 3)
  await saveCase('actual-ui-whole-result-current-denial-and-explicit-history-read-only-selection')
  assert.equal(received.length, 3)
  await app.close()
  await saveCase('endpoint-change-missing-key-old-credential-version-and-grant-denied')

  const recovered = await launch(
    'durable-audit-recover',
    path.join(fixture, 'fixture.json'),
    'secure',
  )
  await until(
    async () => (await status(recovered.page)).availability === 'ready',
    'DURABLE_RECOVER_READY',
  )
  const recoveredStatus = await status(recovered.page)
  assert.equal(recoveredStatus.privacy, 'local')
  assert.equal(recoveredStatus.invocations.length, 0)
  await wait(1800)
  assert.equal(received.length, 3)
  await recovered.close()
  await saveCase('second-app-process-durable-audit-recovery-never-replays')

  const saveFixture = prepare('append-failure-local-save', 'audit-save')
  const saveEvidence = JSON.parse(
    await readFile(path.join(saveFixture, 'fixture-evidence.json'), 'utf8'),
  )
  const saveApp = await launch('append-failure-local-save', path.join(saveFixture, 'fixture.json'))
  await until(
    async () => (await status(saveApp.page)).availability === 'ready',
    'AUDIT_SAVE_PROJECT_READY',
  )
  const saveConfiguration = await configureUI(saveApp.page)
  await saveApp.page.getByLabel('项目模型隐私模式', { exact: true }).selectOption('minimal')
  await selectPublicUI(saveApp.page, saveEvidence.firstJob.resultRef.resultId)
  await previewUI(saveApp.page)
  const saveStatus = await status(saveApp.page)
  const savePreview = await data(saveApp.page, 'previewModelExplanation', {
    contextId: saveStatus.contextId,
    configurationId: saveConfiguration.configurationId,
    selectionIds: saveStatus.selections.map((selection) => selection.selectionId),
  })
  assert.equal(savePreview.authorization.state, 'reusable')
  const saveAudit = path.join(saveApp.userData, 'model-gateway-private-v1/audit')
  await chmod(saveAudit, 0o500)
  const saveInvocation = await data(saveApp.page, 'startModelExplanation', {
    contextId: saveStatus.contextId,
    configurationId: saveConfiguration.configurationId,
    grantId: savePreview.authorization.grantId,
    selectionIds: saveStatus.selections.map((selection) => selection.selectionId),
  })
  await until(
    async () => (await invocation(saveApp.page, saveInvocation.invocationId)).state === 'failed',
    'APPEND_FAILURE_OUTCOME',
  )
  assert.equal(
    (await invocation(saveApp.page, saveInvocation.invocationId)).error.code,
    'GATEWAY_AUDIT_UNAVAILABLE',
  )
  const saving = (await data(saveApp.page, 'restoreTasks')).jobs.find(
    (job) => job.operationId === saveEvidence.atomic.operationId,
  )
  assert.ok(
    saving && ['queued', 'running'].includes(saving.state),
    'ATOMIC_COMMITTED_BEFORE_AUDIT_FAILURE_WAS_OBSERVED',
  )
  assert.equal(await data(saveApp.page, 'getOperation', saveEvidence.atomic.operationId), null)
  const savedAfterAppendFailure = await until(
    async () =>
      (await data(saveApp.page, 'restoreTasks')).jobs.find(
        (job) =>
          job.jobId === saving.jobId &&
          job.operationId === saveEvidence.atomic.operationId &&
          job.state === 'succeeded',
      ),
    'STORE_COMMIT_WITH_AUDIT_STILL_UNSAFE',
    20000,
  )
  assert.equal((await stat(saveAudit)).mode & 0o777, 0o500)
  assert.ok(await data(saveApp.page, 'getOperation', savedAfterAppendFailure.operationId))
  assert.equal(received.length, 3)
  await chmod(saveAudit, 0o700)
  await saveApp.close()
  await saveCase('actual-store-worker-commit-while-audit-directory-remains-unsafe', {
    jobId: savedAfterAppendFailure.jobId,
    operationId: savedAfterAppendFailure.operationId,
  })

  // An actual malformed durable audit disables models while the separately owned worker commits.
  const failureFixture = prepare('initialization-failure', 'atomic')
  const failureProfile =
    '/probe-data/profiles/initialization-failure/model-gateway-private-v1/audit'
  await mkdir(failureProfile, { recursive: true, mode: 0o700 })
  await writeFile(path.join(failureProfile, randomUUID() + '.audit'), 'synthetic-corrupt-audit\n', {
    mode: 0o600,
  })
  const degraded = await launch('initialization-failure', path.join(failureFixture, 'fixture.json'))
  const committed = await until(
    async () =>
      (await data(degraded.page, 'restoreTasks')).jobs.find(
        (job) => job.state === 'succeeded' && job.capability === 'test.atomic',
      ),
    'LOCAL_ATOMIC_COMMIT_FAILED',
    20000,
  )
  assert.equal((await status(degraded.page)).availability, 'unavailable')
  const operation = await data(degraded.page, 'getOperation', committed.operationId)
  assert.ok(operation)
  await expect(degraded.page.getByRole('heading', { name: '解释选中的结果' })).toBeVisible()
  await degraded.close()
  await saveCase(
    'actual-model-init-audit-recovery-failure-local-store-worker-commit-window-works',
    { jobId: committed.jobId, operationId: committed.operationId },
  )

  // No project changes or outbound request are needed to prove a basic backend fails credential writes.
  const basicFixture = prepare('basic', 'atomic')
  const basic = await launch('basic', path.join(basicFixture, 'fixture.json'), 'basic', 'basic')
  await until(
    async () => (await status(basic.page)).availability === 'ready',
    'BASIC_PROJECT_READY',
  )
  assert.equal(basic.runtime.backend, 'basic_text')
  const basicContext = await status(basic.page)
  const basicConfig = await data(basic.page, 'configureModel', {
    contextId: basicContext.contextId,
    configurationId: null,
    configurationVersion: null,
    displayName: 'basic denied',
    endpoint,
    model: 'synthetic-model',
  })
  await expectDenied(
    basic.page,
    'storeModelCredential',
    {
      contextId: basicContext.contextId,
      configurationId: basicConfig.configurationId,
      configurationVersion: basicConfig.configurationVersion,
      secret,
    },
    ['GATEWAY_CREDENTIAL_UNAVAILABLE'],
  )
  const credentials = path.join(basic.userData, 'model-gateway-private-v1/credentials')
  assert.equal(
    (await readdir(credentials)).filter((name) => name.endsWith('.credential')).length,
    0,
  )
  await basic.close()
  await saveCase('actual-main-basic-backend-zero-credential-files')

  const unavailable = await launch(
    'backend-unavailable',
    path.join(basicFixture, 'fixture.json'),
    'backend-unavailable',
    'gnome-libsecret',
    { DBUS_SESSION_BUS_ADDRESS: 'unix:path=/tmp/i06-main-no-such-bus' },
  )
  await until(
    async () => (await status(unavailable.page)).availability === 'ready',
    'UNAVAILABLE_PROJECT_READY',
  )
  assert.equal(unavailable.runtime.encryptionAvailable, false)
  const unavailableContext = await status(unavailable.page)
  const unavailableConfig = await data(unavailable.page, 'configureModel', {
    contextId: unavailableContext.contextId,
    configurationId: null,
    configurationVersion: null,
    displayName: 'unavailable denied',
    endpoint,
    model: 'synthetic-model',
  })
  await expectDenied(
    unavailable.page,
    'storeModelCredential',
    {
      contextId: unavailableContext.contextId,
      configurationId: unavailableConfig.configurationId,
      configurationVersion: unavailableConfig.configurationVersion,
      secret,
    },
    ['GATEWAY_CREDENTIAL_UNAVAILABLE'],
  )
  assert.equal(
    (await readdir(path.join(unavailable.userData, 'model-gateway-private-v1/credentials'))).filter(
      (name) => name.endsWith('.credential'),
    ).length,
    0,
  )
  await unavailable.close()
  await saveCase('actual-main-unavailable-backend-zero-credential-files')

  execFileSync(
    '/workspace/.venv/bin/python',
    [
      '-I',
      '/workspace/tests/i06-main-platform/protocol-negative.py',
      '/probe-data/fixtures/protocol-negative',
      path.join(output, 'main-only-worker-rejection.json'),
    ],
    { cwd: root, encoding: 'utf8', timeout: 15000 },
  )
  await saveCase('actual-worker-protocol-rejects-main-only-method')
  checkPublicBodies(secondJob.resultRef.resultId)
  assert.equal(requestError, false, 'HTTPS_REQUEST_IDENTITY')
  await writeFile(
    path.join(output, 'receiver-manifest.json'),
    JSON.stringify(
      received.map(({ index, path: requestPath, byteCount, sha256 }) => ({
        index,
        requestPath,
        byteCount,
        sha256,
      })),
      null,
      2,
    ) + '\n',
  )
  await writeFile(
    path.join(output, 'scan-input.json'),
    JSON.stringify({
      database: path.join(fixture, 'engine.sqlite'),
      receiverBodyFiles: received.map(({ index }) => `receiver-${index}.body`),
    }) + '\n',
  )
  await writeFile(
    path.join(output, 'result.json'),
    JSON.stringify(
      {
        result: 'passed',
        cases,
        receiverRequests: received.length,
        exportEntry: 'absent',
        evidenceScope:
          'Linux arm64 Electron44.9.0 frozen actual app build, I04 synthetic producers; no Mac/Windows/signed-package claim',
      },
      null,
      2,
    ) + '\n',
  )
} catch (error) {
  // Probe failures are retained, but never echo credential/raw business values from driver call logs.
  const diagnostic = String(error.stack ?? error)
    .replaceAll(secret, '[credential-redacted]')
    .replaceAll(responseMarker, '[response-redacted]')
  await writeFile(path.join(output, 'failure.txt'), diagnostic + '\n')
  await writeFile(
    path.join(output, 'result.json'),
    JSON.stringify({ result: 'failed', completedCases: cases, receiverRequests: received.length }) +
      '\n',
  )
  process.exitCode = 1
} finally {
  await writeFile(
    path.join(output, 'receiver-manifest.json'),
    JSON.stringify(
      received.map(({ index, path: requestPath, byteCount, sha256 }) => ({
        index,
        requestPath,
        byteCount,
        sha256,
      })),
      null,
      2,
    ) + '\n',
  )
  for (const close of applications.values()) await close().catch(() => {})
  for (const socket of sockets) socket.destroy()
  await new Promise((resolve) => server.close(resolve))
}
