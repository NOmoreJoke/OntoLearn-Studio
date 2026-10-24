import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { matchesBusiness3Response, validateV2 } from '../../packages/contracts/src/v2'
import { reassembleOwnershipDetail, type OwnershipDetailPage } from '../../packages/contracts/src'

const root = fileURLToPath(new URL('../../', import.meta.url))
const registryHash = createHash('sha256')
  .update(readFileSync(new URL('../../packages/contracts/v2/registry.json', import.meta.url)))
  .digest('hex')
const id = '00000000-0000-4000-8000-000000000001'
const session = '00000000-0000-4000-8000-000000000002'
const projectId = '00000000-0000-4000-8000-000000000003'
const operationId = '00000000-0000-4000-8000-000000000004'
const otherId = '00000000-0000-4000-8000-000000000005'
const hash = 'a'.repeat(64)
const otherHash = 'b'.repeat(64)
const inputDigest = '52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e'
const cursor = `${'a'.repeat(32)}.${'b'.repeat(16)}.${'C'.repeat(43)}`
const name = '设备 "A"\n𠮷'

describe('complete ownership location document', () => {
  const slot = { subject: 'urn:large:' + 'x'.repeat(40000), predicate: 'urn:ownership:value' }
  const document = {
    ownershipDetailVersion: 1,
    kind: 'manual-ownership-conflict',
    stage: 'preview',
    projectId,
    sourceBaseRevision: 2,
    reason: 'reservedIdentity',
    existing: { id: 'legacy-key-kept', owner: 'mapping-origin', sourceRow: 'original-row', slot },
    incoming: { id: 'd'.repeat(64), owner: null, sourceRow: null, slot },
  }
  const raw = Buffer.from(JSON.stringify(document)),
    documentHash = createHash('sha256').update(raw).digest('hex')
  const segmentCount = Math.ceil(raw.length / 32768)
  const makePages = (): OwnershipDetailPage[] =>
    Array.from({ length: segmentCount }, (_, ordinal) => {
      const bytes = raw.subarray(ordinal * 32768, (ordinal + 1) * 32768)
      return {
        detailReadVersion: 1,
        projectId,
        detailRef: otherId,
        manifest: {
          documentKind: 'ownership-conflict',
          documentHash,
          totalBytes: raw.length,
          segmentCount,
        },
        startOrdinal: ordinal,
        segments: [
          {
            ordinal,
            byteOffset: ordinal * 32768,
            rawByteLength: bytes.length,
            sha256: createHash('sha256').update(bytes).digest('hex'),
            dataBase64: bytes.toString('base64'),
          },
        ],
        nextOrdinal: ordinal + 1 === segmentCount ? null : ordinal + 1,
        complete: ordinal + 1 === segmentCount,
      }
    })
  it('captures all pages privately and preserves >16KiB location and legacy identity', async () => {
    const pages = makePages()
    const promise = reassembleOwnershipDetail({ projectId, detailRef: otherId }, pages)
    pages[0]!.segments[0]!.dataBase64 = ''
    expect(await promise).toEqual(document)
  })
  it('rejects random final page, missing/repeated chunks and corrupted bytes', async () => {
    const pages = makePages()
    expect(pages.at(-1)!.complete).toBe(true)
    await expect(
      reassembleOwnershipDetail({ projectId, detailRef: otherId }, [pages.at(-1)!]),
    ).rejects.toThrow('INVALID_OWNERSHIP_DETAIL')
    await expect(
      reassembleOwnershipDetail({ projectId, detailRef: otherId }, [pages[0]!, ...pages]),
    ).rejects.toThrow('INVALID_OWNERSHIP_DETAIL')
    pages[0]!.segments[0]!.sha256 = 'f'.repeat(64)
    await expect(
      reassembleOwnershipDetail({ projectId, detailRef: otherId }, pages),
    ).rejects.toThrow('INVALID_OWNERSHIP_DETAIL')
  })
})

