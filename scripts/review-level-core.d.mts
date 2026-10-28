export type ReviewLevel = 'L0' | 'L1' | 'L2'

export interface ReviewPolicy {
  version: number
  defaultLevel: ReviewLevel
  rules: { level: ReviewLevel; reason: string; paths: string[] }[]
  dependencies?: { manifests?: string[]; lockfiles?: string[]; critical?: string[] }
}

export interface FileResult {
  path: string
  level: ReviewLevel
  reason: string
}

export function maxLevel(...levels: ReviewLevel[]): ReviewLevel
export function globToRegExp(glob: string): RegExp
export function classifyPath(
  path: string,
  policy: ReviewPolicy,
): { level: ReviewLevel; reason: string }
export function bumpKind(from: string, to: string): 'major' | 'minor' | 'patch' | 'none' | 'unknown'
export function classifyPackageJson(
  baseText: string | null,
  headText: string | null,
  policy: ReviewPolicy,
): { level: ReviewLevel; reasons: string[] }
export function classifyChange(
  files: { path: string; base?: string | null; head?: string | null }[],
  policy: ReviewPolicy,
): { level: ReviewLevel; files: FileResult[] }
