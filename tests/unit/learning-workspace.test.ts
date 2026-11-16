/** Headless component harness only; synthetic callbacks are never product adapters. */
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium, type Browser, type Page } from '@playwright/test'
import { build } from 'vite'
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest'
import { offlineCourse } from '../../apps/desktop/src/renderer/src/learning/content'
import type {
  CheckFeedbackView,
  LearningRecordView,
  LearningWorkspaceProps,
  TaskContext,
} from '../../apps/desktop/src/renderer/src/learning/types'

type Harness = {
  props: LearningWorkspaceProps
  maxHint: number
  version: number
  assistance: LearningRecordView['assistance']
  failHint: boolean
  forgedIndependent: boolean
  deferred: boolean
  malicious: boolean
  resolveCheck?: (value: CheckFeedbackView) => void
  pendingContext?: TaskContext
  reply(context: TaskContext): CheckFeedbackView
}
declare global {
  interface Window {
    mountLearning(props: LearningWorkspaceProps): void
    learningHarness: Harness
  }
}
const ROOT = fileURLToPath(new URL('../../', import.meta.url))
let browser: Browser
let page: Page
let javascript = ''
let css = ''
const errors: string[] = []
const requests: string[] = []

async function mount(
  options: {
    initialTaskId?: string
    connected?: boolean
    projectId?: string
    generation?: number
  } = {},
) {
  await page.evaluate(
    ({ options, taskIds }) => {
      const projectId = options.projectId ?? 'project-A'
      const contexts = Object.fromEntries(
        taskIds.map((taskId) => [
          taskId,
          { projectId, taskId, attemptId: 'attempt:' + taskId, inputVersion: 'input-1' },
        ]),
      )
      const state: Harness = {
        props: {
          generation: options.generation ?? 1,
          projectId: options.connected === false ? null : projectId,
          contexts: options.connected === false ? {} : contexts,
          records: [],
          initialTaskId: options.initialTaskId,
        },
        maxHint: 0,
        version: 0,
        assistance: 'independent',
        failHint: false,
        forgedIndependent: false,
        deferred: false,
        malicious: false,
        reply(context) {
          state.version++
          const record: LearningRecordView = {
            context,
            recordVersion: state.version,
            maxHintLevel: state.forgedIndependent ? 0 : state.maxHint,
            assistance: state.forgedIndependent ? 'independent' : state.assistance,
            operationComplete: true,
            independentTransferSuccess:
              state.forgedIndependent ||
              (context.taskId.startsWith('transfer-') &&
                state.assistance === 'independent' &&
                state.maxHint === 0),
            checkStatus: 'passed',
            evidenceIds: ['unit-only-result'],
          }
          return {
            context,
            record,
            completed: [
              state.malicious
                ? '<img src="https://probe.invalid/x" onerror="alert(1)">'
                : '实际结果条目',
            ],
            repairs: [],
            suggestions: ['查看相关知识点'],
            knowledgePoints: ['SHACL'],
          }
        },
      }
      if (options.connected !== false)
        state.props.actions = {
          async recordHint(context, level) {
            if (state.failHint) throw new Error('synthetic-sensitive-message')
            state.maxHint = Math.max(state.maxHint, level)
            if (state.assistance !== 'agent-full-assistance')
              state.assistance = state.maxHint === 4 ? 'full-demonstration' : 'partial-hints'
            state.version++
            return {
              context,
              level,
              record: {
                context,
                recordVersion: state.version,
                maxHintLevel: state.maxHint,
                assistance: state.assistance,
                operationComplete: false,
                independentTransferSuccess: false,
                checkStatus: 'not-checked',
                evidenceIds: [],
              },
            }
          },
          async checkTask(context) {
            if (state.deferred) {
              state.pendingContext = context
              return new Promise((done) => {
                state.resolveCheck = done
              })
            }
            return state.reply(context)
          },
        }
      window.learningHarness = state
      window.mountLearning(state.props)
    },
    { options, taskIds: offlineCourse.tasks.map((task) => task.id) },
  )
  await page.getByRole('heading', { name: '一步一步，把知识用起来。' }).waitFor()
}

