import { closeSync, constants, fstatSync, lstatSync, openSync, readSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { isAbsolute, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
const APPROVAL_ID = 'v2-contract-corpus-baseline-20261023-v1'
const PATHS = Object.freeze([
  'packages/contracts/v2/fixtures.json',
  'packages/contracts/v2/binding-regressions.json',
  'packages/contracts/v2/frame-fixtures.json',
])
const RECORD_LIMIT = 8192
const CORPUS_LIMIT = 1048576
const SHA256 = /^[a-f0-9]{64}$/
const ERROR_CODES = new Set([
  'NOT_REGULAR_FILE',
  'FILE_CHANGED',
  'FILE_LIMIT',
  'CORPUS_SIZE_MISMATCH',
  'FILE_READ_FAILED',
  'FILE_CLOSE_FAILED',
  'APPROVAL_SHAPE',
  'APPROVAL_SCOPE',
  'APPROVAL_PATHS',
  'CORPUS_ROOT',
  'CORPUS_PATH',
  'OPERATOR_INPUT_REQUIRED',
  'APPROVAL_DIGEST_MISMATCH',
  'APPROVAL_JSON',
  'CORPUS_READ_FAILED',
  'CORPUS_DIGEST_MISMATCH',
])
const RECORD_KEYS = [
  'schemaVersion',
  'approvalId',
  'approvedAt',
  'approvedByControllerThread',
  'decision',
  'sourceBase',
  'sourceRefKind',
  'records',
  'authorityScope',
  'semanticBoundary',
  'expectedMustNotComeFromCandidateOrDynamicRegistry',
  'candidateMayNotSelfApproveOrUpdateThisRecord',
  'replacementRequires',
  'doesNotClose',
]

function reject(code, resource) {
  const error = new Error(code)
  error.code = code
  if (PATHS.includes(resource)) error.resource = resource
  throw error
}
function exactObject(value, keys) {
  return (
    value !== null &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    Object.keys(value).length === keys.length &&
    keys.every((key) => Object.hasOwn(value, key))
  )
}
function boundedText(value, maximum = 2048) {
  return typeof value === 'string' && value.length > 0 && value.length <= maximum
}
function absolutePath(value) {
  return boundedText(value, 4096) && isAbsolute(value)
}

// Local operator file reader only: no adapters, registry, environment discovery or writes.
// A fixed maximum and the descriptor's size are checked before allocating a body buffer.
function readBounded(path, maximum, expectedSize) {
  let fd
  let first
  try {
    const link = lstatSync(path)
    if (!link.isFile() || link.isSymbolicLink()) reject('NOT_REGULAR_FILE')
    fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0))
    const before = fstatSync(fd)
    if (!before.isFile()) reject('NOT_REGULAR_FILE')
    if (before.dev !== link.dev || before.ino !== link.ino) reject('FILE_CHANGED')
    if (!Number.isSafeInteger(before.size) || before.size < 0 || before.size > maximum)
      reject('FILE_LIMIT')
    if (expectedSize !== undefined && before.size !== expectedSize) reject('CORPUS_SIZE_MISMATCH')
    const buffer = Buffer.allocUnsafe(before.size + 1)
    let length = 0
    while (length < buffer.length) {
      const count = readSync(fd, buffer, length, buffer.length - length, null)
      if (count === 0) break
      length += count
    }
    const after = fstatSync(fd)
    if (length !== before.size || after.size !== before.size) reject('FILE_CHANGED')
    return buffer.subarray(0, length)
  } catch (error) {
    first = error
    if (error && typeof error === 'object' && ERROR_CODES.has(error.code)) throw error
    reject('FILE_READ_FAILED')
  } finally {
    if (fd !== undefined) {
      try {
        closeSync(fd)
      } catch {
        if (!first) reject('FILE_CLOSE_FAILED')
      }
    }
  }
}
function validateRecord(value) {
  if (!exactObject(value, RECORD_KEYS)) reject('APPROVAL_SHAPE')
  if (
    value.schemaVersion !== 1 ||
    value.approvalId !== APPROVAL_ID ||
    value.sourceBase !== BASE ||
    value.expectedMustNotComeFromCandidateOrDynamicRegistry !== true ||
    value.candidateMayNotSelfApproveOrUpdateThisRecord !== true
  )
    reject('APPROVAL_SCOPE')
  // These fields are provenance text, not authentication. Authentication is the external SHA.
  for (const key of [
    'approvedAt',
    'approvedByControllerThread',
    'decision',
    'sourceRefKind',
    'authorityScope',
    'semanticBoundary',
    'replacementRequires',
  ])
    if (!boundedText(value[key])) reject('APPROVAL_SHAPE')
  if (
    !Array.isArray(value.doesNotClose) ||
    value.doesNotClose.length > 8 ||
    !value.doesNotClose.every((item) => boundedText(item, 128))
  )
    reject('APPROVAL_SHAPE')
  if (!Array.isArray(value.records) || value.records.length !== 3) reject('APPROVAL_PATHS')
  const byPath = new Map()
  for (const record of value.records) {
    if (!exactObject(record, ['path', 'bytes', 'sha256', 'sourceGitRef'])) reject('APPROVAL_SHAPE')
    if (!PATHS.includes(record.path) || byPath.has(record.path)) reject('APPROVAL_PATHS')
    if (
      !Number.isSafeInteger(record.bytes) ||
      record.bytes < 1 ||
      record.bytes > CORPUS_LIMIT ||
      typeof record.sha256 !== 'string' ||
      !SHA256.test(record.sha256) ||
      record.sourceGitRef !== BASE
    )
      reject('APPROVAL_SHAPE')
    byPath.set(record.path, record)
  }
  if (PATHS.some((path) => !byPath.has(path))) reject('APPROVAL_PATHS')
  return byPath
}
function corpusFile(root, relative) {
  let location = root
  if (!lstatSync(root).isDirectory() || lstatSync(root).isSymbolicLink()) reject('CORPUS_ROOT')
  const parts = relative.split('/')
  for (const part of parts.slice(0, -1)) {
    location = join(location, part)
    const entry = lstatSync(location)
    if (!entry.isDirectory() || entry.isSymbolicLink()) reject('CORPUS_PATH')
  }
  return join(location, parts.at(-1))
}

