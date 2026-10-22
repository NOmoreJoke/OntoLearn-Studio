import { afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest'
import {
  appendFileSync,
  copyFileSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

type EventBinding = import('../../packages/contracts/src/v2').EventBinding

// Root independently supplied this digest; never calculate expected from the candidate record.
const APPROVAL_SHA256 = '6943a912720da27063e5ff63c8eb1cd1edb492ea27927bbc2a94bf68bfb32b8b'
const workspace = fileURLToPath(new URL('../../', import.meta.url))
const approvalSource = join(
  workspace,
  'docs/reviews/T01/v2-corpus-baseline-20261023/approval-record.json',
)
const PATHS = [
  'packages/contracts/v2/fixtures.json',
  'packages/contracts/v2/binding-regressions.json',
  'packages/contracts/v2/frame-fixtures.json',
] as const
interface Options {
  corpusRoot: string
  approvalRecordPath: string
  expectedApprovalSHA256: string
}
interface Result {
  ok: true
  approvalId: string
  approvalSHA256: string
  sourceBase: string
  records: { path: string; bytes: number; sha256: string }[]
}
interface Verifier {
  verifyV2Corpus(options: Options): Result
  parseOperatorArguments(args: string[]): Options
}
let verifier: Verifier
let validateV2: typeof import('../../packages/contracts/src/v2').validateV2
let acceptsJobEvent: typeof import('../../packages/contracts/src/v2').acceptsJobEvent
let JsonlReader: typeof import('../../apps/desktop/src/main/jsonl').JsonlReader
let temporary: string
let options: Options

beforeAll(async () => {
  const moduleURL = new URL('../../scripts/verify-v2-contract-corpus.mjs', import.meta.url).href
  const loaded: unknown = await import(moduleURL)
  verifier = loaded as Verifier
  // Raw record/corpus gate precedes candidate adapter imports in this dedicated test file.
  verifier.verifyV2Corpus({
    corpusRoot: workspace,
    approvalRecordPath: approvalSource,
    expectedApprovalSHA256: APPROVAL_SHA256,
  })
  const adapters = await import('../../packages/contracts/src/v2')
  validateV2 = adapters.validateV2
  acceptsJobEvent = adapters.acceptsJobEvent
  JsonlReader = (await import('../../apps/desktop/src/main/jsonl')).JsonlReader
})
beforeEach(() => {
  temporary = mkdtempSync(join(tmpdir(), 'v2-corpus-baseline-unit-'))
  const corpusRoot = join(temporary, 'corpus')
  for (const path of PATHS) {
    const target = join(corpusRoot, path)
    mkdirSync(dirname(target), { recursive: true })
    copyFileSync(join(workspace, path), target)
  }
  const approvalRecordPath = join(temporary, 'trusted-record.json')
  copyFileSync(approvalSource, approvalRecordPath)
  options = { corpusRoot, approvalRecordPath, expectedApprovalSHA256: APPROVAL_SHA256 }
})
afterEach(() => {
  if (temporary) rmSync(temporary, { recursive: true, force: true })
})

describe('independently approved v2 raw corpus baseline', () => {
  it('checks all three paths and exact identities against the externally pinned record', () => {
    expect(verifier.verifyV2Corpus(options)).toEqual({
      ok: true,
      approvalId: 'v2-contract-corpus-baseline-20261023-v1',
      approvalSHA256: APPROVAL_SHA256,
      sourceBase: '5f910b52c69d86a1076b2032e5d3c63e715947f3',
      records: [
        {
          path: PATHS[0],
          bytes: 472098,
          sha256: '32031804abf3283e87f070ffbfc3f95cf627f6b71e7bc49711faaff52ec31ad6',
        },
        {
          path: PATHS[1],
          bytes: 123964,
          sha256: '9601d6d0a31e3e71078ac2562c6b8501c1292bc2be71de742e40c2fc54512a24',
        },
        {
          path: PATHS[2],
          bytes: 17537,
          sha256: '8e9a142ff04e908cc286c15702cd18b6c2ce9453490585d0855c3f62995dd2e5',
        },
      ],
    })
  })
  for (const path of PATHS) {
    it(`rejects raw whitespace drift: ${path}`, () => {
      appendFileSync(join(options.corpusRoot, path), ' ')
      expect(() => verifier.verifyV2Corpus(options)).toThrow('CORPUS_SIZE_MISMATCH')
    })
    it(`rejects same-length raw drift: ${path}`, () => {
      const target = join(options.corpusRoot, path)
      const bytes = readFileSync(target)
      expect(bytes[bytes.length - 1]).toBe(10)
      bytes[bytes.length - 1] = 32
      writeFileSync(target, bytes)
      expect(() => verifier.verifyV2Corpus(options)).toThrow('CORPUS_DIGEST_MISMATCH')
    })
    it(`rejects a missing corpus rather than searching another version: ${path}`, () => {
      rmSync(join(options.corpusRoot, path))
      expect(() => verifier.verifyV2Corpus(options)).toThrow('FILE_READ_FAILED')
    })
  }
  it('rejects a changed approval record before any corpus is available', () => {
    appendFileSync(options.approvalRecordPath, ' ')
    rmSync(options.corpusRoot, { recursive: true })
    expect(() => verifier.verifyV2Corpus(options)).toThrow('APPROVAL_DIGEST_MISMATCH')
  })
  it('does not accept candidate edited hashes or approvedBy text as authority', () => {
    const record = JSON.parse(readFileSync(options.approvalRecordPath, 'utf8'))
    record.records[0].sha256 = '0'.repeat(64)
    record.approvedByControllerThread = 'candidate-self-approved'
    writeFileSync(options.approvalRecordPath, JSON.stringify(record))
    expect(() => verifier.verifyV2Corpus(options)).toThrow('APPROVAL_DIGEST_MISMATCH')
  })
  it('rejects a same-length change in record bytes using the independent SHA', () => {
    const bytes = readFileSync(options.approvalRecordPath)
    expect(bytes[bytes.length - 1]).toBe(10)
    bytes[bytes.length - 1] = 32
    writeFileSync(options.approvalRecordPath, bytes)
    expect(() => verifier.verifyV2Corpus(options)).toThrow('APPROVAL_DIGEST_MISMATCH')
  })
  it('rejects a wrong operator digest instead of replacing it from the candidate', () => {
    expect(() =>
      verifier.verifyV2Corpus({ ...options, expectedApprovalSHA256: '0'.repeat(64) }),
    ).toThrow('APPROVAL_DIGEST_MISMATCH')
  })
  it('rejects oversized record metadata without parsing it', () => {
    writeFileSync(options.approvalRecordPath, ' '.repeat(8193))
    expect(() => verifier.verifyV2Corpus(options)).toThrow('FILE_LIMIT')
  })
  for (const args of [
    [],
    ['--corpus-root', '/a'],
    ['--corpus-root', '/a', '--corpus-root', '/b', '--approval-record', '/c'],
    ['--corpus-root', '/a', '--approval-record', '/b', '--auto-latest', 'true'],
  ]) {
    it(`requires explicit, unique operator arguments: ${JSON.stringify(args)}`, () => {
      expect(() => verifier.parseOperatorArguments(args)).toThrow('OPERATOR_INPUT_REQUIRED')
    })
  }
  it('preserves all explicit operator inputs without substituting a candidate default', () => {
    expect(
      verifier.parseOperatorArguments([
        '--corpus-root',
        options.corpusRoot,
        '--approval-record',
        options.approvalRecordPath,
        '--expected-approval-sha256',
        APPROVAL_SHA256,
      ]),
    ).toEqual(options)
  })
})

// Literal full inputs below are independently traceable to approved5f slices.
// Expectations follow protocol3/7/9-11/44/56 and acceptance9-10, not valid/expected fields.
const HELLO = {
  kind: 'request',
  protocolVersion: 2,
  id: '00000000-0000-4000-8000-000000000009',
  engineSessionId: null,
  method: 'hello',
  params: {
    supportedVersions: [2],
    clientId: '00000000-0000-4000-8000-000000000007',
  },
}
const ROUTING_VALUE = {
  kind: 'notification',
  protocolVersion: 2,
  engineSessionId: '00000000-0000-4000-8000-000000000002',
  subscriptionId: '00000000-0000-4000-8000-000000000010',
  projectId: '00000000-0000-4000-8000-000000000001',
  jobId: '00000000-0000-4000-8000-000000000003',
  seq: 1,
  event: 'job.state',
  data: {
    jobId: '00000000-0000-4000-8000-000000000003',
    projectId: '00000000-0000-4000-8000-000000000001',
    operationId: '00000000-0000-4000-8000-000000000004',
    capability: 'test.rounds',
    inputSnapshotId: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    dependencyVector: {
      'facts:asserted': 1,
    },
    definitionSetDigests: {},
    parametersHash: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    scope: 'scenario',
    implementation: {
      executionSemanticsVersion: 'E1',
      engineVersion: '0.1.0',
      dependencyLockHash: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    },
    state: 'cancelled',
    stateVersion: 4,
    limits: {
      startupMs: 10000,
      handshakeMs: 5000,
      requestMs: 5000,
      totalMs: 120000,
      heartbeatMs: 10000,
      cancelGraceMs: 5000,
      maxFrameBytes: 262144,
      maxQueuedJobs: 32,
      maxConcurrentJobs: 2,
      maxPageItems: 100,
      maxPageBytes: 131072,
      maxWorkerMemoryBytes: 536870912,
    },
    commitProgress: {
      mode: 'rounds',
      committedProgress: {
        runId: '00000000-0000-4000-8000-000000000005',
        lastCommittedRound: 2,
        snapshotRef: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      },
    },
    resultRef: null,
    error: null,
    createdAtMs: 1,
    updatedAtMs: 9,
    finishedAtMs: 9,
    input: {
      inputSnapshotId: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      scope: 'scenario',
      definitionId: 'test',
      parametersHash: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      derivedResultIds: [],
      preparedPlanRef: null,
    },
    confirmationRef: null,
  },
}
const VALID_BINDING = {
  engineSessionId: '00000000-0000-4000-8000-000000000002',
  projectId: '00000000-0000-4000-8000-000000000001',
  jobId: '00000000-0000-4000-8000-000000000003',
  subscriptionId: '00000000-0000-4000-8000-000000000010',
  lastSeq: 0,
  stateVersion: 3,
  state: 'cancelling',
}

describe('finite independent literal semantic anchors', () => {
  it('accepts the complete bootstrap hello and rejects an unknown params key', () => {
    expect(validateV2('envelope', HELLO)).toBe(true)
    expect(validateV2('envelope', { ...HELLO, params: { ...HELLO.params, extra: true } })).toBe(
      false,
    )
  })
  it('requires lastSeq in the trusted notification binding without a default', () => {
    expect(acceptsJobEvent(ROUTING_VALUE, VALID_BINDING)).toBe(true)
    const missing: Record<string, unknown> = { ...VALID_BINDING }
    delete missing.lastSeq
    expect(acceptsJobEvent(ROUTING_VALUE, missing as unknown as EventBinding)).toBe(false)
  })
  it('rejects a nested duplicate key and discards the later valid frame', () => {
    const frames: unknown[] = []
    const errors: string[] = []
    const reader = new JsonlReader(
      (value) => frames.push(value),
      (error) => errors.push(error),
    )
    reader.push(Buffer.from('7b2278223a7b2261223a312c2261223a327d7d0a', 'hex'))
    reader.push(Buffer.from('7b7d0a', 'hex'))
    reader.end()
    expect(frames).toEqual([])
    expect(errors).toEqual(['json'])
    expect(reader.terminal).toBe(true)
    expect(reader.bufferedBytes).toBe(0)
  })
  it('preserves the complete UTF8/CRLF positive output and clears the finished buffer', () => {
    const frames: unknown[] = []
    const errors: string[] = []
    const reader = new JsonlReader(
      (value) => frames.push(value),
      (error) => errors.push(error),
    )
    reader.push(Buffer.from('', 'hex'))
    reader.push(
      Buffer.from('7b2274657874223a22e4b8ade69687f09f9880227d0d0a7b226f6b223a747275657d0a', 'hex'),
    )
    reader.end()
    expect(frames).toEqual([{ text: '中文😀' }, { ok: true }])
    expect(errors).toEqual([])
    expect(reader.terminal).toBe(true)
    expect(reader.bufferedBytes).toBe(0)
  })
})
