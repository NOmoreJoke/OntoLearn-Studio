/** Strict raw JSON decoding, before any decoded-value schema validation. */
export function parseStrictJson(text: string, maxDepth = 32): unknown {
  let at = 0
  const bad = (): never => {
    throw new Error('INVALID_JSON_FRAME')
  }
  const space = (): void => {
    while (/[\x20\t\r\n]/.test(text[at] ?? '\0')) at++
  }
  const string = (): string => {
    const start = at++
    while (at < text.length) {
      const char = text[at++]
      if (char === '\\') {
        at++
        continue
      }
      if (char === '"') {
        const value: unknown = JSON.parse(text.slice(start, at))
        if (
          typeof value !== 'string' ||
          [...value].some((c) => {
            const cp = c.codePointAt(0)!
            return cp >= 0xd800 && cp <= 0xdfff
          })
        )
          return bad()
        return value
      }
    }
    return bad()
  }
  const value = (depth: number): unknown => {
    space()
    const char = text[at]
    if (char === '"') return string()
    if (char === '{' || char === '[') {
      if (depth >= maxDepth) return bad()
      at++
      space()
      const end = char === '{' ? '}' : ']'
      const keys = new Set<string>()
      const object: Record<string, unknown> = Object.create(null)
      const array: unknown[] = []
      if (text[at] === end) {
        at++
        return char === '{' ? object : array
      }
      while (at < text.length) {
        if (char === '{') {
          if (text[at] !== '"') return bad()
          const key = string()
          if (keys.has(key)) return bad()
          keys.add(key)
          space()
          if (text[at++] !== ':') return bad()
          object[key] = value(depth + 1)
        } else array.push(value(depth + 1))
        space()
        const separator = text[at++]
        if (separator === end) return char === '{' ? object : array
        if (separator !== ',') return bad()
        space()
      }
      return bad()
    }
    const match = /^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(
      text.slice(at),
    )
    if (!match) return bad()
    at += match[0].length
    const result: unknown = JSON.parse(match[0])
    if (
      typeof result === 'number' &&
      (!Number.isFinite(result) || Math.abs(result) > Number.MAX_SAFE_INTEGER)
    )
      return bad()
    return result
  }
  const result = value(0)
  space()
  if (at !== text.length) return bad()
  return result
}

/** Each LF delimits a frame. Bytes are bounded before copying, including partial UTF-8. */
export class JsonlReader {
  private buffer?: Buffer
  private size = 0
  private ended = false
  constructor(
    private readonly frame: (
      value: unknown,
      metadata: Readonly<{ payloadByteLength: number }>,
    ) => void,
    private readonly failure: (reason: 'frame' | 'json') => void,
    private maxBytes = 262144,
  ) {
    if (!Number.isInteger(maxBytes) || maxBytes < 1 || maxBytes > 262144)
      throw new Error('INVALID_FRAME_LIMIT')
    this.buffer = Buffer.allocUnsafe(maxBytes)
  }
  get bufferedBytes(): number {
    return this.size
  }
  get terminal(): boolean {
    return this.ended
  }
  stop(): void {
    this.ended = true
    this.buffer = undefined
    this.size = 0
  }
  /** Negotiation may lower the frame budget; it cannot enlarge allocated storage. */
  restrictLimit(limit: number): void {
    if (this.ended) return
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > this.maxBytes)
      throw new Error('INVALID_FRAME_LIMIT')
    this.maxBytes = limit
    if (this.size > limit) this.fail('frame')
  }
  private fail(reason: 'frame' | 'json'): void {
    this.stop()
    this.failure(reason)
  }
  push(chunk: Uint8Array): void {
    if (this.ended) return
    const input = Buffer.from(chunk.buffer, chunk.byteOffset, chunk.byteLength)
    let start = 0
    while (start < input.length && !this.ended) {
      const newline = input.indexOf(10, start)
      const end = newline < 0 ? input.length : newline
      const length = end - start
      if (this.size + length > this.maxBytes) {
        this.fail('frame')
        return
      }
      if (length) {
        input.copy(this.buffer!, this.size, start, end)
        this.size += length
      }
      if (newline < 0) return
      const payloadByteLength = this.size
      let bytes = this.buffer!.subarray(0, this.size)
      this.size = 0
      if (bytes[bytes.length - 1] === 13) bytes = bytes.subarray(0, -1)
      try {
        // ignoreBOM=true preserves a BOM so the grammar rejects it.
        const text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes)
        this.frame(parseStrictJson(text), Object.freeze({ payloadByteLength }))
      } catch {
        this.fail('json')
        return
      }
      start = newline + 1
    }
  }
  end(): void {
    if (this.ended) return
    if (this.size) this.fail('json')
    else this.stop()
  }
}
