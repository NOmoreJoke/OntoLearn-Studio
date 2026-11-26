import { mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import { launchIsolatedDesktop } from './isolated-desktop'

async function maybeShot(
  page: Page,
  name: string,
  options?: { keepScroll?: boolean },
): Promise<void> {
  const outDir = process.env.ONTOLEARN_W7_SCREENSHOT_DIR
  if (!outDir) return
  mkdirSync(outDir, { recursive: true })
  if (!options?.keepScroll) {
    await page.evaluate(() => window.scrollTo(0, 0))
  }
  await page.screenshot({ path: join(outDir, name), fullPage: false })
}

async function waitForMobileSidebarClosed(page: Page): Promise<void> {
  await expect(page.locator('aside.sidebar')).toHaveAttribute('data-mobile-open', 'false')
  await expect
    .poll(async () => Math.round((await page.locator('aside.sidebar').boundingBox())?.x ?? 0))
    .toBeLessThanOrEqual(-240)
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  await expect
    .poll(async () =>
      page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    )
    .toBe(true)
}

test('W7 zero-code foundation end-to-end: dual-track roadmap, 00 sandbox, 01 zero-code builder + ReadableBusinessDiff, 04 80-row simulation, and 390px responsive check', async () => {
  test.setTimeout(180000)
  const env = { ...process.env }
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  const application = await launchIsolatedDesktop({
    ...(process.env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: process.env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  })

  try {
    const page = await application.firstWindow()
    await application.evaluate(({ BrowserWindow }) => {
      BrowserWindow.getAllWindows()[0].setSize(1440, 900)
    })
    await page.setViewportSize({ width: 1440, height: 900 })

    // 1. Learning Roadmap: Lv.1 retail track + 6 micro-steps + backward-compatible 9 tasks
    await page.getByTestId('nav-learning-center').click()
    const center = page.getByTestId('learning-center')
    await expect(center).toBeVisible()
    await expect(center).toContainText('离线课程 · 无需模型 API')
    await expect(center).toContainText('设备运维')
    await expect(page.getByTestId('learning-path-task')).toHaveCount(9)
    await expect(page.getByTestId('w7-foundation-step-card')).toHaveCount(6)
    await assertNoHorizontalOverflow(page)
    await maybeShot(page, 'w7-1440-roadmap.png')

    // 2. Enter 00 Foundation Sandbox from Step 01 -> switch to Step 02 homonym check -> add triple
    await page.getByTestId('w7-foundation-step-card').first().click()
    const sandbox = page.getByTestId('foundation-sandbox-page')
    await expect(sandbox).toBeVisible()

    await page.locator('[data-testid="foundation-step-tab"][data-step-id="step-02"]').click()
    await page.getByTestId('sandbox-pick-M-018').click()
    await expect(page.getByTestId('homonym-callout')).toBeVisible()
    await expect(page.getByTestId('homonym-callout')).toContainText('#M-018')
    await expect(page.getByTestId('homonym-callout')).toContainText('#M-209')

    await page.getByTestId('sandbox-add-triple').click()
    await expect(page.getByTestId('foundation-progress-pill')).toContainText('已练通 1 / 6 步')
    await maybeShot(page, 'w7-1440-sandbox-excel.png')

    // 3. Step 05 PRD Concept Clinic: reify #SO-101 and create project into 01 Ontology Builder
    await page.locator('[data-testid="foundation-step-tab"][data-step-id="step-05"]').click()
    await expect(page.getByTestId('prd-concept-clinic')).toBeVisible()
    await expect(page.getByTestId('clinic-bad-model')).toBeVisible()
    await page.getByTestId('clinic-reify-btn').click()
    await expect(page.getByTestId('foundation-progress-pill')).toContainText('已练通 2 / 6 步')
    await maybeShot(page, 'w7-1440-sandbox-clinic.png')

    await page.getByTestId('foundation-create-and-apply').click()
    await expect(page.locator('#ontology-workspace')).toBeVisible({ timeout: 30000 })
    const ontologyPanel = page.getByRole('region', { name: '本体项目编辑', exact: true })
    await expect(ontologyPanel.getByTestId('zero-code-triple-builder')).toBeVisible({
      timeout: 30000,
    })
    await expect(ontologyPanel.getByTestId('foundation-draft-chip')).toHaveCount(5)

    // 4. Preview via Zero-Code Triple Builder -> verify ReadableBusinessDiff + single <pre> in <details> -> commit
    await ontologyPanel.getByTestId('zc-preview-add-fact').click()
    const diffRegion = ontologyPanel.getByRole('region', { name: '完整事务差异', exact: true })
    await expect(diffRegion).toBeVisible({ timeout: 30000 })
    await expect(diffRegion.getByTestId('readable-business-diff')).toBeVisible()
    await expect(diffRegion.getByTestId('readable-business-diff')).toContainText('新增')
    await expect(diffRegion.getByTestId('readable-business-diff')).toContainText('门店订单 #SO-101')
    await expect(diffRegion.locator('pre')).toHaveCount(1)
    await expect(diffRegion.locator('details.raw-diff-drawer pre')).toHaveCount(1)
    await diffRegion.scrollIntoViewIfNeeded()
    await maybeShot(page, 'w7-1440-ontology-diff.png', { keepScroll: true })

    await diffRegion.locator('details.raw-diff-drawer summary').click()
    const rawPreText = await diffRegion.locator('details.raw-diff-drawer pre').textContent()
    expect(JSON.parse(rawPreText ?? '[]')).toHaveLength(1)

    await diffRegion
      .getByRole('button', { name: '我已核对完整差异，确认提交', exact: true })
      .click()
    await expect(
      ontologyPanel.getByRole('region', { name: '已提交回执', exact: true }),
    ).toContainText('提交版本 1。', { timeout: 30000 })

    // Verify mode toggle between zero-code and standard RDF/IRI views preserves standard form
    await ontologyPanel.getByTestId('ontology-mode-standard').click()
    await expect(ontologyPanel.getByTestId('zero-code-triple-builder')).toHaveCount(0)
    await expect(ontologyPanel.getByLabel('主体个体 IRI', { exact: true })).toBeVisible()
    await ontologyPanel.getByTestId('ontology-mode-zero-code').click()
    await expect(ontologyPanel.getByTestId('zero-code-triple-builder')).toBeVisible()

    // 5. Enter 04 Quality & Derivation -> run 80-row stress simulation via real Python engine
    await page.getByTestId('nav-step-04').click()
    const qualityWorkspace = page.locator('#quality-workspace')
    await expect(qualityWorkspace.getByTestId('retail-simulation-banner')).toBeVisible({
      timeout: 30000,
    })
    await qualityWorkspace.getByTestId('retail-scale-stress80').click()
    await expect(qualityWorkspace.getByTestId('retail-anomaly-summary')).toContainText(
      '3 笔订单缺门店',
    )
    await expect(qualityWorkspace.getByTestId('retail-anomaly-summary')).toContainText(
      '2 笔实付金额为负',
    )
    await expect(qualityWorkspace.getByTestId('retail-anomaly-summary')).toContainText(
      '2 家门店悬空店长',
    )
    await expect(qualityWorkspace.getByTestId('retail-anomaly-summary')).toContainText(
      '4 名高流失风险待挽回会员',
    )

    await qualityWorkspace.getByTestId('retail-run-simulation').click()
    const evidencePanel = qualityWorkspace.getByTestId('retail-evidence-chains')
    await expect(evidencePanel).toBeVisible({ timeout: 30000 })
    await expect(evidencePanel).toContainText('引擎实测结论：结构有效 · 预期一致')
    await expect(evidencePanel).toContainText('规则推导 4 条')
    await expect(evidencePanel).toContainText('王敏 #M-018')
    await expect(evidencePanel).toContainText('周航 #M-056')
    await maybeShot(page, 'w7-1440-quality-sim.png')

    // 6. Mobile 390x844 responsive check across 04, 00 Sandbox, and Roadmap
    await application.evaluate(({ BrowserWindow }) => {
      BrowserWindow.getAllWindows()[0].setSize(390, 844)
    })
    await page.setViewportSize({ width: 390, height: 844 })
    await waitForMobileSidebarClosed(page)
    await assertNoHorizontalOverflow(page)
    await maybeShot(page, 'w7-390-quality.png')

    await page.getByTestId('mobile-nav-toggle').first().click()
    await expect(page.getByTestId('nav-step-00')).toBeInViewport()
    await page.getByTestId('nav-step-00').click()
    await expect(page.getByTestId('foundation-sandbox-page')).toBeVisible()
    await waitForMobileSidebarClosed(page)
    await assertNoHorizontalOverflow(page)
    await maybeShot(page, 'w7-390-sandbox.png')

    await page.getByTestId('mobile-nav-toggle').first().click()
    await page.getByTestId('nav-learning-center').click()
    await expect(page.getByTestId('learning-center')).toBeVisible()
    await waitForMobileSidebarClosed(page)
    await assertNoHorizontalOverflow(page)
    await maybeShot(page, 'w7-390-roadmap.png')
  } finally {
    await application.close()
  }
})