// These are new literal vectors, not candidate valid/expected fixture values.
function request(method: string, params: unknown) {
  return { kind: 'request', protocolVersion: 3, id, engineSessionId: session, method, params }
}
function response(method: string, result: unknown) {
  return {
    kind: 'response',
    protocolVersion: 3,
    id,
    engineSessionId: session,
    method,
    ok: true,
    result,
  }
}
function failure(method: string) {
  return {
    kind: 'response',
    protocolVersion: 3,
    id,
    engineSessionId: session,
    method,
    ok: false,
    error: {
      code: 'PERMISSION_DENIED',
      messageKey: 'permission.denied',
      retryable: false,
      params: {},
    },
  }
}
function canonicalRequestHash(value: Record<string, unknown>) {
  // These request objects have one nested initialization object, whose sole key is kind.
  // Sorting top-level keys therefore gives the complete Python sort_keys representation.
  const ordered = Object.fromEntries(
    Object.keys(value)
      .sort()
      .map((key) => [key, value[key]]),
  )
  return createHash('sha256').update(JSON.stringify(ordered), 'utf8').digest('hex')
}
const blankParams = { requestVersion: 1, operationId, name, initialization: { kind: 'blank' } }
const exampleParams = {
  exampleCreateRequestVersion: 1,
  operationId,
  name,
  exampleId: 'equipment-maintenance',
  inputDigest,
}
function createResult(named: boolean) {
  const requestHash = canonicalRequestHash(named ? exampleParams : blankParams)
  const common = {
    libraryEvidenceRef: hash,
    projectId,
    operationId,
    requestHash,
    contextHash: hash,
    planHash: hash,
    operationSequence: 1,
    metadataVersion: 1,
    inputSnapshotId: hash,
    beforeCheckpointRef: hash,
    afterCheckpointRef: hash,
  }
  return {
    createResultVersion: 1,
    projectId,
    operationId,
    requestHash,
    receipt: named
      ? {
          ...common,
          domainRevision: 1,
          exampleCreateReceiptVersion: 1,
          exampleId: 'equipment-maintenance',
          inputDigest,
        }
      : { ...common, domainRevision: 0, projectCreateReceiptVersion: 1 },
  }
}
const metadata = {
  name: '设备项目',
  templateRef: null,
  archived: false,
  mode: 'guided',
  origin: 'created',
}
const project = {
  projectId,
  projectRevision: 2,
  inputSnapshotId: hash,
  dependencyVector: { 'facts:asserted': 0 },
  formatVersion: 3,
}
const item = {
  projectId,
  domainRevision: 2,
  metadataVersion: 1,
  metadata,
  operationSequence: 3,
  checkpointRef: hash,
}
const catalog = {
  catalogVersion: 1,
  snapshotId: otherId,
  items: [item],
  total: 1,
  offset: 0,
  nextCursor: null,
}
const workspace = {
  workspaceVersion: 1,
  projectId,
  domainRevision: 2,
  metadataVersion: 1,
  metadata,
  operationSequence: 3,
  checkpointRef: hash,
  inputSnapshotId: hash,
  draft: { editor: 'query', state: 'missing' },
}
const read = {
  readVersion: 1,
  projectId,
  inputSnapshotId: hash,
  workspace,
  domain: {
    projectRevision: 2,
    dependencyVector: { 'facts:asserted': 0 },
    state: { definitions: [], facts: [], mappingState: {} },
  },
}
const pairs = [
  { method: 'project.catalog', params: { pageSize: 1, cursor: null }, result: catalog },
  { method: 'project.create', params: blankParams, result: createResult(false) },
  { method: 'project.example.create', params: exampleParams, result: createResult(true) },
  { method: 'project.open', params: { projectId }, result: project },
  { method: 'project.read', params: { projectId, editor: 'query' }, result: read },
]
type SchemaCase = { name: string; schema: string; value: unknown; expected: boolean }
type BindingCase = {
  name: string
  request: unknown
  response: unknown
  tsExpected: boolean
  pythonExpected: boolean
}
const schemas: SchemaCase[] = []
const bindings: BindingCase[] = []
function schema(name: string, definition: string, value: unknown, expected: boolean) {
  schemas.push({ name, schema: definition, value, expected })
}
function binding(
  name: string,
  q: unknown,
  r: unknown,
  expected: boolean,
  pythonExpected = expected,
) {
  bindings.push({ name, request: q, response: r, tsExpected: expected, pythonExpected })
}
for (const p of pairs) {
  const q = request(p.method, p.params)
  const r = response(p.method, p.result)
  for (const [label, definition, value] of [
    ['request', 'request3', q],
    ['response', 'response3', r],
    ['request envelope', 'envelope3', q],
    ['response envelope', 'envelope3', r],
  ] as const)
    schema(`${p.method} ${label}`, definition, value, true)
  schema(`${p.method} v2 request refused`, 'request', { ...q, protocolVersion: 2 }, false)
  schema(`${p.method} v2 response refused`, 'response', { ...r, protocolVersion: 2 }, false)
  schema(`${p.method} extra request path`, 'request3', { ...q, path: '/private/not-public' }, false)
  schema(`${p.method} extra response bytes`, 'response3', { ...r, bytes: 'opaque' }, false)
  schema(`${p.method} failure`, 'response3', failure(p.method), true)
  binding(`${p.method} complete success`, q, r, true)
  binding(`${p.method} request ID`, q, { ...r, id: otherId }, false)
  binding(`${p.method} session`, q, { ...r, engineSessionId: otherId }, false)
  binding(`${p.method} finite failure`, q, failure(p.method), true)
  binding(
    `${p.method} failure wrong session`,
    q,
    { ...failure(p.method), engineSessionId: otherId },
    false,
  )
}
const blankRequest = request('project.create', blankParams)
const blank = createResult(false)
const namedRequest = request('project.example.create', exampleParams)
const named = createResult(true)
schema('blank result cannot use named receipt', 'result_project.create', named, false)
schema('named result cannot use blank receipt', 'result_project.example.create', blank, false)
schema(
  'named request cannot use blank initialization',
  'params_project.example.create',
  blankParams,
  false,
)
schema(
  'blank request cannot use named initialization',
  'params_project.create',
  exampleParams,
  false,
)
schema(
  'named input digest exact fixed resource',
  'params_project.example.create',
  { ...exampleParams, inputDigest: otherHash },
  false,
)
schema(
  'named receipt digest exact fixed resource',
  'result_project.example.create',
  { ...named, receipt: { ...named.receipt, inputDigest: otherHash } },
  false,
)
schema(
  'create operation must be UUID',
  'params_project.create',
  { ...blankParams, operationId: true },
  false,
)
schema(
  'create extra nested path',
  'params_project.create',
  { ...blankParams, initialization: { kind: 'blank', path: '/private/not-public' } },
  false,
)
schema('unicode create request', 'request3', blankRequest, true)
schema('unicode named request', 'request3', namedRequest, true)
schema('empty create name', 'params_project.create', { ...blankParams, name: '' }, false)
schema(
  'create name over schema scalar limit',
  'params_project.create',
  { ...blankParams, name: '中'.repeat(4097) },
  false,
)
for (const [label, q, result] of [
  ['blank', blankRequest, blank],
  ['named', namedRequest, named],
] as const) {
  binding(
    `${label} operation outer mismatch`,
    q,
    response(q.method, { ...result, operationId: otherId }),
    false,
  )
  binding(
    `${label} operation receipt mismatch`,
    q,
    response(q.method, { ...result, receipt: { ...result.receipt, operationId: otherId } }),
    false,
  )
  binding(
    `${label} project receipt mismatch`,
    q,
    response(q.method, { ...result, receipt: { ...result.receipt, projectId: otherId } }),
    false,
  )
  binding(
    `${label} request hash receipt mismatch`,
    q,
    response(q.method, { ...result, receipt: { ...result.receipt, requestHash: otherHash } }),
    false,
  )
  // Shared TS is deliberately structural; the Node main-process client supplies SHA binding.
  // Python also hashes the actual request here. Never assert false parity for that known split.
  binding(
    `${label} coherent forged digest needs main-process SHA`,
    q,
    response(q.method, {
      ...result,
      requestHash: otherHash,
      receipt: { ...result.receipt, requestHash: otherHash },
    }),
    true,
    false,
  )
}
binding(
  'create changed original name needs main-process SHA',
  request('project.create', { ...blankParams, name: '另一项目' }),
  response('project.create', blank),
  true,
  false,
)
binding(
  'wrong method cannot consume open response',
  request('project.read', { projectId, editor: 'query' }),
  response('project.open', project),
  false,
)
binding(
  'open wrong project',
  request('project.open', { projectId }),
  response('project.open', { ...project, projectId: otherId }),
  false,
)
const catalogRequest = request('project.catalog', { pageSize: 1, cursor: null })
for (const [label, result, expected] of [
  ['empty final page', { ...catalog, items: [], total: 0 }, true],
  ['bounded next page', { ...catalog, total: 2, nextCursor: cursor }, true],
  [
    'too many items',
    { ...catalog, items: [item, { ...item, projectId: otherId }], total: 2 },
    false,
  ],
  ['offset beyond total', { ...catalog, offset: 2 }, false],
  ['premature final page', { ...catalog, total: 2 }, false],
  ['cursor after final item', { ...catalog, nextCursor: cursor }, false],
  ['empty continuing page', { ...catalog, items: [], total: 2, nextCursor: cursor }, false],
] as const)
  binding(`catalog ${label}`, catalogRequest, response('project.catalog', result), expected)
