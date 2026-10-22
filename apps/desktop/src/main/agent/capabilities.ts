import { z } from 'zod'
import { AgentError } from './errors'
import { CODEC_VERSION, DEEPSEEK_ENDPOINT, REQUEST_MODEL } from './deepseek-codec'

export const providerSignatureSchema = z
  .object({
    endpoint: z.literal(DEEPSEEK_ENDPOINT),
    requestedModel: z.literal(REQUEST_MODEL),
    returnedModel: z.string().min(1).max(256),
    fingerprint: z.string().max(256).nullable(),
    mode: z.enum(['enabled', 'disabled']),
    effort: z.enum(['low', 'high', 'max']),
    codecVersion: z.literal(CODEC_VERSION),
  })
  .strict()
const hash = z.string().regex(/^[a-f0-9]{64}$/)
const probeSchema = z
  .object({
    source: z.enum(['synthetic', 'provider']),
    testedAt: z.iso.datetime(),
    signature: providerSignatureSchema,
    connection: z.enum(['passed', 'failed', 'not-run']),
    structuredOutput: z.enum(['passed', 'failed', 'not-run']),
    toolRoundTrip: z.enum(['passed', 'failed', 'not-run']),
    evaluation: z
      .object({
        manifestHash: hash,
        completed: z.boolean(),
        fabricatedResults: z.number().int().nonnegative(),
        allFailuresLocated: z.boolean(),
        allRequirementsPassed: z.boolean(),
      })
      .strict()
      .nullable(),
  })
  .strict()
export type ProviderSignature = z.infer<typeof providerSignatureSchema>
/** Consumes host-verifiable receipts, not model assertions. Does not perform any probe. */
export function assessCapabilities(value: unknown, pinned: unknown, expectedManifestHash: string) {
  const parsed = probeSchema.safeParse(value)
  const baseline = providerSignatureSchema.safeParse(pinned)
  if (!parsed.success || !baseline.success || !hash.safeParse(expectedManifestHash).success) {
    throw new AgentError('INVALID_PROTOCOL')
  }
  const probe = parsed.data
  const drifted = Object.keys(baseline.data).some((key) => {
    const field = key as keyof ProviderSignature
    return baseline.data[field] !== probe.signature[field]
  })
  const evaluation = probe.evaluation
  const protocolPassed =
    probe.connection === 'passed' &&
    probe.structuredOutput === 'passed' &&
    probe.toolRoundTrip === 'passed'
  const qualityPassed =
    evaluation?.manifestHash === expectedManifestHash &&
    evaluation.completed &&
    evaluation.fabricatedResults === 0 &&
    evaluation.allFailuresLocated &&
    evaluation.allRequirementsPassed
  const state =
    probe.source === 'synthetic'
      ? 'synthetic-only'
      : drifted
        ? 'drift-requires-evaluation'
        : !protocolPassed
          ? 'capability-incomplete'
          : !qualityPassed
            ? 'evaluation-required'
            : 'ready'
  return {
    state,
    drifted,
    connection: probe.connection,
    structuredOutput: probe.structuredOutput,
    toolRoundTrip: probe.toolRoundTrip,
    testedAt: probe.testedAt,
    signature: probe.signature,
  }
}