describe.skipIf(process.env.T09_HEADLESS_UI !== '1')(
  'headless component verification (explicit runtime)',
  () => {
    beforeAll(async () => {
      const entry = '\0t09-learning-component-harness'
      const result = await build({
        root: ROOT,
        configFile: false,
        logLevel: 'error',
        oxc: { jsx: { runtime: 'automatic', development: false } },
        plugins: [
          {
            name: 't09-headless-component-entry',
            resolveId(id) {
              return id === 't09-component-entry' || id === resolve(ROOT, 't09-component-entry')
                ? entry
                : undefined
            },
            load(id) {
              if (id !== entry) return undefined
              return `import React from 'react'; import {createRoot} from 'react-dom/client';
          import {LearningWorkspace} from ${JSON.stringify(resolve(ROOT, 'apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx'))};
          const root=createRoot(document.getElementById('root'));
          window.mountLearning=props=>root.render(React.createElement(LearningWorkspace,props));`
            },
          },
        ],
        define: { 'process.env.NODE_ENV': JSON.stringify('production') },
        build: {
          write: false,
          minify: false,
          cssCodeSplit: false,
          lib: { entry: 't09-component-entry', formats: ['iife'], name: 'T09LearningHarness' },
        },
      })
      for (const output of Array.isArray(result) ? result : [result]) {
        if (!('output' in output)) throw new Error('Unexpected watched build')
        for (const item of output.output) {
          if (item.type === 'chunk') javascript += item.code
          else if (item.fileName.endsWith('.css'))
            css +=
              typeof item.source === 'string' ? item.source : new TextDecoder().decode(item.source)
        }
      }
      expect(javascript).not.toBe('')
      expect(css).not.toBe('')
      browser = await chromium.launch({
        headless: true,
        chromiumSandbox: true,
        ignoreDefaultArgs: ['--disable-hang-monitor', '--use-mock-keychain'],
      })
    }, 30000)

    beforeEach(async () => {
      errors.length = 0
      requests.length = 0
      page = await browser.newPage({ viewport: { width: 1440, height: 1050 } })
      page.on('pageerror', (error) => errors.push(error.message))
      page.on('request', (request) => requests.push(request.url()))
      await page.route('**/*', (route) => route.abort())
      await page.setContent(
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>T09 component test</title></head><body style="margin:0"><div id="root"></div></body></html>',
      )
      await page.addStyleTag({ content: css })
      await page.addScriptTag({ content: javascript })
    })
    afterEach(async () => {
      await page?.close()
      expect(errors).toEqual([])
      expect(requests).toEqual([])
    })
    afterAll(async () => {
      await browser?.close()
    })

    async function capture(name: string) {
      if (process.env.T09_UI_CAPTURE !== '1') return
      const directory = resolve(ROOT, 'docs/reviews/T09/evidence/ui')
      await mkdir(directory, { recursive: true })
      await page.screenshot({ path: resolve(directory, name + '.png'), fullPage: true })
    }

    describe('offline learning workspace in a headless browser', () => {
      it('reads all four offline hint levels without a model and never invents a completed check', async () => {
        await mount({ connected: false })
        await capture('desktop-course')
        for (const name of ['概念提示', '操作提示', '部分示范', '完整示范']) {
          await page.getByRole('button', { name: new RegExp(name) }).click()
          await page.getByRole('heading', { name, exact: true }).waitFor()
        }
        expect(
          await page.getByText('课程预览 · 提示可阅读，当前不会保存学习进度。').isVisible(),
        ).toBe(true)
        await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
        expect(await page.getByText('此任务的检查暂不可用，可先查看离线提示。').isVisible()).toBe(
          true,
        )
        await page.getByLabel('选择一个术语').selectOption('开放世界假设')
        expect(await page.getByText('没记录不等于证明不存在。', { exact: true }).isVisible()).toBe(
          true,
        )
        await page.getByText('查看技术定义', { exact: true }).click()
        expect(await page.getByText(/RDF缺少陈述不能推出其否定/).isVisible()).toBe(true)
      })
      it('persists assistance before showing the answer and rejects forged independent completion', async () => {
        await mount({ initialTaskId: 'transfer-repair' })
        await page.evaluate(() => {
          window.learningHarness.failHint = true
        })
        await page.getByRole('button', { name: /完整示范/ }).click()
        expect(await page.getByText('提示使用记录未保存，请重试。').isVisible()).toBe(true)
        expect(await page.getByRole('heading', { name: '完整示范', exact: true }).count()).toBe(0)
        expect(await page.locator('body').innerText()).not.toContain('synthetic-sensitive-message')
        await page.evaluate(() => {
          window.learningHarness.failHint = false
        })
        await page.getByRole('button', { name: /完整示范/ }).click()
        await page.getByRole('heading', { name: '完整示范', exact: true }).waitFor()
        await page.evaluate(() => {
          window.learningHarness.forgedIndependent = true
        })
        await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
        expect(
          await page.getByText('检查结果与当前输入或提示记录不一致，请重新检查。').isVisible(),
        ).toBe(true)
        await page.evaluate(() => {
          window.learningHarness.forgedIndependent = false
        })
        await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
        expect(await page.getByText('本次未计入独立迁移成功。', { exact: true }).isVisible()).toBe(
          true,
        )
        expect(await page.getByLabel('当前输入学习进度').innerText()).toContain(
          '独立迁移成功 0 / 2',
        )
      })
      it('separates actual Agent full assistance from an independently solved transfer', async () => {
        await mount({ initialTaskId: 'transfer-classify' })
        await page.evaluate(() => {
          window.learningHarness.assistance = 'agent-full-assistance'
        })
        await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
        const feedback = page.getByRole('region', { name: '检查反馈' })
        expect(await feedback.getByText('使用 Agent 完整辅助', { exact: true }).isVisible()).toBe(
          true,
        )
        expect(await feedback.getByText('本次未计入独立迁移成功。').isVisible()).toBe(true)
      })
      it('ignores a late check after switching project and generation', async () => {
        await mount({ initialTaskId: 'query' })
        await page.evaluate(() => {
          window.learningHarness.deferred = true
        })
        await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
        await page.getByRole('button', { name: '正在检查…', exact: true }).waitFor()
        await page.evaluate(() => {
          const state = window.learningHarness
          const old = state.pendingContext!
          const contexts = Object.fromEntries(
            Object.entries(state.props.contexts!).map(([id, ctx]) => [
              id,
              { ...ctx, projectId: 'project-B' },
            ]),
          )
          window.mountLearning({
            ...state.props,
            generation: 2,
            projectId: 'project-B',
            contexts,
            initialTaskId: 'mapping',
          })
          setTimeout(() => state.resolveCheck!(state.reply(old)), 0)
        })
        await page
          .getByRole('heading', { name: '从两行CSV形成稳定的设备身份和可追溯事实。', exact: true })
          .waitFor()
        expect(await page.getByText('实际结果条目', { exact: true }).count()).toBe(0)
        expect(await page.getByLabel('当前输入学习进度').innerText()).toContain('0 / 9')
      })
      it('renders imported feedback as text without tags, handlers or network requests', async () => {
        await mount()
        await page.evaluate(() => {
          window.learningHarness.malicious = true
        })
        await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
        await page
          .getByText('<img src="https://probe.invalid/x" onerror="alert(1)">', { exact: true })
          .waitFor()
        expect(await page.locator('img, script[src], iframe').count()).toBe(0)
      })
      it('reconciles newer assistance records instead of showing an older independent result', async () => {
        await mount({ initialTaskId: 'transfer-repair' })
        await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
        await page.getByText('本次独立迁移成功。', { exact: true }).waitFor()
        await page.evaluate(() => {
          const state = window.learningHarness
          const context = state.props.contexts!['transfer-repair']
          const record: LearningRecordView = {
            context,
            recordVersion: 99,
            maxHintLevel: 4,
            assistance: 'agent-full-assistance',
            operationComplete: false,
            independentTransferSuccess: false,
            checkStatus: 'not-checked',
            evidenceIds: [],
          }
          window.mountLearning({ ...state.props, records: [record] })
        })
        await page.getByText('学习记录已更新，请重新检查。', { exact: true }).waitFor()
        expect(await page.getByText('本次独立迁移成功。', { exact: true }).count()).toBe(0)
        expect(await page.getByLabel('当前输入学习进度').innerText()).toContain(
          '独立迁移成功 0 / 2',
        )
      })

      it('requires a real recorded attempt before revealing any transfer hint in preview', async () => {
        await mount({ connected: false, initialTaskId: 'transfer-repair' })
        for (const name of ['概念提示', '操作提示', '部分示范', '完整示范']) {
          await page.getByRole('button', { name: new RegExp(name) }).click()
          await page
            .getByText('请先打开迁移练习，记录提示使用后查看提示。', { exact: true })
            .waitFor()
          expect(await page.getByRole('heading', { name, exact: true }).count()).toBe(0)
        }
      })
      it('does not reveal an actual attempt hint when its recording capability is missing', async () => {
        await mount({ initialTaskId: 'transfer-repair' })
        await page.evaluate(() => {
          const state = window.learningHarness
          window.mountLearning({
            ...state.props,
            actions: { checkTask: state.props.actions!.checkTask },
          })
        })
        await page.getByRole('button', { name: /完整示范/ }).click()
        await page.getByText('提示使用记录暂不可用，请稍后重试。', { exact: true }).waitFor()
        expect(await page.getByRole('heading', { name: '完整示范', exact: true }).count()).toBe(0)
      })
      it.each(['newer-lower', 'same-version-conflict', 'contradictory-newer'] as const)(
        'rejects %s owner records after acknowledged assistance',
        async (variant) => {
          await mount({ initialTaskId: 'transfer-repair' })
          await page.getByRole('button', { name: /完整示范/ }).click()
          await page.getByRole('heading', { name: '完整示范', exact: true }).waitFor()
          await page.evaluate((variant) => {
            const state = window.learningHarness
            const record = state.reply(state.props.contexts!['transfer-repair']).record
            if (variant === 'newer-lower') {
              record.maxHintLevel = 0
              record.assistance = 'independent'
              record.independentTransferSuccess = true
            } else if (variant === 'same-version-conflict') {
              record.recordVersion = 1
            } else {
              record.assistance = 'independent'
              record.independentTransferSuccess = true
            }
            window.mountLearning({ ...state.props, records: [record] })
          }, variant)
          await page.getByText('学习记录不一致，请重新检查。', { exact: true }).waitFor()
          expect(await page.getByLabel('当前输入学习进度').innerText()).toContain(
            '独立迁移成功 0 / 2',
          )
          await page.getByRole('button', { name: /本体构建/ }).click()
          await page
            .getByRole('button', { name: /迁移任务/ })
            .first()
            .click()
          await page.getByText('学习记录不一致，请重新检查。', { exact: true }).waitFor()
        },
      )
      it('retains assistance when inputs change inside the same transfer attempt', async () => {
        await mount({ initialTaskId: 'transfer-repair' })
        await page.getByRole('button', { name: /完整示范/ }).click()
        await page.getByRole('heading', { name: '完整示范', exact: true }).waitFor()
        await page.evaluate(() => {
          const state = window.learningHarness
          const context = { ...state.props.contexts!['transfer-repair'], inputVersion: 'input-2' }
          const record = state.reply(context).record
          record.maxHintLevel = 0
          record.assistance = 'independent'
          record.independentTransferSuccess = true
          window.mountLearning({
            ...state.props,
            contexts: { ...state.props.contexts, 'transfer-repair': context },
            records: [record],
          })
        })
        await page.getByText('学习记录不一致，请重新检查。', { exact: true }).waitFor()
        expect(await page.getByLabel('当前输入学习进度').innerText()).toContain(
          '独立迁移成功 0 / 2',
        )
      })
      it.each(['task', 'attemptId', 'inputVersion'] as const)(
        'ignores a late check after changing %s',
        async (field) => {
          await mount({ initialTaskId: 'query' })
          await page.evaluate(() => {
            window.learningHarness.deferred = true
          })
          await page.getByRole('button', { name: '检查我的操作', exact: true }).click()
          await page.getByRole('button', { name: '正在检查…', exact: true }).waitFor()
          if (field === 'task') await page.getByRole('button', { name: /数据映射/ }).click()
          else
            await page.evaluate((field) => {
              const state = window.learningHarness
              const contexts = {
                ...state.props.contexts,
                query: { ...state.props.contexts!.query, [field]: 'changed' },
              }
              window.mountLearning({ ...state.props, contexts })
            }, field)
          await page.getByRole('button', { name: '检查我的操作', exact: true }).waitFor()
          await page.evaluate(() => {
            const state = window.learningHarness
            state.resolveCheck!(state.reply(state.pendingContext!))
          })
          expect(await page.getByText('实际结果条目', { exact: true }).count()).toBe(0)
          expect(await page.getByLabel('当前输入学习进度').innerText()).toContain('0 / 9')
        },
      )
      it('keeps the learning path and help usable on a narrow screen', async () => {
        await page.setViewportSize({ width: 390, height: 844 })
        await mount({ connected: false, initialTaskId: 'behavior' })
        await page.getByRole('button', { name: /概念提示/ }).click()
        await page.getByRole('heading', { name: '概念提示', exact: true }).waitFor()
        expect(
          await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
        ).toBe(true)
        await capture('mobile-behavior')
      })
    })
  },
)
