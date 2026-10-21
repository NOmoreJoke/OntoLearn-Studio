import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { JsonlReader } from '../../apps/desktop/src/main/jsonl'
import {
  displayHealthSchema,
  healthSchema,
  internalError,
  isTaskUpdate,
  PROTOCOL_VERSION,
  safeBusiness3Error,
  safeDisplayError,
  safeError,
  safeStartupError,
} from '../../packages/contracts/src'
import {
  validateBusiness3,
  validateStartupError,
  validateStartupFailure,
  validateV2,
} from '../../packages/contracts/src/v2'
import errors from '../../packages/contracts/v2/errors.json'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import schema from '../../packages/contracts/v2/schema.json'

const corpus = fixtures.startup
const actualHash = createHash('sha256')
  .update(readFileSync(new URL('../../packages/contracts/v2/registry.json', import.meta.url)))
  .digest('hex')

describe('T01 independent startup canonical, original-byte budget and display boundary', () => {
  it('binds golden values to actual canonical bytes and retains the default2 API', () => {
    expect(corpus.registryHash).toBe(actualHash)
    expect(PROTOCOL_VERSION).toBe(2)
    expect(Object.keys(errors.startup.codes)).toEqual([
      'PROJECT_FORMAT_UNSUPPORTED',
      'STORAGE_BUSY',
      'STORAGE_FAILURE',
      'INTERNAL_ERROR',
    ])
    expect(Object.hasOwn(errors.codes, 'PROJECT_FORMAT_UNSUPPORTED')).toBe(false)
    expect(schema.$defs.error_startup.oneOf).toHaveLength(4)
    expect(corpus.maxPayloadBytes).toBe(errors.startup.maxPayloadBytes)
    for (const branch of schema.$defs.error_startup.oneOf) {
      const code = branch.properties.code.const as keyof typeof errors.startup.codes
      const spec = errors.startup.codes[code]
      expect(branch.properties.params).toEqual(spec.paramsSchema)
      expect(branch.properties.messageKey.const).toBe(spec.messageKey)
      expect(branch.properties.retryable.const).toBe(spec.retryable)
    }
    for (const e of corpus.errors) {
      const spec = errors.startup.codes[e.code as keyof typeof errors.startup.codes]
      expect({ messageKey: e.messageKey, retryable: e.retryable }).toEqual({
        messageKey: spec.messageKey,
        retryable: spec.retryable,
      })
      expect(validateStartupError(e)).toBe(true)
      expect(safeStartupError(e)).toEqual(e)
    }
  })

  for (const c of corpus.cases)
    it(`complete value: ${c.name}`, () => {
      const before = JSON.stringify(c)
      const bytes = Buffer.byteLength(JSON.stringify(c.value))
      expect(validateStartupFailure(c.value, bytes, actualHash)).toBe(c.valid)
      expect(JSON.stringify(c)).toBe(before)
    })

  for (const c of corpus.raw)
    it(`actual reader metadata: ${c.name}`, () => {
      const wire = Buffer.from(c.wireUtf8)
      expect(wire.toString('base64')).toBe(c.wireBase64)
      expect(wire.length).toBe(c.wireBytes)
      expect(Buffer.concat(c.chunksBase64.map((b) => Buffer.from(b, 'base64')))).toEqual(wire)
      const results: Array<{ value: unknown; bytes: number; valid: boolean }> = []
      const failures: string[] = []
      const reader = new JsonlReader(
        (value, metadata) => {
          expect(Object.isFrozen(metadata)).toBe(true)
          results.push({
            value,
            bytes: metadata.payloadByteLength,
            valid: validateStartupFailure(value, metadata.payloadByteLength, actualHash),
          })
        },
        (reason) => failures.push(reason),
      )
      for (const chunk of c.chunksBase64) reader.push(Buffer.from(chunk, 'base64'))
      reader.end()
      expect(failures).toEqual([])
      expect(results).toHaveLength(1)
      expect(results[0].bytes).toBe(c.payloadByteLength)
      expect(results[0].valid).toBe(c.valid)
      if (c.name.startsWith('escaped equal decoded payload ')) {
        expect(c.wireUtf8.match(/\\u[0-9a-f]{4}/g)).toHaveLength(140)
        expect(results[0].value).toEqual(corpus.cases[0].value)
      }
      expect(reader.bufferedBytes).toBe(0)
    })

  it('does not lower the generic frame budget to the startup diagnostic budget', () => {
    const raw = JSON.stringify({ body: 'x'.repeat(2000) }) + '\n'
    const values: unknown[] = []
    const failures: string[] = []
    const reader = new JsonlReader(
      (v, m) => {
        expect(m.payloadByteLength).toBe(Buffer.byteLength(raw) - 1)
        values.push(v)
      },
      (reason) => failures.push(reason),
    )
    reader.push(Buffer.from(raw))
    expect(values).toEqual([{ body: 'x'.repeat(2000) }])
    expect(failures).toEqual([])
  })

  it('requires a finite original byte length and a trusted exact expected hash', () => {
    const value = corpus.cases[0].value
    for (const length of [0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER])
      expect(validateStartupFailure(value, length, actualHash)).toBe(false)
    for (const hash of ['', 'f'.repeat(64), actualHash.toUpperCase()])
      expect(validateStartupFailure(value, 1024, hash)).toBe(false)
  })

  it('keeps startup-only errors out of normal errors, jobs and business envelopes', () => {
    const format = corpus.errors[0]
    expect(validateV2('error', format)).toBe(false)
    expect(validateBusiness3('error', format)).toBe(false)
    expect(safeError(format)).toEqual(internalError)
    expect(safeBusiness3Error(format)).toEqual(internalError)
    expect(safeDisplayError(format)).toEqual(format)
    expect(safeStartupError({ ...format, params: { supportedFormats: [2] } })).toEqual(
      internalError,
    )
    const normal3 = {
      code: 'VERSION_INCOMPATIBLE',
      messageKey: 'protocol.versionIncompatible',
      retryable: false,
      params: { supportedVersions: [3] },
    }
    expect(safeBusiness3Error(normal3)).toEqual(normal3)
    expect(safeError(normal3)).toEqual(internalError)
    expect(safeStartupError(normal3)).toEqual(internalError)
    for (const version of [2, 3]) {
      const frame = {
        kind: 'response',
        protocolVersion: version,
        engineSessionId: '00000000-0000-4000-8000-000000000002',
        id: '00000000-0000-4000-8000-000000000003',
        method: 'health',
        ok: false,
        error: format,
      }
      expect(validateV2('response', frame)).toBe(false)
      expect(validateBusiness3('response', frame)).toBe(false)
      expect(validateV2('envelope', corpus.cases[0].value)).toBe(false)
      expect(validateBusiness3('envelope', corpus.cases[0].value)).toBe(false)
    }
  })

  it('accepts finite display DTOs without selecting runtime or widening normal job errors', () => {
    const health = {
      protocolVersion: 3,
      engineVersion: '0.1.0',
      status: 'ok',
      capabilities: ['health'],
    }
    expect(healthSchema.safeParse(health).success).toBe(false)
    expect(displayHealthSchema.safeParse(health).success).toBe(true)
    expect(displayHealthSchema.safeParse({ ...health, protocolVersion: 4 }).success).toBe(false)
    expect(displayHealthSchema.safeParse({ ...health, profile: 'business3' }).success).toBe(false)
    const event = {
      kind: 'connection',
      generation: 1,
      projectId: '00000000-0000-4000-8000-000000000001',
      state: 'offline',
      attempt: 3,
      error: corpus.errors[0],
    }
    expect(isTaskUpdate(event)).toBe(true)
    expect(isTaskUpdate({ ...event, error: { ...event.error, path: '/private' } })).toBe(false)
    expect(isTaskUpdate({ ...event, attempt: 0 })).toBe(false)
    expect(isTaskUpdate({ ...event, profile: 'business3' })).toBe(false)
    const project = fixtures.business3.cases.find((c) => c.name === 'response project.get')!
      .value as { result: unknown }
    expect(
      isTaskUpdate({
        kind: 'restored',
        generation: 1,
        view: { generation: 1, project: project.result, jobs: [] },
      }),
    ).toBe(true)
  })

  it('checks the same complete decoded/raw golden and constructor values with Python', () => {
    const script = `
import base64, importlib.util, json, pathlib
p = pathlib.Path('packages/contracts/python/contract_v2.py').resolve()
s = importlib.util.spec_from_file_location('startup_contract', p)
c = importlib.util.module_from_spec(s)
s.loader.exec_module(c)
f = json.loads((c.ROOT / 'fixtures.json').read_text())['startup']
h = f['registryHash']
values = [c.validate_startup_failure(x['value'], len(json.dumps(x['value'], separators=(',', ':')).encode()), h) for x in f['cases']]
raw = []
for x in f['raw']:
    wire = b''.join(base64.b64decode(b) for b in x['chunksBase64'])
    assert wire == x['wireUtf8'].encode()
    assert len(wire) == x['wireBytes']
    payload = wire[:-1]
    assert len(payload) == x['payloadByteLength']
    v = json.loads(payload)
    if x['name'].startswith('escaped equal decoded payload '):
        assert payload.count(b'\\\\u') == 140
        assert v == f['cases'][0]['value']
    raw.append(c.validate_startup_failure(v, len(payload), h))
constructed = [c.startup_error(e['code'], e['params']) for e in f['errors']]
normal = c.business3_error('VERSION_INCOMPATIBLE', {'supportedVersions': [3]})
rejected = [c.business3_error('PROJECT_FORMAT_UNSUPPORTED', {'supportedFormats': [3]}), c.startup_error('STORAGE_BUSY', {'retryAfterMs': 249}), c.startup_error('STORAGE_FAILURE', {'operationId': '00000000-0000-4000-8000-000000000001'})]
assert all(not c.validate_startup_failure(f['cases'][0]['value'], n, h) for n in (True, 0, -1, 1.5, 10**10000, float('nan'), float('inf')))
print(json.dumps({'values': values, 'raw': raw, 'constructed': constructed, 'normal': normal, 'rejected': rejected}))
`
    const result = spawnSync('uv', ['run', '--frozen', 'python', '-c', script], {
      cwd: process.cwd(),
      encoding: 'utf8',
      timeout: 30000,
    })
    expect(result.error).toBeUndefined()
    expect(result.signal).toBeNull()
    expect(result.status, result.stderr).toBe(0)
    const actual = JSON.parse(result.stdout)
    expect(actual.values).toEqual(corpus.cases.map((c) => c.valid))
    expect(actual.raw).toEqual(corpus.raw.map((c) => c.valid))
    expect(actual.constructed).toEqual(corpus.errors)
    expect(actual.normal).toEqual({
      code: 'VERSION_INCOMPATIBLE',
      messageKey: 'protocol.versionIncompatible',
      retryable: false,
      params: { supportedVersions: [3] },
    })
    expect(actual.rejected).toEqual([internalError, internalError, internalError])
  })
})
