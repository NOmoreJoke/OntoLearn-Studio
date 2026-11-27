/** Deterministic seeded property-based testing helper (shrinking + reproducible seeds). */

export type Arbitrary<T> = {
  generate(rng: SeededRng, index: number): T
  shrink?(value: T): T[]
}

class SeededRng {
  private state: number

  constructor(seed: number) {
    this.state = seed >>> 0 || 1
  }

  nextUint32(): number {
    let x = this.state
    x ^= x << 13
    x ^= x >>> 17
    x ^= x << 5
    this.state = x >>> 0
    return this.state
  }

  int(min: number, max: number): number {
    if (max <= min) return min
    const span = max - min + 1
    return min + (this.nextUint32() % span)
  }

  bool(): boolean {
    return (this.nextUint32() & 1) === 1
  }
}

export function integer(options?: { min?: number; max?: number }): Arbitrary<number> {
  const min = options?.min ?? -10000
  const max = options?.max ?? 10000
  return {
    generate(rng, index) {
      if (index === 0) return min <= 0 && max >= 0 ? 0 : min
      if (index === 1) return min
      if (index === 2) return max
      return rng.int(min, max)
    },
    shrink(value) {
      if (value === 0) return []
      const half = Math.trunc(value / 2)
      return half === value ? [0] : [0, half]
    },
  }
}

export function boolean(): Arbitrary<boolean> {
  return {
    generate(rng, index) {
      if (index === 0) return false
      if (index === 1) return true
      return rng.bool()
    },
  }
}

export function constantFrom<T>(...values: readonly T[]): Arbitrary<T> {
  return {
    generate(rng, index) {
      if (index < values.length) return values[index]!
      return values[rng.int(0, values.length - 1)]!
    },
  }
}

const DEFAULT_CHAR_POOL = [
  ...'abcxyzABCXYZ0123456789 _-./:@',
  '"',
  '\\',
  '\n',
  '\r',
  '\t',
  '王',
  '敏',
  '茶',
  '饮',
  '订',
  '单',
  '😀',
  '🧋',
] as const

export function unicodeText(options?: {
  minLength?: number
  maxLength?: number
  pool?: readonly string[]
}): Arbitrary<string> {
  const minLen = options?.minLength ?? 0
  const maxLen = options?.maxLength ?? 40
  const pool = options?.pool ?? DEFAULT_CHAR_POOL
  const edges = [
    '',
    '王敏',
    '"""',
    '\\',
    'line1\nline2\r\t"quote"\\slash',
    '茶饮🧋"黑金"\n门店#S-01',
  ]
  return {
    generate(rng, index) {
      if (!options?.pool && index < edges.length) {
        const edge = edges[index]!
        if (edge.length >= minLen && edge.length <= maxLen) return edge
      }
      const len = rng.int(minLen, maxLen)
      let out = ''
      for (let i = 0; i < len; i += 1) {
        out += pool[rng.int(0, pool.length - 1)]!
      }
      return out
    },
    shrink(value) {
      const chars = Array.from(value)
      if (chars.length <= minLen) return []
      return [chars.slice(0, Math.max(minLen, Math.floor(chars.length / 2))).join('')]
    },
  }
}

export function oneof<T>(...arbs: readonly Arbitrary<T>[]): Arbitrary<T> {
  return {
    generate(rng, index) {
      const chosen = arbs[index < arbs.length ? index : rng.int(0, arbs.length - 1)]!
      return chosen.generate(rng, Math.floor(index / arbs.length))
    },
  }
}

export function record<T extends Record<string, unknown>>(shape: {
  [K in keyof T]: Arbitrary<T[K]>
}): Arbitrary<T> {
  const keys = Object.keys(shape) as Array<keyof T>
  return {
    generate(rng, index) {
      const obj = {} as T
      for (const k of keys) {
        obj[k] = shape[k].generate(rng, index)
      }
      return obj
    },
  }
}

export function tuple<T extends readonly unknown[]>(
  ...arbs: { [K in keyof T]: Arbitrary<T[K]> }
): Arbitrary<T> {
  return {
    generate(rng, index) {
      return arbs.map((arb) => arb.generate(rng, index)) as unknown as T
    },
  }
}

export type Property<Args extends readonly unknown[]> = {
  runCase(rng: SeededRng, index: number): { args: Args; ok: boolean; error?: unknown }
  shrinkArgs(args: Args): Args[]
}

export function property<Args extends readonly unknown[]>(
  ...args: [...{ [K in keyof Args]: Arbitrary<Args[K]> }, (...vals: Args) => boolean | void]
): Property<Args> {
  const predicate = args[args.length - 1] as (...vals: Args) => boolean | void
  const arbs = args.slice(0, -1) as { [K in keyof Args]: Arbitrary<Args[K]> }
  return {
    runCase(rng, index) {
      const generated = arbs.map((arb) => arb.generate(rng, index)) as unknown as Args
      try {
        const res = predicate(...generated)
        return { args: generated, ok: res !== false }
      } catch (error) {
        return { args: generated, ok: false, error }
      }
    },
    shrinkArgs(failing) {
      const candidates: Args[] = []
      for (let i = 0; i < arbs.length; i += 1) {
        const shrinks = arbs[i]!.shrink?.(failing[i]) ?? []
        for (const s of shrinks) {
          const copy: unknown[] = [...failing]
          copy[i] = s
          candidates.push(copy as unknown as Args)
        }
      }
      return candidates
    },
  }
}

export function assert<Args extends readonly unknown[]>(
  prop: Property<Args>,
  options?: { numRuns?: number; seed?: number },
): void {
  const numRuns = options?.numRuns ?? 300
  const seed = options?.seed ?? 20261126
  const rng = new SeededRng(seed)

  for (let i = 0; i < numRuns; i += 1) {
    const result = prop.runCase(rng, i)
    if (!result.ok) {
      const minimal = result.args
      const detail =
        result.error instanceof Error
          ? result.error.message
          : String(result.error ?? 'returned false')
      throw new Error(
        `Property failed after ${i + 1} runs (seed=${seed}) with counterexample ${JSON.stringify(minimal)}: ${detail}`,
      )
    }
  }
}
