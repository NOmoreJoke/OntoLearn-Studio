import { mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import { launchIsolatedDesktop } from './isolated-desktop'

async function maybeShot(page: Page, name: string): Promise<void> {
  const outDir = process.env.ONTOLEARN_W6_SCREENSHOT_DIR
  if (!outDir) return
  mkdirSync(outDir, { recursive: true })
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: join(outDir, name), fullPage: false })
}

test('W6 grouped navigation, collapsible assistant rail, center width release, and 390px mobile drawer', async () => {
  test.setTimeout(120000)
  const env = { ...process.env }
  delete env.ELECTRON_RUN_AS_NODE
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

    // 1. Primary view exclusivity: Projects view does not render Learning Roadmap waterfall.
    await expect(page.getByTestId('portal-projects-view')).toBeVisible()
    await expect(page.getByTestId('portal-learning-view')).toHaveCount(0)
    await expect(page.locator('#query-workspace')).toHaveCount(0)

    // 2. Learning Roadmap portal view renders exclusively and launches case cleanly.
    await page.getByTestId('nav-learning-center').click()
    await expect(page.getByTestId('portal-learning-view')).toBeVisible()
    await expect(page.getByTestId('portal-projects-view')).toHaveCount(0)
    await expect(page.getByRole('heading', { name: '六个模块，一条学习路径' })).toBeInViewport()
    await maybeShot(page, 'w6-1440-roadmap.png')

    await page.getByTestId('learning-start-example').click()
    await expect(page.getByTestId('project-status-notice')).toContainText('项目已创建并打开', {
      timeout: 30000,
    })
    await expect(page.locator('#ontology-workspace')).toBeVisible({ timeout: 30000 })
    await expect(page.getByTestId('mentor-panel')).toBeVisible()
    await expect(page.getByTestId('mentor-panel')).toContainText('任务 01 · 本体构建')

    // 3. Roadmap task card launches target module + Mentor tab directly.
    await page.getByTestId('nav-learning-center').click()
    await expect(page.getByTestId('portal-learning-view')).toBeVisible()
    await page.locator('[data-testid="learning-path-task"][data-task-id="query"]').click()
    await expect(page.locator('#query-workspace')).toBeVisible()
    await expect(page.getByTestId('rail-tab-mentor')).toHaveAttribute('aria-selected', 'true')
    await expect(page.getByTestId('mentor-panel')).toContainText('任务 03 · 本体查询')
    await maybeShot(page, 'w6-1440-workspace-mentor.png')

    const mainBoxOpen = await page.locator('.workspace-freeze').boundingBox()
    expect(mainBoxOpen).not.toBeNull()

    // 4. Switching right rail tab to AI Assistant preserves center workspace width.
    await page.getByTestId('rail-tab-agent').click()
    await expect(page.getByTestId('rail-tab-agent')).toHaveAttribute('aria-selected', 'true')
    await expect(page.getByTestId('agent-sidebar')).toBeVisible()
    const mainBoxAgent = await page.locator('.workspace-freeze').boundingBox()
    expect(mainBoxAgent).not.toBeNull()
    expect(Math.abs(mainBoxAgent!.width - mainBoxOpen!.width)).toBeLessThanOrEqual(2)

    // 5. Collapsing assistant rail frees center workspace width (>= 280px).
    await page.getByTestId('mentor-panel-toggle').click()
    await expect(page.getByTestId('assistant-rail')).toHaveCount(0)
    const mainBoxWide = await page.locator('.workspace-freeze').boundingBox()
    expect(mainBoxWide).not.toBeNull()
    expect(mainBoxWide!.width - mainBoxOpen!.width).toBeGreaterThanOrEqual(280)
    await maybeShot(page, 'w6-1440-workspace-wide.png')

    // 6. TopContextBar checkpoint drawer opens/closes without leaving workspace view.
    await page.getByTestId('topbar-checkpoints-toggle').click()
    await expect(page.locator('#project-checkpoints')).toBeVisible()
    await page.getByTestId('topbar-checkpoints-toggle').click()
    await expect(page.locator('#project-checkpoints')).toHaveCount(0)

    // 7. Mobile 390px viewport: zero horizontal overflow and drawer navigation.
    await application.evaluate(({ BrowserWindow }) => {
      BrowserWindow.getAllWindows()[0].setSize(390, 844)
    })
    await page.setViewportSize({ width: 390, height: 844 })
    await expect
      .poll(async () =>
        page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      )
      .toBe(true)
    await expect(page.locator('aside.sidebar')).toHaveAttribute('data-mobile-open', 'false')
    await page.getByTestId('mobile-nav-toggle').first().click()
    await expect(page.locator('aside.sidebar')).toHaveAttribute('data-mobile-open', 'true')
    await expect
      .poll(async () => Math.round((await page.locator('aside.sidebar').boundingBox())?.x ?? -999))
      .toBe(0)
    await expect(page.getByTestId('nav-step-03')).toBeInViewport()
    await maybeShot(page, 'w6-390-mobile-drawer.png')
    await page.getByRole('button', { name: '关闭导航菜单' }).click()
    await expect(page.locator('aside.sidebar')).toHaveAttribute('data-mobile-open', 'false')
  } finally {
    await application.close()
  }
})