schema(
  'catalog malformed cursor',
  'params_project.catalog',
  { pageSize: 1, cursor: '../other' },
  false,
)
schema('catalog page 65', 'params_project.catalog', { pageSize: 65, cursor: null }, false)
schema(
  'catalog extra item path',
  'result_project.catalog',
  { ...catalog, items: [{ ...item, path: '/private/not-public' }] },
  false,
)
const readRequest = request('project.read', { projectId, editor: 'query' })
for (const [label, result, expected] of [
  ['workspace wrong project', { ...read, workspace: { ...workspace, projectId: otherId } }, false],
  [
    'workspace wrong snapshot',
    { ...read, workspace: { ...workspace, inputSnapshotId: otherHash } },
    false,
  ],
  ['domain wrong revision', { ...read, domain: { ...read.domain, projectRevision: 3 } }, false],
  [
    'draft wrong editor',
    { ...read, workspace: { ...workspace, draft: { editor: 'mapping', state: 'missing' } } },
    false,
  ],
  [
    'present draft',
    {
      ...read,
      workspace: {
        ...workspace,
        draft: {
          editor: 'query',
          state: 'present',
          generation: 1,
          present: true,
          boundDomainRevision: 2,
          contentJson: '{}',
          contentHash: hash,
        },
      },
    },
    true,
  ],
  [
    'present draft false flag',
    {
      ...read,
      workspace: {
        ...workspace,
        draft: {
          editor: 'query',
          state: 'present',
          generation: 1,
          present: false,
          boundDomainRevision: 2,
          contentJson: '{}',
          contentHash: hash,
        },
      },
    },
    false,
  ],
  [
    'tombstone draft',
    {
      ...read,
      workspace: {
        ...workspace,
        draft: {
          editor: 'query',
          state: 'tombstone',
          generation: 2,
          present: false,
          boundDomainRevision: 2,
          contentJson: null,
          contentHash: null,
        },
      },
    },
    true,
  ],
  [
    'tombstone cannot carry content',
    {
      ...read,
      workspace: {
        ...workspace,
        draft: {
          editor: 'query',
          state: 'tombstone',
          generation: 2,
          present: false,
          boundDomainRevision: 2,
          contentJson: '{}',
          contentHash: hash,
        },
      },
    },
    false,
  ],
] as const)
  binding(`read ${label}`, readRequest, response('project.read', result), expected)
