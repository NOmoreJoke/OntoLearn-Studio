// 本地页内锚点可变化；协议、主机、端口、路径与查询参数必须完全匹配。
export function isTrustedDocument(candidate: string, trusted: string): boolean {
  try {
    const actual = new URL(candidate)
    const expected = new URL(trusted)
    actual.hash = ''
    expected.hash = ''
    return actual.href === expected.href
  } catch {
    return false
  }
}
