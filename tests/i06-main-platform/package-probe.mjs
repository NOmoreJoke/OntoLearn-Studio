import assert from 'node:assert/strict'
import { execFile, execFileSync, spawn } from 'node:child_process'
import { randomUUID, createHash } from 'node:crypto'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import https from 'node:https'
import { promisify } from 'node:util'
const output = '/probe-data/main-platform'
const secret = 'I06_MAIN_SYNTHETIC_SECRET_' + randomUUID()
const response = 'I06_RESPONSE_PRIVATE_MARKER_' + randomUUID()
const fixture = '/probe-data/fixtures/package'
await mkdir('/probe-data/fixtures', { recursive: true })
await mkdir('/probe-data/profiles/package', { recursive: true, mode: 0o700 })
execFileSync(
  '/workspace/.venv/bin/python',
  ['-I', '/workspace/tests/i06-main-platform/package-fixture.py', fixture],
  { stdio: 'pipe' },
)
const received = []
let badRequest = false
const server = https.createServer(
  {
    key: await readFile('/probe-data/certificates/server.key'),
    cert: await readFile('/probe-data/certificates/server.pem'),
  },
  async (request, reply) => {
    const chunks = []
    for await (const chunk of request) chunks.push(chunk)
    const body = Buffer.concat(chunks),
      index = received.length
    if (request.method !== 'POST' || request.headers.authorization !== 'Bearer ' + secret)
      badRequest = true
    received.push({
      index,
      byteCount: body.length,
      sha256: createHash('sha256').update(body).digest('hex'),
    })
    await writeFile(`${output}/receiver-${index}.body`, body)
    reply.setHeader('Content-Type', 'text/plain; charset=utf-8')
    reply.end(response)
  },
)
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
const finiteBefore = received.length
await promisify(execFile)(
  process.execPath,
  ['/workspace/tests/i06-main-platform/package-finite-denial.mjs'],
  {
    env: {
      ...process.env,
      I06_PACKAGE_FINITE_ENDPOINT: `https://127.0.0.1:${server.address().port}/v1/chat/completions`,
      I06_PACKAGE_FINITE_SECRET: secret,
    },
  },
)
await new Promise((resolve) => setTimeout(resolve, 100))
assert.equal(received.length, finiteBefore)
await writeFile(
  `${output}/package-finite-receiver.json`,
  JSON.stringify(
    {
      result: 'passed',
      receiverActiveDuringDeniedBridgeCalls: true,
      requestsBefore: finiteBefore,
      requestsAfter: received.length,
      actualRequestDelta: received.length - finiteBefore,
    },
    null,
    2,
  ) + '\n',
)

const args = [
  '--inspect=0',
  '--password-store=gnome-libsecret',
  '--user-data-dir=/probe-data/profiles/package',
  `--i04-test-fixture=${fixture}/fixture.json`,
]
await writeFile(
  `${output}/spawn.json`,
  JSON.stringify(
    {
      executable: '/workspace/release/linux-arm64-unpacked/@ontolearndesktop',
      args,
      envNamesAdded: [
        'I04_TEST_FIXTURE',
        'I06_NATIVE_EVIDENCE',
        'I06_NATIVE_FIXTURE_EVIDENCE',
        'I06_NATIVE_SECRET',
        'I06_NATIVE_ENDPOINT',
      ],
      rendererCDP: false,
    },
    null,
    2,
  ) + '\n',
)
const child = spawn('/workspace/release/linux-arm64-unpacked/@ontolearndesktop', args, {
  cwd: '/workspace/apps/desktop',
  env: {
    ...process.env,
    I04_TEST_FIXTURE: `${fixture}/fixture.json`,
    I06_NATIVE_EVIDENCE: `${output}/native-observer.json`,
    I06_NATIVE_FIXTURE_EVIDENCE: `${fixture}/fixture-evidence.json`,
    I06_NATIVE_SECRET: secret,
    I06_NATIVE_ENDPOINT: `https://127.0.0.1:${server.address().port}/v1/chat/completions`,
  },
  stdio: ['ignore', 'pipe', 'pipe'],
})
const logs = []
let diagnostic = '',
  closed = false
const completion = new Promise((resolve) =>
  child.once('close', (code, signal) => {
    closed = true
    resolve({ code, signal })
  }),
)
child.stdout.on('data', (bytes) => logs.push(bytes))
child.stderr.on('data', (bytes) => {
  logs.push(bytes)
  diagnostic += bytes.toString()
})
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
const readObserver = () =>
  readFile(`${output}/native-observer.json`, 'utf8')
    .then(JSON.parse)
    .catch(() => null)
