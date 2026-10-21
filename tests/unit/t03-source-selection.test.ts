import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { createHash } from 'node:crypto'
import { mkdtemp, mkdir, rm, unlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import {
  MAX_SOURCE_BYTES,
  SourceFailure,
  SourceSelectionBroker,
} from '../../apps/desktop/src/main/mapping/source-selection'
import type { SourceSummary } from '../../apps/desktop/src/main/mapping/source-selection'

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (error: Error) => void
  const promise = new Promise<T>((yes, no) => {
    resolve = yes
    reject = no
  })
  return { promise, resolve, reject }
}
const bytes = Buffer.from('equipment_id,equipment_name\n001,泵站A\n')
const hash = (value: Uint8Array) => createHash('sha256').update(value).digest('hex')

let folder: string
let csv: string
let xlsx: string
let brokers: SourceSelectionBroker[]
function broker(picker: () => Promise<string | null>, maxBytes?: number) {
  const value = new SourceSelectionBroker(picker, { maxBytes })
  brokers.push(value)
  return value
}
async function chosen(value: SourceSelectionBroker, project = 'P') {
  const scope = value.openProject(project)
  const selected = await value.pick(scope)
  expect(selected).not.toBeNull()
  return { scope, selected: selected as SourceSummary }
}
beforeEach(async () => {
  folder = await mkdtemp(join(tmpdir(), 't03-source-selection-'))
  csv = join(folder, 'private-selected-source.csv')
  xlsx = join(folder, 'private-selected-source.xlsx')
  await writeFile(csv, bytes)
  // Broker tests validate real file bytes/context only; workbook parsing is deliberately deferred.
  await writeFile(xlsx, Buffer.from('unvalidated workbook candidate bytes'))
  brokers = []
})
afterEach(async () => {
  for (const value of brokers) value.dispose()
  await rm(folder, { recursive: true, force: true })
})

