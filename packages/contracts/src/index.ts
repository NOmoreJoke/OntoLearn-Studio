import { z } from 'zod'

export const PROTOCOL_VERSION = 1 as const
export const healthSchema = z
  .object({
    protocolVersion: z.literal(PROTOCOL_VERSION),
    engineVersion: z.string().min(1),
    status: z.literal('ok'),
    capabilities: z.array(z.literal('health')),
  })
  .strict()

export type EngineHealth = z.infer<typeof healthSchema>
export type HealthResult = { ok: true; data: EngineHealth } | { ok: false; error: string }

// Renderer 只获得按业务命名的方法；不得暴露通用 invoke、spawn 或任意文件路径。
export interface DesktopBridge {
  getEngineHealth(): Promise<HealthResult>
}
