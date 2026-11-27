// Business strings are plain text. Host file paths must not enter display state.
const localPath = /\bfile:\/\/[^\s"'<>]+|(?:^|[\s"'=(:,])(?:[a-z]:[\\/]|\\\\|\/(?!\/))[^\s"'<>]+/gi

export function containsLocalPath(value: string): boolean {
  return value.replace(localPath, '') !== value
}

export function withoutLocalPaths(value: string): string {
  return value.replace(localPath, (match) => {
    const prefix = /^[\s"'=(:,]/.test(match) ? match[0] : ''
    return prefix + '[本地路径已隐藏]'
  })
}

export function maskLocalPaths<T>(value: T): T {
  if (typeof value === 'string') return withoutLocalPaths(value) as T
  if (Array.isArray(value)) return value.map(maskLocalPaths) as T
  if (value && typeof value === 'object')
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [withoutLocalPaths(key), maskLocalPaths(entry)]),
    ) as T
  return value
}
