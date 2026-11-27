export type ReviewLevel = 'L0' | 'L1' | 'L2'

export interface LockfileGroup {
  lockfiles?: string[]
  manifests?: string[]
}

export interface ReviewPolicy {
  version: number
  defaultLevel: ReviewLevel
  rules: { level: ReviewLevel; reason: string; paths: string[] }[]
  dependencies?: {
    manifests?: string[]
    lockfiles?: string[]
    lockfileGroups?: LockfileGroup[]
    critical?: string[]
  }
}

export interface FileResult {
  path: string
  level: ReviewLevel
  reason: string
}

/** 不可通过策略 JSON 覆盖的 L2 硬底线路径 glob。 */
export const IMMUTABLE_L2_PATTERNS: string[]

export function maxLevel(...levels: ReviewLevel[]): ReviewLevel
/** 规范仓库路径防线：空路径、反斜杠、前导 / 或 ./、.. 段等非法输入直接抛错（Fail-Closed）。 */
export function assertCanonicalRepoPath(path: string): string
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
  headPolicy: ReviewPolicy,
  basePolicy?: ReviewPolicy | null,
): { level: ReviewLevel; files: FileResult[] }

export interface SourceManifestEntry {
  path: string
  sha256: string
}
export interface SourceManifest {
  files: SourceManifestEntry[]
}
/** 严格校验 source-manifest 证据架构：非对象、空/缺失 files、非法条目一律抛错（Fail-Closed）。 */
export function validateSourceManifest(manifest: unknown, label?: string): SourceManifest
