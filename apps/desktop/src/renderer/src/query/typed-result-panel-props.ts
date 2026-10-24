// Private controlled-view props; no bridge registration or request authority.
export interface QueryResultPanelProps {
  projectId: string
  resultId: string
  descriptor: unknown
  rows?: {
    value: unknown
    requested: {
      descriptorRef: string
      cursor: string | null
      startIndex: number
      pageSize: number
    }
  }
  text?: {
    value: unknown
    requested: {
      descriptorRef: string
      cursor: string | null
      startUtf8Byte: number
      maxUtf8Bytes: number
    }
  }
  rowsLoading?: boolean
  textLoading?: boolean
  readFailure?: unknown
  onNextRows?: (request: {
    descriptorRef: string
    cursor: string
    startIndex: number
    pageSize: number
  }) => void
  onNextText?: (request: {
    descriptorRef: string
    cursor: string
    startUtf8Byte: number
    maxUtf8Bytes: number
  }) => void
}
