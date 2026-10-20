import { test, expect, _electron as electron } from '@playwright/test'
import { resolve } from 'node:path'

test('desktop calls real engine, keeps isolation and fits minimum window', async () => {
  const env = { ...process.env }
  delete env.ELECTRON_RUN_AS_NODE
  const application = await electron.launch({
    ...(process.env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: process.env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  })
  try {
    const page = await application.firstWindow()
    await expect(page.getByRole('heading', { level: 1 })).toContainText('转化为可验证的知识')
    await expect(page.getByRole('status')).toContainText('尚未检查')
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeEnabled()
    await expect(page.getByRole('status')).toContainText('本地引擎已连接')
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeEnabled()
    await expect(page.getByRole('status')).toContainText('协议 v2')
    expect(
      await page.evaluate(() => typeof (window as unknown as { require?: unknown }).require),
    ).toBe('undefined')
    const preferences = await application.evaluate(({ BrowserWindow }) =>
      BrowserWindow.getAllWindows()[0].webContents.getLastWebPreferences(),
    )
    expect(preferences.contextIsolation).toBe(true)
    expect(preferences.sandbox).toBe(true)
    expect(preferences.nodeIntegration).toBe(false)
    await page.screenshot({ path: 'test-results/desktop-1280.png' })
    await application.evaluate(({ BrowserWindow }) =>
      BrowserWindow.getAllWindows()[0].setSize(1024, 720),
    )
    await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeInViewport()
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true)
    await page.getByRole('link', { name: '模块规划' }).click()
    await expect(page.getByRole('heading', { name: '六个模块，一条学习路径' })).toBeInViewport()
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeEnabled()
    await expect(page.getByRole('status')).toContainText('本地引擎已连接')
    await page.getByRole('link', { name: '开发概览' }).click()
    await expect(page.getByRole('heading', { level: 1 })).toBeInViewport()
    await page.screenshot({ path: 'test-results/desktop-1024.png' })
  } finally {
    await application.close()
  }
})
