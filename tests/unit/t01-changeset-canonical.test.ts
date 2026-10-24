import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { describe, expect, it, vi } from 'vitest'
import {
  reassembleChangeSetDocument,
  type ChangeSetManifest,
  type ChangeSetPage,
} from '../../packages/contracts/src'
import {
  matchesBusiness3Response,
  validateBusiness3,
  validateV2,
  v2Registry,
} from '../../packages/contracts/src/v2'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import regressions from '../../packages/contracts/v2/binding-regressions.json'

const corpus = fixtures.changesets
const hash = (value: Uint8Array) => createHash('sha256').update(value).digest('hex')
const actualHash = hash(
  readFileSync(new URL('../../packages/contracts/v2/registry.json', import.meta.url)),
)
const expected = (document: (typeof corpus.documents)[number]) => ({
  projectId: corpus.ids.project,
  previewHash: 'b'.repeat(64),
  manifest: document.manifest as ChangeSetManifest,
})
const pages = (document: (typeof corpus.documents)[number]) =>
  structuredClone(document.pages) as ChangeSetPage[]

function generated(raw: Buffer, kind: 'diff' | 'undo-impact' = 'diff') {
  const segments: ChangeSetPage['segments'] = []
  for (let offset = 0; offset < raw.length; offset += 32768) {
    const part = raw.subarray(offset, offset + 32768)
    segments.push({
      ordinal: segments.length,
      byteOffset: offset,
      rawByteLength: part.length,
      sha256: hash(part),
      dataBase64: part.toString('base64'),
    })
  }
  const manifest: ChangeSetManifest = {
    documentKind: kind,
    documentHash: hash(raw),
    totalBytes: raw.length,
    segmentCount: segments.length,
    segments: segments.map((segment) => ({
      ordinal: segment.ordinal,
      byteOffset: segment.byteOffset,
      rawByteLength: segment.rawByteLength,
      sha256: segment.sha256,
    })),
  }
  const binding = { projectId: corpus.ids.project, previewHash: 'b'.repeat(64), manifest }
  const list: ChangeSetPage[] = []
  for (let offset = 0; offset < segments.length; offset += 2)
    list.push({
      projectId: binding.projectId,
      previewHash: binding.previewHash,
      documentKind: kind,
      documentHash: manifest.documentHash,
      segments: segments.slice(offset, offset + 2),
      nextCursor: corpus.ids.cursor,
      complete: offset + 2 >= segments.length,
    })
  return { binding, pages: list }
}

