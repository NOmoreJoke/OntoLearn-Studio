import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { AgentSession } from '../../apps/desktop/src/main/agent/agent-service'
import { assessCapabilities } from '../../apps/desktop/src/main/agent/capabilities'
import cases from '../fixtures/agent/synthetic-cases.v1.json'
import manifest from '../fixtures/agent/manifest.v1.json'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
} from '../../apps/desktop/src/main/agent/deepseek-codec'
import type { ToolName } from '../../apps/desktop/src/main/agent/tools'

const signature = {
  endpoint: DEEPSEEK_ENDPOINT,
  requestedModel: REQUEST_MODEL,
  returnedModel: 'synthetic-deepseek-v4-pro',
  fingerprint: 'synthetic-v1',
  mode: 'enabled',
  effort: 'high',
  codecVersion: CODEC_VERSION,
}
const hash = 'a'.repeat(64)
const probe = {
  source: 'provider',
  testedAt: '2026-10-21T00:00:00Z',
  signature,
  connection: 'passed',
  structuredOutput: 'passed',
  toolRoundTrip: 'passed',
  evaluation: {
    manifestHash: hash,
    completed: true,
    fabricatedResults: 0,
    allFailuresLocated: true,
    allRequirementsPassed: true,
  },
}

describe('T08 versioned synthetic evaluation: no provider or deterministic domain execution', () => {
  it('pins exact fixture bytes and the complete ordered case set', () => {
    const bytes = readFileSync(
      new URL('../fixtures/agent/synthetic-cases.v1.json', import.meta.url),
    )
    expect(createHash('sha256').update(bytes).digest('hex')).toBe(manifest.sha256)
    expect(cases.map((item) => item.id)).toEqual(manifest.caseIds)
    expect(manifest.providerAcceptance).toBe('not-run')
  })
  it.each(cases)('$id has complete fixed input and expected receipt/error', async (item) => {
    const session = new AgentSession(item.context, {
      [item.call.function.name as ToolName]: { execute: async () => item.adapterOutcome },
    })
    if (item.execute)
      await session.executeCalls([item.call], () => item.context, new AbortController().signal)
    if ('error' in item.expected) {
      expect(() => session.resolveAnswer(item.answer, item.context)).toThrow(item.expected.error)
    } else {
      expect(session.resolveAnswer(item.answer, item.context)).toEqual(item.expected)
    }
  })
  it('keeps connection, JSON, tool and quality gates distinct, synthetic never becomes ready', () => {
    expect(assessCapabilities({ ...probe, source: 'synthetic' }, signature, hash).state).toBe(
      'synthetic-only',
    )
    expect(
      assessCapabilities(
        { ...probe, structuredOutput: 'not-run', toolRoundTrip: 'not-run' },
        signature,
        hash,
      ),
    ).toMatchObject({
      state: 'capability-incomplete',
      connection: 'passed',
      structuredOutput: 'not-run',
      toolRoundTrip: 'not-run',
    })
    expect(assessCapabilities({ ...probe, evaluation: null }, signature, hash).state).toBe(
      'evaluation-required',
    )
    expect(
      assessCapabilities(
        { ...probe, evaluation: { ...probe.evaluation, fabricatedResults: 1 } },
        signature,
        hash,
      ).state,
    ).toBe('evaluation-required')
    expect(assessCapabilities(probe, signature, hash).state).toBe('ready')
  })
  it.each(['returnedModel', 'fingerprint', 'mode', 'effort'] as const)(
    'requires new evaluation for %s drift',
    (field) => {
      const changed = {
        ...signature,
        [field]: field === 'mode' ? 'disabled' : field === 'effort' ? 'max' : 'changed',
      }
      expect(assessCapabilities({ ...probe, signature: changed }, signature, hash).state).toBe(
        'drift-requires-evaluation',
      )
    },
  )
  it('rejects endpoint changes and wrong manifests or arbitrary response fields', () => {
    expect(() =>
      assessCapabilities(
        { ...probe, signature: { ...signature, endpoint: 'https://evil.example' } },
        signature,
        hash,
      ),
    ).toThrow('INVALID_PROTOCOL')
    expect(assessCapabilities(probe, signature, 'b'.repeat(64)).state).toBe('evaluation-required')
    expect(() => assessCapabilities({ ...probe, key: 'hidden' }, signature, hash)).toThrow(
      'INVALID_PROTOCOL',
    )
  })
})
