import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const ROOT = path.resolve(import.meta.dirname, '../..')
const SCRIPT = path.join(ROOT, 'scripts/check-design-harness.mjs')

function runCheck(args: string[], input?: string) {
  try {
    const stdout = execFileSync(process.execPath, [SCRIPT, ...args], {
      cwd: ROOT,
      input,
      encoding: 'utf8',
    })
    return { status: 0, stdout, stderr: '' }
  } catch (error) {
    const e = error as { status?: number; stdout?: string; stderr?: string }
    return { status: e.status ?? 1, stdout: e.stdout ?? '', stderr: e.stderr ?? '' }
  }
}

describe('W6 design harness deterministic guardrails (positive + negative --stdin)', () => {
  it('passes full repository scan with zero violations', () => {
    const res = runCheck([])
    expect(res.status).toBe(0)
    expect(res.stdout).toContain('Design harness checks passed.')
  })

  it('rejects raw hex colors outside tokens.css via --stdin', () => {
    const res = runCheck(
      ['--stdin', 'apps/desktop/src/renderer/src/style.css'],
      '.bad-card { color: #0369a1; background: var(--paper-surface); }\n',
    )
    expect(res.status).toBe(1)
    expect(res.stderr).toContain('no-raw-hex-css')
    expect(res.stderr).toContain('#0369a1')
  })

  it('rejects stale waterfall placeholders in renderer TSX via --stdin', () => {
    const res = runCheck(
      ['--stdin', 'apps/desktop/src/renderer/src/App.tsx'],
      'export function Demo() { return <span>需求规划 · 待实现</span> }\n',
    )
    expect(res.status).toBe(1)
    expect(res.stderr).toContain('no-stale-placeholders')
  })

  it('rejects bare useEffect, setTimeout, and @ts-ignore inside shell/ via --stdin', () => {
    const res = runCheck(
      ['--stdin', 'apps/desktop/src/renderer/src/shell/BadShell.tsx'],
      [
        '// @ts-ignore',
        'export function BadShell() {',
        '  useEffect(() => {}, [])',
        '  setTimeout(() => {}, 10)',
        '  return null',
        '}',
      ].join('\n'),
    )
    expect(res.status).toBe(1)
    expect(res.stderr).toContain('shell-no-effect-or-timer')
    expect(res.stderr).toContain('shell-no-ts-suppress')
  })
})
