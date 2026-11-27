#!/usr/bin/env node
import { readdirSync, readFileSync, statSync } from 'node:fs'
import path from 'node:path'

const REPO_ROOT = path.resolve(import.meta.dirname, '..')
const RENDERER_SRC = 'apps/desktop/src/renderer/src'
const TOKENS_FILE = `${RENDERER_SRC}/tokens.css`
const SHELL_PREFIX = `${RENDERER_SRC}/shell/`
const FOUNDATION_PREFIX = `${RENDERER_SRC}/foundation/`
const ONTOLOGY_PAGE_FILE = `${RENDERER_SRC}/ontology/OntologyMainlinePage.tsx`
const READABLE_DIFF_FILE = `${RENDERER_SRC}/ontology/ReadableBusinessDiff.tsx`

const REQUIRED_TOKENS = [
  '--paper-canvas',
  '--paper-surface',
  '--ink-primary',
  '--ink-secondary',
  '--hair-border',
  '--accent-primary',
  '--focus-ring',
]

const HEX_COLOR_RE = /(?:[:\s,(])(#[0-9a-fA-F]{3,8})(?=[;\s,)}/]|$)/gm
const STALE_PLACEHOLDER_RE = /需求规划\s*·\s*待实现|待开发|待实现/g
const SHELL_EFFECT_OR_TIMER_RE =
  /\b(useEffect|setTimeout|setInterval|requestAnimationFrame|requestIdleCallback)\s*\(/g
const FOUNDATION_TIMER_RE =
  /\b(setTimeout|setInterval|requestAnimationFrame|requestIdleCallback)\s*\(/g
const TS_SUPPRESS_RE = /@ts-(?:ignore|nocheck)\b/g
const RAW_ONTOLOGY_DIFF_PRE_RE = /<pre>\s*\{JSON\.stringify\(state\.prepared\.rows/g

function normalizeRepoPath(inputPath) {
  const abs = path.isAbsolute(inputPath) ? inputPath : path.resolve(REPO_ROOT, inputPath)
  return path.relative(REPO_ROOT, abs).split(path.sep).join('/')
}

function stripCssComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, '')
}

function lineNumberAt(text, index) {
  let line = 1
  for (let i = 0; i < index; i += 1) {
    if (text.charCodeAt(i) === 10) line += 1
  }
  return line
}

function collectLineMatches(text, regex, rule, messageFor) {
  const violations = []
  regex.lastIndex = 0
  let match = regex.exec(text)
  while (match !== null) {
    const token = match[1] ?? match[0]
    violations.push({
      line: lineNumberAt(text, match.index),
      rule,
      message: messageFor(token),
    })
    match = regex.exec(text)
  }
  return violations
}

export function inspectFile(relPath, content) {
  const normalized = relPath.split(path.sep).join('/')
  const violations = []

  if (normalized === TOKENS_FILE) {
    for (const token of REQUIRED_TOKENS) {
      if (!new RegExp(`${token}\\s*:`).test(content)) {
        violations.push({
          line: 1,
          rule: 'tokens-required',
          message: `Missing required semantic token ${token} in ${TOKENS_FILE}`,
        })
      }
    }
    return violations
  }

  if (normalized.startsWith(`${RENDERER_SRC}/`) && normalized.endsWith('.css')) {
    const stripped = stripCssComments(content)
    violations.push(
      ...collectLineMatches(
        stripped,
        HEX_COLOR_RE,
        'no-raw-hex-css',
        (hex) =>
          `Raw hex color ${hex} is forbidden outside tokens.css; use a semantic CSS variable`,
      ),
    )
  }

  if (
    normalized.startsWith(`${RENDERER_SRC}/`) &&
    (normalized.endsWith('.ts') || normalized.endsWith('.tsx'))
  ) {
    violations.push(
      ...collectLineMatches(
        content,
        STALE_PLACEHOLDER_RE,
        'no-stale-placeholders',
        (text) => `Stale placeholder "${text}" is forbidden in renderer source`,
      ),
    )
  }

  if (
    normalized.startsWith(SHELL_PREFIX) &&
    (normalized.endsWith('.ts') || normalized.endsWith('.tsx'))
  ) {
    violations.push(
      ...collectLineMatches(
        content,
        SHELL_EFFECT_OR_TIMER_RE,
        'shell-no-effect-or-timer',
        (name) => `Imperative hook/timer "${name}()" is forbidden inside shell/`,
      ),
    )
    violations.push(
      ...collectLineMatches(
        content,
        TS_SUPPRESS_RE,
        'shell-no-ts-suppress',
        (directive) => `TypeScript suppression "${directive}" is forbidden inside shell/`,
      ),
    )
  }

  if (
    normalized.startsWith(FOUNDATION_PREFIX) &&
    (normalized.endsWith('.ts') || normalized.endsWith('.tsx'))
  ) {
    violations.push(
      ...collectLineMatches(
        content,
        FOUNDATION_TIMER_RE,
        'foundation-no-timer',
        (name) => `Imperative timer "${name}()" is forbidden inside foundation/`,
      ),
    )
    violations.push(
      ...collectLineMatches(
        content,
        TS_SUPPRESS_RE,
        'foundation-no-ts-suppress',
        (directive) => `TypeScript suppression "${directive}" is forbidden inside foundation/`,
      ),
    )
  }

  if (normalized === ONTOLOGY_PAGE_FILE) {
    if (!content.includes('<ReadableBusinessDiff')) {
      violations.push({
        line: 1,
        rule: 'ontology-readable-diff-required',
        message: 'OntologyMainlinePage.tsx must render <ReadableBusinessDiff>',
      })
    }
    violations.push(
      ...collectLineMatches(
        content,
        RAW_ONTOLOGY_DIFF_PRE_RE,
        'ontology-no-raw-diff-pre',
        () =>
          'Unwrapped raw JSON.stringify(state.prepared.rows) <pre> is forbidden in OntologyMainlinePage.tsx',
      ),
    )
  }

  if (normalized === READABLE_DIFF_FILE) {
    const hasDetailsWrappedPre = /<details[\s\S]*?<pre>[\s\S]*?<\/pre>[\s\S]*?<\/details>/.test(
      content,
    )
    if (!hasDetailsWrappedPre) {
      violations.push({
        line: 1,
        rule: 'readable-diff-details-pre',
        message: 'ReadableBusinessDiff.tsx must wrap its single <pre> inside <details>',
      })
    }
  }

  return violations.map((item) => ({ file: normalized, ...item }))
}

function walkFiles(dir) {
  const results = []
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry)
    const stat = statSync(full)
    if (stat.isDirectory()) results.push(...walkFiles(full))
    else results.push(full)
  }
  return results
}

function main() {
  const args = process.argv.slice(2)
  const stdinIndex = args.indexOf('--stdin')
  const violations = []

  if (stdinIndex !== -1) {
    const targetArg = args[stdinIndex + 1]
    if (!targetArg) {
      console.error('Usage: check-design-harness.mjs --stdin <virtual-path>')
      process.exit(2)
    }
    const relPath = normalizeRepoPath(targetArg)
    const stdinContent = readFileSync(0, 'utf8')
    violations.push(...inspectFile(relPath, stdinContent))
  } else {
    const tokensAbs = path.join(REPO_ROOT, TOKENS_FILE)
    violations.push(...inspectFile(TOKENS_FILE, readFileSync(tokensAbs, 'utf8')))
    const rendererAbs = path.join(REPO_ROOT, RENDERER_SRC)
    for (const fileAbs of walkFiles(rendererAbs)) {
      const rel = path.relative(REPO_ROOT, fileAbs).split(path.sep).join('/')
      if (rel === TOKENS_FILE) continue
      if (rel.endsWith('.css') || rel.endsWith('.ts') || rel.endsWith('.tsx')) {
        violations.push(...inspectFile(rel, readFileSync(fileAbs, 'utf8')))
      }
    }
  }

  if (violations.length > 0) {
    for (const v of violations) {
      console.error(`[design-harness] ${v.file}:${v.line} (${v.rule}) ${v.message}`)
    }
    process.exit(1)
  }
  console.log('Design harness checks passed.')
}

if (path.resolve(process.argv[1] ?? '') === path.resolve(import.meta.filename)) {
  main()
}
