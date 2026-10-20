import fs from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'
import { randomUUID } from 'node:crypto'
import { afterEach, describe, expect, it } from 'vitest'
import {
  ConfigurationRepository,
  type StoredConfiguration,
} from '../../apps/desktop/src/main/model-gateway/configuration-repository'

const cleanups: (() => Promise<unknown>)[] = []
afterEach(async () => {
  for (const cleanup of cleanups.splice(0).reverse()) await cleanup()
})
async function fixture() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'i06-configuration-'))
  cleanups.push(() => fs.rm(root, { recursive: true, force: true }))
  const location = {
    userDataPath: path.join(root, 'app'),
    excludedRoots: [path.join(root, 'project')],
  }
  const repository = await ConfigurationRepository.open(location)
  cleanups.push(() => repository.close())
  const directory = path.join(location.userDataPath, 'model-gateway-private-v1/configurations')
  return { repository, location, directory }
}
function config(): StoredConfiguration {
  return {
    configurationId: randomUUID(),
    configurationVersion: randomUUID(),
    displayName: 'Fixture',
    endpoint: 'https://example.invalid/v1',
    model: 'fixture',
    binding: null,
  }
}
describe('I06 app-private configuration journal', () => {
  it('publishes immutable complete states and recovers without grants or plaintext secret', async () => {
    const f = await fixture(),
      initial = config()
    await f.repository.replace([], [initial])
    const next = {
      ...initial,
      configurationVersion: randomUUID(),
      binding: { ref: randomUUID(), principal: randomUUID(), version: randomUUID() },
    }
    await f.repository.replace([initial], [next])
    const recovered = await ConfigurationRepository.open(f.location)
    cleanups.push(() => recovered.close())
    expect(await recovered.load()).toEqual([next])
    for (const name of await fs.readdir(f.directory)) {
      const raw = await fs.readFile(path.join(f.directory, name), 'utf8')
      expect(raw).not.toMatch(/secret|grantId|previewId|selectionId/)
      expect((await fs.stat(path.join(f.directory, name))).mode & 0o777).toBe(0o600)
    }
  })
  it('copies before await and refuses stale state, duplicate identity and secret-bearing objects', async () => {
    const f = await fixture(),
      initial = config()
    const first = f.repository.replace([], [initial])
    initial.displayName = 'MUTATED'
    await first
    const current = await f.repository.load()
    expect(current[0].displayName).toBe('Fixture')
    await expect(f.repository.replace([], [config()])).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    await expect(f.repository.replace(current, [current[0], current[0]])).rejects.toThrow(
      'CREDENTIAL_UNAVAILABLE',
    )
    await expect(
      f.repository.replace(current, [{ ...current[0], secret: 'MUST_NOT_STORE' } as never]),
    ).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    expect(await f.repository.load()).toEqual(current)
  })
  it('keeps a simultaneous stale writer from replacing the first committed configuration', async () => {
    const f = await fixture(),
      left = config(),
      right = config()
    const results = await Promise.allSettled([
      f.repository.replace([], [left]),
      f.repository.replace([], [right]),
    ])
    expect(results.map((result) => result.status)).toEqual(['fulfilled', 'rejected'])
    expect(await f.repository.load()).toEqual([left])
  })
  it('gives competing repository instances one immutable sequence slot, preserving recovery', async () => {
    const f = await fixture()
    let ready = 0,
      release!: () => void
    const barrier = new Promise<void>((resolve) => {
      release = resolve
    })
    const observer = async (phase: string) => {
      if (phase !== 'file-synced') return
      if (++ready === 2) release()
      await barrier
    }
    const left = await ConfigurationRepository.open(f.location, observer)
    const right = await ConfigurationRepository.open(f.location, observer)
    cleanups.push(
      () => left.close(),
      () => right.close(),
    )
    const options = [config(), config()]
    const result = await Promise.allSettled([
      left.replace([], [options[0]]),
      right.replace([], [options[1]]),
    ])
    expect(result.filter((value) => value.status === 'fulfilled')).toHaveLength(1)
    expect(result.filter((value) => value.status === 'rejected')).toHaveLength(1)
    const winner = result.findIndex((value) => value.status === 'fulfilled')
    const recovered = await ConfigurationRepository.open(f.location)
    cleanups.push(() => recovered.close())
    expect(await recovered.load()).toEqual([options[winner]])
    expect(
      (await fs.readdir(f.directory)).filter((name) => name.endsWith('.configuration')),
    ).toHaveLength(1)
  })
  it('retains a published record after an uncertain durability failure so callers must fail closed', async () => {
    const f = await fixture(),
      initial = config()
    const failing = await ConfigurationRepository.open(f.location, (phase) => {
      if (phase === 'published') throw new Error('SYNTHETIC_POST_LINK_EIO')
    })
    cleanups.push(() => failing.close())
    await expect(failing.replace([], [initial])).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    expect(await f.repository.load()).toEqual([initial])
  })
  it('fails closed on corrupt committed state while ignoring and retaining incomplete pending bytes', async () => {
    const f = await fixture(),
      initial = config()
    const pending = path.join(f.directory, `.pending-${process.pid}-${randomUUID()}`)
    await fs.writeFile(pending, 'INCOMPLETE', { mode: 0o600 })
    await f.repository.replace([], [initial])
    expect(await fs.readFile(pending, 'utf8')).toBe('INCOMPLETE')
    const record = (await fs.readdir(f.directory)).find((name) => name.endsWith('.configuration'))!
    await fs.writeFile(path.join(f.directory, record), '{"secret":"CORRUPTED"}', { mode: 0o600 })
    await expect(ConfigurationRepository.open(f.location)).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    await expect(f.repository.load()).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    expect(await fs.readFile(path.join(f.directory, record), 'utf8')).toContain('CORRUPTED')
  })
})
