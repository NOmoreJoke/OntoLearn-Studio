import { z } from 'zod'

// Main-process internals, deliberately not an IPC or Python wire contract.
export const opaqueId = z.string().uuid()
export const purposeSchema = z.enum(['explain', 'suggest', 'review'])
export const privacySchema = z.enum(['local', 'minimal', 'project'])
export const scopesSchema = z.array(opaqueId).min(1).max(256)
export const partKindSchema = z.enum(['selected', 'tool', 'history', 'summary', 'error'])
export const invocationSchema = z
  .object({
    projectId: opaqueId,
    configId: opaqueId,
    grantId: opaqueId,
    purpose: purposeSchema,
    materials: z.array(opaqueId).min(1).max(64),
  })
  .strict()

export const configSchema = z
  .object({
    id: opaqueId,
    endpoint: z.string().min(1).max(2048),
    credentialRef: opaqueId,
    principal: opaqueId,
    credentialVersion: opaqueId,
    model: z.string().regex(/^[A-Za-z0-9._:/-]{1,128}$/),
  })
  .strict()

export const failureCodes = [
  'INVALID_INPUT',
  'LOCAL_ONLY',
  'AUTHORIZATION_REQUIRED',
  'SCOPE_EXCEEDED',
  'CONFIGURATION_CHANGED',
  'CREDENTIAL_UNAVAILABLE',
  'AUDIT_UNAVAILABLE',
  'REDIRECT_REJECTED',
  'MODEL_UNAVAILABLE',
  'RESPONSE_LIMIT',
  'CANCELLED',
] as const
export type FailureCode = (typeof failureCodes)[number]
export class GatewayFailure extends Error {
  constructor(readonly code: FailureCode) {
    super(code)
  }
}

export function parse<T>(schema: z.ZodType<T>, input: unknown): T {
  const result = schema.safeParse(input)
  if (!result.success) throw new GatewayFailure('INVALID_INPUT')
  return result.data
}

export type EndpointPolicy = 'https' | 'loopback-probe-only'
export function normalizeEndpoint(input: string, policy: EndpointPolicy = 'https'): string {
  try {
    const url = new URL(input)
    if (
      input.trim() !== input ||
      url.username ||
      url.password ||
      url.search ||
      url.hash ||
      input.includes('?') ||
      input.includes('#') ||
      /[\\\s]/u.test(input) ||
      [...input].some(
        (character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127,
      )
    )
      throw new Error()
    if (policy === 'loopback-probe-only') {
      // No DNS names, LAN destinations or automatic ephemeral product HTTP server.
      if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !url.port) throw new Error()
    } else if (url.protocol !== 'https:') throw new Error()
    return url.href
  } catch {
    throw new GatewayFailure('INVALID_INPUT')
  }
}