describe('T01 typed ChangeSet sole canonical and complete document transport', () => {
  it('keeps default2 frozen and marks availability only in explicit internal3', () => {
    expect(corpus.registryHash).toBe(actualHash)
    expect(fixtures.startup.registryHash).toBe(actualHash)
    expect(fixtures.business3.registryHash).toBe(actualHash)
    expect(v2Registry.capabilities['changeset.commit'].implementation).toBe('design-only')
    expect(
      v2Registry.foundationProfiles.business3.capabilityImplementations['changeset.commit'],
    ).toBe('explicit-internal-business3-runtime')
    for (const method of ['changeset.preview', 'changeset.diff.page', 'changeset.confirm']) {
      expect((v2Registry.v2Runtime as string[]).includes(method)).toBe(false)
      expect((v2Registry.foundationProfiles.business3.methods as string[]).includes(method)).toBe(
        true,
      )
    }
  })
  it('binds strict3 hello with the actual internal3-only advertised methods', () => {
    const value = corpus.helloWithChangeSetCapabilities
    expect(matchesBusiness3Response(value.request, value.response, actualHash)).toBe(true)
    expect(validateV2('response', value.response)).toBe(false)
    const bad = structuredClone(value.response)
    bad.result.capabilities.push('not.registered')
    expect(matchesBusiness3Response(value.request, bad, actualHash)).toBe(false)
    expect(matchesBusiness3Response(value.request, value.response, 'f'.repeat(64))).toBe(false)
  })
  for (const c of corpus.cases)
    it(`complete schema: ${c.name}`, () => {
      const before = JSON.stringify(c)
      expect(validateBusiness3(c.schema, c.value)).toBe(c.valid)
      expect(JSON.stringify(c)).toBe(before)
    })
  for (const c of corpus.bindings)
    it(`direct strict3 binding: ${c.name}`, () => {
      const before = JSON.stringify(c)
      expect(matchesBusiness3Response(c.request, c.response, actualHash)).toBe(c.valid)
      expect(validateV2('request', { ...c.request, protocolVersion: 2 })).toBe(false)
      expect(validateV2('response', { ...c.response, protocolVersion: 2 })).toBe(false)
      expect(JSON.stringify(c)).toBe(before)
    })
  it('shares the complete regression binding values', () => {
    expect(regressions.changesets).toEqual(corpus.bindings)
  })
  for (const document of corpus.documents)
    it(`reassembles the entire original UTF8 document: ${document.name}`, async () => {
      const input = pages(document)
      const before = JSON.stringify(input)
      const raw = Buffer.from(document.rawUtf8)
      expect(raw.length).toBe(document.manifest.totalBytes)
      expect(hash(raw)).toBe(document.manifest.documentHash)
      expect(await reassembleChangeSetDocument(expected(document), input)).toEqual(document.value)
      expect(JSON.stringify(input)).toBe(before)
      expect(input.at(-1)!.complete).toBe(true)
      expect(input.at(-1)!.nextCursor).not.toBeNull()
      if (document.name.startsWith('multibyte')) {
        expect(document.manifest.segmentCount).toBeGreaterThan(1)
        expect(() =>
          new TextDecoder('utf8', { fatal: true }).decode(
            Buffer.from(input[0].segments[0].dataBase64, 'base64'),
          ),
        ).toThrow()
      }
    })

  for (const boundary of corpus.generatedBoundaries)
    it(`full raw budget ${boundary.rawByteLength}`, async () => {
      const raw = Buffer.from('["' + 'x'.repeat(boundary.rawByteLength - 4) + '"]')
      expect(raw.length).toBe(boundary.rawByteLength)
      expect(hash(raw)).toBe(boundary.sha256)
      const value = generated(raw)
      expect(value.binding.manifest.segmentCount).toBe(boundary.segmentCount)
      expect(validateV2('changeSetManifest', value.binding.manifest)).toBe(boundary.valid)
      if (boundary.valid) {
        const result = await reassembleChangeSetDocument(value.binding, value.pages)
        expect(result).toHaveLength(1)
        expect(result[0]).toBe('x'.repeat(boundary.rawByteLength - 4))
        for (const page of value.pages) {
          expect(validateV2('changeSetPage', page)).toBe(true)
          expect(Buffer.byteLength(JSON.stringify(page))).toBeLessThanOrEqual(131072)
        }
      } else
        await expect(reassembleChangeSetDocument(value.binding, value.pages)).rejects.toThrow(
          'INVALID_CHANGESET_DOCUMENT',
        )
    }, 20000)

  it('requires complete immutable expected project, preview, kind and manifest bindings', async () => {
    const document = corpus.documents[2]
    for (const key of ['projectId', 'previewHash', 'documentKind', 'documentHash'] as const) {
      const input = pages(document)
      if (key === 'documentKind') input[0].documentKind = 'undo-impact'
      else input[0][key] = key === 'projectId' ? corpus.ids.target : 'f'.repeat(64)
      await expect(reassembleChangeSetDocument(expected(document), input)).rejects.toThrow(
        'INVALID_CHANGESET_DOCUMENT',
      )
    }
    for (const mutation of [
      'missing',
      'reversed',
      'duplicate',
      'offset',
      'hash',
      'data',
      'premature',
      'never-complete',
      'extra',
    ] as const) {
      const input = pages(document)
      if (mutation === 'missing') input[0].segments.shift()
      if (mutation === 'reversed') input.reverse()
      if (mutation === 'duplicate') input[0].segments[1] = structuredClone(input[0].segments[0])
      if (mutation === 'offset') input[0].segments[0].byteOffset++
      if (mutation === 'hash') input[0].segments[0].sha256 = 'f'.repeat(64)
      if (mutation === 'data') input[0].segments[0].dataBase64 = 'YQ=='
      if (mutation === 'premature') input[0].complete = true
      if (mutation === 'never-complete') input.at(-1)!.complete = false
      if (mutation === 'extra') input.push(structuredClone(input.at(-1)!))
      await expect(reassembleChangeSetDocument(expected(document), input)).rejects.toThrow(
        'INVALID_CHANGESET_DOCUMENT',
      )
    }
  })

  it('checks actual raw SHA independently of shape and rejects noncanonical base64 padding', async () => {
    const value = generated(Buffer.from('[]'))
    value.pages[0].segments[0].dataBase64 = Buffer.from('{}').toString('base64')
    await expect(reassembleChangeSetDocument(value.binding, value.pages)).rejects.toThrow(
      'INVALID_CHANGESET_DOCUMENT',
    )
    const padding = generated(Buffer.from('[]'))
    padding.pages[0].segments[0].dataBase64 = 'W13='
    expect(validateV2('changeSetPage', padding.pages[0])).toBe(true)
    await expect(reassembleChangeSetDocument(padding.binding, padding.pages)).rejects.toThrow(
      'INVALID_CHANGESET_DOCUMENT',
    )
  })

  for (const raw of [
    Buffer.from('{}'),
    Buffer.from('[1e999]'),
    Buffer.from('["\\ud800"]'),
    Buffer.from([91, 34, 0xc3, 0x28, 34, 93]),
    Buffer.from('[invalid]'),
  ])
    it(`rejects invalid full JSON/UTF8 even with valid raw hashes: ${raw.toString('hex')}`, async () => {
      const value = generated(raw)
      await expect(reassembleChangeSetDocument(value.binding, value.pages)).rejects.toThrow(
        'INVALID_CHANGESET_DOCUMENT',
      )
    })

  it('rejects the synchronous manifest getter budget switch before any allocation', async () => {
    const document = corpus.documents[0]
    const legitimate = expected(document)
    let reads = 0
    const hostile = {
      projectId: legitimate.projectId,
      previewHash: legitimate.previewHash,
      get manifest() {
        reads++
        return reads <= 5 ? legitimate.manifest : { ...legitimate.manifest, totalBytes: 16777217 }
      },
    }
    const Original = globalThis.Uint8Array
    const allocations: number[] = []
    const Guarded = new Proxy(Original, {
      construct(target, args, receiver) {
        if (typeof args[0] === 'number') {
          allocations.push(args[0])
          if (args[0] > 16777216) throw new Error('TEST_BLOCKED_OVER_BUDGET_ALLOCATION')
        }
        return Reflect.construct(target, args, receiver)
      },
    })
    vi.stubGlobal('Uint8Array', Guarded)
    try {
      await expect(reassembleChangeSetDocument(hostile, pages(document))).rejects.toThrow(
        'INVALID_CHANGESET_DOCUMENT',
      )
      expect(reads).toBe(0)
      expect(allocations).toEqual([])
    } finally {
      vi.unstubAllGlobals()
    }
  })

  it('captures only own data descriptors, rejecting accessors, executable objects and holes', async () => {
    const document = corpus.documents[0]
    let calls = 0
    const getter = () => {
      calls++
      return 1
    }
    const values: Array<{ binding: ReturnType<typeof expected>; input: ChangeSetPage[] }> = []
    for (const where of ['segment', 'page', 'array'] as const) {
      const binding = structuredClone(expected(document))
      const input = pages(document)
      if (where === 'segment')
        Object.defineProperty(input[0].segments[0], 'rawByteLength', {
          get: getter,
          enumerable: true,
        })
      if (where === 'page')
        Object.defineProperty(input[0], 'segments', { get: getter, enumerable: true })
      if (where === 'array') Object.defineProperty(input, '0', { get: getter, enumerable: true })
      values.push({ binding, input })
    }
    const executable = structuredClone(expected(document))
    Object.defineProperty(executable.manifest, 'toJSON', {
      value: () => {
        calls++
        return executable
      },
      enumerable: true,
    })
    values.push({ binding: executable, input: pages(document) })
    const custom = Object.assign(Object.create({ custom: true }), expected(document))
    values.push({ binding: custom, input: pages(document) })
    const symbol = structuredClone(expected(document))
    Object.defineProperty(symbol.manifest, Symbol('hidden'), { value: 1 })
    values.push({ binding: symbol, input: pages(document) })
    const hole = pages(document)
    delete (hole as Array<ChangeSetPage | undefined>)[0]
    values.push({ binding: expected(document), input: hole })
    for (const value of values)
      await expect(reassembleChangeSetDocument(value.binding, value.input)).rejects.toThrow(
        'INVALID_CHANGESET_DOCUMENT',
      )
    expect(calls).toBe(0)
  })

  it('accepts the actual complete ready DTO as expected binding without reading unrelated fields', async () => {
    const document = corpus.documents[0]
    const ready = structuredClone(
      corpus.cases.find((value) => value.name === 'ready')!.value,
    ) as unknown as Parameters<typeof reassembleChangeSetDocument>[0]
    expect(Object.keys(ready).length).toBeGreaterThan(8)
    let calls = 0
    Object.defineProperty(ready, 'unrelatedHostField', {
      get() {
        calls++
        throw new Error('NOT_BINDING_DATA')
      },
      enumerable: true,
    })
    expect(await reassembleChangeSetDocument(ready, pages(document))).toEqual(document.value)
    expect(calls).toBe(0)
  })

  it('captures all mutable caller values before the first async digest', async () => {
    const document = corpus.documents[0]
    const input = pages(document)
    const binding = structuredClone(expected(document))
    const pending = reassembleChangeSetDocument(binding, input)
    binding.previewHash = 'f'.repeat(64)
    binding.manifest.documentHash = 'f'.repeat(64)
    input[0].segments[0].dataBase64 = ''
    expect(await pending).toEqual(document.value)
  })

  it('checks the same complete schema/binding/raw corpus with the sole Python helper', () => {
    const script = `
import base64, hashlib, importlib.util, json, pathlib
p = pathlib.Path('packages/contracts/python/contract_v2.py').resolve()
s = importlib.util.spec_from_file_location('changeset_contract', p)
c = importlib.util.module_from_spec(s)
s.loader.exec_module(c)
f = json.loads((c.ROOT / 'fixtures.json').read_text())['changesets']
values = [c.validate_business3(x['schema'], x['value']) for x in f['cases']]
bindings = [c.matches_business3_response(x['request'], x['response'], f['registryHash']) for x in f['bindings']]
hello = f['helloWithChangeSetCapabilities']
assert c.matches_business3_response(hello['request'], hello['response'], f['registryHash'])
for d in f['documents']:
    data = b''.join(base64.b64decode(s['dataBase64'], validate=True) for p in d['pages'] for s in p['segments'])
    assert data == d['rawUtf8'].encode()
    assert len(data) == d['manifest']['totalBytes']
    assert hashlib.sha256(data).hexdigest() == d['manifest']['documentHash']
    assert json.loads(data) == d['value']
    assert c.validate('changeSetManifest', d['manifest'])
    assert all(c.validate('changeSetPage', p) for p in d['pages'])
print(json.dumps({'values': values, 'bindings': bindings}))
`
    const result = spawnSync('uv', ['run', '--frozen', 'python', '-c', script], {
      encoding: 'utf8',
      timeout: 30000,
    })
    expect(result.error).toBeUndefined()
    expect(result.signal).toBeNull()
    expect(result.status, result.stderr).toBe(0)
    expect(JSON.parse(result.stdout)).toEqual({
      values: corpus.cases.map((c) => c.valid),
      bindings: corpus.bindings.map((c) => c.valid),
    })
  })
})
