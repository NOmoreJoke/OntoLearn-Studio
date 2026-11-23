import fs from 'node:fs/promises'
import http from 'node:http'
import os from 'node:os'
import path from 'node:path'
import { randomUUID } from 'node:crypto'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ModelGatewayCore } from '../../apps/desktop/src/main/model-gateway/gateway'
import { PersistentGatewayAudit } from '../../apps/desktop/src/main/model-gateway/persistent-audit'
import {
  PrivateOperations,
  type PrivateWriteObserver,
  type PrivateWritePhase,
} from '../../apps/desktop/src/main/model-gateway/private-directory'

const roots: string[] = []
const audits: PersistentGatewayAudit[] = []
const servers: http.Server[] = []
afterEach(async () => {
  vi.restoreAllMocks()
  await Promise.all(audits.splice(0).map((audit) => audit.close()))
  await Promise.all(
    servers.splice(0).map(
      (server) =>
        new Promise<void>((resolve) => {
          server.closeAllConnections()
          server.close(() => resolve())
        }),
    ),
  )
  await Promise.all(roots.splice(0).map((root) => fs.rm(root, { recursive: true, force: true })))
})
function deferred() {
  let resolve!: () => void
  const promise = new Promise<void>((done) => {
    resolve = done
  })
  return { promise, resolve }
}
async function fixture(observer?: PrivateWriteObserver) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'i06-persist-gateway-'))
  roots.push(root)
  const location = {
    userDataPath: path.join(root, 'app'),
    excludedRoots: [path.join(root, 'project')],
  }
  const audit = await PersistentGatewayAudit.open(location, observer)
  audits.push(audit)
  const received: string[] = []
  const server = http.createServer((request, response) => {
    let body = ''
    request.on('data', (chunk) => {
      body += chunk
    })
    request.on('end', () => {
      received.push(body)
      response.end('synthetic-only')
    })
  })
  servers.push(server)
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve))
  const address = server.address()
  if (!address || typeof address === 'string') throw new Error('receiver')
  const credential = {
    ref: randomUUID(),
    principal: randomUUID(),
    version: randomUUID(),
    secret: 'SYNTHETIC_KEY_ONLY',
  }
  const gateway = new ModelGatewayCore(
    { read: async () => credential },
    audit,
    'loopback-probe-only',
  )
  const projectId = randomUUID()
  const scopes = [randomUUID()]
  const config = {
    id: randomUUID(),
    endpoint: `http://127.0.0.1:${address.port}/probe`,
    credentialRef: credential.ref,
    principal: credential.principal,
    credentialVersion: credential.version,
    model: 'synthetic',
  }
  gateway.configure(config)
  gateway.setPrivacy(projectId, 'minimal')
  const material = gateway.registerMaterial({
    projectId,
    scopes,
    kind: 'selected',
    text: 'SYNTHETIC_BUSINESS_ONLY',
  })
  const preview = gateway.previewAuthorization({
    projectId,
    configId: config.id,
    purpose: 'explain',
    scopes,
  })
  const grantId = gateway.confirmAuthorization(preview.previewId)
  const invocation = {
    projectId,
    configId: config.id,
    grantId,
    purpose: 'explain',
    materials: [material],
  }
  return { root, location, audit, received, gateway, projectId, invocation }
}