schema('read no raw bytes', 'result_project.read', { ...read, bytes: [1, 2] }, false)
schema(
  'draft no file path',
  'result_project.read',
  {
    ...read,
    workspace: {
      ...workspace,
      draft: { ...workspace.draft, path: '/private/not-public' },
    },
  },
  false,
)
const managedQuery = {
  layer: 'query',
  id: 'example-query',
  value: {
    text: 'SELECT ?s WHERE { ?s ?p ?o }',
    references: [],
    descriptor: {
      version: 1,
      name: '设备查询',
      description: '',
      scope: 'asserted',
      capabilityQuestion: '',
      source: 'editor',
    },
  },
}
schema('managed query ChangeSet', 'changeSetPlan', { definitions: [managedQuery] }, true)
schema(
  'managed query real preview request',
  'request3',
  request('changeset.preview', {
    projectId,
    baseRevision: 2,
    intent: 'change',
    plan: { definitions: [managedQuery] },
  }),
  true,
)
schema(
  'legacy query is not a managed ChangeSet write',
  'changeSetPlan',
  {
    definitions: [
      {
        ...managedQuery,
        value: { text: managedQuery.value.text, references: [] },
      },
    ],
  },
  false,
)
schema(
  'managed descriptor cannot claim bytes',
  'changeSetPlan',
  {
    definitions: [
      {
        ...managedQuery,
        value: {
          ...managedQuery.value,
          descriptor: {
            ...managedQuery.value.descriptor,
            bytes: 'opaque',
          },
        },
      },
    ],
  },
  false,
)
schema(
  'managed definition cannot select path',
  'changeSetPlan',
  {
    definitions: [
      {
        ...managedQuery,
        path: '/private/not-public',
      },
    ],
  },
  false,
)
schema(
  'managed descriptor version fixed',
  'changeSetPlan',
  {
    definitions: [
      {
        ...managedQuery,
        value: {
          ...managedQuery.value,
          descriptor: {
            ...managedQuery.value.descriptor,
            version: 2,
          },
        },
      },
    ],
  },
  false,
)

