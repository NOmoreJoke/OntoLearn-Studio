import { describe, expect, it } from 'vitest'
import { randomUUID } from 'node:crypto'
import {
  matchesBusiness3Response,
  validateBusiness3,
  validateV2,
} from '../../packages/contracts/src/v2'

const projectId = randomUUID(),
  other = randomUUID(),
  operationId = randomUUID()
const hash = 'a'.repeat(64)
const item = {
  projectId,
  domainRevision: 0,
  metadataVersion: 1,
  operationSequence: 1,
  checkpointRef: hash,
  metadata: { name: '项目', mode: 'guided', archived: false, templateRef: null, origin: 'created' },
  lifecycle: { state: 'active', version: 0 },
}
function pair(method: string, params: unknown, result: unknown) {
  const request = {
    kind: 'request',
    protocolVersion: 3,
    id: randomUUID(),
    engineSessionId: randomUUID(),
    method,
    params,
  }
  const response = {
    kind: 'response',
    protocolVersion: 3,
    id: request.id,
    engineSessionId: request.engineSessionId,
    method,
    ok: true,
    result,
  }
  return { request, response }
}
const cases = {
  'project.management.catalog': { state: 'active', pageSize: 10, cursor: null },
  'project.management.read': { projectId },
  'project.management.preview': {
    projectId,
    action: { kind: 'rename', name: '新名称' },
    expectedCheckpointRef: hash,
    expectedLifecycleVersion: 0,
  },
  'project.management.confirm': { projectId, previewRef: randomUUID(), documentHash: hash },
  'project.management.apply': {
    projectId,
    operationId,
    confirmationRef: randomUUID(),
    documentHash: hash,
  },
  'project.management.operation.get': { projectId, operationId, requestHash: hash },
  'project.library.status': {},
}
describe('B1a finite management wire boundaries', () => {
  for (const [method, params] of Object.entries(cases))
    it(`${method} rejects old protocol, extra keys, and caller transport authority`, () => {
      const { request } = pair(method, params, null)
      expect(validateBusiness3('request', request)).toBe(true)
      expect(validateV2('request', { ...request, protocolVersion: 2 })).toBe(false)
      expect(
        validateBusiness3('request', {
          ...request,
          params: { ...params, path: '/tmp/other.sqlite' },
        }),
      ).toBe(false)
      expect(validateBusiness3('request', { ...request, sessionAuthority: randomUUID() })).toBe(
        false,
      )
    })
  it('catalog pages bind filter, unique IDs and honest remaining counts', () => {
    const { request, response } = pair(
      'project.management.catalog',
      cases['project.management.catalog'],
      {
        catalogVersion: 1,
        snapshotId: randomUUID(),
        items: [item],
        total: 1,
        offset: 0,
        nextCursor: null,
      },
    )
    expect(matchesBusiness3Response(request, response, hash)).toBe(true)
    const base = response.result as Record<string, unknown>
    for (const result of [
      { ...base, items: [item, item], total: 2 },
      { ...base, items: [{ ...item, metadata: { ...item.metadata, archived: true } }] },
      { ...base, items: [{ ...item, lifecycle: { state: 'trashed', version: 1 } }] },
      { ...base, total: 2 },
      { ...base, nextCursor: randomUUID() },
    ])
      expect(matchesBusiness3Response(request, { ...response, result }, hash)).toBe(false)
    expect(
      matchesBusiness3Response(request, { ...response, engineSessionId: randomUUID() }, hash),
    ).toBe(false)
  })
  it('reconciliation binds original project, operation and request hash even after trash', () => {
    const result = {
      managementResultVersion: 1,
      kind: 'trash',
      projectId,
      operationId,
      targetProjectId: projectId,
      requestHash: hash,
      receiptHash: hash,
      checkpointRef: hash,
      domainRevision: 1,
      metadataVersion: 1,
      operationSequence: 2,
      lifecycleVersion: 1,
      lifecycleState: 'trashed',
    }
    const { request, response } = pair(
      'project.management.operation.get',
      cases['project.management.operation.get'],
      { state: 'applied', result },
    )
    expect(matchesBusiness3Response(request, response, hash)).toBe(true)
    for (const changed of [
      { projectId: other },
      { operationId: other },
      { requestHash: 'b'.repeat(64) },
      { targetProjectId: other },
    ]) {
      expect(
        matchesBusiness3Response(
          request,
          { ...response, result: { state: 'applied', result: { ...result, ...changed } } },
          hash,
        ),
      ).toBe(false)
    }
    expect(
      matchesBusiness3Response(
        request,
        { ...response, result: { state: 'not-found', result: null } },
        hash,
      ),
    ).toBe(true)
    expect(
      matchesBusiness3Response(
        request,
        { ...response, result: { state: 'not-found', result } },
        hash,
      ),
    ).toBe(false)
  })
  it('actions are finite and do not accept arbitrary metadata, patches or professional mode', () => {
    for (const action of [
      { kind: 'patch', patch: {} },
      { kind: 'rename', name: '' },
      { kind: 'trash', force: true },
      { kind: 'set-mode', mode: 'professional' },
      { kind: 'archive', archived: 'true' },
    ]) {
      expect(validateBusiness3('management.action', action)).toBe(false)
    }
  })
})