describe('trusted main-only source selection over real temporary files', () => {
  it('reads exact bytes/hash with opaque metadata, and returned byte mutation cannot change the file/proof', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    expect(selected).toMatchObject({
      projectId: 'P',
      lifecycleId: scope.lifecycleId,
      format: 'csv',
      encoding: 'utf-8-sig',
      sheet: null,
      byteLength: bytes.length,
      sha256: hash(bytes),
    })
    expect(selected.selectionId).not.toBe(csv)
    expect(JSON.stringify(selected)).not.toContain(folder)
    expect(JSON.stringify(selected)).not.toContain('private-selected-source')
    const snapshot = await value.readForPreview(scope, selected.selectionId)
    expect(Buffer.from(snapshot.bytes)).toEqual(bytes)
    snapshot.bytes[0] = 0
    const fresh = await value.readForCommit(scope, snapshot.proof)
    expect(Buffer.from(fresh.bytes)).toEqual(bytes)
    expect(fresh.bytes.length).toBe(bytes.length)
  })

  it('binds explicit CSV encoding, replacing the old selection and proof', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    const old = await value.readForPreview(scope, selected.selectionId)
    const configured = await value.configure(scope, selected.selectionId, {
      encoding: 'gb18030',
      sheet: null,
    })
    expect(configured.encoding).toBe('gb18030')
    expect(configured.sha256).toBe(selected.sha256)
    expect(configured.selectionId).not.toBe(selected.selectionId)
    await expect(value.readForCommit(scope, old.proof)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
    await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'stale-context',
    })
  })

  it('requires an explicit XLSX sheet and invalidates the old sheet even for identical file bytes', async () => {
    const value = broker(async () => xlsx)
    const { scope, selected } = await chosen(value)
    expect(selected).toMatchObject({ format: 'xlsx', encoding: null, sheet: null })
    await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'sheet-required',
    })
    const first = await value.configure(scope, selected.selectionId, {
      encoding: null,
      sheet: '设备A',
    })
    const snapshot = await value.readForPreview(scope, first.selectionId)
    const second = await value.configure(scope, first.selectionId, {
      encoding: null,
      sheet: '设备B',
    })
    expect(second.sha256).toBe(first.sha256)
    expect(second.sheet).toBe('设备B')
    await expect(value.readForCommit(scope, snapshot.proof)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
    expect((await value.readForPreview(scope, second.selectionId)).summary.sheet).toBe('设备B')
  })

  it('allows real XLSX bytes to be inspected before sheet selection without issuing a commit proof', async () => {
    const raw = Buffer.from('unvalidated workbook candidate bytes')
    const value = broker(async () => xlsx)
    const { scope, selected } = await chosen(value)
    const inspected = await value.readForInspection(scope, selected.selectionId)
    expect(inspected.summary.sheet).toBeNull()
    expect(Buffer.from(inspected.bytes)).toEqual(raw)
    expect(Object.keys(inspected).sort()).toEqual(['bytes', 'summary'])
    await expect(value.readForCommit(scope, inspected as never)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
    await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'sheet-required',
    })
    inspected.bytes[0] = 0
    expect(Buffer.from((await value.readForInspection(scope, selected.selectionId)).bytes)).toEqual(
      raw,
    )
  })

  it('an inspection invalidated by configuration cannot return late bytes or resurrect its selection', async () => {
    const value = broker(async () => xlsx)
    const { scope, selected } = await chosen(value)
    const inspection = value
      .readForInspection(scope, selected.selectionId)
      .catch((failure) => failure)
    const configuring = value.configure(scope, selected.selectionId, { encoding: null, sheet: 'A' })
    await expect(value.readForInspection(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'busy',
    })
    const latest = await configuring
    expect(await inspection).toMatchObject({ kind: 'stale-context' })
    await expect(value.readForInspection(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'stale-context',
    })
    expect((await value.readForInspection(scope, latest.selectionId)).summary.sheet).toBe('A')
  })

  it('inspection rechecks the real source hash and a changed file invalidates existing preview proofs', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    const snapshot = await value.readForPreview(scope, selected.selectionId)
    await writeFile(csv, Buffer.from('equipment_id,equipment_name\n002,泵站A\n'))
    await expect(value.readForInspection(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'source-changed',
    })
    await writeFile(csv, bytes)
    await expect(value.readForCommit(scope, snapshot.proof)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
  })

  it('captures options before real async I/O so later caller mutation cannot change the operation', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    const options: { encoding: 'utf-8' | 'big5'; sheet: null } = { encoding: 'utf-8', sheet: null }
    const operation = value.configure(scope, selected.selectionId, options)
    options.encoding = 'big5'
    expect((await operation).encoding).toBe('utf-8')
  })

  it('rejects equal-looking scope/proof objects and another broker without interpreting them as paths', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    const snapshot = await value.readForPreview(scope, selected.selectionId)
    await expect(value.readForPreview({ ...scope }, selected.selectionId)).rejects.toMatchObject({
      kind: 'stale-context',
    })
    await expect(value.readForCommit(scope, { ...snapshot.proof })).rejects.toMatchObject({
      kind: 'stale-proof',
    })
    const other = broker(async () => csv)
    const next = await chosen(other)
    await expect(other.readForCommit(next.scope, snapshot.proof)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
    expect(Buffer.from((await value.readForCommit(scope, snapshot.proof)).bytes)).toEqual(bytes)
  })

  it('rejects actual source changes before preview and invalidates the handle', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    await writeFile(csv, Buffer.from('changed real file'))
    await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'source-changed',
    })
    await writeFile(csv, bytes)
    await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'stale-context',
    })
  })

  it('rejects equal-length source changes after preview; restoring bytes cannot revive the old proof', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    const snapshot = await value.readForPreview(scope, selected.selectionId)
    const changed = Buffer.from(bytes)
    changed[0] ^= 1
    await writeFile(csv, changed)
    await expect(value.readForCommit(scope, snapshot.proof)).rejects.toMatchObject({
      kind: 'source-changed',
    })
    await writeFile(csv, bytes)
    await expect(value.readForCommit(scope, snapshot.proof)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
  })

  it('handles a removed file with a safe error and does not revive old selection after recreation', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    await unlink(csv)
    const error = await value
      .readForPreview(scope, selected.selectionId)
      .catch((failure) => failure)
    expect(error).toBeInstanceOf(SourceFailure)
    expect(error.kind).toBe('unavailable')
    expect(String(error)).not.toContain(folder)
    expect(JSON.stringify(error)).not.toContain(folder)
    expect(error).not.toHaveProperty('cause')
    await writeFile(csv, bytes)
    await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'stale-context',
    })
  })

  it('rejects growth beyond its byte budget on a real re-read', async () => {
    await writeFile(csv, '001')
    const value = broker(async () => csv, 4)
    const { scope, selected } = await chosen(value)
    await writeFile(csv, '00199')
    await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
      kind: 'limit',
    })
    await expect(value.pick(scope)).rejects.toMatchObject({ kind: 'limit' })
  })

  it('rejects a directory and unsupported extension without a raw filesystem diagnostic', async () => {
    const directory = join(folder, 'not-file.csv')
    await mkdir(directory)
    const value = broker(async () => directory)
    const scope = value.openProject('P')
    await expect(value.pick(scope)).rejects.toMatchObject({
      kind: 'unsupported-file',
      message: 'Source selection failed',
    })
    const oldFormat = broker(async () => join(folder, 'unread.xls'))
    await expect(oldFormat.pick(oldFormat.openProject('P'))).rejects.toMatchObject({
      kind: 'unsupported-file',
    })
  })

  it.skipIf(process.platform === 'win32')(
    'rejects a real FIFO without waiting for a writer',
    async () => {
      const path = join(folder, 'not-regular.csv')
      expect(spawnSync('mkfifo', [path]).status).toBe(0)
      const value = broker(async () => path)
      await expect(value.pick(value.openProject('P'))).rejects.toMatchObject({
        kind: 'unsupported-file',
      })
    },
    5000,
  )

  it('rejects bad trusted picker values/limits with fixed internal errors', async () => {
    const value = broker(async () => 'relative.csv')
    await expect(value.pick(value.openProject('P'))).rejects.toMatchObject({
      kind: 'invalid-choice',
    })
    const failed = broker(async () => {
      throw new Error(`raw path ${csv}`)
    })
    const error = await failed.pick(failed.openProject('P')).catch((failure) => failure)
    expect(error).toMatchObject({ kind: 'picker-failed', message: 'Source selection failed' })
    expect(JSON.stringify(error)).not.toContain(csv)
    for (const maxBytes of [0, -1, NaN, Infinity, MAX_SOURCE_BYTES + 1]) {
      expect(() => broker(async () => csv, maxBytes)).toThrow(SourceFailure)
    }
  })
})