export function verifyV2Corpus(options) {
  if (
    !exactObject(options, ['corpusRoot', 'approvalRecordPath', 'expectedApprovalSHA256']) ||
    !absolutePath(options.corpusRoot) ||
    !absolutePath(options.approvalRecordPath) ||
    typeof options.expectedApprovalSHA256 !== 'string' ||
    options.expectedApprovalSHA256.length !== 64 ||
    !SHA256.test(options.expectedApprovalSHA256)
  )
    reject('OPERATOR_INPUT_REQUIRED')
  const raw = readBounded(options.approvalRecordPath, RECORD_LIMIT)
  const actualApprovalSHA256 = createHash('sha256').update(raw).digest('hex')
  if (actualApprovalSHA256 !== options.expectedApprovalSHA256) reject('APPROVAL_DIGEST_MISMATCH')
  let record
  try {
    record = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(raw))
  } catch {
    reject('APPROVAL_JSON')
  }
  const byPath = validateRecord(record)
  const records = []
  for (const path of PATHS) {
    const approved = byPath.get(path)
    let actual
    try {
      actual = readBounded(corpusFile(options.corpusRoot, path), CORPUS_LIMIT, approved.bytes)
    } catch (error) {
      if (error && ERROR_CODES.has(error.code)) {
        error.resource = path
        throw error
      }
      reject('CORPUS_READ_FAILED', path)
    }
    const sha256 = createHash('sha256').update(actual).digest('hex')
    if (sha256 !== approved.sha256) reject('CORPUS_DIGEST_MISMATCH', path)
    records.push({ path, bytes: actual.length, sha256 })
  }
  return {
    ok: true,
    approvalId: APPROVAL_ID,
    approvalSHA256: actualApprovalSHA256,
    sourceBase: BASE,
    records,
  }
}

export function parseOperatorArguments(args) {
  const names = {
    '--corpus-root': 'corpusRoot',
    '--approval-record': 'approvalRecordPath',
    '--expected-approval-sha256': 'expectedApprovalSHA256',
  }
  if (!Array.isArray(args) || args.length !== 6) reject('OPERATOR_INPUT_REQUIRED')
  const options = {}
  for (let index = 0; index < args.length; index += 2) {
    const flag = args[index]
    if (typeof flag !== 'string' || flag.length > 32 || !Object.hasOwn(names, flag))
      reject('OPERATOR_INPUT_REQUIRED')
    const key = names[flag]
    const value = args[index + 1]
    if (Object.hasOwn(options, key) || typeof value !== 'string' || !value)
      reject('OPERATOR_INPUT_REQUIRED')
    options[key] = value
  }
  return options
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    console.log(JSON.stringify(verifyV2Corpus(parseOperatorArguments(process.argv.slice(2)))))
  } catch (error) {
    // Only a finite code and one of the three fixed relative resource names can be emitted.
    const code = ERROR_CODES.has(error?.code) ? error.code : 'V2_CORPUS_BASELINE_REJECTED'
    const resource = PATHS.includes(error?.resource) ? { resource: error.resource } : {}
    console.error(JSON.stringify({ ok: false, code, ...resource }))
    process.exitCode = 1
  }
}
