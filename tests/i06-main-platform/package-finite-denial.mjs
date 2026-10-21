import assert from 'node:assert/strict'
import { execFileSync, spawn } from 'node:child_process'
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises'
const output = '/probe-data/main-platform'
const fixture = '/probe-data/fixtures/package-finite-denial'
await mkdir('/probe-data/fixtures', { recursive: true })
await mkdir('/probe-data/profiles/package-finite-denial', { recursive: true, mode: 0o700 })
execFileSync(
  '/workspace/.venv/bin/python',
  ['-I', '/workspace/tests/i06-main-platform/native-fixture.py', fixture],
  { stdio: 'pipe' },
)
const args = [
  '--inspect=0',
  '--password-store=gnome-libsecret',
  '--user-data-dir=/probe-data/profiles/package-finite-denial',
  `--i04-test-fixture=${fixture}/fixture.json`,
]
const executable = '/workspace/release/linux-arm64-unpacked/@ontolearndesktop'
const child = spawn(executable, args, {
  cwd: '/workspace',
  env: {
    ...process.env,
    I04_TEST_FIXTURE: `${fixture}/fixture.json`,
    I06_NATIVE_EVIDENCE: `${output}/package-finite-observer.json`,
    I06_NATIVE_FIXTURE_EVIDENCE: `${fixture}/fixture-evidence.json`,
    I06_PACKAGE_FINITE_DENIAL: '1',
    I06_NATIVE_SECRET: process.env.I06_PACKAGE_FINITE_SECRET,
    I06_NATIVE_ENDPOINT: process.env.I06_PACKAGE_FINITE_ENDPOINT,
  },
  stdio: ['ignore', 'pipe', 'pipe'],
})
let diagnostic = '',
  closed = false
const logs = []
const completed = new Promise((resolve) =>
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
const timer = setTimeout(() => child.kill('SIGTERM'), 45000)
try {
  let url
  while (!closed) {
    url = diagnostic.match(/Debugger listening on (ws:\/\/127\.0\.0\.1:\d+\/[^\s]+)/)?.[1]
    if (url) break
    await new Promise((resolve) => setTimeout(resolve, 20))
  }
  assert.ok(url, 'PACKAGED_FINITE_INSPECTOR_ENDPOINT')
  const socket = new WebSocket(url)
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true })
    socket.addEventListener('error', reject, { once: true })
  })
  const bootstrapped = new Promise((resolve, reject) =>
    socket.addEventListener('message', ({ data }) => {
      const message = JSON.parse(data)
      if (message.id !== 1) return
      if (message.error || message.result.exceptionDetails)
        reject(new Error('PACKAGED_FINITE_BOOTSTRAP_FAILED'))
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
  await bootstrapped
  socket.close()
  const exit = await completed
  assert.equal(exit.code, 0)
  assert.equal(exit.signal, null)
  const observer = JSON.parse(await readFile(`${output}/package-finite-observer.json`, 'utf8'))
  assert.equal(observer.result, 'passed')
  assert.equal(observer.finitePolicyDenied, true)
  assert.equal(observer.runtime.packaged, true)
  let credentialFiles = []
  try {
    credentialFiles = await readdir(
      '/probe-data/profiles/package-finite-denial/model-gateway-private-v1/credentials',
    )
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
  }
  assert.equal(credentialFiles.length, 0)
  await writeFile(
    `${output}/package-finite-denial.json`,
    JSON.stringify(
      {
        result: 'passed',
        executable,
        args,
        appIsPackaged: true,
        modelUnavailable: true,
        credentialFiles: 0,
        credentialRecorded: false,
        receiverObservation: 'Measured by active parent receiver, see package-finite-receiver.json',
        rejections: observer.rejections,
        profile: 'package-finite-denial',
      },
      null,
      2,
    ) + '\n',
  )
} finally {
  clearTimeout(timer)
  if (!closed) {
    child.kill('SIGTERM')
    await completed
  }
  await writeFile(`${output}/package-finite.product.log`, Buffer.concat(logs))
}
