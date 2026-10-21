// UI semantics only. Existing Playwright Electron loader is not OS credential/native proof.
import assert from 'node:assert/strict'
import { _electron as electron, expect } from '@playwright/test'
import { writeFile } from 'node:fs/promises'
const mode = process.argv[2]
assert.ok(['source', 'packaged'].includes(mode))
const env = { ...process.env }
for (const key of [
  'ELECTRON_RUN_AS_NODE',
  'ELECTRON_RENDERER_URL',
  'I02_HMR',
  'I04_TEST_FIXTURE',
  'I04_NATIVE_ISOLATED',
])
  delete env[key]
const app = await electron.launch({
  chromiumSandbox: true,
  ...(mode === 'packaged'
    ? { executablePath: '/workspace/release/linux-arm64-unpacked/@ontolearndesktop', args: [] }
    : { args: ['/workspace/apps/desktop'] }),
  cwd: '/workspace/apps/desktop',
  env,
})
try {
  const page = await app.firstWindow()
  const notice = page.locator('.model-panel p[aria-live="polite"]')
  const snapshots = []
  for (const stage of ['initial', 'reload']) {
    if (stage === 'reload') await page.reload()
    await expect(notice).toHaveText('模型服务暂不可用或尚未选择本地项目。可以继续使用本地任务。')
    assert.equal(await notice.getAttribute('role'), null)
    await expect(page.getByRole('status')).toHaveCount(1)
    await expect(page.getByLabel('项目模型隐私模式')).toBeDisabled()
    await expect(page.getByLabel('项目模型隐私模式')).toHaveValue('local')
    const status = await page.evaluate(() => window.ontolearn.getModelAccessStatus({}))
    assert.equal(status.ok, true)
    assert.equal(status.data.availability, 'unavailable')
    assert.equal(status.data.contextId, null)
    assert.equal(status.data.projectId, null)
    snapshots.push({
      stage,
      text: await notice.textContent(),
      ariaLive: await notice.getAttribute('aria-live'),
      role: await notice.getAttribute('role'),
      statusCount: await page.getByRole('status').count(),
      status: status.data,
    })
  }
  const runtime = await app.evaluate(({ app }) => ({
    packaged: app.isPackaged,
    executable: process.execPath,
    versions: process.versions,
  }))
  assert.equal(runtime.packaged, mode === 'packaged')
  await writeFile(
    `/probe-data/main-platform/regression/${mode}-aria-live.json`,
    JSON.stringify(
      {
        result: 'passed',
        mode,
        snapshots,
        runtime,
        scope: 'Minimal unavailable-model live semantics, no credential/native claim.',
      },
      null,
      2,
    ) + '\n',
  )
} finally {
  await app.close()
}