describe('selection lifecycle and late outcomes', () => {
  it('discards an older picker success after a newer selection and aborts the old host signal', async () => {
    const first = deferred<string | null>(),
      second = deferred<string | null>()
    const queue = [first, second]
    const signals: AbortSignal[] = []
    const value = new SourceSelectionBroker(async (signal) => {
      signals.push(signal)
      return queue.shift()!.promise
    })
    brokers.push(value)
    const scope = value.openProject('P')
    const old = value.pick(scope).catch((failure) => failure)
    const latest = value.pick(scope)
    expect(signals[0].aborted).toBe(true)
    second.resolve(csv)
    const selected = (await latest)!
    first.resolve(xlsx)
    expect(await old).toMatchObject({ kind: 'stale-context' })
    expect((await value.readForPreview(scope, selected.selectionId)).summary.format).toBe('csv')
  })

  it('a late picker failure does not cancel the successful newer selection', async () => {
    const first = deferred<string | null>()
    let calls = 0
    const value = broker(async () => (++calls === 1 ? first.promise : csv))
    const scope = value.openProject('P')
    const old = value.pick(scope).catch((failure) => failure)
    const selected = (await value.pick(scope))!
    first.reject(new Error(`private ${xlsx}`))
    expect(await old).toMatchObject({ kind: 'stale-context' })
    expect(Buffer.from((await value.readForPreview(scope, selected.selectionId)).bytes)).toEqual(
      bytes,
    )
  })

  it.each(['cancel', 'close', 'switch', 'reopen', 'dispose'] as const)(
    'invalidates a pending picker on %s',
    async (action) => {
      const choice = deferred<string | null>()
      const value = broker(async () => choice.promise)
      const scope = value.openProject('P')
      const pending = value.pick(scope).catch((failure) => failure)
      if (action === 'cancel') value.cancel(scope)
      else if (action === 'close') value.closeProject(scope)
      else if (action === 'switch') value.openProject('other')
      else if (action === 'reopen') value.openProject('P')
      else value.dispose()
      choice.resolve(csv)
      expect(await pending).toMatchObject({
        kind: action === 'dispose' ? 'disposed' : 'stale-context',
      })
    },
  )

  it('cancels an in-flight real file re-read without invalidating the new selection', async () => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    const pending = value.readForPreview(scope, selected.selectionId).catch((failure) => failure)
    value.cancel(scope)
    const fresh = (await value.pick(scope))!
    expect(await pending).toMatchObject({ kind: 'stale-context' })
    expect(Buffer.from((await value.readForPreview(scope, fresh.selectionId)).bytes)).toEqual(bytes)
  })

  it('a deliberate picker cancellation clears the previous choice and cannot be used as job success', async () => {
    let calls = 0
    const value = broker(async () => (++calls === 1 ? csv : null))
    const { scope, selected } = await chosen(value)
    const snapshot = await value.readForPreview(scope, selected.selectionId)
    expect(await value.pick(scope)).toBeNull()
    await expect(value.readForCommit(scope, snapshot.proof)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
  })
})