const actions = []
let result = { result: 'failed' }
try {
  let nodeURL
  const deadline = Date.now() + 90000
  while (Date.now() < deadline && !closed) {
    nodeURL = diagnostic.match(/Debugger listening on (ws:\/\/127\.0\.0\.1:\d+\/[^\s]+)/)?.[1]
    if (nodeURL) break
    await delay(20)
  }
  assert.ok(nodeURL, 'NATIVE_MAIN_INSPECTOR_ENDPOINT')
  const socket = new WebSocket(nodeURL)
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true })
    socket.addEventListener('error', reject, { once: true })
  })
  const bootstrap = new Promise((resolve, reject) =>
    socket.addEventListener('message', ({ data }) => {
      const message = JSON.parse(data)
      if (message.id !== 1) return
      if (message.error || message.result.exceptionDetails)
        reject(new Error('NATIVE_HOOK_BOOTSTRAP_FAILED'))
      else resolve()
    }),
  )
  socket.send(
    JSON.stringify({
      id: 1,
      method: 'Runtime.evaluate',
      params: {
        expression:
          "process.getBuiltinModule('node:module').createRequire('/workspace/apps/desktop/package.json')('/workspace/tests/i06-main-platform/package-hook.cjs')",
      },
    }),
  )
  await bootstrap
  socket.close()
  let acted = false
  while (Date.now() < deadline && !closed) {
    const observer = await readObserver()
    if (observer?.stage === 'awaiting-real-crash-dialog' && !acted) {
      let ids = []
      try {
        ids = execFileSync('xdotool', ['search', '--onlyvisible', '--name', '.*'], {
          encoding: 'utf8',
        })
          .trim()
          .split('\n')
      } catch {
        /* Real visible prompt may not exist yet. */
      }
      const windows = ids.filter(Boolean).map((id) => ({
        id,
        title: execFileSync('xdotool', ['getwindowname', id], { encoding: 'utf8' }).trim(),
        visible: true,
      }))
      const prompt = windows.find((window) => window.title === 'OntoLearn Studio 窗口恢复')
      if (prompt) {
        assert.equal(observer.inspectorClosedBeforeFault, true)
        assert.equal(received.length, 1)
        execFileSync('scrot', [`${output}/actual-native-dialog.png`])
        execFileSync('xdotool', ['windowactivate', '--sync', prompt.id])
        execFileSync('xdotool', ['key', '--clearmodifiers', 'shift+Tab', 'Return'])
        actions.push({
          observer: 'xdotool visible X11 window inventory',
          windows,
          prompt,
          keys: ['shift+Tab', 'Return'],
          receiverRequestsBeforeAction: received.length,
          inspectorClosedBeforeFault: true,
          dialogReplacement: false,
        })
        await writeFile(`${output}/native-actions.json`, JSON.stringify(actions, null, 2) + '\n')
        acted = true
      }
    }
    await delay(50)
  }
  if (!closed) {
    child.kill('SIGTERM')
    throw new Error('NATIVE_EXTERNAL_DRIVER_DEADLINE')
  }
  const exit = await completion,
    observer = await readObserver()
  assert.equal(exit.code, 0, 'NATIVE_CHILD_NONZERO')
  assert.equal(exit.signal, null)
  assert.equal(observer.result, 'passed')
  assert.equal(observer.windows.length, 2)
  assert.equal(acted, true)
  assert.equal(received.length, 1)
  assert.equal(badRequest, false)
  const body = await readFile(`${output}/receiver-0.body`, 'utf8')
  assert.equal(body.includes(secret), false)
  const request = JSON.parse(body)
  assert.deepEqual(Object.keys(request).sort(), ['model', 'parts'])
  assert.equal(request.model, 'synthetic-native')
  assert.equal(request.parts.length, 1)
  assert.deepEqual(Object.keys(request.parts[0]).sort(), ['kind', 'text'])
  assert.equal(request.parts[0].kind, 'selected')
  const projection = JSON.parse(request.parts[0].text)
  assert.deepEqual(Object.keys(projection).sort(), ['rows', 'source'])
  assert.deepEqual(projection.rows, observer.selection.sourcePage.rows)
  assert.deepEqual(projection.source, {
    ...observer.selection.sourceMetadata,
    selection: 'historical',
    producerCapability: 'test.read',
    stateMeaning: 'observed-at-read; immutable-selected-result; not-live-current-lease',
  })
  assert.ok(body.includes('PRIVATE_VALUE_SENTINEL_'), 'WHOLE_RESULT_IS_EXPLICITLY_SELECTED')
  result = {
    result: 'passed',
    receiverRequests: received.length,
    actualNativeCrashRecovery: true,
    packagedExecutable: true,
    selectionKind: 'whole-result',
    inspectorClosedBeforeFault: true,
    rendererCDPEverAttached: false,
    windows: 2,
    recoveryReadOnly: true,
    noAutomaticResend: true,
    scope:
      'Incremental actual crash and visible recovery prompt; no unresponsive/hang matrix claim.',
  }
} catch (error) {
  result.error = String(error)
  if (!closed) child.kill('SIGTERM')
  await completion
  throw error
} finally {
  await writeFile(`${output}/native.product.log`, Buffer.concat(logs))
  await writeFile(`${output}/receiver-manifest.json`, JSON.stringify(received, null, 2) + '\n')
  await writeFile(`${output}/result.json`, JSON.stringify(result, null, 2) + '\n')
  await writeFile(
    `${output}/scan-input.json`,
    JSON.stringify({
      database: `${fixture}/engine.sqlite`,
      receiverBodyFiles: received.map((entry) => `receiver-${entry.index}.body`),
    }) + '\n',
  )
  await new Promise((resolve) => server.close(resolve))
}
