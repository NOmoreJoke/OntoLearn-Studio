import { randomUUID } from 'node:crypto'
import { mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { dirname } from 'node:path'
import { agentModeSchema, type AgentMode } from '@ontolearn/contracts'
import { z } from 'zod'

const projectIdSchema = z.uuidv4()
const modesSchema = z.record(projectIdSchema, agentModeSchema)

/** App-local presentation preference, outside every project library. */
export class AgentModeStore {
  private readonly modes = new Map<string, AgentMode>()
  private unavailable = false

  constructor(private readonly file?: string) {
    if (!file) return
    try {
      const saved = modesSchema.parse(JSON.parse(readFileSync(file, 'utf8')))
      for (const [id, mode] of Object.entries(saved)) this.modes.set(id, mode)
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') this.unavailable = true
    }
  }

  get(projectId: string): AgentMode {
    return this.modes.get(projectId) ?? 'tutor'
  }

  set(projectId: string, mode: AgentMode): void {
    projectIdSchema.parse(projectId)
    agentModeSchema.parse(mode)
    if (this.unavailable) throw new Error('MODE_STORE_UNAVAILABLE')
    if (this.get(projectId) === mode) return
    const next = new Map(this.modes)
    if (mode === 'tutor') next.delete(projectId)
    else next.set(projectId, mode)
    if (this.file) {
      mkdirSync(dirname(this.file), { recursive: true, mode: 0o700 })
      const temporary = `${this.file}.${randomUUID()}.tmp`
      try {
        writeFileSync(temporary, JSON.stringify(Object.fromEntries(next)), {
          encoding: 'utf8',
          flag: 'wx',
          mode: 0o600,
          flush: true,
        })
        renameSync(temporary, this.file)
      } finally {
        rmSync(temporary, { force: true })
      }
    }
    this.modes.clear()
    for (const [id, saved] of next) this.modes.set(id, saved)
  }
}