it('an abort listener that starts a newer selection cannot be overwritten by the interrupted outer pick', async () => {
  const old = deferred<string | null>()
  let replacement: Promise<SourceSummary | null> | undefined
  let calls = 0
  const value = new SourceSelectionBroker(async (signal) => {
    ++calls
    if (calls === 1) {
      signal.addEventListener(
        'abort',
        () => {
          replacement = value.pick(scope)
        },
        { once: true },
      )
      return old.promise
    }
    return csv
  })
  brokers.push(value)
  const scope = value.openProject('P')
  const first = value.pick(scope).catch((failure) => failure)
  const interruptedOuter = value.pick(scope).catch((failure) => failure)
  expect(await interruptedOuter).toMatchObject({ kind: 'stale-context' })
  expect(calls).toBe(2)
  const selected = (await replacement)!
  old.resolve(csv)
  expect(await first).toMatchObject({ kind: 'stale-context' })
  expect(Buffer.from((await value.readForPreview(scope, selected.selectionId)).bytes)).toEqual(
    bytes,
  )
})

it('bounds actual concurrent filesystem reads and a rejected extra read does not poison the selection', async () => {
  const value = broker(async () => csv)
  const { scope, selected } = await chosen(value)
  const one = value.readForPreview(scope, selected.selectionId)
  const two = value.readForPreview(scope, selected.selectionId)
  await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
    kind: 'busy',
  })
  const completed = await Promise.all([one, two])
  expect(completed.map((item) => Buffer.from(item.bytes))).toEqual([bytes, bytes])
  expect(Buffer.from((await value.readForCommit(scope, completed[0].proof)).bytes)).toEqual(bytes)
})