describe('I06 real private audit at the final egress gate', () => {
  it('sends once after durable audit and restores metadata without replay', async () => {
    const f = await fixture()
    expect(await f.gateway.invoke(f.invocation)).toEqual({ ok: true, text: 'synthetic-only' })
    expect(f.received).toHaveLength(1)
    await f.audit.close()
    const restored = await PersistentGatewayAudit.open(f.location)
    audits.push(restored)
    expect((await restored.readEntries()).map(({ record }) => record.event)).toEqual([
      'attempt-intent',
    ])
    const names = await fs.readdir(
      path.join(f.location.userDataPath, 'model-gateway-private-v1', 'audit'),
    )
    for (const name of names) {
      const raw = await fs.readFile(
        path.join(f.location.userDataPath, 'model-gateway-private-v1', 'audit', name),
        'utf8',
      )
      expect(raw).not.toContain('SYNTHETIC_BUSINESS_ONLY')
      expect(raw).not.toContain('SYNTHETIC_KEY_ONLY')
    }
    expect(f.received).toHaveLength(1)
  })

  it.each<PrivateWritePhase>([
    'partial-written',
    'temp-written',
    'file-synced',
    'published',
    'temp-unlinked',
    'directory-synced',
  ])('blocks every request when an injected persistence failure occurs at %s', async (phase) => {
    const f = await fixture((current) => {
      if (current === phase)
        throw Object.assign(new Error('synthetic storage fault'), { code: 'EIO' })
    })
    expect(await f.gateway.invoke(f.invocation)).toEqual({ ok: false, code: 'AUDIT_UNAVAILABLE' })
    expect(f.received).toHaveLength(0)
    const entries = await f.audit.readEntries()
    expect(entries).toHaveLength(
      ['published', 'temp-unlinked', 'directory-synced'].includes(phase) ? 1 : 0,
    )
  })

  it.each(['ENOSPC', 'EIO'])(
    'blocks egress on an actual filesystem call rejecting with injected %s',
    async (code) => {
      const f = await fixture()
      if (code === 'ENOSPC') {
        const original = fs.open.bind(fs)
        vi.spyOn(fs, 'open').mockImplementation(async (...args: Parameters<typeof fs.open>) => {
          if (String(args[0]).includes('.pending-'))
            throw Object.assign(new Error('synthetic'), { code })
          return original(...args)
        })
      } else vi.spyOn(fs, 'link').mockRejectedValue(Object.assign(new Error('synthetic'), { code }))
      expect(await f.gateway.invoke(f.invocation)).toEqual({ ok: false, code: 'AUDIT_UNAVAILABLE' })
      expect(f.received).toHaveLength(0)
      expect(await f.audit.readEntries()).toEqual([])
    },
  )

  it('rechecks local-only after a real audit has published but before acknowledging it', async () => {
    const entered = deferred()
    const release = deferred()
    let first = true
    const f = await fixture(async (phase) => {
      if (phase === 'published' && first) {
        first = false
        entered.resolve()
        await release.promise
      }
    })
    const running = f.gateway.invoke(f.invocation)
    await entered.promise
    f.gateway.setPrivacy(f.projectId, 'local')
    release.resolve()
    expect(await running).toEqual({ ok: false, code: 'LOCAL_ONLY' })
    expect(f.received).toHaveLength(0)
    expect((await f.audit.readEntries()).map(({ record }) => record.event).sort()).toEqual([
      'attempt-intent',
      'blocked',
    ])
  })

  it('does not send after an audit deadline even if the durable write completes later', async () => {
    const entered = deferred()
    const release = deferred()
    const finished = deferred()
    const f = await fixture(async (phase) => {
      if (phase === 'published') {
        entered.resolve()
        await release.promise
      }
      if (phase === 'directory-synced') finished.resolve()
    })
    try {
      const running = f.gateway.invoke(f.invocation)
      await entered.promise
      expect(await running).toEqual({ ok: false, code: 'AUDIT_UNAVAILABLE' })
      expect(f.received).toHaveLength(0)
    } finally {
      release.resolve()
    }
    await finished.promise
    expect(await f.audit.readEntries()).toHaveLength(1)
    expect(f.received).toHaveLength(0)
  }, 10000)

  it('rejects an oversized scope union before establishing incomplete audit metadata', async () => {
    const f = await fixture()
    f.invocation.materials = [0, 1].map(() =>
      f.gateway.registerMaterial({
        projectId: f.projectId,
        scopes: Array.from({ length: 256 }, () => randomUUID()),
        kind: 'selected',
        text: 'synthetic',
      }),
    )
    expect(await f.gateway.invoke(f.invocation)).toEqual({ ok: false, code: 'INVALID_INPUT' })
    expect(await f.audit.readEntries()).toEqual([])
    expect(f.received).toHaveLength(0)
  })

  it('bounds all private operations, including denied-request audit work, and drains accepted work on close', async () => {
    const operations = new PrivateOperations()
    const release = deferred()
    const pending = Array.from({ length: 32 }, () => operations.run(() => release.promise))
    await expect(operations.run(async () => {})).rejects.toThrow('PRIVATE_STORAGE_UNAVAILABLE')
    let closed = false
    const closing = operations.close(async () => {
      closed = true
    })
    await expect(operations.run(async () => {})).rejects.toThrow('PRIVATE_STORAGE_UNAVAILABLE')
    expect(closed).toBe(false)
    release.resolve()
    await Promise.all([...pending, closing])
    expect(closed).toBe(true)
  })
})
