import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { z } from 'zod'
import { AgentConversation } from '../../apps/desktop/src/main/agent/conversation'
import type { TrustedContext } from '../../apps/desktop/src/main/agent/agent-service'
import suite from '../fixtures/agent/fixed-input-cases.v2.json'
import originManifest from '../fixtures/agent/t09-873c8c0/origin-manifest.json'
import manifestV2 from '../fixtures/agent/manifest.v2.json'

const root = resolve(import.meta.dirname, '../..')
const inputs = resolve(root, 'tests/fixtures/agent/t09-873c8c0')
const sha = (text: string | Buffer) => createHash('sha256').update(text).digest('hex')
const digest = z.string().regex(/^[a-f0-9]{64}$/)
const baseFields = {
  probeVersion: z.literal('t08-fixed-rdflib-csv-1'),
  sourceCommit: z.literal('873c8c051b9870aa12fc7e1dbbd3e0c358e7c380'),
  manifestSha256: z.literal('aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e'),
  fixtureSha256: z.literal('306d41b332d223b47929eb90f196c71e4965a0e9ff81100c9469ed32612e8845'),
  rdflibVersion: z.literal('7.6.0'),
  caseId: z.string().min(1),
}
const queryFields = {
  ...baseFields,
  kind: z.literal('query'),
  inputSha256: digest,
  querySha256: digest,
  query: z.string(),
  scope: z.literal('current-asserted'),
}
const querySchema = z.discriminatedUnion('ok', [
  z
    .object({
      ...queryFields,
      ok: z.literal(true),
      variables: z.array(z.literal('alarm')),
      rows: z.array(z.object({ alarm: z.string().min(1) }).strict()),
    })
    .strict(),
  z
    .object({
      ...queryFields,
      ok: z.literal(false),
      code: z.enum(['QUERY_SYNTAX', 'QUERY_EXECUTION_FAILED']),
    })
    .strict(),
])
const csvSchema = z
  .object({
    ...baseFields,
    kind: z.literal('csv'),
    sourceSha256: digest,
    columns: z.tuple([z.literal('equipment_id'), z.literal('equipment_name')]),
    rows: z.array(
      z
        .object({
          sourceLine: z.number().int().min(2),
          equipment_id: z.string(),
          equipment_name: z.string(),
        })
        .strict(),
    ),
  })
  .strict()
function observe(caseId: string): unknown {
  const executable = resolve(
    root,
    process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python',
  )
  const result = spawnSync(
    executable,
    ['-I', resolve(root, 'tests/fixtures/agent/fixed-input-probe.py'), caseId],
    { encoding: 'utf8', timeout: 10000, maxBuffer: 1048576 },
  )
  expect(result.error).toBeUndefined()
  expect(result.status, result.stderr).toBe(0)
  return JSON.parse(result.stdout)
}
const observations = new Map(
  suite.queryCases.map((item) => [item.id, querySchema.parse(observe(item.id))]),
)
const csv = csvSchema.parse(observe('CSV-original'))

