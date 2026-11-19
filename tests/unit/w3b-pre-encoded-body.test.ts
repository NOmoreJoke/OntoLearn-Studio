import { randomUUID } from 'node:crypto'
import { mkdtemp, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
  encodeChatRequest,
} from '../../apps/desktop/src/main/agent/deepseek-codec'
import { ConfigurationRepository } from '../../apps/desktop/src/main/model-gateway/configuration-repository'
import {
  ModelGatewayCore,
  type AuditRecord,
} from '../../apps/desktop/src/main/model-gateway/gateway'
import {
  MAX_BODY_BYTES,
  type ApprovedBodyRequest,
} from '../../apps/desktop/src/main/model-gateway/pre-encoded-body'
import {
  ModelGatewayService,
  type AgentProviderApproval,
} from '../../apps/desktop/src/main/model-gateway/model-service'
import type { EncryptedCredentialBoundary } from '../../apps/desktop/src/main/model-gateway/credentials'
import type { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { sendOnce } from '../../apps/desktop/src/main/model-gateway/transport'

vi.mock('../../apps/desktop/src/main/model-gateway/transport', () => ({ sendOnce: vi.fn() }))
const transport = vi.mocked(sendOnce)
const sent: string[] = []
const cleanup: Array<() => Promise<unknown>> = []
beforeEach(() => {
  sent.length = 0
  transport.mockReset().mockImplementation(async (_endpoint, _secret, body, _signal, guard) => {
    guard()
    sent.push(body)
    return { status: 200, body: 'synthetic response' }
  })
})
afterEach(async () => {
  for (const action of cleanup.splice(0).reverse()) await action()
})

function envelope(question = '用户明确选择的内容') {
  return encodeChatRequest({
    messages: [
      { role: 'system', content: 'Return JSON.' },
      { role: 'user', content: question },
    ],
    mode: 'disabled',
    effort: 'low',
    availableTools: ['ontology_read'],
    maxTokens: 10,
  })
}
function fixture(append?: (record: AuditRecord) => Promise<void>) {
  const secret = 'SYNTHETIC_SECRET'
  const credential = { ref: randomUUID(), principal: randomUUID(), version: randomUUID(), secret }
  const records: AuditRecord[] = []
  const core = new ModelGatewayCore(
    { read: async () => credential },
    {
      append:
        append ??
        (async (record) => {
          records.push(record)
        }),
    },
  )
  const projectId = randomUUID()
  const config = {
    id: randomUUID(),
    endpoint: 'https://synthetic.invalid/chat/completions',
    credentialRef: credential.ref,
    principal: credential.principal,
    credentialVersion: credential.version,
    model: envelope().model,
  }
  const { version } = core.configure(config)
  core.setPrivacy(projectId, 'project')
  const scopes = [randomUUID()]
  const preview = core.previewAuthorization({
    projectId,
    configId: config.id,
    purpose: 'suggest',
    scopes,
  })
  const grantId = core.confirmAuthorization(preview.previewId)
  function part(path: string, kind: ApprovedBodyRequest['parts'][number]['kind'], text: string) {
    return { path, kind, materialId: core.registerMaterial({ kind, text, scopes, projectId }) }
  }
  function request(question = '用户明确选择的内容'): ApprovedBodyRequest {
    return {
      projectId,
      configId: config.id,
      purpose: 'suggest',
      scopes,
      grantId,
      configVersion: version,
      body: JSON.stringify(envelope(question), null, 2),
      parts: [
        part('messages.0.content', 'history', 'Return JSON.'),
        part('messages.1.content', 'selected', question),
      ],
    }
  }
  return { core, records, config, credential, secret, request, part }
}

describe('I06 approved final body', () => {
  it('writes the exact bytes and the same metadata shape as the existing parts path', async () => {
    const { core, request, secret, records } = fixture()
    const input = request()
    await expect(core.invokeApprovedBody(input)).resolves.toEqual({
      ok: true,
      text: 'synthetic response',
    })
    expect(transport).toHaveBeenCalledWith(
      expect.any(String),
      secret,
      input.body,
      expect.any(AbortSignal),
      expect.any(Function),
    )
    expect(sent).toEqual([input.body])
    const { configId, projectId, purpose, grantId } = input
    await expect(
      core.invoke({
        configId,
        projectId,
        purpose,
        grantId,
        materials: input.parts.map(({ materialId }) => materialId),
      }),
    ).resolves.toMatchObject({ ok: true })
    expect(records).toHaveLength(2)
    expect(records[0]).toEqual({ ...records[1], time: records[0].time })
    expect(records[0]).toMatchObject({
      event: 'attempt-intent',
      decision: 'authorized',
      purpose: 'suggest',
    })
    expect(JSON.stringify(records)).not.toContain(secret)
    expect(JSON.stringify(records)).not.toContain('用户明确选择的内容')
  })

  it.each([
    'system',
    'user',
    'assistant',
    'reasoning',
    'arguments',
    'tool-result',
    'tool-call-id',
    'unknown',
    'tool-schema',
    'duplicate-key',
    'wrong-source',
    'scope',
  ] as const)('rejects uncovered or unauthorized %s before transport', async (mutation) => {
    const { core, request, part } = fixture()
    const input = request()
    const payload = envelope()
    const secret = 'UNREGISTERED_IMPORTED_TEXT'
    switch (mutation) {
      case 'system':
        payload.messages[0].content += secret
        break
      case 'user':
        payload.messages[1].content += secret
        break
      case 'assistant':
        payload.messages.push({ role: 'assistant', content: secret })
        break
      case 'reasoning':
        payload.messages.push({ role: 'assistant', content: null, reasoning_content: secret })
        break
      case 'arguments':
        payload.messages.push({
          role: 'assistant',
          content: null,
          tool_calls: [
            {
              id: 'call-1',
              type: 'function',
              function: {
                name: 'ontology_read',
                arguments: JSON.stringify({ objectIds: [secret] }),
              },
            },
          ],
        })
        input.parts.push(part('messages.2.tool_calls.0.id', 'history', 'call-1'))
        break
      case 'tool-result':
        payload.messages.push({ role: 'tool', tool_call_id: 'call-1', content: secret })
        input.parts.push(part('messages.2.tool_call_id', 'tool', 'call-1'))
        break
      case 'tool-call-id':
        payload.messages.push({ role: 'tool', tool_call_id: secret, content: '{}' })
        input.parts.push(part('messages.2.content', 'tool', '{}'))
        break
      case 'unknown':
        Object.assign(payload, { extra: secret })
        break
      case 'tool-schema':
        payload.tools![0].function.description += secret
        break
      case 'wrong-source':
        input.parts[1] = part('messages.1.content', 'history', payload.messages[1].content!)
        break
      case 'scope':
        input.scopes = [randomUUID()]
        break
    }
    input.body = JSON.stringify(payload)
    if (mutation === 'duplicate-key')
      input.body = input.body.replace('"role":"user"', '"content":"hidden","role":"user"')
    await expect(core.invokeApprovedBody(input)).resolves.toEqual({
      ok: false,
      code: 'SCOPE_EXCEEDED',
    })
    expect(transport).not.toHaveBeenCalled()
  })

  it('covers every dynamic value, including the nested tool arguments and result', async () => {
    const { core, request, part } = fixture()
    const input = request()
    const payload = envelope()
    const args = '{"objectIds":["item-001"]}'
    payload.messages.push(
      {
        role: 'assistant',
        content: '经批准的摘要',
        reasoning_content: '经确认的思考',
        tool_calls: [
          { id: 'call-1', type: 'function', function: { name: 'ontology_read', arguments: args } },
        ],
      },
      { role: 'tool', content: '{"fields":[]}', tool_call_id: 'call-1' },
    )
    input.parts.push(
      part('messages.2.content', 'summary', '经批准的摘要'),
      part('messages.2.reasoning_content', 'history', '经确认的思考'),
      part('messages.2.tool_calls.0.id', 'history', 'call-1'),
      part('messages.2.tool_calls.0.function.arguments', 'history', args),
      part('messages.3.content', 'error', '{"fields":[]}'),
      part('messages.3.tool_call_id', 'tool', 'call-1'),
    )
    input.body = JSON.stringify(payload)
    await expect(core.invokeApprovedBody(input)).resolves.toMatchObject({ ok: true })
    expect(sent).toEqual([input.body])
  })

  it('counts UTF-8 bytes at the exact boundary', async () => {
    const { core, request } = fixture()
    const input = request()
    const pad = MAX_BODY_BYTES - Buffer.byteLength(input.body)
    input.body = ' '.repeat(pad) + input.body
    await expect(core.invokeApprovedBody(input)).resolves.toMatchObject({ ok: true })
    await expect(core.invokeApprovedBody({ ...input, body: input.body + ' ' })).resolves.toEqual({
      ok: false,
      code: 'INVALID_INPUT',
    })
    expect(sent).toHaveLength(1)
  })

  it('preserves generated Unicode and escapes while rejecting any changed value', async () => {
    const { core, request } = fixture()
    const alphabet = ['水', '🎛', '\u0000', '\\', '"', '\t', 'A', 'e\u0301']
    let seed = 1776
    for (let sample = 0; sample < 48; sample++) {
      const value = Array.from({ length: 1 + sample }, () => {
        seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0
        return alphabet[(seed >>> 16) % alphabet.length]
      }).join('')
      const input = request(value)
      await expect(core.invokeApprovedBody(input)).resolves.toMatchObject({ ok: true })
      expect(sent.at(-1)).toBe(input.body)
      await expect(
        core.invokeApprovedBody({ ...input, body: JSON.stringify(envelope(value + '变')) }),
      ).resolves.toEqual({ ok: false, code: 'SCOPE_EXCEEDED' })
    }
    expect(sent).toHaveLength(48)
  })

  it('never calls transport when the durable attempt-intent fails', async () => {
    const { core, request } = fixture(async () => {
      throw new Error('private-path-or-secret')
    })
    await expect(core.invokeApprovedBody(request())).resolves.toEqual({
      ok: false,
      code: 'AUDIT_UNAVAILABLE',
    })
    expect(transport).not.toHaveBeenCalled()
  })

  it.each(['local', 'revoke', 'configuration', 'cancel', 'stale'] as const)(
    'the transport final guard blocks a %s race after intent',
    async (change) => {
      const { core, config, request, records } = fixture()
      const input = request()
      const signal = new AbortController()
      let current = true
      transport.mockImplementationOnce(async (_endpoint, _secret, body, _signal, guard) => {
        expect(records[0]?.event).toBe('attempt-intent')
        if (change === 'local') core.setPrivacy(input.projectId, 'local')
        if (change === 'revoke') core.revokeAuthorization(input.grantId)
        if (change === 'configuration')
          core.configure({ ...config, endpoint: config.endpoint + '/new' })
        if (change === 'cancel') signal.abort()
        if (change === 'stale') current = false
        guard()
        sent.push(body)
        return { status: 200, body: '' }
      })
      const code = {
        local: 'LOCAL_ONLY',
        revoke: 'AUTHORIZATION_REQUIRED',
        configuration: 'CONFIGURATION_CHANGED',
        cancel: 'CANCELLED',
        stale: 'CANCELLED',
      }[change]
      await expect(core.invokeApprovedBody(input, signal.signal, () => current)).resolves.toEqual({
        ok: false,
        code,
      })
      expect(sent).toHaveLength(0)
      expect(records.at(-1)).toMatchObject({ event: 'blocked', reason: code })
    },
  )

  it('rejects local mode before looking up materials or sending', async () => {
    const { core, request } = fixture()
    const input = request()
    core.setPrivacy(input.projectId, 'local')
    await expect(
      core.invokeApprovedBody({ ...input, parts: [], body: 'invalid' }),
    ).resolves.toEqual({ ok: false, code: 'LOCAL_ONLY' })
    expect(transport).not.toHaveBeenCalled()
  })

  it('keeps public configuration versions separate from the gateway config versions', async () => {
    const { core, request, config, credential } = fixture()
    const input = request()
    const root = await mkdtemp(join(process.cwd(), 'build', 'w3b-configuration-'))
    cleanup.push(() => rm(root, { recursive: true, force: true }))
    const repository = await ConfigurationRepository.open({
      userDataPath: join(root, 'app'),
      excludedRoots: [join(root, 'store')],
    })
    cleanup.push(() => repository.close())
    const original = {
      configurationId: config.id,
      configurationVersion: randomUUID(),
      displayName: 'Synthetic',
      endpoint: config.endpoint,
      model: config.model,
      binding: {
        ref: credential.ref,
        principal: credential.principal,
        version: credential.version,
      },
    }
    await repository.replace([], [original])
    const service = await ModelGatewayService.open({
      engine: {} as EngineSupervisor,
      repository,
      credentials: { read: async () => credential } as unknown as EncryptedCredentialBoundary,
      audit: { append: async () => {} },
    })
    cleanup.push(() => service.close())
    expect(service.listConfigurationSummaries()[0].enabled).toBe(true)
    expect(service.probeCapabilities(config.id)).toEqual({
      connection: 'not-run',
      structuredOutput: 'passed',
      toolRoundTrip: 'passed',
      mode: 'synthetic',
    })
    const disabled = await service.setConfigurationEnabled(config.id, false)
    expect(disabled.enabled).toBe(false)
    const enabled = await service.setConfigurationEnabled(config.id, true)
    const { version } = core.configure({ ...config, endpoint: config.endpoint + '/new' })
    expect(
      new Set([
        original.configurationVersion,
        enabled.configurationVersion,
        input.configVersion,
        version,
      ]).size,
    ).toBe(4)
    for (const configVersion of [input.configVersion, enabled.configurationVersion]) {
      await expect(core.invokeApprovedBody({ ...input, configVersion })).resolves.toEqual({
        ok: false,
        code: 'CONFIGURATION_CHANGED',
      })
    }
    await expect(core.invokeApprovedBody({ ...input, configVersion: version })).resolves.toEqual({
      ok: false,
      code: 'AUTHORIZATION_REQUIRED',
    })
    expect(transport).not.toHaveBeenCalled()
    await service.removeConfiguration(config.id)
    expect(await repository.load()).toEqual([])
  })
  it('requires exact main approval, rejects a revoked configuration across awaits, and stamps the internal version', async () => {
    const { credential } = fixture()
    const root = await mkdtemp(join(process.cwd(), 'build', 'w3b-approved-'))
    cleanup.push(() => rm(root, { recursive: true, force: true }))
    const repository = await ConfigurationRepository.open({
      userDataPath: join(root, 'app'),
      excludedRoots: [join(root, 'store')],
    })
    cleanup.push(() => repository.close())
    const configurationId = randomUUID()
    const configurationVersion = randomUUID()
    await repository.replace(
      [],
      [
        {
          configurationId,
          configurationVersion,
          displayName: 'Synthetic only',
          endpoint: DEEPSEEK_ENDPOINT,
          model: REQUEST_MODEL,
          binding: {
            ref: credential.ref,
            principal: credential.principal,
            version: credential.version,
          },
        },
      ],
    )
    const records: AuditRecord[] = []
    const service = await ModelGatewayService.open({
      engine: {} as EngineSupervisor,
      repository,
      credentials: { read: async () => credential } as unknown as EncryptedCredentialBoundary,
      audit: {
        append: async (record) => {
          records.push(record)
        },
      },
    })
    cleanup.push(() => service.close())
    const projectId = randomUUID()
    service.selectProject(projectId)
    const contextId = service.status().contextId!
    service.setPrivacy({ contextId, privacy: 'project' })
    const input = { projectId, purpose: 'suggest' as const, body: JSON.stringify(envelope()) }
    const signal = new AbortController()
    const confirmBody = vi.fn<AgentProviderApproval['confirmBody']>().mockResolvedValue(false)
    const approval: AgentProviderApproval = {
      configurationId,
      configurationVersion,
      confirmBody,
      signature: {
        endpoint: DEEPSEEK_ENDPOINT,
        requestedModel: REQUEST_MODEL,
        returnedModel: REQUEST_MODEL,
        fingerprint: null,
        mode: 'disabled',
        effort: 'low',
        codecVersion: CODEC_VERSION,
      },
    }
    const invoke = (selected = approval, cancellation = signal.signal) =>
      service.invokeAgentBody(input, selected, cancellation, () => true)
    await expect(invoke()).rejects.toThrow('AUTHORIZATION_REQUIRED')
    expect(transport).not.toHaveBeenCalled()

    confirmBody.mockResolvedValueOnce(true)
    await expect(invoke()).resolves.toBe('synthetic response')
    expect(confirmBody.mock.calls.at(-1)?.[0]).toMatchObject({
      body: input.body,
      endpoint: DEEPSEEK_ENDPOINT,
      projectId,
      configurationId,
    })
    expect(records[0].configVersion).toBe(confirmBody.mock.calls.at(-1)?.[0].configVersion)
    expect(records[0].configVersion).not.toBe(configurationVersion)

    let approve!: (value: boolean) => void
    confirmBody.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          approve = resolve
        }),
    )
    const stale = invoke()
    const rejected = expect(stale).rejects.toThrow('AUTHORIZATION_REQUIRED')
    await Promise.resolve()
    await service.setConfigurationEnabled(configurationId, false)
    const enabled = await service.setConfigurationEnabled(configurationId, true)
    approve(true)
    await rejected
    expect(sent).toEqual([input.body])
    expect(enabled.configurationVersion).not.toBe(configurationVersion)

    confirmBody.mockResolvedValueOnce(true)
    const updated = { ...approval, configurationVersion: enabled.configurationVersion }
    await expect(invoke(updated)).resolves.toBe('synthetic response')
    expect(
      new Set([
        configurationVersion,
        enabled.configurationVersion,
        records[0].configVersion,
        records[1].configVersion,
      ]).size,
    ).toBe(4)

    const cancelled = new AbortController()
    confirmBody.mockImplementationOnce(() => new Promise(() => {}))
    const waiting = invoke(updated, cancelled.signal)
    const aborted = expect(waiting).rejects.toThrow('CANCELLED')
    await Promise.resolve()
    cancelled.abort()
    await aborted
    expect(sent).toHaveLength(2)
  })
})
