export type AgentErrorCode =
  | 'INVALID_PROTOCOL'
  | 'INVALID_JSON'
  | 'INCOMPLETE_RESPONSE'
  | 'TOOL_NOT_ALLOWED'
  | 'TOOL_UNAVAILABLE'
  | 'INVALID_TOOL_ARGUMENTS'
  | 'INVALID_EVIDENCE'
  | 'STALE_CONTEXT'
  | 'BUDGET_EXCEEDED'
  | 'CANCELLED'
  | 'TIMED_OUT'
  | 'TOOL_FAILED'

/** Local pure-service errors; never forward Zod issues or provider/tool exception text. */
export class AgentError extends Error {
  constructor(readonly code: AgentErrorCode) {
    super(code)
    this.name = 'AgentError'
  }
}
