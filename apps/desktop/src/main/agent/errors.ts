const agentErrorCodes = [
  'INVALID_PROTOCOL',
  'INVALID_JSON',
  'INCOMPLETE_RESPONSE',
  'TOOL_NOT_ALLOWED',
  'TOOL_UNAVAILABLE',
  'INVALID_TOOL_ARGUMENTS',
  'INVALID_EVIDENCE',
  'STALE_CONTEXT',
  'BUDGET_EXCEEDED',
  'BUSY',
  'PROVIDER_DRIFT',
  'CANCELLED',
  'TIMED_OUT',
  'TOOL_FAILED',
] as const
export type AgentErrorCode = (typeof agentErrorCodes)[number]

/** Runtime boundary too: a cast or untyped adapter cannot turn an error code into free text. */
export function safeAgentErrorCode(value: unknown): AgentErrorCode {
  return agentErrorCodes.includes(value as AgentErrorCode)
    ? (value as AgentErrorCode)
    : 'TOOL_FAILED'
}

/** Local pure-service errors; never forward Zod issues or provider/tool exception text. */
export class AgentError extends Error {
  readonly code: AgentErrorCode
  constructor(code: AgentErrorCode) {
    const safe = safeAgentErrorCode(code)
    super(safe)
    this.code = safe
    this.name = 'AgentError'
  }
}

/** Never retain an adapter-owned instance: even readonly properties can be changed at runtime. */
export function normalizeAgentError(
  value: unknown,
  fallback: AgentErrorCode = 'TOOL_FAILED',
): AgentError {
  let code: unknown = fallback
  try {
    if (value instanceof AgentError) code = value.code
  } catch {
    // A proxy/getter on a foreign error is not a safe error classification.
  }
  return new AgentError(safeAgentErrorCode(code))
}
