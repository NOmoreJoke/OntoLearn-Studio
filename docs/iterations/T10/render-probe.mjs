// CLI-only synthetic report/component preparation. Never launches Electron or a browser.
// Run from the T10 worktree: node docs/iterations/T10/render-probe.mjs
import ts from 'typescript'
import { readFile, writeFile, mkdir, unlink } from 'node:fs/promises'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'

const output = resolve('out/t10-render-probe')
await mkdir(output, { recursive: true })
const sourceRoot = resolve('apps/desktop/src/renderer/src/transfer')
const csp = pathToFileURL(resolve('apps/desktop/src/csp.ts')).href
const reportPath = resolve(output, 'report.mjs')
const panelPath = resolve(output, 'panel.mjs')
const transpile = (source) =>
  ts.transpileModule(source, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ESNext,
      jsx: ts.JsxEmit.ReactJSX,
    },
  }).outputText
try {
  const reportSource = (await readFile(resolve(sourceRoot, 'report.ts'), 'utf8')).replace(
    "'../../../csp'",
    JSON.stringify(csp),
  )
  await writeFile(reportPath, transpile(reportSource))
  const panelSource = (await readFile(resolve(sourceRoot, 'TransferPanel.tsx'), 'utf8')).replace(
    "'./report'",
    JSON.stringify(pathToFileURL(reportPath).href),
  )
  await writeFile(panelPath, transpile(panelSource))
  const { renderPreparedReport } = await import(pathToFileURL(reportPath).href)
  const { TransferPanel } = await import(pathToFileURL(panelPath).href)
  const report = JSON.parse(await readFile('tests/fixtures/transfer/report-input.json', 'utf8'))
  const attacks = JSON.parse(await readFile('tests/fixtures/transfer/malicious-texts.json', 'utf8'))
  report.goals = attacks
  report.title = attacks[0]
  await writeFile(resolve(output, 'malicious-report.html'), renderPreparedReport(report))
  await writeFile(
    resolve(output, 'panel.html'),
    '<!doctype html><meta charset="utf-8">' +
      renderToStaticMarkup(createElement(TransferPanel, { projection: report })),
  )
  await writeFile(
    resolve(output, 'invalid-panel.html'),
    '<!doctype html><meta charset="utf-8">' +
      renderToStaticMarkup(createElement(TransferPanel, { projection: { invalid: true } })),
  )
  console.log('T10_SYNTHETIC_PROBE_READY')
} finally {
  await Promise.all([unlink(reportPath).catch(() => {}), unlink(panelPath).catch(() => {})])
}
