/* eslint-disable @typescript-eslint/no-require-imports -- Actual Electron CommonJS main entry. */
const assert = require('node:assert/strict')
const { randomUUID, createHash } = require('node:crypto')
const fs = require('node:fs/promises')
const http = require('node:http')
const path = require('node:path')
const { app, safeStorage } = require('electron')
const { createElectronCredentialBoundary } = require('./out/electron-safe-storage')
const { PrivateCiphertextRepository } = require('./out/ciphertext-repository')
const { PersistentGatewayAudit } = require('./out/persistent-audit')
const { ModelGatewayCore } = require('./out/gateway')
const mode = process.env.I06_PRIVATE_PROBE_MODE
const userData = '/probe-data/PRIVATE_PATH_MARKER'
const bindingFile = '/probe-data/combination-binding.json'
const forbidden = [
  'I06_COMBINATION_SYNTHETIC_SECRET',
  'I06_COMBINATION_SYNTHETIC_BUSINESS',
  'I06_SYNTHETIC_ENDPOINT_PATH',
  'PRIVATE_PATH_MARKER',
]
const evidence = {
  mode,
  platform: process.platform,
  arch: process.arch,
  versions: process.versions,
  runtimeType: process.type,
  runAsNode: Boolean(process.env.ELECTRON_RUN_AS_NODE),
  assertions: [],
}
const location = (userDataPath = userData) => ({
  userDataPath,
  excludedRoots: ['/probe-data/projects', '/probe-data/exports'],
})
async function scanPrivate(directory) {
  let count = 0
  for (const item of await fs.readdir(directory, { withFileTypes: true })) {
    const full = path.join(directory, item.name)
    const stat = await fs.lstat(full)
    if (item.isDirectory()) {
      assert.equal(stat.mode & 0o7777, 0o700)
      count += await scanPrivate(full)
    } else {
      assert.equal(item.isFile(), true)
      assert.equal(stat.mode & 0o7777, 0o600)
      const bytes = await fs.readFile(full)
      for (const token of forbidden) assert.equal(bytes.includes(Buffer.from(token)), false)
      count++
    }
    assert.equal(stat.uid, process.getuid())
  }
  return count
}
async function receiver(port = 0) {
  let received = 0
  const server = http.createServer((request, response) => {
    const chunks = []
    request.on('data', (chunk) => chunks.push(chunk))
    request.on('end', () => {
      received++
      assert.equal(request.method, 'POST')
      assert.equal(request.headers.authorization, 'Bearer ' + forbidden[0])
      assert.equal(Buffer.concat(chunks).includes(Buffer.from(forbidden[1])), true)
      response.end('synthetic-combination-response')
    })
  })
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve))
  return {
    endpoint: `http://127.0.0.1:${server.address().port}/${forbidden[2]}`,
    count: () => received,
    close: () => new Promise((resolve) => server.close(resolve)),
  }
}
async function directoryNegatives(repository, binding) {
  const bucket = path.join(userData, 'model-gateway-private-v1', 'credentials')
  await fs.chmod(bucket, 0o755)
  await assert.rejects(repository.read(binding.ref), /^Error: CREDENTIAL_UNAVAILABLE$/)
  await fs.chmod(bucket, 0o700)
  const alias = '/probe-data/alias-userdata'
  await fs.symlink(userData, alias)
  await assert.rejects(
    PrivateCiphertextRepository.open(location(alias)),
    /^Error: CREDENTIAL_UNAVAILABLE$/,
  )
  await assert.rejects(
    PrivateCiphertextRepository.open({ userDataPath: userData, excludedRoots: [userData] }),
    /^Error: CREDENTIAL_UNAVAILABLE$/,
  )
  assert.equal((await fs.lstat('/probe-data/foreign-userdata')).uid, 0)
  assert.notEqual(process.getuid(), 0)
  await assert.rejects(
    PrivateCiphertextRepository.open(location('/probe-data/foreign-userdata')),
    /^Error: CREDENTIAL_UNAVAILABLE$/,
  )
  evidence.assertions.push(
    'real-private-permissions',
    'real-symlink-denied',
    'real-excluded-overlap-denied',
    'real-foreign-owner-denied',
  )
}
assert.equal(process.type, 'browser')
assert.equal(process.versions.electron, '44.9.0')
assert.equal(evidence.runAsNode, false)
app.setPath('userData', '/probe-data/electron-userdata-' + mode)
app
  .whenReady()
  .then(async () => {
    evidence.backend = safeStorage.getSelectedStorageBackend()
    evidence.available = safeStorage.isEncryptionAvailable()
    if (mode === 'secure-send') {
      assert.equal(evidence.backend, 'gnome_libsecret')
      assert.equal(evidence.available, true)
      const repository = await PrivateCiphertextRepository.open(location())
      const vault = createElectronCredentialBoundary(repository)
      const binding = await vault.store(randomUUID(), forbidden[0])
      assert.deepEqual(await vault.read(binding.ref), { ...binding, secret: forbidden[0] })
      await directoryNegatives(repository, binding)
      const audit = await PersistentGatewayAudit.open(location())
      const target = await receiver()
      await fs.writeFile(
        bindingFile,
        JSON.stringify({ binding, port: Number(new URL(target.endpoint).port) }),
        { mode: 0o600 },
      )
      const gateway = new ModelGatewayCore(vault, audit, 'loopback-probe-only')
      const projectId = randomUUID(),
        scope = randomUUID(),
        configId = randomUUID()
      gateway.configure({
        id: configId,
        endpoint: target.endpoint,
        credentialRef: binding.ref,
        principal: binding.principal,
        credentialVersion: binding.version,
        model: 'synthetic-protocol',
      })
      gateway.setPrivacy(projectId, 'minimal')
      const material = gateway.registerMaterial({
        projectId,
        scopes: [scope],
        kind: 'selected',
        text: forbidden[1],
      })
      const preview = gateway.previewAuthorization({
        projectId,
        configId,
        purpose: 'explain',
        scopes: [scope],
      })
      const grantId = gateway.confirmAuthorization(preview.previewId)
      assert.deepEqual(
        await gateway.invoke({
          projectId,
          configId,
          grantId,
          purpose: 'explain',
          materials: [material],
        }),
        { ok: true, text: 'synthetic-combination-response' },
      )
      assert.equal(target.count(), 1)
      const entries = await audit.readEntries()
      assert.equal(entries.length, 1)
      assert.equal(entries[0].record.event, 'attempt-intent')
      assert.equal(entries[0].record.reason, 'ATTEMPT_INTENT')
      assert.equal(Object.keys(entries[0].record).includes('body'), false)
      evidence.postCount = target.count()
      await target.close()
      gateway.closeProject(projectId)
      await Promise.all([audit.close(), repository.close()])
      evidence.privateFileCount = await scanPrivate(path.join(userData, 'model-gateway-private-v1'))
      assert.equal(evidence.privateFileCount, 2)
      evidence.assertions.push(
        'actual-safe-storage-private-ciphertext-durable',
        'actual-gateway-post-once',
        'actual-durable-metadata-audit',
        'private-files-no-plaintext-credential-business-path',
      )
    } else if (mode === 'recover-no-replay') {
      const saved = JSON.parse(await fs.readFile(bindingFile, 'utf8'))
      // Listen at the ORIGINAL endpoint before any recovery; a replay must be observable.
      const target = await receiver(saved.port)
      const repository = await PrivateCiphertextRepository.open(location())
      const binding = saved.binding
      assert.deepEqual(await createElectronCredentialBoundary(repository).read(binding.ref), {
        ...binding,
        secret: forbidden[0],
      })
      const audit = await PersistentGatewayAudit.open(location())
      const entries = await audit.readEntries()
      assert.equal(entries.length, 1)
      const gateway = new ModelGatewayCore(
        createElectronCredentialBoundary(repository),
        audit,
        'loopback-probe-only',
      )
      // Constructing real gateway + recovering durable intent must never invoke a request.
      await new Promise((resolve) => setTimeout(resolve, 100))
      assert.equal(target.count(), 0)
      assert.deepEqual(await audit.readEntries(), entries)
      gateway.closeProject(randomUUID())
      evidence.postCount = target.count()
      await target.close()
      await Promise.all([audit.close(), repository.close()])
      evidence.privateFileCount = await scanPrivate(path.join(userData, 'model-gateway-private-v1'))
      evidence.assertions.push(
        'second-electron-process-private-recovery',
        'durable-audit-recovery-no-replay-original-endpoint-observed',
      )
    } else if (['basic', 'unavailable'].includes(mode)) {
      const probeLocation = location('/probe-data/rejected-' + mode)
      const repository = await PrivateCiphertextRepository.open(probeLocation)
      await assert.rejects(
        createElectronCredentialBoundary(repository).store(randomUUID(), forbidden[0]),
        /^Error: CREDENTIAL_UNAVAILABLE$/,
      )
      assert.deepEqual(await repository.listBindings(), [])
      await repository.close()
      const files = await fs.readdir(
        path.join(probeLocation.userDataPath, 'model-gateway-private-v1', 'credentials'),
      )
      assert.deepEqual(files, [])
      if (mode === 'basic') assert.equal(evidence.backend, 'basic_text')
      else assert.equal(evidence.available, false)
      evidence.assertions.push('insecure-or-unavailable-zero-real-credential-files')
    } else if (['corrupt', 'key-loss'].includes(mode)) {
      const { binding } = JSON.parse(await fs.readFile(bindingFile, 'utf8'))
      let probeLocation = location()
      if (mode === 'corrupt') {
        const copy = '/probe-data/corrupt-userdata'
        await fs.cp(userData, copy, { recursive: true })
        probeLocation = location(copy)
        const filename = path.join(
          copy,
          'model-gateway-private-v1',
          'credentials',
          binding.ref + '.credential',
        )
        const envelope = JSON.parse(await fs.readFile(filename, 'utf8'))
        const payload = {
          format: envelope.format,
          binding: envelope.binding,
          ciphertext: Buffer.from('synthetic-invalid-os-ciphertext').toString('base64'),
        }
        const digest = createHash('sha256').update(JSON.stringify(payload)).digest('hex')
        await fs.writeFile(filename, JSON.stringify({ ...payload, digest }))
      }
      const repository = await PrivateCiphertextRepository.open(probeLocation)
      await assert.rejects(
        createElectronCredentialBoundary(repository).read(binding.ref),
        /^Error: CREDENTIAL_UNAVAILABLE$/,
      )
      await repository.close()
      evidence.assertions.push(
        mode === 'corrupt'
          ? 'valid-storage-envelope-invalid-real-os-ciphertext-denied'
          : 'actual-new-keyring-private-credential-recovery-denied',
      )
    } else throw new Error('invalid combination probe mode')
    evidence.result = 'passed'
    await fs.writeFile(
      `/probe-data/combination-results/${mode}.json`,
      JSON.stringify(evidence, null, 2) + '\n',
    )
    console.log(
      JSON.stringify({
        mode,
        result: evidence.result,
        assertions: evidence.assertions,
        postCount: evidence.postCount,
      }),
    )
    app.exit(0)
  })
  .catch(async () => {
    evidence.result = 'failed'
    await fs.writeFile(
      `/probe-data/combination-results/${mode}.json`,
      JSON.stringify(evidence, null, 2) + '\n',
    )
    console.error(JSON.stringify({ mode, result: 'failed' }))
    app.exit(1)
  })