describe('T01 mainline strict3 shared contract and fixed expected Python parity', () => {
  for (const c of schemas)
    it(c.name, () => {
      const before = JSON.stringify(c.value)
      expect(validateV2(c.schema, c.value)).toBe(c.expected)
      expect(JSON.stringify(c.value)).toBe(before)
    })
  for (const c of bindings)
    it(c.name, () => {
      const before = JSON.stringify([c.request, c.response])
      expect(matchesBusiness3Response(c.request, c.response, registryHash)).toBe(c.tsExpected)
      expect(JSON.stringify([c.request, c.response])).toBe(before)
    })
  it('binds Unicode create hash to canonical unescaped UTF8 rather than escaped JSON', () => {
    const canonical = JSON.stringify({
      initialization: { kind: 'blank' },
      name,
      operationId,
      requestVersion: 1,
    })
    expect(blank.requestHash).toBe(createHash('sha256').update(canonical, 'utf8').digest('hex'))
    const escaped = canonical.replace(
      /[\u007f-\uffff]/g,
      (character) => `\\u${character.charCodeAt(0).toString(16).padStart(4, '0')}`,
    )
    expect(createHash('sha256').update(escaped).digest('hex')).not.toBe(blank.requestHash)
  })
  it('checks actual snapshot Python against each independent expected value', () => {
    // The parent isolated runner pins PATH to this snapshot's python-env. No uv/old .venv.
    const script = `
import importlib.util, json, pathlib, sys
p = pathlib.Path('packages/contracts/python/contract_v2.py').resolve()
s = importlib.util.spec_from_file_location('mainline_contract_actual', p)
c = importlib.util.module_from_spec(s)
s.loader.exec_module(c)
v = json.load(sys.stdin)
print(json.dumps({
    'schemas': [c.validate(x['schema'], x['value']) for x in v['schemas']],
    'bindings': [c.matches_business3_response(x['request'], x['response'], v['registryHash'])
                 for x in v['bindings']],
}))
`
    const actual = JSON.parse(
      execFileSync('python', ['-I', '-B', '-c', script], {
        cwd: root,
        encoding: 'utf8',
        input: JSON.stringify({ schemas, bindings, registryHash }),
        timeout: 30000,
        maxBuffer: 1024 * 1024,
      }),
    )
    expect(actual.schemas).toEqual(schemas.map((c) => c.expected))
    expect(actual.bindings).toEqual(bindings.map((c) => c.pythonExpected))
  })
})