describe('T08 approved T09 fixed input: real library observations, not product adapters or provider', () => {
  it('retains exact approved bytes and version/PRD identity, without importing T09 helper or live HEAD', () => {
    expect(sha(readFileSync(resolve(inputs, 'origin-manifest.json')))).toBe(
      suite.originManifestSha256,
    )
    expect(sha(readFileSync(resolve(root, originManifest.source.path)))).toBe(
      originManifest.source.sha256,
    )
    for (const name of ['G-base.json', 'unclosed-high.rq', 'equipment.csv'] as const) {
      expect(sha(readFileSync(resolve(inputs, name)))).toBe(
        originManifest.files[`tests/fixtures/product-baselines/${name}`],
      )
    }
    expect(Object.keys(originManifest.files)).toHaveLength(17)
    for (const [file, expected] of Object.entries(manifestV2.files))
      expect(sha(readFileSync(resolve(inputs, '..', file)))).toBe(expected)
    expect(sha(readFileSync(resolve(inputs, '..', manifestV2.inherits.file)))).toBe(
      manifestV2.inherits.sha256,
    )
  })
  it.each(suite.queryCases)(
    '$id compares complete actual query output or precise syntax failure against the fixed oracle',
    (item) => {
      const observed = observations.get(item.id)!
      expect(observed.caseId).toBe(item.id)
      expect(observed.querySha256).toBe(sha(observed.query))
      if (!observed.ok) {
        expect(observed.code).toBe(item.expectedCode)
        expect(item.expectedSemanticMatch).toBe(false)
      } else {
        const actual = { variables: observed.variables, rows: observed.rows, scope: observed.scope }
        const matches = JSON.stringify(actual) === JSON.stringify(item.expected)
        expect(matches).toBe(item.expectedSemanticMatch)
        expect(observed.rows).toEqual(item.expectedObservedRows ?? item.expected?.rows)
        expect(observed.variables).toEqual(['alarm'])
      }
    },
  )
  it('keeps Q-01 and Q-02 input identities separate and catches the same-count wrong-A02 result', () => {
    const q1 = observations.get('Q-01')!,
      q2 = observations.get('Q-02')!,
      wrong = observations.get('Q-01-semantic-wrong')!
    expect(q1.inputSha256).not.toBe(q2.inputSha256)
    expect(wrong.inputSha256).toBe(q1.inputSha256)
    if (!q1.ok || !wrong.ok || !q2.ok) throw Error('probe unexpectedly failed')
    expect(q1.rows).toEqual([{ alarm: '<urn:ontolearn:learning:alarm/A01>' }])
    expect(q2.rows).toEqual([])
    expect(wrong.rows).toHaveLength(q1.rows.length)
    expect(wrong.rows).toEqual([{ alarm: '<urn:ontolearn:learning:alarm/A02>' }])
    expect(wrong.rows).not.toEqual(q1.rows)
  })
  it.each(suite.csvCandidateCases)(
    '$id grades sample consistency using actual CSV string identities/names',
    (item) => {
      const actual = csv.rows.map(({ equipment_id, equipment_name }) => ({
        equipment_id,
        equipment_name,
      }))
      expect(JSON.stringify(item.candidate) === JSON.stringify(actual)).toBe(
        item.expectedConsistent,
      )
      expect(csv.rows.map((row) => row.sourceLine)).toEqual([2, 3])
      expect(csv.rows.map((row) => row.equipment_id)).toEqual(['001', '002'])
    },
  )
  it('carries actual query rows through codec/session and preserves a semantic failure instead of inventing A01', async () => {
    const actual = observations.get('Q-01-semantic-wrong')!
    if (!actual.ok) throw Error('probe unexpectedly failed')
    const context: TrustedContext = {
      projectId: 'probe:p1',
      projectRevision: 1,
      inputSnapshotId: `probe:${actual.inputSha256}`,
      scopeRef: 'probe:asserted',
      module: 'query',
      mode: 'project',
      selectedObjectIds: [],
    }
    const fields = actual.rows.map((row, index) => ({
      fieldId: `alarm:${index}`,
      value: row.alarm,
    }))
    const observation = {
      kind: 'evidence',
      projectId: context.projectId,
      inputSnapshotId: context.inputSnapshotId,
      scopeRef: context.scopeRef,
      resultId: `probe:${actual.querySha256}`,
      status: 'current',
      traceRefs: [`probe:${actual.querySha256}`],
      fields,
    }
    // This test-only adapter returns the real fixed-input library observation, never oracle.expected.
    const conversation = new AgentConversation(
      context,
      '查询未闭环高危告警',
      {
        mode: 'enabled',
        effort: 'high',
        maxTokens: 1024,
        maxExchanges: 3,
        maxTotalRequestedTokens: 3072,
        toolTimeoutMs: 1000,
        projectedFieldIds: fields.map((field) => field.fieldId),
      },
      {
        query_execute: {
          execute: async (_context, args) => {
            expect(args.sparql).toBe(actual.query)
            const executed = querySchema.parse(observe('Q-01-semantic-wrong'))
            if (!executed.ok) throw Error('actual probe execution failed')
            expect(executed.inputSha256).toBe(actual.inputSha256)
            return {
              ...observation,
              fields: executed.rows.map((row, index) => ({
                fieldId: `alarm:${index}`,
                value: row.alarm,
              })),
            }
          },
        },
      },
    )
    const call = {
      id: 'probe.call/1',
      type: 'function',
      function: {
        name: 'query_execute',
        arguments: JSON.stringify({ sparql: actual.query, scope: 'asserted' }),
      },
    }
    const raw = (id: string, content: string | null, calls?: unknown[]) =>
      JSON.stringify({
        id,
        object: 'chat.completion',
        created: 1,
        model: 'hand-authored-protocol-not-provider',
        choices: [
          {
            index: 0,
            finish_reason: calls ? 'tool_calls' : 'stop',
            message: {
              role: 'assistant',
              content,
              reasoning_content: 'hand-authored test',
              ...(calls ? { tool_calls: calls } : {}),
            },
          },
        ],
      })
    conversation.prepareExchange(() => context)
    await conversation.acceptResponse(
      1,
      raw('probe:r1', null, [call]),
      () => context,
      new AbortController().signal,
    )
    const next = conversation.prepareExchange(() => context)
    expect(next.body.messages.at(-1)).toMatchObject({
      role: 'tool',
      content: JSON.stringify({ kind: 'evidence', status: 'current', fields }),
    })
    await conversation.acceptResponse(
      2,
      raw('probe:r2', '{"kind":"evidence","callIds":["probe.call/1"]}'),
      () => context,
      new AbortController().signal,
    )
    expect(conversation.state().answer).toEqual({
      kind: 'evidence',
      receipts: [{ callId: call.id, tool: 'query_execute', outcome: observation }],
    })
    expect(fields.map((field) => field.value)).toEqual(['<urn:ontolearn:learning:alarm/A02>'])
    expect(fields.map((field) => field.value)).not.toEqual(['<urn:ontolearn:learning:alarm/A01>'])
    const q2 = observations.get('Q-02')!
    expect(() =>
      conversation.addUserTurn('新阶段', () => ({
        ...context,
        projectRevision: 2,
        inputSnapshotId: `probe:${q2.inputSha256}`,
      })),
    ).toThrow('STALE_CONTEXT')
  })
})
