import { z } from 'zod'
import { contextSchema, type TrustedContext } from '../agent-service'
import { decodeStructuredContent, type AssistantMessage } from '../deepseek-codec'
import { AgentError } from '../errors'

const NAME_LIMIT_UTF16 = 128
const SPARQL_LIMIT_UTF16 = 65536
const TEXT_LIMIT_UTF16 = 4096

export type QueryDraftScope = 'asserted' | 'asserted+derived'
export type QueryDraftSource = 'model'

const queryScopeSchema = z.enum(['asserted', 'asserted+derived'])

/** A rejected string never gets replacement characters: isolated surrogates fail the whole decode. */
function hasIsolatedSurrogate(value: string): boolean {
  for (let index = 0; index < value.length; index += 1) {
    const unit = value.charCodeAt(index)
    if (unit >= 0xd800 && unit <= 0xdbff) {
      const next = index + 1 < value.length ? value.charCodeAt(index + 1) : -1
      if (!(next >= 0xdc00 && next <= 0xdfff)) return true
      index += 1
    } else if (unit >= 0xdc00 && unit <= 0xdfff) {
      return true
    }
  }
  return false
}

/** Raw UTF-16 limits; text stays verbatim with no trim, prefix or newline rewriting. */
const boundedText = (limit: number) =>
  z.string().superRefine((value, ctx) => {
    if (value.length > limit) ctx.addIssue({ code: 'custom', message: 'text limit' })
    if (hasIsolatedSurrogate(value)) ctx.addIssue({ code: 'custom', message: 'isolated surrogate' })
  })

const queryDraftContentSchema = z
  .object({
    kind: z.literal('query-draft'),
    name: boundedText(NAME_LIMIT_UTF16),
    description: boundedText(TEXT_LIMIT_UTF16),
    sparql: boundedText(SPARQL_LIMIT_UTF16),
    capabilityQuestion: boundedText(TEXT_LIMIT_UTF16),
  })
  .strict()
  .superRefine((value, ctx) => {
    if (value.name.trim().length === 0) ctx.addIssue({ code: 'custom', message: 'blank name' })
    if (value.sparql.trim().length === 0) ctx.addIssue({ code: 'custom', message: 'blank sparql' })
  })

/** Only the host supplies the query range; inputContext merely records the original input version. */
const hostInputSchema = z
  .object({
    inputContext: contextSchema,
    queryScope: queryScopeSchema,
  })
  .strict()

export type QueryDraftModelContent = z.infer<typeof queryDraftContentSchema>
export type QueryDraftHostInput = z.infer<typeof hostInputSchema>

export interface QueryDraft {
  name: string
  description: string
  sparql: string
  scope: QueryDraftScope
  capabilityQuestion: string
  source: QueryDraftSource
}

export interface QueryDraftProposal {
  kind: 'query-draft-proposal'
  inputContext: TrustedContext
  draft: QueryDraft
  requiresHumanReview: true
}

/**
 * Guarded host read: a hostile hostInput (throwing getters or proxies on any level) collapses
 * to the fixed code instead of letting its original exception cross the boundary.
 */
function readHostInput(hostInput: unknown): QueryDraftHostInput {
  try {
    const checked = hostInputSchema.safeParse(hostInput)
    if (checked.success) return checked.data
  } catch {
    // zod only converts schema failures; property-access throws must not leak raw errors.
  }
  throw new AgentError('INVALID_PROTOCOL')
}

/**
 * Pure decoder and host stamp only: no fetch, credentials, persistence or execution, and no
 * save/confirm/commit ability. A proposal is not a writable DomainPort outcome; consumers must
 * re-validate against their own draft schema and the current project revision before any
 * display, save or execution, and the real read-only query gate stays downstream.
 */
export function decodeQueryDraftProposal(
  message: AssistantMessage,
  hostInput: unknown,
): QueryDraftProposal {
  const host = readHostInput(hostInput)
  const content = decodeStructuredContent(message, queryDraftContentSchema)
  return {
    kind: 'query-draft-proposal',
    inputContext: structuredClone(host.inputContext),
    draft: {
      name: content.name,
      description: content.description,
      sparql: content.sparql,
      scope: host.queryScope,
      capabilityQuestion: content.capabilityQuestion,
      source: 'model',
    },
    requiresHumanReview: true,
  }
}
