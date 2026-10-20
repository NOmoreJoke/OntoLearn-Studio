/* eslint-disable @typescript-eslint/no-require-imports -- Normal Electron CommonJS main entry. */
/* Actual Electron main probe. Synthetic fixture repository is NOT the product private repository. */
const assert = require('node:assert/strict')
const { randomUUID } = require('node:crypto')
const fs = require('node:fs')
const os = require('node:os')
const { app, safeStorage } = require('electron')
const { createElectronCredentialBoundary } = require('./out/electron-safe-storage')
const mode = process.env.I06_PROBE_MODE
const fixturePath = '/probe-data/synthetic-fixture.json'
let writes = 0
let record
const repository = {
  async write(binding, ciphertext) {
    writes++
    record = { binding, ciphertext: Buffer.from(ciphertext) }
  },
  async read() {
    if (!record) throw new Error('synthetic missing fixture')
    return record
  },
}
const evidence = {
  mode,
  platform: process.platform,
  arch: process.arch,
  os: os.release(),
  versions: process.versions,
  runtimeType: process.type,
  runAsNode: Boolean(process.env.ELECTRON_RUN_AS_NODE),
  beforeReady: {
    ready: app.isReady(),
    available: safeStorage.isEncryptionAvailable(),
    backend: safeStorage.getSelectedStorageBackend(),
  },
  assertions: [],
}
assert.equal(process.versions.electron, '44.9.0')
assert.equal(process.type, 'browser')
assert.equal(evidence.runAsNode, false)
assert.equal(evidence.beforeReady.backend, 'unknown')
assert.equal(evidence.beforeReady.available, false)
assert.throws(() => createElectronCredentialBoundary(repository), /^Error: CREDENTIAL_UNAVAILABLE$/)
evidence.assertions.push('factory-denies-before-ready')
app.setPath('userData', '/probe-data/userdata-' + mode)
app
  .whenReady()
  .then(async () => {
    evidence.ready = app.isReady()
    evidence.available = safeStorage.isEncryptionAvailable()
    evidence.backend = safeStorage.getSelectedStorageBackend()
    const vault = createElectronCredentialBoundary(repository)
    if (mode === 'secure-write') {
      assert.equal(evidence.backend, 'gnome_libsecret')
      assert.equal(evidence.available, true)
      const binding = await vault.store(randomUUID(), 'I06_SYNTHETIC_PLATFORM_CREDENTIAL')
      assert.equal(writes, 1)
      assert.equal(
        record.ciphertext.includes(Buffer.from('I06_SYNTHETIC_PLATFORM_CREDENTIAL')),
        false,
      )
      assert.deepEqual(await vault.read(binding.ref), {
        ...binding,
        secret: 'I06_SYNTHETIC_PLATFORM_CREDENTIAL',
      })
      fs.writeFileSync(
        fixturePath,
        JSON.stringify({ binding, ciphertext: record.ciphertext.toString('base64') }),
        { mode: 0o600 },
      )
      evidence.assertions.push(
        'actual-secure-encrypt-decrypt',
        'ciphertext-has-no-plaintext',
        'opaque-binding-only',
      )
    } else if (['recover', 'corrupt', 'key-loss'].includes(mode)) {
      const saved = JSON.parse(fs.readFileSync(fixturePath, 'utf8'))
      record = { binding: saved.binding, ciphertext: Buffer.from(saved.ciphertext, 'base64') }
      if (mode === 'recover') {
        assert.equal(
          (await vault.read(saved.binding.ref)).secret,
          'I06_SYNTHETIC_PLATFORM_CREDENTIAL',
        )
        evidence.assertions.push('actual-second-process-decrypt')
      } else {
        if (mode === 'corrupt') record.ciphertext = Buffer.from('invalid synthetic ciphertext')
        await assert.rejects(vault.read(saved.binding.ref), /^Error: CREDENTIAL_UNAVAILABLE$/)
        evidence.assertions.push(
          mode === 'corrupt'
            ? 'actual-decrypt-failure-sanitized'
            : 'actual-new-keyring-recovery-denied',
        )
      }
      assert.equal(writes, 0)
    } else if (['basic', 'unavailable'].includes(mode)) {
      if (mode === 'basic') assert.equal(evidence.backend, 'basic_text')
      assert.ok(
        !evidence.available ||
          !['gnome_libsecret', 'kwallet', 'kwallet5', 'kwallet6'].includes(evidence.backend),
      )
      await assert.rejects(
        vault.store(randomUUID(), 'I06_SYNTHETIC_PLATFORM_CREDENTIAL'),
        /^Error: CREDENTIAL_UNAVAILABLE$/,
      )
      await assert.rejects(vault.read(randomUUID()), /^Error: CREDENTIAL_UNAVAILABLE$/)
      assert.equal(writes, 0)
      evidence.assertions.push('insecure-or-unavailable-denied-with-zero-writes')
    } else throw new Error('invalid synthetic probe mode')
    evidence.result = 'passed'
    fs.writeFileSync(`/probe-data/${mode}.json`, JSON.stringify(evidence, null, 2) + '\n')
    console.log(
      JSON.stringify({
        mode,
        result: evidence.result,
        backend: evidence.backend,
        available: evidence.available,
        assertions: evidence.assertions,
      }),
    )
    app.exit(0)
  })
  .catch(() => {
    evidence.result = 'failed'
    fs.writeFileSync(`/probe-data/${mode}.json`, JSON.stringify(evidence, null, 2) + '\n')
    console.error(JSON.stringify({ mode, result: 'failed' }))
    app.exit(1)
  })
