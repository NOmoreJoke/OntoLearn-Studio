import { launchIsolatedDesktop } from './isolated-desktop'
import { test, expect } from '@playwright/test'
import { resolve } from 'node:path'
import { writeFile } from 'node:fs/promises'
import type { HealthResult } from '@ontolearn/contracts'

test('desktop calls real engine, keeps isolation and fits minimum window', async () => {
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
    await expect(page.getByRole('heading', { level: 1 })).toContainText('转化为可验证的知识')
    await expect(page.locator('.health-result')).toContainText('尚未检查')
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeEnabled()
    await expect(page.locator('.health-result')).toContainText('本地引擎已连接')
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeEnabled()
    await expect(page.locator('.health-result')).toContainText('协议 v3')
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
    await page.getByTestId('nav-learning-center').click()
    await expect(page.getByRole('heading', { name: '六个模块，一条学习路径' })).toBeInViewport()
    await page.getByRole('link', { name: '项目工作台' }).click()
    await expect(page.getByRole('heading', { level: 1 })).toBeInViewport()
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeEnabled()
    await expect(page.locator('.health-result')).toContainText('本地引擎已连接')
    await page.screenshot({ path: 'test-results/desktop-1024.png' })
  } finally {
    await application.close()
  }
})

test('a health reply from before connection loss cannot replace the current status', async () => {
  const testInfo = test.info()
  const replies: { outcome: string; before: string | null; after: string | null }[] = []
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
    await expect(page.locator('.health-result')).toContainText('尚未检查')
    const health = await page.evaluate(() => window.ontolearn!.getEngineHealth())
    expect(health.ok).toBe(true)
    // Control only IPC delivery in this test. The real preload validates each
    // connection fixture; this does not claim an actual engine exit occurred.
    for (const outcome of ['success', 'error'] as const) {
      await application.evaluate(({ ipcMain }) => {
        ipcMain.removeHandler('engine:health')
        ipcMain.handle(
          'engine:health',
          () =>
            new Promise<HealthResult>((done) => {
              ;(
                globalThis as unknown as { i04ResolveHealth?: (value: HealthResult) => void }
              ).i04ResolveHealth = done
            }),
        )
      })
      await page.getByRole('button', { name: '检查本地引擎' }).click()
      await expect
        .poll(() =>
          application.evaluate(
            () =>
              typeof (globalThis as unknown as { i04ResolveHealth?: unknown }).i04ResolveHealth ===
              'function',
          ),
        )
        .toBe(true)
      await application.evaluate(
        ({ BrowserWindow }, generation) => {
          BrowserWindow.getAllWindows()[0].webContents.send('tasks:update', {
            kind: 'connection',
            generation,
            projectId: '00000000-0000-4000-8000-000000000099',
            state: 'offline',
            attempt: 3,
            error: {
              code: 'ENGINE_EXITED',
              messageKey: 'engine.exited',
              params: {},
              retryable: true,
            },
          })
        },
        outcome === 'success' ? 100 : 101,
      )
      await expect(page.getByRole('status', { name: '引擎连接状态' })).toContainText('离线')
      const before = await page.locator('.health-result').textContent()
      await application.evaluate(
        (_, value) => {
          const state = globalThis as unknown as {
            i04ResolveHealth?: (value: HealthResult) => void
          }
          state.i04ResolveHealth!(value)
          delete state.i04ResolveHealth
        },
        outcome === 'success'
          ? health
          : {
              ok: false,
              error: {
                code: 'INTERNAL_ERROR',
                messageKey: 'engine.internal',
                params: {},
                retryable: false,
              },
            },
      )
      await expect(page.getByRole('button', { name: '检查本地引擎' })).toBeEnabled()
      await expect(page.locator('.health-result')).toHaveText(before!)
      replies.push({ outcome, before, after: await page.locator('.health-result').textContent() })
    }
    // A new explicit check after the loss still accepts its own fresh reply.
    await application.evaluate(({ ipcMain }, value) => {
      ipcMain.removeHandler('engine:health')
      ipcMain.handle('engine:health', () => value)
    }, health)
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.locator('.health-result')).toContainText('本地引擎已连接')
    const evidence = testInfo.outputPath('i04-health-replies.json')
    await writeFile(
      evidence,
      JSON.stringify(
        {
          replies,
          freshExplicit: await page.locator('.health-result').textContent(),
          boundary:
            'Controlled IPC reply ordering and validated connection fixtures; no actual engine exit claim.',
        },
        null,
        2,
      ),
    )
    await testInfo.attach('i04-health-replies', { path: evidence, contentType: 'application/json' })
  } finally {
    await application.close()
  }
})