it.each(['csv', 'xlsx'] as const)(
  'the newest concurrent %s configuration wins and immediately revokes the old proof',
  async (format) => {
    const value = broker(async () => (format === 'csv' ? csv : xlsx))
    const { scope, selected } = await chosen(value)
    const initial =
      format === 'csv'
        ? selected
        : await value.configure(scope, selected.selectionId, { encoding: null, sheet: '初始' })
    const snapshot = await value.readForPreview(scope, initial.selectionId)
    const first = value
      .configure(
        scope,
        initial.selectionId,
        format === 'csv' ? { encoding: 'utf-8', sheet: null } : { encoding: null, sheet: '旧表' },
      )
      .catch((failure) => failure)
    await expect(value.readForCommit(scope, snapshot.proof)).rejects.toMatchObject({
      kind: 'stale-proof',
    })
    await expect(value.readForPreview(scope, initial.selectionId)).rejects.toMatchObject({
      kind: 'busy',
    })
    const latest = await value.configure(
      scope,
      initial.selectionId,
      format === 'csv' ? { encoding: 'big5', sheet: null } : { encoding: null, sheet: '新表' },
    )
    expect(await first).toMatchObject({ kind: 'stale-context' })
    const actual = await value.readForPreview(scope, latest.selectionId)
    expect(actual.summary).toMatchObject(
      format === 'csv' ? { encoding: 'big5', sheet: null } : { encoding: null, sheet: '新表' },
    )
    expect(actual.summary.generation).toBeGreaterThan(initial.generation)
  },
)

it.each(['cancel', 'pick'] as const)(
  'a pending configuration cannot survive a newer %s',
  async (action) => {
    const value = broker(async () => csv)
    const { scope, selected } = await chosen(value)
    const pending = value
      .configure(scope, selected.selectionId, { encoding: 'big5', sheet: null })
      .catch((failure) => failure)
    if (action === 'cancel') value.cancel(scope)
    const fresh = (await value.pick(scope))!
    expect(await pending).toMatchObject({ kind: 'stale-context' })
    expect((await value.readForPreview(scope, fresh.selectionId)).summary.encoding).toBe(
      'utf-8-sig',
    )
  },
)

it('a configuration exceeding the real operation cap revokes the source instead of restoring old options', async () => {
  const value = broker(async () => csv)
  const { scope, selected } = await chosen(value)
  const one = value.readForPreview(scope, selected.selectionId).catch((failure) => failure)
  const two = value.readForPreview(scope, selected.selectionId).catch((failure) => failure)
  await expect(
    value.configure(scope, selected.selectionId, { encoding: 'big5', sheet: null }),
  ).rejects.toMatchObject({ kind: 'busy' })
  expect(await one).toMatchObject({ kind: 'stale-context' })
  expect(await two).toMatchObject({ kind: 'stale-context' })
  await expect(value.readForPreview(scope, selected.selectionId)).rejects.toMatchObject({
    kind: 'stale-context',
  })
  const fresh = (await value.pick(scope))!
  expect((await value.readForPreview(scope, fresh.selectionId)).summary.encoding).toBe('utf-8-sig')
})

it('does not free a slot merely because a picker ignored cancellation; slots recover when it really settles', async () => {
  const first = deferred<string | null>(),
    second = deferred<string | null>()
  let calls = 0
  const value = broker(async () => {
    ++calls
    return calls === 1 ? first.promise : calls === 2 ? second.promise : csv
  })
  const scope = value.openProject('P')
  const one = value.pick(scope).catch((failure) => failure)
  const two = value.pick(scope).catch((failure) => failure)
  await expect(value.pick(scope)).rejects.toMatchObject({ kind: 'busy' })
  expect(calls).toBe(2)
  first.resolve(csv)
  second.resolve(csv)
  expect(await one).toMatchObject({ kind: 'stale-context' })
  expect(await two).toMatchObject({ kind: 'stale-context' })
  const fresh = (await value.pick(scope))!
  expect((await value.readForPreview(scope, fresh.selectionId)).summary.sha256).toBe(hash(bytes))
})
